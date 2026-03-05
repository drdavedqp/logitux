from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from . import app


class LogituxGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Logitux")
        self.root.geometry("640x420")

        self.device_map: dict[str, app.Device] = {}

        self.device_choice = tk.StringVar()
        self.device_name = tk.StringVar()
        self.button_code = tk.StringVar(value="8")
        self.key_combo = tk.StringVar(value="CTRL+ALT+T")
        self.dpi = tk.StringVar(value="1200")
        self.profile = tk.StringVar(value="0")
        self.resolution_slot = tk.StringVar(value="0")

        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Device (input-remapper)").grid(row=0, column=0, sticky=tk.W)
        self.device_combo = ttk.Combobox(frame, textvariable=self.device_choice, width=50, state="readonly")
        self.device_combo.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=(2, 8))
        ttk.Button(frame, text="Refresh Devices", command=self.refresh_devices).grid(row=1, column=3, padx=(8, 0))

        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=4, sticky=tk.EW, pady=8)

        ttk.Label(frame, text="Map Mouse Button -> Keypress").grid(row=3, column=0, sticky=tk.W)
        ttk.Label(frame, text="Button code").grid(row=4, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.button_code, width=10).grid(row=5, column=0, sticky=tk.W)
        ttk.Label(frame, text="Key combo").grid(row=4, column=1, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.key_combo, width=24).grid(row=5, column=1, sticky=tk.W)
        ttk.Button(frame, text="Save mapping", command=self.save_mapping).grid(row=5, column=2, sticky=tk.W)
        ttk.Button(frame, text="Install preset", command=self.install_preset).grid(row=5, column=3, sticky=tk.W)

        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=6, column=0, columnspan=4, sticky=tk.EW, pady=8)

        ttk.Label(frame, text="Set DPI (ratbagctl)").grid(row=7, column=0, sticky=tk.W)
        ttk.Label(frame, text="Ratbag device name").grid(row=8, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.device_name, width=30).grid(row=9, column=0, sticky=tk.W)

        ttk.Label(frame, text="DPI").grid(row=8, column=1, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.dpi, width=10).grid(row=9, column=1, sticky=tk.W)

        ttk.Label(frame, text="Profile").grid(row=8, column=2, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.profile, width=10).grid(row=9, column=2, sticky=tk.W)

        ttk.Label(frame, text="Resolution slot").grid(row=8, column=3, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.resolution_slot, width=10).grid(row=9, column=3, sticky=tk.W)

        ttk.Button(frame, text="Apply DPI", command=self.apply_dpi).grid(row=10, column=0, pady=(8, 0), sticky=tk.W)

        for i in range(4):
            frame.columnconfigure(i, weight=1)

        self.refresh_devices()

    def selected_device(self) -> app.Device:
        key = self.device_choice.get()
        if not key or key not in self.device_map:
            raise ValueError("Select a device first")
        return self.device_map[key]

    def refresh_devices(self) -> None:
        try:
            devices = app.list_devices()
        except app.CommandError as exc:
            messagebox.showerror("Device list failed", str(exc))
            return

        values: list[str] = []
        self.device_map = {}
        for dev in devices:
            label = f"{dev.name} ({dev.id})"
            values.append(label)
            self.device_map[label] = dev
        self.device_combo["values"] = values

        if values:
            self.device_choice.set(values[0])
            self.device_name.set(self.device_map[values[0]].name)

    def save_mapping(self) -> None:
        try:
            dev = self.selected_device()
            app.set_button_mapping(dev.id, self.button_code.get().strip(), self.key_combo.get().strip())
            messagebox.showinfo("Saved", "Mapping saved")
        except ValueError as exc:
            messagebox.showerror("Input error", str(exc))

    def install_preset(self) -> None:
        try:
            dev = self.selected_device()
            target = app.install_input_remapper_preset(dev.name, dev.id)
            messagebox.showinfo("Preset written", str(target))
        except ValueError as exc:
            messagebox.showerror("Input error", str(exc))

    def apply_dpi(self) -> None:
        try:
            dpi = int(self.dpi.get().strip())
            profile = int(self.profile.get().strip())
            slot = int(self.resolution_slot.get().strip())
            app.set_dpi(self.device_name.get().strip(), dpi, profile, slot)
            messagebox.showinfo("Done", "DPI updated")
        except ValueError:
            messagebox.showerror("Input error", "DPI/profile/slot must be integers")
        except app.CommandError as exc:
            messagebox.showerror("DPI failed", str(exc))


def run_gui() -> None:
    root = tk.Tk()
    LogituxGUI(root)
    root.mainloop()
