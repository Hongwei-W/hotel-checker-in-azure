import datetime
import logging

import azure.functions as func
from selenium import webdriver
from selenium.webdriver.common.by import By
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from selenium.webdriver.chrome.service import Service
import datetime
import os

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    service = Service(executable_path="/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get('http://www.ubuntu.com/')
    links = driver.find_elements(By.TAG_NAME, "a")
    link_list = ""
    for link in links:
        if link_list == "":
            link_list = link.text
        else:
            link_list = link_list + ", " + link.text
    print(link_list)
    logging.debug(link_list)
    logging.info(link_list)
    logging.warning(link_list)
    # create blob service client and container client
    # credential = DefaultAzureCredential()
    # storage_account_url = "https://" + os.environ["par_storage_account_name"] + ".blob.core.windows.net"
    # client = BlobServiceClient(account_url=storage_account_url, credential=credential)
    # blob_name = "test" + str(datetime.datetime.now()) + ".txt"
    # blob_client = client.get_blob_client(container=os.environ["par_storage_container_name"], blob=blob_name)
    # blob_client.upload_blob(link_list)