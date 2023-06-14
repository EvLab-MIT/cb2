import typing
from datetime import timedelta, time
import logging
import json
import subprocess
import argparse
import easygui
import time

from py_client.demos.scenario_monitor import ScenarioMonitor
from py_client.remote_client import RemoteClient
from py_client.game_endpoint import Action, GameEndpoint
from py_client.local_game_coordinator import LocalGameCoordinator

from cb2fmri.fixation import show_fixation, test_arrow_keys
from cb2fmri import remapkeys

REFRESH_RATE_HZ = 10
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
    browser.get(url)
    if fullscreen:
        browser.fullscreen_window()

    return ffservice


def main():
    parser = argparse.ArgumentParser("cb2fmri")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--url", type=str, default="http://localhost:8080")
    parser.add_argument("--lobby", type=str, default="scenario-lobby")
    parser.add_argument("--no-launch-browser", action="store_true")

    args = parser.parse_args()

    kvals = {
        "subject_id": easygui.enterbox("Subject ID: ", default="FED_2023MMDDa_3Tn")
    }

    remapkeys.remap()
    easygui.ccbox("Test your buttonbox!")
    test_arrow_keys()

    url = f"{args.url}/play?lobby_name={args.lobby}&auto=join_game_queue"

    if not args.no_launch_browser:
        open_url_in_browser(url, fullscreen=not args.dry_run)

    show_fixation(1)

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
    logger.info(f"trying to attach scenario with id: {scenario_id}")
    game, reason = client.AttachToScenario(
        scenario_id=scenario_id,
        timeout=timedelta(minutes=1),
    )

    assert game is not None, f"couldn't AttachToScenario `{scenario_id}`"

    scenario_file = "scenarios/hehe.json"
    with open(scenario_file, "r") as f:
        scenario_data_json = f.read()
    scenario_data = json.loads(scenario_data)
    scenario_data["kvals"] = kvals
    scenario_data_json = json.dumps(scenario_data)

    # game: GameEndpoint = client.game
    logger.info(f"sending scenario data to game {game}")
    action: Action = Action.LoadScenario(scenario_data_json)
    game.step(action)
    logger.info(f"sent scenario data to game {game}")

    logger.info(f"starting {ScenarioMonitor} intance")
    monitor = ScenarioMonitor(
        game,
        pause_per_turn=(1 / REFRESH_RATE_HZ),  # scenario_data=scenario_data
    )

    # not sure if it's necessary to have the monitor `join()`, it will keep dumping the events to tty,
    # instead we prob. need control to stop/load next things

    # monitor.run()
    # monitor.join()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        remapkeys.reset()
