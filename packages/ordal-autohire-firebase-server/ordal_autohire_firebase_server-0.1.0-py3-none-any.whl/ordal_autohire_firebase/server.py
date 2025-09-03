# ----- firebase mcp server -----
from mcp.server.fastmcp import FastMCP
from typing import Annotated, Optional, List, Literal
from pydantic import Field
from services.firebase_client import get_db
from datetime import datetime, timezone
from google.cloud import firestore as gfs
from services.init_firebase_server import init_agent_tools

# ----- auto apply n jobs ------
from typing import Optional, List, Union
from typing_extensions import Annotated
from pydantic import Field
from datetime import datetime, timezone, timedelta
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

# ----- list matching jobs ------- 
import uuid
from datetime import datetime, timezone

# ----- mcp profile helpers -----
from services.mcp_profile_helpers import *

mcp = FastMCP("ordal-firebase-server")

# ------- job posters tool ------
from google.cloud.firestore_v1 import FieldFilter
import re

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

def _resolve_role(db, user_id: str) -> str:
    """Return 'jobposter' | 'jobseeker' | 'unknown'."""
    if db.collection("jobposters").document(user_id).get().exists:
        return "jobposter"
    if db.collection("jobseekers").document(user_id).get().exists:
        return "jobseeker"
    return "unknown"

def _assert_job_ownership(db, poster_id: str, job_id: str) -> Optional[dict]:
    """Return None if ok, else an error dict."""
    job_snap = db.collection("jobs").document(job_id).get()
    if not job_snap.exists:
        return {"ok": False, "error": f"job {job_id!r} not found"}
    jd = job_snap.to_dict() or {}
    if str(jd.get("poster_id")) != poster_id:
        return {"ok": False, "error": "forbidden", "reason": "You do not own this job"}
    return None

# ------- ROLE CHECK ---------
@mcp.tool(name="whoami_role")
def whoami_role(
    user_id: Annotated[str, Field(description="Auth UID")]
) -> dict:
    """Return your role so the agent chooses the right tools."""
    db = get_db()
    role = _resolve_role(db, user_id)
    return {"role": role}

# -------- FREE TOOLS --------
@mcp.tool()
def get_user_profile(
    user_id: Annotated[str, Field(description="Auth UID of the jobseeker")]
) -> dict:
    """Return plan, locale, skills, resume_summary for the user."""
    db = get_db()
    doc = db.collection("jobseekers").document(user_id).get()
    if not doc.exists:
        return {"error": f"user {user_id} not found"}
    data = doc.to_dict()
    return {
        "plan": data.get("plan","free"),
        "locale": data.get("locale",""),
        "skills": data.get("skills", []),
        "resume_summary": data.get("resume_summary","")
    }

@mcp.tool()
def verify_subscription(
    user_id: Annotated[str, Field(description="Auth UID")],
    feature: Annotated[str, Field(description='"auto_apply" or "poster_pro_filters"')]
) -> dict:
    """Check if a user has access to a feature."""
    db = get_db()

    if feature == "auto_apply":
        js = db.collection("jobseekers").document(user_id).get()
        if js.exists:
            allowed = (js.to_dict().get("plan") == "pro")
            return {"allowed": allowed, "reason": None if allowed else "Upgrade to Pro to auto apply."}
        return {"allowed": False, "reason": "Not a jobseeker or no profile."}

    if feature == "poster_pro_filters":
        # direct plan on jobposters doc
        jp = db.collection("jobposters").document(user_id).get()
        if jp.exists and (jp.to_dict() or {}).get("plan") == "pro":
            return {"allowed": True, "reason": None}
        # subscriptions fallback (keeps your prior logic)
        sub = (db.collection("subscriptions")
                .where(filter=FieldFilter("user_id", "==", user_id))
                .where(filter=FieldFilter("kind", "==", "poster"))
                .where(filter=FieldFilter("status", "==", "active"))
                .get())
        allowed = len(sub) > 0
        return {"allowed": allowed, "reason": None if allowed else "Poster Pro required."}

    return {"allowed": False, "reason": "Unknown feature or no active plan."}

# --- score ---
def _score_job(jd: dict, skills: List[str]) -> int:
    """
    Score a job by checking user skills against title/description/tags/company/location.
    """
    text = " ".join([
        str(jd.get("title") or ""),
        str(jd.get("description") or ""),
        " ".join(map(str, jd.get("tags") or [])),
        str(jd.get("company") or ""),
        str(jd.get("location") or ""),
    ]).lower()

    hits = 0
    for s in skills or []:
        tok = str(s).strip().lower()
        if not tok:
            continue
        # word-ish match to avoid 'c' matching 'c++'
        if re.search(rf"\b{re.escape(tok)}\b", text):
            hits += 1

    return min(100, hits * 20)

# ------ list matching jobs --------
@mcp.tool()
def list_matching_jobs(
    user_id: Annotated[str, Field(description="Auth UID")],
    limit: Annotated[int, Field(description="Number of top jobs to return", ge=1, le=50)] = 10
) -> dict:
    """Return top-N jobs (excluding already applied) and persist a snapshot by list_id."""
    db = get_db()
    user_doc = db.collection("jobseekers").document(user_id).get()
    if not user_doc.exists:
        return {"jobs": [], "list_id": None}

    # 0) Collect IDs of already-applied jobs (any status)
    applied_col = db.collection("jobseekers").document(user_id).collection("jobs_applied")
    applied_ids = {snap.id for snap in applied_col.stream()}  # doc id == job_id
    
    skills = user_doc.to_dict().get("skills", [])
    
    # 1) Source pool (cap to 100 recent “open” jobs; newest first)
    jobs = (
        db.collection("jobs")
          .where("status", "==", "open")
          .order_by("created_at", direction=gfs.Query.DESCENDING)
          .limit(100)
          .get()
    )

    # 2) Score & exclude previously applied
    scored: list[dict] = []
    for j in jobs:
        if j.id in applied_ids:
            continue  # skip already applied
        jd = j.to_dict() or {}
        sc = _score_job(jd, skills)
        scored.append({
            "job_id": j.id,
            "title": jd.get("title"),
            "company": jd.get("company"),
            "location": jd.get("location"),
            "score": sc,
        })

    # 3) Deterministic ordering then take top K
    scored.sort(key=lambda x: (-int(x["score"]), str(x["job_id"])))
    topk = scored[:limit]

    # 4) 1-based index for UX/agent reasoning
    for i, row in enumerate(topk, start=1):
        row["index"] = i

    # 5) Persist snapshot exactly as shown
    list_id = str(uuid.uuid4())
    snapshot_ref = (
        db.collection("jobseekers").document(user_id)
          .collection("job_lists").document(list_id)
    )
    snapshot_ref.set({
        "created_at": int(datetime.now(timezone.utc).timestamp() * 1000),
        "limit": limit,
        "jobs": topk,
        "skills_basis": skills,
        "version": 1,
        "excluded_applied_count": len(applied_ids),
    })

    return {"jobs": topk, "list_id": list_id}

