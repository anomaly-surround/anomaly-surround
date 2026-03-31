"""Global hotkey manager for Anomaly Surround."""
import threading

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False


class HotkeyManager:
    def __init__(self):
        self.callbacks = {}
        self.registered = {}
        self.enabled = False

    def set_callback(self, action, callback):
        """Set callback for an action (e.g., 'toggle_surround')."""
        self.callbacks[action] = callback

    def register_all(self, hotkey_map):
        """Register all hotkeys from a {action: key_combo} dict."""
        if not KEYBOARD_AVAILABLE:
            return

        self.unregister_all()

        for action, combo in hotkey_map.items():
            if not combo or action not in self.callbacks:
                continue
            try:
                hook = keyboard.add_hotkey(combo, self.callbacks[action], suppress=False)
                self.registered[action] = (combo, hook)
            except Exception as e:
                print(f"Failed to register hotkey {combo} for {action}: {e}")

        self.enabled = True

    def unregister_all(self):
        """Remove all registered hotkeys."""
        if not KEYBOARD_AVAILABLE:
            return

        for action, (combo, hook) in self.registered.items():
            try:
                keyboard.remove_hotkey(hook)
            except Exception:
                pass

        self.registered.clear()
        self.enabled = False

    def update_hotkey(self, action, new_combo):
        """Update a single hotkey binding."""
        if not KEYBOARD_AVAILABLE:
            return

        # Remove old
        if action in self.registered:
            try:
                keyboard.remove_hotkey(self.registered[action][1])
            except Exception:
                pass
            del self.registered[action]

        # Register new
        if new_combo and action in self.callbacks:
            try:
                hook = keyboard.add_hotkey(new_combo, self.callbacks[action], suppress=False)
                self.registered[action] = (new_combo, hook)
            except Exception as e:
                print(f"Failed to register hotkey {new_combo}: {e}")

    def is_available(self):
        return KEYBOARD_AVAILABLE
