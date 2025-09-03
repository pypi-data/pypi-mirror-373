import os, time
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

# Path to your service account key JSON
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not cred_path or not os.path.exists(cred_path):
    raise SystemExit("Set GOOGLE_APPLICATION_CREDENTIALS to an absolute path of your Firebase service account JSON")

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

now = int(time.time() * 1000)

def add(doc_ref, data):
    doc_ref.set(data, merge=True)
    print("✓", doc_ref.path)

# ---------------------------
# jobseekers (sample)
# ---------------------------
add(db.collection("jobseekers").document("USER_001"), {
    "plan": "free",
    "locale": "AU",
    "personal_info": {"first_name":"Obie","last_name":"Ananda","dob":"2001-03-12"},
    "background_info": {"yoe":2,"summary":"Full-stack SWE focused on agents.","interests":["AI","Frontend","Infra"]},
    "skills": ["React","TypeScript","FastAPI","SQL"],
    "resume_summary": "2y building agentic systems…",
    "created_at": now
})

add(db.collection("jobseekers").document("USER_002"), {
    "plan": "pro",
    "locale": "SG",
    "personal_info": {"first_name":"Aisha","last_name":"Tan","dob":"1998-08-09"},
    "background_info": {"yoe":4,"summary":"Retail lead turned ops coordinator.","interests":["Operations","Customer Service"]},
    "skills": ["POS","Inventory","Excel","Scheduling"],
    "resume_summary": "Retail operations, rostering, and inventory control.",
    "created_at": now
})

# ---------------------------
# jobposters
# ---------------------------
add(db.collection("jobposters").document("POSTER_001"), {
    "company_name":"WerkDone",
    "contact_email":"hr@werkdone.example",
    "plan":"free",
    "created_at":now
})
add(db.collection("jobposters").document("POSTER_002"), {
    "company_name":"Harbor Health Clinic",
    "contact_email":"jobs@harborhealth.example",
    "plan":"pro",
    "created_at":now
})
add(db.collection("jobposters").document("POSTER_003"), {
    "company_name":"Metro Retail Group",
    "contact_email":"talent@metroretail.example",
    "plan":"free",
    "created_at":now
})
add(db.collection("jobposters").document("POSTER_004"), {
    "company_name":"BrightPath Education",
    "contact_email":"careers@brightpath.example",
    "plan":"pro",
    "created_at":now
})

# ---------------------------
# new jobposter (Google)
# ---------------------------
add(db.collection("jobposters").document("POSTER_005"), {
    "company_name": "Google",
    "contact_email": "careers@google.example",
    "plan": "pro",
    "created_at": now
})


# ---------------------------
# helper to add jobs
# ---------------------------
def add_job(job_id, title, company, poster_id, location, description, tags=None,
            salary_min=None, salary_max=None, source="ordal", status="open",
            edition_prices=None):
    add(db.collection("jobs").document(job_id), {
        "title": title,
        "company": company,
        "poster_id": poster_id,
        "location": location,
        "description": description,
        "tags": tags or [],
        "salary_min": salary_min,
        "salary_max": salary_max,
        "source": source,
        "edition_prices": edition_prices or {"standard": 0, "deluxe": 0},
        "created_at": now,
        "status": status
    })

