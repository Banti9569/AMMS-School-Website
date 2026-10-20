from models import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

# ----------------- USERS & AUTH -----------------

def authenticate_user(username, password):
    conn = get_db()
    cursor = conn.cursor()
    # Can match username directly (mobile for parents, 'admin' or mobile for admin)
    cursor.execute("SELECT * FROM users WHERE (username = ? OR phone = ?) AND status = 'active'", (username.strip(), username.strip()))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_all_parents():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT u.*, 
           COUNT(s.id) as children_count,
           GROUP_CONCAT(s.first_name || ' ' || s.last_name || ' (' || s.class_name || ')') as children_names
    FROM users u
    LEFT JOIN students s ON s.parent_id = u.id
    WHERE u.role = 'parent'
    GROUP BY u.id
    ORDER BY u.created_at DESC
    """)
    parents = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return parents

def create_parent_user(mobile, full_name, password="Password@123", email=None):
    conn = get_db()
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        cursor.execute("""
        INSERT INTO users (role, username, password_hash, full_name, email, phone)
        VALUES ('parent', ?, ?, ?, ?, ?)
        """, (mobile.strip(), password_hash, full_name.strip(), email.strip() if email else None, mobile.strip()))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id, None
    except Exception as e:
        conn.close()
        return None, str(e)

def reset_user_password(user_id, new_password):
    conn = get_db()
    cursor = conn.cursor()
    password_hash = generate_password_hash(new_password)
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
    conn.commit()
    conn.close()
    return True

# ----------------- STUDENTS -----------------

def get_all_students(class_filter=None, search=None):
    conn = get_db()
    cursor = conn.cursor()
    query = """
    SELECT s.*, u.full_name as parent_name, u.phone as parent_phone
    FROM students s
    LEFT JOIN users u ON s.parent_id = u.id
    WHERE 1=1
    """
    params = []
    if class_filter:
        query += " AND s.class_name = ?"
        params.append(class_filter)
    if search:
        query += " AND (s.first_name LIKE ? OR s.last_name LIKE ? OR s.admission_no LIKE ? OR u.phone LIKE ?)"
        term = f"%{search.strip()}%"
        params.extend([term, term, term, term])
    
    query += " ORDER BY s.class_name, s.roll_no ASC"
    cursor.execute(query, params)
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return students

def get_student_by_id(student_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.*, u.full_name as parent_name, u.phone as parent_phone, u.email as parent_email
    FROM students s
    LEFT JOIN users u ON s.parent_id = u.id
    WHERE s.id = ?
    """, (student_id,))
    student = cursor.fetchone()
    conn.close()
    return dict(student) if student else None

def get_students_by_parent(parent_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM students 
    WHERE parent_id = ?
    ORDER BY class_name ASC, roll_no ASC
    """, (parent_id,))
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return students

def create_student(data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO students (
        admission_no, roll_no, first_name, last_name, class_name, section, 
        dob, gender, blood_group, parent_id, address, emergency_contact, photo_url
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['admission_no'].strip(), int(data['roll_no']), data['first_name'].strip(), 
        data['last_name'].strip(), data['class_name'], data.get('section', 'A'),
        data.get('dob'), data.get('gender', 'Male'), data.get('blood_group'),
        data.get('parent_id'), data.get('address'), data.get('emergency_contact'),
        data.get('photo_url', '/static/images/school/students_reading.jpg')
    ))
    student_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return student_id

def update_student(student_id, data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE students SET
        admission_no = ?, roll_no = ?, first_name = ?, last_name = ?,
        class_name = ?, section = ?, dob = ?, gender = ?, blood_group = ?,
        parent_id = ?, address = ?, emergency_contact = ?, photo_url = ?
    WHERE id = ?
    """, (
        data['admission_no'].strip(), int(data['roll_no']), data['first_name'].strip(),
        data['last_name'].strip(), data['class_name'], data.get('section', 'A'),
        data.get('dob'), data.get('gender'), data.get('blood_group'),
        data.get('parent_id'), data.get('address'), data.get('emergency_contact'),
        data.get('photo_url'), student_id
    ))
    conn.commit()
    conn.close()
    return True

