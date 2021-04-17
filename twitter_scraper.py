import logging

# create logger
logger = logging.getLogger('twitter_scrapper')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

# debug, info, warning, error, critical
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime
import json

class TwitterScrapper:

    def __init__(self):
        options = Options()
        webdriver.ChromeOptions()
        # options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        
        # Set implicit 10 second wait 
        # Will wait automatically for 10secs if element not present
        driver.implicitly_wait(10)

    def login():
        logger.info("Logging into Twitter")
        driver.get("https://twitter.com/login")
        
        try:
            # Username
            print("username")
            username = driver.find_element_by_xpath('//input[@name="session[username_or_email]"]')
            username.send_keys('frank.tran@live.ca')
            # Password
            print("password")
            password = driver.find_element_by_xpath('//input[@name="session[password]"]')
            password.send_keys('Twitter@2056', Keys.RETURN)

        except Exception as e:
            logger.error(e)
            logger.error('Unable to Login')

    # 
    def searchTwitter():
        
        pass


TwitterScrapper()
