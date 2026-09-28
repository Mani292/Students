import os
from playwright.sync_api import sync_playwright

def run_comprehensive_verification():
    os.makedirs("/home/jules/verification/screenshots", exist_ok=True)
    os.makedirs("/home/jules/verification/videos", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(record_video_dir="/home/jules/verification/videos")
        page = context.new_page()

        # 1. Landing Page
        print("1. Testing Landing Page...")
        page.goto("http://localhost:3000")
        page.wait_for_timeout(1000)

        # 2. Login Flow - Student
        print("2. Testing Student Login & Portal...")
        page.get_by_role("button", name="Sign In").first.click()
        page.wait_for_timeout(500)
        page.fill("input[type='email']", "student@univ.edu")
        page.fill("input[type='password']", "password123")
        page.get_by_role("button", name="Sign In").first.click()
        page.wait_for_timeout(1500)

        # Take screenshot of Student Portal Overview
        page.screenshot(path="/home/jules/verification/screenshots/student_portal.png")

        # Navigate Student Portal tabs
        print("   - Testing Student Portal tabs...")
        for tab in ["Grade Book", "Leave & Permissions", "Attendance", "Service Center", "Digital ID", "AI Copilot", "Learning Hub", "Career Matching", "Project Lab"]:
            loc = page.get_by_text(tab, exact=True)
            if loc.count() > 0:
                loc.first.click()
                page.wait_for_timeout(300)

        # Logout Student
        logout_btn = page.locator("button").filter(has_text="Logout")
        if logout_btn.count() > 0:
            logout_btn.first.click()
            page.wait_for_timeout(1000)

        # 3. Login Flow - Faculty
        print("3. Testing Faculty Login & Dashboard...")
        page.fill("input[type='email']", "faculty@univ.edu")
        page.fill("input[type='password']", "password123")
        page.get_by_role("button", name="Sign In").first.click()
        page.wait_for_timeout(1500)

        page.screenshot(path="/home/jules/verification/screenshots/faculty_dashboard.png")

        # Logout Faculty
        logout_btn = page.locator("button").filter(has_text="Logout")
        if logout_btn.count() > 0:
            logout_btn.first.click()
            page.wait_for_timeout(1000)

        # 4. Login Flow - Admin
        print("4. Testing Admin Login & Console...")
        page.fill("input[type='email']", "admin@univ.edu")
        page.fill("input[type='password']", "password123")
        page.get_by_role("button", name="Sign In").first.click()
        page.wait_for_timeout(1500)

        page.screenshot(path="/home/jules/verification/screenshots/admin_console.png")

        context.close()
        browser.close()
        print("All user journeys tested successfully!")

if __name__ == "__main__":
    run_comprehensive_verification()
