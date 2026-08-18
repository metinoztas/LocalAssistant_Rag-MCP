import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext


# ==================================================
# Color Palette (Catppuccin Mocha)
# ==================================================

COLORS = {
    "bg":          "#1e1e2e",
    "surface":     "#181825",
    "surface_alt": "#313244",
    "overlay":     "#45475a",
    "text":        "#cdd6f4",
    "subtext":     "#a6adc8",
    "muted":       "#6c7086",
    "accent":      "#cba6f7",
    "blue":        "#89b4fa",
    "green":       "#a6e3a1",
    "red":         "#f38ba8",
}

FONT = "Segoe UI"


class RAGGui:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title("Local RAG AI Assistant")

        self.root.geometry("1050x650")

        self.root.minsize(850, 500)

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
            foreground=COLORS["bg"],
            font=(FONT, 9, "bold"),
            borderwidth=0,
            padding=(14, 7)
        )

        style.map(
            "Accent.TButton",
            background=[
                ("active", "#b48ef0"),
                ("disabled", COLORS["overlay"])
            ],
            foreground=[
                ("disabled", COLORS["muted"])
            ]
        )

        # Secondary Button
        style.configure(
            "Secondary.TButton",
            background=COLORS["surface_alt"],
            foreground=COLORS["text"],
            font=(FONT, 9),
            borderwidth=0,
            padding=(14, 7)
        )

        style.map(
            "Secondary.TButton",
            background=[
                ("active", COLORS["overlay"]),
                ("disabled", COLORS["surface"])
            ],
            foreground=[
                ("disabled", COLORS["muted"])
            ]
        )

        # Danger Button (Remove)
        style.configure(
            "Danger.TButton",
            background=COLORS["red"],
            foreground=COLORS["bg"],
            font=(FONT, 9),
            borderwidth=0,
            padding=(14, 7)
        )

        style.map(
            "Danger.TButton",
            background=[
                ("active", "#e06080"),
                ("disabled", COLORS["overlay"])
            ]
        )

        # Progress Bar
        style.configure(
            "Accent.Horizontal.TProgressbar",
            background=COLORS["accent"],
            troughcolor=COLORS["surface_alt"],
            borderwidth=0
        )

    # ==================================================
    # GUI Layout
    # ==================================================

    def create_widgets(self):

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # ------------------------------------------------
        # Title
        # ------------------------------------------------

        title_frame = tk.Frame(
            self.root,
            bg=COLORS["bg"]
        )

        title_frame.grid(
            row=0, column=0,
            sticky="ew",
            padx=16, pady=(14, 0)
        )

        self.title_label = tk.Label(
            title_frame,
            text="Local RAG AI Assistant",
            font=(FONT, 17, "bold"),
            fg=COLORS["accent"],
            bg=COLORS["bg"]
        )

        self.title_label.pack(side="left")

        # ------------------------------------------------
        # Content Area (Chat + Document Panel)
        # ------------------------------------------------

        content_frame = tk.Frame(
            self.root,
            bg=COLORS["bg"]
        )

        content_frame.grid(
            row=1, column=0,
            sticky="nsew",
            padx=16, pady=8
        )

        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # ---- Chat ----

        self.chat_text = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            font=(FONT, 10),
            state="disabled",
            bg=COLORS["surface"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            selectbackground=COLORS["accent"],
            selectforeground=COLORS["bg"],
            relief="flat",
            borderwidth=0,
            padx=14,
            pady=12
        )

        self.chat_text.grid(
            row=0, column=0,
            sticky="nsew",
            padx=(0, 8)
        )

        # ---- Document Panel ----

        doc_panel = tk.Frame(
            content_frame,
            bg=COLORS["surface"],
            width=230
        )

        doc_panel.grid(
            row=0, column=1,
            sticky="ns"
        )

        doc_panel.grid_propagate(False)
        doc_panel.config(width=230)
        doc_panel.grid_rowconfigure(2, weight=1)
        doc_panel.grid_columnconfigure(0, weight=1)

        doc_title = tk.Label(
            doc_panel,
            text="Documents",
            font=(FONT, 11, "bold"),
            fg=COLORS["text"],
            bg=COLORS["surface"],
            anchor="w"
        )

        doc_title.grid(
            row=0, column=0,
            sticky="ew",
            padx=10, pady=(12, 0)
        )

        doc_formats = tk.Label(
            doc_panel,
            text="txt  pdf  docx  md  html  pptx",
            font=(FONT, 7),
            fg=COLORS["muted"],
            bg=COLORS["surface"],
            anchor="w"
        )

        doc_formats.grid(
            row=1, column=0,
            sticky="ew",
            padx=10, pady=(0, 6)
        )

        self.doc_listbox = tk.Listbox(
            doc_panel,
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            font=(FONT, 9),
            selectbackground=COLORS["accent"],
            selectforeground=COLORS["bg"],
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            activestyle="none"
        )

        self.doc_listbox.grid(
            row=2, column=0,
            sticky="nsew",
            padx=10, pady=4
        )

        doc_btn_frame = tk.Frame(
            doc_panel,
            bg=COLORS["surface"]
        )

        doc_btn_frame.grid(
            row=3, column=0,
            sticky="ew",
            padx=10, pady=(4, 12)
        )

        doc_btn_frame.grid_columnconfigure(0, weight=1)
        doc_btn_frame.grid_columnconfigure(1, weight=1)

        self.add_button = ttk.Button(
            doc_btn_frame,
            text="Add",
            style="Secondary.TButton"
        )

        self.add_button.grid(
            row=0, column=0,
            sticky="ew",
            padx=(0, 3)
        )

        self.remove_doc_button = ttk.Button(
            doc_btn_frame,
            text="Remove",
            style="Danger.TButton"
        )

        self.remove_doc_button.grid(
            row=0, column=1,
            sticky="ew",
            padx=(3, 0)
        )

        # ------------------------------------------------
        # Bottom Frame
        # ------------------------------------------------

        bottom_frame = tk.Frame(
            self.root,
            bg=COLORS["bg"]
        )

        bottom_frame.grid(
            row=2, column=0,
            sticky="ew",
            padx=16, pady=(0, 14)
        )

        bottom_frame.grid_columnconfigure(0, weight=1)

        # Entry Row

        entry_frame = tk.Frame(
            bottom_frame,
            bg=COLORS["bg"]
        )

        entry_frame.grid(
            row=0, column=0,
            sticky="ew"
        )

        entry_frame.grid_columnconfigure(0, weight=1)

        self.question_entry = tk.Entry(
            entry_frame,
            font=(FONT, 11),
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            borderwidth=0,
            disabledbackground=COLORS["surface"],
            disabledforeground=COLORS["muted"]
        )

        self.question_entry.grid(
            row=0, column=0,
            sticky="ew",
            padx=(0, 6),
            ipady=8
        )

        self.send_button = ttk.Button(
            entry_frame,
            text="Send",
            style="Accent.TButton"
        )

        self.send_button.grid(
            row=0, column=1
        )

        # Button Row

        btn_frame = tk.Frame(
            bottom_frame,
            bg=COLORS["bg"]
        )

        btn_frame.grid(
            row=1, column=0,
            sticky="w",
            pady=(8, 0)
        )

        self.clear_button = ttk.Button(
            btn_frame,
            text="Clear Chat",
            style="Secondary.TButton"
        )

        self.clear_button.pack(side="left")

        # Status

        self.status_label = tk.Label(
            bottom_frame,
            text="Status : Starting...",
            font=(FONT, 9),
            fg=COLORS["muted"],
            bg=COLORS["bg"],
            anchor="w"
        )

        self.status_label.grid(
            row=2, column=0,
            sticky="ew",
            pady=(8, 0)
        )

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

            self.chat_text.insert(
                tk.END,
                f"{sender}\n",
                tag
            )

            self.chat_text.insert(
                tk.END,
                f"{message}\n"
            )

            if sources:
                self._insert_collapsible_source(sources)

            self.chat_text.insert(tk.END, "\n")

            self.chat_text.configure(state="disabled")

            self.chat_text.see(tk.END)

        self.root.after(0, update)

    def _insert_collapsible_source(self, sources):
        """
        Tıklanabilir açılır/kapanır kaynak bilgisi ekler.
        """

        self._source_counter += 1
        sid = self._source_counter

        header_tag = f"src_header_{sid}"
        detail_tag = f"src_detail_{sid}"

        source_text = ", ".join(sources)

        # Header: tıklanabilir "▶ Source"
        self.chat_text.insert(
            tk.END,
            "▶ Source\n",
            header_tag
        )

        # Detail: gizli kaynak bilgisi
        detail_start = self.chat_text.index(tk.END)
        self.chat_text.insert(
            tk.END,
            f"  {source_text}\n",
            detail_tag
        )

        # Header stilini ayarla
        self.chat_text.tag_configure(
            header_tag,
            foreground=COLORS["muted"],
            font=(FONT, 8, "italic"),
            

        )

        # Detail stilini ayarla ve gizle
        self.chat_text.tag_configure(
            detail_tag,
            foreground=COLORS["muted"],
            font=(FONT, 9, "italic"),
            elide=True
        )

        # Tıklama olayı
        def toggle(event, h=header_tag, d=detail_tag):
            current = self.chat_text.tag_cget(d, "elide")
            if current == "1" or current == "true" or current is True:
                self.chat_text.tag_configure(d, elide=False)
                # Header metnini güncelle
                h_ranges = self.chat_text.tag_ranges(h)
                if h_ranges:
                    self.chat_text.configure(state="normal")
                    self.chat_text.delete(h_ranges[0], h_ranges[1])
                    self.chat_text.insert(h_ranges[0], "▼ Source\n", h)
                    self.chat_text.configure(state="disabled")
            else:
                self.chat_text.tag_configure(d, elide=True)
                h_ranges = self.chat_text.tag_ranges(h)
                if h_ranges:
                    self.chat_text.configure(state="normal")
                    self.chat_text.delete(h_ranges[0], h_ranges[1])
                    self.chat_text.insert(h_ranges[0], "▶ Source\n", h)
                    self.chat_text.configure(state="disabled")

        self.chat_text.tag_bind(header_tag, "<Button-1>", toggle)

    # ==================================================
    # Status
    # ==================================================

    def set_status(self, text):

        self.root.after(
            0,
            lambda: self.status_label.config(
                text=f"Status : {text}"
            )
        )

    # ==================================================
    # Entry
    # ==================================================

    def get_question(self):

        return self.question_entry.get().strip()

    def clear_question(self):

        self.question_entry.delete(
            0,
            tk.END
        )

    # ==================================================
    # Input Control
    # ==================================================

    def enable_input(self):

        self.question_entry.configure(
            state="normal"
        )

        self.send_button.configure(
            state="normal"
        )

        self.add_button.configure(
            state="normal"
        )

        self.focus_input()

    def disable_input(self):

        self.question_entry.configure(
            state="disabled"
        )

        self.send_button.configure(
            state="disabled"
        )

        self.add_button.configure(
            state="disabled"
        )

    # ==================================================
    # Clear Chat
    # ==================================================

    def clear_chat(self):

        self.chat_text.configure(
            state="normal"
        )

        self.chat_text.delete(
            "1.0",
            tk.END
        )

        self.chat_text.configure(
            state="disabled"
        )

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
            font=(FONT, 9, "italic")
        )

    # ==================================================
    # Document Panel
    # ==================================================

    def refresh_documents(self, sources):
        """
        Belge panelindeki listeyi günceller.
        """

        def update():
            self.doc_listbox.delete(0, tk.END)
            for source in sorted(sources):
                self.doc_listbox.insert(tk.END, source)

        self.root.after(0, update)

    def get_selected_document(self):
        """
        Seçili belge adını döndürür.
        """

        selection = self.doc_listbox.curselection()

        if not selection:
            return None

        return self.doc_listbox.get(selection[0])

    # ==================================================
    # Loading Dialog
    # ==================================================

    def show_loading(self, title, message):
        """
        Yükleme diyaloğu gösterir.
        """

        def create():

            if self._loading_window is not None:
                return

            win = tk.Toplevel(self.root)
            win.title(title)
            win.geometry("380x130")
            win.resizable(False, False)
            win.configure(bg=COLORS["bg"])
            win.transient(self.root)

            # Ana pencereye göre ortala
            self.root.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() - 380) // 2
            y = self.root.winfo_y() + (self.root.winfo_height() - 130) // 2
            win.geometry(f"+{x}+{y}")

            win.protocol("WM_DELETE_WINDOW", lambda: None)

            self._loading_label = tk.Label(
                win,
                text=message,
                font=(FONT, 10),
                fg=COLORS["text"],
                bg=COLORS["bg"],
                anchor="w"
            )

            self._loading_label.pack(
                padx=24, pady=(24, 12),
                fill="x"
            )

            progress = ttk.Progressbar(
                win,
                mode="indeterminate",
                style="Accent.Horizontal.TProgressbar"
            )

            progress.pack(
                padx=24, pady=(0, 24),
                fill="x"
            )

            progress.start(15)

            self._loading_window = win

        self.root.after(0, create)

    def update_loading(self, message):
        """
        Yükleme mesajını günceller.
        """

        def update():
            if self._loading_label is not None:
                self._loading_label.config(text=message)

        self.root.after(0, update)

    def close_loading(self):
        """
        Yükleme diyaloğunu kapatır.
        """

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

        self.set_status(
            "Loading..."
        )

    # ==================================================
    # Ready
    # ==================================================

    def ready(self):

        self.enable_input()

        self.set_status(
            "Ready"
        )

    # ==================================================
    # Mainloop
    # ==================================================

    def run(self):

        self.initialize()

        self.root.mainloop()