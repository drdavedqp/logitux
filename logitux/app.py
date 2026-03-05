from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CONFIG_DIR = Path.home() / ".config" / "logitux"
CONFIG_FILE = CONFIG_DIR / "profiles.json"


@dataclass
class Device:
    name: str
    id: str


class CommandError(RuntimeError):
    pass


def run_command(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise CommandError(f"{' '.join(cmd)} failed: {result.stderr.strip()}")
    return result.stdout


def list_devices() -> list[Device]:
    """Read devices from input-remapper-control."""
    out = run_command(["input-remapper-control", "--list-devices"])
    devices: list[Device] = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if " " not in line:
            continue
        name, dev_id = line.rsplit(" ", 1)
        devices.append(Device(name=name.strip(), id=dev_id.strip()))
    return devices


def load_profiles() -> dict:
    if not CONFIG_FILE.exists():
        return {"mappings": {}, "dpi": {}}
    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_profiles(data: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def set_button_mapping(device_id: str, button: str, key_combo: str) -> dict:
    data = load_profiles()
    data.setdefault("mappings", {}).setdefault(device_id, {})[button] = key_combo
    save_profiles(data)
    return data


def set_dpi(device_name: str, dpi: int, profile: int = 0, resolution_slot: int = 0) -> None:
    """Apply DPI via ratbagctl (used by piper on Fedora/Nobara)."""
    run_command(
        [
            "ratbagctl",
            device_name,
            "profile",
            str(profile),
            "resolution",
            str(resolution_slot),
            "set",
            str(dpi),
        ]
    )


def build_input_remapper_preset(device_name: str, mappings: dict[str, str]) -> dict:
    preset = {
        "preset": "logitux",
        "device": device_name,
        "mapping": [],
    }
    for button, key_combo in sorted(mappings.items(), key=lambda x: int(x[0])):
        preset["mapping"].append(
            {
                "input": {"type": "button", "code": int(button)},
                "output": {"type": "keyboard", "keys": key_combo},
            }
        )
    return preset


def install_input_remapper_preset(device_name: str, device_id: str) -> Path:
    profiles = load_profiles()
    mapping = profiles.get("mappings", {}).get(device_id, {})
    preset = build_input_remapper_preset(device_name, mapping)
    safe_name = device_name.replace("/", "_")
    target_dir = Path.home() / ".config" / "input-remapper-2" / "presets" / safe_name
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / "logitux.json"
    with target_file.open("w", encoding="utf-8") as f:
        json.dump(preset, f, indent=2)
    return target_file


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="logitux",
        description="Simple Logitech Options+ style helper for Nobara/Linux",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("devices", help="List input-remapper devices")

    map_parser = sub.add_parser("map-button", help="Map a mouse button to keyboard keys")
    map_parser.add_argument("device_id", help="input-remapper device id")
    map_parser.add_argument("button", help="Button code (e.g. 8)")
    map_parser.add_argument("key_combo", help="Output key combo (e.g. CTRL+ALT+T)")

    dpi_parser = sub.add_parser("set-dpi", help="Set DPI with ratbagctl")
    dpi_parser.add_argument("device_name", help="Exact ratbagctl device name")
    dpi_parser.add_argument("dpi", type=int, help="DPI value")
    dpi_parser.add_argument("--profile", type=int, default=0)
    dpi_parser.add_argument("--resolution-slot", type=int, default=0)

    preset_parser = sub.add_parser("install-preset", help="Write input-remapper preset from saved mappings")
    preset_parser.add_argument("device_name")
    preset_parser.add_argument("device_id")

    sub.add_parser("gui", help="Launch graphical interface")

    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        if args.command == "devices":
            for dev in list_devices():
                print(f"{dev.name}\t{dev.id}")
            return 0

        if args.command == "map-button":
            set_button_mapping(args.device_id, args.button, args.key_combo)
            print(f"Saved mapping: device={args.device_id}, button={args.button} -> {args.key_combo}")
            return 0

        if args.command == "set-dpi":
            set_dpi(args.device_name, args.dpi, args.profile, args.resolution_slot)
            print("DPI updated")
            return 0

        if args.command == "install-preset":
            path = install_input_remapper_preset(args.device_name, args.device_id)
            print(f"Preset written to {path}")
            return 0

        if args.command == "gui":
            from .gui import run_gui

            run_gui()
            return 0

        return 1
    except CommandError as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