# ---------------------------
# tech (5 jobs)
# ---------------------------
add_job(
    "JOB_001", "Frontend Engineer (Next.js)", "WerkDone", "POSTER_001",
    "Singapore",
    "Build UI for agent workflows and dashboards. Strong React/Next.js required.",
    tags=["React","Next.js","Tailwind","REST"], salary_min=70000, salary_max=90000
)
add_job(
    "JOB_002", "AI Agent Engineer", "Indie Labs", "POSTER_001",
    "Remote",
    "Design MCP tools and agents. Python, LangChain/FastAPI experience preferred.",
    tags=["Python","LangChain","FastAPI","SQL"], salary_min=80000, salary_max=110000
)
add_job(
    "JOB_003", "Backend Engineer (Python/FastAPI)", "WerkDone", "POSTER_001",
    "Singapore",
    "Own API design and microservices. Strong in Python and SQL.",
    tags=["Python","FastAPI","SQL","APIs"], salary_min=75000, salary_max=95000
)
add_job(
    "JOB_004", "Fullstack Developer", "Indie Labs", "POSTER_001",
    "Remote",
    "Deliver full-stack features with React + Node/FastAPI.",
    tags=["React","Node.js","FastAPI"], salary_min=70000, salary_max=95000
)
add_job(
    "JOB_005", "DevOps Engineer", "WerkDone", "POSTER_001",
    "Singapore",
    "Automate CI/CD, infra as code, and observability.",
    tags=["AWS","Terraform","CI/CD","Kubernetes"], salary_min=85000, salary_max=120000
)

# ---------------------------
# healthcare (5 jobs)
# ---------------------------
add_job(
    "JOB_100", "Registered Nurse", "Harbor Health Clinic", "POSTER_002",
    "Sydney, AU",
    "Provide patient care, coordinate with doctors, update charts, maintain safety protocols.",
    tags=["Nursing","AHPRA","Patient Care"], salary_min=65000, salary_max=90000
)
add_job(
    "JOB_101", "Medical Receptionist", "Harbor Health Clinic", "POSTER_002",
    "Melbourne, AU",
    "Front-desk operations, appointment scheduling, patient intake, insurance verification.",
    tags=["Reception","Scheduling","Customer Service"], salary_min=45000, salary_max=60000
)
add_job(
    "JOB_102", "Physiotherapist", "Harbor Health Clinic", "POSTER_002",
    "Sydney, AU",
    "Rehab plans, patient support, mobility therapy.",
    tags=["Physiotherapy","Rehab","Patient Care"], salary_min=70000, salary_max=95000
)
add_job(
    "JOB_103", "Healthcare Assistant", "Harbor Health Clinic", "POSTER_002",
    "Brisbane, AU",
    "Assist patients with daily needs, maintain records.",
    tags=["Support","Care","Patient Assistance"], salary_min=40000, salary_max=50000
)
add_job(
    "JOB_104", "Clinical Data Specialist", "Harbor Health Clinic", "POSTER_002",
    "Remote",
    "Manage clinical databases, ensure compliance.",
    tags=["Data","Compliance","Healthcare"], salary_min=75000, salary_max=95000
)
add_job(
    "JOB_006", "Software Engineer", "Google", "POSTER_005",
    "Sydney, AU",
    "Design, build, and maintain scalable systems at Google. Strong CS fundamentals, distributed systems experience, and coding excellence required.",
    tags=["C++","Java","Python","Distributed Systems","Cloud"],
    salary_min=120000, salary_max=160000
)

# ---------------------------
# retail & operations (5 jobs)
# ---------------------------
add_job(
    "JOB_200", "Store Manager", "Metro Retail Group", "POSTER_003",
    "Jakarta, ID",
    "Lead daily retail operations, manage staff rosters, optimize inventory and sales KPIs.",
    tags=["Retail","Inventory","Leadership","POS"], salary_min=55000000, salary_max=90000000
)
add_job(
    "JOB_201", "Warehouse Associate", "Metro Retail Group", "POSTER_003",
    "Singapore",
    "Pick/pack orders, manage stock movement, support last-mile logistics.",
    tags=["Logistics","Warehouse","Safety"], salary_min=32000, salary_max=42000
)
add_job(
    "JOB_202", "Retail Sales Associate", "Metro Retail Group", "POSTER_003",
    "Kuala Lumpur, MY",
    "Assist customers, manage POS, restock inventory.",
    tags=["Retail","Customer Service","POS"], salary_min=25000, salary_max=35000
)
add_job(
    "JOB_203", "Operations Coordinator", "Metro Retail Group", "POSTER_003",
    "Singapore",
    "Support daily ops, schedule staff, liaise with logistics.",
    tags=["Operations","Scheduling","Inventory"], salary_min=40000, salary_max=55000
)
add_job(
    "JOB_204", "E-commerce Specialist", "Metro Retail Group", "POSTER_003",
    "Remote",
    "Manage online orders, update product catalog, track KPIs.",
    tags=["E-commerce","Inventory","Digital"], salary_min=45000, salary_max=60000
)

