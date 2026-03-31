"""CLI interface for Anomaly Surround."""
import argparse
import sys
import json
from config import (
    load_settings, save_settings, load_profile, save_profile,
    list_profiles, GAME_PRESETS, DEFAULT_PROFILE
)
from audio_engine import (
    is_eqapo_installed, write_full_config, get_audio_devices,
    set_master_volume, configure_windows_spatial_audio
)
from game_monitor import GameMonitor, KNOWN_GAMES


def cmd_status(args):
    settings = load_settings()
    profile = load_profile(settings["active_profile"])

    print(f"\n  Anomaly Surround - Status")
    print(f"  {'='*35}")
    print(f"  Equalizer APO:   {'Installed' if is_eqapo_installed() else 'NOT INSTALLED'}")
    print(f"  Active Profile:  {settings['active_profile']}")
    print(f"  Surround:        {'ON' if profile.get('surround_enabled') else 'OFF'}")
    print(f"  HRTF:            {'ON' if profile.get('hrtf_enabled') else 'OFF'}")
    print(f"  EQ:              {'ON' if settings.get('eq_enabled') else 'OFF'}")
    print(f"  Auto-start:      {'ON' if settings.get('auto_start') else 'OFF'}")
    print(f"  Spatial Audio:   {settings.get('spatial_audio', 'off')}")
    print(f"  Master Volume:   {settings.get('master_volume', 100)}%")
    print()

    devices = get_audio_devices()
    if devices:
        print(f"  Audio Devices:")
        for d in devices:
            print(f"    - {d['name']}")
    print()


def cmd_profiles(args):
    profiles = list_profiles()
    settings = load_settings()
    active = settings["active_profile"]

    print(f"\n  Available Profiles:")
    print(f"  {'='*35}")
    for p in profiles:
        marker = " *" if p == active else "  "
        if p in GAME_PRESETS:
            print(f"  {marker} {p} (preset: {GAME_PRESETS[p]['name']})")
        else:
            profile = load_profile(p)
            print(f"  {marker} {p} ({profile.get('name', 'Custom')})")
    print(f"\n  * = active profile\n")


def cmd_apply(args):
    settings = load_settings()
    profile_name = args.profile or settings["active_profile"]
    profile = load_profile(profile_name)

    if not is_eqapo_installed():
        print("\n  ERROR: Equalizer APO is not installed.")
        print("  Download from: https://sourceforge.net/projects/equalizerapo/")
        print("  Install it and configure it for your HyperX headphones.\n")
        return

    success, msg = write_full_config(profile, enabled=True)
    if success:
        settings["active_profile"] = profile_name
        save_settings(settings)
        print(f"\n  Profile '{profile_name}' applied successfully!")
        print(f"  {msg}\n")
    else:
        print(f"\n  ERROR: {msg}\n")


def cmd_eq(args):
    settings = load_settings()
    profile = load_profile(settings["active_profile"])

    if args.band is not None and args.gain is not None:
        bands = profile.get("eq_bands", [])
        if 0 <= args.band < len(bands):
            bands[args.band]["gain"] = args.gain
            profile["eq_bands"] = bands
            save_profile(settings["active_profile"], profile)
            print(f"  Band {args.band} ({bands[args.band]['freq']} Hz) set to {args.gain} dB")

            if is_eqapo_installed():
                write_full_config(profile)
                print("  Config updated.")
        else:
            print(f"  Invalid band index. Use 0-{len(bands)-1}")
    else:
        bands = profile.get("eq_bands", [])
        print(f"\n  EQ Bands ({settings['active_profile']}):")
        print(f"  {'='*40}")
        for i, band in enumerate(bands):
            bar_len = int(abs(band['gain']))
            if band['gain'] >= 0:
                bar = '+' * bar_len
                print(f"  [{i}] {band['freq']:>5} Hz: {band['gain']:+.1f} dB  |{'=' * 10}{bar}")
            else:
                bar = '-' * bar_len
                print(f"  [{i}] {band['freq']:>5} Hz: {band['gain']:+.1f} dB  |{bar}{'=' * (10 - bar_len)}")
        print()


def cmd_surround(args):
    settings = load_settings()
    profile = load_profile(settings["active_profile"])

    if args.action == "on":
        profile["surround_enabled"] = True
        profile["hrtf_enabled"] = True
        save_profile(settings["active_profile"], profile)
        if is_eqapo_installed():
            write_full_config(profile)
        print("  Virtual 7.1 surround ENABLED")
    elif args.action == "off":
        profile["surround_enabled"] = False
        profile["hrtf_enabled"] = False
        save_profile(settings["active_profile"], profile)
        if is_eqapo_installed():
            write_full_config(profile)
        print("  Virtual 7.1 surround DISABLED")
    elif args.action == "status":
        print(f"  Surround: {'ON' if profile.get('surround_enabled') else 'OFF'}")
        print(f"  HRTF: {'ON' if profile.get('hrtf_enabled') else 'OFF'}")
        print(f"  Room size: {profile.get('room_size', 50)}%")
        print(f"  Stereo width: {profile.get('stereo_width', 70)}%")


