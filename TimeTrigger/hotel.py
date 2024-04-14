from collections import defaultdict
from datetime import datetime

from TimeTrigger.utils.marriott_utils import list_all_dates, marriott_date, month_end, month_start, next_month


BASE_URL = "https://www.marriott.com/search/availabilityCalendar.mi?propertyCode=%s&isSearch=true&costTab=total&fromDate=%s&flexibleDateSearch=true&isFlexibleDatesOptionSelected=true&lengthOfStay=1&roomCount=1&numAdultsPerRoom=1&clusterCode=%s&numberOfRooms=1"

class HotelRate:
    """Rate class to store rate information for a hotel on a given date
    A rate object consists of a date, rate name, price, and the url to book the rate
    """
    def __init__(self, date, rate_code, url):
        self.date = date
        self.rate_code = rate_code
        self.url = url

        self.price = None

    def set_price(self, price):
        self.price = price

    def __str__(self):
        return f"{self.rate_code} on {self.date}: {self.price}"

    def __repr__(self):
        return self.__str__()

class HotelUrl:
    """Url class to store url information for a hotel on a given date
    A url object consists of a date and a url
    """
    def __init__(self):
        self.rate_code = None
        self.url = None # generated url
        self.dates = set()  # included dates
    
    def __str__(self):
        return f"{self.url} on {self.dates}"
    
    def __repr__(self):
        return self.__str__()


class Hotel:
    """Hotel class to store rate information for a hotel rate
    A Hotel object consists of a hotel name and a dictionary of rates
    """
    def __init__(self, name, code, dates, additional_rates):
        self.name = name
        self.code = code
        
        # a list of HotelUrl objects
        self.urls = defaultdict(HotelUrl) # {(datetime, rate): HotelUrl}
        self.__fill_urls(dates, additional_rates)

        # will be filled by the search
        self.rates = defaultdict(list) # a list of results, {date: [HotelRate1, HotelRate2, ...]}
   
    def __fill_urls(self, dates, additional_rates):
        # remove points from the additional rates
        search_points = False
        if "points" in additional_rates:
            additional_rates.remove("points")
            search_points = True

        # add the additional rates to the rates
        rates = ["none", "aaa"] + additional_rates

        # find the months that the dates are in, also merge the dates that are in the same month
        months = self.__find_months_wanted(dates)
        # create a url for each rate in each month, merge the dates that are in the same month
        for url_date, dates in months.items():
            for rate in rates:
                key = (url_date, rate)
                self.urls[key].url = BASE_URL % (self.code, marriott_date(url_date), rate)
                self.urls[key].dates = dates
                self.urls[key].rate_code = rate
            if search_points:
                key = (url_date, "points")
                self.urls[key].url = BASE_URL % (self.code, marriott_date(url_date), "none") + "&useRewardsPoints=true"
                self.urls[key].dates = dates
                self.urls[key].rate_code = "points"

        
    def __find_months_wanted(self, dates):
        """find the months that the dates are in

        Args:
            dates ([{"ciDate":"", "coDate":""}]): a list of ci, co dates

        Returns:
            {datetime:[datetime]}: a dictionary of months and the dates wanted that are in the month
        """
        months = defaultdict(set)
        for d in dates:
            # for each ci, co date, find the months that the dates are in
            ci_date = datetime.strptime(d["ciDate"], '%Y-%m-%d')
            co_date = datetime.strptime(d["coDate"], '%Y-%m-%d')

            # find by a while loop, while through the months 
            cur_month = month_end(ci_date) # last day of the month
            boundary_month = month_end(co_date)
            while cur_month <= boundary_month:
                # prepare month - url need the first day of the month
                url_date = month_start(cur_month)

                # prepare dates
                from_date = max(ci_date, url_date)
                to_date = min(co_date, cur_month)
                dates_wanted = list_all_dates(from_date, to_date)

                months[url_date] = months[url_date].union(dates_wanted)

                # advance to the next month
                cur_month = month_end(next_month(cur_month))
        return months
        
    