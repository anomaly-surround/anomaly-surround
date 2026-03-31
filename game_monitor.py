"""Game process monitor - detects running games and auto-switches profiles."""
import threading
import time
import psutil


# Common game executables mapped to profile types
KNOWN_GAMES = {
    # FPS
    "valorant.exe": "fps",
    "csgo.exe": "fps",
    "cs2.exe": "fps",
    "overwatch.exe": "fps",
    "r5apex.exe": "fps",  # Apex Legends
    "cod.exe": "fps",
    "modernwarfare.exe": "fps",
    "destiny2.exe": "fps",
    "fortnite.exe": "fps",
    "pubg.exe": "fps",
    "rainbow6.exe": "fps",
    "tarkov.exe": "fps",
    "escapefromtarkov.exe": "fps",
    "hunt.exe": "fps",
    "deadbydaylight.exe": "fps",

    # RPG / Immersive
    "witcher3.exe": "rpg",
    "cyberpunk2077.exe": "rpg",
    "eldenring.exe": "rpg",
    "baldursgate3.exe": "rpg",
    "bg3.exe": "rpg",
    "skyrim.exe": "rpg",
    "skyrimse.exe": "rpg",
    "fallout4.exe": "rpg",
    "starfield.exe": "rpg",
    "hogwartslegacy.exe": "rpg",
    "darksouls3.exe": "rpg",
    "gta5.exe": "rpg",
    "rdr2.exe": "rpg",
    "ffxiv.exe": "rpg",
    "ffxiv_dx11.exe": "rpg",
    "wow.exe": "rpg",
    "guildwars2.exe": "rpg",
    "lostark.exe": "rpg",

    # MOBA / Strategy (use rpg profile for rich audio)
    "league of legends.exe": "rpg",
    "dota2.exe": "rpg",

    # Music / Media
    "spotify.exe": "music",
    "itunes.exe": "music",
}


class GameMonitor:
    def __init__(self, on_game_detected=None, on_game_closed=None):
        self.on_game_detected = on_game_detected
        self.on_game_closed = on_game_closed
        self.current_game = None
        self.current_profile = None
        self.running = False
        self.thread = None
        self.custom_mappings = {}
        self.poll_interval = 5  # seconds

    def add_game_mapping(self, exe_name, profile_name):
        """Add a custom game-to-profile mapping."""
        self.custom_mappings[exe_name.lower()] = profile_name

    def remove_game_mapping(self, exe_name):
        """Remove a custom game-to-profile mapping."""
        self.custom_mappings.pop(exe_name.lower(), None)

    def get_all_mappings(self):
        """Get combined built-in + custom mappings."""
        mappings = dict(KNOWN_GAMES)
        mappings.update(self.custom_mappings)
        return mappings

    def _scan_processes(self):
        """Scan running processes for known games."""
        mappings = self.get_all_mappings()
        for proc in psutil.process_iter(["name"]):
            try:
                name = proc.info["name"]
                if name and name.lower() in mappings:
                    return name.lower(), mappings[name.lower()]
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None, None

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            game_exe, profile = self._scan_processes()

            if game_exe and game_exe != self.current_game:
                self.current_game = game_exe
                self.current_profile = profile
                if self.on_game_detected:
                    self.on_game_detected(game_exe, profile)

            elif not game_exe and self.current_game:
                old_game = self.current_game
                self.current_game = None
                self.current_profile = None
                if self.on_game_closed:
                    self.on_game_closed(old_game)

            time.sleep(self.poll_interval)

    def start(self):
        """Start monitoring."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop monitoring."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
            self.thread = None

    def get_running_games(self):
        """Get list of currently detected games."""
        games = []
        mappings = self.get_all_mappings()
        for proc in psutil.process_iter(["name"]):
            try:
                name = proc.info["name"]
                if name and name.lower() in mappings:
                    games.append({
                        "exe": name.lower(),
                        "profile": mappings[name.lower()],
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return games
