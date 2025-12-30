"""
CITYARRAY Venue Context
"""

VENUES = {
    "city_hall": {
        "name": "Los Angeles City Hall",
        "capacity": 500,
        "languages": ["en", "es", "zh", "ko", "vi"],
        "assembly": "Grand Park"
    },
    "demo_site": {
        "name": "Demo Location",
        "capacity": 50,
        "languages": ["en", "es", "zh", "ko", "vi"],
        "assembly": "Building lobby"
    }
}

class VenueContext:
    def __init__(self, venue_id="demo_site"):
        self.venue = VENUES.get(venue_id, VENUES["demo_site"])
    
    def get_capacity(self):
        return self.venue["capacity"]
    
    def get_languages(self):
        return self.venue["languages"]
    
    def get_assembly(self):
        return self.venue["assembly"]

if __name__ == "__main__":
    v = VenueContext("city_hall")
    print(f"Venue: {v.venue['name']}")
    print(f"Capacity: {v.get_capacity()}")
    print(f"Assembly: {v.get_assembly()}")