# ---------------------------
# education (5 jobs)
# ---------------------------
add_job(
    "JOB_300", "Primary School Teacher", "BrightPath Education", "POSTER_004",
    "Perth, AU",
    "Plan and deliver lessons, assess learning outcomes, collaborate with parents/staff.",
    tags=["Teaching","Curriculum","Classroom Management"], salary_min=65000, salary_max=85000
)
add_job(
    "JOB_301", "Teacher’s Aide", "BrightPath Education", "POSTER_004",
    "Adelaide, AU",
    "Support classroom instruction, supervise activities, assist with learning materials.",
    tags=["Support","Education","Child Safety"], salary_min=42000, salary_max=52000
)
add_job(
    "JOB_302", "High School Math Teacher", "BrightPath Education", "POSTER_004",
    "Sydney, AU",
    "Teach secondary math curriculum, support student progress.",
    tags=["Math","Teaching","Curriculum"], salary_min=70000, salary_max=90000
)
add_job(
    "JOB_303", "Special Education Teacher", "BrightPath Education", "POSTER_004",
    "Melbourne, AU",
    "Support students with special needs in inclusive classrooms.",
    tags=["SpecialEd","Teaching","Support"], salary_min=68000, salary_max=88000
)
add_job(
    "JOB_304", "Curriculum Designer", "BrightPath Education", "POSTER_004",
    "Remote",
    "Design learning modules, update assessments, collaborate with teachers.",
    tags=["Curriculum","Design","Education"], salary_min=75000, salary_max=95000
)

# ---------------------------
# hospitality (5 jobs)
# ---------------------------
add_job(
    "JOB_400", "Barista", "Bean & Co.", "POSTER_003",
    "Brisbane, AU",
    "Prepare coffee/beverages, handle POS, maintain service standards.",
    tags=["Barista","Customer Service","POS"], salary_min=42000, salary_max=52000
)
add_job(
    "JOB_401", "Hotel Front Desk Agent", "HarborStay Hotels", "POSTER_003",
    "Gold Coast, AU",
    "Check-in/out guests, manage reservations, handle guest inquiries.",
    tags=["Hospitality","Front Desk","Reservations"], salary_min=45000, salary_max=55000
)
add_job(
    "JOB_402", "Restaurant Server", "Metro Retail Group", "POSTER_003",
    "Singapore",
    "Take orders, serve food, maintain table service.",
    tags=["Restaurant","Service","POS"], salary_min=35000, salary_max=42000
)
add_job(
    "JOB_403", "Chef de Partie", "HarborStay Hotels", "POSTER_003",
    "Sydney, AU",
    "Prepare meals, manage kitchen section, uphold hygiene.",
    tags=["Chef","Food","Kitchen"], salary_min=50000, salary_max=65000
)
add_job(
    "JOB_404", "Event Coordinator", "Bean & Co.", "POSTER_003",
    "Melbourne, AU",
    "Plan/manage events, liaise with clients, oversee logistics.",
    tags=["Events","Coordination","Hospitality"], salary_min=55000, salary_max=75000
)

