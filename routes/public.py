from flask import Blueprint, render_template, request, flash, redirect, url_for
from db_helpers import (
    get_notices, get_notice_by_id, get_gallery_items, get_all_teachers,
    get_page_content, save_contact_message
)

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def home():
    pinned_notices = [n for n in get_notices(limit=6) if n.get('is_pinned')]
    latest_notices = get_notices(limit=5)
    gallery_preview = get_gallery_items()[:6]
    teachers = get_all_teachers()[:4]
    
    principal_msg = get_page_content('principal_message', 'Message from the Principal', '')
    
    # Hero slider slides
    slider_slides = [
        {
            'image': '/static/images/school/hero_campus.jpg',
            'title': 'Welcome to Al Majid Mission School',
            'subtitle': 'Hazipur, West Bengal — Cultivating Knowledge, Character & Leadership Since 2012',
            'btn_text': 'Explore Admissions',
            'btn_link': '/admissions'
        },
        {
            'image': '/static/images/school/hero_classroom.jpg',
            'title': 'Holistic Academic Excellence',
            'subtitle': 'Modern Smart Classrooms, Individual Mentorship & WBBSE Aligned Curriculum',
            'btn_text': 'Our Faculty',
            'btn_link': '/staff'
        },
        {
            'image': '/static/images/school/hero_library.jpg',
            'title': 'Knowledge & Moral Discipline',
            'subtitle': 'Rich Resource Library, Islamic Ethics & Scientific Spirit Hand in Hand',
            'btn_text': 'About Our Mission',
            'btn_link': '/about'
        },
        {
            'image': '/static/images/school/hero_sports.jpg',
            'title': 'Sports & Character Building',
            'subtitle': 'Active Physical Education, Athletic Meets & Co-Curricular Competitions',
            'btn_text': 'View Gallery',
            'btn_link': '/gallery'
        }
    ]

    return render_template(
        'public/index.html',
        slider_slides=slider_slides,
        pinned_notices=pinned_notices,
        latest_notices=latest_notices,
        gallery_preview=gallery_preview,
        teachers=teachers,
        principal_msg=principal_msg
    )

@public_bp.route('/about')
def about():
    history = get_page_content('history', 'Our History', '')
    mission = get_page_content('mission', 'Our Mission', '')
    vision = get_page_content('vision', 'Our Vision', '')
    principal_msg = get_page_content('principal_message', 'Message from the Principal', '')
    return render_template('public/about.html', history=history, mission=mission, vision=vision, principal_msg=principal_msg)

@public_bp.route('/admissions')
def admissions():
    admissions_info = get_page_content('admissions_info', 'Admission Process', '')
    fees_info = get_page_content('fees_info', 'Fee Policy', '')
    return render_template('public/admissions.html', admissions_info=admissions_info, fees_info=fees_info)

@public_bp.route('/staff')
def staff():
    teachers = get_all_teachers()
    return render_template('public/staff.html', teachers=teachers)

@public_bp.route('/gallery')
def gallery():
    category = request.args.get('category', 'All')
    items = get_gallery_items(category)
    categories = ['All', 'Campus', 'Academics', 'Sports', 'Cultural', 'Science Lab']
    return render_template('public/gallery.html', items=items, categories=categories, current_cat=category)

@public_bp.route('/notices')
def notices():
    category = request.args.get('category', 'All')
    search = request.args.get('search', '').strip()
    notices_list = get_notices(category=category, search=search, target='Public')
    categories = ['All', 'Admission', 'Exam', 'Academic', 'Holiday', 'Sports', 'General']
    return render_template('public/notices.html', notices=notices_list, categories=categories, current_cat=category, search=search)

@public_bp.route('/notices/<int:notice_id>')
def notice_detail(notice_id):
    notice = get_notice_by_id(notice_id)
    if not notice:
        flash('Notice not found.', 'warning')
        return redirect(url_for('public.notices'))
    return render_template('public/notice_detail.html', notice=notice)

@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        if not name or not phone or not message:
            flash('Please fill in all required fields (Name, Phone number, and Message).', 'danger')
            return render_template('public/contact.html', form_data=request.form)
            
        save_contact_message(name, phone, email, subject or 'General Inquiry', message)
        flash('Thank you for contacting Al Majid Mission School! Our administrative office will get back to you shortly.', 'success')
        return redirect(url_for('public.contact'))
        
    return render_template('public/contact.html')
