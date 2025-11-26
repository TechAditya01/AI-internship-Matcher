import random
import sys

try:
    from app import create_app
    from extensions import db
    from models import Admin, Department, Internship
except ModuleNotFoundError as e:
    missing = str(e).split()[-1].strip("'\n")
    print(f"Missing dependency: {missing}")
    print()
    print("To run this seeder you need the project dependencies installed in your virtualenv.")
    print("Activate your venv and run:")
    print()
    print("    & .\\venv\\Scripts\\Activate.ps1")
    print("    pip install -r requirements.txt")
    print()
    print("Then re-run:    python seed.py")
    sys.exit(1)

app = create_app()

print("Using DB:", app.config["SQLALCHEMY_DATABASE_URI"])

app.app_context().push()

admin = Admin.query.first()
if not admin:
    admin = Admin(
        email="admin@internship.gov.in",
        name="System Administrator"
    )
    admin.set_password("Admin@123")
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin created successfully!")
    print(f"Email: admin@internship.gov.in")
    print(f"Password: Admin@123")
else:
    print("✅ Admin already exists!")
    print(f"Email: {admin.email}")

# ✅ Step 1: Get an existing admin
admin = Admin.query.first()
if not admin:
    raise Exception("❌ No admin found! Please run create_admin.py first.")

# ✅ Step 2: Departments to seed
departments = [
    {
        "name": "National e-Governance Division",
        "email": "negd@meity.gov.in",
        "password": "Negd@123",
        "ministry": "Ministry of Electronics and IT",
        "department_type": "Central",
        "location": "New Delhi, Delhi",
        "contact_person": "Rakesh Sharma",
        "contact_phone": "9876543210",
        "description": "Works on implementing Digital India initiatives."
    },
    {
        "name": "Department of Higher Education",
        "email": "dhe@mhrd.gov.in",
        "password": "Edu@123",
        "ministry": "Ministry of Education",
        "department_type": "Central",
        "location": "New Delhi, Delhi",
        "contact_person": "Anjali Verma",
        "contact_phone": "9876501234",
        "description": "Handles policy-making and research in higher education."
    },
    {
        "name": "Department of Health Research",
        "email": "dhr@mohfw.gov.in",
        "password": "Health@123",
        "ministry": "Ministry of Health and Family Welfare",
        "department_type": "Central",
        "location": "Pune, Maharashtra",
        "contact_person": "Dr. Vivek Joshi",
        "contact_phone": "9811122233",
        "description": "Promotes and funds health research in medical institutions."
    },
    {
        "name": "Department of Renewable Energy",
        "email": "dre@mnre.gov.in",
        "password": "Green@123",
        "ministry": "Ministry of New and Renewable Energy",
        "department_type": "Central",
        "location": "Bengaluru, Karnataka",
        "contact_person": "Priya Nair",
        "contact_phone": "9823345567",
        "description": "Develops policies for solar, wind, and renewable energy."
    },
    {
        "name": "Department of Skill Development & Entrepreneurship",
        "email": "dsde@msde.gov.in",
        "password": "Skill@123",
        "ministry": "Ministry of Skill Development and Entrepreneurship",
        "department_type": "Central",
        "location": "Lucknow, Uttar Pradesh",
        "contact_person": "Amit Kumar",
        "contact_phone": "9812233445",
        "description": "Focuses on skilling programs and entrepreneurship development."
    },
    {
        "name": "Department of Animal Husbandry & Dairying",
        "email": "dahd@agricoop.gov.in",
        "password": "Dairy@123",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "department_type": "Central",
        "location": "Jaipur, Rajasthan",
        "contact_person": "Sunita Mehta",
        "contact_phone": "9877709876",
        "description": "Works on livestock management and dairy development."
    },
    {
        "name": "Department of Water Resources",
        "email": "dwr@jalshakti.gov.in",
        "password": "Water@123",
        "ministry": "Ministry of Jal Shakti",
        "department_type": "Central",
        "location": "Varanasi, Uttar Pradesh",
        "contact_person": "Rajeev Pandey",
        "contact_phone": "9811456789",
        "description": "Manages water resources and Ganga rejuvenation projects."
    },
    {
        "name": "Department of Tourism",
        "email": "dot@tourism.gov.in",
        "password": "Tour@123",
        "ministry": "Ministry of Tourism",
        "department_type": "Central",
        "location": "Goa, Goa",
        "contact_person": "Kavita Menon",
        "contact_phone": "9878891234",
        "description": "Promotes tourism development and cultural heritage."
    },
    {
        "name": "Department of Environment & Climate Change",
        "email": "decc@moef.gov.in",
        "password": "Env@123",
        "ministry": "Ministry of Environment, Forest and Climate Change",
        "department_type": "Central",
        "location": "Bhopal, Madhya Pradesh",
        "contact_person": "Arun Mishra",
        "contact_phone": "9819912345",
        "description": "Focuses on environmental protection and climate policies."
    },
    {
        "name": "Department of Transportation",
        "email": "dotrans@transport.gov.in",
        "password": "Trans@123",
        "ministry": "Ministry of Road Transport and Highways",
        "department_type": "Central",
        "location": "Mumbai, Maharashtra",
        "contact_person": "Neha Kulkarni",
        "contact_phone": "9825567890",
        "description": "Works on road safety, transport infrastructure and logistics."
    }
]

