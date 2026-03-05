# logitux

A lightweight Logitech Options+ style helper for Linux/Nobara focused on:
- mapping mouse buttons to keyboard shortcuts
- adjusting DPI

It uses tooling that already works well on Fedora/Nobara:
- [`input-remapper`](https://github.com/sezanzeb/input-remapper) for button -> key mappings
- [`ratbagctl`](https://github.com/libratbag/libratbag) for DPI control

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

### 1) List devices known by input-remapper

### GUI (simple desktop app)

```bash
logitux gui
```

Use it to:
- refresh/select your mouse device
- save button -> keypress mappings
- install the generated input-remapper preset
- set DPI/profile/slot via ratbagctl


```bash
logitux devices
```

### 2) Save button mapping (example: button 8 -> Ctrl+Alt+T)

```bash
logitux map-button "<device-id>" 8 "CTRL+ALT+T"
```

### 3) Generate an input-remapper preset from saved mappings

```bash
logitux install-preset "MX Master 3" "<device-id>"
```

Preset is written to:

```text
~/.config/input-remapper-2/presets/<device-name>/logitux.json
```

Then activate it with input-remapper GUI or CLI.

### 4) Set DPI with ratbagctl

```bash
logitux set-dpi "MX Master 3" 1200 --profile 0 --resolution-slot 0
```

## Notes for MX 4 / MX series on Nobara

- Ensure `input-remapper` service is installed/running.
- Ensure `libratbag` (`ratbagctl`) is installed.
- Device names must match exactly for `ratbagctl`.

## Run tests

```bash
pytest
```
