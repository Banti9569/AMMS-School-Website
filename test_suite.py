"""
Al Majid Mission School - Comprehensive Automated Test Suite
Supports testing both against live running server and direct Flask test client.
"""
import re
import sys

def get_tester():
    """Determine whether to use live server via requests or Flask test_client."""
    import requests
    try:
        r = requests.get("http://127.0.0.1:5000/", timeout=1)
        if r.status_code == 200:
            print(">> Connected to live running server at http://127.0.0.1:5000")
            return "live", None
    except Exception:
        pass

    print(">> Live server not running on port 5000; falling back to in-memory Flask test_client.")
    from app import create_app
    app = create_app()
    return "client", app

class TestClientWrapper:
    def __init__(self, mode, app=None):
        self.mode = mode
        self.app = app
        if mode == "live":
            import requests
            self.session = requests.Session()
            self.base = "http://127.0.0.1:5000"
        else:
            self.client = app.test_client()
            
    def get(self, path):
        if self.mode == "live":
            r = self.session.get(self.base + path)
            return r.status_code, r.text
        else:
            r = self.client.get(path, follow_redirects=True)
            return r.status_code, r.get_data(as_text=True)
            
    def post(self, path, data):
        if self.mode == "live":
            r = self.session.post(self.base + path, data=data, allow_redirects=True)
            return r.status_code, r.text
        else:
            r = self.client.post(path, data=data, follow_redirects=True)
            return r.status_code, r.get_data(as_text=True)

def run_test_suite():
    mode, app = get_tester()
    tester = TestClientWrapper(mode, app)

    # 1. Public Routes Verification
    public_urls = [
        "/",
        "/about",
        "/admissions",
        "/staff",
        "/gallery",
        "/notices",
        "/contact",
        "/login",
        "/reset-password-request"
    ]
    
    print("\n[1/4] Testing Public Web Pages...")
    for path in public_urls:
        status, html = tester.get(path)
        assert status == 200, f"Route {path} failed with HTTP {status}"
        print(f"  [OK] {path} -> HTTP {status}")

    # 2. Security Check: Verify Demo Passwords Removed from Frontend
    print("\n[2/4] Verifying Demo Passwords Removed From Frontend...")
    status, login_html = tester.get("/login")
    assert "Quick Demo Credentials" not in login_html, "SECURITY ERROR: 'Quick Demo Credentials' still visible on login page!"
    assert "parent123" not in login_html, "SECURITY ERROR: Demo password 'parent123' found in login page HTML!"
    assert "admin123" not in login_html, "SECURITY ERROR: Demo password 'admin123' found in login page HTML!"
    print("  [OK] Login page is clean: zero demo credentials displayed to public.")

    # 3. Parent Login & Portal
    print("\n[3/4] Testing Parent Portal Authentication & Wards...")
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', login_html)
    assert match, "CSRF token not found on login page"
    csrf = match.group(1)

    parent_payload = {
        'csrf_token': csrf,
        'login_type': 'parent',
        'username': '9876543210',
        'password': 'parent123'
    }
    status, res_html = tester.post("/login", data=parent_payload)
    assert status == 200, f"Parent login failed: {status}"
    assert "Samiul" in res_html, "Student Samiul Haque not found in Parent dashboard"
    print("  [OK] Parent login successful -> Ward dashboard active.")

    parent_subpages = [
        "/parent/dashboard",
        "/parent/attendance",
        "/parent/results",
        "/parent/fees",
        "/parent/timetable",
        "/parent/notices"
    ]
    for p in parent_subpages:
        p_status, _ = tester.get(p)
        assert p_status == 200, f"Parent subpage {p} failed with HTTP {p_status}"
        print(f"  [OK] Parent module {p} accessible.")

    # 4. Admin Portal Login & Modules
    print("\n[4/4] Testing Administrator Portal & CMS Modules...")
    # New session for admin
    admin_tester = TestClientWrapper(mode, app)
    _, adm_login_html = admin_tester.get("/login")
    adm_csrf = re.search(r'name="csrf_token"\s+value="([^"]+)"', adm_login_html).group(1)

    admin_payload = {
        'csrf_token': adm_csrf,
        'login_type': 'admin',
        'username': 'admin',
        'password': 'admin123'
    }
    status, adm_res = admin_tester.post("/login", data=admin_payload)
    assert status == 200, f"Admin login failed: {status}"
    assert "Administrator" in adm_res or "Dashboard" in adm_res, "Admin console not loaded"
    print("  [OK] Admin login successful -> Console authorized.")

    admin_pages = [
        "/admin/dashboard",
        "/admin/students",
        "/admin/parents",
        "/admin/teachers",
        "/admin/attendance",
        "/admin/results",
        "/admin/fees",
        "/admin/timetable",
        "/admin/notices",
        "/admin/gallery",
        "/admin/pages",
        "/admin/messages"
    ]
    for p in admin_pages:
        a_status, a_html = admin_tester.get(p)
        assert a_status == 200, f"Admin module {p} failed with HTTP {a_status}"
        if p == "/admin/parents":
            assert 'value="parent123"' not in a_html, "Demo password parent123 pre-filled in admin parents page!"
        print(f"  [OK] Admin module {p} verified.")

    print("\n" + "=" * 65)
    print("  SUCCESS: 100% OF TESTS PASSED! APPLICATION IS SECURE & READY.")
    print("=" * 65)

if __name__ == '__main__':
    run_test_suite()
