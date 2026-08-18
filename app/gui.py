import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext

# ==================================================
# Color Palette (Modern Dark - Custom)
# ==================================================
COLORS = {
    "bg":          "#121212",  # Mat koyu gri (Ana arka plan)
    "surface":     "#18181b",  # Panel arka planı
    "surface_alt": "#1F2937",  # Kömür siyahı (Girdi ve paneller)
    "overlay":     "#374151",  # Çizgiler ve kenarlıklar
    "text":        "#E5E7EB",  # Açık gri (Ana metin)
    "subtext":     "#9CA3AF",  # İkincil metin
    "muted":       "#6B7280",  # Pasif/Silik metin
    "accent":      "#2563EB",  # Elektrik mavisi (Ana butonlar)
    "blue":        "#8B5CF6",  # Canlı mor (Senin mesajların)
    "green":       "#10B981",  # Zümrüt yeşili (AI mesajları/Başarı)
    "red":         "#EF4444",  # Yumuşak kırmızı (Hata/Silme)
    "warning":     "#F59E0B",  # Sarı/Turuncu (Uyarılar)
}

FONT = "Segoe UI"

class RAGGui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Local RAG AI Assistant")
        self.root.geometry("1100x700")
        self.root.minsize(900, 550)
        self.root.configure(bg=COLORS["bg"])

        self._loading_window = None
        self._loading_label = None
        self._source_counter = 0

        self._configure_styles()
        self.create_widgets()

    # ==================================================
    # TTK Styles
    # ==================================================
    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Accent Button (Send)
        style.configure(
            "Accent.TButton",
            background=COLORS["accent"],
            foreground="#F8F9FA",  # Kırık beyaz metin
            font=(FONT, 10, "bold"),
            borderwidth=0,
            focuscolor=COLORS["accent"],
            padding=(16, 8)
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#1D4ED8"), ("disabled", COLORS["overlay"])],
            foreground=[("disabled", COLORS["muted"])]
        )

        # Secondary Button
        style.configure(
            "Secondary.TButton",
            background=COLORS["surface_alt"],
            foreground=COLORS["text"],
            font=(FONT, 10),
            borderwidth=0,
            focuscolor=COLORS["surface_alt"],
            padding=(16, 8)
        )
        style.map(
            "Secondary.TButton",
            background=[("active", COLORS["overlay"]), ("disabled", COLORS["surface"])],
            foreground=[("disabled", COLORS["muted"])]
        )

        # Danger Button (Remove)
        style.configure(
            "Danger.TButton",
            background=COLORS["surface_alt"],
            foreground=COLORS["red"],
            font=(FONT, 10),
            borderwidth=0,
            focuscolor=COLORS["surface_alt"],
            padding=(16, 8)
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#DC2626"), ("disabled", COLORS["overlay"])],
            foreground=[("active", "#F8F9FA"), ("disabled", COLORS["muted"])]
        )

        # Progress Bar
        style.configure(
            "Accent.Horizontal.TProgressbar",
            background=COLORS["accent"],
            troughcolor=COLORS["surface_alt"],
            borderwidth=0,
            thickness=4
        )

    # ==================================================
    # GUI Layout
    # ==================================================
    def create_widgets(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # ------------------------------------------------
        # Top Header Bar
        # ------------------------------------------------
        header_frame = tk.Frame(self.root, bg=COLORS["surface"], height=60)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)

        self.title_label = tk.Label(
            header_frame,
            text="AI Assistant",
            font=("Cascadia Code", 18, "normal"),
            fg=COLORS["text"],
            bg=COLORS["surface"]
        )
        self.title_label.pack(side="left", padx=24, pady=15)

        # ------------------------------------------------
        # Content Area (Chat + Document Panel)
        # ------------------------------------------------
        content_frame = tk.Frame(self.root, bg=COLORS["bg"])
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # ---- Chat ----
        self.chat_text = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            font=(FONT, 10),
            state="disabled",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            selectbackground=COLORS["accent"],
            selectforeground="#F8F9FA",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10,
            spacing1=6,
            spacing2=3,
            spacing3=7
        )
        self.chat_text.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # ---- Document Panel (Sidebar) ----
        doc_panel = tk.Frame(
            content_frame,
            bg=COLORS["surface"],
            width=280,
            highlightbackground=COLORS["overlay"],
            highlightthickness=1
        )
        doc_panel.grid(row=0, column=1, sticky="ns")
        doc_panel.grid_propagate(False)
        doc_panel.config(width=280)
        doc_panel.grid_rowconfigure(2, weight=1)
        doc_panel.grid_columnconfigure(0, weight=1)

        doc_title = tk.Label(
            doc_panel,
            text="Knowledge Base",
            font=(FONT, 12, "bold"),
            fg=COLORS["text"],
            bg=COLORS["surface"],
            anchor="w"
        )
        doc_title.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 4))

        doc_formats = tk.Label(
            doc_panel,
            text="Supported: PDF, TXT, DOCX, MD",
            font=(FONT, 8),
            fg=COLORS["subtext"],
            bg=COLORS["surface"],
            anchor="w"
        )
        doc_formats.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))

        self.doc_listbox = tk.Listbox(
            doc_panel,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            font=(FONT, 10),
            selectbackground=COLORS["overlay"],
            selectforeground=COLORS["text"],
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            activestyle="none"
        )
        self.doc_listbox.grid(row=2, column=0, sticky="nsew", padx=20, pady=0)

        doc_btn_frame = tk.Frame(doc_panel, bg=COLORS["surface"])
        doc_btn_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=20)
        doc_btn_frame.grid_columnconfigure(0, weight=1)
        doc_btn_frame.grid_columnconfigure(1, weight=1)

        self.add_button = ttk.Button(doc_btn_frame, text="Add File", style="Secondary.TButton")
        self.add_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.remove_doc_button = ttk.Button(doc_btn_frame, text="Remove", style="Danger.TButton")
        self.remove_doc_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # ------------------------------------------------
        # Bottom Frame (Input Area)
        # ------------------------------------------------
        bottom_frame = tk.Frame(self.root, bg=COLORS["surface"])
        bottom_frame.grid(row=2, column=0, sticky="ew")
        bottom_frame.grid_columnconfigure(0, weight=1)

        input_container = tk.Frame(bottom_frame, bg=COLORS["surface"])
        input_container.grid(row=0, column=0, sticky="ew", padx=24, pady=20)
        input_container.grid_columnconfigure(0, weight=1)

        # Entry Row
        entry_frame = tk.Frame(
            input_container, 
            bg=COLORS["surface_alt"], 
            highlightbackground=COLORS["overlay"], 
            highlightthickness=1
        )
        entry_frame.grid(row=0, column=0, sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)

        self.question_entry = tk.Entry(
            entry_frame,
            font=(FONT, 11),
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            borderwidth=0,
            disabledbackground=COLORS["surface_alt"],
            disabledforeground=COLORS["muted"]
        )
        self.question_entry.grid(row=0, column=0, sticky="ew", padx=15, ipady=12)

        self.send_button = ttk.Button(entry_frame, text="Send", style="Accent.TButton")
        self.send_button.grid(row=0, column=1, padx=4, pady=4)

        # Toolbar Row
        toolbar_frame = tk.Frame(input_container, bg=COLORS["surface"])
        toolbar_frame.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        toolbar_frame.grid_columnconfigure(1, weight=1)

        self.clear_button = tk.Button(
            toolbar_frame,
            text="Clear Chat",
            font=(FONT, 9),
            fg=COLORS["subtext"],
            bg=COLORS["surface"],
            activebackground=COLORS["surface"],
            activeforeground=COLORS["text"],
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            command=self.clear_chat
        )
        self.clear_button.grid(row=0, column=0, sticky="w")

        self.status_label = tk.Label(
            toolbar_frame,
            text="System ready",
            font=(FONT, 9),
            fg=COLORS["muted"],
            bg=COLORS["surface"],
            anchor="e"
        )
        self.status_label.grid(row=0, column=1, sticky="e")

        self.configure_tags()

    # ==================================================
    # Chat
    # ==================================================
    def add_message(self, sender, message, sources=None):
        def update():
            self.chat_text.configure(state="normal")
            tag = "assistant"
            
            if sender.lower() == "you":
                tag = "you"

            self.chat_text.insert(tk.END, f"{sender}\n", tag)
            self.chat_text.insert(tk.END, f"{message}\n")

            if sources:
                self._insert_collapsible_source(sources)

            self.chat_text.insert(tk.END, "\n")
            self.chat_text.configure(state="disabled")
            self.chat_text.see(tk.END)

        self.root.after(0, update)

    def _insert_collapsible_source(self, sources):
        self._source_counter += 1
        sid = self._source_counter

        header_tag = f"src_header_{sid}"
        detail_tag = f"src_detail_{sid}"
        source_text = ", ".join(sources)

        self.chat_text.insert(tk.END, "▶ View Sources\n", header_tag)
        detail_start = self.chat_text.index(tk.END)
        self.chat_text.insert(tk.END, f"  {source_text}\n", detail_tag)

        self.chat_text.tag_configure(
            header_tag,
            foreground=COLORS["subtext"],
            font=(FONT, 9, "bold"),
        )
        
        self.chat_text.tag_configure(
            detail_tag,
            foreground=COLORS["muted"],
            font=(FONT, 9),
            elide=True
        )

        def toggle(event, h=header_tag, d=detail_tag):
            current = self.chat_text.tag_cget(d, "elide")
            if current == "1" or current == "true" or current is True:
                self.chat_text.tag_configure(d, elide=False)
                h_ranges = self.chat_text.tag_ranges(h)
                if h_ranges:
                    self.chat_text.configure(state="normal")
                    self.chat_text.delete(h_ranges[0], h_ranges[1])
                    self.chat_text.insert(h_ranges[0], "▼ Hide Sources\n", h)
                    self.chat_text.configure(state="disabled")
            else:
                self.chat_text.tag_configure(d, elide=True)
                h_ranges = self.chat_text.tag_ranges(h)
                if h_ranges:
                    self.chat_text.configure(state="normal")
                    self.chat_text.delete(h_ranges[0], h_ranges[1])
                    self.chat_text.insert(h_ranges[0], "▶ View Sources\n", h)
                    self.chat_text.configure(state="disabled")

        self.chat_text.tag_bind(header_tag, "<Button-1>", toggle)

    # ==================================================
    # Status
    # ==================================================
    def set_status(self, text):
        self.root.after(
            0,
            lambda: self.status_label.config(text=f"{text}")
        )

    # ==================================================
    # Entry
    # ==================================================
    def get_question(self):
        return self.question_entry.get().strip()

    def clear_question(self):
        self.question_entry.delete(0, tk.END)

    # ==================================================
    # Input Control
    # ==================================================
    def enable_input(self):
        self.question_entry.configure(state="normal")
        self.send_button.configure(state="normal")
        self.add_button.configure(state="normal")
        self.focus_input()

    def disable_input(self):
        self.question_entry.configure(state="disabled")
        self.send_button.configure(state="disabled")
        self.add_button.configure(state="disabled")

    # ==================================================
    # Clear Chat
    # ==================================================
    def clear_chat(self):
        self.chat_text.configure(state="normal")
        self.chat_text.delete("1.0", tk.END)
        self.chat_text.configure(state="disabled")

    # ==================================================
    # File Dialog
    # ==================================================
    def ask_file(self):
        return filedialog.askopenfilename(
            title="Select Document",
            filetypes=[
            (
                "Supported Documents",
                "*.txt *.pdf *.docx *.md *.markdown *.html *.htm *.pptx"
            ),
            ("All Files", "*.*")
            ]
        )

    # ==================================================
    # Focus
    # ==================================================
    def focus_input(self):
        self.question_entry.focus_set()

    # ==================================================
    # Tags
    # ==================================================
    def configure_tags(self):
        self.chat_text.tag_configure(
            "assistant",
            foreground=COLORS["green"],
            font=(FONT, 10, "bold")
        )
        self.chat_text.tag_configure(
            "you",
            foreground=COLORS["blue"],
            font=(FONT, 10, "bold")
        )
        self.chat_text.tag_configure(
            "source",
            foreground=COLORS["muted"],
            font=(FONT, 9)
        )

    # ==================================================
    # Document Panel
    # ==================================================
    def refresh_documents(self, sources):
        def update():
            self.doc_listbox.delete(0, tk.END)
            for source in sorted(sources):
                self.doc_listbox.insert(tk.END, f"  {source}")

        self.root.after(0, update)

    def get_selected_document(self):
        selection = self.doc_listbox.curselection()
        if not selection:
            return None
        return self.doc_listbox.get(selection[0]).strip()

    # ==================================================
    # Loading Dialog
    # ==================================================
    def show_loading(self, title, message):
        def create():
            if self._loading_window is not None:
                return

            win = tk.Toplevel(self.root)
            win.title(title)
            win.geometry("400x140")
            win.resizable(False, False)
            win.configure(bg=COLORS["surface"])
            win.transient(self.root)

            self.root.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
            y = self.root.winfo_y() + (self.root.winfo_height() - 140) // 2
            win.geometry(f"+{x}+{y}")
            win.protocol("WM_DELETE_WINDOW", lambda: None)

            self._loading_label = tk.Label(
                win,
                text=message,
                font=(FONT, 10),
                fg=COLORS["text"],
                bg=COLORS["surface"],
                anchor="center"
            )
            self._loading_label.pack(padx=24, pady=(32, 16), fill="x")

            progress = ttk.Progressbar(
                win,
                mode="indeterminate",
                style="Accent.Horizontal.TProgressbar"
            )
            progress.pack(padx=40, pady=(0, 32), fill="x")
            progress.start(15)

            self._loading_window = win

        self.root.after(0, create)

    def update_loading(self, message):
        def update():
            if self._loading_label is not None:
                self._loading_label.config(text=message)
        self.root.after(0, update)

    def close_loading(self):
        def close():
            if self._loading_window is not None:
                self._loading_window.destroy()
                self._loading_window = None
                self._loading_label = None
        self.root.after(0, close)

    # ==================================================
    # Startup
    # ==================================================
    def initialize(self):
        self.disable_input()
        self.set_status("Initializing system...")

    # ==================================================
    # Ready
    # ==================================================
    def ready(self):
        self.enable_input()
        self.set_status("Ready")

    # ==================================================
    # Mainloop
    # ==================================================
    def run(self):
        self.initialize()
        self.root.mainloop()