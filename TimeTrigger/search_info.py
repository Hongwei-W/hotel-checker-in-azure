from TimeTrigger.hotel import Hotel
from TimeTrigger.trip import Trip


class SearchInfo:
    """SearchInfo class to store search information
    It parse the search information from the user JSON input
    """
    def __init__(self):
        # self.properties = []
        # self.ci_date = datetime.strptime(ci_date, '%Y-%m-%d')
        # self.co_date = datetime.strptime(co_date, '%Y-%m-%d')
        # self.rates = ['aaa'] + rates
        pass
    
    def parse(self, trips):
        ts = []
        for t in trips:
            # create a trip object
            trip = Trip(t["tripName"])
            for h in t["hotels"]:
                # create a hotel object
                hotel = Hotel(h["hotelName"], h["hotelCode"], h["dates"], h.get("rates", []))
                trip.add_hotel(hotel)
            ts.append(trip)
        return ts
    