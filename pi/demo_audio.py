"""
CITYARRAY Demo with Audio - Full Version
"""

import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import time
from led_simulator import LEDSimulator
from hailo_detect import HailoDetector
from city_data import CityData
from scenarios import SCENARIOS
from templates import TIER_COLORS
from audio import speak

LANGUAGES = ["en", "es", "zh", "ko", "vi"]

SPEECH = {
    "ready": {"en": "City Array ready", "es": "Sistema listo", "zh": "Xi tong zhun bei", "ko": "Junbi wan ryo", "vi": "San sang"},
    "person": {"en": "person detected", "es": "persona detectada", "zh": "ren bei jian ce", "ko": "saram balgyeon", "vi": "nguoi duoc phat hien"},
    "clear": {"en": "Weather clear", "es": "Clima despejado", "zh": "Tian qi qing", "ko": "Nalsi malg eum", "vi": "Troi quang"},
    "air_good": {"en": "Air quality good", "es": "Aire bueno", "zh": "Kong qi hao", "ko": "Gonggi joeum", "vi": "Khong khi tot"},
    "wind": {"en": "Wind alert", "es": "Alerta de viento", "zh": "Feng jing bao", "ko": "Baram gyeongbo", "vi": "Canh bao gio"},
    "earthquake": {"en": "Earthquake. Drop cover hold.", "es": "Terremoto. Agachese cubrase.", "zh": "Di zhen. Duo xia yan hu.", "ko": "Jijin. Eompe sumeo.", "vi": "Dong dat. Cui xuong che."},
    "all_clear": {"en": "All clear", "es": "Todo despejado", "zh": "Jing bao jie chu", "ko": "Anjeon hwakbo", "vi": "An toan"},
}

DISPLAY_TEXT = {
    "ready": {"en": "READY", "es": "LISTO", "zh": "ZHUN BEI", "ko": "JUNBI", "vi": "SAN SANG"},
    "air_good": {"en": "AIR GOOD", "es": "AIRE BIEN", "zh": "KONG HAO", "ko": "GONGGI", "vi": "KHI TOT"},
    "wind": {"en": "WIND", "es": "VIENTO", "zh": "FENG", "ko": "PARAM", "vi": "GIO"},
    "earthquake": {"en": "EARTHQUAKE", "es": "TERREMOTO", "zh": "DI ZHEN", "ko": "JIJIN", "vi": "DONG DAT"},
    "all_clear": {"en": "ALL CLEAR", "es": "DESPEJADO", "zh": "AN QUAN", "ko": "ANJEON", "vi": "AN TOAN"},
}

class DemoAudio:
    def __init__(self):
        print("=== CITYARRAY Demo + Audio ===\n")
        self.display = LEDSimulator()
        self.detector = HailoDetector()
        self.city = CityData()
        print("Ready!\n")
    
    def show(self, text, tier="informational"):
        color = TIER_COLORS.get(tier, (0, 100, 255))
        self.display.clear()
        self.display.draw_text_centered(text[:10], color)
        self.display.render()
        self.display.process_events()
    
    def show_and_speak(self, display_text, speech_text, tier="informational", lang="en"):
        self.show(display_text, tier)
        speak(speech_text, lang)
        time.sleep(0.3)
    
    def show_multilingual(self, key, tier="informational", prefix=""):
        for lang in LANGUAGES:
            display = DISPLAY_TEXT.get(key, {}).get(lang, key.upper())
            speech = SPEECH.get(key, {}).get(lang, key)
            if prefix:
                display = f"{prefix} {display}"
                speech = f"{prefix} {speech}"
            self.show_and_speak(display[:10], speech, tier, lang)
    
    def run(self):
        print("Starting full demo...\n")
        
        # 1. Ready
        print("1. Ready...")
        self.show_multilingual("ready", "informational")
        
        # 2. Detect
        print("2. Detecting...")
        img = self.detector.capture()
        dets = self.detector.detect(img, conf_threshold=0.25)
        count = sum(1 for d in dets if d["class"] == "person")
        print(f"   {count} person(s)")
        for lang in LANGUAGES:
            speech = f"{count} {SPEECH['person'][lang]}"
            self.show_and_speak(f"{count} PERSON", speech, "informational", lang)
        
        # 3. Weather
        print("3. Weather...")
        w = self.city.get_weather()
        if "error" not in w:
            temp = w["temp_f"]
            print(f"   {temp}F")
            for lang in LANGUAGES:
                self.show_and_speak(f"{temp}F", f"{temp} {SPEECH['clear'][lang]}", "informational", lang)
        
        # 4. Air Quality
        print("4. Air quality...")
        a = self.city.get_air_quality()
        if "error" not in a:
            level = a["level"]
            print(f"   {level}")
            tier = "warning" if level in ["POOR", "HAZARDOUS"] else "informational"
            self.show_multilingual("air_good", tier)
        
        # 5. NWS Alerts
        print("5. NWS alerts...")
        alerts = self.city.get_nws_alerts()
        if alerts and "error" not in alerts[0]:
            print(f"   {alerts[0]['event']}")
            self.show_multilingual("wind", "warning")
        
        # 6. Earthquake
        print("6. Earthquake scenario...")
        self.show_multilingual("earthquake", "emergency")
        
        # 7. All Clear
        print("7. All clear...")
        self.show_multilingual("all_clear", "advisory")
        
        print("\n=== Demo complete! ===")
    
    def cleanup(self):
        self.display.quit()
        self.detector.close()

if __name__ == "__main__":
    demo = DemoAudio()
    try:
        demo.run()
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        demo.cleanup()