# -------- UPDATE PROFILE TOOLS --------
@mcp.tool()
def set_locale(
    user_id: Annotated[str, Field(description="Auth UID")],
    locale: Annotated[str, Field(description="Locale/country code, e.g. 'AU' or 'SG'")]
) -> dict:
    """set profile location"""
    db = get_db()
    db.collection("jobseekers").document(user_id).set({"locale": locale}, merge=True)
    return {"ok": True, "updated": ["locale"]}

@mcp.tool()
def upsert_personal_info(
    user_id: Annotated[str, Field(description="Auth UID")],
    first_name: Annotated[Optional[str], Field(nullable=True)] = None,
    last_name: Annotated[Optional[str], Field(nullable=True)] = None,
    email: Annotated[Optional[str], Field(nullable=True)] = None,
    phone: Annotated[Optional[str], Field(nullable=True)] = None,
    dob: Annotated[Optional[str], Field(description="YYYY-MM-DD", nullable=True)] = None,
) -> dict:
    """
    updates a new record into personal_info if it doesn't exist
    or updates an existing record if matching one is found based
    on a unique identifier or conflict condition. 
    """
    patch = {}
    for k, v in {
        "first_name": first_name, "last_name": last_name,
        "email": email, "phone": phone, "dob": dob
    }.items():
        if v is not None:
            patch[k] = v
    if not patch:
        return {"ok": True, "updated": []}
    get_db().collection("jobseekers").document(user_id).set({"personal_info": patch}, merge=True)
    return {"ok": True, "updated": [f"personal_info.{k}" for k in patch]}

@mcp.tool()
def update_resume_summary(
    user_id: Annotated[str, Field(description="Auth UID")],
    text: Annotated[Optional[str], Field(description="Text or substring (for remove_substring)", nullable=True)] = None,
    mode: Annotated[
        str,
        Field(description="one of: replace | append | prepend | clear | remove_substring")
    ] = "replace",
) -> dict:
    ref = get_db().collection("jobseekers").document(user_id)
    snap = ref.get()
    cur = (snap.to_dict() or {}).get("resume_summary", "") or ""

    if mode == "clear":
        ref.set({"resume_summary": ""}, merge=True)
    elif mode == "replace":
        ref.set({"resume_summary": (text or "")}, merge=True)
    elif mode == "append":
        new_txt = (cur + (" " if cur and text else "") + (text or "")).strip()
        ref.set({"resume_summary": new_txt}, merge=True)
    elif mode == "prepend":
        new_txt = ((text or "") + (" " if cur and text else "") + cur).strip()
        ref.set({"resume_summary": new_txt}, merge=True)
    elif mode == "remove_substring":
        if not text:
            return {"ok": False, "error": "text required for remove_substring"}
        ref.set({"resume_summary": cur.replace(text, "").strip()}, merge=True)
    else:
        return {"ok": False, "error": f"unknown mode {mode!r}"}

    return {"ok": True, "updated": ["resume_summary"], "mode": mode}

@mcp.tool()
def update_background_summary(
    user_id: Annotated[str, Field(description="Auth UID")],
    text: Annotated[Optional[str], Field(description="Text or substring (for remove_substring)", nullable=True)] = None,
    mode: Annotated[
        Literal["replace", "append", "prepend", "clear", "remove_substring", "delete"],
        Field(description="replace | append | prepend | clear | remove_substring | delete")
    ] = "replace",
) -> dict:
    """
    Edit background_info.summary without touching resume_summary.
    - replace: set to `text`
    - append:  add `text` to the end (space-normalized)
    - prepend: add `text` to the start (space-normalized)
    - clear:   set to empty string ""
    - remove_substring: remove the first/each occurrence of `text`
    - delete:  delete the field (unset background_info.summary)
    """
    ref = get_db().collection("jobseekers").document(user_id)
    snap = ref.get()
    data = snap.to_dict() or {}
    cur_bg = (data.get("background_info") or {})
    cur = (cur_bg.get("summary") or "")

    path = "background_info.summary"

    if mode == "delete":
        # Completely remove the field
        ref.update({path: gfs.DELETE_FIELD})
        return {"ok": True, "updated": ["background_info.summary"], "mode": "delete"}

    if mode == "clear":
        ref.set({"background_info": {"summary": ""}}, merge=True)
    elif mode == "replace":
        ref.set({"background_info": {"summary": (text or "")}}, merge=True)
    elif mode == "append":
        new_txt = (cur + (" " if cur and text else "") + (text or "")).strip()
        ref.set({"background_info": {"summary": new_txt}}, merge=True)
    elif mode == "prepend":
        new_txt = ((text or "") + (" " if cur and text else "") + cur).strip()
        ref.set({"background_info": {"summary": new_txt}}, merge=True)
    elif mode == "remove_substring":
        if not text:
            return {"ok": False, "error": "text required for remove_substring"}
        ref.set({"background_info": {"summary": cur.replace(text, "").strip()}}, merge=True)
    else:
        return {"ok": False, "error": f"unknown mode {mode!r}"}

    return {"ok": True, "updated": ["background_info.summary"], "mode": mode}

