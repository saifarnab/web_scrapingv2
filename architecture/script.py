import logging
import os
import re
import time

import openpyxl
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def config_driver(maximize_window: bool) -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument('--headless')
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


def save_items_url(urls: list):
    data = {'URL': urls}
    df = pd.DataFrame(data)
    csv_file_path = '6000_urls.csv'
    df.to_csv(csv_file_path, index=False)
    print(f'Data saved to {csv_file_path}')


def get_items(driver: webdriver.Chrome, postcode: str):
    driver.get('https://members.architecture.com.au/FAA/search-by-location.aspx')
    driver.find_element(By.ID, 'agreeterms').click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//div[@class='mat-select-arrow']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//span[normalize-space()='100km']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//input[@id='txtLocationSearchField']").send_keys(postcode)
    time.sleep(5)
    driver.find_element(By.XPATH, "//span[normalize-space()='Search']").click()

    # items
    time.sleep(10)
    items = []
    pattern = r'window\.open\(\'(\/faa\/faaprofile\?profileid=\d+)\''
    for i in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

    for i in range(5):
        carts = driver.find_elements(By.XPATH, '//div[@class="card-inner"]')
        print(f'Extracting from page = {i + 1}. Found {len(carts)} urls')
        for cart in carts:
            html_string = cart.get_attribute('outerHTML')
            match = re.search(pattern, html_string)
            if match:
                url = match.group(1)
                items.append(url)

        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//button[@aria-label='Next page']//span[@class='mat-button-wrapper']//*[name()='svg']")))

        driver.find_element(By.XPATH,
                            "//button[@aria-label='Next page']//span[@class='mat-button-wrapper']//*[name()='svg']").click()
        time.sleep(3)

    save_items_url(items)


def scanner():
    postcode = '6000'
    driver = config_driver(True)
    get_items(driver, postcode)


def create_excel_with_header(filename: str):
    if os.path.exists(filename) is True:
        return
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(['LINK', 'NAME', 'ADDRESS', 'PHONE', 'EMAIL', 'WEBSITE'])
    workbook.save(filename)


def append_to_excel(data, filename):
    workbook = openpyxl.load_workbook(filename)
    sheet = workbook.active
    for row in data:
        sheet.append(row)
    workbook.save(filename)


def scanner2():
    filename = 'data.xlsx'
    driver = config_driver(True)
    create_excel_with_header(filename)
    df = pd.read_csv('urls.csv')
    for index, row in df.iterrows():
        url = f'https://members.architecture.com.au{row['URL']}'
        driver.get(url)
        try:
            name = driver.find_element(By.ID, "CompanyName").text
        except:
            name = ''
        try:
            address = driver.find_element(By.ID, "CompanyAddress").text
        except:
            address = ''
        try:
            phone = driver.find_elements(By.XPATH, '//div[@id="ContactHeading"]//p')
            phone = phone[0].text
        except:
            phone = ''
        elms = driver.find_elements(By.XPATH, '//div[@id="ContactHeading"]//p//a')
        try:
            mail = elms[0].text
        except:
            mail = ''
        try:
            website = elms[1].text
        except:
            website = ''

        append_to_excel([[url, name, address, phone, mail, website]], filename)
        print(f'{index}. inserted from {url}')


if __name__ == '__main__':
    logging.info('----------------- Script start running ... -----------------')
    scanner2()
