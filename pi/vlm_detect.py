"""
CITYARRAY VLM Detector
Uses Moondream for scene understanding
"""

import subprocess
import base64
from datetime import datetime
from pathlib import Path
from database import log_detection

IMAGE_DIR = Path.home() / "pi" / "images"
IMAGE_DIR.mkdir(exist_ok=True)

def capture():
    """Capture image from Pi camera."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = IMAGE_DIR / f"vlm_{timestamp}.jpg"
    subprocess.run([
        "rpicam-still", "-o", str(path),
        "-t", "500", "--nopreview", "--ev", "1"
    ], capture_output=True)
    return path

def image_to_base64(image_path):
    """Convert image to base64 string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def describe_scene(image_path, prompt="Describe what you see in this image in one sentence."):
    """Use Moondream VLM to describe the scene."""
    try:
        # Ollama vision format
        result = subprocess.run([
            "ollama", "run", "moondream",
            f"[img]{image_path}[/img] {prompt}"
        ], capture_output=True, text=True, timeout=120)
        
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Scene analysis timed out."
    except Exception as e:
        return f"Error: {e}"

def analyze_for_safety(image_path):
    """Analyze scene for safety concerns."""
    prompt = """Look at this image and answer:
1. What objects and people do you see?
2. Is there any danger (fire, smoke, weapons, crowd crush)?
3. Safety level: SAFE, CAUTION, or DANGER?

Be brief."""
    
    return describe_scene(image_path, prompt)

def detect_and_describe():
    """Capture and analyze scene."""
    print("Capturing image...")
    image_path = capture()
    
    print("Analyzing scene (30-60 seconds)...")
    description = describe_scene(image_path)
    
    print(f"\nScene: {description}")
    
    # Log to database
    log_detection("vlm_scene", 1.0, str(image_path))
    
    return description, image_path

def safety_check():
    """Full safety analysis."""
    print("Capturing image...")
    image_path = capture()
    
    print("Analyzing safety (60-90 seconds)...")
    analysis = analyze_for_safety(image_path)
    
    print(f"\nAnalysis:\n{analysis}")
    
    # Determine tier from response
    analysis_lower = analysis.lower()
    if "danger" in analysis_lower:
        tier = "emergency"
    elif "caution" in analysis_lower:
        tier = "warning"
    else:
        tier = "informational"
    
    print(f"\nTier: {tier}")
    return analysis, tier, image_path


if __name__ == "__main__":
    print("=== VLM Scene Detection ===\n")
    
    print("1. Quick description:")
    desc, path = detect_and_describe()
    
    print("\n" + "="*40 + "\n")
    
    print("2. Safety analysis:")
    analysis, tier, path = safety_check()
