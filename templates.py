"""100 CV template definitions. These are real selectable theme/layout presets."""
PALETTES = [
    ("Blue", "#2457C5"), ("Navy", "#17365D"), ("Black", "#222222"),
    ("Teal", "#087E8B"), ("Purple", "#7952B3"), ("Green", "#27864B"),
    ("Orange", "#D35400"), ("Gold", "#A67C32"), ("Red", "#B42318"),
    ("Slate", "#475569"),
]
LAYOUTS = ["Classic", "Modern", "Minimal", "Sidebar", "Elegant"]
CATEGORIES = {
    "professional": ("Professional", ["Modern Office", "Corporate", "Executive", "Business Analyst", "Management", "Administrative", "Finance", "Accounting", "Sales", "Customer Service"]),
    "student": ("Student & Graduate", ["Grade 12 Graduate", "First Job", "University Student", "Internship", "Scholarship", "Academic", "No Experience", "Volunteer", "Entry Level", "Training Program"]),
    "factory": ("Factory & Worker", ["Factory Worker", "Packaging Worker", "Warehouse", "Production Operator", "Quality Control", "Assembly Line", "Logistics", "Inventory Clerk", "Machine Operator", "General Worker"]),
    "technical": ("Technical & Engineering", ["Car Mechanic", "Automotive Technician", "Electrical Technician", "Electronics Technician", "Maintenance Technician", "Civil Engineer", "Mechanical Engineer", "Plumber", "Welder", "Technician"]),
    "digital": ("IT & Digital", ["Software Developer", "Web Developer", "IT Support", "Cybersecurity", "Data Analyst", "Graphic Designer", "UI UX Designer", "Digital Marketing", "Video Editor", "Content Creator"]),
    "service": ("Service & Hospitality", ["Cashier", "Retail Assistant", "Receptionist", "Hotel Staff", "Restaurant Staff", "Chef", "Barista", "Delivery Driver", "Security Guard", "Teacher Assistant"]),
    "health": ("Health & Education", ["Nursing Assistant", "Healthcare Worker", "Pharmacy Assistant", "Teacher", "Tutor", "Childcare Worker", "Lab Assistant", "Social Worker", "Trainer", "Research Assistant"]),
    "international": ("International & Special", ["International English", "ATS Friendly", "Europass Style", "Remote Work", "Career Change", "Freelancer", "Creative Portfolio", "Two Column", "Photo Resume", "Clean One Page"]),
    "hospitality2": ("Transport & Operations", ["Truck Driver", "Motorcycle Mechanic", "Automotive Service Advisor", "Purchasing Assistant", "Procurement", "Operations Officer", "Dispatch Officer", "Courier", "Travel Consultant", "Airline Ground Staff"]),
    "creative": ("Creative & Premium", ["Creative Purple", "Elegant Gold", "Premium Black", "Minimal White", "Green Professional", "Blue Sidebar", "Orange Accent", "Soft Pastel", "Modern Gradient", "Premium Profile"]),
}

TEMPLATES = []
for cat_key, (cat_name, names) in CATEGORIES.items():
    for i, name in enumerate(names):
        palette_name, hex_color = PALETTES[(i + len(TEMPLATES)) % len(PALETTES)]
        layout = LAYOUTS[(i + len(TEMPLATES)) % len(LAYOUTS)]
        TEMPLATES.append({
            "id": f"{cat_key}_{i+1:02d}",
            "name": name,
            "category": cat_name,
            "palette": palette_name,
            "color": hex_color,
            "layout": layout,
            "number": len(TEMPLATES) + 1,
        })
assert len(TEMPLATES) == 100

def get_template(template_id):
    return next((t for t in TEMPLATES if t["id"] == template_id), TEMPLATES[0])

def get_categories():
    return [(key, value[0]) for key, value in CATEGORIES.items()]

def templates_for_category(category_key):
    return [t for t in TEMPLATES if t["id"].startswith(category_key + "_")]
