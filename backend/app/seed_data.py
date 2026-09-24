"""Data for `python -m app.seed`. Edit this file to change what gets seeded.

Only the class program is seeded. People are NOT seeded: students and
teachers get their accounts the first time they sign in through Authelia
(see provisioning.py). The one exception is the school-wide integration
staff, who can be tagged on a task before they ever sign in.
"""

# The class program. Its code must match CLASS_PROGRAM_CODE in .env.
PROGRAM = {
    "code": "NETWORK-CYBER",
    "name": "Network Engineering and Cyber Security",
}

# School-wide support staff: (display name, title, phone).
INTEGRATION = [
    ("Gretchen Boyette", "English Language Learners Coord.", "412.847.1913"),
    ("Jen Groomes", "Math Integration", "412.847.1958"),
    ("Tad Thayer", "Science Integration", "412.847.1957"),
    ("Nicholas Sauer", "Student Engagement Specialist", "412.847.1934"),
]

# Starter work for the class. Each task: (title, description, support staff
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
