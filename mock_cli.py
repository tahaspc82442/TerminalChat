import sys
import time
import shutil

GREEN = '\033[0;32m'
DIM_GREEN = '\033[0;32m'
RESET = '\033[0m'
BLINK_BLOCK = '\033[1 q' 
CLEAR = '\033[2J\033[H'

def type_out(text, delay=0.015, newline=True):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    if newline:
        print()

def main():
    sys.stdout.write(CLEAR + GREEN + BLINK_BLOCK)
    sys.stdout.flush()
    
    ascii_logo = """
 _____                   _             _  ____ _           _   
|_   _|__ _ __ _ __ _(_)_ __  __ _| |/ ___| |__   __ _| |_ 
  | |/ _ \\ '__| '_ ` _ \\| | '_ \\/ _` | | |    | '_ \\ / _` | __|
  | |  __/ |  | | | | | | | | | | (_| | | |___| | | | (_| | |_ 
  |_|\\___|_|  |_| |_| |_|_|_| |_|\\__,_|_|\\____|_| |_|\\__,_|\\__|
    """
    print(ascii_logo)
    
    type_out("[*] ESTABLISHING CONNECTION...", 0.03)
    type_out("[*] INITIALIZING ENGINE...", 0.03)
    time.sleep(1)
    type_out("[*] Ready.", 0.03)
    time.sleep(0.5)
    
    type_out("\n[READY]", 0.05)
    type_out("AVAILABLE COMMANDS:", 0.01)
    type_out("  /chat [Name]   - Open a chat", 0.01)
    type_out("  /inbox         - List available chats", 0.01)
    type_out("  /quit          - Exit TerminalChat\n", 0.01)
    
    # Prompt 1
    sys.stdout.write(f"{GREEN}root@ig-server:~/$ {RESET}{GREEN}")
    sys.stdout.flush()
    time.sleep(1)
    type_out("/inbox", 0.1)
    
    print(f"\n{DIM_GREEN}--- AVAILABLE CHATS ---")
    print(" [+] Trinity")
    print(" [+] Morpheus")
    print(" [+] Agent Smith")
    print(f"-----------------------{GREEN}\n")
    
    # Prompt 2
    sys.stdout.write(f"{GREEN}root@ig-server:~/$ {RESET}{GREEN}")
    sys.stdout.flush()
    time.sleep(1.5)
    type_out("/chat Trinity", 0.1)
    print("[*] Opening Trinity...")
    time.sleep(0.5)
    
    print(f"\n{DIM_GREEN}--- CHAT: TRINITY ---{GREEN}")
    
    terminal_width = 80
    
    # Message 1
    print(f"{DIM_GREEN}[TRINITY] Neo...{GREEN}")
    # Message 2
    formatted = f"[YOU] Who is this?"
    padding = max(0, terminal_width - len(formatted) - 2)
    print(" " * padding + formatted)
    # Message 3
    print(f"{DIM_GREEN}[TRINITY] Follow the white rabbit.{GREEN}")
    print(f"{DIM_GREEN}" + "-" * 30 + f"{GREEN}\n")
    
    # Prompt 3
    sys.stdout.write(f"{GREEN}root@ig-server:~/Trinity$ {RESET}{GREEN}")
    sys.stdout.flush()
    time.sleep(2)
    type_out("Down the rabbit hole...", 0.1)
    
    formatted = f"[YOU] Down the rabbit hole..."
    padding = max(0, terminal_width - len(formatted) - 2)
    print(" " * padding + formatted)
    
    sys.stdout.write(f"{GREEN}root@ig-server:~/Trinity$ {RESET}{GREEN}")
    sys.stdout.flush()
    time.sleep(3)

if __name__ == "__main__":
    main()
