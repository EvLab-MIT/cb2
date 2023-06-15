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
from cb2fmri.remapkeys import KmonadProcessTracker

REFRESH_RATE_HZ = 10

logging.basicConfig(level=logging.INFO)
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


def load_scenario(
    game: GameEndpoint, scenario_file: str = "scenarios/hehe.json", kvals: dict = {}
):
    # test some scenario file to try to join
    with open(scenario_file, "r") as f:
        scenario_data_json = f.read()
    scenario_data = json.loads(scenario_data)
    if kvals not in scenario_data:
        scenario_data["kvals"] = {}
    scenario_data["kvals"].update(kvals)
    scenario_data_json = json.dumps(scenario_data)

    # game: GameEndpoint = client.game
    logger.info(f"sending scenario data to game {game}")
    action: Action = Action.LoadScenario(scenario_data_json)
    game.step(action)


def run_experiment_sequence(sequence: typing.List):
    pass


def main(kmonad=None):
    logger.info("hello! this is CB2fMRI.")

    parser = argparse.ArgumentParser("cb2fmri")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--url", type=str, default="http://localhost:8080")
    parser.add_argument("--lobby", type=str, default="scenario-lobby")
    parser.add_argument("--no-launch-browser", action="store_true")
    parser.add_argument("--no-remap-keys", action="store_true")

    args = parser.parse_args()

    # collect SUBJECT_ID to keep track
    kvals = {
        "subject_id": easygui.enterbox("Subject ID: ", default="FED_2023MMDDa_3Tn")
    }
    logger.info(f'SUBJECT_ID: {kvals["subject_id"]}')

    # use selenium to open up a browser to the game server instance
    # (NOTE: game server instance must be started separately, and is not done via this script.
    # that would be too many moving parts requiring coordination. in the future we may even
    # explore the possibility of having a game server run on openmind and query it internally
    # over the MIT network)
    url = f"{args.url}/play?lobby_name={args.lobby}&auto=join_game_queue"
    if not args.no_launch_browser:
        open_url_in_browser(url, fullscreen=not args.dry_run)

    # start the keymapping process for use with the buttonbox
    kmonad = kmonad or KmonadProcessTracker()
    if not args.no_remap_keys:
        kmonad.obtain_sudo()
        kmonad.remap()

    # while the browser window loads, ask the participant to test their now-remapped
    # buttons so they can control the arrow keys using the two buttonboxes.
    easygui.ccbox("Test your buttonbox now!")
    test_arrow_keys()

    # by now the browser should have loaded and joined an empty game room. this is a
    # good time to establish a connection to the server.
    client = RemoteClient(url=url, lobby_name="scenario-lobby")
    connected, reason = client.Connect()
    assert connected, f"Unable to connect: {reason}"
    logger.info(f"Connected? {connected}")

    logger.info(
        "confirmation of having joined a game: "
        + str(easygui.ccbox("Have you joined a game yet?")),
    )

    # we have to attach to an existing scenario first to be able to generate a `GameEndpoint` object
    # game: py_client.game_endpoint.GameEndpoint
    # the default scenario on startup is identified by just an empty-string
    scenario_id = ""
    logger.info(f"trying to attach scenario with id: {scenario_id}")
    game, reason = client.AttachToScenario(
        scenario_id=scenario_id,
        timeout=timedelta(minutes=1),
    )

    assert game is not None, f"couldn't AttachToScenario `{scenario_id}`"
    logger.info(
        f"starting {ScenarioMonitor} intance to monitor happenings in the scenario (is this necessary?)"
    )
    monitor = ScenarioMonitor(
        game,
        pause_per_turn=(1 / REFRESH_RATE_HZ),  # scenario_data=scenario_data
    )
    monitor.run()
    monitor.join()

    load_scenario(game, scenario_file="scenarios/hehe.json", kvals=kvals)


if __name__ == "__main__":
    kmonad = KmonadProcessTracker()
    try:
        main(kmonad)
    # we want to ideally intercept Ctrl+C on main so we can restore the keymapping
    # this fails if there is a more general kind of exception
    except KeyboardInterrupt:
        kmonad.reset()
