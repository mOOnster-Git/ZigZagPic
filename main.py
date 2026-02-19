import os
import sys
import shutil
import datetime
import webbrowser
import tkinter as tk
import ctypes
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

# --- Modern Dark Theme Colors ---
COLOR_BG = "#2D2D30"         # Main Window Background (Dark Gray)
COLOR_TITLE_BAR = "#2D2D30"  # Title Bar Background
COLOR_FG = "#FFFFFF"         # Main Text Color (White)
COLOR_ACCENT = "#007ACC"     # Accent Color (Blue) - Start Button
COLOR_INPUT_BG = "#3E3E42"   # Input Field Background
COLOR_INPUT_FG = "#FFFFFF"   # Input Field Text
COLOR_HOVER = "#3E3E42"      # Button Hover Background
COLOR_DANGER = "#E81123"     # Close Button Hover (Red)
COLOR_BORDER = "#434346"     # Border Color
COLOR_WARNING = "#FFAA00"    # Warning Text Color (Orange)
COLOR_FOOTER = "#1E1E1E"     # Footer Background

class InterleaverApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.version = "v2.2.4"
        self.root.title("ZigZag Pic") # Requested Form.Text
        self.root.configure(bg=COLOR_BG)
        
        # Remove native title bar
        self.root.overrideredirect(True)
        
        # Initial geometry
        self.width = 750
        self.height = 800
        self._center_window()

        # Fonts
        self.font_title = ("Segoe UI", 10, "bold")
        self.font_header = ("Malgun Gothic", 14, "bold")
        self.font_base = ("Malgun Gothic", 10)
        self.font_bold = ("Malgun Gothic", 10, "bold")
        self.font_small = ("Malgun Gothic", 9)
        self.font_mono = ("Consolas", 10)

        # State
        self.folder_rows = []
        self.row_counter = 0
        self.auto_open_var = tk.BooleanVar(value=True)
        self._drag_data = {"x": 0, "y": 0}
        self.is_maximized = False
        self.pre_maximize_geom = f"{self.width}x{self.height}"
        
        # Mode State
        self.is_preview_mode = True

        # Build UI
        self._build_custom_title_bar()
        self._build_main_ui()
        
        # Initialize with 2 rows
        self._add_folder_row()
        self._add_folder_row()
        
        # Show in taskbar
        self.root.after(10, self._set_app_window)

    def _set_app_window(self):
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        self.root.wm_withdraw()
        self.root.after(10, self.root.wm_deiconify)

    def _center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")

    def _build_custom_title_bar(self):
        """Custom Title Bar Implementation"""
        self.title_bar = tk.Frame(self.root, bg=COLOR_TITLE_BAR, height=35, relief="flat")
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)

        # Title Label (Left)
        title_lbl = tk.Label(
            self.title_bar, 
            text="ZigZag Pic - 지그재그 사진 정리", 
            fg=COLOR_FG, 
            bg=COLOR_TITLE_BAR, 
            font=self.font_title
        )
        title_lbl.pack(side="left", padx=10)

        # Dragging Events
        self.title_bar.bind("<Button-1>", self._start_move)
        self.title_bar.bind("<B1-Motion>", self._do_move)
        title_lbl.bind("<Button-1>", self._start_move)
        title_lbl.bind("<B1-Motion>", self._do_move)

        # Window Controls (Right)
        btn_config = {
            "bg": COLOR_TITLE_BAR, "fg": COLOR_FG, 
            "bd": 0, "relief": "flat", 
            "font": ("Marlett", 10), "width": 4, "height": 2
        }

        # Close Button [X]
        self.btn_close = tk.Button(self.title_bar, text="r", command=self.root.quit, **btn_config) # Marlett 'r' is X
        self.btn_close.pack(side="right")
        self.btn_close.bind("<Enter>", lambda e: self.btn_close.config(bg=COLOR_DANGER))
        self.btn_close.bind("<Leave>", lambda e: self.btn_close.config(bg=COLOR_TITLE_BAR))

        # Maximize Button [□]
        self.btn_max = tk.Button(self.title_bar, text="1", command=self._toggle_maximize, **btn_config) # Marlett '1' is Maximize
        self.btn_max.pack(side="right")
        self.btn_max.bind("<Enter>", lambda e: self.btn_max.config(bg=COLOR_HOVER))
        self.btn_max.bind("<Leave>", lambda e: self.btn_max.config(bg=COLOR_TITLE_BAR))

        # Minimize Button [_]
        self.btn_min = tk.Button(self.title_bar, text="0", command=self._minimize_window, **btn_config) # Marlett '0' is Minimize
        self.btn_min.pack(side="right")
        self.btn_min.bind("<Enter>", lambda e: self.btn_min.config(bg=COLOR_HOVER))
        self.btn_min.bind("<Leave>", lambda e: self.btn_min.config(bg=COLOR_TITLE_BAR))

    def _start_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _do_move(self, event):
        if not self.is_maximized:
            dx = event.x - self._drag_data["x"]
            dy = event.y - self._drag_data["y"]
            x = self.root.winfo_x() + dx
            y = self.root.winfo_y() + dy
            self.root.geometry(f"+{x}+{y}")

    def _toggle_maximize(self):
        if self.is_maximized:
            self.root.geometry(self.pre_maximize_geom)
            self.is_maximized = False
            self.btn_max.config(text="1") # Maximize icon
        else:
            self.pre_maximize_geom = self.root.geometry()
            # Windows maximize workaround for overrideredirect
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            self.is_maximized = True
            self.btn_max.config(text="2") # Restore icon

    def _minimize_window(self):
        # Minimize hack for overrideredirect
        self.root.update_idletasks()
        self.root.overrideredirect(False)
        self.root.iconify()
        self.root.after(10, lambda: self.root.overrideredirect(True))

    def _build_main_ui(self):
        main_frame = tk.Frame(self.root, bg=COLOR_BG, padx=20, pady=10)
        main_frame.pack(fill="both", expand=True)

        # Header
        header_lbl = tk.Label(
            main_frame, 
            text="졸업/이벤트 영상 필수품! 친구들 사진을 공평하게 섞어드려요", 
            fg=COLOR_ACCENT, 
            bg=COLOR_BG, 
            font=self.font_header
        )
        header_lbl.pack(pady=(10, 20))

        # Settings Section (Scrollable)
        self._build_settings_section(main_frame)

        # Run Section
        self._build_run_section(main_frame)

        # Progress Section
        self._build_progress_section(main_frame)

        # Footer
        self._build_footer(main_frame)

    def _build_settings_section(self, parent):
        # Container
        container = tk.Frame(parent, bg=COLOR_BG)
        container.pack(fill="both", expand=True, pady=(0, 10))

        # Header Row
        tk.Label(container, text="📂 폴더 목록", font=self.font_bold, bg=COLOR_BG, fg=COLOR_FG).pack(anchor="w")

        # Scrollable Canvas
        canvas_frame = tk.Frame(container, bg=COLOR_BG, bd=1, relief="solid") # Border for list area
        canvas_frame.pack(fill="both", expand=True, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg=COLOR_BG, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(
            canvas_frame, orient="vertical", command=self.canvas.yview,
            width=5, bg=COLOR_BG, troughcolor=COLOR_BG, activebackground=COLOR_ACCENT, bd=0
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLOR_BG)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        # Scrollbar will be packed when needed

        # Add Button Area
        btn_frame = tk.Frame(container, bg=COLOR_BG, pady=5)
        btn_frame.pack(fill="x")
        
        self.btn_add = tk.Button(
            btn_frame, text="+ 폴더 추가", bg=COLOR_INPUT_BG, fg=COLOR_FG,
            font=self.font_base, relief="flat", padx=15, pady=5,
            command=self._add_folder_row
        )
        self.btn_add.pack(side="left")
        self._bind_hover(self.btn_add)

        # Path Info & Option
        info_frame = tk.Frame(container, bg=COLOR_BG, pady=5)
        info_frame.pack(fill="x")
        
        tk.Label(info_frame, text="📍 저장 위치: 바탕화면 (자동 생성)", fg="#AAAAAA", bg=COLOR_BG, font=self.font_small).pack(side="left")
        
        # Custom Checkbox (using checkbutton with styled colors)
        cb = tk.Checkbutton(
            info_frame, text="완료 후 폴더 열기", variable=self.auto_open_var,
            bg=COLOR_BG, fg=COLOR_FG, selectcolor=COLOR_INPUT_BG, activebackground=COLOR_BG, activeforeground=COLOR_FG,
            font=self.font_small
        )
        cb.pack(side="right")

    def _add_folder_row(self):
        row_id = self.row_counter
        self.row_counter += 1

        row_frame = tk.Frame(self.scrollable_frame, bg=COLOR_BG, pady=5)
        row_frame.pack(fill="x", padx=5)

        # Index Label
        idx_lbl = tk.Label(row_frame, text=f"#{len(self.folder_rows)+1}", bg=COLOR_BG, fg=COLOR_ACCENT, font=self.font_bold, width=3)
        idx_lbl.pack(side="left")

        # Path Entry
        path_var = tk.StringVar()
        path_var.trace_add("write", lambda *args: self._reset_to_preview())
        path_entry = tk.Entry(row_frame, textvariable=path_var, bg=COLOR_INPUT_BG, fg=COLOR_INPUT_FG, font=self.font_base, relief="flat", insertbackground=COLOR_FG)
        path_entry.pack(side="left", fill="x", expand=True, padx=5, ipady=4)

        # Browse Button
        btn_browse = tk.Button(
            row_frame, text="...", bg=COLOR_INPUT_BG, fg=COLOR_FG,
            font=self.font_bold, relief="flat", width=4,
            command=lambda: self._browse_folder(path_var)
        )
        btn_browse.pack(side="left", padx=2)
        self._bind_hover(btn_browse)

        # Prefix
        tk.Label(row_frame, text="접두사:", bg=COLOR_BG, fg="#AAAAAA", font=self.font_small).pack(side="left", padx=(10, 2))
        name_var = tk.StringVar()
        name_var.trace_add("write", lambda *args: self._reset_to_preview())
        name_entry = tk.Entry(row_frame, textvariable=name_var, bg=COLOR_INPUT_BG, fg=COLOR_INPUT_FG, font=self.font_base, width=10, relief="flat", insertbackground=COLOR_FG)
        name_entry.pack(side="left", padx=2, ipady=4)

        # Remove Button
        btn_remove = tk.Button(
            row_frame, text="X", bg=COLOR_BG, fg=COLOR_DANGER,
            font=self.font_bold, relief="flat", width=3,
            command=lambda: self._remove_folder_row(row_id)
        )
        btn_remove.pack(side="left", padx=2)
        btn_remove.bind("<Enter>", lambda e: btn_remove.config(bg=COLOR_DANGER, fg="white"))
        btn_remove.bind("<Leave>", lambda e: btn_remove.config(bg=COLOR_BG, fg=COLOR_DANGER))

        self.folder_rows.append({
            'id': row_id, 'frame': row_frame, 'path_var': path_var, 'name_var': name_var, 'label': idx_lbl
        })
        self._update_row_labels()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._reset_to_preview()
        self._toggle_scrollbar()
        
        # Auto-scroll to bottom
        if len(self.folder_rows) > 7:
            self.root.update_idletasks()
            self.canvas.yview_moveto(1.0)

    def _remove_folder_row(self, row_id):
        for row in self.folder_rows:
            if row['id'] == row_id:
                row['frame'].destroy()
                self.folder_rows.remove(row)
                break
        self._update_row_labels()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._reset_to_preview()
        self._toggle_scrollbar()

    def _toggle_scrollbar(self):
        if len(self.folder_rows) > 7:
            self.scrollbar.pack(side="right", fill="y")
        else:
            self.scrollbar.pack_forget()

    def _reset_to_preview(self):
        if hasattr(self, 'btn_start') and not self.is_preview_mode:
            self.btn_start.config(text="결과값 미리보기")
            self.is_preview_mode = True
            
            self.log_text.config(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.config(state="disabled")

    def _update_row_labels(self):
        for idx, row in enumerate(self.folder_rows):
            row['label'].config(text=f"#{idx + 1}")

    def _browse_folder(self, var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)

    def _build_run_section(self, parent):
        frame = tk.Frame(parent, bg=COLOR_BG, pady=10)
        frame.pack(fill="x")

        self.btn_start = tk.Button(
            frame, text="결과값 미리보기", bg=COLOR_ACCENT, fg="white",
            font=("Malgun Gothic", 12, "bold"), relief="flat",
            padx=20, pady=10, cursor="hand2",
            command=self._handle_action_button
        )
        self.btn_start.pack(fill="x")
        self.btn_start.bind("<Enter>", lambda e: self.btn_start.config(bg="#0063A5")) # Darker blue
        self.btn_start.bind("<Leave>", lambda e: self.btn_start.config(bg=COLOR_ACCENT))

        self.progress_bar = ttk.Progressbar(frame, mode="determinate")
        self.progress_bar.pack(fill="x", pady=(10, 0))

    def _build_progress_section(self, parent):
        frame = tk.Frame(parent, bg=COLOR_BG)
        frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(
            frame, height=5, bg=COLOR_INPUT_BG, fg="#AAAAAA",
            font=self.font_mono, relief="flat", state="disabled", padx=10, pady=5
        )
        self.log_text.pack(fill="both", expand=True)

    def _build_footer(self, parent):
        # Footer Container
        footer_frame = tk.Frame(parent, bg=COLOR_FOOTER, height=60) # Increased height
        footer_frame.pack(side="bottom", fill="x")
        footer_frame.pack_propagate(False) # Fixed height

        # Top Separator
        tk.Frame(footer_frame, bg="#3E3E42", height=1).pack(fill="x", side="top")

        # Content Frame
        content = tk.Frame(footer_frame, bg=COLOR_FOOTER, padx=15)
        content.pack(fill="both", expand=True)

        # Left: Credits
        left_box = tk.Frame(content, bg=COLOR_FOOTER)
        left_box.pack(side="left", fill="y", pady=10)
        
        # ZigZag Pic {버전정보}
        # 제작자 : mOOnster
        tk.Label(left_box, text=f"ZigZag Pic {self.version}", fg="#CCCCCC", bg=COLOR_FOOTER, font=("Malgun Gothic", 10, "bold")).pack(anchor="w")
        tk.Label(left_box, text="제작자 : mOOnster", fg="#888888", bg=COLOR_FOOTER, font=("Malgun Gothic", 9)).pack(anchor="w")

        # Right: Donation Buttons
        right_box = tk.Frame(content, bg=COLOR_FOOTER)
        right_box.pack(side="right", fill="y", pady=10)

        # Toss Button
        btn_toss = tk.Button(
            right_box, text="토스 후원", bg="#3282F6", fg="white",
            font=("Malgun Gothic", 11, "bold"), relief="flat", padx=15, pady=2,
            command=lambda: self._show_qr_popup("toss.png", "토스 후원")
        )
        btn_toss.pack(side="left", padx=5)
        
        # Kakao Button
        btn_kakao = tk.Button(
            right_box, text="카카오 후원", bg="#FEE500", fg="black",
            font=("Malgun Gothic", 11, "bold"), relief="flat", padx=15, pady=2,
            command=lambda: self._show_qr_popup("kakao.png", "카카오 후원")
        )
        btn_kakao.pack(side="left", padx=5)

    def _show_qr_popup(self, image_file, title):
        try:
            # Check if file exists (PyInstaller one-file support)
            if hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            img_path = os.path.join(base_path, image_file)
            
            if not os.path.exists(img_path):
                messagebox.showerror("오류", f"이미지 파일을 찾을 수 없습니다.\n{img_path}")
                return

            # Popup Window
            qr_win = tk.Toplevel(self.root)
            qr_win.title(title)
            qr_win.configure(bg=COLOR_BG)
            qr_win.geometry("300x350")
            
            # Center
            x = self.root.winfo_x() + (self.width // 2) - 150
            y = self.root.winfo_y() + (self.height // 2) - 175
            qr_win.geometry(f"+{x}+{y}")

            tk.Label(qr_win, text=title, font=self.font_header, fg=COLOR_FG, bg=COLOR_BG).pack(pady=10)

            # Image
            img = Image.open(img_path)
            img = img.resize((200, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            lbl_img = tk.Label(qr_win, image=photo, bg=COLOR_BG)
            lbl_img.image = photo # Keep reference
            lbl_img.pack(pady=10)

            tk.Button(qr_win, text="닫기", command=qr_win.destroy, bg=COLOR_INPUT_BG, fg=COLOR_FG, relief="flat", width=10).pack(pady=10)

        except Exception as e:
            messagebox.showerror("오류", f"QR 코드를 열 수 없습니다.\n{e}")

    def _bind_hover(self, widget):
        widget.bind("<Enter>", lambda e: widget.config(bg=COLOR_HOVER))
        widget.bind("<Leave>", lambda e: widget.config(bg=COLOR_INPUT_BG))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.root.update_idletasks()

    def reset_progress(self):
        self.progress_bar["value"] = 0

    # --- Logic Methods (Copied & Adapted) ---
    def _get_image_files(self, folder):
        exts = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp")
        files = []
        try:
            for name in os.listdir(folder):
                path = os.path.join(folder, name)
                if os.path.isfile(path) and name.lower().endswith(exts):
                    files.append(name)
        except: pass
        files.sort()
        return files

    def _handle_action_button(self):
        if self.is_preview_mode:
            self.start_preview()
        else:
            self.start_interleaving()

    def start_preview(self):
        valid_folders = []
        for idx, row in enumerate(self.folder_rows):
            path = row['path_var'].get().strip()
            name = row['name_var'].get().strip()
            if path:
                valid_folders.append({'path': path, 'name': name, 'idx': idx + 1})

        if len(valid_folders) < 2:
            messagebox.showwarning("경고", "최소 2개 이상의 폴더를 선택해주세요.")
            return

        # Check existing
        all_files = []
        min_len = float('inf')
        for item in valid_folders:
            if not os.path.isdir(item['path']):
                messagebox.showwarning("오류", f"폴더를 찾을 수 없습니다: {item['path']}")
                return
            files = self._get_image_files(item['path'])
            if not files:
                messagebox.showwarning("경고", f"이미지가 없는 폴더입니다: {item['path']}")
                return
            all_files.append(files)
            min_len = min(min_len, len(files))

        total_files = min_len * len(valid_folders)
        
        # Show Summary in Log
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        res_dir = os.path.join(desktop, f"ZigZagPic_{ts}")
        
        # Generate sample names (first 3 files)
        samples = []
        cnt = 1
        for i in range(min(3, min_len)):
            for f_idx in range(len(valid_folders)):
                if len(samples) >= 3: break
                fname = all_files[f_idx][i]
                ext = os.path.splitext(fname)[1]
                prefix = valid_folders[f_idx]['name']
                suffix = f"_{prefix}" if prefix else ""
                new_name = f"{cnt:03d}{suffix}{ext}"
                samples.append(new_name)
                cnt += 1
        
        sample_str = ", ".join(samples) + " ..."

        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("end", f" 작업 요약: {len(valid_folders)}개 폴더 × 각 {min_len}장 = 총 {total_files}장 생성 예정\n")
        self.log_text.insert("end", f"📄 파일명: {sample_str}\n")
        self.log_text.insert("end", f"📂 예상 저장 위치: {res_dir}")
        self.log_text.config(state="disabled")

        # Change Button State
        self.btn_start.config(text="합치기 시작")
        self.is_preview_mode = False

    def start_interleaving(self):
        valid_folders = []
        for idx, row in enumerate(self.folder_rows):
            path = row['path_var'].get().strip()
            name = row['name_var'].get().strip()
            if path:
                valid_folders.append({'path': path, 'name': name, 'idx': idx + 1})

        if len(valid_folders) < 2:
            messagebox.showwarning("경고", "최소 2개 이상의 폴더를 선택해주세요.")
            return

        # Check existing
        all_files = []
        min_len = float('inf')
        for item in valid_folders:
            if not os.path.isdir(item['path']):
                messagebox.showwarning("오류", f"폴더를 찾을 수 없습니다: {item['path']}")
                return
            files = self._get_image_files(item['path'])
            if not files:
                messagebox.showwarning("경고", f"이미지가 없는 폴더입니다: {item['path']}")
                return
            all_files.append(files)
            min_len = min(min_len, len(files))

        total_files = min_len * len(valid_folders)
        # self._show_preview_dialog(valid_folders, min_len, total_files, all_files)
        self._run_interleave(valid_folders, all_files, min_len)
        
        # Reset State
        self.btn_start.config(text="결과값 미리보기")
        self.is_preview_mode = True

    def _show_preview_dialog(self, valid_folders, min_len, total_files, all_files):
        # Preview Window
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.geometry("600x800")
        win.configure(bg=COLOR_BG)
        
        # Center relative to main
        x = self.root.winfo_x() + 50
        y = self.root.winfo_y() + 50
        win.geometry(f"+{x}+{y}")
        
        # Title Bar
        tb = tk.Frame(win, bg=COLOR_TITLE_BAR, height=35)
        tb.pack(fill="x", side="top")
        tb.pack_propagate(False)
        
        tk.Label(tb, text="결과 미리보기 (공평하게 섞는 중...)", fg=COLOR_FG, bg=COLOR_TITLE_BAR, font=self.font_title).pack(side="left", padx=10)
        
        # Close Button
        btn_close = tk.Button(tb, text="r", command=win.destroy, bg=COLOR_TITLE_BAR, fg=COLOR_FG, bd=0, font=("Marlett", 10), width=4)
        btn_close.pack(side="right")
        btn_close.bind("<Enter>", lambda e: btn_close.config(bg=COLOR_DANGER))
        btn_close.bind("<Leave>", lambda e: btn_close.config(bg=COLOR_TITLE_BAR))

        # Main Content Area
        content = tk.Frame(win, bg=COLOR_BG, padx=20, pady=20)
        content.pack(fill="both", expand=True)

        # Info Header
        info_text = f"총 {len(valid_folders)}개 폴더 / 각 {min_len}장 / 총 {total_files}장 생성 예정"
        tk.Label(content, text=info_text, font=self.font_bold, fg=COLOR_ACCENT, bg=COLOR_BG).pack(anchor="w", pady=(0, 5))
        
        # Warning
        tk.Label(content, text="⚠️ 가장 사진이 적은 폴더 개수에 맞춰 남는 사진은 제외됩니다!", font=self.font_base, fg=COLOR_WARNING, bg=COLOR_BG).pack(anchor="w", pady=(0, 10))

        # ListBox Container
        list_frame = tk.Frame(content, bg=COLOR_BG, bd=1, relief="solid") # Border
        list_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        self.preview_list = tk.Listbox(
            list_frame, 
            bg=COLOR_INPUT_BG, 
            fg=COLOR_FG, 
            font=self.font_mono,
            selectbackground=COLOR_ACCENT,
            selectforeground="white",
            relief="flat",
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.preview_list.yview)
        
        self.preview_list.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Populate List
        cnt = 1
        for i in range(min_len):
            for f_idx in range(len(valid_folders)):
                fname = all_files[f_idx][i]
                ext = os.path.splitext(fname)[1]
                prefix = valid_folders[f_idx]['name']
                suffix = f"_{prefix}" if prefix else ""
                new_name = f"{cnt:03d}{suffix}{ext}  <--  {fname}"
                self.preview_list.insert("end", new_name)
                cnt += 1

        # Action Bar (Bottom)
        action_bar = tk.Frame(win, bg=COLOR_BG, height=60)
        action_bar.pack(fill="x", side="bottom", pady=20)
        
        # Buttons
        btn_frame = tk.Frame(action_bar, bg=COLOR_BG)
        btn_frame.pack(anchor="center")

        def do_run():
            win.destroy()
            self._run_interleave(valid_folders, all_files, min_len)

        # Cancel Button
        btn_cancel = tk.Button(
            btn_frame, text="취소", 
            bg=COLOR_INPUT_BG, fg=COLOR_FG, 
            font=self.font_bold, relief="flat", 
            width=12, height=2,
            command=win.destroy
        )
        btn_cancel.pack(side="left", padx=10)
        btn_cancel.bind("<Enter>", lambda e: btn_cancel.config(bg="#555555"))
        btn_cancel.bind("<Leave>", lambda e: btn_cancel.config(bg=COLOR_INPUT_BG))

        # Proceed Button
        btn_ok = tk.Button(
            btn_frame, text="진행 (파일 생성)", 
            bg=COLOR_ACCENT, fg="white", 
            font=self.font_bold, relief="flat", 
            width=15, height=2,
            command=do_run
        )
        btn_ok.pack(side="left", padx=10)
        btn_ok.bind("<Enter>", lambda e: btn_ok.config(bg="#0063A5"))
        btn_ok.bind("<Leave>", lambda e: btn_ok.config(bg=COLOR_ACCENT))

    def _run_interleave(self, folder_list, all_files, min_len):
        self.reset_progress()
        self.log(f"작업 시작: {len(folder_list)}개 폴더, 각 {min_len}장")
        
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        res_dir = os.path.join(desktop, f"ZigZagPic_{ts}")
        os.makedirs(res_dir, exist_ok=True)
        
        total = min_len * len(folder_list)
        self.progress_bar["maximum"] = total
        
        cnt = 1
        try:
            for i in range(min_len):
                for f_idx in range(len(folder_list)):
                    fname = all_files[f_idx][i]
                    src = os.path.join(folder_list[f_idx]['path'], fname)
                    ext = os.path.splitext(fname)[1]
                    prefix = folder_list[f_idx]['name']
                    suffix = f"_{prefix}" if prefix else ""
                    new_name = f"{cnt:03d}{suffix}{ext}"
                    shutil.copy2(src, os.path.join(res_dir, new_name))
                    
                    self.log(f"[{cnt}] {new_name}")
                    cnt += 1
                    self.progress_bar["value"] = cnt
                    if cnt % 5 == 0: self.root.update_idletasks()
                    
            messagebox.showinfo("완료", f"작업 완료!\n위치: {res_dir}")
            if self.auto_open_var.get():
                os.startfile(res_dir)
        except Exception as e:
            messagebox.showerror("오류", str(e))
            self.log(f"오류: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InterleaverApp(root)
    root.mainloop()
