"""
CITYARRAY Full Demo + Voice Assistant
Runs demo, then listens for wake word
"""

import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import time
import requests
from datetime import datetime
from led_simulator import LEDSimulator
from hailo_detect import HailoDetector
from city_data import CityData, OPENWEATHER_KEY
from scenarios import SCENARIOS
from templates import TIER_COLORS
from audio import speak
from voice_input import listen, load_model

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
    "listening": {"en": "LISTENING", "es": "ESCUCHA", "zh": "TING", "ko": "DEUDGO", "vi": "NGHE"},
}

def get_weather_any_city(city_name):
    """Get weather for any city worldwide."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_KEY}&units=imperial"
        data = requests.get(url, timeout=10).json()
        if data.get("cod") == 200:
            return {
                "city": data["name"],
                "temp_f": round(data["main"]["temp"]),
                "conditions": data["weather"][0]["main"],
                "humidity": data["main"]["humidity"]
            }
        else:
            return {"error": data.get("message", "City not found")}
    except Exception as e:
        return {"error": str(e)}

def get_air_quality_any_city(city_name):
    """Get air quality for any city worldwide."""
    try:
        # First get coordinates
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={OPENWEATHER_KEY}"
        geo_data = requests.get(geo_url, timeout=10).json()
        
        if not geo_data:
            return {"error": "City not found"}
        
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
        city = geo_data[0]["name"]
        
        # Then get air quality
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}"
        data = requests.get(url, timeout=10).json()
        
        aqi = data["list"][0]["main"]["aqi"]
        levels = {1: "good", 2: "fair", 3: "moderate", 4: "poor", 5: "hazardous"}
        
        return {
            "city": city,
            "aqi": aqi,
            "level": levels.get(aqi, "unknown")
        }
    except Exception as e:
        return {"error": str(e)}


def get_time_any_city(city_name):
    """Get local time for any city worldwide."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_KEY}"
        data = requests.get(url, timeout=10).json()
        if data.get("cod") == 200:
            # timezone is offset in seconds from UTC
            tz_offset = data["timezone"]
            from datetime import timezone, timedelta
            utc_now = datetime.now(timezone.utc)
            local_time = utc_now + timedelta(seconds=tz_offset)
            return {
                "city": data["name"],
                "time": local_time,
                "hour": local_time.hour,
                "minute": local_time.minute
            }
        else:
            return {"error": data.get("message", "City not found")}
    except Exception as e:
        return {"error": str(e)}

def extract_city_name(text, keywords):
    """Extract city name from query after keyword."""
    text_lower = text.lower()
    for keyword in keywords:
        if keyword in text_lower:
            # Get text after keyword
            parts = text_lower.split(keyword)
            if len(parts) > 1:
                city = parts[1].strip().strip("?").strip()
                # Remove common words
                for remove in ["the", "in", "at", "for", "of", "is"]:
                    city = city.replace(remove, "").strip()
                if city:
                    return city.title()
    return None