@mcp.tool()
def update_yoe(
    user_id: Annotated[str, Field(description="Auth UID")],
    value: Annotated[Optional[str], Field(description="Number or delta", nullable=True)] = None,
    op: Annotated[str, Field(description="one of: set | add | subtract | clear")] = "set",
) -> dict:
    ref = get_db().collection("jobseekers").document(user_id)
    if op == "clear":
        ref.set({"background_info": {"yoe": gfs.DELETE_FIELD}}, merge=True)
        return {"ok": True, "updated": ["background_info.yoe"], "mode": "clear"}

    n = to_int_or_none(value)
    if n is None:
        return {"ok": False, "error": f"Invalid number: {value!r}"}

    snap = ref.get()
    cur_bi = (snap.to_dict() or {}).get("background_info", {}) or {}
    cur = to_int_or_none(cur_bi.get("yoe"))

    if op == "set" or cur is None:
        new_val = n
    elif op == "add":
        new_val = max(0, cur + n)
    elif op == "subtract":
        new_val = max(0, cur - n)
    else:
        return {"ok": False, "error": f"unknown op {op!r}"}

    ref.set({"background_info": {"yoe": new_val}}, merge=True)
    return {"ok": True, "updated": ["background_info.yoe"], "mode": op, "value": new_val}

@mcp.tool()
def update_interests(
    user_id: Annotated[str, Field(description="Auth UID")],
    interests: Annotated[Optional[str], Field(description="Comma-separated values", nullable=True)] = None,
    mode: Annotated[str, Field(description="one of: add | remove | replace | clear")] = "add",
) -> dict:
    ref = get_db().collection("jobseekers").document(user_id)
    values = parse_csv(interests)

    if mode == "clear":
        ref.set({"background_info": {"interests": []}}, merge=True)
        return {"ok": True, "updated": ["background_info.interests"], "mode": "clear"}

    if mode == "replace":
        ref.set({"background_info": {"interests": unique_case_preserve(values)}}, merge=True)
        return {"ok": True, "updated": ["background_info.interests"], "mode": "replace"}

    # add/remove use transforms on the dot-path
    path = "background_info.interests"
    if mode == "add":
        if values:
            ref.update({path: gfs.ArrayUnion(values)})
        return {"ok": True, "updated": ["background_info.interests"], "mode": "add", "added": values}
    if mode == "remove":
        if values:
            # case-insensitive remove needs normalization; do best-effort exact removes
            # (LLM should pass exact tokens from UI; otherwise you could fetch+filter)
            ref.update({path: gfs.ArrayRemove(values)})
        return {"ok": True, "updated": ["background_info.interests"], "mode": "remove", "removed": values}

    return {"ok": False, "error": f"unknown mode {mode!r}"}

@mcp.tool()
def update_skills(
    user_id: Annotated[str, Field(description="Auth UID")],
    skills: Annotated[Optional[str], Field(description="Comma-separated skills", nullable=True)] = None,
    mode: Annotated[str, Field(description="one of: add | remove | replace | clear")] = "add",
) -> dict:
    ref = get_db().collection("jobseekers").document(user_id)
    parsed = parse_skills(skills)

    if mode == "clear":
        ref.set({"skills": []}, merge=True)
        return {"ok": True, "updated": ["skills"], "mode": "clear"}

    if mode == "replace":
        ref.set({"skills": unique_case_preserve(parsed)}, merge=True)
        return {"ok": True, "updated": ["skills"], "mode": "replace"}

    snap = ref.get()
    cur = (snap.to_dict() or {}).get("skills", []) or []
    cur_lc = {s.lower(): s for s in cur}

    if mode == "add":
        to_add = [s for s in parsed if s.lower() not in cur_lc]
        if to_add:
            ref.update({"skills": gfs.ArrayUnion(to_add)})
        return {"ok": True, "updated": ["skills"], "mode": "add", "added": to_add}

    if mode == "remove":
        # try exact first; if not found, try canonical/startswith heuristics
        to_remove_exact = []
        canon_to_exact = {canon_token(s): s for s in cur}
        for raw in parsed:
            c = canon_token(raw)
            if c in canon_to_exact:
                to_remove_exact.append(canon_to_exact[c]); continue
            if raw.lower() in cur_lc:
                to_remove_exact.append(cur_lc[raw.lower()]); continue
            # last resort: unique startswith match
            hits = [orig for k, orig in cur_lc.items() if k.startswith(c)]
            hits = list(dict.fromkeys(hits))
            if len(hits) == 1:
                to_remove_exact.append(hits[0])
        if to_remove_exact:
            ref.update({"skills": gfs.ArrayRemove(to_remove_exact)})
            return {"ok": True, "updated": ["skills"], "mode": "remove", "removed": to_remove_exact}
        return {"ok": True, "updated": [], "mode": "remove", "note": f"No close match for: {', '.join(parsed)}"}

    return {"ok": False, "error": f"unknown mode {mode!r}"}

# -------- JOBSEEKERS PRO TOOLS --------
# --- helpers ---------------------------------------------------------------
def _get_nested(d: dict, path: str):
    cur = d
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur

def _coalesce_str(*vals):
    for v in vals:
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

def _norm_skills(skills) -> list[str]:
    out = []
    for s in skills or []:
        if isinstance(s, str):
            t = s.strip()
            if t:
                out.append(t)
        elif isinstance(s, dict):
            for k in ("name", "label", "title", "value"):
                v = s.get(k)
                if isinstance(v, str) and v.strip():
                    out.append(v.strip())
                    break
    seen = set()
    dedup = []
    for t in out:
        lt = t.lower()
        if lt not in seen:
            seen.add(lt)
            dedup.append(t)
    return dedup

def _intify(v):
    try:
        return int(v)
    except Exception:
        return None

