"""
CITYARRAY Message Templates
Multilingual alert messages (romanized for LED display)
"""

# Tier colors
TIER_COLORS = {
    "informational": (0, 100, 255),    # Blue
    "advisory": (0, 255, 0),            # Green
    "warning": (255, 191, 0),           # Amber
    "emergency": (255, 0, 0),           # Red
}

# Detection to message mapping (romanized for LED)
DETECTION_MESSAGES = {
    "person": {
        "tier": "informational",
        "translations": {
            "en": "PERSON",
            "es": "PERSONA",
            "zh": "REN YUAN",
            "ko": "SARAM",
            "vi": "NGUOI",
        }
    },
    "crowd": {
        "tier": "advisory",
        "translations": {
            "en": "CROWD: {count}",
            "es": "MULTITUD: {count}",
            "zh": "REN QUN: {count}",
            "ko": "GUNJUNG: {count}",
            "vi": "DAM DONG: {count}",
        }
    },
    "fire": {
        "tier": "emergency",
        "translations": {
            "en": "FIRE EXIT NOW",
            "es": "FUEGO SALGA",
            "zh": "HUO ZAI KUAI PAO",
            "ko": "BULIYA DAEPIHAE",
            "vi": "CHAY THOAT NGAY",
        }
    },
    "smoke": {
        "tier": "warning",
        "translations": {
            "en": "SMOKE",
            "es": "HUMO",
            "zh": "YAN WU",
            "ko": "YEONGI",
            "vi": "KHOI",
        }
    },
    "car": {
        "tier": "informational",
        "translations": {
            "en": "VEHICLE",
            "es": "VEHICULO",
            "zh": "CHE LIANG",
            "ko": "CHARYANG",
            "vi": "XE",
        }
    },
    "truck": {
        "tier": "informational",
        "translations": {
            "en": "TRUCK",
            "es": "CAMION",
            "zh": "KA CHE",
            "ko": "TEUREOK",
            "vi": "XE TAI",
        }
    },
    "tv": {
        "tier": "informational",
        "translations": {
            "en": "TV",
            "es": "TELE",
            "zh": "DIAN SHI",
            "ko": "TV",
            "vi": "TIVI",
        }
    },
    "laptop": {
        "tier": "informational",
        "translations": {
            "en": "LAPTOP",
            "es": "PORTATIL",
            "zh": "DIAN NAO",
            "ko": "NOTEUBUK",
            "vi": "MAY TINH",
        }
    },
    "chair": {
        "tier": "informational",
        "translations": {
            "en": "CHAIR",
            "es": "SILLA",
            "zh": "YI ZI",
            "ko": "UIJA",
            "vi": "GHE",
        }
    },
    "bed": {
        "tier": "informational",
        "translations": {
            "en": "BED",
            "es": "CAMA",
            "zh": "CHUANG",
            "ko": "CHIMDAE",
            "vi": "GIUONG",
        }
    },
}

# Status messages
STATUS_MESSAGES = {
    "ready": {
        "tier": "informational",
        "translations": {
            "en": "READY",
            "es": "LISTO",
            "zh": "ZHUN BEI",
            "ko": "JUNBI",
            "vi": "SAN SANG",
        }
    },
    "scanning": {
        "tier": "informational",
        "translations": {
            "en": "SCANNING",
            "es": "ESCANEANDO",
            "zh": "SAO MIAO",
            "ko": "SEUKAN",
            "vi": "DANG QUET",
        }
    },
    "all_clear": {
        "tier": "advisory",
        "translations": {
            "en": "ALL CLEAR",
            "es": "DESPEJADO",
            "zh": "AN QUAN",
            "ko": "ANJEON",
            "vi": "AN TOAN",
        }
    },
}


def get_message_for_detection(object_class, language="en", count=None):
    """Get message for a detected object."""
    obj = object_class.lower()
    
    if obj not in DETECTION_MESSAGES:
        return None, None, None
    
    msg = DETECTION_MESSAGES[obj]
    tier = msg["tier"]
    color = TIER_COLORS[tier]
    
    text = msg["translations"].get(language, msg["translations"]["en"])
    
    if count and "{count}" in text:
        text = text.format(count=count)
    
    return text, tier, color


def get_status_message(status, language="en"):
    """Get status message."""
    if status not in STATUS_MESSAGES:
        return None, None, None
    
    msg = STATUS_MESSAGES[status]
    tier = msg["tier"]
    color = TIER_COLORS[tier]
    text = msg["translations"].get(language, msg["translations"]["en"])
    
    return text, tier, color


def get_supported_languages():
    """Get list of supported languages."""
    return ["en", "es", "zh", "ko", "vi"]


if __name__ == "__main__":
    print("=== All Languages ===")
    for lang in get_supported_languages():
        text, tier, color = get_message_for_detection("person", lang)
        print(f"{lang}: {text}")
