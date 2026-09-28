import os
from playwright.sync_api import sync_playwright

def run_verification():
    os.makedirs("/home/jules/verification/screenshots", exist_ok=True)
    os.makedirs("/home/jules/verification/videos", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(record_video_dir="/home/jules/verification/videos")
        page = context.new_page()

        # 1. Open Landing Page
        page.goto("http://localhost:3000")
        page.wait_for_timeout(1000)

        # 2. Click "Get Started" or "Sign In"
        page.get_by_role("button", name="Sign In").first.click()
        page.wait_for_timeout(1000)

        # 3. Fill Login
        page.fill("input[type='email']", "student@univ.edu")
        page.fill("input[type='password']", "password123")
        page.get_by_role("button", name="Sign In").first.click()
        page.wait_for_timeout(2000)

        # 4. Take Screenshot of Student Portal
        page.screenshot(path="/home/jules/verification/screenshots/verification.png")

        context.close()
        browser.close()

if __name__ == "__main__":
    run_verification()
