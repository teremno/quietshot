from datetime import datetime, timezone

from quietshot.filenames import next_screenshot_path


def test_timestamp_and_collision_suffix(tmp_path):
    instant = datetime(2026, 11, 10, 12, 34, 56, 123456, tzinfo=timezone.utc)
    first = next_screenshot_path(tmp_path, instant)
    assert first.name == "QuietShot_2026-11-10_12-34-56_123.png"
    first.touch()
    assert next_screenshot_path(tmp_path, instant).name == (
        "QuietShot_2026-11-10_12-34-56_123_2.png"
    )

