"""Translate one Qt shortcut chord to pynput's global-hotkey syntax."""

_TO_PYNPUT = {"Ctrl": "<ctrl>", "Alt": "<alt>", "Shift": "<shift>", "Meta": "<cmd>"}
_FROM_PYNPUT = {value: key for key, value in _TO_PYNPUT.items()}


def to_pynput(portable_text: str) -> str:
    """Accept a modifier plus A-Z, 0-9, or F1-F12."""
    parts = [part.strip() for part in portable_text.split("+")]
    if len(parts) < 2 or not parts[-1]:
        raise ValueError("Press a modifier and a letter, digit, or F1–F12 key.")
    modifiers = parts[:-1]
    if not modifiers or any(part not in _TO_PYNPUT for part in modifiers):
        raise ValueError("Use Ctrl, Alt, Shift, or Meta with one key.")
    key = parts[-1].upper()
    valid_key = (len(key) == 1 and key.isascii() and key.isalnum()) or (
        key.startswith("F") and key[1:].isdigit() and 1 <= int(key[1:]) <= 12
    )
    if not valid_key:
        raise ValueError("Use a letter, digit, or F1–F12 as the final key.")
    if len(set(modifiers)) != len(modifiers):
        raise ValueError("A modifier cannot be used twice.")
    return "+".join([*(_TO_PYNPUT[part] for part in modifiers), key.lower()])


def to_qt(hotkey: str) -> str:
    parts = hotkey.split("+")
    if len(parts) < 2 or any(part not in _FROM_PYNPUT for part in parts[:-1]):
        return "Ctrl+Alt+S"
    return "+".join([*(_FROM_PYNPUT[part] for part in parts[:-1]), parts[-1].upper()])

