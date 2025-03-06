import json
import logging
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from concurrent.futures import ThreadPoolExecutor
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException

logging.basicConfig(
    filename="scraping.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Scraper:
    def __init__(self):
        self.driver = self._initialize_driver()
        self.base_url = "https://precodahora.ba.gov.br/produtos/"
        self.cities = {"Salvador": "2927408", "Feira de Santana": "2910800"}
        self.state_code = "29"
        self.results = []

    def _initialize_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def load_data(self):
        try:
            with open(self.json_file, "r") as f:
                ean_list = json.load(f)
            return ean_list
        except FileNotFoundError:
            logging.error("JSON file not found")
            return []

    def start_driver(self):
        return webdriver.Chrome(service=self.service, options=self.chrome_options)

    def search_product(self, ean):
        driver = self.start_driver
        url = "https://precodahora.ba.gov.br/"
        driver.get(url)
        time.sleep(2)

        try:
            search_box = driver.find_element(By.XPATH, "//input[@id='fake-sbar']")
            search_box.clear()
            search_box.send_keys(ean)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)

            description = driver.find_element(
                By.XPATH, "//div[@style='font-size:18px;']/strong"
            ).text
            price = driver.find_element(By.XPATH, "//span[@class='search-gtin']").text
            collection_date = driver.find_element(
                By.XPATH, "//i[@class='fa fa-calendar']"
            ).text
            establishment = driver.find_element(
                By.XPATH, "//i[@class='fa fa-building']"
            ).text

            data = {
                "ean": ean,
                "description": description,
                "price": price,
                "collection_date": collection_date,
                "establishment": establishment,
            }
            logging.info(f"Success: {ean} - {description} - {price}")
            return data
        except (NoSuchElementException, TimeoutException) as e:
            logging.error(f"Error fetching {ean}: {e}")
            return None
        finally:
            driver.quit()

    def collect_data(self, quantity=100):
        eans = self.ean_list[:quantity]
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self.search_product, eans))
        return [result for result in results if result]

    def salve_csv(self, data, file_name="data_collected.csv"):
        df = pd.DataFrame(data)
        df.to_csv(file_name, index=False, encoding="utf-8")
        print(f"Data salved in {file_name}")

    def execute(self, quantity=100):
        collected_data = self.collect_data(quantity)
        self.salve_csv(collected_data)
