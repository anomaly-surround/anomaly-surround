"""Headphone database for auto-EQ correction.

Each entry has:
- match: substring to match against Windows audio device name (lowercase)
- name: friendly display name
- eq_correction: EQ adjustments to flatten/optimize the headphone's response
  These are compensation curves — they correct for known frequency response issues
"""

HEADPHONE_DB = [
    # HyperX
    {
        "match": "hyperx cloud alpha s",
        "name": "HyperX Cloud Alpha S",
        "eq_correction": [
            {"freq": 31, "gain": 1, "q": 1.0},
            {"freq": 62, "gain": 0, "q": 1.0},
            {"freq": 125, "gain": -1, "q": 1.0},
            {"freq": 250, "gain": 0, "q": 1.0},
            {"freq": 500, "gain": 0, "q": 1.0},
            {"freq": 1000, "gain": -1, "q": 1.0},
            {"freq": 2000, "gain": 1, "q": 1.0},
            {"freq": 4000, "gain": 2, "q": 1.0},
            {"freq": 8000, "gain": -1, "q": 1.0},
            {"freq": 16000, "gain": 0, "q": 1.0},
        ],
    },
    {
        "match": "hyperx cloud ii",
        "name": "HyperX Cloud II",
        "eq_correction": [
            {"freq": 31, "gain": 0, "q": 1.0},
            {"freq": 62, "gain": -1, "q": 1.0},
            {"freq": 125, "gain": -1, "q": 1.0},
            {"freq": 250, "gain": 0, "q": 1.0},
            {"freq": 500, "gain": 1, "q": 1.0},
            {"freq": 1000, "gain": 0, "q": 1.0},
            {"freq": 2000, "gain": 2, "q": 1.0},
            {"freq": 4000, "gain": 1, "q": 1.0},
            {"freq": 8000, "gain": -2, "q": 1.0},
            {"freq": 16000, "gain": -1, "q": 1.0},
        ],
    },
    {
        "match": "hyperx cloud",
        "name": "HyperX Cloud",
        "eq_correction": [
            {"freq": 31, "gain": 0, "q": 1.0},
            {"freq": 62, "gain": -1, "q": 1.0},
            {"freq": 125, "gain": 0, "q": 1.0},
            {"freq": 250, "gain": 0, "q": 1.0},
            {"freq": 500, "gain": 0, "q": 1.0},
            {"freq": 1000, "gain": 0, "q": 1.0},
            {"freq": 2000, "gain": 1, "q": 1.0},
            {"freq": 4000, "gain": 2, "q": 1.0},
            {"freq": 8000, "gain": -1, "q": 1.0},
            {"freq": 16000, "gain": 0, "q": 1.0},
        ],
    },
    # SteelSeries
    {
        "match": "arctis",
        "name": "SteelSeries Arctis",
        "eq_correction": [
            {"freq": 31, "gain": 1, "q": 1.0},
            {"freq": 62, "gain": 1, "q": 1.0},
            {"freq": 125, "gain": 0, "q": 1.0},
            {"freq": 250, "gain": 0, "q": 1.0},
            {"freq": 500, "gain": -1, "q": 1.0},
            {"freq": 1000, "gain": 0, "q": 1.0},
            {"freq": 2000, "gain": 2, "q": 1.0},
            {"freq": 4000, "gain": 1, "q": 1.0},
            {"freq": 8000, "gain": -1, "q": 1.0},
            {"freq": 16000, "gain": -1, "q": 1.0},
        ],
    },
    # Logitech
    {
        "match": "g pro",
        "name": "Logitech G Pro",
        "eq_correction": [
            {"freq": 31, "gain": 0, "q": 1.0},
            {"freq": 62, "gain": -1, "q": 1.0},
            {"freq": 125, "gain": 0, "q": 1.0},
            {"freq": 250, "gain": 1, "q": 1.0},
            {"freq": 500, "gain": 0, "q": 1.0},
            {"freq": 1000, "gain": 0, "q": 1.0},
            {"freq": 2000, "gain": 2, "q": 1.0},
            {"freq": 4000, "gain": 3, "q": 0.8},
            {"freq": 8000, "gain": -2, "q": 1.0},
            {"freq": 16000, "gain": -1, "q": 1.0},
        ],
    },
    {
        "match": "g733",
        "name": "Logitech G733",
        "eq_correction": [
            {"freq": 31, "gain": -1, "q": 1.0},
            {"freq": 62, "gain": -2, "q": 1.0},
            {"freq": 125, "gain": 0, "q": 1.0},
            {"freq": 250, "gain": 1, "q": 1.0},
            {"freq": 500, "gain": 0, "q": 1.0},
            {"freq": 1000, "gain": 0, "q": 1.0},
            {"freq": 2000, "gain": 1, "q": 1.0},
            {"freq": 4000, "gain": 2, "q": 1.0},
            {"freq": 8000, "gain": -1, "q": 1.0},
            {"freq": 16000, "gain": 0, "q": 1.0},
        ],
    },
    # Razer
    {
        "match": "razer kraken",
        "name": "Razer Kraken",
        "eq_correction": [
            {"freq": 31, "gain": -2, "q": 1.0},
            {"freq": 62, "gain": -2, "q": 1.0},
            {"freq": 125, "gain": -1, "q": 1.0},
            {"freq": 250, "gain": 0, "q": 1.0},
            {"freq": 500, "gain": 1, "q": 1.0},
            {"freq": 1000, "gain": 0, "q": 1.0},
            {"freq": 2000, "gain": 2, "q": 1.0},
            {"freq": 4000, "gain": 3, "q": 0.8},
            {"freq": 8000, "gain": -1, "q": 1.0},
            {"freq": 16000, "gain": -1, "q": 1.0},
        ],
    },
    {
        "match": "razer blackshark",
        "name": "Razer BlackShark",
        "eq_correction": [
            {"freq": 31, "gain": 0, "q": 1.0},
            {"freq": 62, "gain": -1, "q": 1.0},
            {"freq": 125, "gain": 0, "q": 1.0},
            {"freq": 250, "gain": 0, "q": 1.0},
            {"freq": 500, "gain": 0, "q": 1.0},
            {"freq": 1000, "gain": 1, "q": 1.0},
            {"freq": 2000, "gain": 2, "q": 1.0},
            {"freq": 4000, "gain": 1, "q": 1.0},
            {"freq": 8000, "gain": -2, "q": 1.0},
            {"freq": 16000, "gain": 0, "q": 1.0},
        ],
    },
    # Corsair
    {
        "match": "corsair hs",
        "name": "Corsair HS Series",
        "eq_correction": [
            {"freq": 31, "gain": 0, "q": 1.0},
            {"freq": 62, "gain": -1, "q": 1.0},
            {"freq": 125, "gain": 0, "q": 1.0},
            {"freq": 250, "gain": 1, "q": 1.0},
            {"freq": 500, "gain": 0, "q": 1.0},
            {"freq": 1000, "gain": 0, "q": 1.0},
            {"freq": 2000, "gain": 1, "q": 1.0},
            {"freq": 4000, "gain": 2, "q": 1.0},
            {"freq": 8000, "gain": -1, "q": 1.0},
            {"freq": 16000, "gain": -1, "q": 1.0},
        ],
    },
    {
        "match": "corsair void",
        "name": "Corsair Void",
        "eq_correction": [
            {"freq": 31, "gain": -1, "q": 1.0},
            {"freq": 62, "gain": -2, "q": 1.0},
            {"freq": 125, "gain": 0, "q": 1.0},
            {"freq": 250, "gain": 1, "q": 1.0},
            {"freq": 500, "gain": 0, "q": 1.0},
            {"freq": 1000, "gain": 0, "q": 1.0},
            {"freq": 2000, "gain": 2, "q": 1.0},
            {"freq": 4000, "gain": 2, "q": 1.0},
            {"freq": 8000, "gain": -2, "q": 1.0},
            {"freq": 16000, "gain": -1, "q": 1.0},
        ],
    },
    # Beyerdynamic
    {
        "match": "beyerdynamic",
        "name": "Beyerdynamic",
        "eq_correction": [
            {"freq": 31, "gain": 1, "q": 1.0},
            {"freq": 62, "gain": 0, "q": 1.0},
            {"freq": 125, "gain": 0, "q": 1.0},
            {"freq": 250, "gain": 0, "q": 1.0},
            {"freq": 500, "gain": 0, "q": 1.0},
            {"freq": 1000, "gain": 0, "q": 1.0},
            {"freq": 2000, "gain": 0, "q": 1.0},
            {"freq": 4000, "gain": -1, "q": 1.0},
            {"freq": 8000, "gain": -3, "q": 1.0},
            {"freq": 16000, "gain": -2, "q": 1.0},
        ],
    },
    # Audio-Technica
    {
        "match": "audio-technica",
        "name": "Audio-Technica",
        "eq_correction": [
            {"freq": 31, "gain": 1, "q": 1.0},
            {"freq": 62, "gain": 1, "q": 1.0},
            {"freq": 125, "gain": 0, "q": 1.0},
            {"freq": 250, "gain": 0, "q": 1.0},
            {"freq": 500, "gain": 0, "q": 1.0},
            {"freq": 1000, "gain": 0, "q": 1.0},
            {"freq": 2000, "gain": 0, "q": 1.0},
            {"freq": 4000, "gain": 1, "q": 1.0},
            {"freq": 8000, "gain": -1, "q": 1.0},
            {"freq": 16000, "gain": 0, "q": 1.0},
        ],
    },
    # Sony
    {
        "match": "sony wh",
        "name": "Sony WH Series",
        "eq_correction": [
            {"freq": 31, "gain": 0, "q": 1.0},
            {"freq": 62, "gain": -1, "q": 1.0},
            {"freq": 125, "gain": 0, "q": 1.0},
            {"freq": 250, "gain": 0, "q": 1.0},
            {"freq": 500, "gain": 1, "q": 1.0},
            {"freq": 1000, "gain": 0, "q": 1.0},
            {"freq": 2000, "gain": 1, "q": 1.0},
            {"freq": 4000, "gain": 0, "q": 1.0},
            {"freq": 8000, "gain": -1, "q": 1.0},
            {"freq": 16000, "gain": 0, "q": 1.0},
        ],
    },
    {
        "match": "sony inzone",
        "name": "Sony INZONE",
        "eq_correction": [
            {"freq": 31, "gain": 0, "q": 1.0},
            {"freq": 62, "gain": 0, "q": 1.0},
            {"freq": 125, "gain": 0, "q": 1.0},
            {"freq": 250, "gain": 1, "q": 1.0},
            {"freq": 500, "gain": 0, "q": 1.0},
            {"freq": 1000, "gain": 0, "q": 1.0},
            {"freq": 2000, "gain": 2, "q": 1.0},
            {"freq": 4000, "gain": 1, "q": 1.0},
            {"freq": 8000, "gain": -2, "q": 1.0},
            {"freq": 16000, "gain": -1, "q": 1.0},
        ],
    },
    # Sennheiser
    {
        "match": "sennheiser",
        "name": "Sennheiser",
        "eq_correction": [
            {"freq": 31, "gain": 1, "q": 1.0},
            {"freq": 62, "gain": 0, "q": 1.0},
            {"freq": 125, "gain": 0, "q": 1.0},
            {"freq": 250, "gain": 0, "q": 1.0},
            {"freq": 500, "gain": 0, "q": 1.0},
            {"freq": 1000, "gain": 0, "q": 1.0},
            {"freq": 2000, "gain": 1, "q": 1.0},
            {"freq": 4000, "gain": 0, "q": 1.0},
            {"freq": 8000, "gain": -1, "q": 1.0},
            {"freq": 16000, "gain": 0, "q": 1.0},
        ],
    },
]


def detect_headphone(device_list):
    """Match detected audio devices against the headphone database.

    Returns the best match or None.
    """
    for device in device_list:
        name = device.get("name", "").lower()
        for hp in HEADPHONE_DB:
            if hp["match"] in name:
                return hp
    return None


def get_corrected_eq(base_eq, headphone):
    """Apply headphone correction on top of a base EQ profile.

    Adds the correction values to the base EQ gains.
    """
    if not headphone:
        return base_eq

    correction = headphone.get("eq_correction", [])
    corrected = []
    for i, band in enumerate(base_eq):
        new_band = dict(band)
        if i < len(correction):
            new_band["gain"] = band["gain"] + correction[i]["gain"]
            # Clamp to -12 to +12
            new_band["gain"] = max(-12, min(12, new_band["gain"]))
        corrected.append(new_band)
    return corrected
