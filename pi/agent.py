"""
CITYARRAY Agent
Detection → Database → Display loop
"""

import time
import subprocess
from datetime import datetime
from pathlib import Path
from ultralytics import YOLO
from database import log_detection, get_detection_summary
from templates import get_message_for_detection, get_status_message, get_supported_languages
from led_simulator import LEDSimulator

# Paths
IMAGE_DIR = Path.home() / "pi" / "images"
IMAGE_DIR.mkdir(exist_ok=True)

# Load model
print("Loading YOLOv8...")
model = YOLO('yolov8n.pt')

def capture_image():
    """Capture from Pi camera."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = IMAGE_DIR / f"capture_{timestamp}.jpg"
    
    subprocess.run([
        "rpicam-still", "-o", str(image_path),
        "-t", "500", "--nopreview", "--ev", "1"
    ], capture_output=True)
    
    return image_path

def detect_objects(image_path):
    """Run YOLO detection."""
    results = model.predict(str(image_path), save=False, verbose=False)
    
    detections = []
    for r in results:
        for box in r.boxes:
            obj = {
                "class": model.names[int(box.cls[0])],
                "confidence": float(box.conf[0])
            }
            detections.append(obj)
            log_detection(obj["class"], obj["confidence"], str(image_path))
    
    return detections

def run_agent():
    """Main agent loop."""
    sim = LEDSimulator()
    languages = get_supported_languages()
    lang_index = 0
    
    # Show ready message
    text, tier, color = get_status_message("ready", "en")
    sim.clear()
    sim.draw_text_centered(text, color)
    sim.render()
    time.sleep(2)
    
    last_detection = None
    last_detection_time = 0
    scan_interval = 3  # seconds between scans
    display_duration = 2  # seconds per language
    
    print("Agent running... Press ESC to quit")
    print("Scanning every", scan_interval, "seconds")
    
    running = True
    last_scan = 0
    last_display_change = time.time()
    
    while running:
        running = sim.process_events()
        current_time = time.time()
        
        # Scan for objects
        if current_time - last_scan > scan_interval:
            print("\nScanning...")
            image_path = capture_image()
            detections = detect_objects(image_path)
            
            if detections:
                # Use highest confidence detection
                best = max(detections, key=lambda d: d["confidence"])
                last_detection = best["class"]
                last_detection_time = current_time
                print(f"Detected: {best['class']} ({best['confidence']:.0%})")
            else:
                print("No objects detected")
                # Clear detection after 10 seconds
                if current_time - last_detection_time > 10:
                    last_detection = None
            
            last_scan = current_time
        
        # Rotate language display
        if current_time - last_display_change > display_duration:
            sim.clear()
            
            if last_detection:
                lang = languages[lang_index]
                text, tier, color = get_message_for_detection(last_detection, lang)
                
                if text:
                    # Truncate if too long
                    max_chars = 10
                    if len(text) > max_chars:
                        text = text[:max_chars]
                    sim.draw_text_centered(text, color)
                    print(f"Display [{lang}]: {text}")
            else:
                text, tier, color = get_status_message("scanning", languages[lang_index])
                sim.draw_text_centered(text, color)
            
            lang_index = (lang_index + 1) % len(languages)
            last_display_change = current_time
        
        sim.render()
        sim.tick(30)
    
    sim.quit()
    print("\nAgent stopped")
    print("\n=== Session Summary ===")
    for s in get_detection_summary():
        print(f"{s['object_class']}: {s['count']} times")


if __name__ == "__main__":
    run_agent()
