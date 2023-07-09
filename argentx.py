from time import sleep

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from utils import focus_window, logger


def open_extension(driver: Chrome, extension_id: str) -> None:
    logger.info("Open extension")
    url = f"chrome-extension://{extension_id}/index.html"
    focus_window(driver, url)


def fill_wallet(driver: Chrome, seed_phrase: str, password: str) -> None | int | str:
    logger.info("Filling extension")

    restore_wallet = '//button[text()="Restore an existing wallet"]'
    # 12 pieces
    input_phrase = '//*[@id="root"]/div/div/div/div/div[1]/div/form/div[1]//input'
    continue_button = '//button[text()="Continue"]'
    first_password = '//input[@name="password"]'
    repeat_password = '//input[@name="repeatPassword"]'
    finish_button = '//*[text()="Finish"]'

    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, restore_wallet))).click()
    except Exception as ex:
        logger.info("Is already filled", ex)
        return "Already filled"

    while len(driver.find_elements(By.XPATH, input_phrase)) < 12:
        sleep(1)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//html"))).click()

    sleep(0.5)
    elements = driver.find_elements(By.XPATH, input_phrase)

    for i, phrase in zip(range(12), seed_phrase.split(' ')):
        try:
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f'[data-testid="seed-input-{i}"]')))
            element.send_keys(phrase)
        except Exception as ex:
            logger.error(f"{phrase}, {ex}")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, continue_button))).click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, first_password))).send_keys(password)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, repeat_password))).send_keys(password)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, continue_button))).click()
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, finish_button))).click()
    sleep(3)
    logger.success("Complete extension")


def run_argentx(driver: Chrome, seed_phrase: str, extension_id: str, wallet_password: str):
    open_extension(driver, extension_id)
    fill_wallet(driver, seed_phrase, wallet_password)