def _resolve_display_name(user_doc: dict, first_name: str | None, last_name: str | None) -> str | None:
    # Match your JS helper’s precedence
    pi = user_doc.get("personal_info") or {}
    return _coalesce_str(
        user_doc.get("displayName"),
        user_doc.get("fullName"),
        user_doc.get("name"),
        pi.get("name"),
        " ".join([p for p in [pi.get("first_name"), pi.get("last_name")] if p]),
        " ".join([p for p in [first_name, last_name] if p]),
    )

# --- fixed builder ---------------------------------------------------------
def _build_applicant_doc(
    user_id: str,
    user_doc: dict,
    job_id: str,
    now_ms: int | None = None,
    score: int | None = None,
) -> dict:
    from datetime import datetime, timezone
    if now_ms is None:
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

    # First/Last name from common shapes (includes personal_info.*)
    first_name = _coalesce_str(
        user_doc.get("first_name"),
        _get_nested(user_doc, "name.first"),
        _get_nested(user_doc, "profile.first_name"),
        _get_nested(user_doc, "background_info.first_name"),
        _get_nested(user_doc, "personal_info.first_name"),
        user_doc.get("given_name"),
        user_doc.get("firstName"),
    )
    last_name = _coalesce_str(
        user_doc.get("last_name"),
        _get_nested(user_doc, "name.last"),
        _get_nested(user_doc, "profile.last_name"),
        _get_nested(user_doc, "background_info.last_name"),
        _get_nested(user_doc, "personal_info.last_name"),
        user_doc.get("family_name"),
        user_doc.get("lastName"),
    )

    full_name = _resolve_display_name(user_doc, first_name, last_name)

    email = _coalesce_str(
        user_doc.get("email"),
        _get_nested(user_doc, "contact.email"),
        _get_nested(user_doc, "profile.email"),
        _get_nested(user_doc, "personal_info.email"),
    )
    phone = _coalesce_str(
        user_doc.get("phone"),
        _get_nested(user_doc, "contact.phone"),
        _get_nested(user_doc, "profile.phone"),
        _get_nested(user_doc, "personal_info.phone"),
        _get_nested(user_doc, "phone_number"),
    )

    resume_url = _coalesce_str(
        user_doc.get("resume_url"),
        user_doc.get("cv_url"),
        _get_nested(user_doc, "resume.url"),
        _get_nested(user_doc, "files.resume.url"),
    )
    portfolio_url = _coalesce_str(
        user_doc.get("portfolio_url"),
        user_doc.get("website"),
        _get_nested(user_doc, "links.portfolio"),
        _get_nested(user_doc, "links.website"),
    )

    expected_salary_min = _intify(
        user_doc.get("expected_salary_min")
        or _get_nested(user_doc, "expected_salary.min")
        or _get_nested(user_doc, "salary.min")
        or _get_nested(user_doc, "personal_info.expected_salary_min")
    )
    expected_salary_max = _intify(
        user_doc.get("expected_salary_max")
        or _get_nested(user_doc, "expected_salary.max")
        or _get_nested(user_doc, "salary.max")
        or _get_nested(user_doc, "personal_info.expected_salary_max")
    )
    yoe = _intify(
        user_doc.get("yoe")
        or user_doc.get("years_of_experience")
        or _get_nested(user_doc, "experience.years")
        or _get_nested(user_doc, "personal_info.yoe")
    )

    resume_summary = _coalesce_str(
        user_doc.get("resume_summary"),
        user_doc.get("summary"),
        _get_nested(user_doc, "background_info.interests.summary"),
        _get_nested(user_doc, "bio"),
        _get_nested(user_doc, "personal_info.summary"),
    )

    bi_summary = _get_nested(user_doc, "background_info.interests.summary")
    background_info = {"interests": {"summary": bi_summary}} if bi_summary else None

    skills = _norm_skills(user_doc.get("skills"))

    doc = {
        "id": user_doc.get("id") or user_id,
        "user_id": user_id,
        "job_id": job_id,
        "accountType": user_doc.get("accountType", "jobseeker"),

        "first_name": first_name,
        "last_name": last_name,
        "name": full_name,               # <-- now mirrors the JS helper

        "email": email,
        "phone": phone,

        "skills": skills or None,
        "resume_url": resume_url,
        "portfolio_url": portfolio_url,

        "expected_salary_min": expected_salary_min,
        "expected_salary_max": expected_salary_max,
        "yoe": yoe,

        "resume_summary": resume_summary,
        "background_info": background_info,

        "applied_at": now_ms,
        "status": "applied",
        "score": _intify(score) if score is not None else None,
    }

    # Drop empty/None to avoid Firestore nulls or placeholder strings
    return {k: v for k, v in doc.items() if v not in (None, "", [])}

