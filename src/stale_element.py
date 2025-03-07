from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WebElementWrapper:
    def __init__(self, driver, by, locator, timeout=10):
        self.driver = driver
        self.by = by
        self.locator = locator
        self.timeout = timeout
        self.element = self._find_element()

    def _find_element(self):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((self.by, self.locator))
        )

    def get_element(self):
        try:
            self.element.is_displayed()
            return self.element
        except StaleElementReferenceException:
            print("Obsolete element, relocating...")
            self.element = self._find_element()
            return self.element

    def click(self):
        self.get_element().click()

    def send_keys(self, keys):
        self.get_element().send_keys(keys)
