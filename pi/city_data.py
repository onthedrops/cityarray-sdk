"""
CITYARRAY City Data Integration
"""

import requests

OPENWEATHER_KEY = "fd9375b142b3e1233b7b2aa0160762b5"

class CityData:
    def __init__(self, city="Los Angeles", state="CA", lat=34.05, lon=-118.24):
        self.city = city
        self.state = state
        self.lat = lat
        self.lon = lon
    
    def get_weather(self):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={OPENWEATHER_KEY}&units=imperial"
            data = requests.get(url, timeout=10).json()
            return {
                "temp_f": round(data["main"]["temp"]),
                "conditions": data["weather"][0]["main"],
                "humidity": data["main"]["humidity"]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_air_quality(self):
        try:
            url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={self.lat}&lon={self.lon}&appid={OPENWEATHER_KEY}"
            data = requests.get(url, timeout=10).json()
            aqi = data["list"][0]["main"]["aqi"]
            levels = {1: "GOOD", 2: "FAIR", 3: "MODERATE", 4: "POOR", 5: "HAZARDOUS"}
            return {"aqi": aqi, "level": levels.get(aqi, "UNKNOWN")}
        except Exception as e:
            return {"error": str(e)}
    
    def get_nws_alerts(self):
        try:
            url = f"https://api.weather.gov/alerts/active?area={self.state}"
            headers = {"User-Agent": "CITYARRAY"}
            data = requests.get(url, headers=headers, timeout=10).json()
            alerts = []
            for feature in data.get("features", [])[:3]:
                props = feature["properties"]
                alerts.append({
                    "event": props.get("event"),
                    "severity": props.get("severity"),
                    "headline": props.get("headline", "")[:80]
                })
            return alerts
        except Exception as e:
            return [{"error": str(e)}]

if __name__ == "__main__":
    city = CityData()
    print("=== Weather ===")
    print(city.get_weather())
    print("\n=== Air Quality ===")
    print(city.get_air_quality())
    print("\n=== NWS Alerts ===")
    for a in city.get_nws_alerts():
        print(a)
