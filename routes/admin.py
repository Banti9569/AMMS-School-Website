import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from security import admin_required
from datetime import date, datetime
from db_helpers import (
    get_admin_dashboard_counts, get_all_students, get_student_by_id,
    create_student, update_student, delete_student,
    get_all_parents, create_parent_user, reset_user_password,
    get_all_teachers, get_teacher_by_id, create_teacher, update_teacher, delete_teacher,
    get_notices, get_notice_by_id, create_notice, update_notice, delete_notice,
    get_gallery_items, create_gallery_item, delete_gallery_item,
    get_attendance_sheet, save_attendance_record,
    get_student_results_grouped, save_result_entry, delete_result,
    get_all_fees, create_fee_record, record_fee_payment,
    get_class_timetable, save_timetable_slot, delete_timetable_slot,
    get_all_page_contents, update_page_content,
    get_all_contact_messages, mark_message_as_read, delete_contact_message
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

CLASSES = ['Nursery', 'KG', 'Class I', 'Class II', 'Class III', 'Class IV', 'Class V', 'Class VI', 'Class VII', 'Class VIII', 'Class IX', 'Class X']

def allowed_file(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ext in {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

# ----------------- DASHBOARD -----------------

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    counts = get_admin_dashboard_counts()
    recent_notices = get_notices(limit=4)
    recent_messages = get_all_contact_messages()[:4]
    return render_template('admin/dashboard.html', counts=counts, recent_notices=recent_notices, recent_messages=recent_messages)

# ----------------- STUDENTS -----------------

@admin_bp.route('/students', methods=['GET', 'POST'])
@admin_required
def students():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            parent_id = request.form.get('parent_id')
            parent_id = int(parent_id) if parent_id and parent_id.isdigit() else None
            
            data = {
                'admission_no': request.form.get('admission_no', '').strip(),
                'roll_no': request.form.get('roll_no', 1),
                'first_name': request.form.get('first_name', '').strip(),
                'last_name': request.form.get('last_name', '').strip(),
                'class_name': request.form.get('class_name', 'Class I'),
                'section': request.form.get('section', 'A'),
                'dob': request.form.get('dob'),
                'gender': request.form.get('gender', 'Male'),
                'blood_group': request.form.get('blood_group'),
                'parent_id': parent_id,
                'address': request.form.get('address'),
                'emergency_contact': request.form.get('emergency_contact'),
                'photo_url': '/static/images/school/students_reading.jpg'
            }
            try:
                create_student(data)
                flash('Student enrolled successfully!', 'success')
            except Exception as e:
                flash(f'Error adding student: {e}', 'danger')
        return redirect(url_for('admin.students'))
        
    class_filter = request.args.get('class_name')
    search = request.args.get('search')
    students_list = get_all_students(class_filter=class_filter, search=search)
    parents_list = get_all_parents()
    
    return render_template(
        'admin/students.html',
        students=students_list,
        parents=parents_list,
        classes=CLASSES,
        selected_class=class_filter,
        search=search
    )

@admin_bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('admin.students'))
        
    if request.method == 'POST':
        parent_id = request.form.get('parent_id')
        parent_id = int(parent_id) if parent_id and parent_id.isdigit() else None
        
        data = {
            'admission_no': request.form.get('admission_no', '').strip(),
            'roll_no': request.form.get('roll_no', 1),
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
            'class_name': request.form.get('class_name', 'Class I'),
            'section': request.form.get('section', 'A'),
            'dob': request.form.get('dob'),
            'gender': request.form.get('gender', 'Male'),
            'blood_group': request.form.get('blood_group'),
            'parent_id': parent_id,
            'address': request.form.get('address'),
            'emergency_contact': request.form.get('emergency_contact'),
            'photo_url': student['photo_url']
        }
        update_student(student_id, data)
        flash('Student details updated successfully.', 'success')
        return redirect(url_for('admin.students'))
        
    parents_list = get_all_parents()
    return render_template('admin/student_edit.html', student=student, parents=parents_list, classes=CLASSES)

@admin_bp.route('/students/<int:student_id>/delete', methods=['POST'])
@admin_required
def remove_student(student_id):
    delete_student(student_id)
    flash('Student record deleted.', 'info')
    return redirect(url_for('admin.students'))

# ----------------- PARENTS -----------------

@admin_bp.route('/parents', methods=['GET', 'POST'])
@admin_required
def parents():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            mobile = request.form.get('mobile', '').strip()
            name = request.form.get('full_name', '').strip()
            password = request.form.get('password', '').strip()
            email = request.form.get('email', '').strip()
            
            if not mobile or not name:
                flash('Mobile number and Name are required for Parent account.', 'warning')
            elif not password:
                flash('Initial password is required to create a parent account.', 'warning')
            else:
                uid, err = create_parent_user(mobile, name, password, email)
                if err:
                    flash(f'Error creating parent account: {err}', 'danger')
                else:
                    flash(f'Parent account created successfully for {name} ({mobile})!', 'success')
        elif action == 'reset_password':
            user_id = request.form.get('user_id')
            new_pass = request.form.get('new_password', '').strip()
            if not new_pass:
                flash('Please enter a new password to reset.', 'warning')
            elif user_id:
                reset_user_password(int(user_id), new_pass)
                flash('Parent password has been reset successfully.', 'success')
        return redirect(url_for('admin.parents'))
        
    parents_list = get_all_parents()
    return render_template('admin/parents.html', parents=parents_list)

# ----------------- TEACHERS -----------------

from PIL import Image

@admin_bp.route('/teachers', methods=['GET', 'POST'])
@admin_required
def teachers():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            photo_url = request.form.get('photo_url', '').strip()
            
            # Handle photo file upload
            photo_file = request.files.get('photo')
            if photo_file and photo_file.filename != '' and allowed_file(photo_file.filename):
                safe_name = secure_filename(photo_file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"teacher_{timestamp}_{safe_name}"
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'staff')
                os.makedirs(upload_dir, exist_ok=True)
                save_path = os.path.join(upload_dir, filename)
                try:
                    img = Image.open(photo_file)
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGB')
                    img.save(save_path)
                except Exception:
                    photo_file.seek(0)
                    photo_file.save(save_path)
                photo_url = f"/static/uploads/staff/{filename}"
                
            if not photo_url:
                photo_url = '/static/images/staff/teacher_math.jpg'

            data = {
                'name': request.form.get('name', ''),
                'designation': request.form.get('designation', ''),
                'qualification': request.form.get('qualification', ''),
                'subject': request.form.get('subject', ''),
                'experience_years': request.form.get('experience_years', 1),
                'email': request.form.get('email'),
                'phone': request.form.get('phone'),
                'bio': request.form.get('bio'),
                'display_order': request.form.get('display_order', 99),
                'photo_url': photo_url
            }
            create_teacher(data)
            flash('Teacher added to staff directory.', 'success')
        return redirect(url_for('admin.teachers'))
        
    teachers_list = get_all_teachers()
    return render_template('admin/teachers.html', teachers=teachers_list)

@admin_bp.route('/teachers/<int:teacher_id>/delete', methods=['POST'])
@admin_required
def remove_teacher(teacher_id):
    delete_teacher(teacher_id)
    flash('Teacher removed from directory.', 'info')
    return redirect(url_for('admin.teachers'))

# ----------------- NOTICES -----------------

@admin_bp.route('/notices', methods=['GET', 'POST'])
@admin_required
def notices():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            data = {
                'title': request.form.get('title', ''),
                'category': request.form.get('category', 'General'),
                'content': request.form.get('content', ''),
                'is_pinned': bool(request.form.get('is_pinned')),
                'target_audience': request.form.get('target_audience', 'All'),
                'published_date': request.form.get('published_date', date.today().isoformat())
            }
            create_notice(data)
            flash('Notice published successfully!', 'success')
        return redirect(url_for('admin.notices'))
        
    notices_list = get_notices()
    return render_template('admin/notices.html', notices=notices_list)

@admin_bp.route('/notices/<int:notice_id>/delete', methods=['POST'])
@admin_required
def remove_notice(notice_id):
    delete_notice(notice_id)
    flash('Notice deleted.', 'info')
    return redirect(url_for('admin.notices'))

# ----------------- GALLERY -----------------

@admin_bp.route('/gallery', methods=['GET', 'POST'])
@admin_required
def gallery():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'Campus')
        caption = request.form.get('caption', '').strip()
        image_url = request.form.get('image_url', '').strip()
        
        # Handle file upload if provided
        file = request.files.get('file')
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'gallery', filename)
            file.save(upload_path)
            image_url = f"/static/uploads/gallery/{filename}"
            
        if not image_url:
            image_url = '/static/images/school/hero_campus.jpg'
            
        create_gallery_item(title, category, image_url, caption)
        flash('Photo added to gallery!', 'success')
        return redirect(url_for('admin.gallery'))
        
    gallery_list = get_gallery_items()
    return render_template('admin/gallery.html', gallery=gallery_list)