def cmd_volume(args):
    if args.level is not None:
        level = max(0, min(100, args.level))
        if set_master_volume(level):
            print(f"  Volume set to {level}%")
        else:
            print("  Failed to set volume")
    else:
        print("  Specify volume level: surround volume 75")


def cmd_games(args):
    monitor = GameMonitor()

    if args.action == "list":
        print(f"\n  Game Profile Mappings:")
        print(f"  {'='*50}")
        settings = load_settings()
        custom = settings.get("game_profiles", {})
        all_mappings = {**KNOWN_GAMES, **custom}
        for exe, profile in sorted(all_mappings.items()):
            marker = " (custom)" if exe in custom else ""
            print(f"  {exe:<35} -> {profile}{marker}")
        print()

    elif args.action == "detect":
        games = monitor.get_running_games()
        if games:
            print(f"\n  Detected Games:")
            for g in games:
                print(f"    {g['exe']} -> {g['profile']} profile")
        else:
            print("\n  No known games detected.")
        print()

    elif args.action == "add":
        if args.exe and args.profile_name:
            settings = load_settings()
            if "game_profiles" not in settings:
                settings["game_profiles"] = {}
            settings["game_profiles"][args.exe.lower()] = args.profile_name
            save_settings(settings)
            print(f"  Added: {args.exe} -> {args.profile_name}")
        else:
            print("  Usage: surround games add <exe_name> <profile_name>")


def cmd_autostart(args):
    settings = load_settings()
    if args.action == "on":
        settings["auto_start"] = True
        save_settings(settings)
        _set_windows_autostart(True)
        print("  Auto-start ENABLED")
    elif args.action == "off":
        settings["auto_start"] = False
        save_settings(settings)
        _set_windows_autostart(False)
        print("  Auto-start DISABLED")


def _set_windows_autostart(enable):
    """Add/remove from Windows startup."""
    import os
    startup_dir = os.path.join(
        os.environ.get("APPDATA", ""),
        "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
    )
    shortcut_path = os.path.join(startup_dir, "Anomaly Surround.bat")

    if enable:
        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
        with open(shortcut_path, "w") as f:
            f.write(f'@echo off\npythonw "{app_path}" --background\n')
    else:
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)


def main():
    parser = argparse.ArgumentParser(
        prog="surround",
        description="Anomaly Surround - 7.1 Virtual Surround Sound for HyperX headphones"
    )
    subparsers = parser.add_subparsers(dest="command")

    # status
    subparsers.add_parser("status", help="Show current status")

    # profiles
    subparsers.add_parser("profiles", help="List available profiles")

    # apply
    apply_p = subparsers.add_parser("apply", help="Apply a profile")
    apply_p.add_argument("profile", nargs="?", help="Profile name")

    # eq
    eq_p = subparsers.add_parser("eq", help="View/edit EQ bands")
    eq_p.add_argument("--band", "-b", type=int, help="Band index (0-9)")
    eq_p.add_argument("--gain", "-g", type=float, help="Gain in dB (-12 to 12)")

    # surround
    surround_p = subparsers.add_parser("surround", help="Toggle surround on/off")
    surround_p.add_argument("action", choices=["on", "off", "status"])

    # volume
    vol_p = subparsers.add_parser("volume", help="Set master volume")
    vol_p.add_argument("level", type=int, nargs="?", help="Volume 0-100")

    # games
    games_p = subparsers.add_parser("games", help="Game profile management")
    games_p.add_argument("action", choices=["list", "detect", "add"])
    games_p.add_argument("exe", nargs="?", help="Game executable name")
    games_p.add_argument("profile_name", nargs="?", help="Profile to use")

    # autostart
    auto_p = subparsers.add_parser("autostart", help="Toggle auto-start")
    auto_p.add_argument("action", choices=["on", "off"])

    args = parser.parse_args()

    commands = {
        "status": cmd_status,
        "profiles": cmd_profiles,
        "apply": cmd_apply,
        "eq": cmd_eq,
        "surround": cmd_surround,
        "volume": cmd_volume,
        "games": cmd_games,
        "autostart": cmd_autostart,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