class DemoFull:
    def __init__(self):
        print("=== CITYARRAY Full Demo ===\n")
        print("Loading models...")
        self.display = LEDSimulator()
        self.detector = HailoDetector()
        self.city = CityData()
        load_model()  # Whisper
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
    
    def run_demo(self):
        """Run the initial demo."""
        print("Running demo...\n")
        
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
        
        print("\nDemo complete!\n")
    
    def handle_query(self, text):
        """Process voice query."""
        text_lower = text.lower()
        
        # TIME
        if "time" in text_lower:
            city_name = extract_city_name(text, ["in ", "for ", "at "])
            if city_name:
                t = get_time_any_city(city_name)
                if "error" not in t:
                    hour = t["hour"]
                    minute = t["minute"]
                    am_pm = "AM" if hour < 12 else "PM"
                    hour_12 = hour if hour <= 12 else hour - 12
                    if hour_12 == 0:
                        hour_12 = 12
                    if minute == 0:
                        return f"In {t['city']}, it's {hour_12} {am_pm}."
                    else:
                        return f"In {t['city']}, it's {hour_12}:{minute:02d} {am_pm}."
                return f"Couldn't get time for {city_name}."
            else:
                now = datetime.now()
                hour = now.hour
                minute = now.minute
                am_pm = "AM" if hour < 12 else "PM"
                hour_12 = hour if hour <= 12 else hour - 12
                if hour_12 == 0:
                    hour_12 = 12
                if minute == 0:
                    return f"It's {hour_12} {am_pm}."
                else:
                    return f"It's {hour_12}:{minute:02d} {am_pm}."
        
        # WEATHER (any city)
        if "weather" in text_lower or "temperature" in text_lower or "temp " in text_lower:
            city_name = extract_city_name(text, ["in ", "for ", "of ", "at "])
            if city_name:
                w = get_weather_any_city(city_name)
                if "error" not in w:
                    return f"{w['city']} is {w['temp_f']} degrees and {w['conditions']}."
                return f"Couldn't get weather for {city_name}."
            else:
                # Default to LA
                w = self.city.get_weather()
                if "error" not in w:
                    return f"Los Angeles is {w['temp_f']} degrees and {w['conditions']}."
                return "Couldn't get weather."
        
        # AIR QUALITY (any city)
        if "air" in text_lower:
            city_name = extract_city_name(text, ["in ", "for ", "of ", "at "])
            if city_name:
                a = get_air_quality_any_city(city_name)
                if "error" not in a:
                    return f"Air quality in {a['city']} is {a['level']}."
                return f"Couldn't get air quality for {city_name}."
            else:
                # Default to LA
                a = self.city.get_air_quality()
                if "error" not in a:
                    return f"Air quality in Los Angeles is {a['level']}."
                return "Couldn't get air quality."
        
        # DETECTION
        if "see" in text_lower or "detect" in text_lower:
            img = self.detector.capture()
            dets = self.detector.detect(img, conf_threshold=0.25)
            if dets:
                objects = list(set([d['class'] for d in dets]))
                return f"I see {', '.join(objects)}"
            return "I don't see any objects."
        
        # ALERTS
        if "alert" in text_lower or "warning" in text_lower:
            alerts = self.city.get_nws_alerts()
            if alerts and "error" not in alerts[0]:
                return f"Active alert: {alerts[0]['event']}."
            return "No active alerts."
        
        # PEOPLE COUNT
        if "people" in text_lower or "person" in text_lower or "how many" in text_lower:
            img = self.detector.capture()
            dets = self.detector.detect(img, conf_threshold=0.25)
            count = sum(1 for d in dets if d['class'] == 'person')
            return f"I see {count} people."
        
        # SAFETY CHECK
        if "safe" in text_lower:
            alerts = self.city.get_nws_alerts()
            if alerts and "error" not in alerts[0] and alerts[0]["severity"] == "Severe":
                return f"Caution. Active alert: {alerts[0]['event']}."
            return "Area appears safe."
        
        # DATE
        if "date" in text_lower or "today" in text_lower:
            now = datetime.now()
            return f"Today is {now.strftime('%A, %B %d, %Y')}."
        
        return "I'm not sure. Try asking the time, weather, air quality, or what I see."
    
    def check_wake_word(self, text):
        """Check for wake word."""
        wake_words = ["city"]
        text_lower = text.lower()
        for wake in wake_words:
            if wake in text_lower:
                return True
        return False
    
    def run_assistant(self):
        """Voice assistant loop."""
        print("=== Voice Assistant Mode ===")
        print("Say 'City' + question")
        print("Examples:")
        print("  - City, what time is it?")
        print("  - City, weather in Tokyo?")
        print("  - City, air quality in Beijing?")
        print("Ctrl+C to exit\n")
        
        speak("Now listening. Say city to ask a question.", "en")
        
        while True:
            try:
                # Show listening
                self.show("LISTENING", "informational")
                
                # Listen
                text = listen(5)
                print(f"Heard: {text}")
                
                if self.check_wake_word(text):
                    print("Wake word detected!")
                    self.show("YES?", "advisory")
                    speak("Yes?", "en")
                    
                    # Process query
                    response = self.handle_query(text)
                    print(f"Response: {response}")
                    
                    # Show and speak
                    self.show(response[:10].upper(), "informational")
                    speak(response, "en")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                speak("Goodbye.", "en")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def cleanup(self):
        self.display.quit()
        self.detector.close()

if __name__ == "__main__":
    demo = DemoFull()
    try:
        demo.run_demo()
        demo.run_assistant()
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        demo.cleanup()
