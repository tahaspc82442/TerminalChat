import customtkinter as ctk
import queue
import threading
from engine import InstagramEngine

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Distraction-Free Instagram")
        self.geometry("900x600")
        
        # Grid layout (1 row, 2 columns)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1) # Sidebar (small)
        self.grid_columnconfigure(1, weight=3) # Main chat area (large)

        # ---------------- LEFT SIDEBAR (Chats) ----------------
        self.sidebar_frame = ctk.CTkScrollableFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Inbox", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.chat_buttons = []
        
        # ---------------- RIGHT MAIN AREA (Messages) ----------------
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Chat history textbox
        self.chat_history = ctk.CTkTextbox(self.main_frame, state="disabled", wrap="word", font=ctk.CTkFont(size=14))
        self.chat_history.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")

        # Input area
        self.input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.message_input = ctk.CTkEntry(self.input_frame, placeholder_text="Type a message...")
        self.message_input.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.message_input.bind("<Return>", self.send_message_event)

        self.send_button = ctk.CTkButton(self.input_frame, text="Send", width=80, command=self.send_message)
        self.send_button.grid(row=0, column=1, sticky="e")
        
        # Status Bar
        self.status_label = ctk.CTkLabel(self.main_frame, text="Initializing engine...", text_color="gray")
        self.status_label.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="w")

        # ---------------- ENGINE SETUP ----------------
        self.output_queue = queue.Queue()
        self.engine = InstagramEngine(self.output_queue)
        
        self.current_chat = None
        
        # Start queue polling
        self.after(100, self.check_queue)

    def check_queue(self):
        try:
            while True:
                msg = self.output_queue.get_nowait()
                msg_type = msg.get("type")
                
                if msg_type == "status":
                    self.status_label.configure(text=msg.get("message"))
                
                elif msg_type == "error":
                    self.status_label.configure(text=f"Error: {msg.get('message')}", text_color="red")
                    
                elif msg_type == "inbox_data":
                    self.populate_sidebar(msg.get("chats", []))
                    
                elif msg_type == "chat_history":
                    self.display_messages(msg.get("messages", []))
                    
        except queue.Empty:
            pass
            
        self.after(100, self.check_queue)

    def populate_sidebar(self, chats):
        # Clear existing buttons
        for btn in self.chat_buttons:
            btn.destroy()
        self.chat_buttons.clear()
        
        for i, chat_name in enumerate(chats):
            btn = ctk.CTkButton(self.sidebar_frame, text=chat_name, fg_color="transparent", 
                                text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                anchor="w", command=lambda n=chat_name: self.open_chat(n))
            btn.grid(row=i+1, column=0, padx=10, pady=5, sticky="ew")
            self.chat_buttons.append(btn)

    def open_chat(self, chat_name):
        self.current_chat = chat_name
        self.status_label.configure(text=f"Opening {chat_name}...")
        
        self.chat_history.configure(state="normal")
        self.chat_history.delete("0.0", "end")
        self.chat_history.insert("end", f"Loading conversation with {chat_name}...\n")
        self.chat_history.configure(state="disabled")
        
        self.engine.send_command("open_chat", chat_name=chat_name)

    def display_messages(self, messages):
        self.chat_history.configure(state="normal")
        self.chat_history.delete("0.0", "end")
        
        if not messages:
            self.chat_history.insert("end", "No messages found or unable to parse.")
        else:
            for m in messages:
                self.chat_history.insert("end", f"{m}\n\n")
                
        self.chat_history.configure(state="disabled")
        # Scroll to bottom
        self.chat_history.yview("end")

    def send_message_event(self, event):
        self.send_message()

    def send_message(self):
        text = self.message_input.get().strip()
        if text and self.current_chat:
            self.message_input.delete(0, "end")
            
            # Optimistically add to UI
            self.chat_history.configure(state="normal")
            self.chat_history.insert("end", f"You: {text}\n\n")
            self.chat_history.configure(state="disabled")
            self.chat_history.yview("end")
            
            self.engine.send_command("send_message", text=text)

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
