"""
CITYARRAY Emergency Scenarios
"""

from templates import TIER_COLORS

SCENARIOS = {
    "1": {
        "name": "Earthquake",
        "tier": "emergency",
        "messages": {
            "en": "EARTHQUAKE",
            "es": "TERREMOTO",
            "zh": "DI ZHEN",
            "ko": "JIJIN",
            "vi": "DONG DAT"
        }
    },
    "2": {
        "name": "Fire",
        "tier": "emergency",
        "messages": {
            "en": "FIRE EXIT",
            "es": "FUEGO SALGA",
            "zh": "HUO ZAI",
            "ko": "BULIYA",
            "vi": "CHAY"
        }
    },
    "3": {
        "name": "Air Quality",
        "tier": "warning",
        "messages": {
            "en": "AIR ALERT",
            "es": "ALERTA AIRE",
            "zh": "KONG QI",
            "ko": "GONGGI",
            "vi": "KHONG KHI"
        }
    },
    "4": {
        "name": "All Clear",
        "tier": "advisory",
        "messages": {
            "en": "ALL CLEAR",
            "es": "DESPEJADO",
            "zh": "AN QUAN",
            "ko": "ANJEON",
            "vi": "AN TOAN"
        }
    },
    "5": {
        "name": "Ready",
        "tier": "informational",
        "messages": {
            "en": "READY",
            "es": "LISTO",
            "zh": "ZHUN BEI",
            "ko": "JUNBI",
            "vi": "SAN SANG"
        }
    }
}

def get_scenario(scenario_id):
    return SCENARIOS.get(scenario_id)

def list_scenarios():
    for key, s in SCENARIOS.items():
        print(f"{key}: {s['name']} [{s['tier']}]")

if __name__ == "__main__":
    print("=== Scenarios ===")
    list_scenarios()
