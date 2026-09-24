"""Data for `python -m app.seed`. Edit this file to change who/what gets seeded.

Staff come from the A.W. Beattie "Instructors and Learning Support"
directory. Students, projects, and hours are PLACEHOLDERS: no real
student roster was provided.
"""

# (first, last, phone) for lead instructors and instructional assistants.
# A person listed under two programs (Paula Gibson) is created once.
PROGRAMS = [
    {
        "code": "ADV-DESIGN",
        "name": "Advertising Design",
        "instructors": [("Andrew", "Dumbeck", "412.847.1917"), ("Jessica", "Lingsch", "412.847.1951")],
        "assistants": [],
    },
    {
        "code": "AUTO-COLLISION",
        "name": "Automotive Collision Technology",
        "instructors": [("Pat", "Ciccone", "412.847.1941"), ("Joe", "Pelesky", "412.847.1942")],
        "assistants": [("Jim", "Meinert", "412.847.1841")],
    },
    {
        "code": "AUTO-TECH",
        "name": "Automotive Technology",
        "instructors": [
            ("Rick", "Bennett", "412.847.1948"),
            ("Jonathan", "Mansfield", "412.847.1922"),
            ("Nathan", "Monroe", "412.847.1949"),
        ],
        "assistants": [("Eric", "Szelc", "412.847.1948")],
    },
    {
        "code": "CARPENTRY",
        "name": "Carpentry/Building Construction",
        "instructors": [
            ("Cam", "Galloway", "412.847.1943"),
            ("John", "Brown", "412.847.1944"),
            ("Dale", "Dankmyer", "412.847.1956"),
        ],
        "assistants": [("Noah", "Pare", "412.847.1944")],
    },
    {
        "code": "COSMETOLOGY",
        "name": "Cosmetology",
        "instructors": [
            ("Sarah", "Nolan", "412.847.1927"),
            ("Cynthia", "Cazin", "412.847.1928"),
            ("Joani", "Zelazowski", "412.847.1929"),
            ("Stevie", "Slogan", "412.847.1923"),
        ],
        "assistants": [("Anna", "Yourish", "412.847.1928")],
    },
    {
        "code": "CULINARY",
        "name": "Culinary Arts",
        "instructors": [("Evelyn", "Sussman", "412.847.1916"), ("Aaron", "Yurek", "412.847.1933")],
        "assistants": [("Ashton", "Monroe", "412.847.1931")],
    },
    {
        "code": "DENTAL",
        "name": "Dental Careers",
        "instructors": [("Paula", "Gibson", "412.847.1936")],
        "assistants": [],
    },
    {
        "code": "ECE",
        "name": "Early Childhood Education",
        "instructors": [("Cari", "Ludwig", "412.847.1926")],
        "assistants": [("Diane", "Murray", "412.847.1926")],
    },
    {
        "code": "ERT",
        "name": "Emergency Response Technology",
        "instructors": [("Lee", "Silnutzer", "412.847.1938")],
        "assistants": [("Alexa", "Kurta", "412.847.1938")],
    },
    {
        "code": "HEALTH-NURSING",
        "name": "Health and Nursing Sciences",
        "instructors": [("Sarah", "Dietz", "412.847.1937"), ("Douglas", "Moran", "412.847.1939")],
        "assistants": [("Hilary", "Falo", "412.847.1937")],
    },
    {
        "code": "HVAC",
        "name": "HVAC",
        "instructors": [("Charles", "Wike", "412.847.1945"), ("Roy", "Hughes", "412.847.1946")],
        "assistants": [("Joe", "Goodyear", "412.847.1945")],
    },
    {
        "code": "NETWORK-CYBER",
        "name": "Network Engineering and Cyber Security",
        "instructors": [("Michael", "Lingsch", "412.847.1952")],
        "assistants": [("Michael", "Powers", "412.847.1952")],
    },
    {
        "code": "PHARMACY",
        "name": "Introduction to Pharmacy",
        "instructors": [("Paula", "Gibson", "412.847.1936")],
        "assistants": [],
    },
    {
        "code": "PASTRY",
        "name": "Pastry Arts",
        "instructors": [("Ken", "Morehead", "412.847.1932")],
        "assistants": [],
    },
    {
        "code": "ROBOTICS",
        "name": "Robotics Engineering Technology",
        "instructors": [("Michael", "Purucker", "412.847.1953")],
        "assistants": [],
    },
    {
        "code": "SPORTS-MED",
        "name": "Sports Medicine",
        "instructors": [("Darren", "Vtipil", "412.847.1964"), ("Chris", "Cowger", "412.847.1965")],
        "assistants": [],
    },
    {
        "code": "SURGICAL",
        "name": "Surgical Sciences",
        "instructors": [("Vincenzina", "Olszewski", "412.847.1954")],
        "assistants": [],
    },
    {
        "code": "VET-SCIENCE",
        "name": "Veterinary Sciences",
        "instructors": [("Megan", "Chuckery", "412.847.1883"), ("Jennifer", "Dumbeck", "412.847.1886")],
        "assistants": [],
    },
]