# -------- AUTO APPLY N JOBS ---------
@mcp.tool(name="auto_apply_n_v2")
def auto_apply_n(
    user_id: Annotated[str, Field(description="Auth UID")],
    n: Annotated[int, Field(description="How many jobs to auto-apply (default 3, max 10)", ge=1, le=10)] = 3,
    min_score: Annotated[int, Field(description="Try this score first; tool will back off if no hits", ge=0, le=100)] = 70,
    tz: Annotated[Optional[str], Field(description="IANA timezone for daily cap (e.g. 'Australia/Sydney')", nullable=True)] = "Australia/Sydney",
    
    # explicit targeting
    job_id: Annotated[Optional[str], Field(description="Apply to this specific job id", nullable=True)] = None,
    job_ids: Annotated[Optional[str], Field(description="Comma-separated job ids to apply", nullable=True)] = None,

    # resolve from previously returned list
    list_id: Annotated[Optional[str], Field(description="Snapshot id from list_matching_jobs", nullable=True)] = None,
    job_index: Annotated[Optional[Union[int, str]], Field(description="1-based index within the snapshot list", nullable=True)] = None,
    job_query: Annotated[Optional[str], Field(description="Fuzzy text like 'google' or 'frontend' against the snapshot list", nullable=True)] = None,
) -> dict:
    """
    Pro feature:
      - If job_id / job_ids provided => apply exactly those jobs (ignores score thresholds), respecting daily cap and dedupe.
      - Else => auto-pick up to `n` jobs using score threshold with backoff (min_score -> 50 -> 30 -> 0).
      - Applications stored in: jobseekers/{user_id}/jobs_applied/{job_id}
      - New apps start as status='applied'; doc id = job_id (dedupe).
      - Daily cap = 10 apps/day/user (based on created_at, in user's tz).
    """
    db = get_db()

    # 0) Pro gate
    sub = verify_subscription(user_id=user_id, feature="auto_apply")
    if not sub.get("allowed"):
        return {"ok": False, "error": "Not allowed", "reason": sub.get("reason")}

    # 1) day window for cap
    try:
        z = ZoneInfo(tz) if (tz and ZoneInfo) else timezone.utc
    except Exception:
        z = timezone.utc
    now_local = datetime.now(z)
    sod_local = datetime(now_local.year, now_local.month, now_local.day, 0, 0, 0, tzinfo=z)
    eod_local = sod_local + timedelta(days=1)

    sod_ms = int(sod_local.astimezone(timezone.utc).timestamp() * 1000)
    eod_ms = int(eod_local.astimezone(timezone.utc).timestamp() * 1000)

    user_ref = db.collection("jobseekers").document(user_id)
    applied_col = user_ref.collection("jobs_applied")

    # 2) daily cap check
    todays_q = applied_col.where("created_at", ">=", sod_ms).where("created_at", "<", eod_ms)
    todays = list(todays_q.stream())
    todays_count = len(todays)
    DAILY_CAP = 10
    if todays_count >= DAILY_CAP:
        return {"ok": False, "error": "Daily cap reached", "today_count": todays_count, "cap": DAILY_CAP}

    remaining_quota = min(n, DAILY_CAP - todays_count)
    if remaining_quota <= 0:
        return {"ok": False, "error": "No remaining quota today", "today_count": todays_count, "cap": DAILY_CAP}

    # 3) resolve target set
    explicit_ids: List[str] = []
    if job_ids:
        explicit_ids.extend([j.strip() for j in job_ids.split(",") if j.strip()])
    if job_id:
        explicit_ids.append(job_id.strip())
    explicit_ids = list(dict.fromkeys(explicit_ids))

    # --- 2) Resolve via snapshot if provided and no explicit ids ---
    if not explicit_ids:
        if job_index is not None and not list_id:
            return {"ok": False, "error": "missing_list_id",
                    "hint": "Call list_matching_jobs first and pass its list_id with job_index."}

        if list_id:
            snap_ref = db.collection("jobseekers").document(user_id).collection("job_lists").document(list_id)
            snap = snap_ref.get()
            if not snap.exists:
                return {"ok": False, "error": "snapshot_not_found",
                        "hint": f"list_id={list_id!r} not found. Re-run list_matching_jobs and use its list_id."}

            data = snap.to_dict() or {}
            job_list: List[dict] = data.get("jobs", [])

            if job_index is not None:
                try:
                    idx = int(job_index)
                except Exception:
                    return {"ok": False, "error": f"invalid job_index={job_index!r}, must be an integer-like string"}
                if not (1 <= idx <= len(job_list)):
                    return {"ok": False, "error": f"job_index out of range (1..{len(job_list)})"}
                explicit_ids = [job_list[idx - 1].get("job_id")]

            elif job_query:
                q = job_query.lower().strip()
                hits = [j for j in job_list if any(q in str(j.get(k, "")).lower()
                                                for k in ("title","company","location"))]
                if hits:
                    hits.sort(key=lambda x: (-int(x.get("score", 0)), str(x.get("job_id", ""))))
                    explicit_ids = [hits[0]["job_id"]]

    # If we resolved any explicit id(s), run your existing by-ids branch
    if explicit_ids:
        to_consider = explicit_ids[:remaining_quota]
        exists_snaps = db.get_all([applied_col.document(jid) for jid in to_consider])
        already = {s.id for s in exists_snaps if s.exists}
        final_ids = [jid for jid in to_consider if jid not in already]
        if not final_ids:
            return {"ok": True, "submitted": 0, "skipped": list(already),
                    "today_count": todays_count, "cap": DAILY_CAP, "mode": "by_ids"}

        job_snaps = db.get_all([db.collection("jobs").document(jid) for jid in final_ids])
        job_map = {s.id: (s.to_dict() or {}) for s in job_snaps}

        user_doc = (user_ref.get().to_dict() or {})
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        batch = db.batch()
        results = []

        for jid in final_ids:
            jdoc = job_map.get(jid, {})
            poster_id = jdoc.get("poster_id")

            # 1) write to jobseeker's jobs_applied
            job_snapshot = {
                "job_id": jid,
                "title": jdoc.get("title"),
                "company": jdoc.get("company"),
                "location": jdoc.get("location"),
                "tags": jdoc.get("tags", []),
                "poster_id": poster_id,
                "salary_min": jdoc.get("salary_min"),
                "salary_max": jdoc.get("salary_max"),
                "source": jdoc.get("source"),
                "status": jdoc.get("status"),
            }
            applied_ref = applied_col.document(jid)
            applied_payload = {
                "user_id": user_id,
                "job_id": jid,
                "poster_id": poster_id,
                "status": "applied",
                "score": int(jdoc.get("score", 0)) if jdoc.get("score") is not None else 0,
                "job_snapshot": job_snapshot,
                "created_at": now_ms,
                "updated_at": now_ms,
            }
            batch.set(applied_ref, applied_payload)

            # 2) write/merge applicant under jobs/{jid}/applicants/{user_id}
            job_ref = db.collection("jobs").document(jid)
            applicant_ref = job_ref.collection("applicants").document(user_id)
            applicant_doc = _build_applicant_doc(
                user_id=user_id,
                user_doc=user_doc,
                job_id=jid,
                now_ms=now_ms,                    # <-- add this
                score=applied_payload["score"],
            ) 
            batch.set(applicant_ref, applicant_doc, merge=True)

            # 3) increment visible applicants count on the job
            batch.update(job_ref, {"applicants": gfs.Increment(1)})

            results.append({"job_id": jid, "status": "applied", "poster_id": poster_id})

        batch.commit()

        return {"ok": True, "submitted": len(results), "applications": results,
                "skipped": list(already), "today_count": todays_count + len(results),
                "cap": DAILY_CAP, "mode": "by_ids"}

    # 4) auto-pick mode: use matcher + backoff; deterministic order
    pool = list_matching_jobs(user_id=user_id, limit=100).get("jobs", [])

    # backoff ladder
    ladder = []
    if min_score not in (50, 30, 0):
        ladder.append(min_score)
    ladder += [50, 30, 0]

    picked: List[dict] = []
    used_threshold: Optional[int] = None
    for thr in ladder:
        candidates = [j for j in pool if int(j.get("score", 0)) >= thr]
        # Deterministic ordering: score DESC, job_id ASC
        candidates.sort(key=lambda x: (-int(x.get("score", 0)), str(x.get("job_id", ""))))
        if candidates:
            picked = candidates[:remaining_quota]
            used_threshold = thr
            break

    if not picked:
        return {"ok": True, "submitted": 0, "reason": f"no matches >= any threshold in {ladder}", "today_count": todays_count, "cap": DAILY_CAP, "mode": "auto"}

    # dedupe against existing apps
    exists_snaps = db.get_all([applied_col.document(j["job_id"]) for j in picked])
    already = {s.id for s in exists_snaps if s.exists}
    to_apply = [j for j in picked if j["job_id"] not in already]
    if not to_apply:
        return {"ok": True, "submitted": 0, "skipped": list(already), "reason": "all selected already applied", "today_count": todays_count, "cap": DAILY_CAP, "mode": "auto", "threshold_used": used_threshold}

    # fetch job docs for snapshots
    job_snaps = db.get_all([db.collection("jobs").document(j["job_id"]) for j in to_apply])
    job_map = {s.id: (s.to_dict() or {}) for s in job_snaps}

    # write
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    batch = db.batch()
    results = []
    
    user_doc = (user_ref.get().to_dict() or {})
    for j in to_apply:
        jid = j["job_id"]
        jdoc = job_map.get(jid, {})
        poster_id = j.get("poster_id") or jdoc.get("poster_id")

        # 1) jobseeker application doc
        ref = applied_col.document(jid)
        payload = {
            "user_id": user_id,
            "job_id": jid,
            "poster_id": poster_id,
            "status": "applied",
            "score": int(j.get("score", 0)),
            "job_snapshot": {...},
            "created_at": now_ms,
            "updated_at": now_ms,
        }
        batch.set(ref, payload)

        # 2) job applicants subcollection
        job_ref = db.collection("jobs").document(jid)
        applicant_ref = job_ref.collection("applicants").document(user_id)
        applicant_doc = _build_applicant_doc(
            user_id=user_id,
            user_doc=user_doc,
            job_id=jid,
            now_ms=now_ms,                    # <-- add this
            score=applied_payload["score"],
        ) 
        batch.set(applicant_ref, applicant_doc, merge=True)

        # 3) bump job applicants count
        batch.update(job_ref, {"applicants": gfs.Increment(1)})

        results.append({"job_id": jid, "status": "applied", "poster_id": poster_id, "score": payload["score"]})
    batch.commit()

    return {
        "ok": True,
        "submitted": len(results),
        "applications": results,
        "skipped": list(already),
        "today_count": todays_count + len(results),
        "cap": DAILY_CAP,
        "mode": "auto",
        "threshold_used": used_threshold,
    }
    
