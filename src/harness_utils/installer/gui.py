"""Graphical User Interface (GUI) Installer Wizard for Harness Utils.

Built using Tkinter (Python Standard Library). Provides a multi-step installation
wizard with script discovery, custom script adding, installation directory selection,
PATH and shortcut options, and real-time installation logs.
"""

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from harness_utils.installer.installer_engine import InstallerEngine
from harness_utils.installer.script_manager import ScriptInfo, ScriptManager


class InstallerGUI(tk.Tk):
    """Tkinter-based Windows Installer Wizard."""

    def __init__(self, script_dir: str | Path = "script"):
        super().__init__()

        self.title("Harness Utils - Windows Script Installer")
        self.geometry("640x480")
        self.resizable(False, False)

        # Style configuration
        self.style = ttk.Style(self)
        self.style.theme_use("vista" if "vista" in self.style.theme_names() else "default")

        self.script_manager = ScriptManager(script_dir=script_dir)
        self.installer_engine = InstallerEngine()
        self.scripts: list[ScriptInfo] = self.script_manager.scan_scripts()

        # Wizard state variables
        self.install_dir_var = tk.StringVar(value=str(self.installer_engine.install_dir))
        self.add_path_var = tk.BooleanVar(value=True)
        self.start_menu_var = tk.BooleanVar(value=True)
        self.desktop_var = tk.BooleanVar(value=True)

        self.current_step = 0
        self.frames: list[ttk.Frame] = []

        self._build_ui()
        self._show_step(0)

    def _build_ui(self) -> None:
        """Construct wizard container and step frames."""
        self.container = ttk.Frame(self, padding="10")
        self.container.pack(fill=tk.BOTH, expand=True)

        # Step 0: Welcome Frame
        self.frame_welcome = ttk.Frame(self.container)
        lbl_title = ttk.Label(
            self.frame_welcome,
            text="Welcome to Harness Utils Setup",
            font=("Segoe UI", 16, "bold"),
        )
        lbl_title.pack(anchor=tk.W, pady=(10, 5))

        lbl_desc = ttk.Label(
            self.frame_welcome,
            text="This wizard will install Windows harness automation scripts onto your system.\n\n"
                 "You can select which scripts to install, add your own custom scripts,\n"
                 "and automatically configure system PATH environment variables.",
            font=("Segoe UI", 10),
            wraplength=580,
            justify=tk.LEFT,
        )
        lbl_desc.pack(anchor=tk.W, pady=10)

        # Step 1: Script Selection Frame
        self.frame_scripts = ttk.Frame(self.container)
        lbl_sec1 = ttk.Label(
            self.frame_scripts,
            text="Select Scripts to Install",
            font=("Segoe UI", 14, "bold"),
        )
        lbl_sec1.pack(anchor=tk.W, pady=(5, 5))

        lbl_sec1_desc = ttk.Label(
            self.frame_scripts,
            text="Choose scripts from the project or add new custom scripts to include in the setup:",
            font=("Segoe UI", 9),
        )
        lbl_sec1_desc.pack(anchor=tk.W, pady=(0, 5))

        # Listbox for scripts with checkboxes frame
        self.script_list_frame = ttk.Frame(self.frame_scripts)
        self.script_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.script_vars: dict[str, tk.BooleanVar] = {}
        self.script_check_canvas = tk.Canvas(self.script_list_frame, borderwidth=1, relief="sunken")
        self.scrollbar = ttk.Scrollbar(self.script_list_frame, orient="vertical", command=self.script_check_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.script_check_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.script_check_canvas.configure(scrollregion=self.script_check_canvas.bbox("all"))
        )
        self.script_check_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.script_check_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.script_check_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self._refresh_script_checkboxes()

        # Buttons to Add Script & Select/Unselect All
        btn_box = ttk.Frame(self.frame_scripts)
        btn_box.pack(fill=tk.X, pady=5)

        btn_add_script = ttk.Button(
            btn_box, text="➕ Add Custom Script...", command=self._on_add_custom_script
        )
        btn_add_script.pack(side=tk.LEFT, padx=(0, 5))

        btn_select_all = ttk.Button(
            btn_box, text="Select All", command=lambda: self._toggle_all_scripts(True)
        )
        btn_select_all.pack(side=tk.LEFT, padx=5)

        btn_unselect_all = ttk.Button(
            btn_box, text="Unselect All", command=lambda: self._toggle_all_scripts(False)
        )
        btn_unselect_all.pack(side=tk.LEFT, padx=5)

        # Step 2: Destination & Options Frame
        self.frame_options = ttk.Frame(self.container)
        lbl_sec2 = ttk.Label(
            self.frame_options, text="Installation Options", font=("Segoe UI", 14, "bold")
        )
        lbl_sec2.pack(anchor=tk.W, pady=(5, 5))

        lbl_dir = ttk.Label(self.frame_options, text="Destination Directory:")
        lbl_dir.pack(anchor=tk.W, pady=(10, 2))

        dir_entry_box = ttk.Frame(self.frame_options)
        dir_entry_box.pack(fill=tk.X, pady=(0, 10))

        txt_dir = ttk.Entry(dir_entry_box, textvariable=self.install_dir_var, width=50)
        txt_dir.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        btn_browse = ttk.Button(dir_entry_box, text="Browse...", command=self._on_browse_dir)
        btn_browse.pack(side=tk.RIGHT)

        chk_path = ttk.Checkbutton(
            self.frame_options,
            text="Add destination folder to User PATH environment variable",
            variable=self.add_path_var,
        )
        chk_path.pack(anchor=tk.W, pady=5)

        chk_start = ttk.Checkbutton(
            self.frame_options,
            text="Create Start Menu shortcuts",
            variable=self.start_menu_var,
        )
        chk_start.pack(anchor=tk.W, pady=5)

        chk_desktop = ttk.Checkbutton(
            self.frame_options,
            text="Create Desktop shortcuts",
            variable=self.desktop_var,
        )
        chk_desktop.pack(anchor=tk.W, pady=5)

        # Step 3: Installation Progress Frame
        self.frame_progress = ttk.Frame(self.container)
        lbl_sec3 = ttk.Label(
            self.frame_progress, text="Installing Scripts...", font=("Segoe UI", 14, "bold")
        )
        lbl_sec3.pack(anchor=tk.W, pady=(5, 5))

        self.progress_bar = ttk.Progressbar(self.frame_progress, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, pady=10)

        self.txt_log = tk.Text(self.frame_progress, height=12, width=70, state="disabled")
        self.txt_log.pack(fill=tk.BOTH, expand=True, pady=5)

        # Navigation Bar
        self.nav_frame = ttk.Frame(self, padding="10")
        self.nav_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.btn_back = ttk.Button(self.nav_frame, text="< Back", command=self._on_back)
        self.btn_back.pack(side=tk.LEFT)

        self.btn_cancel = ttk.Button(self.nav_frame, text="Cancel", command=self.destroy)
        self.btn_cancel.pack(side=tk.RIGHT, padx=(5, 0))

        self.btn_next = ttk.Button(self.nav_frame, text="Next >", command=self._on_next)
        self.btn_next.pack(side=tk.RIGHT)

        self.frames = [
            self.frame_welcome,
            self.frame_scripts,
            self.frame_options,
            self.frame_progress,
        ]

    def _refresh_script_checkboxes(self) -> None:
        """Clear and rebuild script checkboxes."""
        for child in self.scrollable_frame.winfo_children():
            child.destroy()

        self.script_vars.clear()
        for script in self.scripts:
            var = tk.BooleanVar(value=script.is_enabled)
            self.script_vars[script.name] = var

            chk_frame = ttk.Frame(self.scrollable_frame)
            chk_frame.pack(fill=tk.X, anchor=tk.W, pady=2, padx=5)

            chk = ttk.Checkbutton(
                chk_frame,
                text=f"{script.name} ({script.script_type})",
                variable=var,
            )
            chk.pack(anchor=tk.W)

            lbl_desc = ttk.Label(
                chk_frame, text=f"  ↳ {script.description}", font=("Segoe UI", 8), foreground="gray"
            )
            lbl_desc.pack(anchor=tk.W)

    def _on_add_custom_script(self) -> None:
        """File picker dialog to add a new script file."""
        file_path = filedialog.askopenfilename(
            title="Select Custom Script File",
            filetypes=[
                ("Script Files", "*.ps1;*.bat;*.cmd;*.vbs;*.py;*.sh"),
                ("PowerShell Scripts", "*.ps1"),
                ("Batch Files", "*.bat;*.cmd"),
                ("Python Scripts", "*.py"),
                ("All Files", "*.*"),
            ],
        )
        if file_path:
            try:
                added_script = self.script_manager.add_script(file_path)
                self.scripts = self.script_manager.scan_scripts()
                self._refresh_script_checkboxes()
                messagebox.showinfo(
                    "Script Added",
                    f"Successfully added '{added_script.name}' to the installation list!",
                )
            except Exception as e:
                messagebox.showerror("Error Adding Script", str(e))

    def _toggle_all_scripts(self, state: bool) -> None:
        for var in self.script_vars.values():
            var.set(state)

    def _on_browse_dir(self) -> None:
        selected = filedialog.askdirectory(
            title="Select Installation Directory",
            initialdir=self.install_dir_var.get(),
        )
        if selected:
            self.install_dir_var.set(selected)

    def _show_step(self, step_idx: int) -> None:
        self.current_step = step_idx
        for i, frame in enumerate(self.frames):
            if i == step_idx:
                frame.pack(fill=tk.BOTH, expand=True)
            else:
                frame.pack_forget()

        # Update button states
        self.btn_back.config(state=tk.NORMAL if step_idx > 0 and step_idx < 3 else tk.DISABLED)

        if step_idx == 2:
            self.btn_next.config(text="Install")
        elif step_idx == 3:
            self.btn_next.config(text="Finish", state=tk.DISABLED)
            self.btn_back.config(state=tk.DISABLED)
            self.btn_cancel.config(state=tk.DISABLED)
            self._start_installation()
        else:
            self.btn_next.config(text="Next >", state=tk.NORMAL)

    def _on_next(self) -> None:
        if self.current_step == 1:
            # Ensure at least one script is selected
            selected_count = sum(1 for v in self.script_vars.values() if v.get())
            if selected_count == 0:
                messagebox.showwarning(
                    "No Scripts Selected", "Please select at least one script to install."
                )
                return
        if self.current_step < len(self.frames) - 1:
            self._show_step(self.current_step + 1)
        else:
            self.destroy()

    def _on_back(self) -> None:
        if self.current_step > 0:
            self._show_step(self.current_step - 1)

    def _log_message(self, message: str) -> None:
        self.txt_log.config(state="normal")
        self.txt_log.insert(tk.END, message + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")

    def _start_installation(self) -> None:
        self.progress_bar.start(10)
        self._log_message("Starting installation...")

        # Update script selection states
        for script in self.scripts:
            if script.name in self.script_vars:
                script.is_enabled = self.script_vars[script.name].get()

        selected_scripts = [s for s in self.scripts if s.is_enabled]
        install_path = Path(self.install_dir_var.get())

        def _worker() -> None:
            try:
                engine = InstallerEngine(install_dir=install_path)
                self._log_message(f"Target Directory: {install_path}")
                self._log_message(f"Selected Scripts: {len(selected_scripts)}")

                engine.install(
                    scripts=selected_scripts,
                    add_to_path=self.add_path_var.get(),
                    create_start_menu=self.start_menu_var.get(),
                    create_desktop=self.desktop_var.get(),
                )

                self._log_message("----------------------------------------")
                self._log_message("SUCCESS: All scripts installed successfully!")
                if self.add_path_var.get():
                    self._log_message("NOTE: PATH environment variable updated.")

                self.after(0, self._on_install_complete, True)
            except Exception as e:
                self._log_message(f"ERROR: Installation failed: {e}")
                self.after(0, self._on_install_complete, False)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def _on_install_complete(self, success: bool) -> None:
        self.progress_bar.stop()
        self.btn_next.config(state=tk.NORMAL)
        if success:
            messagebox.showinfo("Installation Complete", "Harness Utils scripts installed successfully!")
        else:
            messagebox.showerror("Installation Error", "Installation encountered errors. Check log for details.")


def launch_gui(script_dir: str | Path = "script") -> None:
    """Launch the installer GUI."""
    app = InstallerGUI(script_dir=script_dir)
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
