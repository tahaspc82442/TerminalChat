import threading
import queue
import time
import os

# Crucial fix for PyInstaller: Force Playwright to use user directory instead of temp bundle directory
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.expanduser("~/Library/Caches/ms-playwright")

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import json

class InstagramEngine:
    def __init__(self, output_queue):
        self.input_queue = queue.Queue()
        self.output_queue = output_queue
        self.browser_context = None
        self.page = None
        self.current_polling_chat = None
        self.last_scraped_messages = None
        import os
        self.user_data_dir = os.path.expanduser("~/.terminalchat_session")
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def send_command(self, action, **kwargs):
        kwargs['action'] = action
        self.input_queue.put(kwargs)

    def _run(self):
        with Stealth().use_sync(sync_playwright()) as p:
            try:
                self.output_queue.put({"type": "status", "message": "Launching browser..."})
                self.browser_context = p.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir,
                    headless=True,
                    viewport={"width": 1280, "height": 800}
                )
                self.page = self.browser_context.new_page()
                
                # Navigate to inbox initially
                self.output_queue.put({"type": "status", "message": "Loading Instagram..."})
                self.page.goto("https://www.instagram.com/direct/inbox/")
                
                try:
                    self.page.wait_for_load_state("networkidle", timeout=10000)
                except:
                    pass
                
                # Check for login redirect
                if "login" in self.page.url or "accounts" in self.page.url:
                    self.output_queue.put({"type": "login_required"})
                    self.browser_context.close()
                    return # Exit the thread
                    
                self.output_queue.put({"type": "status", "message": "Ready."})
                self._scrape_inbox()

                # Event loop
                while True:
                    try:
                        cmd = self.input_queue.get(timeout=2.0)
                        action = cmd.get("action")
                        
                        if action == "load_inbox":
                            self._scrape_inbox()
                        elif action == "open_chat":
                            self._open_chat(cmd.get("chat_name"))
                        elif action == "send_message":
                            self._send_message(cmd.get("text"))
                        elif action == "quit":
                            if self.browser_context:
                                self.browser_context.close()
                            break
                        elif action == "inbox":
                            self.current_polling_chat = None
                            self.last_scraped_messages = None
                            self._scrape_inbox()
                            
                        self.input_queue.task_done()
                    except queue.Empty:
                        # Polling loop for live chat updates
                        if self.current_polling_chat:
                            self._scrape_messages(silent=True)
                        continue

            except Exception as e:
                self.output_queue.put({"type": "error", "message": str(e)})

    def _scrape_inbox(self):
        self.output_queue.put({"type": "status", "message": "Fetching inbox..."})
        try:
            # Go back to inbox root if not there
            if not self.page.url.endswith("inbox/"):
                self.page.goto("https://www.instagram.com/direct/inbox/")
                time.sleep(2)

            # On some Instagram versions, there are no A tags. 
            # Chats are contained in div/spans with dir="auto" containing a span with a title.
            chat_elements = self.page.locator('span[dir="auto"] span[title]').all()
            
            chats = []
            seen = set()
            for el in chat_elements:
                try:
                    name = el.get_attribute("title")
                    if name and name not in seen:
                        seen.add(name)
                        chats.append(name)
                except:
                    pass
                    
            self.output_queue.put({"type": "inbox_data", "chats": chats})
            self.output_queue.put({"type": "status", "message": "Inbox loaded."})
        except Exception as e:
            self.output_queue.put({"type": "error", "message": f"Inbox error: {e}"})

    def _open_chat(self, chat_name):
        self.output_queue.put({"type": "status", "message": f"Opening {chat_name}..."})
        try:
            # First ensure we are in the inbox
            if not self.page.url.endswith("inbox/"):
                self.page.goto("https://www.instagram.com/direct/inbox/")
                time.sleep(2)
                
            # Find the chat by its title attribute (case insensitive CSS selector)
            # The 'i' at the end makes it case-insensitive
            chat_el = self.page.locator(f'span[title="{chat_name}" i]').first
            
            if chat_el.count() == 0:
                # Fallback to pseudo text selector
                chat_el = self.page.locator(f'span:has-text("{chat_name}")').first
                
            if chat_el.count() > 0:
                # Force click to bypass transparent overlays
                chat_el.click(force=True)
                time.sleep(3) # Wait for the chat messages to load
                self.current_polling_chat = chat_name
                self.last_scraped_messages = None
                self._scrape_messages()
            else:
                self.output_queue.put({"type": "error", "message": f"Could not find '{chat_name}' in your recent chats. Try running /refresh"})
        except Exception as e:
            self.output_queue.put({"type": "error", "message": f"Open chat error: {e}"})

    def _scrape_messages(self, silent=False):
        try:
            script = """
            () => {
                let results = [];
                // Find all leaf nodes that have text or are images
                let elements = document.querySelectorAll('div[dir="auto"], span[dir="auto"]');
                let validElements = [];
                
                for (let el of elements) {
                    if (el.children.length > 0 && !el.querySelector('img')) continue;
                    validElements.push(el);
                }
                
                // Also grab any stray images inside message rows
                let imgs = document.querySelectorAll('div[role="row"] img');
                for (let img of imgs) validElements.push(img);
                
                // Fallback to all auto divs if we need to
                if (validElements.length === 0) {
                    validElements = document.querySelectorAll('div[dir="auto"]');
                }
                
                for (let el of validElements) {
                    let text = el.innerText ? el.innerText.trim() : "";
                    let rect = el.getBoundingClientRect();
                    
                    if (rect.width === 0 || rect.height === 0) continue;
                    
                    let center_x = rect.left + (rect.width / 2);
                    let is_me = center_x > 800; // Screen is 1280 wide
                    let has_img = el.tagName.toLowerCase() === 'img' || el.querySelector('img') !== null;
                    
                    // Filter out time stamps (usually short, simple text like "9m")
                    // We only want actual messages or attachments
                    if (text.length > 0 || has_img) {
                        // Avoid duplicates or massively long text blocks that are layout wrappers
                        if (text.length > 0 && text.length < 1000 && !text.includes('\\n')) {
                             results.push({text: text, is_me: is_me, img: has_img});
                        } else if (has_img && text.length === 0) {
                             results.push({text: "[Attachment]", is_me: is_me, img: true});
                        }
                    }
                }
                
                // Clean up results (remove duplicates that might happen from nested divs)
                let final_results = [];
                for (let i = 0; i < results.length; i++) {
                    if (i > 0 && results[i].text === results[i-1].text && results[i].is_me === results[i-1].is_me) {
                        continue;
                    }
                    final_results.push(results[i]);
                }
                return final_results.slice(-15); // Return last 15 messages
            }
            """
            messages = self.page.evaluate(script)
            
            # Check if it has changed since last scrape
            import json
            current_state = json.dumps(messages)
            if current_state != self.last_scraped_messages:
                self.last_scraped_messages = current_state
                self.output_queue.put({"type": "chat_history", "messages": messages})
                if not silent:
                    self.output_queue.put({"type": "status", "message": "Chat loaded."})
                
        except Exception as e:
            if not silent:
                self.output_queue.put({"type": "error", "message": f"Message scrape error: {e}"})

    def _send_message(self, text):
        self.output_queue.put({"type": "status", "message": "Sending message..."})
        try:
            # Find the message input box. It's usually a div with contenteditable="true" or a textarea
            input_box = self.page.locator('div[contenteditable="true"]').first
            if not input_box:
                input_box = self.page.locator('textarea').first
                
            if input_box:
                input_box.fill(text)
                input_box.press("Enter")
                time.sleep(1)
                self.output_queue.put({"type": "status", "message": "Message sent."})
                # Reload chat history to show the new message
                self._scrape_messages()
            else:
                self.output_queue.put({"type": "error", "message": "Could not find input box."})
        except Exception as e:
            self.output_queue.put({"type": "error", "message": f"Send error: {e}"})

def authenticate():
    import os
    print("[*] Launching authentication browser...")
    user_data_dir = os.path.expanduser("~/.terminalchat_session")
    with Stealth().use_sync(sync_playwright()) as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        page.goto("https://www.instagram.com/direct/inbox/")
        
        print("[*] Please log in to Instagram in the popup window.")
        print("[*] Waiting for successful login...")
        
        while "login" in page.url or "accounts" in page.url:
            try:
                page.wait_for_timeout(1000)
            except:
                # Browser was closed
                break
                
        print("[+] Authentication detected! Saving session and closing browser...")
        time.sleep(3) # Wait for cookies to settle
        try:
            context.close()
        except:
            pass