# ------ JOB POSTERS TOOLS -------
# --- JOB POSTER HELPERS ---
@mcp.tool(name="poster_list_my_jobs")
def poster_list_my_jobs(
    user_id: Annotated[str, Field(description="Auth UID of the jobposter")],
    limit: Annotated[int, Field(ge=1, le=100, default=50)] = 50,
) -> dict:
    db = get_db()
    if _resolve_role(db, user_id) != "jobposter":
        return {"ok": False, "error": "forbidden"}

    snaps = (db.collection("jobs")
               .where(filter=FieldFilter("poster_id", "==", user_id))
               .order_by("created_at", direction=gfs.Query.DESCENDING)  # rely on Firestore
               .limit(limit)
               .get())

    rows = []
    for s in snaps:
        j = s.to_dict() or {}
        rows.append({
            "job_id": s.id,
            "title": j.get("title"),
            "status": j.get("status"),
            "created_at": _to_epoch_ms(j.get("created_at")),  # normalize
            "location": j.get("location"),
            "tags": j.get("tags", []),
            "applicants": j.get("applicants", 0),
        })

    # optional secondary sorts without unary minus on raw values
    rows.sort(key=lambda r: (-int(r["created_at"]), str(r.get("title") or ""), str(r["job_id"])))
    return {"ok": True, "jobs": rows}

# ------ FREE TIER -------
@mcp.tool(name="poster_list_applicants")
def poster_list_applicants(
    user_id: Annotated[str, Field(description="Auth UID of the jobposter")],
    job_id: Annotated[str, Field(description="Target job id")],
    status: Annotated[Optional[str], Field(default=None, description="Filter by application status (e.g., 'applied','pending','accepted','rejected')", nullable=True)] = None,
    limit: Annotated[int, Field(default=100, ge=1, le=500, description="Max number of applicants to return")] = 100,
) -> dict:
    """List all candidates who applied to a given job (free feature)."""
    db = get_db()
    # Ownership gate
    err = _assert_job_ownership(db, user_id, job_id)
    if err:
        return err

    q = db.collection_group("jobs_applied").where(filter=FieldFilter("job_id", "==", job_id))
    if status:
        q = q.where(filter=FieldFilter("status", "==", status))
    snaps = q.limit(limit).get()

    applicants = []
    for s in snaps:
        d = s.to_dict() or {}
        seeker_id = d.get("user_id")
        # enrich with minimal seeker profile
        seeker = db.collection("jobseekers").document(seeker_id).get()
        prof = seeker.to_dict() if seeker.exists else {}
        pi = (prof or {}).get("personal_info", {}) or {}
        name = " ".join([str(pi.get("first_name") or "").strip(), str(pi.get("last_name") or "").strip()]).strip() or pi.get("display_name") or seeker_id
        applicants.append({
            "user_id": seeker_id,
            "name": name,
            "status": d.get("status"),
            "score": d.get("score"),
            "applied_at": d.get("created_at"),
            "skills": (prof or {}).get("skills", []),
            "yoe": ((prof or {}).get("background_info") or {}).get("yoe"),
        })

    # Stable ordering: status then -score then name
    applicants.sort(key=lambda x: (str(x.get("status") or "zzz"), -(int(x.get("score") or 0)), str(x.get("name") or "")))
    return {"ok": True, "job_id": job_id, "count": len(applicants), "applicants": applicants}

