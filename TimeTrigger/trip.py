class Trip:
    """Trip class represents a trip with a name and a list of Hotel objects
    """
    def __init__(self, name):
        self.name = name
        self.hotels = [] # a list of hotels
 
    def add_hotel(self, hotel):
        self.hotels.append(hotel)
    
    def __str__(self):
        return f"{self.name}: {self.hotels}"
    