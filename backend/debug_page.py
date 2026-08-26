from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:3000")
    page.wait_for_timeout(2000)
    print("Page Title:", page.title())
    print("Page Content snippet:", page.content()[:500])
    page.screenshot(path="/home/jules/verification/screenshots/debug.png")
    browser.close()
