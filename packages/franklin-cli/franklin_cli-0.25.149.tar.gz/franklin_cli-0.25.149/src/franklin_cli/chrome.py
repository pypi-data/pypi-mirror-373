import shutil
import os
import platform
import sys
import time
from pathlib import Path
from functools import wraps
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, InvalidSessionIdException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.chrome.options import Options

import click
from . import terminal as term
from . import config as cfg
from . import system
from .logger import logger

def chrome_installed(required=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            if not is_chrome_installed():
                if required:
                    term.secho("You need to install Google Chrome to run",
                               "Jupyter lab through Franklin")
                    if required:
                        raise click.Abort()


            return func(*args, **kwargs)

        return wrapper
    return decorator


def is_chrome_installed():
    system = platform.system()

    # Try known executable names and paths
    candidates = {
        "Windows": [
            "chrome.exe",
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        ],
        "Darwin": [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ],
        "Linux": [
            "google-chrome",
            "google-chrome-stable",
            "chromium-browser",
            "chromium",
        ]
    }

    for path in candidates.get(system, []):
        if shutil.which(path) or os.path.exists(path):
            return True

    return False

def get_chrome_driver():

    import tempfile

    # tmpdir = tempfile.mkdtemp()
    options = Options()
    options.add_argument("--disable-infobars")  # suppresses the "Chrome is being controlled..." message

    # On Linux/Mac: --user-data-dir=/home/yourname/.config/selenium-profile
    # On Windows: --user-data-dir=C:\\Users\\YourName\\AppData\\Local\\Google\\Chrome\\User Data\\SeleniumProfile

    # options.add_argument(f"--user-data-dir={tmpdir}") 
    home = Path().home()
    user_data_dir = home / '.config' / 'google-chrome' / 'Default'
    if system.system() == "Windows":
        user_data_dir = home / 'AppData' / 'Local' / 'Google' / 'Chrome' / 'User Data' / 'Default'
    elif system.system() == "Darwin":
        user_data_dir = home / 'Library' / 'Application Support' / 'Google' / 'Chrome' / 'Default'
    elif system.system() == "Linux":
        user_data_dir = home / '.config' / 'google-chrome' / 'Default'
    else:
        # If the system is not recognized, use the temporary directory
        user_data_dir = tempfile.mkdtemp()

    options.add_argument(f"--user-data-dir={user_data_dir}") 
        
    options.add_argument("--remote-debugging-port=9222")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Set up the WebDriver with the correct version of ChromeDriver
    driver = webdriver.Chrome(
        service=ChromeService(
            ChromeDriverManager().install()
            ),
            options=options
        )
    return driver

def open_chrome(driver, token_url) -> None:
    # Open the Jupyter Notebook in the Chrome controlled by Selenium
    driver.get(token_url)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })


# class InifiniteBouncingBar:
#     def __init__(self, , delay=0.05):
#         self.length = cfg.pg_options['length']
#         self.delay = delay
#         self.fill_char = cfg.pg_options['fill_char']
#         self.empty_char = cfg.pg_options['empty_char']
#         self.pos = 0
#         self.direction = 1  # 1 for right, -1 for left

#     def step(self):
#         bar = [self.empty_char] * self.length
#         bar[self.pos] = self.fill_char
#         sys.stdout.write('\r[' + ''.join(bar) + ']')
#         sys.stdout.flush()

#         self.pos += self.direction
#         if self.pos == 0 or self.pos == self.length - 1:
#             self.direction *= -1


class InifiniteBouncingBar:
    def __init__(self, **kwargs):
        self.length = kwargs['width'] - 2  # Subtract 2 for the brackets
        self.fill_char = kwargs['fill_char']
        self.empty_char = kwargs['empty_char']
        self.pg_ljust = cfg.pg_ljust
        self.pos = 0
        self.direction = 1  # 1 for right, -1 for left

    def step(self):
        bar = [self.empty_char] * self.length
        bar[self.pos] = self.fill_char
        sys.stdout.write('\r' + 'Jupyter is running:'.ljust(self.pg_ljust) + '[' + ''.join(bar) + ']')
        sys.stdout.flush()
        self.pos += self.direction
        if self.pos == 0 or self.pos == self.length - 1:
            self.direction *= -1

# def infinite_bouncing_bar(length=30, delay=0.05):
#     pos = 0
#     direction = 1  # 1 for right, -1 for left
#     while True:
#         bar = [' '] * length
#         bar[pos] = '='
#         sys.stdout.write('\r[' + ''.join(bar) + ']')
#         sys.stdout.flush()
#         time.sleep(delay)
#         pos += direction
#         if pos == 0 or pos == length - 1:
#             direction *= -1

# infinite_bouncing_bar()

def chrome_open_and_wait(token_url: str) -> None:

    logger.debug('Getting Chrome driver')
    driver = get_chrome_driver()

    logger.debug(f'Opening Chrome with URL: {token_url}')
    open_chrome(driver, token_url)

    inf_prog = InifiniteBouncingBar(**cfg.pg_options)

    def callback(d):
        inf_prog.step()
        return d.current_url and "lab/tree" in d.current_url

    try:
        logger.debug(f'Waiting for Chrome')
        WebDriverWait(driver, 300).until(
            # EC.presence_of_element_located((By.CLASS_NAME, "jp-Notebook"))
            # lambda d: shutdown or d.current_url and "lab/tree" in d.current_url       
            # lambda d: d.current_url and "lab/tree" in d.current_url       
            callback
            )
        logger.debug('Polling loop to detect when the tab is closed')
        while True:
            if len(driver.window_handles) == 0:
                break
            time.sleep(1)

    except WebDriverException as e:
        logger.debug(f'WebDriverException occurred: {e}')
    except InvalidSessionIdException as e:
        logger.debug(f'InvalidSessionIdException occurred: {e}')
    except NoSuchWindowException as e:
        logger.debug(f'NoSuchWindowException occurred: {e}')
    finally:
        # Close the browser if it's still open
        try:
            driver.quit()
        except NoSuchWindowException:
            pass
