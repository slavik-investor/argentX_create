from loguru import logger

logger.add("log/debug.log")


def focus_window(driver, url):
    driver.execute_script("window.open()")
    windows_after = driver.window_handles
    new_window = [x for x in windows_after][-1]
    try:
        driver.switch_to.window(new_window)
        driver.execute_script("window.focus()")
    except Exception as e:
        logger.info(str(e))
    driver.get(url)
