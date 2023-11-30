import time

import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def config_driver() -> webdriver.Chrome:
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
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def update_file(row_index, val1, val2):
    try:
        file_path = 'file.xlsx'
        sheet_name = 'Sheet1'
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df.at[row_index, 'Product Overview'] = str(val1)
        df.at[row_index, 'Img Found'] = str(val2)

        df.to_excel(file_path, sheet_name=sheet_name, index=False)
        print(f"Column updated for row {row_index} in Excel file.")
    except Exception as e:
        print(f"An error occurred: {e}")


def read_file():
    file_path = 'file.xlsx'
    sheet_name = 'Sheet1'
    column_names = ['Sales org', 'Dist channel', 'Active', 'Valid from', 'Valid to', 'Category Path', 'Manufacturer',
                    'ManufacturerFilter', 'Product ID', 'SAP Code', 'Marketing Text', 'product Range Name',
                    'Product  Name', 'Material Title', 'Pop Up Page Material Title', 'Additional Information',
                    'Pack Contents', 'Pack Size', 'Brand', 'BrandFilter', 'VendorCode', 'Type', 'Shade', 'Spill',
                    'Best Sellers', 'Image Name', 'SDS Sheet', 'Key Word 1', 'Key Word 2', 'Key Word 3',
                    'Wrights Exclusive Products', 'PDF']
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        selected_columns = df[df.columns.tolist()]
        return selected_columns
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def wright_dental_save_img(link: str, pro_id: str) -> str:
    try:
        response = requests.get(link)
        img_ext = link.split('.')[-1]
        path = f'asset/{pro_id}.{img_ext}'
        if response.status_code == 200:
            with open(path, 'wb') as file:
                file.write(response.content)
            return 'Found'
        else:
            return 'Not Found'
    except Exception as e:
        return 'Not Found'


def my_wright_place_save_img(link: str, pro_id: str) -> str:
    try:
        response = requests.get(link)
        img_ext = link.split('?')[0].split('.')[-1]
        path = f'asset/{pro_id}.{img_ext}'
        if response.status_code == 200:
            with open(path, 'wb') as file:
                file.write(response.content)
            return 'Found'
        else:
            return 'Not Found'
    except Exception as e:
        return 'Not Found'


def wright_dental(driver: webdriver.Chrome, key: str, p_id, row_index: int) -> bool:
    try:
        driver.get(f'https://wrightdental.co.uk/en/search?q={key}')
        time.sleep(2)
        product_xpath = '//div[@class="PublicProductListItemstyles__PublicProductListItemContainer-sc-12kch60-0 gbbJes"]//a'
        no_xpath = '//h1[@class="NoDataToDisplaystyles__Heading-sc-1tn253l-2 VVARl"]'
        no_products = driver.find_elements(By.XPATH, no_xpath)
        if len(no_products) > 0:
            return False
        try:
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, product_xpath)))
        except:
            return False
        products = driver.find_elements(By.XPATH, product_xpath)
        for product in products:
            p_link = product.get_attribute('href')
            if p_link.split('=')[-1] == p_id:
                driver.get(p_link)
                img_xpath = '//div[@class="Gallerystyles__MainItemContainer-sc-cp026m-1 dHFiOX"]//img'
                try:
                    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, img_xpath)))
                    img_link = driver.find_element(By.XPATH, img_xpath).get_attribute('src')
                    found = wright_dental_save_img(img_link, product_id)
                except:
                    found = 'Not Found'
                try:
                    p_overview_xpath = '//p[@class="AttributeContentBlockstyles__AttributeContentBlockSummary-sc-13hmukp-2 sDuEe"]'
                    p_overview = driver.find_element(By.XPATH, p_overview_xpath).text
                except:
                    p_overview = ''
                update_file(row_index, p_overview, found)
                print(f'{row_index} Found')
                return True
        return False
    except Exception as e:
        print(e)
        print(f'{row_index} Not Found')
        update_file(row_index, '', 'Not found')
        return False


def my_wright_place(driver: webdriver.Chrome, pro_id: str, row_index: int):
    try:
        driver.get('https://www.mywrightplace.co.za/logon')
        driver.find_element(By.XPATH, '//input[@name="email"]').send_keys('celeste@wright-millners.co.za')
        driver.find_element(By.XPATH, '//input[@name="password"]').send_keys('Friday14')
        driver.find_element(By.ID, 'logonButton').click()
        time.sleep(3)
        driver.find_element(By.ID, 'productSearch').send_keys(pro_id)
        driver.find_element(By.ID, 'searchButton').click()
        time.sleep(3)
        products = driver.find_elements(By.XPATH, '//a[@class="orderEntry"]')
        for product in products:
            if product.text == pro_id:
                driver.get(f'{product.get_attribute("href")}')
                img_link = driver.find_element(By.CLASS_NAME, 'imagePopup').get_attribute('href')
                found = my_wright_place_save_img(img_link, pro_id)
                update_file(row_index, '', found)
                print(f'{row_index} Found')
                return
    except Exception as e:
        print(e)

    print(f'{row_index} Not Found')
    update_file(row_index, '', 'Not found')


if __name__ == '__main__':
    print('----------------- Script start running ... -----------------')
    df = read_file()
    ch_driver = config_driver()
    # wright_dental(driver)

    for index, row in df.iterrows():
        if str(row['Img Found']) == 'nan':
            # search_key = 'Luxaflow;star;syr;2x1.5g'.split(';')[0]
            # product_id = 'DMG214002'
            # search_key = 'Casting;Wax;Smooth;Green'.split(';')[0]
            # product_id = '10030'

            search_key = str(row['product Range Name']).split(';')[0]
            product_id = str(row['Product ID'])
            if not wright_dental(ch_driver, search_key, product_id, index):
                my_wright_place(ch_driver, product_id, index)
