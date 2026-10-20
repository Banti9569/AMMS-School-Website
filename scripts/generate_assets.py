import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs("static/images/school", exist_ok=True)
os.makedirs("static/images/staff", exist_ok=True)

# Curated palette for Al Majid Mission School (Emerald Green & Warm Gold & Modern Slate)
PALETTES = {
    "hero_campus.jpg": ("#064e3b", "#047857", "Al Majid Mission School", "Campus & Main Administrative Building - Hazipur"),
    "hero_classroom.jpg": ("#1e3a8a", "#0284c7", "Smart Classrooms", "Interactive Learning & Holistic Education"),
    "hero_library.jpg": ("#78350f", "#b45309", "Central Library", "Rich Collection of Islamic, Scientific & Academic Books"),
    "hero_sports.jpg": ("#14532d", "#15803d", "Sports & Athletics", "Football, Cricket & Track Events"),
    
    "campus_garden.jpg": ("#065f46", "#10b981", "Green Campus", "Eco-friendly, serene environment for learning"),
    "science_lab.jpg": ("#0f766e", "#14b8a6", "Advanced Science Lab", "Physics, Chemistry & Biology Practical Training"),
    "computer_lab.jpg": ("#1e293b", "#3b82f6", "Modern Computer Lab", "Equipped with high-speed Internet and coding tools"),
    "annual_function.jpg": ("#831843", "#db2777", "Annual Cultural Fest", "Exhibition of student talents and cultural heritage"),
    "art_craft.jpg": ("#701a75", "#c026d3", "Art & Calligraphy", "Fostering creativity, sketching and Islamic calligraphy"),
    "students_reading.jpg": ("#134e4a", "#2dd4bf", "Reading Circle", "Nurturing curiosity and strong moral values"),
    "sports_day.jpg": ("#9a3412", "#ea580c", "Annual Sports Meet", "Championing physical fitness and sportsmanship"),
    "morning_assembly.jpg": ("#1e3a8a", "#3b82f6", "Morning Assembly", "Daily prayers, moral lectures and national anthem"),
}

STAFF_PALETTES = {
    "principal.jpg": ("#0f5132", "#198754", "Janab Maqsood Alam", "Principal & Academic Director", "M.Sc., B.Ed (22+ Yrs Exp)"),
    "teacher_math.jpg": ("#1e3a8a", "#2563eb", "Shabana Parveen", "Head of Mathematics", "M.Sc. Applied Maths, B.Ed"),
    "teacher_science.jpg": ("#0f766e", "#0d9488", "Dr. Arifuzzaman Mondal", "Senior Science Faculty", "Ph.D. in Physics, B.Ed"),
    "teacher_english.jpg": ("#78350f", "#d97706", "Syed Rehan Ali", "English Literature & Grammar", "M.A. English (Gold Medalist)"),
    "teacher_bengali.jpg": ("#831843", "#be185d", "Nasreen Sultana", "Bengali Language & Culture", "M.A. Bengali, B.Ed"),
    "teacher_computer.jpg": ("#1e293b", "#475569", "Tanvir Ahmed", "Computer Science & IT", "B.Tech (CSE), MCA"),
}

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def create_rich_card(filename, bg1, bg2, title, subtitle, extra=""):
    w, h = (1200, 750) if "hero_" in filename else (800, 560)
    img = Image.new('RGB', (w, h), color=hex_to_rgb(bg1))
    draw = ImageDraw.Draw(img)
    
    # Smooth horizontal/diagonal gradient
    c1 = hex_to_rgb(bg1)
    c2 = hex_to_rgb(bg2)
    for y in range(h):
        r = int(c1[0] + (c2[0] - c1[0]) * (y / h))
        g = int(c1[1] + (c2[1] - c1[1]) * (y / h))
        b = int(c1[2] + (c2[2] - c1[2]) * (y / h))
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    
    # Decorative geometry
    overlay_color = (255, 255, 255, 20)
    for i in range(0, w, 60):
        draw.line([(i, 0), (i + 150, h)], fill=(255, 255, 255, 12), width=1)
    
    # Elegant border
    draw.rectangle([20, 20, w-20, h-20], outline=(255, 255, 255, 80), width=2)
    draw.rectangle([26, 26, w-26, h-26], outline=(255, 215, 0, 100), width=1)

    # Badges and headers
    draw.text((60, 60), "AL MAJID MISSION SCHOOL - HAZIPUR", fill=(255, 215, 0))
    
    # Center text
    draw.text((60, h//2 - 40), title, fill=(255, 255, 255))
    draw.text((60, h//2 + 20), subtitle, fill=(220, 230, 240))
    if extra:
        draw.text((60, h//2 + 70), extra, fill=(255, 215, 0))
        
    draw.text((60, h - 70), "Dedicated to Academic Excellence & Islamic Moral Values", fill=(200, 220, 210))
    return img

# Generate School Images
for fname, (bg1, bg2, title, subtitle) in PALETTES.items():
    filepath = os.path.join("static/images/school", fname)
    img = create_rich_card(fname, bg1, bg2, title, subtitle)
    img.save(filepath, "JPEG", quality=90)

# Generate Staff Images
for fname, (bg1, bg2, name, role, cred) in STAFF_PALETTES.items():
    filepath = os.path.join("static/images/staff", fname)
    img = create_rich_card(fname, bg1, bg2, name, role, cred)
    img.save(filepath, "JPEG", quality=90)

print("Generated all school and staff fallback assets successfully!")