# (first, last, title, phone). Not tied to a program.
LEARNING_SUPPORT = [
    ("John", "Ellis", "Learning Support", "412.847.1931"),
    ("Erin", "Brennan", "Learning Support", "412.847.1924"),
    ("Bella", "Ellis", "Learning Support", "412.847.1959"),
    ("Erin", "Rushe", "Special Populations Coord.", "412.847.1925"),
    ("Jonathan", "Chuckery", "Educational Support", "412.847.1947"),
]

# (first, last, title, phone). School-wide; teachers can tag these on tasks.
INTEGRATION = [
    ("Gretchen", "Boyette", "English Language Learners Coord.", "412.847.1913"),
    ("Jen", "Groomes", "Math Integration", "412.847.1958"),
    ("Tad", "Thayer", "Science Integration", "412.847.1957"),
    ("Nicholas", "Sauer", "Student Engagement Specialist", "412.847.1934"),
]

# PLACEHOLDER students, by program code: (username, first, last).
STUDENTS = {
    "AUTO-TECH": [("student.alex", "Alex", "Chen"), ("student.jordan", "Jordan", "Patel")],
    "CULINARY": [("student.sam", "Sam", "Okafor"), ("student.taylor", "Taylor", "Brooks")],
    "COSMETOLOGY": [("student.morgan", "Morgan", "Lee")],
    "NETWORK-CYBER": [("student.casey", "Casey", "Reyes")],
}

# PLACEHOLDER work, by program code. Each task: (title, description,
# support staff as (first, last) of an INTEGRATION entry, or None).
# `status` maps username -> one status per task, in task order.
PROJECTS = {
    "AUTO-TECH": {
        "title": "Service Request #1042: 2014 Civic, check engine light",
        "description": "Customer reports a flashing check engine light and rough idle.",
        "tasks": [
            ("Pull and interpret the OBD-II code", "Use the scan tool and record the code.", ("Jen", "Groomes")),
            ("Inspect coils and plugs on the misfiring cylinder", "Swap test the coil to confirm.", None),
            ("Write up the repair order", "Parts, labor time, and customer notes.", None),
        ],
        "status": {
            "student.alex": ["complete", "in_progress", "not_started"],
            "student.jordan": ["in_progress", "not_started", "not_started"],
        },
    },
    "CULINARY": {
        "title": "Knife Skills & Mise en Place",
        "description": "Build foundational prep and sanitation skills for service.",
        "tasks": [
            ("Complete ServSafe module 1", "Read the sanitation module and pass the quiz.", ("Gretchen", "Boyette")),
            ("Plate a 3-course sample menu", "Plan and plate an appetizer, entree, and dessert.", None),
            ("Knife skills assessment", "Demonstrate julienne, brunoise, and chiffonade cuts.", ("Nicholas", "Sauer")),
        ],
        "status": {
            "student.sam": ["complete", "in_progress", "not_started"],
            "student.taylor": ["in_progress", "not_started", "not_started"],
        },
    },
    "COSMETOLOGY": {
        "title": "Client Consultation & Cut",
        "description": "Practice consultation, cutting, and color technique.",
        "tasks": [
            ("Complete sanitation certification", "Pass the state board sanitation exam.", None),
            ("Haircut technique assessment", "Demonstrate a graduated bob on a mannequin.", None),
            ("Color theory exam", "Written exam on the color wheel and formulation.", ("Tad", "Thayer")),
        ],
        "status": {"student.morgan": ["complete", "in_progress", "not_started"]},
    },
    "NETWORK-CYBER": {
        "title": "Home Lab Network Build",
        "description": "Design, subnet, and secure a small routed network.",
        "tasks": [
            ("Build home lab topology diagram", "Diagram a routed network with 4 VLANs.", ("Jen", "Groomes")),
            ("Complete Network+ practice exam", "Score 80% or better on the practice exam.", None),
            ("Set up a pfSense firewall", "Install pfSense and configure basic firewall rules.", None),
        ],
        "status": {"student.casey": ["complete", "not_started", "not_started"]},
    },
}

# PLACEHOLDER hours: (username, program code, days ago, minutes, summary).
WORK_LOGS = [
    ("student.morgan", "COSMETOLOGY", 1, 150, "Practiced foils and a blowout on the mannequin."),
    ("student.morgan", "COSMETOLOGY", 2, 180, "Clinic floor: two shampoo and style clients."),
    ("student.morgan", "COSMETOLOGY", 4, 120, "Sanitation review for the state board."),
    ("student.alex", "AUTO-TECH", 1, 90, "Pulled a P0301 code on the Civic."),
    ("student.casey", "NETWORK-CYBER", 2, 60, "Drew the lab topology and planned VLANs."),
]
