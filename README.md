# QuietShot

A small screenshot utility for people who share screen details with colleagues and AI agents. Click the movable, translucent camera button or press `Ctrl+Alt+S`, select an area, add annotations, then copy or save a full-resolution PNG.

## Features

- Floating, draggable button; right-click for capture, settings, or quit.
- Global hotkey and optional system tray menu.
- Settings window for the shortcut and save folder; changes apply immediately.
- Select a region on the monitor under the pointer.
- Arrows, rectangles, and freehand marks with six preset colors, a custom color picker, and 1–20 px thickness. Covers for private details stay solid black.
- Undo, copy to clipboard, and save as PNG at the source pixel dimensions.
- The editor closes after a successful PNG save; cancelling the save dialog keeps it open.
- The next Save PNG dialog starts in the folder used for the last successful save, even after restarting QuietShot.
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

The default save folder is `~/Pictures/QuietShot`. Open **Settings…** from the button's right-click menu or the tray menu to change the shortcut and initial folder. After a successful save, the last used folder takes precedence. Preferences and the recent folder are stored as separate JSON files in Qt's `AppConfigLocation` for QuietShot:

```json
{
  "hotkey": "<ctrl>+<alt>+s",
  "output_dir": "~/Pictures/QuietShot"
}
```

The settings window records one shortcut with a modifier plus a letter, digit, or F1–F12. Advanced users can also edit the JSON using `pynput` hotkey syntax, then restart QuietShot.

## Installers

Download the installer for your OS from [GitHub Releases](https://github.com/teremno/quietshot/releases) when a release is available:

- Windows x64: `QuietShot-*-Windows-x64-Setup.exe` installs for the current user and adds an uninstaller.
- macOS Apple Silicon or Intel: choose the matching `.dmg`, open it, and drag QuietShot to Applications.
- Linux x64: install the `.deb` with your package manager. It includes a desktop launcher.

These packages include Python and app dependencies. The Windows and macOS packages are currently unsigned, so the OS may show a publisher warning. Linux builds target Ubuntu 22.04 x64 for broad glibc compatibility, but other distributions are not yet verified.

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
- `settings_dialog.py`: user-facing preferences.
- `save_location.py`: recent save destination, persisted separately from preferences.
- `installers/`: platform package definitions; `package.yml` builds each OS on its own runner.

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
- The macOS and Windows installers are not code-signed or notarized yet.

## License

MIT. See [LICENSE](LICENSE).
