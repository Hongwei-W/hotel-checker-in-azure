# from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from TimeTrigger.hotel import HotelRate
# from TimeTrigger.selenium_debug import SeleniumWithAzureBlob
from TimeTrigger.utils.selenium_utils import random_sleep, scroll_to_the_bottom

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class Search:
    """Search class to search for the rates of a hotel
    It search ONE hotel object
    """
    def __init__(self, hotel):
        self.hotel = hotel
        # self.blob_client = blob_client

        self.tasks = self.hotel.urls.values() # a list of HotelUrl objects
    
    def search(self):
        retry = 0 # only 3 retries for all tasks
        for task in self.tasks:
            # for each url of the rates of the month, get the rates of the dates
            while retry < 3:
                try:
                    logging.debug(f"Searching {self.hotel.name} for {task.url}, retry: {retry}")
                    random_sleep()
                    self.__each_task(task)
                except Exception as e:
                    logging.error(f"Error: {self.hotel.name} failed to search, error [{e}], retry: {retry}")
                    retry += 1
                else:
                    break
             
    
    def __each_task(self, task):
        """find rate for each url (namely each date within that month)

        Args:
            task (_type_): _description_
        """
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--window-size=1920,1080")
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        chrome_options.add_argument(f'user-agent={user_agent}')

        service = Service(executable_path="/usr/local/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # selenium_debug = SeleniumWithAzureBlob(driver, self.blob_client, "selenium-debug")
        
        driver.get(task.url)
        scroll_to_the_bottom(driver)
        
        waited = False
        for date in task.dates: # it is guaranteed that the date is in this month
            # save those rates to the hotel object
            rate = HotelRate(date, task.rate_code, task.url)

            if not waited:
                WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, f"//div[@aria-label='{date.strftime('%a %b %d %Y')}']")))
                # selenium_debug.save_screenshot(f"/tmp/{datetime.now()}_{self.hotel.name}_{date.strftime('%Y-%m-%d')}.png")
                # selenium_debug.save_html(f"/tmp/{datetime.now()}_{self.hotel.name}_{date.strftime('%Y-%m-%d')}.html")
                # selenium_debug.save_page_source(f"/tmp/{datetime.now()}_{self.hotel.name}_{date.strftime('%Y-%m-%d')}.txt")
                waited = True
            e = driver.find_element(by=By.XPATH, value=f"//div[@aria-label='{date.strftime('%a %b %d %Y')}']")
            price = e.find_element(by=By.CLASS_NAME, value='price-section').text
            price = self.__handle_search_price(price)
            
            if price == -1:
                # if the price is not available or cannot retrieve, skip this date
                continue
        
            rate.set_price(price)
            self.hotel.rates[date].append(rate)

    def __handle_search_price(self, price):
        """convert price text as integer, if is not available, return -1; if is other string, log a warning

        Args:
            price (str): original price text

        Returns:
            int: converted price as int, or -1 as not available or invalid
        """
        if price == '-' or price == 'Not available for check-in':
            return -1

        try:
            price = int(price.replace(',', ''))
        except ValueError as e:
            logging.warning(f"Error: {price} is not a valid price")
            price = -1
        return price