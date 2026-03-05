from pathlib import Path

from logitux import app


def test_build_preset_sorts_buttons():
    preset = app.build_input_remapper_preset("MX Master", {"9": "CTRL+T", "8": "ALT+TAB"})
    assert preset["mapping"][0]["input"]["code"] == 8
    assert preset["mapping"][0]["output"]["keys"] == "ALT+TAB"


def test_mapping_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(app, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(app, "CONFIG_FILE", tmp_path / "profiles.json")

    app.set_button_mapping("abc", "8", "CTRL+ALT+T")
    data = app.load_profiles()

    assert data["mappings"]["abc"]["8"] == "CTRL+ALT+T"


def test_install_input_remapper_preset(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setattr(Path, "home", lambda: home)
    monkeypatch.setattr(app, "CONFIG_DIR", home / ".config" / "logitux")
    monkeypatch.setattr(app, "CONFIG_FILE", home / ".config" / "logitux" / "profiles.json")

    app.set_button_mapping("dev-1", "8", "CTRL+ALT+T")
    output = app.install_input_remapper_preset("MX Master 3", "dev-1")

    assert output.exists()
    assert output.read_text(encoding="utf-8").find("CTRL+ALT+T") > 0
