# Floating button recovery (0.3.1)

## Cause confirmed in source and regression checks

Capture hides the floating button before displaying the selection overlay. Previously only Escape emitted `cancelled`. Closing the selector through the window manager (for example Alt+F4) left the overlay reference set and the floating button hidden. Subsequent captures were rejected as busy. The process and tray stayed alive, which made restarting appear necessary.

The button also accepted coordinates outside all available screens. The tray's Show action only called `show()`, leaving an off-screen or minimized window unreachable. There was no idle recovery after desktop/window stacking or display changes. These are confirmed failure paths; the user's original intermittent event was not recorded, so its exact trigger cannot be established retrospectively.

## Fix

- Handle cancellation in the selector's close event. A successful selection marks completion before emitting its image, so closing it does not cancel the editor.
- Keep the entire button within an available screen after dragging and during recovery. Disconnected-monitor coordinates are moved back to the nearest available desktop area.
- Centralize show/hide intent in `ButtonVisibility`. Every two seconds while idle, restore the button, clear minimized state, and raise it without requesting keyboard activation. Pause recovery during capture, editing, dragging, popup menus, and modal dialogs.
- Respect explicit Hide from the tray. Show now repairs visibility and coordinates.
- Keep macOS tool windows visible when the app is inactive.
- Handle unexpected capture/selector/editor construction failures at the application boundary, log the traceback, release capture state, and show a retryable error.

## Verification and limits

Regression tests cover window-manager close, Escape, successful selection/editor completion, hidden/minimized/off-screen recovery, explicit hiding, and an unexpected capture failure. Existing save, recent-folder, and annotation checks remain in the suite. CI runs on Windows, Linux, and macOS; package smoke checks run on all four installer targets.

Offscreen tests cannot prove behavior of Windows Show Desktop, sleep/wake, physical monitor disconnection, exclusive fullscreen apps, or macOS Spaces. These remain manual desktop checks. Wayland compositor restrictions still apply. Recovery is limited to normal desktop windows and never attempts to cover secure system screens.
