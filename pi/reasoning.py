"""
CITYARRAY Reasoning Engine
Uses Ollama LLM for decisions
"""

import subprocess

def ask_llm(prompt, model="phi3:mini"):
    """Query the local LLM."""
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "TIMEOUT"

def reason_about_scene(detections):
    """Given detections, decide what to do."""
    if not detections:
        return "SCANNING", "informational", "No objects"
    
    # Simple prompt
    top = detections[0]['class']
    prompt = f"One word safety level for seeing a {top}: safe, caution, or danger?"
    
    response = ask_llm(prompt)
    
    # Map response to tier
    response_lower = response.lower()
    if "danger" in response_lower:
        tier = "emergency"
    elif "caution" in response_lower:
        tier = "warning"
    else:
        tier = "informational"
    
    message = top.upper()
    return message, tier, response

if __name__ == "__main__":
    test = [{"class": "person", "confidence": 0.85}]
    
    print("Testing reasoning (may take 60+ seconds)...")
    message, tier, response = reason_about_scene(test)
    print(f"Message: {message}")
    print(f"Tier: {tier}")
    print(f"LLM said: {response}")
