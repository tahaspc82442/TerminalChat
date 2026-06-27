from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time

print("Starting screenshot diagnostic...")
with Stealth().use_sync(sync_playwright()) as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="/Users/mohdtahaabbas/instagram-deaddict/notifier/ig_session",
        headless=True,
        viewport={"width": 1280, "height": 800}
    )
    page = browser.new_page()
    page.goto("https://www.instagram.com/direct/inbox/")
    time.sleep(8)
    
    # Click mounika
    el = page.locator('span[title="mounika" i]').first
    if el.count() > 0:
        el.click(force=True)
        print("Clicked mounika, waiting 8 seconds for chat to load...")
        time.sleep(8)
        
        print("Taking screenshot...")
        page.screenshot(path="/Users/mohdtahaabbas/.gemini/antigravity-cli/brain/62ff0c33-7709-4514-8111-38a669f57fd9/chat_screenshot.png")
    else:
        print("Could not find mounika")

    browser.close()
print("Done.")
