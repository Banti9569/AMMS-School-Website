# Al Majid Mission School Website & Management Portal
**Hazipur, West Bengal - 731245**

A modern, mobile-first, full-stack web application and school management system built using **Python Flask**, **SQLite**, and **HTML5 / CSS3 / Vanilla JavaScript** with a curated Emerald Green and White theme, dynamic dark/light mode, and dedicated role-based portals for Parents and Administrators.

---

## 🌟 Key Features

### 1. Public Pages (Accessible to All, No Login Required)
- **Home**: Dynamic hero image slider with touch-swipe support, admissions open highlight banner, official pinned circulars, statistics counter, and parent portal callouts.
- **About Us**: Institutional history since 2012, core mission & vision, principal's message with leadership portrait, and guiding values.
- **Admissions & Fees**: 4-step admission guide, class eligibility criteria (Nursery to Class X), and transparent standard fee schedule with scholarship notes.
- **Teachers & Faculty**: Comprehensive faculty directory cards detailing qualifications, subjects, and years of experience.
- **Photo Gallery**: Categorized galleries (Campus, Academics, Sports, Cultural, Science Lab) with interactive full-screen Lightbox viewer.
- **Notices & Events**: Searchable announcements and school circulars with category filtering (Admissions, Exams, Holidays, Sports).
- **Contact Us**: Official campus address, administrative and admission phone lines, interactive Google Map embed, and working inquiry form.

### 2. Parent Portal (Login with Mobile Number + Password)
*Designed specifically for parents because school students do not carry phones.*
- **Child Switcher**: Seamless switching between multiple enrolled wards (e.g., siblings in Class V and Class IX) under a single parent account.
- **Attendance History**: Monthly calendar log with Present/Absent/Late badges and calculated percentage.
- **Term Examination Results**: Detailed marksheet report cards with subject-wise scores, maximum marks, grade badges (AA, A+, A, etc.), and printable format.
- **Fee Status & Receipts**: Ledger of pending and paid fee vouchers, outstanding balance alert, and official receipt numbers.
- **Class Timetable**: Daily 6-day period schedule (Monday to Saturday) with subjects, timings, and teachers.
- **Parent Circulars**: Targeted administrative announcements.