@admin_bp.route('/gallery/<int:item_id>/delete', methods=['POST'])
@admin_required
def remove_gallery(item_id):
    delete_gallery_item(item_id)
    flash('Gallery photo removed.', 'info')
    return redirect(url_for('admin.gallery'))

# ----------------- ATTENDANCE -----------------

@admin_bp.route('/attendance', methods=['GET', 'POST'])
@admin_required
def attendance():
    today_str = date.today().isoformat()
    selected_date = request.args.get('date', today_str)
    selected_class = request.args.get('class_name', 'Class VIII')
    
    if request.method == 'POST':
        # Batch save attendance
        form_date = request.form.get('attendance_date', today_str)
        form_class = request.form.get('class_name', selected_class)
        
        # Keys like status_12, remarks_12
        for key in request.form:
            if key.startswith('status_'):
                student_id = int(key.replace('status_', ''))
                status = request.form.get(key)
                remarks = request.form.get(f'remarks_{student_id}', '')
                save_attendance_record(student_id, form_date, status, remarks)
                
        flash(f'Attendance recorded successfully for {form_class} on {form_date}.', 'success')
        return redirect(url_for('admin.attendance', class_name=form_class, date=form_date))
        
    sheet = get_attendance_sheet(selected_class, selected_date)
    return render_template(
        'admin/attendance.html',
        classes=CLASSES,
        selected_class=selected_class,
        selected_date=selected_date,
        sheet=sheet
    )

