from pathlib import Path
from time import sleep
import concurrent.futures

import requests
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from argentx import run_argentx
from utils import logger


class Worker:
    open_url = "http://local.adspower.net:50325/api/v1/browser/start?user_id={}"
    close_url = "http://local.adspower.net:50325/api/v1/browser/stop?user_id={}"
    active_url = "http://local.adspower.net:50325/api/v1/browser/active?user_id={}"

    def __init__(
        self,
        ids_file: str,
        seed_file: str,
        password: str,
        ext_id: str
    ):
        self.seeds = self.read_file(seed_file)
        self.profile_ids = self.read_file(ids_file)
        self.password = password
        self.ext_id = ext_id

    @ staticmethod
    def read_file(file_name: str) -> list[str]:
        with Path(file_name).open() as file:
            return [line.replace("\n", "") for line in file.readlines()]

    def wait_browser_active(self, profile_id: str, timeout: int) -> bool:
        for i in range(timeout):
            sleep(1)
            resp = requests.get(self.active_url.format(profile_id))
            if resp.status_code != 200:
                continue
            if resp.json().get("data", {}).get("data", {}).get("status") != "Active":
                continue
            else:
                break
        return True

    def close_ads_profile(self, profile_id: str) -> bool:
        logger.info(f"Close profile {profile_id}")
        resp = requests.get(self.close_url.format(profile_id))
        if resp.status_code == 200 and resp.json().get("msg") == "Success":
            return True
        if resp.status_code != 200:
            sleep(3)
            return self.close_ads_profile(profile_id)

    def open_ads_profile(self, profile_id: str) -> Chrome:
        resp = requests.get(self.open_url.format(profile_id)).json()
        chrome_driver = resp["data"]["webdriver"]
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "debuggerAddress", resp["data"]["ws"]["selenium"])
        driver = Chrome(chrome_driver, options=chrome_options)
        return driver

    def run_one_account(self, account_id: str, seed_phrase: str):
        try:
            driver = self.open_ads_profile(account_id)
            logger.info(f"Open profile {account_id}")
        except Exception as ex:
            sleep(2)
            self.close_ads_profile(account_id)
            logger.error(f"Can't open prfile{account_id}, error: {ex}")
            return

        try:
            run_argentx(driver, seed_phrase, self.ext_id, self.password)
        except Exception as e:
            logger.error(f"log_error_filling,  {account_id}, {e}")

        driver.quit()
        self.close_ads_profile(account_id)

    def run_work(self):

        for account_id, seed_phrase in zip(self.profile_ids, self.seeds):
            self.run_one_account(account_id, seed_phrase)
            self.wait_browser_active(account_id, 2)
            sleep(0.5)
