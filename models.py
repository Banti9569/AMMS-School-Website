import sqlite3
import os
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    os.makedirs(os.path.dirname(Config.DATABASE), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    # 1. Users (Admin and Parents)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL CHECK(role IN ('admin', 'parent')),
        username TEXT UNIQUE NOT NULL, -- Mobile number for parents, 'admin' or username for admin
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Students
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admission_no TEXT UNIQUE NOT NULL,
        roll_no INTEGER NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        class_name TEXT NOT NULL, -- e.g. 'Class I', 'Class V', 'Class VIII', 'Class X'
        section TEXT DEFAULT 'A',
        dob DATE,
        gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
        blood_group TEXT,
        parent_id INTEGER,
        address TEXT,
        emergency_contact TEXT,
        photo_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_id) REFERENCES users(id) ON DELETE SET NULL
    )
    """)

    # 3. Teachers & Staff
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        designation TEXT NOT NULL,
        qualification TEXT NOT NULL,
        subject TEXT NOT NULL,
        experience_years INTEGER DEFAULT 1,
        email TEXT,
        phone TEXT,
        photo_url TEXT,
        bio TEXT,
        display_order INTEGER DEFAULT 0
    )
    """)

    # 4. Notices & Announcements
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT DEFAULT 'General' CHECK(category IN ('General', 'Academic', 'Exam', 'Holiday', 'Sports', 'Admission')),
        content TEXT NOT NULL,
        is_pinned INTEGER DEFAULT 0,
        target_audience TEXT DEFAULT 'All' CHECK(target_audience IN ('All', 'Parents', 'Public')),
        file_url TEXT,
        published_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 5. Gallery
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gallery (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT DEFAULT 'Campus' CHECK(category IN ('Campus', 'Academics', 'Sports', 'Cultural', 'Science Lab', 'Celebration')),
        image_url TEXT NOT NULL,
        caption TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 6. Attendance
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        date DATE NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Present', 'Absent', 'Late', 'Excused')),
        remarks TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(student_id, date),
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    # 7. Results / Marks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        exam_name TEXT NOT NULL, -- e.g., 'First Term Evaluation 2026', 'Mid-Term Exam 2026'
        class_name TEXT NOT NULL,
        subject TEXT NOT NULL,
        marks_obtained REAL NOT NULL,
        max_marks REAL NOT NULL DEFAULT 100,
        grade TEXT,
        remarks TEXT,
        exam_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    # 8. Fees
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fee_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        fee_title TEXT NOT NULL, -- e.g., 'Monthly Tuition - October 2026', 'Annual Session Fee 2026'
        amount REAL NOT NULL,
        paid_amount REAL DEFAULT 0,
        due_date DATE NOT NULL,
        payment_date DATE,
        payment_status TEXT DEFAULT 'Pending' CHECK(payment_status IN ('Paid', 'Pending', 'Partial')),
        payment_method TEXT,
        receipt_no TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    # 9. Timetable
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS timetables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT NOT NULL,
        day_of_week TEXT NOT NULL CHECK(day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')),
        period_no INTEGER NOT NULL,
        period_time TEXT NOT NULL, -- e.g., '09:00 AM - 09:45 AM'
        subject TEXT NOT NULL,
        teacher_name TEXT,
        room_no TEXT DEFAULT 'Room 101'
    )
    """)

    # 10. CMS Pages Content
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pages_content (
        key TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 11. Contact Messages
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contact_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def seed_data_if_empty():
    conn = get_db()
    cursor = conn.cursor()

    # Check if admin exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    if cursor.fetchone()[0] == 0:
        # Seed Admin
        admin_pass = generate_password_hash("admin123")
        cursor.execute("""
        INSERT INTO users (role, username, password_hash, full_name, email, phone)
        VALUES ('admin', 'admin', ?, 'Chief Administrator', 'admin@almajidmissionschool.edu.in', '9434056789')
        """, (admin_pass,))

        # Seed Parents
        parent_pass = generate_password_hash("parent123")
        cursor.execute("""
        INSERT INTO users (role, username, password_hash, full_name, email, phone)
        VALUES 
        ('parent', '9876543210', ?, 'Md. Rafiqul Islam', 'rafiqul.islam@gmail.com', '9876543210'),
        ('parent', '9876543211', ?, 'Nurul Hasan Mondal', 'nurul.hasan@yahoo.com', '9876543211'),
        ('parent', '9876543212', ?, 'Abdul Karim Sk', 'karim.sk786@gmail.com', '9876543212')
        """, (parent_pass, parent_pass, parent_pass))
        
        rafiq_id = 2
        nurul_id = 3
        karim_id = 4

        # Seed Students
        cursor.execute("""
        INSERT INTO students (admission_no, roll_no, first_name, last_name, class_name, section, dob, gender, blood_group, parent_id, address, emergency_contact, photo_url)
        VALUES 
        ('AMMS-2024-081', 12, 'Samiul', 'Haque', 'Class VIII', 'A', '2012-04-15', 'Male', 'O+', ?, 'Hazipur Purba Para, Hazipur, 731245', '9876543210', '/static/images/school/students_reading.jpg'),
        ('AMMS-2025-052', 7, 'Ayesha', 'Khatun', 'Class V', 'B', '2015-08-22', 'Female', 'A+', ?, 'Hazipur Dakshin Para, Hazipur, 731245', '9876543211', '/static/images/school/students_reading.jpg'),
        ('AMMS-2023-094', 4, 'Farhan', 'Akhtar', 'Class IX', 'A', '2011-01-10', 'Male', 'B+', ?, 'Hazipur Dakshin Para, Hazipur, 731245', '9876543211', '/static/images/school/hero_classroom.jpg'),
        ('AMMS-2024-063', 18, 'Zoya', 'Parveen', 'Class VI', 'A', '2014-06-19', 'Female', 'AB+', ?, 'Hazipur Station Road, Hazipur, 731245', '9876543212', '/static/images/school/students_reading.jpg')
        """, (rafiq_id, nurul_id, nurul_id, karim_id))

        # Seed Teachers
        cursor.execute("""
        INSERT INTO teachers (name, designation, qualification, subject, experience_years, email, phone, photo_url, bio, display_order)
        VALUES 
        ('Janab Maqsood Alam', 'Principal & Academic Director', 'M.Sc. (Physics), B.Ed', 'Administration & Science Guidance', 22, 'principal@almajidmissionschool.edu.in', '9434056780', '/static/images/staff/principal.jpg', 'Dedicated to combining rigorous modern scientific education with exemplary moral discipline and character formation.', 1),
        ('Mrs. Shabana Parveen', 'Senior Teacher & HOD Mathematics', 'M.Sc. (Applied Mathematics), B.Ed', 'Mathematics & Mental Ability', 14, 'shabana.math@almajidmissionschool.edu.in', '9832011223', '/static/images/staff/teacher_math.jpg', 'Specialist in making core mathematical concepts intuitive, engaging, and enjoyable for school students.', 2),
        ('Dr. Arifuzzaman Mondal', 'Assistant Teacher (Physical Sciences)', 'Ph.D. in Physics, B.Ed', 'Physical Science & Laboratory', 11, 'arif.science@almajidmissionschool.edu.in', '9734022334', '/static/images/staff/teacher_science.jpg', 'Passionate science educator fostering research mindset, practical experiments and scientific inquiry.', 3),
        ('Syed Rehan Ali', 'Assistant Teacher (English)', 'M.A. English Literature (Gold Medalist), B.Ed', 'English Language & Spoken English', 9, 'rehan.english@almajidmissionschool.edu.in', '9641033445', '/static/images/staff/teacher_english.jpg', 'Focuses on phonetics, communicative English fluency, reading habits, and creative composition skills.', 4),
        ('Nasreen Sultana', 'Assistant Teacher (Bengali & History)', 'M.A. Bengali, B.Ed', 'Bengali Literature & Social Studies', 8, 'nasreen.bengali@almajidmissionschool.edu.in', '9593044556', '/static/images/staff/teacher_bengali.jpg', 'Expert in rich regional literature, ethical studies, and cultural heritage education.', 5),
        ('Tanvir Ahmed', 'Computer Instructor & Lab In-charge', 'B.Tech in Computer Science, MCA', 'Computer Science & Coding', 6, 'tanvir.it@almajidmissionschool.edu.in', '9475055667', '/static/images/staff/teacher_computer.jpg', 'Teaching modern computing, office applications, Scratch logic, and foundational programming.', 6)
        """)

        # Seed Notices
        today = date.today()
        cursor.execute("""
        INSERT INTO notices (title, category, content, is_pinned, target_audience, published_date)
        VALUES 
        ('Admissions Open for Academic Session 2026-27 (Nursery to Class IX)', 'Admission', 'Admissions are cordially invited for the upcoming academic session 2026-27 for Nursery, KG, and Classes I to IX. Application forms are available at the school administrative counter between 9:00 AM and 2:00 PM on all working days. Early bird concessions are available for deserving and meritorious students.', 1, 'All', ?),
        ('Mid-Term Examination 2026 Schedule & Routine Published', 'Exam', 'The Mid-Term Examinations for Classes V to X will commence from November 10, 2026. Detailed timetable and syllabus distributions have been provided to all students and uploaded to the Parent Portal. Parents are requested to ensure regular revision at home.', 1, 'All', ?),
        ('Celebration of Annual Sports Meet and Athletic Competition', 'Sports', 'The Annual School Sports Day will be held on the school campus grounds on December 18, 2026. Events will include 100m sprint, relay race, high jump, tug of war, and gymnastics drill. Students should register their names with their physical education teachers.', 0, 'All', ?),
        ('Parent-Teacher Meeting (PTM) for Classes VI - X', 'Academic', 'A mandatory Parent-Teacher Meeting will take place this Saturday from 10:00 AM to 1:00 PM. Parents can review the progress reports, attendance trends, and behavioral feedback of their wards with class teachers.', 0, 'Parents', ?),
        ('Notice regarding Winter Uniform and School Timings Update', 'General', 'Effective November 1st, all students are advised to attend in official school navy green sweaters with the school monogram crest. School arrival time will remain 8:30 AM sharp.', 0, 'All', ?)
        """, (
            today.isoformat(),
            (today - timedelta(days=2)).isoformat(),
            (today - timedelta(days=5)).isoformat(),
            (today - timedelta(days=8)).isoformat(),
            (today - timedelta(days=12)).isoformat()
        ))

        # Seed Gallery
        cursor.execute("""
        INSERT INTO gallery (title, category, image_url, caption)
        VALUES 
        ('Main Academic Campus Building', 'Campus', '/static/images/school/hero_campus.jpg', 'Panoramic view of Al Majid Mission School campus in Hazipur with lush greenery.'),
        ('Smart Digital Classroom Session', 'Academics', '/static/images/school/hero_classroom.jpg', 'Interactive classroom setup with visual educational aids and collaborative seating.'),
        ('Well-Stocked Central Library', 'Campus', '/static/images/school/hero_library.jpg', 'Students enjoying reading hours in our quiet and resourceful school library.'),
        ('High-Tech Physics & Chemistry Laboratory', 'Science Lab', '/static/images/school/science_lab.jpg', 'Hands-on practical training under the supervision of experienced science teachers.'),
        ('Modern Computer & IT Lab', 'Academics', '/static/images/school/computer_lab.jpg', 'Computer education starting from primary classes to equip children with 21st-century digital skills.'),
        ('Annual Sports & Athletic Meet', 'Sports', '/static/images/school/sports_day.jpg', 'Track events and sportsmanship displayed during our vibrant annual sports day.'),
        ('Annual Cultural & Recitation Program', 'Cultural', '/static/images/school/annual_function.jpg', 'Student recitations, ethical skits, and prize distribution ceremony.'),
        ('Fine Arts & Islamic Calligraphy Exhibition', 'Cultural', '/static/images/school/art_craft.jpg', 'Creative masterpieces handcrafted by students across all grade levels.')
        """)

        # Seed Attendance for Student 1 (Samiul Haque - id 1) and Student 2 (Ayesha Khatun - id 2)
        # 25 school days
        for day_offset in range(1, 26):
            rec_date = (today - timedelta(days=day_offset))
            if rec_date.weekday() != 6: # skip Sunday
                stat_samiul = 'Present' if day_offset not in (4, 11) else ('Absent' if day_offset == 4 else 'Late')
                stat_ayesha = 'Present' if day_offset not in (7, 18) else ('Absent' if day_offset == 7 else 'Late')
                cursor.execute("""
                INSERT OR IGNORE INTO attendance (student_id, date, status, remarks)
                VALUES 
                (1, ?, ?, ?),
                (2, ?, ?, ?)
                """, (
                    rec_date.isoformat(), stat_samiul, 'Routine Attendance' if stat_samiul=='Present' else ('Fever' if stat_samiul=='Absent' else 'Delayed Bus'),
                    rec_date.isoformat(), stat_ayesha, 'Routine Attendance' if stat_ayesha=='Present' else ('Doctor appointment' if stat_ayesha=='Absent' else 'Rain delay')
                ))

        # Seed Results for Samiul Haque (id 1, Class VIII)
        exam_title = 'First Term Examination 2026'
        subjects_marks = [
            ('Bengali 1st Language', 88, 100, 'A+', 'Very good creative writing and comprehension.'),
            ('English 2nd Language', 84, 100, 'A+', 'Strong grasp of grammar and vocabulary.'),
            ('Mathematics', 92, 100, 'AA', 'Outstanding problem solving and geometry skills.'),
            ('Physical Science', 86, 100, 'A+', 'Clear understanding of physics fundamentals.'),
            ('Life Science', 90, 100, 'AA', 'Excellent botanical and zoological diagrams.'),
            ('History', 79, 100, 'A', 'Good narrative accuracy and chronological sense.'),
            ('Geography', 85, 100, 'A+', 'Accurate map pointing and topographical notes.'),
            ('Computer Science', 95, 100, 'AA', 'Top performance in programming logic.')
        ]
        for sub, marks, max_m, grd, rem in subjects_marks:
            cursor.execute("""
            INSERT INTO results (student_id, exam_name, class_name, subject, marks_obtained, max_marks, grade, remarks, exam_date)
            VALUES (1, ?, 'Class VIII', ?, ?, ?, ?, ?, '2026-05-20')
            """, (exam_title, sub, marks, max_m, grd, rem))

        # Results for Ayesha Khatun (id 2, Class V)
        ayesha_marks = [
            ('Bengali', 92, 100, 'AA', 'Superb handwriting and recitation.'),
            ('English', 87, 100, 'A+', 'Fluent reading and sentence construction.'),
            ('Mathematics', 89, 100, 'A+', 'Quick mental arithmetic calculation.'),
            ('Environmental Studies', 94, 100, 'AA', 'High awareness of nature and hygiene.'),
            ('Arabic & Moral Values', 96, 100, 'AA', 'Impeccable recitation and good conduct.'),
            ('Art & Craft', 90, 100, 'AA', 'Vibrant sketches and neat coloring.')
        ]
        for sub, marks, max_m, grd, rem in ayesha_marks:
            cursor.execute("""
            INSERT INTO results (student_id, exam_name, class_name, subject, marks_obtained, max_marks, grade, remarks, exam_date)
            VALUES (2, ?, 'Class V', ?, ?, ?, ?, ?, '2026-05-22')
            """, (exam_title, sub, marks, max_m, grd, rem))

        # Seed Fee Records
        cursor.execute("""
        INSERT INTO fee_records (student_id, fee_title, amount, paid_amount, due_date, payment_date, payment_status, payment_method, receipt_no)
        VALUES 
        (1, 'Monthly Tuition Fee - October 2026', 1200.0, 1200.0, '2026-10-15', '2026-10-08', 'Paid', 'Cash Counter', 'REC-2026-1089'),
        (1, 'Quarterly Computer & Lab Fee', 600.0, 600.0, '2026-09-30', '2026-09-25', 'Paid', 'UPI', 'REC-2026-0942'),
        (1, 'Annual Session & Development Fee 2026', 3500.0, 3500.0, '2026-04-10', '2026-04-05', 'Paid', 'Bank Transfer', 'REC-2026-0412'),
        (1, 'Mid-Term Exam Fee November 2026', 450.0, 0.0, '2026-11-05', NULL, 'Pending', NULL, NULL),
        
        (2, 'Monthly Tuition Fee - October 2026', 950.0, 950.0, '2026-10-15', '2026-10-10', 'Paid', 'Cash Counter', 'REC-2026-1095'),
        (2, 'Annual Session Fee 2026', 2800.0, 2800.0, '2026-04-10', '2026-04-08', 'Paid', 'Cash Counter', 'REC-2026-0435'),
        (2, 'Mid-Term Exam Fee November 2026', 350.0, 0.0, '2026-11-05', NULL, 'Pending', NULL, NULL)
        """)

        # Seed Timetable for Class VIII
        timetable_entries = [
            ('Class VIII', 'Monday', 1, '09:00 AM - 09:45 AM', 'Mathematics', 'Mrs. Shabana Parveen'),
            ('Class VIII', 'Monday', 2, '09:45 AM - 10:30 AM', 'English Literature', 'Syed Rehan Ali'),
            ('Class VIII', 'Monday', 3, '10:45 AM - 11:30 AM', 'Physical Science', 'Dr. Arifuzzaman Mondal'),
            ('Class VIII', 'Monday', 4, '11:30 AM - 12:15 PM', 'Bengali', 'Nasreen Sultana'),
            ('Class VIII', 'Monday', 5, '01:00 PM - 01:45 PM', 'History & Civics', 'Nasreen Sultana'),
            ('Class VIII', 'Monday', 6, '01:45 PM - 02:30 PM', 'Computer Practice', 'Tanvir Ahmed'),

            ('Class VIII', 'Tuesday', 1, '09:00 AM - 09:45 AM', 'English Grammar', 'Syed Rehan Ali'),
            ('Class VIII', 'Tuesday', 2, '09:45 AM - 10:30 AM', 'Mathematics', 'Mrs. Shabana Parveen'),
            ('Class VIII', 'Tuesday', 3, '10:45 AM - 11:30 AM', 'Life Science', 'Dr. Arifuzzaman Mondal'),
            ('Class VIII', 'Tuesday', 4, '11:30 AM - 12:15 PM', 'Geography', 'S. K. Mukherjee'),
            ('Class VIII', 'Tuesday', 5, '01:00 PM - 01:45 PM', 'Moral Studies & Arabic', 'Janab Maqsood Alam'),
            ('Class VIII', 'Tuesday', 6, '01:45 PM - 02:30 PM', 'Library / Reading Hour', 'Staff'),

            ('Class VIII', 'Wednesday', 1, '09:00 AM - 09:45 AM', 'Physical Science', 'Dr. Arifuzzaman Mondal'),
            ('Class VIII', 'Wednesday', 2, '09:45 AM - 10:30 AM', 'Mathematics', 'Mrs. Shabana Parveen'),
            ('Class VIII', 'Wednesday', 3, '10:45 AM - 11:30 AM', 'Bengali Composition', 'Nasreen Sultana'),
            ('Class VIII', 'Wednesday', 4, '11:30 AM - 12:15 PM', 'English Writing', 'Syed Rehan Ali'),
            ('Class VIII', 'Wednesday', 5, '01:00 PM - 01:45 PM', 'Geography', 'S. K. Mukherjee'),
            ('Class VIII', 'Wednesday', 6, '01:45 PM - 02:30 PM', 'Physical Education / Games', 'Sports Master'),

            ('Class VIII', 'Thursday', 1, '09:00 AM - 09:45 AM', 'Mathematics', 'Mrs. Shabana Parveen'),
            ('Class VIII', 'Thursday', 2, '09:45 AM - 10:30 AM', 'Life Science Lab', 'Dr. Arifuzzaman Mondal'),
            ('Class VIII', 'Thursday', 3, '10:45 AM - 11:30 AM', 'History', 'Nasreen Sultana'),
            ('Class VIII', 'Thursday', 4, '11:30 AM - 12:15 PM', 'English Spoken Practice', 'Syed Rehan Ali'),
            ('Class VIII', 'Thursday', 5, '01:00 PM - 01:45 PM', 'Computer Theory', 'Tanvir Ahmed'),
            ('Class VIII', 'Thursday', 6, '01:45 PM - 02:30 PM', 'Art & Craft', 'Art Teacher'),

            ('Class VIII', 'Friday', 1, '08:30 AM - 09:15 AM', 'Mathematics Doubt Clearing', 'Mrs. Shabana Parveen'),
            ('Class VIII', 'Friday', 2, '09:15 AM - 10:00 AM', 'Bengali Poetry', 'Nasreen Sultana'),
            ('Class VIII', 'Friday', 3, '10:15 AM - 11:00 AM', 'Science Experiment', 'Dr. Arifuzzaman Mondal'),
            ('Class VIII', 'Friday', 4, '11:00 AM - 11:45 AM', 'Moral Values & Ethics', 'Janab Maqsood Alam'),

            ('Class VIII', 'Saturday', 1, '09:00 AM - 09:45 AM', 'English Debate & Quiz', 'Syed Rehan Ali'),
            ('Class VIII', 'Saturday', 2, '09:45 AM - 10:30 AM', 'Mental Math & Reasoning', 'Mrs. Shabana Parveen'),
            ('Class VIII', 'Saturday', 3, '10:45 AM - 11:30 AM', 'General Science Quiz', 'Dr. Arifuzzaman Mondal'),
            ('Class VIII', 'Saturday', 4, '11:30 AM - 12:15 PM', 'Co-Curricular / Club Activities', 'All Staff')
        ]
        for cname, dow, pno, ptime, subj, teach in timetable_entries:
            cursor.execute("""
            INSERT INTO timetables (class_name, day_of_week, period_no, period_time, subject, teacher_name)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (cname, dow, pno, ptime, subj, teach))

        # Seed CMS Pages Content
        pages = [
            ('history', 'Our Glorious Journey & History', 
             'Al Majid Mission School was founded in 2012 at Hazipur, West Bengal (PIN: 731245) with a profound philanthropic vision: to provide premier, modern English and regional-medium schooling coupled with deep moral rectitude to children from all walks of life. Over the past decade, our institution has flourished from a humble gathering of passionate educators into a modern, thriving campus equipped with science laboratories, computer technology, rich library resources, and distinguished faculty. Our alumni now pursue higher studies in medicine, engineering, civil services, and entrepreneurship across India.'),
            
            ('mission', 'Our Mission',
             'To empower every young mind through academic excellence, critical inquiry, digital literacy, and strong ethical foundations rooted in discipline, respect, service to humanity, and communal harmony. We believe every child is uniquely gifted and deserves an empathetic, encouraging learning ecosystem.'),
            
            ('vision', 'Our Vision',
             'To be recognized as a beacon of enlightened education in rural and semi-urban Bengal, bridging modern scientific knowledge with everlasting human and spiritual values, producing conscientious global citizens and compassionate community leaders.'),
            
            ('principal_message', 'Message from the Principal',
             'Warm greetings to all parents, well-wishers, and students. At Al Majid Mission School, we do not view education merely as a means to acquire grades or certificates, but as a holistic crucible for building character, intellect, and empathy. Our dedicated teachers strive each day to ignite curiosity, encourage independent thinking, and instill timeless moral values. We work hand-in-hand with parents to ensure that our boys and girls emerge confident, humble, and prepared for future challenges. I warmly welcome you to our school family.\n\n— Janab Maqsood Alam, M.Sc., B.Ed, Principal'),
            
            ('admissions_info', 'Admission Process & Guidelines',
             'Admissions for Classes Pre-Primary to Class X are open annually starting October for the subsequent academic term. Parents can collect the Prospectus & Registration Form from the school administrative office or submit an inquiry online. The admission process includes an age verification check, an interactive child-friendly readiness assessment for higher classes, and an informal parental interaction to align on learning goals.'),
            
            ('fees_info', 'Transparent Fee Policy & Concessions',
             'Al Majid Mission School operates on a strictly non-profit, educational mission philosophy. Our fee schedule is designed to be accessible and transparent without hidden charges. Merit scholarships and need-based fee waivers are provided to underprivileged students, orphans, and single-parent households upon review by the Governing Committee.')
        ]
        for k, t, c in pages:
            cursor.execute("""
            INSERT INTO pages_content (key, title, content)
            VALUES (?, ?, ?)
            """, (k, t, c))

        # Seed Sample Contact Message
        cursor.execute("""
        INSERT INTO contact_messages (name, phone, email, subject, message, is_read)
        VALUES 
        ('Giasuddin Ansari', '9832155443', 'giasuddin.a@yahoo.com', 'Admission inquiry for Class VI', 'Respected Sir, I want to admit my son to Class VI for the 2026-27 session. Kindly inform me of the last date for submitting the form and hostel facilities if available.', 0),
        ('Sultana Begum', '9749123890', 'sultana.b@gmail.com', 'School Bus Route to Murshidabad border', 'Hello, do you have a school transport pick-up point near Hazipur Bazar junction? Kindly update the schedule.', 1)
        """)

    conn.commit()
    conn.close()
