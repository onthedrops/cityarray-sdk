"""
CITYARRAY City Demo
Full demonstration for city officials
"""

import time
import sys
from led_simulator import LEDSimulator
from hailo_detect import HailoDetector
from city_data import CityData
from venues import VenueContext
from scenarios import ScenarioPlayer, SCENARIOS
from database import get_detection_summary

class CityDemo:
    def __init__(self, venue_id="demo_site"):
        print("=== CITYARRAY City Demo ===\n")
        print("Initializing components...")
        
        self.display = LEDSimulator()
        self.detector = HailoDetector()
        self.city = CityData()
        self.venue = VenueContext(venue_id)
        self.scenarios = ScenarioPlayer()
        
        self.person_count = 0
        self.running = True
        
        print(f"Venue: {self.venue.venue['name']}")
        print(f"Languages: {', '.join(self.venue.get_languages())}")
        print("\nReady!\n")
    
    def show_message(self, text, color, duration=2):
        """Display message with language rotation."""
        self.display.clear()
        if len(text) > 10:
            text = text[:10]
        self.display.draw_text_centered(text, color)
        self.display.render()
        time.sleep(duration)
    
    def show_scenario(self, scenario_id):
        """Play scenario with all languages."""
        scenario = SCENARIOS.get(scenario_id)
        if not scenario:
            return
        
        print(f"\n>>> {scenario['name'].upper()} <<<")
        
        tier = scenario["tier"]
        colors = {
            "emergency": (255, 0, 0),
            "warning": (255, 191, 0),
            "advisory": (0, 255, 0),
            "informational": (0, 100, 255)
        }
        color = colors.get(tier, (0, 100, 255))
        
        # Rotate through languages
        for lang, msg in scenario["messages"].items():
            print(f"  [{lang}] {msg}")
            self.show_message(msg[:10], color, duration=1.5)
            
            if not self.display.process_events():
                return
    
    def show_weather(self):
        """Display current weather."""
        print("\nFetching weather...")
        weather = self.city.get_weather()
        
        if "error" not in weather:
            msg = f"{weather['temp_f']}F {weather['conditions']}"
            print(f"Weather: {msg}")
            self.show_message(msg[:10], (0, 100, 255), duration=3)
        else:
            print(f"Weather error: {weather['error']}")
    
    def show_air_quality(self):
        """Display air quality."""
        print("\nFetching air quality...")
        aqi = self.city.get_air_quality()
        
        if "error" not in aqi:
            level = aqi["level"]
            print(f"Air Quality: {level}")
            
            colors = {
                "GOOD": (0, 255, 0),
                "FAIR": (0, 255, 0),
                "MODERATE": (255, 191, 0),
                "POOR": (255, 100, 0),
                "HAZARDOUS": (255, 0, 0)
            }
            color = colors.get(level, (255, 191, 0))
            self.show_message(f"AQI {level}", color, duration=3)
        else:
            print(f"AQI error: {aqi['error']}")
    
    def show_nws_alerts(self):
        """Display real NWS alerts."""
        print("\nFetching NWS alerts...")
        alerts = self.city.get_nws_alerts()
        
        if alerts and "error" not in alerts[0]:
            for alert in alerts[:2]:
                severity = alert["severity"]
                event = alert["event"]
                print(f"[{severity}] {event}")
                
                tier = self.city.get_alert_tier(severity)
                colors = {
                    "emergency": (255, 0, 0),
                    "warning": (255, 191, 0),
                    "advisory": (0, 255, 0),
                    "informational": (0, 100, 255)
                }
                color = colors.get(tier, (255, 191, 0))
                
                # Show shortened event name
                short = event[:10].upper()
                self.show_message(short, color, duration=3)
        else:
            print("No active alerts")
            self.show_message("NO ALERTS", (0, 255, 0), duration=2)
    
    def detect_and_count(self):
        """Run detection and count people."""
        dets = self.detector.detect(self.detector.capture(), conf_threshold=0.25)
        
        self.person_count = sum(1 for d in dets if d['class'] == 'person')
        
        if dets:
            objects = [d['class'] for d in dets]
            print(f"Detected: {objects}")
        
        # Show count
        capacity = self.venue.get_capacity()
        percent = (self.person_count / capacity) * 100
        
        if percent > 100:
            self.show_message("OVER CAP", (255, 0, 0), duration=2)
        elif percent > 80:
            self.show_message(f"{self.person_count} PEOPLE", (255, 191, 0), duration=2)
        else:
            self.show_message(f"{self.person_count} PEOPLE", (0, 100, 255), duration=2)
        
        return dets
    
    def run_demo_script(self):
        """Run the full demo script."""
        print("\n" + "="*50)
        print("CITYARRAY CITY DEMO - STARTING")
        print("="*50 + "\n")
        
        # 1. Startup
        print("1. System startup...")
        self.show_scenario("8")  # System Ready
        
        # 2. Detection
        print("\n2. Live detection...")
        self.detect_and_count()
        time.sleep(1)
        
        # 3. Weather
        print("\n3. Weather data...")
        self.show_weather()
        
        # 4. Air Quality
        print("\n4. Air quality...")
        self.show_air_quality()
        
        # 5. NWS Alerts
        print("\n5. Real NWS alerts...")
        self.show_nws_alerts()
        
        # 6. Emergency Scenarios
        print("\n6. Emergency scenarios...")
        self.show_scenario("1")  # Earthquake
        time.sleep(1)
        self.show_scenario("3")  # Fire
        
        # 7. All Clear
        print("\n7. All clear...")
        self.show_scenario("7")
        
        print("\n" + "="*50)
        print("DEMO COMPLETE")
        print("="*50)
    
    def interactive_mode(self):
        """Interactive demo with keyboard controls."""
        print("\n=== Interactive Mode ===")
        print("Keys:")
        print("  1-8: Play scenario")
        print("  W: Weather")
        print("  A: Air quality")
        print("  N: NWS alerts")
        print("  D: Detect")
        print("  R: Run full demo")
        print("  Q: Quit")
        print()
        
        self.scenarios.list_scenarios()
        
        while self.running:
            if not self.display.process_events():
                break
            
            self.display.render()
            self.display.tick(30)
    
    def cleanup(self):
        """Clean up resources."""
        self.display.quit()
        self.detector.close()


if __name__ == "__main__":
    demo = CityDemo(venue_id="demo_site")
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--auto":
            demo.run_demo_script()
        else:
            demo.run_demo_script()
            # demo.interactive_mode()  # Uncomment for interactive
    except KeyboardInterrupt:
        print("\n\nDemo stopped.")
    finally:
        demo.cleanup()
