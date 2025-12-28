"""
CITYARRAY Scenario Simulator
Pre-built emergency scenarios for demo
"""

from templates import TIER_COLORS

SCENARIOS = {
    "1": {
        "name": "Earthquake",
        "tier": "emergency",
        "messages": {
            "en": "EARTHQUAKE DROP COVER HOLD",
            "es": "TERREMOTO AGACHESE CUBRASE",
            "zh": "DI ZHEN DUO XIA YAN HU",
            "ko": "JIJIN EOMPE SUMEO",
            "vi": "DONG DAT CUI XUONG CHE"
        },
        "tts": "Earthquake detected. Drop, cover, and hold on. When shaking stops, evacuate to assembly point."
    },
    
    "2": {
        "name": "Active Threat",
        "tier": "emergency",
        "messages": {
            "en": "RUN HIDE FIGHT",
            "es": "CORRE ESCONDETE PELEA",
            "zh": "KUAI PAO DUO CANG FAN JI",
            "ko": "DALLYO SUMEO SSAWOO",
            "vi": "CHAY TRON CHONG TRA"
        },
        "tts": "Security threat. Run if you can. Hide if you cannot run. Fight only as last resort."
    },
    
    "3": {
        "name": "Fire",
        "tier": "emergency",
        "messages": {
            "en": "FIRE EXIT NOW",
            "es": "FUEGO SALGA AHORA",
            "zh": "HUO ZAI LI KAI",
            "ko": "BULIYA DAEPIHAE",
            "vi": "CHAY THOAT NGAY"
        },
        "tts": "Fire detected. Exit the building immediately. Do not use elevators. Proceed to assembly point."
    },
    
    "4": {
        "name": "Air Quality Alert",
        "tier": "warning",
        "messages": {
            "en": "AIR QUALITY ALERT",
            "es": "ALERTA CALIDAD AIRE",
            "zh": "KONG QI JING BAO",
            "ko": "GONGGI GYEONGBO",
            "vi": "CANH BAO KHONG KHI"
        },
        "tts": "Air quality is unhealthy. If outdoors, move inside. Close windows and doors."
    },
    
    "5": {
        "name": "Flash Flood",
        "tier": "warning",
        "messages": {
            "en": "FLASH FLOOD WARNING",
            "es": "AVISO INUNDACION",
            "zh": "HONG SHUI JING BAO",
            "ko": "HONGSOO GYEONGBO",
            "vi": "CANH BAO LU QUET"
        },
        "tts": "Flash flood warning. Move to higher ground immediately. Avoid flood waters."
    },
    
    "6": {
        "name": "Crowd Capacity",
        "tier": "warning",
        "messages": {
            "en": "CAPACITY REACHED",
            "es": "CAPACIDAD MAXIMA",
            "zh": "REN SHU YI MAN",
            "ko": "SUYONG CHOGWA",
            "vi": "DA DU SO NGUOI"
        },
        "tts": "Venue is at capacity. Please use alternate entrance or wait for space."
    },
    
    "7": {
        "name": "All Clear",
        "tier": "advisory",
        "messages": {
            "en": "ALL CLEAR",
            "es": "TODO DESPEJADO",
            "zh": "JING BAO JIE CHU",
            "ko": "ANJEON HWAGBO",
            "vi": "AN TOAN"
        },
        "tts": "All clear. The emergency has ended. You may resume normal activities."
    },
    
    "8": {
        "name": "System Ready",
        "tier": "informational",
        "messages": {
            "en": "CITYARRAY READY",
            "es": "CITYARRAY LISTO",
            "zh": "XI TONG JIU XU",
            "ko": "JUNBI WANRYO",
            "vi": "SAN SANG"
        },
        "tts": "City Array emergency communication system is online and ready."
    }
}


class ScenarioPlayer:
    def __init__(self, display=None, speaker=None):
        self.display = display
        self.speaker = speaker
        self.current_scenario = None
    
    def list_scenarios(self):
        """List available scenarios."""
        print("\n=== Available Scenarios ===")
        for key, scenario in SCENARIOS.items():
            print(f"  {key}: {scenario['name']} [{scenario['tier']}]")
        print()
    
    def play(self, scenario_id, venue=None):
        """Play a scenario."""
        if scenario_id not in SCENARIOS:
            print(f"Unknown scenario: {scenario_id}")
            return None
        
        scenario = SCENARIOS[scenario_id]
        self.current_scenario = scenario
        
        print(f"\n>>> SCENARIO: {scenario['name']} <<<")
        print(f"Tier: {scenario['tier'].upper()}")
        print(f"Messages:")
        for lang, msg in scenario['messages'].items():
            print(f"  [{lang}] {msg}")
        
        if venue:
            print(f"Venue: {venue.venue['name']}")
            print(f"Assembly: {venue.get_assembly_point()}")
        
        return scenario
    
    def get_color(self, scenario_id):
        """Get color for scenario tier."""
        if scenario_id not in SCENARIOS:
            return (0, 100, 255)
        tier = SCENARIOS[scenario_id]["tier"]
        return TIER_COLORS.get(tier, (0, 100, 255))


if __name__ == "__main__":
    player = ScenarioPlayer()
    player.list_scenarios()
    
    print("Playing scenario 1 (Earthquake):")
    player.play("1")
    
    print("\nPlaying scenario 4 (Air Quality):")
    player.play("4")