# ---------------------------
# marketing & design (5 jobs)
# ---------------------------
add_job(
    "JOB_500", "Digital Marketing Specialist", "Indie Labs", "POSTER_001",
    "Remote",
    "Plan and execute campaigns, manage social accounts, track performance metrics.",
    tags=["SEO","SEM","Content","Analytics"], salary_min=60000, salary_max=80000
)
add_job(
    "JOB_501", "Graphic Designer", "Metro Retail Group", "POSTER_003",
    "Kuala Lumpur, MY",
    "Design POS materials, banners, social media creatives. Adobe CC required.",
    tags=["Photoshop","Illustrator","Branding"], salary_min=45000, salary_max=65000
)
add_job(
    "JOB_502", "Social Media Manager", "WerkDone", "POSTER_001",
    "Singapore",
    "Grow brand presence on social platforms, analyze campaigns.",
    tags=["Social Media","Content","Analytics"], salary_min=55000, salary_max=75000
)
add_job(
    "JOB_503", "Brand Strategist", "Indie Labs", "POSTER_001",
    "Remote",
    "Develop brand positioning, collaborate with design teams.",
    tags=["Branding","Strategy","Content"], salary_min=65000, salary_max=85000
)
add_job(
    "JOB_504", "UI/UX Designer", "WerkDone", "POSTER_001",
    "Singapore",
    "Design user-friendly interfaces, conduct user research.",
    tags=["UI","UX","Design","Figma"], salary_min=70000, salary_max=90000
)

# ---------------------------
# finance & admin (5 jobs)
# ---------------------------
add_job(
    "JOB_600", "Accounts Payable Officer", "Harbor Health Clinic", "POSTER_002",
    "Sydney, AU",
    "Process invoices, reconcile statements, support month-end close.",
    tags=["AP","Excel","Reconciliation"], salary_min=60000, salary_max=75000
)
add_job(
    "JOB_601", "Office Administrator", "WerkDone", "POSTER_001",
    "Singapore",
    "Coordinate meetings, manage documentation, assist HR and procurement.",
    tags=["Administration","Scheduling","Docs"], salary_min=38000, salary_max=48000
)
add_job(
    "JOB_602", "Financial Analyst", "Metro Retail Group", "POSTER_003",
    "Jakarta, ID",
    "Analyze financial reports, forecast, support budgeting.",
    tags=["Finance","Excel","Forecast"], salary_min=70000, salary_max=95000
)
add_job(
    "JOB_603", "Payroll Specialist", "Harbor Health Clinic", "POSTER_002",
    "Melbourne, AU",
    "Manage payroll, employee records, ensure compliance.",
    tags=["Payroll","Compliance","Excel"], salary_min=60000, salary_max=80000
)
add_job(
    "JOB_604", "Executive Assistant", "WerkDone", "POSTER_001",
    "Singapore",
    "Support executives with scheduling, travel, correspondence.",
    tags=["Executive","Scheduling","Docs"], salary_min=50000, salary_max=70000
)

# ---------------------------
# construction & field (5 jobs)
# ---------------------------
add_job(
    "JOB_700", "Site Supervisor", "BuildRight Constructors", "POSTER_003",
    "Melbourne, AU",
    "Oversee daily site works, safety compliance, subcontractor coordination.",
    tags=["Construction","OH&S","Coordination"], salary_min=75000, salary_max=95000
)
add_job(
    "JOB_701", "Electrician", "BuildRight Constructors", "POSTER_003",
    "Sydney, AU",
    "Install and maintain electrical systems, read schematics, ensure safety.",
    tags=["Electrical","Trade","Safety"], salary_min=70000, salary_max=90000
)
add_job(
    "JOB_702", "Civil Engineer", "BuildRight Constructors", "POSTER_003",
    "Perth, AU",
    "Plan and oversee civil works, liaise with contractors.",
    tags=["Engineering","Civil","Construction"], salary_min=85000, salary_max=110000
)
add_job(
    "JOB_703", "Carpenter", "BuildRight Constructors", "POSTER_003",
    "Brisbane, AU",
    "Woodwork, fittings, furniture installation on site.",
    tags=["Carpentry","Construction","Safety"], salary_min=60000, salary_max=80000
)
add_job(
    "JOB_704", "Plumber", "BuildRight Constructors", "POSTER_003",
    "Sydney, AU",
    "Install and repair piping systems in residential/commercial projects.",
    tags=["Plumbing","Construction","Safety"], salary_min=65000, salary_max=85000
)

print("Seeding complete.")
