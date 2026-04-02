"""Configuration management for surround sound app."""
import json
import os

APP_NAME = "Anomaly Surround"
CONFIG_DIR = os.path.join(os.environ.get("APPDATA", ""), APP_NAME)
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")
PROFILES_DIR = os.path.join(CONFIG_DIR, "profiles")
EQAPO_CONFIG_DIR = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "EqualizerAPO", "config")
EQAPO_MAIN_CONFIG = os.path.join(EQAPO_CONFIG_DIR, "config.txt")

DEFAULT_SETTINGS = {
    "auto_start": False,
    "minimize_to_tray": True,
    "active_profile": "default",
    "surround_enabled": True,
    "hrtf_enabled": True,
    "eq_enabled": True,
    "master_volume": 100,
    "game_profiles": {},
    "spatial_audio": "windows_sonic",
    "hotkeys_enabled": True,
    "hotkeys": {
        "toggle_surround": "ctrl+alt+s",
        "toggle_hrtf": "ctrl+alt+h",
        "toggle_eq": "ctrl+alt+e",
        "profile_1": "ctrl+alt+1",
        "profile_2": "ctrl+alt+2",
        "profile_3": "ctrl+alt+3",
        "profile_4": "ctrl+alt+4",
        "volume_up": "ctrl+alt+up",
        "volume_down": "ctrl+alt+down",
    },
}

DEFAULT_HOTKEY_LABELS = {
    "toggle_surround": "Toggle Surround",
    "toggle_hrtf": "Toggle HRTF",
    "toggle_eq": "Toggle Equalizer",
    "profile_1": "Profile Slot 1",
    "profile_2": "Profile Slot 2",
    "profile_3": "Profile Slot 3",
    "profile_4": "Profile Slot 4",
    "volume_up": "Volume Up",
    "volume_down": "Volume Down",
}

DEFAULT_EQ_BANDS = [
    {"freq": 31, "gain": 0, "q": 1.0},
    {"freq": 62, "gain": 0, "q": 1.0},
    {"freq": 125, "gain": 0, "q": 1.0},
    {"freq": 250, "gain": 0, "q": 1.0},
    {"freq": 500, "gain": 0, "q": 1.0},
    {"freq": 1000, "gain": 0, "q": 1.0},
    {"freq": 2000, "gain": 0, "q": 1.0},
    {"freq": 4000, "gain": 0, "q": 1.0},
    {"freq": 8000, "gain": 0, "q": 1.0},
    {"freq": 16000, "gain": 0, "q": 1.0},
]

DEFAULT_PROFILE = {
    "name": "Default",
    "eq_bands": DEFAULT_EQ_BANDS,
    "surround_enabled": True,
    "hrtf_enabled": True,
    "room_size": 50,
    "stereo_width": 70,
    "center_level": 100,
    "lfe_level": 80,
    "rear_level": 90,
    "side_level": 85,
    "preamp_gain": 0,
}

# Game presets
GAME_PRESETS = {
    "fps": {
        "name": "FPS Competitive",
        "eq_bands": [
            {"freq": 31, "gain": -2, "q": 1.0},
            {"freq": 62, "gain": -1, "q": 1.0},
            {"freq": 125, "gain": 0, "q": 1.0},
            {"freq": 250, "gain": 1, "q": 1.0},
            {"freq": 500, "gain": 2, "q": 1.0},
            {"freq": 1000, "gain": 3, "q": 1.0},
            {"freq": 2000, "gain": 4, "q": 1.0},
            {"freq": 4000, "gain": 5, "q": 0.8},
            {"freq": 8000, "gain": 3, "q": 1.0},
            {"freq": 16000, "gain": 1, "q": 1.0},
        ],
        "surround_enabled": True,
        "hrtf_enabled": True,
        "room_size": 30,
        "stereo_width": 90,
        "center_level": 100,
        "lfe_level": 50,
        "rear_level": 100,
        "side_level": 95,
        "preamp_gain": -3,
    },
    "rpg": {
        "name": "RPG / Immersive",
        "eq_bands": [
            {"freq": 31, "gain": 3, "q": 1.0},
            {"freq": 62, "gain": 4, "q": 1.0},
            {"freq": 125, "gain": 2, "q": 1.0},
            {"freq": 250, "gain": 1, "q": 1.0},
            {"freq": 500, "gain": 0, "q": 1.0},
            {"freq": 1000, "gain": 0, "q": 1.0},
            {"freq": 2000, "gain": 1, "q": 1.0},
            {"freq": 4000, "gain": 2, "q": 1.0},
            {"freq": 8000, "gain": 3, "q": 1.0},
            {"freq": 16000, "gain": 2, "q": 1.0},
        ],
        "surround_enabled": True,
        "hrtf_enabled": True,
        "room_size": 70,
        "stereo_width": 80,
        "center_level": 100,
        "lfe_level": 90,
        "rear_level": 85,
        "side_level": 80,
        "preamp_gain": -2,
    },
    "music": {
        "name": "Music",
        "eq_bands": [
            {"freq": 31, "gain": 2, "q": 1.0},
            {"freq": 62, "gain": 3, "q": 1.0},
            {"freq": 125, "gain": 1, "q": 1.0},
            {"freq": 250, "gain": 0, "q": 1.0},
            {"freq": 500, "gain": 0, "q": 1.0},
            {"freq": 1000, "gain": 0, "q": 1.0},
            {"freq": 2000, "gain": 1, "q": 1.0},
            {"freq": 4000, "gain": 2, "q": 1.0},
            {"freq": 8000, "gain": 3, "q": 1.0},
            {"freq": 16000, "gain": 2, "q": 1.0},
        ],
        "surround_enabled": False,
        "hrtf_enabled": False,
        "room_size": 40,
        "stereo_width": 60,
        "center_level": 100,
        "lfe_level": 80,
        "rear_level": 70,
        "side_level": 70,
        "preamp_gain": 0,
    },
}


def ensure_dirs():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(PROFILES_DIR, exist_ok=True)


def load_settings():
    ensure_dirs()
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            saved = json.load(f)
            settings = {**DEFAULT_SETTINGS, **saved}
            return settings
    return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    ensure_dirs()
    with open(CONFIG_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def _validate_name(name):
    """Validate profile/game name — alphanumeric, underscore, dash, space only."""
    import re
    if not name or not re.match(r'^[a-zA-Z0-9_\- ]+$', name):
        raise ValueError(f"Invalid name: {name}")
    return name.strip()


def load_profile(name):
    name = _validate_name(name)
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    # Ensure resolved path is within PROFILES_DIR
    if not os.path.realpath(path).startswith(os.path.realpath(PROFILES_DIR)):
        raise ValueError(f"Invalid profile path: {name}")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    if name in GAME_PRESETS:
        return dict(GAME_PRESETS[name])
    return dict(DEFAULT_PROFILE)


def save_profile(name, profile):
    name = _validate_name(name)
    ensure_dirs()
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    if not os.path.realpath(path).startswith(os.path.realpath(PROFILES_DIR)):
        raise ValueError(f"Invalid profile path: {name}")
    with open(path, "w") as f:
        json.dump(profile, f, indent=2)


def list_profiles():
    ensure_dirs()
    profiles = ["default"]
    profiles.extend(GAME_PRESETS.keys())
    if os.path.exists(PROFILES_DIR):
        for f in os.listdir(PROFILES_DIR):
            if f.endswith(".json"):
                name = f[:-5]
                if name not in profiles:
                    profiles.append(name)
    return profiles
