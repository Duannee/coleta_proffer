import json
import logging
import random
import time
import requests
import pandas as pd
import os
import sys
from dotenv import load_dotenv
from twocaptcha import TwoCaptcha
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from datetime import datetime
from queue import Queue
from threading import Thread
import threading

from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from stale_element import WebElementWrapper


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

        self.cnpj_requests_count = 0
        self.last_cnpj_request_time = time.time()
        self.cnpj_lock = threading.Lock()

        self.cnpj_cache = {}

    def _initialize_driver(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
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

    def fetch_cnpj_data(self, cnpj):
        if not cnpj:
            return None

        if cnpj in self.cnpj_cache:
            print(f"CNPJ {cnpj} found in cache")
            return self.cnpj_cache[cnpj]

        with self.cnpj_lock:
            current_time = time.time()
            elapsed_time = current_time - self.last_cnpj_request_time

            if self.cnpj_requests_count >= 3:
                wait_time = max(60 - elapsed_time, 0)
                print(f"Waiting {wait_time:.2f} seconds to respect the CNPJ API...")
                time.sleep(wait_time)
                self.cnpj_requests_count = 0
                self.last_cnpj_request_time = time.time()
            self.cnpj_requests_count += 1

        url = f"https://publica.cnpj.ws/cnpj/{cnpj}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.cnpj_cache[cnpj] = data
                return data
            elif response.status_code == 404:
                print(f"CNPJ {cnpj} not found in the API")
                return None
            else:
                print(f"Error accessing CNPJ API {cnpj}: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Connection error when querying CNPJ {cnpj}: {e}")
            return None

    def extract_cnpj(self):
        try:
            cnpj_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[@id='hbtn_1-0']"))
            )
            return cnpj_element.get_attribute("data-cnpj")

        except (NoSuchElementException, TimeoutException):
            print("CNPJ not found")
            return None

    def solve_recaptcha(self):

        sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        challenge_url = "https://precodahora.ba.gov.br/challenge/"
        self.driver.get(challenge_url)
        time.sleep(3)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='g-recaptcha']"))
        )
        captcha_key = self.driver.find_element(
            By.XPATH, "//div[@class='g-recaptcha']"
        ).get_attribute("data-sitekey")

        print(f"Captcha Site Key: {captcha_key}")

        if not captcha_key:
            raise ValueError("Failed to extract captcha site key")

        load_dotenv()

        api_key = os.getenv("API_KEY")

        solver = TwoCaptcha(api_key)
        try:
            result = solver.recaptcha(sitekey=captcha_key, url=challenge_url)
            code = result["code"]
            print(code)

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "g-recaptcha-response"))
            )

            self.driver.execute_script(
                f"document.getElementById('g-recaptcha-response').innerHTML = '{code}';"
            )

            self.driver.execute_script(
                "var event = new Event('input', { bubbles: true });"
                "document.getElementById('g-recaptcha-response').dispatchEvent(event);"
            )

            self.driver.execute_script(
                "var event = new Event('change', { bubbles: true });"
                "document.getElementById('g-recaptcha-response').dispatchEvent(event);"
            )

            time.sleep(2)

            self.driver.find_element(
                By.CSS_SELECTOR, ".btn.btn-lg.btn-danger.mt-2.btn-block"
            ).click()

            WebDriverWait(self.driver, 10).until(EC.url_changes(challenge_url))
            print("CAPTCHA solved and page processed successfully!!")

        except Exception as e:
            print(f"Erro ao resolver CAPTCHA: {e}")

    def search_product(self, ean, city_code):
        self.driver.get(self.base_url)
        time.sleep(2)

    def extract_product_data(self, ean, description, city_code):
        try:
            self.driver.get(self.base_url)
            time.sleep(random.uniform(1.5, 3))
            search_box = WebElementWrapper(
                self.driver, By.XPATH, "//input[@id='top-sbar']"
            )
            search_box.get_element().clear()
            search_box.send_keys(ean)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)

            self.solve_recaptcha()

            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            self.driver.save_screenshot("screenshot.png")

            no_results = self.driver.find_elements(
                By.XPATH, "//div[contains(text(), 'No results found')]"
            )
            if no_results:
                print(f"No results found for EAN {ean} in city {city_code}.")
                return None

            price = WebElementWrapper(
                self.driver,
                By.XPATH,
                "//div[@style='font-size:42px;font-weight:bold; color: #000;']",
            ).text()
            establishment = WebElementWrapper(
                self.driver, By.XPATH, "//div[i[@class='fa fa-building']]"
            ).text()

            cnpj = self.extract_cnpj()
            if not cnpj:
                print(f"No CNPJ found for EAN {ean}, skipping query.")

            cnpj_data = self.fetch_cnpj_data(cnpj) if cnpj else None

            if cnpj_data:
                estabelecimento = cnpj_data.get("estabelecimento", {})
                neighborhood = estabelecimento.get("bairro", "N/A")
                city = estabelecimento.get("cidade", {}).get("nome", "N/A")
                uf = estabelecimento.get("estado", {}).get("sigla", "N/A")
            else:
                neighborhood, city, uf = "N/A", "N/A", "N/A"

            data = {
                "ean": ean,
                "description": description,
                "price": price,
                "collection_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "establishment": establishment,
                "cidade": city,
                "cnpj": cnpj,
                "bairro": neighborhood,
                "uf": uf,
                "city_code": city_code,
                "state_code": self.state_code,
            }
            print(f"Data extracted for EAN {ean}: {data}")
            return data
        except TimeoutException:
            print("Timed out while trying to click the submit button!")
        except NoSuchElementException:
            print(f"Product with EAN {ean} not found in city {city_code}.")
            return None
        except TimeoutException:
            print(
                f"Timeout while searching for product with EAN {ean} in city {city_code}."
            )
            return None

    def collect_data_for_city(self, ean, description, city_name, city_code):
        print(f"Fetching data for EAN {ean} in {city_name}")
        self.search_product(ean, city_code)
        product_data = self.extract_product_data(ean, description, city_code)
        if product_data:
            return product_data
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
