from robot.api.deco import keyword, library
from selenium.webdriver import ChromeOptions, FirefoxOptions
from selenium.webdriver.common.options import BaseOptions


@library(scope='GLOBAL', version='0.1')
class BrowserUtils:
    @keyword
    def get_default_browser_options(self, browser_name: str) -> BaseOptions:
        alternatives = {
            "chrome": self.get_chrome_options(),
            "firefox": self.get_firefox_options(),
        }
        options = alternatives.get(browser_name)

        if not isinstance(options, BaseOptions):
            raise ValueError(f"Invalid browser_name value: '{browser_name}'")

        return options

    @keyword
    def get_chrome_options(self) -> ChromeOptions:
        """Returns Chrome config options"""
        return ChromeOptions()

    @keyword
    def get_firefox_options(self) -> FirefoxOptions:
        """Returns Firefox config options"""
        return FirefoxOptions()
