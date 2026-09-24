"""Data for `python -m app.seed`. Edit this file to change what gets seeded.

Only the class program is created. People are NOT seeded: students and
teachers get their accounts the first time they sign in through Authelia
(see provisioning.py). The one exception is the school-wide integration
staff, who can be tagged on a task before they ever sign in.
"""

# The full A.W. Beattie staff directory, kept here for the CTE-wide
# version. On this branch only the program matching CLASS_PROGRAM_CODE is
# created, using its name from this list.
# (first, last, phone) for lead instructors and instructional assistants.
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


# School-wide support staff: (display name, title, phone).
INTEGRATION = [
    ("Gretchen Boyette", "English Language Learners Coord.", "412.847.1913"),
    ("Jen Groomes", "Math Integration", "412.847.1958"),
    ("Tad Thayer", "Science Integration", "412.847.1957"),
    ("Nicholas Sauer", "Student Engagement Specialist", "412.847.1934"),
]

# Starter work, added only when the class is first created. Each task: (title, description, support staff
# display name from INTEGRATION, or None). Every student gets every task.
PROJECTS = [
    {
        "title": "Home Lab Network Build",
        "description": "Design, subnet, and secure a small routed network.",
        "tasks": [
            ("Build home lab topology diagram", "Diagram a routed network with 4 VLANs.", "Jen Groomes"),
            ("Complete Network+ practice exam", "Score 80% or better on the practice exam.", None),
            ("Set up a pfSense firewall", "Install pfSense and configure basic firewall rules.", None),
        ],
    },
]
