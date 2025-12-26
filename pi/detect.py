"""
CITYARRAY Detection Engine
Camera + YOLOv8 + Database logging
"""

import subprocess
from datetime import datetime
from pathlib import Path
from ultralytics import YOLO
from database import log_detection, get_recent_detections, get_detection_summary

# Paths
IMAGE_DIR = Path.home() / "cityarray" / "images"
IMAGE_DIR.mkdir(exist_ok=True)

# Load model
model = YOLO('yolov8n.pt')

def capture_image():
    """Capture image from Pi camera."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = IMAGE_DIR / f"capture_{timestamp}.jpg"
    
    subprocess.run([
        "rpicam-still", "-o", str(image_path),
        "-t", "1000", "--nopreview", "--ev", "1"
    ], capture_output=True)
    
    return image_path

def detect_objects(image_path):
    """Run YOLO detection on image."""
    results = model.predict(str(image_path), save=False, verbose=False)
    
    detections = []
    for r in results:
        for box in r.boxes:
            obj = {
                "class": model.names[int(box.cls[0])],
                "confidence": float(box.conf[0])
            }
            detections.append(obj)
    
    return detections

def detect_and_log():
    """Capture, detect, and log to database."""
    print("Capturing image...")
    image_path = capture_image()
    
    print("Running detection...")
    detections = detect_objects(image_path)
    
    if detections:
        print(f"Detected {len(detections)} object(s):")
        for d in detections:
            print(f"  - {d['class']} ({d['confidence']:.0%})")
            log_detection(d['class'], d['confidence'], str(image_path))
    else:
        print("No objects detected")
    
    return detections

def what_do_you_see():
    """Answer: What have you seen recently?"""
    summary = get_detection_summary()
    
    if not summary:
        return "I haven't detected anything yet."
    
    parts = []
    for item in summary:
        parts.append(f"{item['count']} {item['object_class']}(s)")
    
    return "I have seen: " + ", ".join(parts)

if __name__ == "__main__":
    # Run single detection
    detect_and_log()
    
    # Show summary
    print("\n" + what_do_you_see())
