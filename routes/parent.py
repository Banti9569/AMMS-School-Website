from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from security import parent_required
from db_helpers import (
    get_students_by_parent, get_student_by_id, get_student_attendance,
    get_student_attendance_summary, get_student_results_grouped,
    get_student_fees, get_class_timetable, get_notices
)

parent_bp = Blueprint('parent', __name__, url_prefix='/parent')

def get_current_parent_child():
    parent_id = session.get('user_id')
    children = get_students_by_parent(parent_id)
    if not children:
        return None, []
        
    active_child_id = session.get('active_child_id')
    active_child = None
    if active_child_id:
        active_child = next((c for c in children if c['id'] == active_child_id), None)
        
    if not active_child:
        active_child = children[0]
        session['active_child_id'] = active_child['id']
        
    return active_child, children

@parent_bp.route('/select-child/<int:student_id>')
@parent_required
def select_child(student_id):
    parent_id = session.get('user_id')
    children = get_students_by_parent(parent_id)
    valid_child = next((c for c in children if c['id'] == student_id), None)
    if valid_child:
        session['active_child_id'] = student_id
        flash(f"Switched view to {valid_child['first_name']} {valid_child['last_name']}.", 'info')
    else:
        flash("Child record not associated with your account.", 'danger')
        
    # Redirect back to referring page or dashboard
    ref = request.referrer
    if ref and '/parent/' in ref:
        return redirect(ref)
    return redirect(url_for('parent.dashboard'))

@parent_bp.route('/dashboard')
@parent_required
def dashboard():
    child, children = get_current_parent_child()
    if not child:
        return render_template('parent/no_child.html')
        
    attendance_summary = get_student_attendance_summary(child['id'])
    recent_attendance = get_student_attendance(child['id'])[:7]
    results_grouped = get_student_results_grouped(child['id'])
    latest_exam = results_grouped[0] if results_grouped else None
    fees_summary = get_student_fees(child['id'])
    notices = get_notices(target='Parents', limit=4)
    
    return render_template(
        'parent/dashboard.html',
        child=child,
        children=children,
        attendance_summary=attendance_summary,
        recent_attendance=recent_attendance,
        latest_exam=latest_exam,
        fees_summary=fees_summary,
        notices=notices
    )

@parent_bp.route('/attendance')
@parent_required
def attendance():
    child, children = get_current_parent_child()
    if not child:
        return render_template('parent/no_child.html')
        
    month = request.args.get('month')
    year = request.args.get('year')
    records = get_student_attendance(child['id'], month=month, year=year)
    summary = get_student_attendance_summary(child['id'])
    
    return render_template(
        'parent/attendance.html',
        child=child,
        children=children,
        records=records,
        summary=summary,
        selected_month=month,
        selected_year=year
    )

@parent_bp.route('/results')
@parent_required
def results():
    child, children = get_current_parent_child()
    if not child:
        return render_template('parent/no_child.html')
        
    exams = get_student_results_grouped(child['id'])
    return render_template(
        'parent/results.html',
        child=child,
        children=children,
        exams=exams
    )

@parent_bp.route('/fees')
@parent_required
def fees():
    child, children = get_current_parent_child()
    if not child:
        return render_template('parent/no_child.html')
        
    fees_data = get_student_fees(child['id'])
    return render_template(
        'parent/fees.html',
        child=child,
        children=children,
        fees=fees_data
    )

@parent_bp.route('/timetable')
@parent_required
def timetable():
    child, children = get_current_parent_child()
    if not child:
        return render_template('parent/no_child.html')
        
    schedule = get_class_timetable(child['class_name'])
    return render_template(
        'parent/timetable.html',
        child=child,
        children=children,
        schedule=schedule
    )

@parent_bp.route('/notices')
@parent_required
def notices():
    child, children = get_current_parent_child()
    notices_list = get_notices(target='Parents')
    return render_template(
        'parent/notices.html',
        child=child,
        children=children,
        notices=notices_list
    )