# ------ PRO TIER -------
def _score_candidate_for_job(job_text: str, skills: List[str]) -> int:
    t = (job_text or "").lower()
    hits = sum(1 for s in skills or [] if str(s).lower() in t)
    return min(100, hits * 20)

# ------- LIST TOP N CANDIDATES ---------
def _to_epoch_ms(v) -> int:
    """Coerce Timestamp/int/float/str/None to epoch ms; fallback 0."""
    if v is None:
        return 0
    ts = getattr(v, "timestamp", None)
    if callable(ts):
        try:
            return int(v.timestamp() * 1000)
        except Exception:
            pass
    try:
        return int(v)
    except Exception:
        try:
            return int(float(str(v)))
        except Exception:
            return 0

def _coalesce_str(*vals):
    for v in vals:
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

def _norm_skills(skills) -> list[str]:
    out = []
    for s in skills or []:
        if isinstance(s, str):
            t = s.strip()
            if t:
                out.append(t)
        elif isinstance(s, dict):
            for k in ("name","label","title","value"):
                v = s.get(k)
                if isinstance(v, str) and v.strip():
                    out.append(v.strip()); break
    seen=set(); ded=[]
    for t in out:
        lt=t.lower()
        if lt not in seen:
            seen.add(lt); ded.append(t)
    return ded

@mcp.tool(name="poster_list_top_candidates")
def poster_list_top_candidates(
    user_id: Annotated[str, Field(description="Auth UID of the jobposter")],
    job_id: Annotated[str, Field(description="Target job id")],
    n: Annotated[int, Field(default=5, ge=1, le=50, description="Top-N to return")] = 5,
) -> dict:
    """Pro: Return top-N candidates ranked by simple skills-vs-job match."""
    db = get_db()

    # gates
    if _resolve_role(db, user_id) != "jobposter":
        return {"ok": False, "error": "forbidden", "reason": "Poster-only tool"}
    sub = verify_subscription(user_id=user_id, feature="poster_pro_filters")
    if not sub.get("allowed"):
        return {"ok": False, "error": "not_allowed", "reason": sub.get("reason")}
    err = _assert_job_ownership(db, user_id, job_id)
    if err:
        return err

    # job text
    job_snap = db.collection("jobs").document(job_id).get()
    jd = job_snap.to_dict() or {}
    job_text = " ".join([
        str(jd.get("title") or ""),
        str(jd.get("description") or ""),
        " ".join(map(str, jd.get("tags") or [])),
    ])

    # read applicants from jobs/{job_id}/applicants
    apps = (db.collection("jobs").document(job_id)
              .collection("applicants")
              .order_by("applied_at", direction=gfs.Query.DESCENDING)  # keeps newest first
              .get())

    rows = []
    for app in apps:
        a = app.to_dict() or {}

        # uid may be saved as user_id, id, or the doc id
        seeker_id = a.get("user_id") or a.get("id") or app.id

        # profile (for skills fallback, yoe, displayName…)
        seeker = db.collection("jobseekers").document(seeker_id).get()
        prof = seeker.to_dict() if seeker.exists else {}
        pi = (prof.get("personal_info") or {}) if prof else {}

        # skills: prefer applicant doc, fallback to profile
        skills = _norm_skills(a.get("skills")) or _norm_skills(prof.get("skills"))

        # name: prefer applicant doc, then profile, then personal_info, then uid
        name = _coalesce_str(
            a.get("name"),
            " ".join([a.get("first_name",""), a.get("last_name","")]).strip(),
            prof.get("displayName"),
            prof.get("display_name"),
            prof.get("fullName"),
            prof.get("name"),
            pi.get("name"),
            " ".join([pi.get("first_name",""), pi.get("last_name","")]).strip(),
            seeker_id,
        )

        match_score = _score_candidate_for_job(job_text, skills)

        rows.append({
            "user_id": seeker_id,
            "name": name,
            "status": a.get("status") or "applied",
            "applied_at": a.get("applied_at"),
            "email": a.get("email"),
            "phone": a.get("phone"),
            "skills": skills,
            "yoe": a.get("yoe") or (prof.get("background_info") or {}).get("yoe"),
            "match_score": int(match_score or 0),
        })

    # rank: match desc, then applied_at desc, then name asc
    rows.sort(key=lambda x: (
        -int(x.get("match_score") or 0),
        -_to_epoch_ms(x.get("applied_at")),
        str(x.get("name") or "")
    ))

    return {"ok": True, "job_id": job_id, "top": rows[:n], "total": len(rows)}

