import json
import logging
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

logger = logging.basicConfig(
    filename="scraping.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Scraper:
    def __init__(self, json_file="lista_eans.json", max_workers=5):
        self.json_file = json_file
        self.max_workers = max_workers
        self.ean_list = self.load_data

        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")

        self.service = Service(ChromeDriverManager().install())

    def load_data(self):
        try:
            with open(self.json_file, "r") as f:
                ean_list = json.load(f)
            return ean_list
        except FileNotFoundError:
            logging.error("JSON file not found")
            return []
