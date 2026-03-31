"""GUI interface for Anomaly Surround using tkinter."""
import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import threading
import os
import sys

from config import (
    load_settings, save_settings, load_profile, save_profile,
    list_profiles, GAME_PRESETS, DEFAULT_PROFILE, DEFAULT_EQ_BANDS, APP_NAME,
    DEFAULT_HOTKEY_LABELS
)
from hotkeys import HotkeyManager
from headphone_db import detect_headphone, get_corrected_eq
from audio_engine import (
    is_eqapo_installed, write_full_config, get_audio_devices,
    set_master_volume
)
from game_monitor import GameMonitor


# Fix DPI scaling - makes text and UI crisp on high-DPI displays
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


# Color scheme - clean dark
BG = "#101418"
BG_CARD = "#181c22"
BG_INPUT = "#22272e"
BG_HOVER = "#2a3038"
BORDER = "#2a2f38"
ACCENT = "#7c6bf0"
ACCENT_LIGHT = "#a89cf8"
GREEN = "#4ade80"
RED = "#f87171"
YELLOW = "#fbbf24"
TEXT = "#e8ecf0"
TEXT_DIM = "#6b7a8d"
TEXT_MID = "#9ba8b8"
FONT = "Segoe UI"


class SurroundApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("960x720")
        self.root.configure(bg=BG)
        self.root.minsize(860, 640)

        self.settings = load_settings()
        self.current_profile = load_profile(self.settings["active_profile"])
        self.eq_sliders = []
        self.game_monitor = None
        self.hotkey_manager = HotkeyManager()
        self.detected_headphone = detect_headphone(get_audio_devices())

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._configure_styles()
        self._build_ui()
        self._start_game_monitor()
        self._setup_hotkeys()
        self._update_status()

    def _configure_styles(self):
        s = self.style
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=BG_INPUT, foreground=TEXT_MID,
                    font=(FONT, 10, "bold"), padding=(18, 10))
        s.map("TNotebook.Tab",
              background=[("selected", BG_CARD)],
              foreground=[("selected", TEXT)])

        s.configure("Accent.TButton", background=ACCENT, foreground="white",
                    font=(FONT, 10, "bold"), padding=(18, 9), borderwidth=0)
        s.map("Accent.TButton", background=[("active", ACCENT_LIGHT)])

        s.configure("Dark.TButton", background=BG_INPUT, foreground=TEXT_MID,
                    font=(FONT, 9), padding=(12, 7), borderwidth=0)
        s.map("Dark.TButton", background=[("active", BG_HOVER)])

        s.configure("TCombobox", fieldbackground=BG_INPUT, background=BG_INPUT,
                    foreground=TEXT, selectbackground=ACCENT, borderwidth=0,
                    arrowcolor=TEXT_DIM)

    def _build_ui(self):
        # Header bar
        header = tk.Frame(self.root, bg=BG, height=56)
        header.pack(fill="x", padx=24, pady=(18, 0))
        header.pack_propagate(False)

        tk.Label(header, text=APP_NAME, font=(FONT, 17, "bold"),
                fg=TEXT, bg=BG).pack(side="left")

        tk.Label(header, text="7.1 Surround", font=(FONT, 10),
                fg=TEXT_DIM, bg=BG).pack(side="left", padx=(10, 0), pady=(4, 0))

        self.status_label = tk.Label(header, text="", font=(FONT, 10),
                                    fg=GREEN, bg=BG)
        self.status_label.pack(side="right")

        # Separator
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=24)

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=24, pady=(12, 24))

        self._build_main_tab()
        self._build_eq_tab()
        self._build_surround_tab()
        self._build_games_tab()
        self._build_hotkeys_tab()
        self._build_settings_tab()

    # --- Card helper ---
    def _card(self, parent, **kwargs):
        f = tk.Frame(parent, bg=BG_CARD, highlightbackground=BORDER,
                     highlightthickness=1, **kwargs)
        return f

    def _card_title(self, parent, text):
        tk.Label(parent, text=text, font=(FONT, 11, "bold"),
                fg=TEXT, bg=BG_CARD).pack(anchor="w", padx=20, pady=(18, 8))

    # ==================== MAIN TAB ====================
    def _build_main_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Main  ")

        # Profile
        card = self._card(tab)
        card.pack(fill="x", pady=(12, 6))

        self._card_title(card, "Profile")

        row = tk.Frame(card, bg=BG_CARD)
        row.pack(fill="x", padx=20, pady=(0, 18))

        profiles = list_profiles()
        self.profile_var = tk.StringVar(value=self.settings["active_profile"])
        self.profile_combo = ttk.Combobox(row, textvariable=self.profile_var,
                                          values=profiles, state="readonly", width=22,
                                          font=(FONT, 10))
        self.profile_combo.pack(side="left", padx=(0, 8))
        self.profile_combo.bind("<<ComboboxSelected>>", self._on_profile_change)

        ttk.Button(row, text="Apply", style="Accent.TButton",
                  command=self._apply_profile).pack(side="left", padx=4)
        ttk.Button(row, text="Save As...", style="Dark.TButton",
                  command=self._save_profile_as).pack(side="left", padx=4)

        # Toggles
        card2 = self._card(tab)
        card2.pack(fill="x", pady=6)

        self._card_title(card2, "Quick Controls")

        row2 = tk.Frame(card2, bg=BG_CARD)
        row2.pack(fill="x", padx=20, pady=(0, 18))

        self.surround_var = tk.BooleanVar(value=self.current_profile.get("surround_enabled", True))
        self.hrtf_var = tk.BooleanVar(value=self.current_profile.get("hrtf_enabled", True))
        self.eq_var = tk.BooleanVar(value=self.settings.get("eq_enabled", True))

        self._make_toggle(row2, "7.1 Surround", self.surround_var, self._toggle_surround)
        self._make_toggle(row2, "HRTF Spatial", self.hrtf_var, self._toggle_hrtf)
        self._make_toggle(row2, "Equalizer", self.eq_var, self._toggle_eq)

        # Volume
        card3 = self._card(tab)
        card3.pack(fill="x", pady=6)

        self._card_title(card3, "Master Volume")

        vol_row = tk.Frame(card3, bg=BG_CARD)
        vol_row.pack(fill="x", padx=20, pady=(0, 18))

        self.volume_var = tk.IntVar(value=self.settings.get("master_volume", 100))
        self.volume_label = tk.Label(vol_row, text=f"{self.volume_var.get()}%",
                                    font=(FONT, 13, "bold"), fg=TEXT, bg=BG_CARD, width=5)
        self.volume_label.pack(side="right")

        vol_scale = tk.Scale(vol_row, from_=0, to=100, orient="horizontal",
                           variable=self.volume_var, command=self._on_volume_change,
                           bg=BG_CARD, fg=TEXT, troughcolor=BG_INPUT,
                           highlightthickness=0, bd=0, sliderrelief="flat",
                           activebackground=ACCENT, showvalue=False)
        vol_scale.pack(side="left", fill="x", expand=True)

        # Status row
        status_row = tk.Frame(tab, bg=BG)
        status_row.pack(fill="x", pady=(6, 0))

        # EQ APO
        eqapo_card = self._card(status_row)
        eqapo_card.pack(side="left", fill="x", expand=True, padx=(0, 4))

        eqapo_ok = is_eqapo_installed()
        inner = tk.Frame(eqapo_card, bg=BG_CARD)
        inner.pack(fill="x", padx=20, pady=14)
        tk.Label(inner, text="Equalizer APO", font=(FONT, 10),
                fg=TEXT_MID, bg=BG_CARD).pack(side="left")
        tk.Label(inner, text="Installed" if eqapo_ok else "NOT INSTALLED",
                font=(FONT, 10, "bold"), fg=GREEN if eqapo_ok else RED,
                bg=BG_CARD).pack(side="right")

        # Game monitor
        game_card = self._card(status_row)
        game_card.pack(side="left", fill="x", expand=True, padx=(4, 0))

        inner2 = tk.Frame(game_card, bg=BG_CARD)
        inner2.pack(fill="x", padx=20, pady=14)
        tk.Label(inner2, text="Game Monitor", font=(FONT, 10),
                fg=TEXT_MID, bg=BG_CARD).pack(side="left")
        self.game_status_label = tk.Label(inner2, text="Scanning...",
                                         font=(FONT, 10), fg=TEXT_DIM, bg=BG_CARD)
        self.game_status_label.pack(side="right")

        # Audio device selector
        dev_card = self._card(tab)
        dev_card.pack(fill="x", pady=(6, 0))

        self._card_title(dev_card, "Audio Device")

        self.all_devices = get_audio_devices()
        # Filter to output devices only (exclude inputs like microphones)
        self.output_devices = [d for d in self.all_devices
                               if not any(kw in d["name"].lower() for kw in
                                         ["microphone", "mic", "line in", "stereo mix",
                                          "aux jack", "rear green", "rear blue",
                                          "rear pink", "front pink", "front green",
                                          "subwoofer", "center", "side", "rear (",
                                          "front ("])]
        device_names = [d["name"] for d in self.output_devices]

        saved_device = self.settings.get("selected_device", "")
        self.device_var = tk.StringVar(value=saved_device if saved_device in device_names else
                                      (device_names[0] if device_names else ""))

        self.device_combo = ttk.Combobox(dev_card, textvariable=self.device_var,
                                         values=device_names, state="readonly",
                                         font=(FONT, 10))
        self.device_combo.pack(fill="x", padx=20, pady=(0, 10))
        self.device_combo.bind("<<ComboboxSelected>>", self._on_device_change)

        hp_row = tk.Frame(dev_card, bg=BG_CARD)
        hp_row.pack(fill="x", padx=20, pady=(0, 14))

        self.hp_label = tk.Label(hp_row, text="", font=(FONT, 9, "bold"),
                                fg=GREEN, bg=BG_CARD)
        self.hp_label.pack(side="left")

        tk.Button(hp_row, text="Apply Correction", font=(FONT, 8, "bold"),
                 bg=ACCENT, fg="white", bd=0, padx=8, pady=3, cursor="hand2",
                 activebackground=ACCENT_LIGHT, activeforeground="white",
                 command=self._apply_headphone_correction).pack(side="right")

        self._update_hp_label()

    # ==================== EQ TAB ====================
    def _build_eq_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Equalizer  ")

        # Presets
        preset_row = tk.Frame(tab, bg=BG)
        preset_row.pack(fill="x", pady=(12, 8))

        tk.Label(preset_row, text="Presets", font=(FONT, 10),
                fg=TEXT_DIM, bg=BG).pack(side="left", padx=(0, 8))

        for name, preset in GAME_PRESETS.items():
            ttk.Button(preset_row, text=preset["name"], style="Dark.TButton",
                      command=lambda n=name: self._load_eq_preset(n)).pack(side="left", padx=3)

        ttk.Button(preset_row, text="Flat", style="Dark.TButton",
                  command=self._reset_eq).pack(side="left", padx=3)

        # EQ Card
        card = self._card(tab)
        card.pack(fill="both", expand=True, pady=6)

        # Preamp
        preamp_row = tk.Frame(card, bg=BG_CARD)
        preamp_row.pack(fill="x", padx=20, pady=(18, 8))

        tk.Label(preamp_row, text="Preamp", font=(FONT, 10),
                fg=TEXT_MID, bg=BG_CARD).pack(side="left")

        self.preamp_var = tk.DoubleVar(value=self.current_profile.get("preamp_gain", 0))
        self.preamp_label = tk.Label(preamp_row, text=f"{self.preamp_var.get():+.1f} dB",
                                    font=(FONT, 10, "bold"), fg=TEXT, bg=BG_CARD, width=8)
        self.preamp_label.pack(side="right")

        preamp_scale = tk.Scale(preamp_row, from_=-12, to=12, orient="horizontal",
                               variable=self.preamp_var, resolution=0.5,
                               command=lambda v: self._on_preamp_change(),
                               bg=BG_CARD, fg=TEXT, troughcolor=BG_INPUT,
                               highlightthickness=0, bd=0, showvalue=False)
        preamp_scale.pack(side="left", fill="x", expand=True, padx=12)

        # Separator
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=20, pady=4)

        # Band sliders
        sliders_frame = tk.Frame(card, bg=BG_CARD)
        sliders_frame.pack(fill="both", expand=True, padx=20, pady=(4, 8))

        # +12 / 0 / -12 labels
        label_col = tk.Frame(sliders_frame, bg=BG_CARD, width=30)
        label_col.pack(side="left", fill="y")
        label_col.pack_propagate(False)
        tk.Label(label_col, text="+12", font=(FONT, 8), fg=TEXT_DIM,
                bg=BG_CARD).pack(side="top", pady=(8, 0))
        tk.Label(label_col, text="0", font=(FONT, 8), fg=TEXT_DIM,
                bg=BG_CARD).place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(label_col, text="-12", font=(FONT, 8), fg=TEXT_DIM,
                bg=BG_CARD).pack(side="bottom", pady=(0, 24))

        bands = self.current_profile.get("eq_bands", DEFAULT_EQ_BANDS)
        self.eq_sliders = []

        for i, band in enumerate(bands):
            col = tk.Frame(sliders_frame, bg=BG_CARD)
            col.pack(side="left", fill="y", expand=True, padx=1)

            gain_var = tk.DoubleVar(value=band["gain"])
            gain_label = tk.Label(col, text=f"{band['gain']:+.0f}",
                                 font=(FONT, 9, "bold"), fg=ACCENT_LIGHT,
                                 bg=BG_CARD, width=4)
            gain_label.pack(pady=(4, 0))

            slider = tk.Scale(col, from_=12, to=-12, orient="vertical",
                            variable=gain_var, resolution=0.5,
                            command=lambda v, idx=i: self._on_eq_change(idx),
                            bg=BG_CARD, fg=TEXT, troughcolor=BG_INPUT,
                            highlightthickness=0, bd=0,
                            width=14, sliderlength=18, showvalue=False,
                            activebackground=ACCENT)
            slider.pack(fill="y", expand=True)

            freq_text = f"{band['freq']}" if band['freq'] < 1000 else f"{band['freq']//1000}k"
            tk.Label(col, text=freq_text, font=(FONT, 8),
                    fg=TEXT_DIM, bg=BG_CARD).pack(pady=(0, 4))

            self.eq_sliders.append({"var": gain_var, "label": gain_label, "freq": band["freq"]})

        # Apply
        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.pack(fill="x", padx=20, pady=(4, 16))
        ttk.Button(btn_row, text="Apply EQ", style="Accent.TButton",
                  command=self._apply_eq).pack(side="right")

    # ==================== SURROUND TAB ====================
    def _build_surround_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Surround  ")

        card = self._card(tab)
        card.pack(fill="both", expand=True, pady=12)

        self._card_title(card, "7.1 Channel Configuration")

        channels = [
            ("Stereo Width", "stereo_width", 70),
            ("Center Channel", "center_level", 100),
            ("LFE / Sub Bass", "lfe_level", 80),
            ("Rear Channels", "rear_level", 90),
            ("Side Channels", "side_level", 85),
            ("Room Size", "room_size", 50),
        ]

        self.surround_vars = {}

        for label_text, key, default in channels:
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill="x", padx=20, pady=5)

            tk.Label(row, text=label_text, font=(FONT, 10),
                    fg=TEXT, bg=BG_CARD, width=16, anchor="w").pack(side="left")

            var = tk.IntVar(value=self.current_profile.get(key, default))
            self.surround_vars[key] = var

            val_label = tk.Label(row, text=f"{var.get()}%", font=(FONT, 10, "bold"),
                               fg=ACCENT_LIGHT, bg=BG_CARD, width=5)
            val_label.pack(side="right")

            scale = tk.Scale(row, from_=0, to=100, orient="horizontal",
                           variable=var,
                           command=lambda v, lbl=val_label, vr=var: lbl.config(text=f"{vr.get()}%"),
                           bg=BG_CARD, fg=TEXT, troughcolor=BG_INPUT,
                           highlightthickness=0, bd=0, showvalue=False,
                           activebackground=ACCENT)
            scale.pack(side="left", fill="x", expand=True, padx=12)

        # Spatial audio
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=20, pady=12)

        spatial_row = tk.Frame(card, bg=BG_CARD)
        spatial_row.pack(fill="x", padx=20)

        tk.Label(spatial_row, text="Windows Spatial Audio", font=(FONT, 10),
                fg=TEXT_MID, bg=BG_CARD).pack(side="left")

        self.spatial_var = tk.StringVar(value=self.settings.get("spatial_audio", "windows_sonic"))
        for text, val in [("Off", "off"), ("Windows Sonic", "windows_sonic")]:
            rb = tk.Radiobutton(spatial_row, text=text, variable=self.spatial_var, value=val,
                              bg=BG_CARD, fg=TEXT, selectcolor=BG_INPUT,
                              activebackground=BG_CARD, activeforeground=TEXT,
                              font=(FONT, 10), indicatoron=1)
            rb.pack(side="left", padx=10)

        # Apply
        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.pack(fill="x", padx=20, pady=16)
        ttk.Button(btn_row, text="Apply Surround", style="Accent.TButton",
                  command=self._apply_surround).pack(side="right")

    # ==================== GAMES TAB ====================
    def _build_games_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Games  ")

        # Detection status
        card1 = self._card(tab)
        card1.pack(fill="x", pady=(12, 6))

        detect_row = tk.Frame(card1, bg=BG_CARD)
        detect_row.pack(fill="x", padx=20, pady=(14, 4))

        tk.Label(detect_row, text="Game Auto-Detection", font=(FONT, 11, "bold"),
                fg=TEXT, bg=BG_CARD).pack(side="left")

        self.game_detect_var = tk.BooleanVar(value=self.settings.get("game_detection", True))
        self.game_detect_btn = tk.Button(detect_row, text="ON" if self.game_detect_var.get() else "OFF",
                       font=(FONT, 9, "bold"), width=5, bd=0, cursor="hand2",
                       command=self._toggle_game_detection)
        self._style_toggle_btn(self.game_detect_btn, self.game_detect_var.get())
        self.game_detect_btn.pack(side="right")

        tk.Label(card1, text="Switches profile automatically when a game is detected.",
                font=(FONT, 9), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w", padx=20, pady=(0, 4))

        auto_apply_row = tk.Frame(card1, bg=BG_CARD)
        auto_apply_row.pack(fill="x", padx=20, pady=(0, 4))

        self.auto_apply_var = tk.BooleanVar(value=self.settings.get("auto_apply_on_game", True))
        tk.Checkbutton(auto_apply_row, text="Auto-apply EQ when game detected/closed",
                      variable=self.auto_apply_var, command=self._toggle_auto_apply,
                      bg=BG_CARD, fg=TEXT, selectcolor=BG_INPUT,
                      activebackground=BG_CARD, activeforeground=TEXT,
                      font=(FONT, 9)).pack(side="left")
        tk.Label(auto_apply_row, text="(disable if audio drops on game launch)",
                font=(FONT, 8), fg=TEXT_DIM, bg=BG_CARD).pack(side="left", padx=6)

        self.detected_label = tk.Label(card1, text="No games detected",
                                      font=(FONT, 10), fg=TEXT_DIM, bg=BG_CARD)
        self.detected_label.pack(anchor="w", padx=20, pady=(0, 16))

        # Add mapping
        card2 = self._card(tab)
        card2.pack(fill="x", pady=6)

        self._card_title(card2, "Add Game Mapping")

        input_row = tk.Frame(card2, bg=BG_CARD)
        input_row.pack(fill="x", padx=20, pady=(0, 16))

        tk.Label(input_row, text="EXE", font=(FONT, 9),
                fg=TEXT_DIM, bg=BG_CARD).pack(side="left", padx=(0, 6))
        self.game_exe_entry = tk.Entry(input_row, bg=BG_INPUT, fg=TEXT,
                                      insertbackground=TEXT, bd=0, relief="flat",
                                      font=(FONT, 10), width=24,
                                      highlightthickness=1, highlightcolor=ACCENT,
                                      highlightbackground=BORDER)
        self.game_exe_entry.pack(side="left", padx=(0, 12), ipady=6)

        tk.Label(input_row, text="Profile", font=(FONT, 9),
                fg=TEXT_DIM, bg=BG_CARD).pack(side="left", padx=(0, 6))
        self.game_profile_var = tk.StringVar(value="fps")
        ttk.Combobox(input_row, textvariable=self.game_profile_var,
                     values=list_profiles(), state="readonly", width=14,
                     font=(FONT, 10)).pack(side="left", padx=(0, 12))

        ttk.Button(input_row, text="Add", style="Accent.TButton",
                  command=self._add_game_mapping).pack(side="left")

        # Mappings list
        card3 = self._card(tab)
        card3.pack(fill="both", expand=True, pady=6)

        self._card_title(card3, "Game Mappings")

        list_container = tk.Frame(card3, bg=BG_CARD)
        list_container.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        scrollbar = tk.Scrollbar(list_container, bg=BG_INPUT, troughcolor=BG_CARD,
                                activebackground=BG_HOVER)
        scrollbar.pack(side="right", fill="y")

        self.games_listbox = tk.Listbox(list_container, bg=BG_INPUT, fg=TEXT,
                                        selectbackground=ACCENT, selectforeground="white",
                                        font=("Consolas", 10), bd=0,
                                        yscrollcommand=scrollbar.set, height=10,
                                        highlightthickness=0, relief="flat")
        self.games_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.games_listbox.yview)

        self._refresh_games_list()

    # ==================== SETTINGS TAB ====================
    # ==================== HOTKEYS TAB ====================
    def _build_hotkeys_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Hotkeys  ")

        # Enable toggle
        card_toggle = self._card(tab)
        card_toggle.pack(fill="x", pady=(12, 6))

        toggle_row = tk.Frame(card_toggle, bg=BG_CARD)
        toggle_row.pack(fill="x", padx=20, pady=14)

        self.hotkeys_enabled_var = tk.BooleanVar(
            value=self.settings.get("hotkeys_enabled", True))

        tk.Checkbutton(toggle_row, text="Enable Global Hotkeys",
                      variable=self.hotkeys_enabled_var,
                      command=self._toggle_hotkeys_enabled,
                      bg=BG_CARD, fg=TEXT, selectcolor=BG_INPUT,
                      activebackground=BG_CARD, activeforeground=TEXT,
                      font=(FONT, 11, "bold")).pack(side="left")

        if not self.hotkey_manager.is_available():
            tk.Label(toggle_row, text="(keyboard module not found)",
                    font=(FONT, 9), fg=RED, bg=BG_CARD).pack(side="left", padx=10)

        # Bindings card
        card = self._card(tab)
        card.pack(fill="both", expand=True, pady=6)

        self._card_title(card, "Key Bindings")
        tk.Label(card, text="Click a key field and press your desired shortcut. Use Ctrl, Alt, Shift + key.",
                font=(FONT, 9), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w", padx=20, pady=(0, 12))

        hotkeys = self.settings.get("hotkeys", {})
        self.hotkey_entries = {}

        bindings_frame = tk.Frame(card, bg=BG_CARD)
        bindings_frame.pack(fill="both", expand=True, padx=20)

        for action, label_text in DEFAULT_HOTKEY_LABELS.items():
            row = tk.Frame(bindings_frame, bg=BG_CARD)
            row.pack(fill="x", pady=4)

            tk.Label(row, text=label_text, font=(FONT, 10),
                    fg=TEXT, bg=BG_CARD, width=18, anchor="w").pack(side="left")

            current_key = hotkeys.get(action, "")

            key_var = tk.StringVar(value=current_key)
            entry = tk.Entry(row, textvariable=key_var, bg=BG_INPUT, fg=ACCENT_LIGHT,
                           insertbackground=TEXT, bd=0, relief="flat",
                           font=(FONT, 10), width=20,
                           highlightthickness=1, highlightbackground=BORDER,
                           highlightcolor=ACCENT, justify="center")
            entry.pack(side="left", padx=8, ipady=5)

            # Capture key press
            entry.bind("<FocusIn>", lambda e, ent=entry: ent.config(fg=YELLOW))
            entry.bind("<FocusOut>", lambda e, ent=entry: ent.config(fg=ACCENT_LIGHT))
            entry.bind("<Key>", lambda e, act=action, var=key_var, ent=entry:
                      self._capture_hotkey(e, act, var, ent))

            # Clear button
            tk.Button(row, text="Clear", font=(FONT, 8), bg=BG_INPUT, fg=TEXT_DIM,
                     bd=0, padx=8, pady=2, cursor="hand2",
                     activebackground=BG_HOVER, activeforeground=TEXT,
                     command=lambda a=action, v=key_var: self._clear_hotkey(a, v)
                     ).pack(side="left", padx=4)

            self.hotkey_entries[action] = key_var

        # Profile slot assignments
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=20, pady=12)

        self._card_title(card, "Profile Slot Assignments")
        tk.Label(card, text="Assign profiles to hotkey slots 1-4.",
                font=(FONT, 9), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w", padx=20, pady=(0, 8))

        slots_frame = tk.Frame(card, bg=BG_CARD)
        slots_frame.pack(fill="x", padx=20, pady=(0, 16))

        profiles = list_profiles()
        self.profile_slot_vars = {}

        for i in range(1, 5):
            slot_row = tk.Frame(slots_frame, bg=BG_CARD)
            slot_row.pack(fill="x", pady=3)

            tk.Label(slot_row, text=f"Slot {i}", font=(FONT, 10),
                    fg=TEXT_MID, bg=BG_CARD, width=8, anchor="w").pack(side="left")

            slot_key = f"profile_slot_{i}"
            current = self.settings.get("profile_slots", {}).get(str(i), "")

            slot_var = tk.StringVar(value=current)
            combo = ttk.Combobox(slot_row, textvariable=slot_var,
                               values=["(none)"] + profiles, state="readonly",
                               width=20, font=(FONT, 10))
            combo.pack(side="left", padx=8)
            if not current:
                combo.set("(none)")

            self.profile_slot_vars[i] = slot_var

        # Save button
        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.pack(fill="x", padx=20, pady=(4, 16))

        ttk.Button(btn_row, text="Save Hotkeys", style="Accent.TButton",
                  command=self._save_hotkeys).pack(side="right")

    def _capture_hotkey(self, event, action, var, entry):
        """Capture a key combo when the user presses keys in the entry field."""
        # Build combo string from the event
        parts = []
        if event.state & 0x4:
            parts.append("ctrl")
        if event.state & 0x8 or event.state & 0x20000:
            parts.append("alt")
        if event.state & 0x1:
            parts.append("shift")

        key = event.keysym.lower()

        # Skip modifier-only presses
        if key in ("control_l", "control_r", "alt_l", "alt_r",
                   "shift_l", "shift_r", "caps_lock", "meta_l", "meta_r"):
            return "break"

        # Map special keys
        key_map = {
            "up": "up", "down": "down", "left": "left", "right": "right",
            "return": "enter", "escape": "esc", "space": "space",
            "tab": "tab", "backspace": "backspace", "delete": "delete",
        }
        key = key_map.get(key, key)

        parts.append(key)
        combo = "+".join(parts)

        var.set(combo)
        entry.config(fg=ACCENT_LIGHT)

        return "break"

    def _clear_hotkey(self, action, var):
        var.set("")

    def _save_hotkeys(self):
        # Save key bindings
        hotkeys = {}
        for action, var in self.hotkey_entries.items():
            hotkeys[action] = var.get()
        self.settings["hotkeys"] = hotkeys
        self.settings["hotkeys_enabled"] = self.hotkeys_enabled_var.get()

        # Save profile slots
        slots = {}
        for i, var in self.profile_slot_vars.items():
            val = var.get()
            if val and val != "(none)":
                slots[str(i)] = val
        self.settings["profile_slots"] = slots

        save_settings(self.settings)

        # Re-register hotkeys
        self._setup_hotkeys()
        self._show_toast("Hotkeys saved")

    def _toggle_hotkeys_enabled(self):
        self.settings["hotkeys_enabled"] = self.hotkeys_enabled_var.get()
        save_settings(self.settings)
        if self.hotkeys_enabled_var.get():
            self._setup_hotkeys()
        else:
            self.hotkey_manager.unregister_all()
            self._show_toast("Hotkeys disabled")

    def _setup_hotkeys(self):
        """Register all global hotkeys."""
        if not self.hotkey_manager.is_available():
            return
        if not self.settings.get("hotkeys_enabled", True):
            return

        # Set callbacks
        self.hotkey_manager.set_callback("toggle_surround", self._hk_toggle_surround)
        self.hotkey_manager.set_callback("toggle_hrtf", self._hk_toggle_hrtf)
        self.hotkey_manager.set_callback("toggle_eq", self._hk_toggle_eq)
        self.hotkey_manager.set_callback("profile_1", lambda: self._hk_switch_profile(1))
        self.hotkey_manager.set_callback("profile_2", lambda: self._hk_switch_profile(2))
        self.hotkey_manager.set_callback("profile_3", lambda: self._hk_switch_profile(3))
        self.hotkey_manager.set_callback("profile_4", lambda: self._hk_switch_profile(4))
        self.hotkey_manager.set_callback("volume_up", self._hk_volume_up)
        self.hotkey_manager.set_callback("volume_down", self._hk_volume_down)

        hotkeys = self.settings.get("hotkeys", {})
        self.hotkey_manager.register_all(hotkeys)

    def _hk_toggle_surround(self):
        self.surround_var.set(not self.surround_var.get())
        self.current_profile["surround_enabled"] = self.surround_var.get()
        self._apply_current()
        state = "ON" if self.surround_var.get() else "OFF"
        self.root.after(0, lambda: self._show_toast(f"Surround {state}"))

    def _hk_toggle_hrtf(self):
        self.hrtf_var.set(not self.hrtf_var.get())
        self.current_profile["hrtf_enabled"] = self.hrtf_var.get()
        self._apply_current()
        state = "ON" if self.hrtf_var.get() else "OFF"
        self.root.after(0, lambda: self._show_toast(f"HRTF {state}"))

    def _hk_toggle_eq(self):
        self.eq_var.set(not self.eq_var.get())
        self.settings["eq_enabled"] = self.eq_var.get()
        save_settings(self.settings)
        self._apply_current()
        state = "ON" if self.eq_var.get() else "OFF"
        self.root.after(0, lambda: self._show_toast(f"EQ {state}"))

    def _hk_switch_profile(self, slot):
        slots = self.settings.get("profile_slots", {})
        profile_name = slots.get(str(slot))
        if not profile_name:
            return
        self.current_profile = load_profile(profile_name)
        self.settings["active_profile"] = profile_name
        save_settings(self.settings)
        self.root.after(0, lambda: self.profile_var.set(profile_name))
        self.root.after(0, self._refresh_eq_sliders)
        self.root.after(0, self._refresh_surround_sliders)
        self._apply_current()
        self.root.after(0, lambda: self._show_toast(f"Profile: {profile_name}"))

    def _hk_volume_up(self):
        level = min(100, self.volume_var.get() + 5)
        self.volume_var.set(level)
        self.root.after(0, lambda: self.volume_label.config(text=f"{level}%"))
        self.settings["master_volume"] = level
        set_master_volume(level)

    def _hk_volume_down(self):
        level = max(0, self.volume_var.get() - 5)
        self.volume_var.set(level)
        self.root.after(0, lambda: self.volume_label.config(text=f"{level}%"))
        self.settings["master_volume"] = level
        set_master_volume(level)

    def _build_settings_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Settings  ")

        # App settings
        card = self._card(tab)
        card.pack(fill="x", pady=(12, 6))

        self._card_title(card, "Application")

        self.autostart_var = tk.BooleanVar(value=self.settings.get("auto_start", False))
        tk.Checkbutton(card, text="Start with Windows",
                      variable=self.autostart_var, command=self._toggle_autostart,
                      bg=BG_CARD, fg=TEXT, selectcolor=BG_INPUT,
                      activebackground=BG_CARD, activeforeground=TEXT,
                      font=(FONT, 10)).pack(anchor="w", padx=20, pady=4)

        self.tray_var = tk.BooleanVar(value=self.settings.get("minimize_to_tray", True))
        tk.Checkbutton(card, text="Minimize to system tray",
                      variable=self.tray_var, command=self._toggle_tray,
                      bg=BG_CARD, fg=TEXT, selectcolor=BG_INPUT,
                      activebackground=BG_CARD, activeforeground=TEXT,
                      font=(FONT, 10)).pack(anchor="w", padx=20, pady=4)

        poll_row = tk.Frame(card, bg=BG_CARD)
        poll_row.pack(anchor="w", padx=20, pady=(8, 16))

        tk.Label(poll_row, text="Game scan interval (sec)", font=(FONT, 10),
                fg=TEXT, bg=BG_CARD).pack(side="left")

        self.poll_var = tk.IntVar(value=5)
        tk.Spinbox(poll_row, from_=2, to=30, textvariable=self.poll_var,
                  width=4, bg=BG_INPUT, fg=TEXT, font=(FONT, 10),
                  buttonbackground=BG_INPUT, bd=0, highlightthickness=1,
                  highlightbackground=BORDER).pack(side="left", padx=10)

        # Devices
        card2 = self._card(tab)
        card2.pack(fill="x", pady=6)

        self._card_title(card2, "Audio Devices")

        devices = get_audio_devices()
        for d in devices:
            tk.Label(card2, text=d['name'], font=(FONT, 10),
                    fg=TEXT_MID, bg=BG_CARD).pack(anchor="w", padx=20, pady=2)
        tk.Frame(card2, bg=BG_CARD, height=12).pack()

        # About
        card3 = self._card(tab)
        card3.pack(fill="x", pady=6)

        inner = tk.Frame(card3, bg=BG_CARD)
        inner.pack(fill="x", padx=20, pady=16)

        tk.Label(inner, text=APP_NAME, font=(FONT, 12, "bold"),
                fg=TEXT, bg=BG_CARD).pack(anchor="w")
        tk.Label(inner, text="7.1 Virtual Surround for HyperX Alpha S  |  Powered by Equalizer APO",
                font=(FONT, 9), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w", pady=(2, 0))

    # ==================== HELPERS ====================

    def _make_toggle(self, parent, text, var, command):
        btn = tk.Button(parent, text=text, font=(FONT, 10, "bold"),
                       width=14, height=2, bd=0, cursor="hand2",
                       command=lambda: self._do_toggle(var, btn, command))
        self._style_toggle_btn(btn, var.get())
        btn.pack(side="left", padx=6)

    def _do_toggle(self, var, btn, command):
        var.set(not var.get())
        self._style_toggle_btn(btn, var.get())
        command()

    def _style_toggle_btn(self, btn, is_on):
        if is_on:
            btn.config(bg=ACCENT, fg="white", activebackground=ACCENT_LIGHT, activeforeground="white")
        else:
            btn.config(bg=BG_INPUT, fg=TEXT_DIM, activebackground=BG_HOVER, activeforeground=TEXT_DIM)

    # ==================== ACTIONS ====================

    def _on_device_change(self, event=None):
        selected = self.device_var.get()
        self.settings["selected_device"] = selected
        save_settings(self.settings)
        # Re-detect headphone based on selected device
        selected_dev = [d for d in self.output_devices if d["name"] == selected]
        self.detected_headphone = detect_headphone(selected_dev) if selected_dev else None
        self._update_hp_label()
        self._show_toast(f"Device: {selected}")

    def _update_hp_label(self):
        if self.detected_headphone:
            self.hp_label.config(text=f"Detected: {self.detected_headphone['name']}", fg=GREEN)
        else:
            self.hp_label.config(text="Unknown device", fg=TEXT_DIM)

    def _apply_headphone_correction(self):
        if not self.detected_headphone:
            return
        base_eq = self.current_profile.get("eq_bands", DEFAULT_EQ_BANDS)
        corrected = get_corrected_eq(base_eq, self.detected_headphone)
        self.current_profile["eq_bands"] = corrected
        save_profile(self.settings["active_profile"], self.current_profile)
        self._refresh_eq_sliders()
        self._apply_current()
        self._show_toast(f"EQ corrected for {self.detected_headphone['name']}")

    def _on_profile_change(self, event=None):
        name = self.profile_var.get()
        self.current_profile = load_profile(name)
        self._refresh_eq_sliders()
        self._refresh_surround_sliders()

    def _apply_profile(self):
        name = self.profile_var.get()
        self.current_profile = load_profile(name)
        self.settings["active_profile"] = name
        save_settings(self.settings)

        if is_eqapo_installed():
            success, msg = write_full_config(self.current_profile)
            if success:
                self._show_toast(f"Profile '{name}' applied")
            else:
                messagebox.showerror("Error", msg)
        else:
            messagebox.showwarning("Warning", "Equalizer APO not installed.\nConfig saved but not applied.")

    def _save_profile_as(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Save Profile")
        dialog.geometry("320x180")
        dialog.configure(bg=BG_CARD)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Profile name", font=(FONT, 10),
                fg=TEXT_MID, bg=BG_CARD).pack(pady=(18, 6))

        name_entry = tk.Entry(dialog, bg=BG_INPUT, fg=TEXT, insertbackground=TEXT,
                            font=(FONT, 11), bd=0, relief="flat",
                            highlightthickness=1, highlightbackground=BORDER,
                            highlightcolor=ACCENT)
        name_entry.pack(padx=24, fill="x", ipady=6)
        name_entry.focus_set()

        def save():
            name = name_entry.get().strip()
            if name:
                save_profile(name, self.current_profile)
                self.profile_var.set(name)
                self.profile_combo["values"] = list_profiles()
                self.settings["active_profile"] = name
                save_settings(self.settings)
                dialog.destroy()
                self._show_toast(f"Profile '{name}' saved")

        ttk.Button(dialog, text="Save", style="Accent.TButton",
                  command=save).pack(pady=12)

    def _toggle_surround(self):
        self.current_profile["surround_enabled"] = self.surround_var.get()
        self._apply_current()

    def _toggle_hrtf(self):
        self.current_profile["hrtf_enabled"] = self.hrtf_var.get()
        self._apply_current()

    def _toggle_eq(self):
        self.settings["eq_enabled"] = self.eq_var.get()
        save_settings(self.settings)
        self._apply_current()

    def _on_volume_change(self, val):
        level = int(float(val))
        self.volume_label.config(text=f"{level}%")
        self.settings["master_volume"] = level
        # Debounce - only apply after user stops dragging
        if hasattr(self, '_vol_timer'):
            self.root.after_cancel(self._vol_timer)
        self._vol_timer = self.root.after(100, lambda: set_master_volume(level))

    def _on_preamp_change(self):
        self.preamp_label.config(text=f"{self.preamp_var.get():+.1f} dB")

    def _on_eq_change(self, idx):
        var = self.eq_sliders[idx]["var"]
        label = self.eq_sliders[idx]["label"]
        label.config(text=f"{var.get():+.0f}")

    def _apply_eq(self):
        bands = []
        for slider in self.eq_sliders:
            bands.append({"freq": slider["freq"], "gain": slider["var"].get(), "q": 1.0})
        self.current_profile["eq_bands"] = bands
        self.current_profile["preamp_gain"] = self.preamp_var.get()
        save_profile(self.settings["active_profile"], self.current_profile)
        self._apply_current()
        self._show_toast("EQ applied")

    def _apply_surround(self):
        for key, var in self.surround_vars.items():
            self.current_profile[key] = var.get()
        self.settings["spatial_audio"] = self.spatial_var.get()
        save_settings(self.settings)
        save_profile(self.settings["active_profile"], self.current_profile)
        self._apply_current()
        self._show_toast("Surround settings applied")

    def _load_eq_preset(self, name):
        if name in GAME_PRESETS:
            preset = GAME_PRESETS[name]
            bands = preset.get("eq_bands", DEFAULT_EQ_BANDS)
            for i, band in enumerate(bands):
                if i < len(self.eq_sliders):
                    self.eq_sliders[i]["var"].set(band["gain"])
                    self.eq_sliders[i]["label"].config(text=f"{band['gain']:+.0f}")
            self.preamp_var.set(preset.get("preamp_gain", 0))
            self.preamp_label.config(text=f"{self.preamp_var.get():+.1f} dB")

    def _reset_eq(self):
        for slider in self.eq_sliders:
            slider["var"].set(0)
            slider["label"].config(text="+0")
        self.preamp_var.set(0)
        self.preamp_label.config(text="+0.0 dB")

    def _refresh_eq_sliders(self):
        bands = self.current_profile.get("eq_bands", DEFAULT_EQ_BANDS)
        for i, band in enumerate(bands):
            if i < len(self.eq_sliders):
                self.eq_sliders[i]["var"].set(band["gain"])
                self.eq_sliders[i]["label"].config(text=f"{band['gain']:+.0f}")
        self.preamp_var.set(self.current_profile.get("preamp_gain", 0))
        self.preamp_label.config(text=f"{self.preamp_var.get():+.1f} dB")

    def _refresh_surround_sliders(self):
        for key, var in self.surround_vars.items():
            var.set(self.current_profile.get(key, 50))
        self.surround_var.set(self.current_profile.get("surround_enabled", True))
        self.hrtf_var.set(self.current_profile.get("hrtf_enabled", True))

    def _apply_current(self):
        if is_eqapo_installed():
            write_full_config(self.current_profile)

    def _add_game_mapping(self):
        exe = self.game_exe_entry.get().strip()
        profile = self.game_profile_var.get()
        if not exe:
            return
        if not exe.lower().endswith(".exe"):
            exe += ".exe"
        if "game_profiles" not in self.settings:
            self.settings["game_profiles"] = {}
        self.settings["game_profiles"][exe.lower()] = profile
        save_settings(self.settings)
        if self.game_monitor:
            self.game_monitor.add_game_mapping(exe, profile)
        self.game_exe_entry.delete(0, "end")
        self._refresh_games_list()
        self._show_toast(f"Added {exe} -> {profile}")

    def _refresh_games_list(self):
        self.games_listbox.delete(0, "end")
        from game_monitor import KNOWN_GAMES
        custom = self.settings.get("game_profiles", {})
        all_mappings = {**KNOWN_GAMES, **custom}
        for exe in sorted(all_mappings.keys()):
            marker = " [custom]" if exe in custom else ""
            self.games_listbox.insert("end", f"  {exe:<35} -> {all_mappings[exe]}{marker}")

    def _toggle_autostart(self):
        self.settings["auto_start"] = self.autostart_var.get()
        save_settings(self.settings)
        from cli import _set_windows_autostart
        _set_windows_autostart(self.autostart_var.get())

    def _toggle_tray(self):
        self.settings["minimize_to_tray"] = self.tray_var.get()
        save_settings(self.settings)

    # ==================== GAME MONITOR ====================

    def _toggle_auto_apply(self):
        self.settings["auto_apply_on_game"] = self.auto_apply_var.get()
        save_settings(self.settings)

    def _toggle_game_detection(self):
        self.game_detect_var.set(not self.game_detect_var.get())
        enabled = self.game_detect_var.get()
        self.settings["game_detection"] = enabled
        save_settings(self.settings)
        self._style_toggle_btn(self.game_detect_btn, enabled)
        self.game_detect_btn.config(text="ON" if enabled else "OFF")

        if enabled:
            if self.game_monitor and not self.game_monitor.running:
                self.game_monitor.start()
            self.game_status_label.config(text="Scanning...", fg=TEXT_DIM)
            self._show_toast("Game detection ON")
        else:
            if self.game_monitor and self.game_monitor.running:
                self.game_monitor.stop()
            self.game_status_label.config(text="Disabled", fg=TEXT_DIM)
            self.detected_label.config(text="Auto-detection disabled", fg=TEXT_DIM)
            self._show_toast("Game detection OFF")

    def _start_game_monitor(self):
        self.game_monitor = GameMonitor(
            on_game_detected=self._on_game_detected,
            on_game_closed=self._on_game_closed
        )
        custom = self.settings.get("game_profiles", {})
        for exe, profile in custom.items():
            self.game_monitor.add_game_mapping(exe, profile)
        if self.settings.get("game_detection", True):
            self.game_monitor.start()
        else:
            self.game_status_label.config(text="Disabled", fg=TEXT_DIM)

    def _on_game_detected(self, exe, profile_name):
        self.root.after(0, lambda: self._handle_game_detected(exe, profile_name))

    def _handle_game_detected(self, exe, profile_name):
        self.detected_label.config(text=f"Detected: {exe} -> {profile_name}", fg=GREEN)
        self.game_status_label.config(text=f"Playing: {exe}", fg=GREEN)
        self.current_profile = load_profile(profile_name)
        self.profile_var.set(profile_name)
        self._refresh_eq_sliders()
        self._refresh_surround_sliders()
        if self.settings.get("auto_apply_on_game", True):
            self._apply_current()
        self._show_toast(f"Switched to {profile_name}")

    def _on_game_closed(self, exe):
        self.root.after(0, lambda: self._handle_game_closed(exe))

    def _handle_game_closed(self, exe):
        self.detected_label.config(text=f"{exe} closed — reverted to default", fg=TEXT_DIM)
        self.game_status_label.config(text="No game detected", fg=TEXT_DIM)
        default_profile = self.settings.get("active_profile", "default")
        self.current_profile = load_profile(default_profile)
        self.profile_var.set(default_profile)
        self._refresh_eq_sliders()
        self._refresh_surround_sliders()
        if self.settings.get("auto_apply_on_game", True):
            self._apply_current()

    def _update_status(self):
        if is_eqapo_installed():
            self.status_label.config(text="Active", fg=GREEN)
        else:
            self.status_label.config(text="EQ APO Missing", fg=RED)

    def _show_toast(self, message):
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.attributes("-alpha", 0.95)

        x = self.root.winfo_x() + self.root.winfo_width() - 310
        y = self.root.winfo_y() + 70
        toast.geometry(f"280x38+{x}+{y}")
        toast.configure(bg=BG_CARD)

        tk.Label(toast, text=message, bg=BG_CARD, fg=YELLOW,
                font=(FONT, 10), padx=14, pady=8).pack(fill="both", expand=True)

        toast.after(2000, toast.destroy)

    # ==================== SYSTEM TRAY ====================

    def _setup_tray(self):
        self._tray_icon = None
        self.root.bind("<Unmap>", self._on_minimize)

    def _on_minimize(self, event=None):
        if not self.tray_var.get():
            return
        if self.root.state() == "iconic":
            self.root.withdraw()
            self._show_tray_icon()

    def _create_tray_image(self):
        from PIL import Image, ImageDraw
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([4, 4, 60, 60], radius=12, fill="#7c3aed")
        draw.text((18, 12), "A", fill="white")
        return img

    def _show_tray_icon(self):
        if self._tray_icon is not None:
            return

        import pystray

        menu = pystray.Menu(
            pystray.MenuItem("Open", self._tray_restore, default=True),
            pystray.MenuItem("Quit", self._tray_quit),
        )

        self._tray_icon = pystray.Icon(
            APP_NAME, self._create_tray_image(), APP_NAME, menu
        )

        threading.Thread(target=self._tray_icon.run, daemon=True).start()

    def _tray_restore(self, icon=None, item=None):
        if self._tray_icon:
            self._tray_icon.stop()
            self._tray_icon = None
        self.root.after(0, self._do_restore)

    def _do_restore(self):
        self.root.deiconify()
        self.root.state("normal")
        self.root.lift()
        self.root.focus_force()

    def _tray_quit(self, icon=None, item=None):
        if self._tray_icon:
            self._tray_icon.stop()
            self._tray_icon = None
        self.hotkey_manager.unregister_all()
        if self.game_monitor:
            self.game_monitor.stop()
        save_settings(self.settings)
        import os
        os._exit(0)

    def on_close(self):
        if self.tray_var.get():
            self.root.withdraw()
            self._show_tray_icon()
        else:
            self._force_close()

    def _force_close(self):
        self.hotkey_manager.unregister_all()
        if self._tray_icon:
            self._tray_icon.stop()
            self._tray_icon = None
        if self.game_monitor:
            self.game_monitor.stop()
        save_settings(self.settings)
        self.root.destroy()


def run_gui():
    root = tk.Tk()
    app = SurroundApp(root)
    app._setup_tray()
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