# ✅ Step 3: Insert Departments
seeded_departments = []
for data in departments:
    existing = Department.query.filter_by(email=data["email"]).first()
    if not existing:
        dept = Department(
            name=data["name"],
            email=data["email"],
            ministry=data["ministry"],
            department_type=data["department_type"],
            location=data["location"],
            contact_person=data["contact_person"],
            contact_phone=data["contact_phone"],
            description=data["description"],
            created_by=admin.id
        )
        dept.set_password(data["password"])
        db.session.add(dept)
        seeded_departments.append(dept)

db.session.commit()
print(f"✅ {len(seeded_departments)} departments seeded!")

# ✅ Step 4: Seed ~100 Internships (10 each department)
titles = [
    "Research Intern", "Policy Analyst Intern", "Software Developer Intern",
    "AI Research Intern", "Data Science Intern", "Sustainability Analyst",
    "Community Outreach Intern", "Design Intern", "Business Analyst Intern",
    "Cybersecurity Intern", "Renewable Energy Analyst", "Transport Planning Intern"
]

skills = [
    "Python, SQL, Data Analysis", "Research, Writing, Communication",
    "Java, Spring Boot, APIs", "Machine Learning, Deep Learning",
    "Cloud Computing, AWS", "Policy Research, Economics",
    "Renewable Energy, Solar", "IoT, Sensors, Smart Devices",
    "GIS Mapping, Urban Planning", "Excel, Business Analytics"
]

courses = [
    "Computer Science", "Economics", "Public Policy",
    "Electrical Engineering", "Mechanical Engineering", "Environmental Science",
    "Data Science", "Civil Engineering", "Business Administration"
]

locations = [
    "New Delhi", "Mumbai", "Bengaluru", "Chennai",
    "Pune", "Lucknow", "Jaipur", "Kolkata", "Hyderabad"
]

for dept in Department.query.all():
    for i in range(10):  # 10 internships each
        title = random.choice(titles)
        existing = Internship.query.filter_by(title=title, company_id=dept.id).first()
        if not existing:
            internship = Internship(
                company_id=dept.id,
                title=f"{title} #{i+1}",
                description=f"{title} role at {dept.name}.",
                sector=random.choice(["Technology", "Policy", "Healthcare", "Energy", "Environment", "Transport"]),
                location=random.choice(locations),
                required_skills=random.choice(skills),
                preferred_course=random.choice(courses),
                min_cgpa=round(random.uniform(6.0, 8.5), 2),
                year_of_study_requirement=random.choice(["2nd Year", "3rd Year", "Final Year"]),
                total_positions=random.randint(2, 10),
                duration_months=random.randint(2, 6),
                stipend=random.choice([5000, 8000, 10000, 12000])
            )
            db.session.add(internship)

db.session.commit()
print("✅ 100+ internships seeded successfully!")
