"""
MyPcNow - Windows 11 Privacy Cleaner
Main application with CustomTkinter GUI.
"""

import sys
import os
import threading
import time

# Handle frozen exe path
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

import customtkinter as ctk

from cleaners import CLEANER_CATEGORIES


class MyPCNow(ctk.CTk):
    """Main application window."""

    APP_NAME = "MyPcNow"
    APP_VERSION = "1.0.0"
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 750

    def __init__(self):
        super().__init__()

        # Window setup
        self.title(f"{self.APP_NAME} v{self.APP_VERSION} - PC 프라이버시 클리너")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(600, 600)
        self.resizable(True, True)

        # Appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # State
        self.checkboxes = {}  # key -> (CTkCheckBox, IntVar)
        self.is_cleaning = False

        # Build UI
        self._build_ui()

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.WINDOW_WIDTH) // 2
        y = (self.winfo_screenheight() - self.WINDOW_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        """Build the complete user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # scrollable area expands
        self.grid_rowconfigure(3, weight=0)  # log area fixed

        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(
            header,
            text=f"MyPcNow",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title_label.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Windows 11 프라이버시 클리너  |  내 PC 흔적을 안전하게 삭제합니다",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        subtitle.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 5))

        # Select All / Deselect All buttons in header
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")

        self.select_all_btn = ctk.CTkButton(
            btn_frame,
            text="전체 선택",
            width=100,
            height=32,
            command=self._select_all,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
        )
        self.select_all_btn.pack(side="left", padx=5)

        self.deselect_all_btn = ctk.CTkButton(
            btn_frame,
            text="전체 해제",
            width=100,
            height=32,
            command=self._deselect_all,
            fg_color="#4B5563",
            hover_color="#374151",
        )
        self.deselect_all_btn.pack(side="left", padx=5)

        # --- Scrollable Checkbox Area ---
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            label_text="삭제 항목 선택",
            label_font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.scroll_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        row_idx = 0
        for cat_key, cat_info in CLEANER_CATEGORIES.items():
            # Category header
            cat_header = ctk.CTkFrame(self.scroll_frame, fg_color="#1E293B", corner_radius=8)
            cat_header.grid(row=row_idx, column=0, sticky="ew", pady=(10, 2), padx=5)
            cat_header.grid_columnconfigure(0, weight=1)

            # Category select all checkbox
            cat_var = ctk.IntVar(value=0)
            cat_cb = ctk.CTkCheckBox(
                cat_header,
                text=f"  {cat_info['name']}",
                font=ctk.CTkFont(size=14, weight="bold"),
                variable=cat_var,
                command=lambda ck=cat_key, cv=cat_var: self._toggle_category(ck, cv),
                checkbox_width=22,
                checkbox_height=22,
            )
            cat_cb.grid(row=0, column=0, padx=10, pady=8, sticky="w")
            self.checkboxes[f"__cat_{cat_key}"] = (cat_cb, cat_var)
            row_idx += 1

            # Individual items
            for item_key, item_label in cat_info["items"].items():
                var = ctk.IntVar(value=0)
                cb = ctk.CTkCheckBox(
                    self.scroll_frame,
                    text=f"    {item_label}",
                    font=ctk.CTkFont(size=13),
                    variable=var,
                    command=lambda: self._update_category_states(),
                    checkbox_width=18,
                    checkbox_height=18,
                )
                cb.grid(row=row_idx, column=0, padx=25, pady=2, sticky="w")
                self.checkboxes[item_key] = (cb, var)
                row_idx += 1

        # --- Action buttons ---
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=2, column=0, padx=20, pady=(5, 5), sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(action_frame, height=6)
        self.progress_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self.progress_bar.set(0)

        self.clean_btn = ctk.CTkButton(
            action_frame,
            text="지금 정리하기",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            command=self._start_cleaning,
            fg_color="#DC2626",
            hover_color="#B91C1C",
        )
        self.clean_btn.grid(row=1, column=0, sticky="ew", padx=(0, 5))

        self.status_label = ctk.CTkLabel(
            action_frame,
            text="항목을 선택하고 '지금 정리하기'를 클릭하세요",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.status_label.grid(row=2, column=0, sticky="w", pady=(5, 0))

        # --- Log Area ---
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=3, column=0, padx=20, pady=(5, 15), sticky="ew")
        self.log_frame.grid_columnconfigure(0, weight=1)

        log_label = ctk.CTkLabel(
            self.log_frame,
            text="실행 로그",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        log_label.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")

        self.log_text = ctk.CTkTextbox(
            self.log_frame,
            height=150,
            font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled",
        )
        self.log_text.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")

    def _toggle_category(self, cat_key, cat_var):
        """Toggle all items in a category when category checkbox is clicked."""
        value = cat_var.get()
        cat_info = CLEANER_CATEGORIES[cat_key]
        for item_key in cat_info["items"]:
            if item_key in self.checkboxes:
                _, var = self.checkboxes[item_key]
                var.set(value)

    def _update_category_states(self):
        """Update category checkboxes based on their children states."""
        for cat_key, cat_info in CLEANER_CATEGORIES.items():
            cat_cb_key = f"__cat_{cat_key}"
            if cat_cb_key not in self.checkboxes:
                continue
            _, cat_var = self.checkboxes[cat_cb_key]
            all_checked = True
            for item_key in cat_info["items"]:
                if item_key in self.checkboxes:
                    _, var = self.checkboxes[item_key]
                    if var.get() == 0:
                        all_checked = False
                        break
            cat_var.set(1 if all_checked else 0)

    def _select_all(self):
        """Select all checkboxes."""
        for key, (cb, var) in self.checkboxes.items():
            var.set(1)

    def _deselect_all(self):
        """Deselect all checkboxes."""
        for key, (cb, var) in self.checkboxes.items():
            var.set(0)

    def _get_selected_items(self):
        """Get list of selected item keys (excluding category headers)."""
        selected = []
        for key, (cb, var) in self.checkboxes.items():
            if not key.startswith("__cat_") and var.get() == 1:
                selected.append(key)
        return selected

    def _log(self, message):
        """Thread-safe log message to the log textbox."""
        def _append():
            self.log_text.configure(state="normal")
            self.log_text.insert("end", message + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        self.after(0, _append)

    def _start_cleaning(self):
        """Start the cleaning process in a background thread."""
        if self.is_cleaning:
            return

        selected = self._get_selected_items()
        if not selected:
            self.status_label.configure(text="선택된 항목이 없습니다!", text_color="#EF4444")
            return

        self.is_cleaning = True
        self.clean_btn.configure(state="disabled", text="정리 중...")
        self.select_all_btn.configure(state="disabled")
        self.deselect_all_btn.configure(state="disabled")
        self.status_label.configure(text="정리 진행 중...", text_color="#FBBF24")
        self.progress_bar.set(0)

        # Clear log
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

        thread = threading.Thread(target=self._run_cleaning, args=(selected,), daemon=True)
        thread.start()

    def _run_cleaning(self, selected_items):
        """Run cleaning in background thread."""
        start_time = time.time()
        self._log(f"=== MyPcNow 정리 시작 ({len(selected_items)}개 항목) ===\n")

        # Group selected items by category
        items_by_category = {}
        for cat_key, cat_info in CLEANER_CATEGORIES.items():
            cat_items = [s for s in selected_items if s in cat_info["items"]]
            if cat_items:
                items_by_category[cat_key] = cat_items

        total_categories = len(items_by_category)
        completed = 0

        for cat_key, items in items_by_category.items():
            cat_info = CLEANER_CATEGORIES[cat_key]
            self._log(f"\n--- {cat_info['name']} ---")

            cleaner_class = cat_info["cleaner"]
            cleaner = cleaner_class(log_callback=self._log)
            cleaner.run(items)

            completed += 1
            progress = completed / total_categories
            self.after(0, lambda p=progress: self.progress_bar.set(p))

        elapsed = time.time() - start_time
        self._log(f"\n=== 정리 완료! ({elapsed:.1f}초 소요) ===")

        # Update UI on main thread
        def _finish():
            self.progress_bar.set(1)
            self.is_cleaning = False
            self.clean_btn.configure(state="normal", text="지금 정리하기")
            self.select_all_btn.configure(state="normal")
            self.deselect_all_btn.configure(state="normal")
            self.status_label.configure(
                text=f"정리 완료! {len(selected_items)}개 항목 처리됨 ({elapsed:.1f}초)",
                text_color="#22C55E",
            )

        self.after(0, _finish)


def main():
    app = MyPCNow()
    app.mainloop()


if __name__ == "__main__":
    main()
