"""Remember the last successful screenshot destination across app restarts."""

import json
import logging
from pathlib import Path

from quietshot.config import config_path

LOG = logging.getLogger(__name__)


class SaveLocationStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or config_path().with_name("state.json")
        self._last_dir = self._read()

    def preferred_dir(self, fallback: Path) -> Path:
        """Prefer the last existing destination, otherwise use the configured default."""
        if self._last_dir is not None and self._last_dir.is_dir():
            return self._last_dir
        return fallback

    def remember(self, directory: Path) -> None:
        """Update memory first so the current session works even if disk writing fails."""
        self._last_dir = directory
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps({"last_save_dir": str(directory)}, indent=2), encoding="utf-8"
        )
        temporary.replace(self.path)

    def _read(self) -> Path | None:
        if not self.path.exists():
            return None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            value = data.get("last_save_dir") if isinstance(data, dict) else None
            if not isinstance(value, str) or not value:
                raise ValueError("state.json has no valid last_save_dir")
            return Path(value)
        except (OSError, ValueError):
            LOG.exception("Cannot load recent save location from %s", self.path)
            return None
