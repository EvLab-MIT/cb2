import typing
from datetime import timedelta, time
import logging
import IPython

from drivercb2.fixation import show_fixation
from py_client.demos.scenario_monitor import ScenarioMonitor
from py_client.remote_client import RemoteClient
from py_client.game_endpoint import Action, GameEndpoint
from py_client.local_game_coordinator import LocalGameCoordinator
import easygui

REFRESH_RATE_HZ = 10
logger = logging.getLogger(__file__)


def open_url_in_browser(url, executable_path="", ffservice=None):
    from selenium import webdriver

    ffservice = ffservice or webdriver.chrome.service.Service(
        executable_path="/home/aalok/Downloads/geckodriver/geckodriver-v0.31.0-linux32/geckodriver"
    )
    browser = webdriver.Firefox(service=ffservice)
    # launches URL in browser
    browser.get(url)
    browser.fullscreen_window()

    return ffservice


if __name__ == "__main__":
    kvals = dict(
        # subject_id=easygui.enterbox("Subject ID: ", default="FED_2023----a_3Tn")
    )

    # show_fixation(0.1)

    url = "http://0.0.0.0:8080"
    suffix = "/play?lobby_name=scenario-lobby"

    open_url_in_browser(url + suffix)

    client = RemoteClient(url=url, lobby_name="scenario-lobby")
    connected, reason = client.Connect()
    assert connected, f"Unable to connect: {reason}"
    logger.info(f"Connected? {connected}")

    logger.info(
        "confirmation of having joined a game: "
        + str(easygui.ccbox("Have you joined a game yet?")),
    )

    # we have to attach to an existing scenario first to be able to generate a `GameEndpoint` object
    scenario_id = ""  # "robin-black"
    game, reason = client.AttachToScenario(
        scenario_id=scenario_id,
        timeout=timedelta(minutes=1),
    )

    assert game is not None, f"couldn't AttachToScenario `{scenario_id}`"

    scenario_file = "scenarios/hehe.json"
    with open(scenario_file, "r") as f:
        scenario_data = f.read()

    # game: GameEndpoint = client.game
    logger.info(f"trying to attach scenario with id: {scenario_id}")
    action: Action = Action.LoadScenario(scenario_data)
    game.step(action)
    logger.info(f"sent scenario data to game {game}")

    logger.info(f"starting {ScenarioMonitor} intance")
    monitor = ScenarioMonitor(
        game,
        pause_per_turn=(1 / REFRESH_RATE_HZ),  # scenario_data=scenario_data
    )
    monitor.run()
    monitor.join()
