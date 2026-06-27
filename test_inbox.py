from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time

print("Starting diagnostic 3...")
with Stealth().use_sync(sync_playwright()) as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="/Users/mohdtahaabbas/instagram-deaddict/notifier/ig_session",
        headless=True
    )
    page = browser.new_page()
    page.goto("https://www.instagram.com/direct/inbox/")
    time.sleep(8)
    
    # Let's find "mounika" and print its outerHTML
    try:
        el = page.locator('text="mounika"').first
        print("Outer HTML of mounika:")
        print(el.evaluate("el => el.outerHTML"))
        
        # Let's go up a few parents to see the structure of a chat row
        parent = page.locator('text="mounika"').first.locator('xpath=../../../..')
        print("Outer HTML of parent row:")
        print(parent.evaluate("el => el.outerHTML"))
    except Exception as e:
        print(f"Error finding mounika: {e}")

    browser.close()
print("Done.")
