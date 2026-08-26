import os
import time
from playwright.sync_api import sync_playwright

os.makedirs("/home/jules/verification/videos", exist_ok=True)
os.makedirs("/home/jules/verification/screenshots", exist_ok=True)

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="/home/jules/verification/videos"
        )
        page = context.new_page()
        try:
            page.goto("http://localhost:3000")
            page.wait_for_timeout(1000)

            # 1. Login View Screenshot & Action
            page.screenshot(path="/home/jules/verification/screenshots/1_login_view.png")
            page.get_by_role("button", name="Sign In to Ecosystem").click()
            page.wait_for_timeout(1000)

            # 2. Student Portal Screenshot
            page.screenshot(path="/home/jules/verification/screenshots/2_student_portal.png")
            page.wait_for_timeout(1000)

            # 3. Smart Attendance Tab
            page.get_by_role("button", name="Smart Attendance").click()
            page.wait_for_timeout(500)
            page.get_by_placeholder("e.g. 4A9F21").fill("8F2A91")
            page.get_by_role("button", name="Submit Attendance Verification").click()
            page.wait_for_timeout(1000)
            page.screenshot(path="/home/jules/verification/screenshots/3_attendance_verification.png")

            # 4. AI Copilot Chat Tab
            page.get_by_role("button", name="AI Copilot Chat").click()
            page.wait_for_timeout(500)
            page.get_by_placeholder("Ask about attendance, policies, or career...").fill("What is the attendance policy requirement?")
            page.keyboard.press("Enter")
            page.wait_for_timeout(1500)
            page.screenshot(path="/home/jules/verification/screenshots/4_ai_copilot_chat.png")

            # Final screenshot
            page.screenshot(path="/home/jules/verification/screenshots/verification.png")
            print("Playwright frontend verification completed successfully.")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    run_verification()
