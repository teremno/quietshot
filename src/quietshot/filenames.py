"""Generate readable, collision-safe screenshot names."""

from datetime import datetime
from pathlib import Path


def next_screenshot_path(directory: Path, now: datetime | None = None) -> Path:
    instant = now or datetime.now().astimezone()
    stem = f"QuietShot_{instant:%Y-%m-%d_%H-%M-%S}_{instant.microsecond // 1000:03d}"
    candidate = directory / f"{stem}.png"
    suffix = 2
    while candidate.exists():
        candidate = directory / f"{stem}_{suffix}.png"
        suffix += 1
    return candidate

