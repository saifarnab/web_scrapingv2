import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# excel db path
GAMEDB = 'scrap.xlsx'

# log format
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)


def config_driver(maximize_window: bool) -> webdriver.Chrome:
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("lang=en-GB")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--log-level=3")
    # driver = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)
    driver = webdriver.Chrome(options=chrome_options)
    if maximize_window is True:
        driver.maximize_window()
    return driver


def login(driver: webdriver.Chrome):
    driver.get('https://egate.nub.ly/accounts/login/')
    time.sleep(1)
    driver.find_element(By.XPATH, '//input[@name="username"]').send_keys('0927628515')
    driver.find_element(By.XPATH, '//input[@name="password"]').send_keys('wael1988')
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    time.sleep(2)


def booking(driver: webdriver.Chrome):
    driver.get('https://egate.nub.ly/appointments/book/')
    driver.find_element(By.CSS_SELECTOR, "img[alt='موني جرام']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//button[contains(text(),'التالي')]").click()
    time.sleep(1000)


def scanner():
    driver = config_driver(True)
    login(driver)
    booking(driver)


if __name__ == '__main__':
    logging.info('----------------- Script start running ... -----------------')
    scanner()
