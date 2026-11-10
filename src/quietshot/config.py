"""Small, user-editable application configuration."""

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QStandardPaths

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class Settings:
    hotkey: str = "<ctrl>+<alt>+s"
    output_dir: str = ""


def config_path() -> Path:
    root = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
    return Path(root) / "settings.json"


def load_settings() -> Settings:
    path = config_path()
    if not path.exists():
        return Settings()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise TypeError("settings.json must contain an object")
        hotkey = data.get("hotkey", Settings.hotkey)
        output_dir = data.get("output_dir", "")
        if not isinstance(hotkey, str) or not isinstance(output_dir, str):
            raise TypeError("hotkey and output_dir must be strings")
        return Settings(hotkey=hotkey, output_dir=output_dir)
    except (OSError, TypeError, ValueError):
        LOG.exception("Cannot load settings from %s; using defaults", path)
        return Settings()


def save_settings(settings: Settings) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(settings.__dict__, indent=2), encoding="utf-8")
    temp.replace(path)

