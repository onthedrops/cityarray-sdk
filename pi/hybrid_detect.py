"""
CITYARRAY Hybrid Detector
Fast YOLO + Deep VLM when needed
"""

import time
from hailo_detect import HailoDetector
from vlm_detect import describe_scene, analyze_for_safety, capture
from database import log_detection, get_recent_detections

class HybridDetector:
    def __init__(self):
        print("Loading Hailo detector...")
        self.hailo = HailoDetector()
        self.last_objects = set()
        self.person_count = 0
        self.vlm_cooldown = 0
        self.last_vlm_time = 0
        print("Hybrid detector ready!")
    
    def fast_scan(self):
        """Quick YOLO scan (35ms)."""
        img = self.hailo.capture()
        dets = self.hailo.detect(img, conf_threshold=0.25)
        return dets, img
    
    def should_trigger_vlm(self, detections):
        """Decide if VLM analysis is needed."""
        if not detections:
            return False, None
        
        # Cooldown: don't run VLM more than once per 60 seconds
        if time.time() - self.last_vlm_time < 60:
            return False, None
        
        current_objects = set(d['class'] for d in detections)
        person_count = sum(1 for d in detections if d['class'] == 'person')
        
        # Trigger 1: New object type appeared
        new_objects = current_objects - self.last_objects
        if new_objects:
            self.last_objects = current_objects
            return True, f"New object: {new_objects}"
        
        # Trigger 2: Person count changed significantly
        if abs(person_count - self.person_count) >= 2:
            self.person_count = person_count
            return True, f"Person count changed to {person_count}"
        
        # Trigger 3: Potential danger objects
        danger_objects = {'knife', 'scissors', 'fire hydrant'}
        if current_objects & danger_objects:
            return True, f"Potential concern: {current_objects & danger_objects}"
        
        self.last_objects = current_objects
        self.person_count = person_count
        return False, None
    
    def deep_analyze(self, image_path):
        """Run VLM for scene understanding."""
        self.last_vlm_time = time.time()
        return analyze_for_safety(image_path)
    
    def scan(self):
        """Main scan: fast + conditional deep."""
        # Fast scan
        dets, img = self.fast_scan()
        
        result = {
            "detections": dets,
            "image": img,
            "vlm_triggered": False,
            "vlm_analysis": None,
            "tier": "informational"
        }
        
        if dets:
            # Check if VLM needed
            trigger, reason = self.should_trigger_vlm(dets)
            
            if trigger:
                print(f"VLM triggered: {reason}")
                result["vlm_triggered"] = True
                result["vlm_analysis"] = self.deep_analyze(img)
                
                # Determine tier from VLM
                if result["vlm_analysis"]:
                    analysis_lower = result["vlm_analysis"].lower()
                    if "danger" in analysis_lower:
                        result["tier"] = "emergency"
                    elif "caution" in analysis_lower:
                        result["tier"] = "warning"
        
        return result
    
    def force_vlm(self):
        """Force VLM analysis (for voice queries)."""
        img = self.hailo.capture()
        print("Analyzing scene...")
        analysis = analyze_for_safety(img)
        return analysis, img
    
    def close(self):
        self.hailo.close()


if __name__ == "__main__":
    detector = HybridDetector()
    
    print("\n=== Hybrid Detection Demo ===")
    print("Running 5 scans...\n")
    
    for i in range(5):
        print(f"Scan {i+1}:")
        result = detector.scan()
        
        if result["detections"]:
            objects = [d['class'] for d in result["detections"]]
            print(f"  YOLO (35ms): {objects}")
        else:
            print("  YOLO: No objects")
        
        if result["vlm_triggered"]:
            print(f"  VLM: {result['vlm_analysis'][:100]}...")
            print(f"  Tier: {result['tier']}")
        
        print()
        time.sleep(2)
    
    detector.close()
    print("Done!")
