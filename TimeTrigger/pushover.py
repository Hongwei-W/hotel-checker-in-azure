import logging
import requests

from TimeTrigger.database import ChangedStatus
from TimeTrigger.pushover_handler import PushoverHandler
from TimeTrigger.utils.marriott_utils import RATE_CODES


class NotificationHelper(PushoverHandler):
    template = {
        ChangedStatus.PriceReduced: {
            "title": 'Found A Price Drop of a Hotel in {}', # trip.name
            "content": '{} price (rate code {}) on {} has dropped to {} from {}' # hotel.name, rate.rate_code, rate.date, rate.price, rate.last_price
        }
    }

    def __init__(self, app_token, user_group):
        super().__init__(app_token, user_group)
        
    def __set_message(self, cr, trip_name, hotel_name):
        template = self.template[cr.status]
        message = {
            "title": template["title"].format(trip_name),
            "content": template["content"].format(hotel_name, RATE_CODES.get(cr.rate_code, cr.rate_code), self.__convert_to_date_str(cr.date), cr.price, cr.last_price)
        }
        return message
        
    def __convert_to_date_str(self, date):
        return date.strftime('%Y-%m-%d')
            
    def push(self, data, trip_name, hotel_name):
        for cr in data:
            message = self.__set_message(cr, trip_name, hotel_name)
            resp = self.send_message(message)
            
            try:
                resp.raise_for_status()
            except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
                logging.error(f'HTTP error [{e}]')
                # TODO logging
            logging.info(f'Successfully sent notification with resp status [{resp.status_code}] (original payload [{message}])')