# ------ CANDIDATE INSIGHTS ------
@mcp.tool(name="poster_candidate_insight")
def poster_candidate_insight(
    user_id: Annotated[str, Field(description="Auth UID of the jobposter")],
    job_id: Annotated[str, Field(description="Job id to scope the search")],
    name_query: Annotated[Optional[str], Field(default=None, description="Case-insensitive substring of candidate name", nullable=True)] = None,
    candidate_user_id: Annotated[Optional[str], Field(default=None, description="Direct user id (overrides name_query)", nullable=True)] = None,
) -> dict:
    """Pro: Show a candidate's profile snapshot for this job (skills, yoe, summaries, recent activity)."""
    db = get_db()

    if _resolve_role(db, user_id) != "jobposter":
        return {"ok": False, "error": "forbidden", "reason": "Poster-only tool"}
    sub = verify_subscription(user_id=user_id, feature="poster_pro_filters")
    if not sub.get("allowed"):
        return {"ok": False, "error": "not_allowed", "reason": sub.get("reason")}

    err = _assert_job_ownership(db, user_id, job_id)
    if err:
        return err

    # Get applicants first (scoped to this job)
    apps = (db.collection_group("jobs_applied")
              .where(filter=FieldFilter("job_id", "==", job_id))
              .get())
    applied_ids = []
    for s in apps:
        d = s.to_dict() or {}
        applied_ids.append(d.get("user_id"))

    if not applied_ids:
        return {"ok": True, "found": 0, "insights": []}

    # Determine target(s)
    targets = []
    if candidate_user_id:
        if candidate_user_id in applied_ids:
            targets = [candidate_user_id]
        else:
            return {"ok": False, "error": "not_found", "reason": "Candidate has not applied to this job"}

    else:
        q = (name_query or "").strip().lower()
        if not q:
            return {"ok": False, "error": "bad_request", "reason": "Provide name_query or candidate_user_id"}
        # Pull candidate profiles and filter by name locally
        for uid in applied_ids:
            snap = db.collection("jobseekers").document(uid).get()
            if not snap.exists:
                continue
            prof = snap.to_dict() or {}
            pi = prof.get("personal_info", {}) or {}
            name = " ".join([str(pi.get("first_name") or "").strip(), str(pi.get("last_name") or "").strip()]).strip() or pi.get("display_name") or uid
            if q in name.lower():
                targets.append(uid)

        if not targets:
            return {"ok": True, "found": 0, "insights": []}

    # Build insights
    insights = []
    for uid in targets:
        ps = db.collection("jobseekers").document(uid).get()
        pd = ps.to_dict() or {}
        pi = pd.get("personal_info", {}) or {}
        bg = pd.get("background_info", {}) or {}
        insights.append({
            "user_id": uid,
            "name": " ".join([str(pi.get("first_name") or "").strip(), str(pi.get("last_name") or "").strip()]).strip() or pi.get("display_name") or uid,
            "skills": pd.get("skills", []),
            "yoe": bg.get("yoe"),
            "summary": (pd.get("resume_summary") or "")[:500],
            "interests": bg.get("interests", []),
            "last_updated": pd.get("updated_at"),
        })

    return {"ok": True, "found": len(insights), "insights": insights}

# ------- ACCEPT / REJECT CANDIDATE --------
@mcp.tool(name="poster_update_candidate_status")
def poster_update_candidate_status(
    user_id: Annotated[str, Field(description="Auth UID of the jobposter")],
    job_id: Annotated[str, Field(description="Job id")],
    candidate_user_id: Annotated[str, Field(description="Jobseeker UID")],
    decision: Annotated[Literal["accepted","rejected","pending"], Field(description="Set to accepted / rejected / pending")] = "pending",
) -> dict:
    """Pro: Accept/reject/pending a candidate for your job."""
    db = get_db()

    if _resolve_role(db, user_id) != "jobposter":
        return {"ok": False, "error": "forbidden", "reason": "Poster-only tool"}
    sub = verify_subscription(user_id=user_id, feature="poster_pro_filters")
    if not sub.get("allowed"):
        return {"ok": False, "error": "not_allowed", "reason": sub.get("reason")}

    err = _assert_job_ownership(db, user_id, job_id)
    if err:
        return err

    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

    # Ensure candidate actually applied
    seeker_doc = db.collection("jobseekers").document(candidate_user_id).collection("jobs_applied").document(job_id)
    seeker_snap = seeker_doc.get()
    if not seeker_snap.exists:
        return {"ok": False, "error": "not_found", "reason": "Candidate has not applied to this job"}

    batch = db.batch()
    batch.set(
        db.collection("jobs").document(job_id).collection("applications").document(candidate_user_id),
        {"user_id": candidate_user_id, "job_id": job_id, "status": decision, "updated_at": now_ms},
        merge=True,
    )
    batch.set(
        seeker_doc,
        {"status": decision, "updated_at": now_ms},
        merge=True,
    )
    batch.commit()

    return {"ok": True, "job_id": job_id, "user_id": candidate_user_id, "status": decision}

# --- MEMORY TOOLS (Firestore) ---
@mcp.tool()
def get_conversation_history(
    user_id: Annotated[str, Field(description="Auth UID")],
    session_id: Annotated[str, Field(description="Session id for this chat")],
    limit: Annotated[int, Field(ge=1, le=50, description="How many recent messages")] = 6
) -> dict:
    """Return last N messages for a session, newest last."""
    db = get_db()
    msgs = (db.collection("chat_sessions").document(session_id)
              .collection("messages")
              .order_by("created_at", direction="DESCENDING")
              .limit(limit).get())
    out = [{"role": m.to_dict().get("role"),
            "content": m.to_dict().get("content"),
            "created_at": m.to_dict().get("created_at")} for m in msgs]
    return {"messages": list(reversed(out))}

@mcp.tool()
def store_chat_messages(
    user_id: Annotated[str, Field(description="Auth UID")],
    session_id: Annotated[str, Field(description="Session id")],
    messages: Annotated[List[dict], Field(description="[{role, content}]")]
) -> dict:
    """Append messages to history."""
    db = get_db()
    now = int(datetime.now(timezone.utc).timestamp()*1000)
    sess_ref = db.collection("chat_sessions").document(session_id)
    sess_ref.set({"user_id": user_id, "started_at": now, "last_active_at": now}, merge=True)
    batch = db.batch()
    for m in messages:
        ref = sess_ref.collection("messages").document()
        batch.set(ref, {"role": m.get("role"), "content": m.get("content"), "created_at": now})
    batch.commit()
    return {"ok": True}

def main() -> None:
    """
    Package entrypoint:
    - load .env + initialize Firebase Admin
    - import any extra tool modules (so @mcp.tool decorators register)
    - start the MCP server
    """
    init_agent_tools()

    mcp.run()

if __name__ == "__main__":
    main()
