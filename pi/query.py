"""
CITYARRAY Query Handler
Answers questions using LLM + detections
"""

import subprocess
from database import get_recent_detections, get_detection_summary

def ask_llm(prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", "phi3:mini", prompt],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.stdout.strip()
    except:
        return "I couldn't process that."

def what_do_you_see():
    """Answer: What do you see?"""
    recent = get_recent_detections(5)
    if not recent:
        return "I haven't detected anything recently."
    
    objects = [r['object_class'] for r in recent]
    return f"I see: {', '.join(objects)}"

def ask_about_scene(question):
    """Use LLM to answer complex questions."""
    summary = get_detection_summary()
    
    if not summary:
        context = "No objects detected yet."
    else:
        context = "Detected: " + ", ".join([f"{s['object_class']} ({s['count']}x)" for s in summary])
    
    prompt = f"""Context: {context}
Question: {question}
Answer in one short sentence:"""
    
    return ask_llm(prompt)

if __name__ == "__main__":
    print("Quick query:")
    print(what_do_you_see())
    
    print("\nLLM query (wait 30-60 sec):")
    print(ask_about_scene("Is the area safe?"))
