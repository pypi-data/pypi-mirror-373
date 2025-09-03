# mcp_profile_helpers.py
from typing import Optional, List
from google.cloud import firestore as gfs

FILLERS = {"gang","boss","pls","please","thanks","thank you","mate"}
ALIASES = {
    "js":"javascript","ts":"typescript","c sharp":"c#","csharp":"c#",
    "cpp":"c++","golang":"go","node":"node.js","b":"b programming language"
}

def parse_csv(v: Optional[str]) -> List[str]:
    if not v: return []
    return [s.strip() for s in v.split(",") if s.strip()]

def to_int_or_none(v) -> Optional[int]:
    if v is None: return None
    try:
        return int(v)
    except Exception:
        return None

def canon_token(s: str) -> str:
    s = s.strip().lower().replace("’","'")
    if s.endswith(" programming language"):
        s = s[:-len(" programming language")]
    return s

def parse_skills(raw: Optional[str]) -> List[str]:
    if not raw: return []
    vals = [s.strip() for s in raw.split(",") if s.strip()]
    out, seen = [], set()
    for v in vals:
        lc = v.lower()
        if lc in FILLERS: 
            continue
        canon = ALIASES.get(lc, v)
        key = canon.lower()
        if key not in seen:
            seen.add(key)
            out.append(canon)
    return out

def unique_case_preserve(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for s in items:
        k = s.lower()
        if k not in seen:
            seen.add(k); out.append(s)
    return out