# ----------------- RESULTS -----------------

@admin_bp.route('/results', methods=['GET', 'POST'])
@admin_required
def results():
    selected_class = request.args.get('class_name', 'Class VIII')
    students_in_class = get_all_students(class_filter=selected_class)
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            student_id = int(request.form.get('student_id'))
            exam_name = request.form.get('exam_name', 'Mid-Term Exam 2026')
            subject = request.form.get('subject', '')
            marks_obtained = request.form.get('marks_obtained', 0)
            max_marks = request.form.get('max_marks', 100)
            grade = request.form.get('grade', '')
            remarks = request.form.get('remarks', '')
            
            save_result_entry(student_id, exam_name, selected_class, subject, marks_obtained, max_marks, grade, remarks)
            flash('Result mark entry saved successfully!', 'success')
        elif action == 'delete':
            result_id = int(request.form.get('result_id'))
            delete_result(result_id)
            flash('Result entry deleted.', 'info')
            
        return redirect(url_for('admin.results', class_name=selected_class))
        
    selected_student_id = request.args.get('student_id')
    selected_student = None
    student_results = []
    if selected_student_id and selected_student_id.isdigit():
        selected_student = get_student_by_id(int(selected_student_id))
        if selected_student:
            student_results = get_student_results_grouped(int(selected_student_id))
            
    return render_template(
        'admin/results.html',
        classes=CLASSES,
        selected_class=selected_class,
        students=students_in_class,
        selected_student=selected_student,
        student_results=student_results
    )

