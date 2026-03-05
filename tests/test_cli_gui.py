import types
import sys

from logitux import app


def test_parse_args_gui():
    args = app.parse_args(["gui"])
    assert args.command == "gui"


def test_main_gui_invokes_runner(monkeypatch):
    called = {"ok": False}

    fake_module = types.SimpleNamespace(run_gui=lambda: called.__setitem__("ok", True))
    monkeypatch.setitem(sys.modules, "logitux.gui", fake_module)

    rc = app.main(["gui"])

    assert rc == 0
    assert called["ok"] is True
