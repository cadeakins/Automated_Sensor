import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import re
import time
import math
from pathlib import Path
from PIL import Image, ImageTk

from gui_theme import (
    NAVY,
    NAVY_2,
    OFF_WHITE,
    TECHMI_BLUE,
    FONT_BRAND,
    _btn,
)

# Fixed layout sizes for main dashboard shell
SIDEBAR_WIDTH = 200
TOPBAR_HEIGHT = 70
CONTENT_PAD_X = 15
CONTENT_PAD_Y = 12

class LayoutMixin:
    """
    GUI section mixin split out of the original SensorGUI class.
    """

    def _build_ui(self):
            # For reference weight = 0 means fixed size, 1 means flexible
            # Row 0 topbar
            self.root.grid_rowconfigure(0, weight=0)
            # Row 1 main dashboard
            self.root.grid_rowconfigure(1, weight=1)
            # Col 0 is fixed sidebar
            self.root.grid_columnconfigure(0, weight=0, minsize=SIDEBAR_WIDTH)
            # Col 1 is flexible main content area
            self.root.grid_columnconfigure(1, weight=1)

            self._build_sidebar(self.root)
            self._build_topbar()
            self._build_content(self.root)
            

    def _build_topbar(self):
            """
            Creates the main bar on top with logo, title, settings, and status
            """
            bar = tk.Frame(self.root, bg=NAVY, height=TOPBAR_HEIGHT)
            bar.grid(row=0, column=1, sticky="ew")
            bar.grid_propagate(False)
            bar.grid_columnconfigure(0, weight=1)
            bar.grid_columnconfigure(1, weight=0)
            
            # Center: Title
            tk.Label(
                  bar,
                  text="Bioreactor Sensor Control Panel",
                  fg="white",
                  bg=NAVY,
                  font=(FONT_BRAND, 16, "bold")
            ).grid(row=0, column=0, padx=20, sticky="w")

            # Right side: system ready + settings
            right = tk.Frame(bar, bg=NAVY)
            right.grid(row=0, column=1, padx=16, sticky="e")

            # System ready pill
            self.system_ready_lbl = tk.Label(
                right, text="⬤  System Ready",
                fg="#d1fae5", bg="#0d2e1a",
                font=(FONT_BRAND, 11, "bold"),
                padx=12, pady=7, relief="flat"
            )
            self.system_ready_lbl.pack(side=tk.LEFT, padx=(0, 12))

            _btn(right, "⚙  Settings", self._open_settings_window,
                 kind="dark").pack(side=tk.LEFT)

    
    def _build_sidebar(self, parent):
            """
            Builds fixed left sidebar.
            Sidebar spans both root rows so it owns full height of app.
            Prevents dashboard content from appearing underneath it
            """
            sb = tk.Frame(parent, bg=NAVY, width=SIDEBAR_WIDTH)
            sb.grid(row=0, column=0, rowspan=2, sticky="ns")
            sb.grid_propagate(False)
            sb.grid_rowconfigure(3, weight=1)

            # Logo
            logo_frame = tk.Frame(sb, bg=NAVY, width=SIDEBAR_WIDTH, height=TOPBAR_HEIGHT)
            logo_frame.grid(row=0, column=0, sticky="nsw", padx=(8, 16))
            logo_frame.grid_propagate(False)

            # Try to load logo
            try : 
                logo_image = Image.open("logo_azul.png").convert("RGBA")

                target_height = 70
                scale = target_height / logo_image.height
                target_width = max(1, int(logo_image.width * scale))

                # Resize
                if target_width > SIDEBAR_WIDTH - 24:
                    target_width = SIDEBAR_WIDTH - 24
                    scale = target_width / logo_image.width
                    target_height = max(1, int(logo_image.height * scale))

                logo_image = logo_image.resize((target_width, target_height), Image.LANCZOS)
                
                # Store PhotoImage on shelf so Tkinter does not garbage collect it
                self._topbar_logo_photo = ImageTk.PhotoImage(logo_image)

                logo_label = tk.Label(logo_frame, image=self._topbar_logo_photo, bg=NAVY)
                logo_label.place(relx=0.45, rely=0.5, anchor="center")

            # If image fails to load fallback to text
            except Exception : 
                self._topbar_logo_photo = None

                logo_label = tk.Label(
                    logo_frame,
                    text="TECHMI",
                    fg="white",
                    bg=NAVY,
                    font=(FONT_BRAND, 20, "bold")
                )
                logo_label.place(relx=0.5, rely=0.5, anchor="center")


           # Dashboard nav active state.
            active = tk.Frame(sb, bg=TECHMI_BLUE, padx=0, pady=0)
            active.grid(row=1, column=0, sticky="ew", padx=10, pady=(8, 4))

            tk.Label(
                active,
                text="⌂  Dashboard",
                fg="white",
                bg=TECHMI_BLUE,
                font=(FONT_BRAND, 12, "bold"),
                padx=14,
                pady=10,
                anchor="w"
            ).pack(fill=tk.X)

            # Settings nav.
            settings_nav = tk.Label(
                sb,
                text="⚙  Settings",
                fg="#9db5d4",
                bg=NAVY,
                font=(FONT_BRAND, 11),
                padx=22,
                pady=12,
                anchor="w",
                cursor="hand2"
            )
            settings_nav.grid(row=2, column=0, sticky="ew")
            settings_nav.bind("<Button-1>", lambda e: self._open_settings_window())

            # All systems nominal card near bottom.
            nom = tk.Frame(sb, bg=NAVY_2, padx=10, pady=10)
            nom.grid(row=3, column=0, sticky="sew", padx=10, pady=12)

            tk.Label(
                nom,
                text="⬤  All Systems",
                fg="#bbf7d0",
                bg=NAVY_2,
                font=(FONT_BRAND, 10, "bold"),
                anchor="w"
            ).pack(fill=tk.X)

            tk.Label(
                nom,
                text="   Nominal",
                fg="#6ee7b7",
                bg=NAVY_2,
                font=(FONT_BRAND, 10),
                anchor="w"
            ).pack(fill=tk.X)

            # Version label at very bottom.
            tk.Label(
                sb,
                text="v1.0.0",
                fg="#3d5a80",
                bg=NAVY,
                font=(FONT_BRAND, 9)
            ).grid(row=4, column=0, pady=12)


    def _build_content(self, parent):
            """
            Builds the scrollable dashboard content area.
            Content fills space to right of sidebar, cards inside use two responsive columns.
            """
            # Scrollable canvas
            outer = tk.Frame(parent, bg=OFF_WHITE)
            outer.grid(row=1, column=1, sticky="nsew")
            # Let canvas fill whole content area
            outer.grid_rowconfigure(0, weight=1)
            outer.grid_columnconfigure(0, weight=1)

            canvas = tk.Canvas(outer, bg=OFF_WHITE, highlightthickness=0, bd=0)
            scrollbar = ttk.Scrollbar(outer, orient="vertical",
                                      command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)

            # Place canvas and scrollbar
            scrollbar.grid(row=0, column=1, sticky="ns")
            canvas.grid(row=0, column=0, sticky="nsew")

            content_frame = tk.Frame(canvas, bg=OFF_WHITE)
            canvas_window = canvas.create_window((0, 0), window=content_frame,anchor="nw")

            def _on_content_configure(event):
                """
                Updates scroll area after content changes size
                """
                canvas.configure(scrollregion=canvas.bbox("all"))

            def _on_canvas_configure(event) : 
                """
                Keep content frame locked to visible canvas width
                """
                canvas.itemconfig(canvas_window, width=event.width)

            # Scroll region when inner content changes
            content_frame.bind("<Configure>",_on_content_configure)
            # Canvas window width synced to canvas width
            canvas.bind("<Configure>", _on_canvas_configure)

            def _on_mousewheel(event):
                """ 
                Allows mouse wheel scrolling
                """
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
            # Bind mouse wheel only while cursor is over the canvas.
            canvas.bind("<Enter>", lambda event: canvas.bind_all("<MouseWheel>", _on_mousewheel))
            canvas.bind("<Leave>", lambda event: canvas.unbind_all("<MouseWheel>"))

            # Give the dashboard some padding inside the canvas.
            content_frame.grid_columnconfigure(0, weight=1)
            content_frame.grid_columnconfigure(1, weight=1)

            # Left dashboard column.
            left = tk.Frame(content_frame, bg=OFF_WHITE)
            left.grid(
                row=0,
                column=0,
                sticky="nsew",
                padx=(CONTENT_PAD_X, CONTENT_PAD_X // 2),
                pady=CONTENT_PAD_Y
            )
            left.grid_columnconfigure(0, weight=1)

            # Right dashboard column.
            right = tk.Frame(content_frame, bg=OFF_WHITE)
            right.grid(
                row=0,
                column=1,
                sticky="nsew",
                padx=(CONTENT_PAD_X // 2, CONTENT_PAD_X),
                pady=CONTENT_PAD_Y
            )
            right.grid_columnconfigure(0, weight=1)

            # Build left column panels.
            self._build_setup_panel(left)
            self._build_timing_panel(left)
            self._build_run_control_panel(left)
            self._build_live_status_panel(left)
            self._build_log_panel(left)

            # Build right column panels.
            self._build_camera_preview_panel(right)
            self._build_camera_settings_panel(right)
            self._build_recovery_panel(right)