def delete_student(student_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    return True

# ----------------- TEACHERS -----------------

def get_all_teachers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teachers ORDER BY display_order ASC, name ASC")
    teachers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return teachers

def get_teacher_by_id(teacher_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teachers WHERE id = ?", (teacher_id,))
    teacher = cursor.fetchone()
    conn.close()
    return dict(teacher) if teacher else None

def create_teacher(data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO teachers (name, designation, qualification, subject, experience_years, email, phone, photo_url, bio, display_order)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['name'].strip(), data['designation'].strip(), data['qualification'].strip(),
        data['subject'].strip(), int(data.get('experience_years', 1)),
        data.get('email'), data.get('phone'),
        data.get('photo_url', '/static/images/staff/principal.jpg'),
        data.get('bio'), int(data.get('display_order', 99))
    ))
    t_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return t_id

def update_teacher(teacher_id, data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE teachers SET
        name = ?, designation = ?, qualification = ?, subject = ?,
        experience_years = ?, email = ?, phone = ?, photo_url = ?,
        bio = ?, display_order = ?
    WHERE id = ?
    """, (
        data['name'].strip(), data['designation'].strip(), data['qualification'].strip(),
        data['subject'].strip(), int(data.get('experience_years', 1)),
        data.get('email'), data.get('phone'),
        data.get('photo_url'), data.get('bio'),
        int(data.get('display_order', 99)), teacher_id
    ))
    conn.commit()
    conn.close()
    return True

def delete_teacher(teacher_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    conn.commit()
    conn.close()
    return True

# ----------------- NOTICES -----------------

def get_notices(category=None, search=None, target='All', limit=None):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM notices WHERE 1=1"
    params = []
    
    if target == 'Public':
        query += " AND target_audience IN ('All', 'Public')"
    elif target == 'Parents':
        query += " AND target_audience IN ('All', 'Parents')"
    
    if category and category != 'All':
        query += " AND category = ?"
        params.append(category)
        
    if search:
        query += " AND (title LIKE ? OR content LIKE ?)"
        s = f"%{search.strip()}%"
        params.extend([s, s])
        
    query += " ORDER BY is_pinned DESC, published_date DESC, id DESC"
    if limit:
        query += f" LIMIT {int(limit)}"
        
    cursor.execute(query, params)
    notices = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return notices

def get_notice_by_id(notice_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notices WHERE id = ?", (notice_id,))
    notice = cursor.fetchone()
    conn.close()
    return dict(notice) if notice else None

def create_notice(data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO notices (title, category, content, is_pinned, target_audience, file_url, published_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data['title'].strip(), data.get('category', 'General'), data['content'].strip(),
        1 if data.get('is_pinned') else 0, data.get('target_audience', 'All'),
        data.get('file_url'), data.get('published_date', date.today().isoformat())
    ))
    n_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return n_id

def update_notice(notice_id, data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE notices SET
        title = ?, category = ?, content = ?, is_pinned = ?,
        target_audience = ?, file_url = ?, published_date = ?
    WHERE id = ?
    """, (
        data['title'].strip(), data.get('category', 'General'), data['content'].strip(),
        1 if data.get('is_pinned') else 0, data.get('target_audience', 'All'),
        data.get('file_url'), data.get('published_date', date.today().isoformat()),
        notice_id
    ))
    conn.commit()
    conn.close()
    return True

def delete_notice(notice_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notices WHERE id = ?", (notice_id,))
    conn.commit()
    conn.close()
    return True

# ----------------- GALLERY -----------------

def get_gallery_items(category=None):
    conn = get_db()
    cursor = conn.cursor()
    if category and category != 'All':
        cursor.execute("SELECT * FROM gallery WHERE category = ? ORDER BY id DESC", (category,))
    else:
        cursor.execute("SELECT * FROM gallery ORDER BY id DESC")
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items

def create_gallery_item(title, category, image_url, caption=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO gallery (title, category, image_url, caption)
    VALUES (?, ?, ?, ?)
    """, (title.strip(), category, image_url, caption.strip() if caption else None))
    g_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return g_id

def delete_gallery_item(gallery_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gallery WHERE id = ?", (gallery_id,))
    conn.commit()
    conn.close()
    return True

# ----------------- ATTENDANCE -----------------

def get_student_attendance(student_id, month=None, year=None):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM attendance WHERE student_id = ?"
    params = [student_id]
    
    if month and year:
        query += " AND strftime('%m', date) = ? AND strftime('%Y', date) = ?"
        params.extend([f"{int(month):02d}", str(year)])
        
    query += " ORDER BY date DESC"
    cursor.execute(query, params)
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records

def get_student_attendance_summary(student_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        COUNT(*) as total_days,
        SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_days,
        SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent_days,
        SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) as late_days
    FROM attendance
    WHERE student_id = ?
    """, (student_id,))
    row = cursor.fetchone()
    conn.close()
    
    total = row['total_days'] or 0
    present = row['present_days'] or 0
    late = row['late_days'] or 0
    absent = row['absent_days'] or 0
    
    # Effective present can include late
    percentage = round(((present + (late * 0.5)) / total * 100), 1) if total > 0 else 100.0
    return {
        'total_days': total,
        'present_days': present,
        'absent_days': absent,
        'late_days': late,
        'percentage': percentage
    }

def get_attendance_sheet(class_name, date_str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.id as student_id, s.roll_no, s.first_name, s.last_name, s.admission_no,
           a.id as attendance_id, a.status, a.remarks
    FROM students s
    LEFT JOIN attendance a ON a.student_id = s.id AND a.date = ?
    WHERE s.class_name = ?
    ORDER BY s.roll_no ASC
    """, (date_str, class_name))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records

def save_attendance_record(student_id, date_str, status, remarks=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO attendance (student_id, date, status, remarks)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(student_id, date) DO UPDATE SET
        status = excluded.status,
        remarks = excluded.remarks
    """, (student_id, date_str, status, remarks.strip() if remarks else None))
    conn.commit()
    conn.close()
    return True

# ----------------- RESULTS -----------------

def get_student_results_grouped(student_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM results
    WHERE student_id = ?
    ORDER BY exam_date DESC, id ASC
    """, (student_id,))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Group by exam_name
    grouped = {}
    for r in records:
        ename = r['exam_name']
        if ename not in grouped:
            grouped[ename] = {
                'exam_name': ename,
                'class_name': r['class_name'],
                'exam_date': r['exam_date'],
                'subjects': [],
                'total_obtained': 0,
                'total_max': 0,
                'percentage': 0,
                'overall_grade': 'A'
            }
        grouped[ename]['subjects'].append(r)
        grouped[ename]['total_obtained'] += r['marks_obtained']
        grouped[ename]['total_max'] += r['max_marks']
    
    for ename, data in grouped.items():
        if data['total_max'] > 0:
            pct = round((data['total_obtained'] / data['total_max']) * 100, 1)
            data['percentage'] = pct
            if pct >= 90:
                data['overall_grade'] = 'AA (Outstanding)'
            elif pct >= 80:
                data['overall_grade'] = 'A+ (Excellent)'
            elif pct >= 70:
                data['overall_grade'] = 'A (Very Good)'
            elif pct >= 60:
                data['overall_grade'] = 'B+ (Good)'
            elif pct >= 50:
                data['overall_grade'] = 'B (Satisfactory)'
            else:
                data['overall_grade'] = 'C (Needs Improvement)'
                
    return list(grouped.values())

def save_result_entry(student_id, exam_name, class_name, subject, marks_obtained, max_marks=100, grade="", remarks=""):
    conn = get_db()
    cursor = conn.cursor()
    # Calculate grade if empty
    if not grade:
        pct = (float(marks_obtained) / float(max_marks)) * 100
        if pct >= 90: grade = 'AA'
        elif pct >= 80: grade = 'A+'
        elif pct >= 70: grade = 'A'
        elif pct >= 60: grade = 'B+'
        elif pct >= 50: grade = 'B'
        elif pct >= 35: grade = 'C'
        else: grade = 'D'
        
    cursor.execute("""
    INSERT INTO results (student_id, exam_name, class_name, subject, marks_obtained, max_marks, grade, remarks, exam_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id, exam_name.strip(), class_name, subject.strip(),
        float(marks_obtained), float(max_marks), grade, remarks.strip() if remarks else None,
        date.today().isoformat()
    ))
    r_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return r_id

def delete_result(result_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM results WHERE id = ?", (result_id,))
    conn.commit()
    conn.close()
    return True

# ----------------- FEES -----------------

def get_student_fees(student_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM fee_records
    WHERE student_id = ?
    ORDER BY due_date DESC, id DESC
    """, (student_id,))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    total_fee = sum(r['amount'] for r in records)
    total_paid = sum(r['paid_amount'] or 0 for r in records)
    total_due = total_fee - total_paid
    pending_count = sum(1 for r in records if r['payment_status'] != 'Paid')
    
    return {
        'records': records,
        'total_fee': total_fee,
        'total_paid': total_paid,
        'total_due': max(0, total_due),
        'pending_count': pending_count
    }

def get_all_fees(status_filter=None):
    conn = get_db()
    cursor = conn.cursor()
    query = """
    SELECT f.*, s.first_name, s.last_name, s.admission_no, s.class_name, s.roll_no,
           u.full_name as parent_name, u.phone as parent_phone
    FROM fee_records f
    JOIN students s ON f.student_id = s.id
    LEFT JOIN users u ON s.parent_id = u.id
    WHERE 1=1
    """
    params = []
    if status_filter and status_filter != 'All':
        query += " AND f.payment_status = ?"
        params.append(status_filter)
        
    query += " ORDER BY f.due_date DESC, f.id DESC"
    cursor.execute(query, params)
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records

def create_fee_record(student_id, fee_title, amount, due_date):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO fee_records (student_id, fee_title, amount, paid_amount, due_date, payment_status)
    VALUES (?, ?, ?, 0, ?, 'Pending')
    """, (student_id, fee_title.strip(), float(amount), due_date))
    f_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return f_id

def record_fee_payment(fee_id, paid_amount, payment_method, receipt_no=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT amount, paid_amount FROM fee_records WHERE id = ?", (fee_id,))
    fee = cursor.fetchone()
    if not fee:
        conn.close()
        return False
        
    new_paid = float(paid_amount)
    total_amount = fee['amount']
    status = 'Paid' if new_paid >= total_amount else ('Partial' if new_paid > 0 else 'Pending')
    
    if not receipt_no:
        receipt_no = f"REC-{datetime.now().strftime('%Y%m%d')}-{fee_id}"
        
    cursor.execute("""
    UPDATE fee_records SET
        paid_amount = ?,
        payment_status = ?,
        payment_method = ?,
        receipt_no = ?,
        payment_date = ?
    WHERE id = ?
    """, (new_paid, status, payment_method, receipt_no, date.today().isoformat(), fee_id))
    conn.commit()
    conn.close()
    return True

# ----------------- TIMETABLE -----------------

def get_class_timetable(class_name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM timetables
    WHERE class_name = ?
    ORDER BY 
        CASE day_of_week
            WHEN 'Monday' THEN 1
            WHEN 'Tuesday' THEN 2
            WHEN 'Wednesday' THEN 3
            WHEN 'Thursday' THEN 4
            WHEN 'Friday' THEN 5
            WHEN 'Saturday' THEN 6
        END,
        period_no ASC
    """, (class_name,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    # Organize by day
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    schedule = {d: [] for d in days_order}
    for row in rows:
        if row['day_of_week'] in schedule:
            schedule[row['day_of_week']].append(row)
    return schedule

def save_timetable_slot(class_name, day_of_week, period_no, period_time, subject, teacher_name, room_no=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO timetables (class_name, day_of_week, period_no, period_time, subject, teacher_name, room_no)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (class_name, day_of_week, int(period_no), period_time.strip(), subject.strip(), teacher_name.strip(), room_no.strip()))
    conn.commit()
    conn.close()
    return True

def delete_timetable_slot(slot_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM timetables WHERE id = ?", (slot_id,))
    conn.commit()
    conn.close()
    return True

# ----------------- CMS PAGES CONTENT -----------------

def get_all_page_contents():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pages_content")
    rows = {r['key']: {'title': r['title'], 'content': r['content'], 'updated_at': r['updated_at']} for r in cursor.fetchall()}
    conn.close()
    return rows

def get_page_content(key, default_title="", default_content=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pages_content WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'title': row['title'], 'content': row['content']}
    return {'title': default_title, 'content': default_content}

def update_page_content(key, title, content):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO pages_content (key, title, content, updated_at)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(key) DO UPDATE SET
        title = excluded.title,
        content = excluded.content,
        updated_at = CURRENT_TIMESTAMP
    """, (key, title.strip(), content.strip()))
    conn.commit()
    conn.close()
    return True

# ----------------- CONTACT MESSAGES -----------------

def save_contact_message(name, phone, email, subject, message):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO contact_messages (name, phone, email, subject, message)
    VALUES (?, ?, ?, ?, ?)
    """, (name.strip(), phone.strip(), email.strip() if email else None, subject.strip(), message.strip()))
    m_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return m_id

def get_all_contact_messages():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contact_messages ORDER BY is_read ASC, created_at DESC")
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages

def mark_message_as_read(message_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE contact_messages SET is_read = 1 WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()
    return True

def delete_contact_message(message_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contact_messages WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()
    return True

# ----------------- ADMIN DASHBOARD COUNTS -----------------

def get_admin_dashboard_counts():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'parent'")
    total_parents = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM teachers")
    total_teachers = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM notices")
    total_notices = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM gallery")
    total_gallery = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM fee_records WHERE payment_status != 'Paid'")
    pending_fees = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contact_messages WHERE is_read = 0")
    unread_messages = cursor.fetchone()[0]
    
    conn.close()
    return {
        'total_students': total_students,
        'total_parents': total_parents,
        'total_teachers': total_teachers,
        'total_notices': total_notices,
        'total_gallery': total_gallery,
        'pending_fees': pending_fees,
        'unread_messages': unread_messages
    }
