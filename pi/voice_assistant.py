"""
CITYARRAY Voice Assistant
Hey CityArray, what do you see?
"""

import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'

from voice_input import listen, load_model
from audio import speak
from hailo_detect import HailoDetector
from vlm_detect import describe_scene, capture
from city_data import CityData
from database import get_recent_detections

# Load models at startup
print("=== CITYARRAY Voice Assistant ===\n")
print("Loading models...")
load_model()  # Whisper
detector = HailoDetector()  # Hailo
city = CityData()
print("Ready!\n")

def handle_query(text):
    """Process voice query and return response."""
    text = text.lower()
    
    # What do you see?
    if "see" in text or "detect" in text:
        print("  → Running detection...")
        img = detector.capture()
        dets = detector.detect(img, conf_threshold=0.25)
        if dets:
            objects = [d['class'] for d in dets]
            count = len(objects)
            unique = list(set(objects))
            return f"I see {count} objects: {', '.join(unique)}"
        else:
            return "I don't see any objects right now."
    
    # Describe the scene (VLM)
    if "describe" in text or "what's happening" in text:
        print("  → Analyzing scene (60 seconds)...")
        img = capture()
        desc = describe_scene(img)
        return desc
    
    # Weather
    if "weather" in text or "temperature" in text:
        print("  → Getting weather...")
        w = city.get_weather()
        if "error" not in w:
            return f"It's {w['temp_f']} degrees and {w['conditions']}."
        return "I couldn't get the weather."
    
    # Air quality
    if "air" in text:
        print("  → Getting air quality...")
        a = city.get_air_quality()
        if "error" not in a:
            return f"Air quality is {a['level']}."
        return "I couldn't get air quality."
    
    # Alerts
    if "alert" in text or "warning" in text:
        print("  → Checking alerts...")
        alerts = city.get_nws_alerts()
        if alerts and "error" not in alerts[0]:
            return f"Active alert: {alerts[0]['event']}."
        return "No active alerts."
    
    # How many people?
    if "people" in text or "person" in text or "how many" in text:
        print("  → Counting people...")
        img = detector.capture()
        dets = detector.detect(img, conf_threshold=0.25)
        count = sum(1 for d in dets if d['class'] == 'person')
        return f"I see {count} people."
    
    # Safe?
    if "safe" in text:
        print("  → Checking safety...")
        alerts = city.get_nws_alerts()
        if alerts and "error" not in alerts[0] and alerts[0]["severity"] == "Severe":
            return f"Caution. There is an active alert: {alerts[0]['event']}."
        return "The area appears safe. No severe alerts."
    
    # Default
    return "I heard you but I'm not sure how to help with that. Try asking what I see, the weather, or air quality."

def check_wake_word(text):
    """Check if text contains wake word."""
    wake_words = ["city array", "cityarray", "hey city", "hey array"]
    text_lower = text.lower()
    for wake in wake_words:
        if wake in text_lower:
            return True
    return False

def run_assistant():
    """Main assistant loop."""
    print("Say 'Hey CityArray' followed by your question.")
    print("Examples:")
    print("  - Hey CityArray, what do you see?")
    print("  - Hey CityArray, what's the weather?")
    print("  - Hey CityArray, how many people?")
    print("\nPress Ctrl+C to exit.\n")
    
    speak("City Array ready. Say hey city array to ask a question.", "en")
    
    while True:
        try:
            # Listen for wake word + command
            print("Listening...")
            text = listen(5)
            print(f"Heard: {text}")
            
            if check_wake_word(text):
                print("Wake word detected!")
                speak("Yes?", "en")
                
                # Get the query part after wake word
                query = text
                
                # Process query
                response = handle_query(query)
                print(f"Response: {response}")
                
                # Speak response
                speak(response, "en")
            else:
                print("(No wake word)")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            speak("Goodbye.", "en")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_assistant()
