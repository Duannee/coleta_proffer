import json
import logging
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from datetime import datetime

from concurrent.futures import ThreadPoolExecutor
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

    def load_ean_json(self, json_ean_file="lista_eans.json"):
        with open(json_ean_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def load_description_json(self, json_description_file="lista_descricao.json"):
        with open(json_description_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def search_product(self, ean, city_code):
        self.driver.get(self.base_url)
        time.sleep(2)

    def extract_product_data(self, ean, description, city_code):
        try:
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='top-sbar']"))
            )
            search_box.clear()
            search_box.send_keys(ean)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)

            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            self.driver.save_screenshot("screenshot.png")

            no_results = self.driver.find_elements(
                By.XPATH, "//div[contains(text(), 'No results found')]"
            )
            if no_results:
                print(f"No results found for EAN {ean} in city {city_code}.")
                return None

            price = self.driver.find_element(
                By.XPATH,
                "//div[@style='font-size:42px;font-weight:bold; color: #000;']",
            ).text.strip()
            establishment = self.driver.find_element(
                By.XPATH, "//div[i[@class='fa fa-building']]"
            ).text.strip()

            data = {
                "ean": ean,
                "description": description,
                "price": price,
                "collection_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "establishment": establishment,
            }
            print(f"Data extracted for EAN {ean}: {data}")  # Debugging
            return data
        except NoSuchElementException:
            print(f"Product with EAN {ean} not found in city {city_code}.")
            return None
        except TimeoutException:
            print(
                f"Timeout while searching for product with EAN {ean} in city {city_code}."
            )
            return None

    def collect_data(self, ean_list, description_list):
        for ean, description in zip(ean_list, description_list):
            for city_name, city_code in self.cities.items():
                print(f"Fetching data for EAN {ean} in {city_name}")
                self.search_product(ean, city_code)
                product_data = self.extract_product_data(ean, description, city_code)
                if product_data:
                    self.results.append(product_data)
                time.sleep(1)
        print(f"Total results collected: {len(self.results)}")

    def save_csv(self, file_name="data_collected.csv"):
        df = pd.DataFrame(self.results)
        df.to_csv(file_name, index=False, encoding="utf-8")
        print(f"Data saved to {file_name}")

    def close_driver(self):
        self.driver.quit()


if __name__ == "__main__":
    scraper = Scraper()

    try:
        ean_list = scraper.load_ean_json("lista_eans.json")
        description_list = scraper.load_description_json("lista_descricao.json")

        scraper.collect_data(ean_list, description_list)

        scraper.save_csv("data_collected.csv")
    finally:
        scraper.close_driver()
