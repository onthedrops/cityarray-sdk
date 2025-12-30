"""
CITYARRAY City Demo - All Multilingual
"""

import time
from led_simulator import LEDSimulator
from hailo_detect import HailoDetector
from city_data import CityData
from venues import VenueContext
from scenarios import SCENARIOS
from templates import TIER_COLORS

# Multilingual labels
LABELS = {
    "person": {"en": "PERSON", "es": "PERSONA", "zh": "REN", "ko": "SARAM", "vi": "NGUOI"},
    "people": {"en": "PEOPLE", "es": "PERSONAS", "zh": "REN", "ko": "MYEONG", "vi": "NGUOI"},
    "clear": {"en": "CLEAR", "es": "DESPEJADO", "zh": "QING", "ko": "MALG", "vi": "QUANG"},
    "cloudy": {"en": "CLOUDY", "es": "NUBLADO", "zh": "YUN", "ko": "HURIM", "vi": "MAY"},
    "rain": {"en": "RAIN", "es": "LLUVIA", "zh": "YU", "ko": "BI", "vi": "MUA"},
    "hot": {"en": "HOT", "es": "CALOR", "zh": "RE", "ko": "DEOWO", "vi": "NONG"},
    "cold": {"en": "COLD", "es": "FRIO", "zh": "LENG", "ko": "CHUWO", "vi": "LANH"},
    "wind": {"en": "WIND ALERT", "es": "ALERTA", "zh": "FENG", "ko": "PARAM", "vi": "GIO"},
    "flood": {"en": "FLOOD", "es": "INUNDA", "zh": "SHUI", "ko": "HONGSOO", "vi": "LU"},
    "air_good": {"en": "AIR GOOD", "es": "AIRE BIEN", "zh": "KONG HAO", "ko": "GONGGI", "vi": "KHI TOT"},
    "air_bad": {"en": "AIR BAD", "es": "AIRE MAL", "zh": "KONG CHA", "ko": "NAPPEUM", "vi": "KHI XAU"},
}

LANGUAGES = ["en", "es", "zh", "ko", "vi"]

class CityDemo:
    def __init__(self):
        print("=== CITYARRAY Demo ===\n")
        self.display = LEDSimulator()
        self.detector = HailoDetector()
        self.city = CityData()
        self.venue = VenueContext("demo_site")
        print("Ready!\n")
    
    def show(self, text, tier="informational", duration=1.5):
        color = TIER_COLORS.get(tier, (0, 100, 255))
        self.display.clear()
        self.display.draw_text_centered(text[:10], color)
        self.display.render()
        time.sleep(duration)
        return self.display.process_events()
    
    def show_multilingual(self, label_key, prefix="", tier="informational", duration=1.2):
        """Show message in all 5 languages."""
        labels = LABELS.get(label_key, {"en": label_key.upper()})
        for lang in LANGUAGES:
            text = labels.get(lang, labels["en"])
            if prefix:
                text = f"{prefix} {text}"
            if not self.show(text[:10], tier, duration):
                return False
        return True
    
    def show_scenario(self, scenario_id):
        s = SCENARIOS.get(scenario_id)
        if not s:
            return True
        print(f">>> {s['name']} <<<")
        for lang in LANGUAGES:
            msg = s["messages"].get(lang, s["messages"]["en"])
            if not self.show(msg, s["tier"], duration=1.2):
                return False
        return True
    
    def show_weather(self):
        print("Weather...")
        w = self.city.get_weather()
        if "error" not in w:
            temp = w["temp_f"]
            cond = w["conditions"].lower()
            print(f"  {temp}F {cond}")
            
            # Map conditions to label
            if "clear" in cond or "sun" in cond:
                label = "clear"
            elif "cloud" in cond:
                label = "cloudy"
            elif "rain" in cond:
                label = "rain"
            else:
                label = "clear"
            
            # Show temp with condition in each language
            for lang in LANGUAGES:
                cond_text = LABELS[label].get(lang, LABELS[label]["en"])
                text = f"{temp}F {cond_text}"
                if not self.show(text[:10], "informational", 1.2):
                    return False
        return True
    
    def show_air(self):
        print("Air quality...")
        a = self.city.get_air_quality()
        if "error" not in a:
            level = a["level"]
            print(f"  {level}")
            
            if level in ["POOR", "HAZARDOUS"]:
                label = "air_bad"
                tier = "warning"
            else:
                label = "air_good"
                tier = "informational"
            
            return self.show_multilingual(label, "", tier, 1.2)
        return True
    
    def show_alerts(self):
        print("NWS alerts...")
        alerts = self.city.get_nws_alerts()
        if alerts and "error" not in alerts[0]:
            a = alerts[0]
            event = a["event"].lower()
            print(f"  {a['event']}")
            
            # Map to short label
            if "wind" in event:
                label = "wind"
            elif "flood" in event:
                label = "flood"
            elif "cold" in event:
                label = "cold"
            elif "heat" in event or "hot" in event:
                label = "hot"
            else:
                label = "wind"  # default
            
            tier = "emergency" if a["severity"] == "Severe" else "warning"
            return self.show_multilingual(label, "", tier, 1.2)
        else:
            print("  No alerts")
            return self.show("NO ALERTS", "advisory", 2)
    
    def detect(self):
        print("Detecting...")
        img = self.detector.capture()
        dets = self.detector.detect(img, conf_threshold=0.25)
        count = sum(1 for d in dets if d["class"] == "person")
        print(f"  {count} person(s)")
        
        label = "person" if count == 1 else "people"
        return self.show_multilingual(label, str(count), "informational", 1.2)
    
    def run(self):
        print("Starting demo...\n")
        
        # 1. Ready
        if not self.show_scenario("5"):
            return
        
        # 2. Detection (5 languages)
        if not self.detect():
            return
        
        # 3. Weather (5 languages)
        if not self.show_weather():
            return
        
        # 4. Air Quality (5 languages)
        if not self.show_air():
            return
        
        # 5. NWS Alerts (5 languages)
        if not self.show_alerts():
            return
        
        # 6. Emergency scenario
        if not self.show_scenario("1"):
            return
        time.sleep(1)
        
        # 7. All clear
        if not self.show_scenario("4"):
            return
        
        print("\nDemo complete!")
    
    def cleanup(self):
        self.display.quit()
        self.detector.close()

if __name__ == "__main__":
    demo = CityDemo()
    try:
        demo.run()
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        demo.cleanup()
