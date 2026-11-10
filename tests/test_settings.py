from quietshot import config
from quietshot.config import Settings
from quietshot.shortcuts import to_pynput, to_qt


def test_shortcut_translation_and_validation():
    assert to_pynput("Ctrl+Alt+S") == "<ctrl>+<alt>+s"
    assert to_pynput("Meta+Shift+F12") == "<cmd>+<shift>+f12"
    assert to_qt("<ctrl>+<alt>+s") == "Ctrl+Alt+S"
    for invalid in ("S", "Ctrl+", "Ctrl+Alt+Space", "Ctrl+Ctrl+S"):
        try:
            to_pynput(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Expected invalid shortcut: {invalid}")


def test_settings_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "config_path", lambda: tmp_path / "settings.json")
    expected = Settings(hotkey="<ctrl>+<shift>+f2", output_dir=str(tmp_path / "shots"))
    config.save_settings(expected)
    assert config.load_settings() == expected
