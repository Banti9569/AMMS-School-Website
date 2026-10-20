import urllib.request
import os

images = {
    # Campus & Hero slider
    "static/images/school/hero_campus.jpg": "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=1200&q=80",
    "static/images/school/hero_classroom.jpg": "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=1200&q=80",
    "static/images/school/hero_library.jpg": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=1200&q=80",
    "static/images/school/hero_sports.jpg": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200&q=80",
    
    # Facilities & Gallery
    "static/images/school/campus_garden.jpg": "https://images.unsplash.com/photo-1562774053-701939374585?w=800&q=80",
    "static/images/school/science_lab.jpg": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=800&q=80",
    "static/images/school/computer_lab.jpg": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80",
    "static/images/school/annual_function.jpg": "https://images.unsplash.com/photo-1511578314322-379afb476865?w=800&q=80",
    "static/images/school/art_craft.jpg": "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=800&q=80",
    "static/images/school/students_reading.jpg": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=800&q=80",
    "static/images/school/sports_day.jpg": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800&q=80",
    "static/images/school/morning_assembly.jpg": "https://images.unsplash.com/photo-1577896851231-70ef18881754?w=800&q=80",
    
    # People
    "static/images/staff/principal.jpg": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=600&q=80",
    "static/images/staff/teacher_math.jpg": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=600&q=80",
    "static/images/staff/teacher_science.jpg": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&q=80",
    "static/images/staff/teacher_english.jpg": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&q=80",
    "static/images/staff/teacher_bengali.jpg": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=600&q=80",
    "static/images/staff/teacher_computer.jpg": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=600&q=80",
}

headers = {'User-Agent': 'Mozilla/5.0'}

for path, url in images.items():
    if not os.path.exists(path):
        try:
            print(f"Downloading {path}...")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as response, open(path, 'wb') as out_file:
                out_file.write(response.read())
            print(f"Saved: {path}")
        except Exception as e:
            print(f"Failed to download {path}: {e}")
