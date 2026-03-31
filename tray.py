"""System tray integration for background mode."""
import threading
import os
import sys

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

from config import load_settings, save_settings, load_profile, APP_NAME
from audio_engine import write_full_config, is_eqapo_installed
from game_monitor import GameMonitor


def create_tray_icon():
    """Create the tray icon image."""
    from icon import create_icon
    return create_icon(64)


class TrayApp:
    def __init__(self):
        self.settings = load_settings()
        self.game_monitor = None
        self.icon = None

    def _on_game_detected(self, exe, profile_name):
        profile = load_profile(profile_name)
        if is_eqapo_installed():
            write_full_config(profile)
        if self.icon:
            self.icon.notify(f"Switched to {profile_name} profile", APP_NAME)

    def _on_game_closed(self, exe):
        default_name = self.settings.get("active_profile", "default")
        profile = load_profile(default_name)
        if is_eqapo_installed():
            write_full_config(profile)

    def _open_gui(self, icon, item):
        """Open the GUI window."""
        from gui import run_gui
        threading.Thread(target=run_gui, daemon=True).start()

    def _toggle_surround(self, icon, item):
        profile = load_profile(self.settings["active_profile"])
        profile["surround_enabled"] = not profile.get("surround_enabled", True)
        if is_eqapo_installed():
            write_full_config(profile)

    def _quit(self, icon, item):
        if self.game_monitor:
            self.game_monitor.stop()
        icon.stop()

    def run(self):
        if not TRAY_AVAILABLE:
            print("System tray not available (install pystray and Pillow)")
            return

        # Start game monitor
        self.game_monitor = GameMonitor(
            on_game_detected=self._on_game_detected,
            on_game_closed=self._on_game_closed
        )
        custom = self.settings.get("game_profiles", {})
        for exe, profile in custom.items():
            self.game_monitor.add_game_mapping(exe, profile)
        self.game_monitor.start()

        # Apply current profile on start
        profile = load_profile(self.settings["active_profile"])
        if is_eqapo_installed():
            write_full_config(profile)

        # Create tray icon
        menu = pystray.Menu(
            pystray.MenuItem("Open", self._open_gui, default=True),
            pystray.MenuItem("Toggle Surround", self._toggle_surround),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._quit),
        )

        self.icon = pystray.Icon(APP_NAME, create_tray_icon(), APP_NAME, menu)
        self.icon.run()


def run_tray():
    app = TrayApp()
    app.run()
