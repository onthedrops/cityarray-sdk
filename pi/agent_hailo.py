"""
CITYARRAY Agent with Hailo Acceleration
"""

import time
from hailo_detect import HailoDetector
from database import get_detection_summary
from templates import get_message_for_detection, get_status_message, get_supported_languages
from led_simulator import LEDSimulator

def run_agent():
    print("Starting CITYARRAY Agent (Hailo accelerated)...")
    
    detector = HailoDetector()
    sim = LEDSimulator()
    languages = get_supported_languages()
    lang_index = 0
    
    # Show ready
    text, tier, color = get_status_message("ready", "en")
    sim.clear()
    sim.draw_text_centered(text, color)
    sim.render()
    time.sleep(2)
    
    last_detection = None
    last_detection_time = 0
    scan_interval = 2
    display_duration = 2
    
    print("Agent running... Press ESC to quit")
    
    running = True
    last_scan = 0
    last_display_change = time.time()
    
    while running:
        running = sim.process_events()
        current_time = time.time()
        
        # Scan
        if current_time - last_scan > scan_interval:
            img = detector.capture()
            dets = detector.detect(img, conf_threshold=0.25)
            
            if dets:
                best = max(dets, key=lambda d: d["confidence"])
                last_detection = best["class"]
                last_detection_time = current_time
                print(f"Detected: {best['class']} ({best['confidence']:.0%})")
            else:
                if current_time - last_detection_time > 10:
                    last_detection = None
            
            last_scan = current_time
        
        # Display
        if current_time - last_display_change > display_duration:
            sim.clear()
            
            if last_detection:
                lang = languages[lang_index]
                text, tier, color = get_message_for_detection(last_detection, lang)
                if text:
                    if len(text) > 10:
                        text = text[:10]
                    sim.draw_text_centered(text, color)
            else:
                text, tier, color = get_status_message("scanning", languages[lang_index])
                sim.draw_text_centered(text, color)
            
            lang_index = (lang_index + 1) % len(languages)
            last_display_change = current_time
        
        sim.render()
        sim.tick(30)
    
    sim.quit()
    detector.close()
    
    print("\n=== Summary ===")
    for s in get_detection_summary():
        print(f"{s['object_class']}: {s['count']} times")


if __name__ == "__main__":
    run_agent()
