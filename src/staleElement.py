from selenium.common.exceptions import StaleElementReferenceException


class WebElementWrapper:
    def __init__(self, driver, by, locator, timeout=10):
        self.driver = driver
        self.by = by
        self.locator = locator
        self.timeout = timeout
        self.element = self._find_element()
