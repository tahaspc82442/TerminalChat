import threading
import queue
import time
import sys
import os


from engine import InstagramEngine

# ANSI Escape Codes for Retro Vibe
GREEN = '\033[1;32m'
DIM_GREEN = '\033[0;32m'
RESET = '\033[0m'
BLINK_BLOCK = '\033[1 q' # Blinking block cursor
RESET_CURSOR = '\033[0 q' # Default cursor
CLEAR = '\033[2J\033[H' # Clear screen and move to top

def typewriter_print(text, delay=0.015):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

class CLIApp:
    def __init__(self):
        self.output_queue = queue.Queue()
        self.engine = None
        self.current_chat = None
        self.running = True
        
    def start(self):
        # Apply retro styling
        sys.stdout.write(CLEAR + GREEN + BLINK_BLOCK)
        sys.stdout.flush()
        
        ascii_logo = """
 _____                   _             _  ____ _           _   
|_   _|__ _ __ _ __ _(_)_ __  __ _| |/ ___| |__   __ _| |_ 
  | |/ _ \\ '__| '_ ` _ \\| | '_ \\/ _` | | |    | '_ \\ / _` | __|
  | |  __/ |  | | | | | | | | | | (_| | | |___| | | | (_| | |_ 
  |_|\\___|_|  |_| |_| |_|_|_| |_|\\__,_|_|\\____|_| |_|\\__,_|\\__|
                                                               
        """
        typewriter_print(ascii_logo, 0.005)
        typewriter_print("[*] ESTABLISHING CONNECTION...", 0.03)
        typewriter_print("[*] INITIALIZING ENGINE...", 0.03)
        
        # Ensure Playwright browser is installed for distribution
        try:
            from playwright._impl._driver import compute_driver_executable, get_driver_env
            import subprocess
            driver_executable = compute_driver_executable()
            env = get_driver_env()
            subprocess.run([driver_executable, "install", "chromium"], env=env, check=True)
        except Exception:
            pass # Fail silently, engine will catch error later if it didn't work
        
        self.engine = InstagramEngine(self.output_queue)
        
        # Start a thread to listen for engine outputs
        printer_thread = threading.Thread(target=self.print_worker, daemon=True)
        printer_thread.start()
        
        # Wait until browser is ready
        while True:
            # We just sleep, the printer_thread will print "Ready."
            time.sleep(1)
            if hasattr(self, 'browser_ready') and self.browser_ready:
                break
                
        typewriter_print("\n[READY]", 0.05)
        typewriter_print("AVAILABLE COMMANDS:", 0.02)
        typewriter_print("  /chat [Name]   - Open a chat", 0.02)
        typewriter_print("  /inbox         - List available chats", 0.02)
        typewriter_print("  /quit          - Exit TerminalChat\n", 0.02)
        
        # Main input loop
        while self.running:
            try:
                # Bash-style hacker prompt
                prompt = f"{GREEN}root@ig-server:~/{self.current_chat}$ {RESET}{GREEN}" if self.current_chat else f"{GREEN}root@ig-server:~/$ {RESET}{GREEN}"
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() == '/quit' or user_input.lower() == '/exit':
                    print("\nShutting down safely (closing browser)...")
                    self.engine.send_command("quit")
                    time.sleep(2)
                    self.running = False
                    break
                    
                elif user_input.lower() == '/refresh':
                    self.engine.send_command("load_inbox")
                    
                elif user_input.lower() == '/inbox':
                    self.current_chat = None
                    self.engine.send_command("inbox")
                    
                elif user_input.startswith('/chat '):
                    name = user_input.split(' ', 1)[1].strip()
                    self.current_chat = name
                    self.engine.send_command("open_chat", chat_name=name)
                    
                elif user_input.startswith('/'):
                    print(f"{DIM_GREEN}Unknown command. Use /chat [Name], /inbox, or /quit{GREEN}")
                    
                else:
                    if self.current_chat:
                        self.engine.send_command("send_message", text=user_input)
                    else:
                        print(f"{DIM_GREEN}Error: No active channel. Use /chat [Name] to establish connection.{GREEN}")
            
            except KeyboardInterrupt:
                self.running = False
                break
                
        print(f"\n{DIM_GREEN}[*] TERMINATING SECURE CONNECTION...{GREEN}")
        # Reset terminal to normal before exiting
        sys.stdout.write(RESET + RESET_CURSOR)
        sys.stdout.flush()
        sys.exit(0)
        
    def print_worker(self):
        while self.running:
            try:
                msg = self.output_queue.get(timeout=1.0)
                msg_type = msg.get("type")
                
                # Clear current input line to prevent messy text overlap
                sys.stdout.write('\r\033[K') 
                
                if msg_type == "status":
                    text = msg.get("message")
                    if text == "Ready.":
                        self.browser_ready = True
                    # Only print important statuses to keep terminal clean
                    if "Opening" in text or "Sent" in text or "error" in text.lower():
                        print(f"[*] {text}")
                
                elif msg_type == "login_required":
                    sys.stdout.write(f"\r\033[K{GREEN}[!] ACCESS DENIED. NO VALID SESSION FOUND.{RESET}\n")
                    input(f"{GREEN}[*] Press ENTER to launch authentication window...{RESET}")
                    # Stop the current engine
                    if self.engine:
                        self.engine.send_command("quit")
                    
                    from engine import authenticate
                    authenticate()
                    
                    # Restart engine after successful login
                    print(f"{GREEN}[*] Rebooting Secure Terminal...{RESET}")
                    self.engine = InstagramEngine(self.output_queue)
                    
                elif msg_type == "error":
                    print(f"[!] ERROR: {msg.get('message')}")
                    
                elif msg_type == "inbox_data":
                    chats = msg.get("chats", [])
                    print(f"\n{DIM_GREEN}--- AVAILABLE CHATS ---")
                    for c in chats:
                        print(f" [+] {c}")
                    print(f"-----------------------{GREEN}\n")
                    
                elif msg_type == "chat_history":
                    messages = msg.get("messages", [])
                    print(f"\n{DIM_GREEN}--- CHAT: {self.current_chat.upper()} ---{GREEN}")
                    
                    import shutil
                    terminal_width = shutil.get_terminal_size().columns
                    
                    for m in messages:
                        text = m.get("text", "")
                        is_me = m.get("is_me", False)
                        
                        if is_me:
                            # Right align
                            formatted = f"[YOU] {text}"
                            padding = max(0, terminal_width - len(formatted) - 2)
                            print(" " * padding + formatted)
                        else:
                            # Left align
                            print(f"{DIM_GREEN}[{self.current_chat.upper()}] {text}{GREEN}")
                            
                    print(f"{DIM_GREEN}" + "-" * 30 + f"{GREEN}\n")
                
                # Reprint the prompt after printing background messages
                prompt = f"{GREEN}root@ig-server:~/{self.current_chat}$ {RESET}{GREEN}" if self.current_chat else f"{GREEN}root@ig-server:~/$ {RESET}{GREEN}"
                sys.stdout.write(prompt)
                sys.stdout.flush()
                
            except queue.Empty:
                continue

if __name__ == "__main__":
    app = CLIApp()
    app.start()