# ----------------- FEES -----------------

@admin_bp.route('/fees', methods=['GET', 'POST'])
@admin_required
def fees():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            student_id = int(request.form.get('student_id'))
            title = request.form.get('fee_title', '')
            amount = float(request.form.get('amount', 0))
            due_date = request.form.get('due_date', date.today().isoformat())
            create_fee_record(student_id, title, amount, due_date)
            flash('Fee invoice created successfully!', 'success')
        elif action == 'record_payment':
            fee_id = int(request.form.get('fee_id'))
            paid_amount = float(request.form.get('paid_amount', 0))
            payment_method = request.form.get('payment_method', 'Cash')
            receipt_no = request.form.get('receipt_no')
            record_fee_payment(fee_id, paid_amount, payment_method, receipt_no)
            flash('Payment recorded and receipt generated.', 'success')
        return redirect(url_for('admin.fees'))
        
    status_filter = request.args.get('status', 'All')
    fees_list = get_all_fees(status_filter=status_filter)
    all_students = get_all_students()
    
    return render_template('admin/fees.html', fees=fees_list, students=all_students, status_filter=status_filter)

# ----------------- TIMETABLE -----------------

@admin_bp.route('/timetable', methods=['GET', 'POST'])
@admin_required
def timetable():
    selected_class = request.args.get('class_name', 'Class VIII')
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            day = request.form.get('day_of_week')
            pno = request.form.get('period_no')
            ptime = request.form.get('period_time')
            subject = request.form.get('subject')
            teacher = request.form.get('teacher_name')
            room = request.form.get('room_no', '')
            save_timetable_slot(selected_class, day, pno, ptime, subject, teacher, room)
            flash('Timetable slot added.', 'success')
        elif action == 'delete':
            slot_id = int(request.form.get('slot_id'))
            delete_timetable_slot(slot_id)
            flash('Timetable slot removed.', 'info')
        return redirect(url_for('admin.timetable', class_name=selected_class))
        
    schedule = get_class_timetable(selected_class)
    teachers_list = get_all_teachers()
    return render_template('admin/timetable.html', classes=CLASSES, selected_class=selected_class, schedule=schedule, teachers=teachers_list)

# ----------------- CMS PAGES -----------------

@admin_bp.route('/pages', methods=['GET', 'POST'])
@admin_required
def pages():
    if request.method == 'POST':
        for key in ['history', 'mission', 'vision', 'principal_message', 'admissions_info', 'fees_info']:
            title = request.form.get(f'{key}_title', '')
            content = request.form.get(f'{key}_content', '')
            if title and content:
                update_page_content(key, title, content)
                
        # Handle Principal photo upload if provided
        principal_photo = request.files.get('principal_photo')
        if principal_photo and principal_photo.filename != '' and allowed_file(principal_photo.filename):
            dest_dir = os.path.join(current_app.root_path, 'static', 'images', 'staff')
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, 'principal.jpg')
            try:
                img = Image.open(principal_photo)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(dest_path, 'JPEG', quality=92)
            except Exception:
                principal_photo.seek(0)
                principal_photo.save(dest_path)
            flash('Principal photo and message updated successfully!', 'success')
        else:
            flash('Public page content updated successfully.', 'success')
        return redirect(url_for('admin.pages'))
        
    pages_content = get_all_page_contents()
    return render_template('admin/pages.html', pages=pages_content)

# ----------------- MESSAGES -----------------

@admin_bp.route('/messages', methods=['GET', 'POST'])
@admin_required
def messages():
    if request.method == 'POST':
        action = request.form.get('action')
        message_id = int(request.form.get('message_id'))
        if action == 'mark_read':
            mark_message_as_read(message_id)
            flash('Message marked as read.', 'info')
        elif action == 'delete':
            delete_contact_message(message_id)
            flash('Message deleted.', 'info')
        return redirect(url_for('admin.messages'))
        
    messages_list = get_all_contact_messages()
    return render_template('admin/messages.html', messages=messages_list)
