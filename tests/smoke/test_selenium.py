from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver


def test_example_chrome(chrome_webdriver: WebDriver):
    chrome_webdriver.get("http://www.example.com")

    assert chrome_webdriver.title == "Example Domain"
