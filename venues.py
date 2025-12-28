"""
CITYARRAY Venue Context
Location-aware emergency procedures
"""

VENUES = {
    "city_hall": {
        "name": "Los Angeles City Hall",
        "address": "200 N Spring St, Los Angeles, CA 90012",
        "capacity": 500,
        "exits": {
            "north": "Temple St Exit",
            "south": "1st St Exit", 
            "east": "Main St Exit",
            "west": "Spring St Exit"
        },
        "languages": ["en", "es", "zh", "ko", "vi", "tl", "hy"],
        "hazards": ["earthquake zone", "protest gathering point"],
        "procedures": {
            "earthquake": "DROP COVER HOLD - Evacuate to Grand Park after shaking stops",
            "fire": "Use nearest stairwell - Do not use elevators - Meet at Grand Park",
            "active_threat": "RUN HIDE FIGHT - Exit away from threat - Call 911",
            "air_quality": "Shelter in place - Close windows - Await all clear"
        },
        "assembly_point": "Grand Park - Near fountain"
    },
    
    "staples_center": {
        "name": "Crypto.com Arena",
        "address": "1111 S Figueroa St, Los Angeles, CA 90015",
        "capacity": 20000,
        "exits": {
            "north": "Gate A - Figueroa St",
            "south": "Gate C - Chick Hearn Ct",
            "east": "Gate B - LA Live Way",
            "west": "Gate D - Figueroa St"
        },
        "languages": ["en", "es", "zh", "ko", "ja"],
        "hazards": ["crowd crush risk", "limited vehicle egress", "high density"],
        "procedures": {
            "earthquake": "STAY SEATED until shaking stops - Follow staff to exits",
            "fire": "Walk to nearest exit - Do not run - Staff will direct",
            "active_threat": "RUN to nearest exit or HIDE under seats",
            "crowd_surge": "Move to sides - Protect chest - Stay on feet"
        },
        "assembly_point": "LA Live plaza - By Starbucks"
    },
    
    "lax_terminal": {
        "name": "LAX Terminal 4",
        "address": "Los Angeles International Airport",
        "capacity": 5000,
        "exits": {
            "arrivals": "Lower level curbside",
            "departures": "Upper level curbside",
            "emergency": "Tarmac access - Staff only"
        },
        "languages": ["en", "es", "zh", "ko", "ja", "tl", "vi", "hi", "ar", "fr"],
        "hazards": ["security zone", "aircraft proximity", "international travelers"],
        "procedures": {
            "earthquake": "Move away from windows - Follow TSA instructions",
            "fire": "Exit to curbside - Do not use escalators",
            "active_threat": "RUN to exits or HIDE - Follow law enforcement",
            "security": "Shelter in place - Await TSA all clear"
        },
        "assembly_point": "Terminal 4 parking structure Level 1"
    },
    
    "demo_site": {
        "name": "Demo Location",
        "address": "Conference Room",
        "capacity": 50,
        "exits": {
            "main": "Main door",
            "emergency": "Side exit"
        },
        "languages": ["en", "es", "zh", "ko", "vi"],
        "hazards": [],
        "procedures": {
            "earthquake": "DROP COVER HOLD - Exit when safe",
            "fire": "Exit immediately - Use stairs",
            "active_threat": "RUN HIDE FIGHT"
        },
        "assembly_point": "Building lobby"
    }
}

class VenueContext:
    def __init__(self, venue_id="demo_site"):
        self.venue_id = venue_id
        self.venue = VENUES.get(venue_id, VENUES["demo_site"])
    
    def get_procedure(self, emergency_type):
        """Get procedure for emergency type."""
        return self.venue["procedures"].get(emergency_type, "Follow staff instructions")
    
    def get_nearest_exit(self, direction=None):
        """Get exit information."""
        exits = self.venue["exits"]
        if direction and direction in exits:
            return exits[direction]
        return list(exits.values())[0]
    
    def get_languages(self):
        """Get languages for this venue."""
        return self.venue["languages"]
    
    def get_capacity(self):
        """Get venue capacity."""
        return self.venue["capacity"]
    
    def get_assembly_point(self):
        """Get assembly point."""
        return self.venue.get("assembly_point", "Safe area outside")
    
    def generate_alert(self, emergency_type):
        """Generate location-aware alert."""
        procedure = self.get_procedure(emergency_type)
        assembly = self.get_assembly_point()
        
        return {
            "venue": self.venue["name"],
            "type": emergency_type,
            "message": procedure,
            "assembly": assembly,
            "languages": self.get_languages()
        }


if __name__ == "__main__":
    print("=== Venue Context Demo ===\n")
    
    for venue_id in ["city_hall", "staples_center", "demo_site"]:
        venue = VenueContext(venue_id)
        print(f"Venue: {venue.venue['name']}")
        print(f"Capacity: {venue.get_capacity()}")
        print(f"Languages: {', '.join(venue.get_languages())}")
        
        alert = venue.generate_alert("earthquake")
        print(f"Earthquake procedure: {alert['message'][:60]}...")
        print(f"Assembly: {alert['assembly']}")
        print()
