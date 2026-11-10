# QuietShot

A small screenshot utility for people who share screen details with colleagues and AI agents. Click the movable, translucent camera button or press `Ctrl+Alt+S`, select an area, add annotations, then copy or save a full-resolution PNG.

## Features

- Floating, draggable button; right-click for capture or quit.
- Global hotkey and optional system tray menu.
- Select a region on the monitor under the pointer.
- Red arrows, rectangles, freehand marks, and solid covers for private details.
- Undo, copy to clipboard, and save as PNG at the source pixel dimensions.
- Timestamped filenames with millisecond precision and a collision suffix.

## Install and run

Requires Python 3.10 or newer.

```bash
python -m venv .venv
# Activate .venv using your shell, then:
python -m pip install -e .
python -m quietshot
```

On Windows PowerShell, activation is `.venv\Scripts\Activate.ps1`. On macOS/Linux, use `source .venv/bin/activate`.

The default save folder is `~/Pictures/QuietShot`. You can change the hotkey and default folder in the settings file at the location returned by Qt's `AppConfigLocation` for QuietShot:

```json
{
  "hotkey": "<ctrl>+<alt>+s",
  "output_dir": "~/Pictures/QuietShot"
}
```

`pynput` hotkey syntax is used. Restart QuietShot after editing the file.

## Platform status

| Platform | Capture | Global hotkey | Notes |
| --- | --- | --- | --- |
| Windows 11 | Qt screen capture | `pynput` | Initial development platform |
| macOS | Qt screen capture | `pynput` | Grant Screen Recording and Accessibility permissions if requested by macOS |
| Linux X11 | Qt screen capture | `pynput` | Requires an active graphical session |
| Linux Wayland | Qt screen capture via PipeWire/desktop portal | Floating button | Experimental; the OS asks which display to share. Global hotkeys and always-on-top behavior depend on the compositor. |

Platform rows describe the implementation path, not completed device testing. Automated CI checks run on all three operating systems; interactive capture and permissions still need manual validation on each one.

## Architecture

- `capture.py`: synchronous Qt capture on Windows/macOS/X11 and a separate asynchronous Qt/portal adapter for Linux Wayland.
- `hotkeys.py`: global hotkey boundary.
- `selection.py`: pixel-correct region selection.
- `annotations.py`: image-space annotations and original-size export.
- `editor.py`: annotation UI and save/copy workflow.
- `floating.py`: movable always-on-top trigger.
- `app.py`: coordinates the workflow and tray.
- `filenames.py`: timestamp and collision-safe names.

## Development

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m pytest -q
```

## Known limitations

- Linux Wayland capture is experimental and needs a working PipeWire/desktop portal. Its global hotkey may not work; the floating button remains the primary trigger.
- The first version captures the monitor under the pointer; cross-monitor selections are not yet supported.
- Protected content and some applications may intentionally appear blank because of operating-system capture restrictions.
- No packaged installers or signed binaries yet. Run from Python for now.

## License

MIT. See [LICENSE](LICENSE).
