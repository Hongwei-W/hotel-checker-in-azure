from datetime import datetime
from enum import Enum
from azure.cosmos import CosmosClient

from TimeTrigger.cosmos_handler import CosmosHandler
from TimeTrigger.hotel import Hotel, HotelRate
from TimeTrigger.utils.marriott_utils import marriott_date


class ChangedStatus(Enum):
    PriceReduced = 1
    PriceIncreased = 2
    RateAdded = 3
    RateRemoved = 4
    

class ChangedRates(HotelRate):
    """store the changed rates
    can infer trip name and hotel name from trip and hotel object in main.py

    Args:
        hotel_rate (HotelRate): the HotelRate object
    """
    def __init__(self, hotel_rate: HotelRate, status: ChangedStatus, last_price=None):
        super().__init__(hotel_rate.date, hotel_rate.rate_code, hotel_rate.url)
        self.price = hotel_rate.price
        self.status = status
        self.last_price = last_price


class DBManager(CosmosHandler):
    def __init__(self, hotel: Hotel, trip_name: str, endpoint, key):
        self.endpoint = endpoint
        self.key = key

        self.database = "marriott"
        self.c_trip_hotel = "tripHotel"
        self.c_date_rates = "dateRates"

        self.client = CosmosClient(self.endpoint, self.key)

        self.changed_rates = [] # a list of ChangedRates objects

        self.hotel = hotel
        self.trip_name = trip_name

        self.trip_hotel_id = f"{self.hotel.code}_{self.trip_name}"

    def __find_trip_hotel(self):
        items = self.get_cosmos_container_items_by_where(self.database, self.c_trip_hotel, {"id": self.trip_hotel_id})
        assert len(items) <= 1, f"Error: multiple items found for {self.hotel.code} in {self.trip_name}"

        # if the item is not found, directly insert it
        if len(items) == 0:
            return None
        return items[0]
    
    def __find_date_rate(self, date: datetime):
        items = self.get_cosmos_container_items_by_where(self.database, self.c_date_rates, {"id": self.__convert_datetime_to_dr_id(date)})
        assert len(items) <= 1, f"Error: multiple items found for {self.hotel.code} in {self.trip_name} on {date}"

        # if the item is not found, directly insert it
        if len(items) == 0:
            return None
        return items[0]
    
    def __create_trip_hotel_object(self):
        trip_hotel = {
            "trip": self.trip_name,
            "hotelCode": self.hotel.code,
            "hotelName": self.hotel.name,
            "id": self.trip_hotel_id,
            # is there a simple self.dates to reference all date?
            # "dates": 
        }
        return trip_hotel

    def __create_date_rate_object(self, date: datetime, rates):
        date_rate = {
            "date": marriott_date(date),
            "rates": [self.__convert_rate_to_dr_rate(rate) for rate in rates],
            "tripHotelFk": self.trip_hotel_id,
            "id": self.__convert_datetime_to_dr_id(date)
        }
        return date_rate

    def __check_update_trip_hotel(self, th):
        if not (self.trip_name == th["trip"] and self.hotel.code == th["hotelCode"] and self.hotel.name == th["hotelName"]):
            th["trip"] = self.trip_name
            th["hotelCode"] = self.hotel.code
            th["hotelName"] = self.hotel.name
            self.update_cosmos_container_item(self.database, self.c_trip_hotel, th)
        return

    def __check_update_date_rate(self, dr, rates):
        need_update = False
        
        if dr.get("tripHotelFk", None) != self.trip_hotel_id:
            dr["tripHotelFk"] = self.trip_hotel_id
            need_update = True
        
        dr_rates_dic = self.__convert_dr_rates_to_dict_by_code(dr["rates"])
        for rate in rates:
            if rate.rate_code not in dr_rates_dic:
                # if the rate is not found, insert the rate
                new_dr_rate = self.__convert_rate_to_dr_rate(rate)
                dr_rates_dic[rate.rate_code] = new_dr_rate
                need_update = True
            else:
                if rate.price > dr_rates_dic[rate.rate_code]["price"]:
                    # if the new rate is more expensive
                    dr_rates_dic[rate.rate_code]["price"] = rate.price
                    need_update = True
                elif rate.price < dr_rates_dic[rate.rate_code]["price"]:
                    # add the rate to the changed_rates
                    self.changed_rates.append(ChangedRates(rate, ChangedStatus.PriceReduced, dr_rates_dic[rate.rate_code]["price"]))
                   
                    # if the new rate is less expensive
                    dr_rates_dic[rate.rate_code]["price"] = rate.price

                    need_update = True
        if need_update:
            dr["rates"] = list(dr_rates_dic.values())
            self.update_cosmos_container_item(self.database, self.c_date_rates, dr)
        return

    def upsert(self):
        # ensure the trip_hotel object is in the database
        th = self.__find_trip_hotel()
        if th is None:
            new_trip_hotel = self.__create_trip_hotel_object()
            self.create_cosmos_container_item(self.database, self.c_trip_hotel, new_trip_hotel)
            # self.changed_rates = [ChangedRates(rate, ChangedStatus.RateAdded) for rate in hotel.rates]
        else:
            self.__check_update_trip_hotel(th)
    
        # ensure the each date_rate is in database
        for date, rates in self.hotel.rates.items():
            dr = self.__find_date_rate(date)
            if dr is None:
                new_date_rate = self.__create_date_rate_object(date, rates)
                self.create_cosmos_container_item(self.database, self.c_date_rates, new_date_rate)
            else:
                self.__check_update_date_rate(dr, rates)

    def __convert_rate_to_dr_rate(self, rate: HotelRate):
        return {"code": rate.rate_code, "price": rate.price}
    
    def __convert_dr_rates_to_dict_by_code(self, rates):
        return {rate["code"]: rate for rate in rates}

    def __convert_datetime_to_dr_id(self, date: datetime):
        return f"{self.trip_hotel_id}_{date.strftime('%d%m%Y')}"
    
    def get_changed_rates(self):
        return self.changed_rates
