"""
CITYARRAY City Data Integration
Weather, Air Quality, NWS Alerts
"""

import requests
from datetime import datetime

# Free API keys - sign up at:
# https://openweathermap.org/api (weather)
# https://docs.airnowapi.org/ (air quality - free for gov)

OPENWEATHER_KEY = fd9375b142b3e1233b7b2aa0160762b5"  # Get free key

class CityData:
    def __init__(self, city="Los Angeles", state="CA", lat=34.05, lon=-118.24):
        self.city = city
        self.state = state
        self.lat = lat
        self.lon = lon
    
    def get_weather(self):
        """Get current weather."""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={fd9375b142b3e1233b7b2aa0160762b5}&units=imperial"
            data = requests.get(url, timeout=10).json()
            
            return {
                "temp_f": round(data["main"]["temp"]),
                "conditions": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_mph": round(data["wind"]["speed"])
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_air_quality(self):
        """Get AQI from OpenWeather."""
        try:
            url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={self.lat}&lon={self.lon}&appid={fd9375b142b3e1233b7b2aa0160762b5}"
            data = requests.get(url, timeout=10).json()
            
            aqi = data["list"][0]["main"]["aqi"]
            # 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor
            levels = {1: "GOOD", 2: "FAIR", 3: "MODERATE", 4: "POOR", 5: "HAZARDOUS"}
            
            return {
                "aqi": aqi,
                "level": levels.get(aqi, "UNKNOWN"),
                "pm25": data["list"][0]["components"]["pm2_5"]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_nws_alerts(self):
        """Get real NWS alerts for state."""
        try:
            url = f"https://api.weather.gov/alerts/active?area={self.state}"
            headers = {"User-Agent": "CITYARRAY Emergency System"}
            data = requests.get(url, headers=headers, timeout=10).json()
            
            alerts = []
            for feature in data.get("features", [])[:5]:  # Top 5
                props = feature["properties"]
                alerts.append({
                    "event": props.get("event", "Unknown"),
                    "headline": props.get("headline", ""),
                    "severity": props.get("severity", "Unknown"),
                    "urgency": props.get("urgency", "Unknown"),
                    "areas": props.get("areaDesc", ""),
                    "expires": props.get("expires", "")
                })
            return alerts
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_alert_tier(self, severity):
        """Map NWS severity to our tier."""
        mapping = {
            "Extreme": "emergency",
            "Severe": "emergency",
            "Moderate": "warning",
            "Minor": "advisory",
            "Unknown": "informational"
        }
        return mapping.get(severity, "informational")


if __name__ == "__main__":
    city = CityData()
    
    print("=== Weather ===")
    weather = city.get_weather()
    if "error" not in weather:
        print(f"{weather['temp_f']}°F, {weather['conditions']}")
    else:
        print(f"Error: {weather['error']}")
    
    print("\n=== Air Quality ===")
    aqi = city.get_air_quality()
    if "error" not in aqi:
        print(f"AQI Level: {aqi['level']} (PM2.5: {aqi['pm25']})")
    else:
        print(f"Error: {aqi['error']}")
    
    print("\n=== NWS Alerts ===")
    alerts = city.get_nws_alerts()
    if alerts and "error" not in alerts[0]:
        for a in alerts:
            print(f"[{a['severity']}] {a['event']}: {a['headline'][:80]}...")
    else:
        print("No active alerts or error fetching")
