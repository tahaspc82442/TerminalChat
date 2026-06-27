from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time

with Stealth().use_sync(sync_playwright()) as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="/Users/mohdtahaabbas/instagram-deaddict/notifier/ig_session",
        headless=True,
        viewport={"width": 1280, "height": 800}
    )
    page = browser.new_page()
    page.goto("https://www.instagram.com/direct/inbox/")
    time.sleep(5)
    
    # Click mounika
    el = page.locator('span[title="mounika" i]').first
    if el.count() > 0:
        el.click(force=True)
        time.sleep(5)
        
        script = """
        () => {
            let results = [];
            // Find all potential message bubbles. 
            // In IG, messages usually have specific background colors or are within row containers.
            // Let's get all leaf nodes that have text, or images.
            let elements = document.querySelectorAll('div[dir="auto"]');
            for (let el of elements) {
                let text = el.innerText.trim();
                let rect = el.getBoundingClientRect();
                
                // If the element is on the right half of the main chat pane (which starts around x=400)
                // Actually, let's just check if its center is > 800 (since screen is 1280)
                let center_x = rect.left + (rect.width / 2);
                let is_me = center_x > 800;
                
                let has_img = el.querySelector('img') !== null;
                
                if (text.length > 0 || has_img) {
                    if (text.length > 0 && text.length < 500 && !text.includes('\\n')) {
                         results.push({text: text, is_me: is_me, img: has_img, x: center_x});
                    } else if (has_img && text.length === 0) {
                         results.push({text: "[Attachment]", is_me: is_me, img: true, x: center_x});
                    }
                }
            }
            return results;
        }
        """
        data = page.evaluate(script)
        for d in data:
            print(d)
    browser.close()
