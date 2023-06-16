import subprocess
import logging

logger = logging.getLogger(__file__)


def open_url_in_browser(url, executable_path="", ffservice=None, fullscreen=True):
    from selenium import webdriver

    geckopath = (
        executable_path
        or subprocess.check_output(["which", "geckodriver"]).decode().strip()
    )
    if ffservice or geckopath:
        ffservice = ffservice or webdriver.chrome.service.Service(
            executable_path=geckopath
        )
    else:
        raise ModuleNotFoundError(
            "`geckodriver` is not in your path. do you have it installed?"
        )

    browser = webdriver.Firefox(service=ffservice)

    # launches URL in browser
    logger.info(f"opening up a browser window using {geckopath} to URL {url}")
    browser.get(url)
    if fullscreen:
        browser.fullscreen_window()

    return ffservice
