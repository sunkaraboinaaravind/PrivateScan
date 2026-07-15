import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import queue

from app.processor import FileProcessor
from app.ai_engine import AIEngine

# Color Palette (Premium Dark Mode)
BG_MAIN = "#121212"       # Deep dark background
BG_CARD = "#1E1E1E"       # Cards/Panels background
BG_WIDGET = "#2D2D2D"     # Entry fields/button hover
ACCENT_PRIMARY = "#BB86FC" # Light purple accent
ACCENT_SECONDARY = "#03DAC6"# Cyan accent
TEXT_MAIN = "#E0E0E0"      # Off-white text
TEXT_MUTED = "#A0A0A0"     # Gray muted text
BORDER_COLOR = "#333333"   # Subtle border

class PrivateScanApp(tk.Tk):
    """The main desktop application GUI for PrivateScan."""

    def __init__(self):
        super().__init__()
        
        self.title("PrivateScan — Offline Document & Image Analyzer")
        self.geometry("1100x750")
        self.configure(bg=BG_MAIN)
        
        # Initialize engines
        self.ai = AIEngine()
        self.current_file_path = None
        self.extracted_text = ""
        self.chat_history = []
        self.stream_queue = queue.Queue()
        
        # Configure styles
        self._setup_styles()
        
        # Build UI layout
        self._build_ui()
        
        # Check connection on start
        self._refresh_models()

    def _setup_styles(self):
        """Configure ttk theme and custom styles."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # General window styles
        self.style.configure(".", background=BG_MAIN, foreground=TEXT_MAIN, fieldbackground=BG_WIDGET)
        
        # Frames
        self.style.configure("TFrame", background=BG_MAIN)
        self.style.configure("Card.TFrame", background=BG_CARD, borderwidth=1, relief="solid")
        
        # Labels
        self.style.configure("TLabel", background=BG_MAIN, foreground=TEXT_MAIN, font=("Helvetica", 10))
        self.style.configure("Title.TLabel", background=BG_MAIN, foreground=ACCENT_PRIMARY, font=("Helvetica", 16, "bold"))
        self.style.configure("Subtitle.TLabel", background=BG_MAIN, foreground=TEXT_MUTED, font=("Helvetica", 9, "italic"))
        self.style.configure("CardTitle.TLabel", background=BG_CARD, foreground=ACCENT_SECONDARY, font=("Helvetica", 12, "bold"))
        self.style.configure("Muted.TLabel", background=BG_CARD, foreground=TEXT_MUTED, font=("Helvetica", 10))
        self.style.configure("Status.TLabel", background=BG_MAIN, foreground=TEXT_MUTED, font=("Helvetica", 9))
        
        # Buttons
        self.style.configure(
            "TButton", 
            background=BG_WIDGET, 
            foreground=TEXT_MAIN, 
            borderwidth=0, 
            font=("Helvetica", 10, "bold"),
            padding=8
        )
        self.style.map("TButton", background=[("active", ACCENT_PRIMARY), ("disabled", "#555555")], foreground=[("active", "#121212")])
        
        self.style.configure("Accent.TButton", background=ACCENT_PRIMARY, foreground="#121212")
        self.style.map("Accent.TButton", background=[("active", "#D7B5FF")])
        
        # Tabs
        self.style.configure("TNotebook", background=BG_MAIN, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=BG_CARD, foreground=TEXT_MUTED, font=("Helvetica", 10, "bold"), padding=6)
        self.style.map("TNotebook.Tab", background=[("selected", BG_MAIN)], foreground=[("selected", ACCENT_PRIMARY)])

    def _build_ui(self):
        """Assemble all widgets in the window."""
        # Top Header
        header_frame = ttk.Frame(self, padding=(15, 10))
        header_frame.pack(fill=tk.X)
        
        title_lbl = ttk.Label(header_frame, text="🔒 PRIVATESCAN", style="Title.TLabel")
        title_lbl.pack(side=tk.LEFT)
        
        subtitle_lbl = ttk.Label(header_frame, text="   100% On-Device AI Document Intelligence", style="Subtitle.TLabel")
        subtitle_lbl.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Connection status / Model Selector
        self.conn_lbl = ttk.Label(header_frame, text="Ollama: Checking...", foreground=TEXT_MUTED)
        self.conn_lbl.pack(side=tk.RIGHT, padx=10)
        
        self.model_combo = ttk.Combobox(header_frame, state="readonly", width=20, font=("Helvetica", 9))
        self.model_combo.pack(side=tk.RIGHT, padx=5)
        
        refresh_btn = ttk.Button(header_frame, text="🔄", width=3, command=self._refresh_models)
        refresh_btn.pack(side=tk.RIGHT)

        # Main Workspace (Split Pane)
        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Left Column: Document Manager & Text Viewer
        left_column = ttk.Frame(paned_window, padding=5)
        paned_window.add(left_column, weight=1)

        # File Drop Zone / Selector card
        drop_card = ttk.Frame(left_column, style="Card.TFrame", padding=15)
        drop_card.pack(fill=tk.X, pady=(0, 10))

        self.drop_lbl = ttk.Label(drop_card, text="Click to Browse & Load File\nSupports PDF, Images, DOCX, CSV, Text & Code", style="Muted.TLabel", justify=tk.CENTER)
        self.drop_lbl.pack(fill=tk.BOTH, expand=True, pady=10)
        drop_card.bind("<Button-1>", lambda e: self._browse_file())
        self.drop_lbl.bind("<Button-1>", lambda e: self._browse_file())

        # Document Details card
        self.meta_frame = ttk.Frame(left_column, style="Card.TFrame", padding=10)
        self.meta_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.meta_lbl = ttk.Label(self.meta_frame, text="No document loaded.", style="Muted.TLabel")
        self.meta_lbl.pack(anchor=tk.W)

        # Extracted Text Viewer
        text_viewer_frame = ttk.Frame(left_column, style="Card.TFrame", padding=10)
        text_viewer_frame.pack(fill=tk.BOTH, expand=True)

        tv_title = ttk.Label(text_viewer_frame, text="Extracted Text Preview", style="CardTitle.TLabel")
        tv_title.pack(anchor=tk.W, pady=(0, 5))

        self.text_preview = tk.Text(
            text_viewer_frame, 
            bg="#181818", 
            fg=TEXT_MAIN, 
            insertbackground=TEXT_MAIN, 
            font=("Consolas", 10),
            bd=0, 
            padx=10, 
            pady=10,
            wrap=tk.WORD
        )
        self.text_preview.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(text_viewer_frame, command=self.text_preview.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.text_preview.config(yscrollcommand=scrollbar.set)

        # Right Column: Analysis Tabs
        right_column = ttk.Frame(paned_window, padding=5)
        paned_window.add(right_column, weight=1)

        # Notebook tabs
        self.notebook = ttk.Notebook(right_column)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Actions Panel
        self.tab_actions = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_actions, text="✨ Analysis Actions")
        self._build_actions_tab()

        # Tab 2: Q&A Chat Panel
        self.tab_chat = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_chat, text="💬 Ask Document")
        self._build_chat_tab()

        # Bottom Status Bar
        self.status_bar = ttk.Label(self, text="Ready", style="Status.TLabel", padding=(15, 5))
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Periodic GUI queue poller
        self._poll_queue()

    def _build_actions_tab(self):
        """Construct the UI inside the Actions tab."""
        # Top button control row
        btn_frame = ttk.Frame(self.tab_actions, padding=10)
        btn_frame.pack(fill=tk.X)

        self.btn_sum = ttk.Button(btn_frame, text="📝 Summarize", command=lambda: self._run_analysis("summarize"))
        self.btn_sum.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.btn_pii = ttk.Button(btn_frame, text="🔍 Detect PII", command=lambda: self._run_analysis("pii"))
        self.btn_pii.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.btn_ext = ttk.Button(btn_frame, text="🔑 Key Info", command=lambda: self._run_analysis("key_info"))
        self.btn_ext.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # Output Text Pane
        output_frame = ttk.Frame(self.tab_actions, style="Card.TFrame", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        out_title = ttk.Label(output_frame, text="AI Analysis Results", style="CardTitle.TLabel")
        out_title.pack(anchor=tk.W, pady=(0, 5))

        self.output_text = tk.Text(
            output_frame, 
            bg="#181818", 
            fg=TEXT_MAIN, 
            insertbackground=TEXT_MAIN, 
            font=("Segoe UI", 10),
            bd=0, 
            padx=10, 
            pady=10,
            wrap=tk.WORD
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.output_text.config(yscrollcommand=scrollbar.set)

    def _build_chat_tab(self):
        """Construct the UI inside the Q&A Chat tab."""
        chat_frame = ttk.Frame(self.tab_chat, style="Card.TFrame", padding=10)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Chat history view
        self.chat_view = tk.Text(
            chat_frame, 
            bg="#181818", 
            fg=TEXT_MAIN, 
            insertbackground=TEXT_MAIN, 
            font=("Segoe UI", 10),
            bd=0, 
            padx=10, 
            pady=10,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.chat_view.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(chat_frame, command=self.chat_view.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.chat_view.config(yscrollcommand=scrollbar.set)

        # Message input area
        input_frame = ttk.Frame(self.tab_chat, padding=(0, 5))
        input_frame.pack(fill=tk.X)

        self.chat_input = ttk.Entry(input_frame, font=("Segoe UI", 11))
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_input.bind("<Return>", lambda e: self._send_chat())

        self.btn_send = ttk.Button(input_frame, text="Send", command=self._send_chat, style="Accent.TButton")
        self.btn_send.pack(side=tk.RIGHT)

        self.btn_clear = ttk.Button(input_frame, text="Clear", width=5, command=self._clear_chat)
        self.btn_clear.pack(side=tk.RIGHT, padx=5)

    def _refresh_models(self):
        """Refresh models list and update status label."""
        if self.ai.check_connection():
            self.conn_lbl.config(text="Ollama: Connected ✅", foreground="#03DAC6")
            models = self.ai.list_local_models()
            if models:
                self.model_combo.config(values=models)
                # Try to pick a default model
                default_idx = 0
                for i, m in enumerate(models):
                    if "llama3" in m or "llama" in m:
                        default_idx = i
                        break
                self.model_combo.current(default_idx)
                self._set_status("Ollama server connected. Models loaded successfully.")
            else:
                self.model_combo.config(values=["No models pulled!"])
                self.model_combo.current(0)
                self._set_status("Ollama running, but no models found. Run 'ollama pull llama3.2' first.")
        else:
            self.conn_lbl.config(text="Ollama: Offline ❌", foreground="#CF6679")
            self.model_combo.config(values=["Connection error"])
            self.model_combo.current(0)
            self._set_status("Could not connect to Ollama. Make sure the server is running.")

    def _set_status(self, text):
        """Update bottom status bar text."""
        self.status_bar.config(text=text)

    def _browse_file(self):
        """Open file browser dialog."""
        file_path = filedialog.askopenfilename(
            title="Select document to analyze",
            filetypes=[
                ("Supported files", "*.pdf *.docx *.txt *.md *.csv *.xlsx *.xls *.png *.jpg *.jpeg *.bmp *.gif *.webp *.py *.js *.html *.css *.java *.c *.cpp *.h *.cs *.go *.rs *.sh *.bat *.sql"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self._load_file(file_path)

    def _load_file(self, file_path):
        """Process file and extract text in a background thread."""
        self._set_status(f"Ingesting file: {os.path.basename(file_path)}...")
        self.drop_lbl.config(text=f"Selected: {os.path.basename(file_path)}")
        
        def bg_task():
            try:
                res = FileProcessor.extract_text(file_path)
                self.stream_queue.put(("file_loaded", res))
            except Exception as e:
                self.stream_queue.put(("error", f"Failed to read file:\n{str(e)}"))
                
        threading.Thread(target=bg_task, daemon=True).start()

    def _run_analysis(self, task):
        """Run summary, PII detection, or key info tasks in a background thread."""
        if not self.extracted_text.strip():
            messagebox.showwarning("Warning", "Please load a file with extractable text first.")
            return

        model = self.model_combo.get()
        if model in ["Connection error", "No models pulled!", ""]:
            messagebox.showerror("Error", "Please select a valid Ollama model. Ensure Ollama is running.")
            return

        self._set_status(f"Analyzing document using local model '{model}'...")
        self._toggle_buttons(state=tk.DISABLED)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "Thinking...")

        # Switch to action tab to show results
        self.notebook.select(self.tab_actions)

        def bg_task():
            def cb(chunk):
                self.stream_queue.put(("chunk", chunk))
            
            # Clear output placeholder
            self.stream_queue.put(("clear_output", None))
            self.ai.analyze_document(model, self.extracted_text, task, stream_callback=cb)
            self.stream_queue.put(("done", None))

        threading.Thread(target=bg_task, daemon=True).start()

    def _send_chat(self):
        """Send chat message to local AI with document context."""
        question = self.chat_input.get().strip()
        if not question:
            return

        if not self.extracted_text.strip():
            messagebox.showwarning("Warning", "Please load a file to talk about first.")
            return

        model = self.model_combo.get()
        if model in ["Connection error", "No models pulled!", ""]:
            messagebox.showerror("Error", "Please select a valid Ollama model.")
            return

        # Add user message to UI
        self._append_to_chat("user", question)
        self.chat_input.delete(0, tk.END)
        
        # Prepare assistant placeholder
        self._append_to_chat("assistant", "Thinking...")
        self.chat_history.append(("user", question))
        
        self._set_status(f"Chatting with local model '{model}'...")
        self._toggle_buttons(state=tk.DISABLED)

        def bg_task():
            def cb(chunk):
                self.stream_queue.put(("chat_chunk", chunk))
            
            # Clear assistant "Thinking..." text
            self.stream_queue.put(("clear_chat_last", None))
            response = self.ai.ask_question(model, self.extracted_text, question, self.chat_history, stream_callback=cb)
            self.chat_history.append(("assistant", response))
            self.stream_queue.put(("chat_done", None))

        threading.Thread(target=bg_task, daemon=True).start()

    def _append_to_chat(self, sender, text):
        """Insert a message into the chat display text box."""
        self.chat_view.config(state=tk.NORMAL)
        
        # Style formatting tags
        self.chat_view.tag_config("user", foreground=ACCENT_SECONDARY, font=("Segoe UI", 10, "bold"))
        self.chat_view.tag_config("assistant", foreground=ACCENT_PRIMARY, font=("Segoe UI", 10, "bold"))
        
        if sender == "user":
            self.chat_view.insert(tk.END, "👤 You:\n", "user")
        else:
            self.chat_view.insert(tk.END, "🤖 PrivateScan AI:\n", "assistant")
            
        self.chat_view.insert(tk.END, f"{text}\n\n")
        self.chat_view.config(state=tk.DISABLED)
        self.chat_view.see(tk.END)

    def _clear_chat(self):
        """Clear all chat history and history view."""
        self.chat_history.clear()
        self.chat_view.config(state=tk.NORMAL)
        self.chat_view.delete("1.0", tk.END)
        self.chat_view.config(state=tk.DISABLED)

    def _toggle_buttons(self, state):
        """Enable or disable all action buttons while AI runs."""
        self.btn_sum.config(state=state)
        self.btn_pii.config(state=state)
        self.btn_ext.config(state=state)
        self.btn_send.config(state=state)

    def _poll_queue(self):
        """Poll the thread safe queue for updates to display on UI."""
        try:
            while True:
                msg_type, data = self.stream_queue.get_nowait()
                
                if msg_type == "file_loaded":
                    res = data
                    self.current_file_path = res["metadata"]["path"]
                    self.extracted_text = res["text"]
                    
                    # Update preview
                    self.text_preview.delete("1.0", tk.END)
                    self.text_preview.insert(tk.END, self.extracted_text)
                    
                    # Update metadata labels
                    meta = res["metadata"]
                    kb_size = round(meta["size_bytes"] / 1024, 2)
                    self.meta_lbl.config(
                        text=f"📄 Name: {meta['name']}\n"
                             f"📂 Type: {meta['type']}\n"
                             f"⚖️ Size: {kb_size} KB\n"
                             f"📍 Path: {meta['path']}"
                    )
                    self._set_status(f"File loaded: {meta['name']}. Extracted {len(self.extracted_text)} characters.")
                    
                elif msg_type == "chunk":
                    # Stream chunk into the output text area
                    self.output_text.insert(tk.END, data)
                    self.output_text.see(tk.END)
                    
                elif msg_type == "clear_output":
                    self.output_text.delete("1.0", tk.END)
                    
                elif msg_type == "done":
                    self._toggle_buttons(state=tk.NORMAL)
                    self._set_status("Analysis completed.")
                    
                elif msg_type == "chat_chunk":
                    # Stream chunk into chat view
                    self.chat_view.config(state=tk.NORMAL)
                    self.chat_view.insert(tk.END, data)
                    self.chat_view.config(state=tk.DISABLED)
                    self.chat_view.see(tk.END)
                    
                elif msg_type == "clear_chat_last":
                    # Remove "Thinking..." message
                    self.chat_view.config(state=tk.NORMAL)
                    # We look back and delete from the end
                    # The "Thinking...\n\n" is 11 chars
                    end_idx = self.chat_view.index("end-1c")
                    start_idx = f"{end_idx} - 11 chars"
                    self.chat_view.delete(start_idx, tk.END)
                    self.chat_view.insert(tk.END, "\n") # Restore trailing newline
                    self.chat_view.config(state=tk.DISABLED)
                    
                elif msg_type == "chat_done":
                    self._toggle_buttons(state=tk.NORMAL)
                    self._set_status("Ready")
                    
                elif msg_type == "error":
                    self._toggle_buttons(state=tk.NORMAL)
                    messagebox.showerror("Error", data)
                    self._set_status("An error occurred.")
                    
        except queue.Empty:
            pass
        finally:
            # Poll again in 100ms
            self.after(100, self._poll_queue)
