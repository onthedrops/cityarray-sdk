"""
CITYARRAY Audio Module
Text-to-speech for alerts
"""

import subprocess

DEVICE = "plughw:2,0"

# Language codes for espeak
ESPEAK_VOICES = {
    "en": "en",
    "es": "es",
    "zh": "zh",
    "ko": "ko",
    "vi": "vi"
}

def speak(text, lang="en"):
    """Speak text in specified language."""
    voice = ESPEAK_VOICES.get(lang, "en")
    try:
        cmd = f'espeak -v {voice} "{text}" --stdout | aplay -D {DEVICE} -q'
        subprocess.run(cmd, shell=True, timeout=30)
        return True
    except Exception as e:
        print(f"TTS error: {e}")
        return False

def speak_multilingual(messages):
    """Speak message in all available languages."""
    for lang, text in messages.items():
        if lang in ESPEAK_VOICES:
            print(f"  [{lang}] {text}")
            speak(text, lang)

def alert(text):
    """Speak alert in English."""
    speak(text, "en")

if __name__ == "__main__":
    print("Testing TTS...\n")
    
    print("English:")
    speak("Emergency alert system ready", "en")
    
    print("Spanish:")
    speak("Sistema de alerta listo", "es")
    
    print("Multilingual test:")
    speak_multilingual({
        "en": "Earthquake",
        "es": "Terremoto",
        "zh": "Di zhen",
        "ko": "Jijin",
        "vi": "Dong dat"
    })
    
    print("\nDone!")
