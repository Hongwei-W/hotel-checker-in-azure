import json
import logging
import azure.functions as func
import os

from TimeTrigger.database import DBManager
from TimeTrigger.pushover import NotificationHelper
from TimeTrigger.search import Search
from TimeTrigger.search_info import SearchInfo


PUSHOVER_APP_TOKEN = os.environ.get('PushoverAppToken')
PUSHOVER_USER_GROUP = os.environ.get('PushoverUserGroup')

COSMOSDB_ENDPOINT = os.environ.get('CosmosDBEndpoint')
COSMOSDB_KEY = os.environ.get('CosmosDBKey')

@app.blob_input(arg_name="searchhotels", path='search-hotels/search_hotels.json', connection='AzureWebJobsStorage')
@app.schedule(schedule="0 0 */3 * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def main(myTimer: func.TimerRequest, searchhotels:str) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')
    
    data = json.loads(searchhotels)
    
    nh = NotificationHelper(PUSHOVER_APP_TOKEN, PUSHOVER_USER_GROUP)
    
    search_info = SearchInfo()
    trips = search_info.parse(data)
    
    for trip in trips:
        for hotel in trip.hotels:
            # search
            search = Search(hotel)
            search.search()
            
            # save to db
            db = DBManager(hotel, trip.name, COSMOSDB_ENDPOINT, COSMOSDB_KEY)
            db.upsert()

            # push changed_rates
            changed_rates = db.get_changed_rates()
            nh.push(changed_rates, trip.name, hotel.name)
