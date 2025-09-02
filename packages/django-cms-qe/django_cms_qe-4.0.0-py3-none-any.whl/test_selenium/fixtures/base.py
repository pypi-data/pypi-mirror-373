import os

import pytest
from selenium import webdriver
from webdriverwrapper.pytest import *  # noqa: F403,F401

from ..browser import ChromeBrowser
from ..pages.cms import LoginPage, WizardPage

__all__ = [
    'display',
    'session_driver',
    '_driver',
    'homepage_url',
    'admin_username',
]


@pytest.fixture(scope='session', autouse=True)
def display(request):
    no_display = request.config.getoption('--no-display')

    if no_display:
        yield
    else:
        from pyvirtualdisplay import Display

        display = Display(visible=0, size=(1200, 2000))
        display.start()
        yield
        display.stop()


@pytest.yield_fixture(scope='session')
def session_driver(request, homepage_url, admin_username):
    no_display = request.config.getoption('--no-display')

    driver = open_browser(homepage_url)
    try:
        LoginPage(driver).open().login(admin_username)
        WizardPage(driver).open().create_home_page()
        yield driver
    finally:
        if not no_display:
            driver.quit()


def open_browser(homepage_url):
    """
    Open browser a type URL `homepage_url`.
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--no-sandbox')  # So it will work in GitLab CI.

    driver = ChromeBrowser(chrome_options=chrome_options)
    driver.get(homepage_url)
    return driver


@pytest.fixture
def _driver(session_driver, homepage_url):
    session_driver.get(homepage_url)
    return session_driver


@pytest.fixture(scope='session')
def homepage_url():
    port = os.environ.get('WEB_PORT', '8000')
    return f'http://localhost:{port}'


@pytest.fixture(scope='session')
def admin_username():
    return os.environ.get('ADMIN_USER', 'admin')