### 3. Administrator Console (Full Control)
- **Dashboard**: Real-time counters for students, parents, teachers, notices, pending fee vouchers, and unread inquiries.
- **Student Management**: Enroll students, assign class/roll/section, link to parent accounts, edit, and delete.
- **Parent Accounts**: Create parent login accounts by mobile number and instantly reset passwords.
- **Teacher Directory**: Add and manage staff profiles and designations.
- **Daily Attendance Entry**: Class-wise roll-call sheet with one-click "Mark All Present" button and individual status toggles.
- **Result & Mark Entry**: Record marks per student, class, and examination term with automatic grade computation.
- **Fee Management**: Issue fee invoices, record fee payments (Cash, UPI, Bank), and generate receipt numbers.
- **Timetable Management**: Add and manage daily period slots per class.
- **Post Notices**: Publish circulars with categories, audience targeting (All, Parents, Public), and home pinning.
- **Gallery Uploads**: Upload photos with captions and categories.
- **Content Management (CMS)**: Edit public page text (About history, mission, vision, principal's message, fee policy) directly from the admin interface.
- **Contact Messages Inbox**: View and manage inquiries received from the public contact form.

### 4. Security & Architecture
- **Password Hashing**: Secure password encryption via `werkzeug.security` (scrypt / pbkdf2).
- **Session-Bound CSRF Protection**: Every state-changing form submission is strictly validated with cryptographically secure tokens.
- **Role-Based Guards**: Route decorators (`@login_required`, `@admin_required`, `@parent_required`) preventing unauthorized access.
- **Zero Heavy Dependencies**: Uses native Flask, SQLite, and Vanilla CSS/JS for lightning-fast mobile loading on 3G/4G networks.

---

## 📁 Folder Structure

```
A.M.M.S/
├── .env                       # Environment variables (secret keys, port, paths - NOT committed)
├── .env.example               # Template environment configuration file
├── .gitignore                 # Excludes secrets, databases, and temporary files from git
├── app.py                     # Flask application factory, CSRF hook, and global context
├── run.py                     # Application startup script with environment loading
├── config.py                  # School metadata, database paths, and upload configs (via dotenv)
├── models.py                  # SQLite schema definitions and automatic seed data
├── db_helpers.py              # Centralized data access queries and business logic
├── security.py                # CSRF validation and role-based access decorators
├── auth.py                    # Unified parent & admin login/logout routes
├── test_suite.py              # Automated full-coverage test suite for all routes & auth
├── requirements.txt           # Python package dependencies
├── routes/
│   ├── public.py              # Public web pages (home, about, admissions, staff, gallery, contact)
│   ├── parent.py              # Parent portal routes (attendance, results, fees, timetable)
│   └── admin.py               # Admin control panel routes (CRUD for all school modules)
├── database/
│   ├── school.db              # SQLite relational database
│   └── backups/               # Safe database backups directory
├── scripts/
│   ├── download_images.py     # Static image asset downloader utility
│   └── generate_assets.py     # High-resolution placeholder generator utility
├── static/
│   ├── css/
│   │   ├── style.css          # Green & white theme, HSL tokens, dark mode, mobile drawer
│   │   ├── components.css     # Slider, lightbox, mark sheets, fee tables, cards
│   │   └── admin.css          # Admin console layout, attendance widgets, toolbars
│   ├── js/
│   │   ├── main.js            # Theme toggle, mobile drawer, touch slider, auto-dismiss alerts
│   │   ├── lightbox.js        # Full-screen image preview with captions & navigation
│   │   └── admin.js           # Bulk attendance selection, delete confirmations
│   ├── images/
│   │   ├── logo.svg           # School emblem vector crest
│   │   ├── school/            # Campus and classroom educational imagery
│   │   └── staff/             # Teacher and leadership portraits
│   └── uploads/
│       ├── gallery/           # Admin uploaded gallery photos
│       ├── notices/           # Notice attachment files
│       └── staff/             # Teacher uploaded portraits
└── templates/
    ├── base.html              # Base layout with mobile bottom-bar and theme switcher
    ├── public/                # Public templates (index, about, admissions, staff, gallery, notices, contact)
    ├── auth/                  # Login and password assistance templates
    ├── parent/                # Parent portal templates (dashboard, attendance, results, fees, timetable)
    └── admin/                 # Admin console templates (dashboard, students, parents, attendance, etc.)
```

---

## 🚀 Getting Started & Run Instructions

### 1. Requirements
- Python 3.10+ (tested on Python 3.12)
- Dependencies installed via `pip`:
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
The project reads configurations from `.env`. A pre-configured `.env` is already active, and you can reference `.env.example` to customize settings:
```ini
FLASK_APP=run.py
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_secure_secret_key
PORT=5000
DATABASE_PATH=database/school.db
```

### 3. Launching the Web Server
Run the application using:
```bash
python run.py
```
Or directly with Flask:
```bash
python app.py
```

The web server will start at:
👉 **`http://127.0.0.1:5000`**

*(The database `database/school.db` is initialized and pre-seeded automatically on first startup).*

### 4. Running the Automated Test Suite
To verify all routes, login authentication, and security protections:
```bash
python test_suite.py
```

---

## 🔑 Initial Setup Credentials (Development / Testing)

> [!NOTE]
> Frontend pages do not expose default passwords for privacy and security. The following seeded credentials can be used for initial setup and verification:

### Demo Login

This project includes admin and parent portal functionality for development and testing.

For security, default login credentials and personal records are not published in this repository. Configure secure credentials locally before running the application.

*Passwords can be changed or reset at any time by the administrator from the Admin Console.*

---

## 📱 Mobile-First Features
- **Adaptive Quick Bottom Bar**: Quick one-tap navigation to Home, Admissions, Notices, Portal Login, and Direct School Call.
- **Off-Canvas Slide Drawer**: Fast menu navigation on mobile phones with touch overlay.
- **Light / Dark Mode**: User preference toggle automatically saved to `localStorage`.
- **Touch Slider**: Swipe left or right on mobile phones to cycle through campus pictures.
- **Horizontal Scroll Wrappers**: Mark sheets and fee tables scroll horizontally without breaking screen widths on small phone viewports.
- **Printable Marksheets**: Parents can print or save their child's term report card directly from their phone.

---

## 📜 Attribution & Credits
Educational imagery sourced under free licenses via **Unsplash** and **Pexels**. All trademarks and emblems belong to **Al Majid Mission School**, Hazipur, West Bengal 731245.
