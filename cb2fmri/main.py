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

from cb2fmri.fixation import show_fixation, practice_arrow_keys, wait_for_trigger
from cb2fmri.remapkeys import KmonadProcessTracker
from cb2fmri.utils import open_url_in_browser


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

SECONDS = 1


def load_scenario(
    game: GameEndpoint, 
    scenario_file: str = "scenarios/hehe.json", 
    kvals: dict = {},
):
    # test some scenario file to try to join
    with open(scenario_file, "r") as f:
        scenario_data_json = f.read()
    scenario_data = json.loads(scenario_data_json)
    if "kvals" not in scenario_data:
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
    parser.add_argument("--host", type=str, default="http://localhost:8080")
    parser.add_argument("--lobby", type=str, default="scenario-lobby")
    parser.add_argument("--no-launch-browser", action="store_true")
    parser.add_argument("--no-remap-keys", action="store_true")
    parser.add_argument("--test", action="store_true")

    args = parser.parse_args()

    # collect SUBJECT_ID to keep track
    subject_id, run_no = (
        easygui.multenterbox(
            msg="",
            title="",
            fields=("Subject ID: ", "Run #: "),
            values=(f"FED_2023{time.strftime('%m%d')}x_3Tn", -1),
        )
        if not args.test
        else ("TEST", -1)
    )

    kvals = {"subject_id": subject_id, "run": run_no}

    if kvals["subject_id"] and kvals["run"]:
        pass
    else:
        logger.info(f"SUBJECT_ID or RUN# not provided. exiting.")
        exit()

    logger.info(f'SUBJECT_ID: {kvals["subject_id"]}\nRUN#: {repr(kvals["run"])}')

    # use selenium to open up a browser to the game server instance
    # (NOTE: game server instance must be started separately, and is not done via this script.
    # that would be too many moving parts requiring coordination. in the future we may even
    # explore the possibility of having a game server run on openmind and query it internally
    # over the MIT network)
    suffix = "&auto=join_game_queue"
    url = f"{args.host}/play?lobby_name={args.lobby}"
    if not args.no_launch_browser:
        open_url_in_browser(url + suffix, fullscreen=False)

    # start the keymapping process for use with the buttonbox
    kmonad = kmonad or KmonadProcessTracker()
    if not args.no_remap_keys:
        kmonad.obtain_sudo()
        kmonad.remap()

    # while the browser window loads, ask the participant to test their now-remapped
    # buttons so they can control the arrow keys using the two buttonboxes.
    # if not args.test:
    response = easygui.ccbox("Test your buttonbox now!")
    if response:
        success = practice_arrow_keys()

    # by now the browser should have loaded and joined an empty game room. this is a
    # good time to establish a connection to the server.
    logger.info(f"Trying to connect to {args.host} and lobby {args.lobby}")
    try:
        client = RemoteClient(url=args.host, render=False, lobby_name=args.lobby)
        connected, reason = client.Connect()
        logger.info(f"Connected? {connected}")
    except Exception as e:
        if not args.no_launch_browser:
            raise

    logger.info(
        "Confirmation of having joined a game: "
        + str(
            easygui.ccbox(
                "If you're in the lobby, click 'JOIN GAME' now! "
                + "Have you joined a game yet?"
            )
        )
    )

    # we have to attach to an existing scenario first to be able to generate a `GameEndpoint` object
    # game: py_client.game_endpoint.GameEndpoint
    # the default scenario on startup is identified by just an empty-string
    scenario_id = ""
    logger.info(f"trying to attach scenario with id: {scenario_id}")
    try:
        game, reason = client.AttachToScenario(
            scenario_id=scenario_id, timeout=timedelta(minutes=1)
        )
        assert game is not None, f"couldn't AttachToScenario `{scenario_id}`"
    except Exception as e:
        if not args.no_launch_browser:
            raise

    logger.info(
        f"starting {ScenarioMonitor} instance to monitor happenings in the scenario (is this necessary?)"
    )

    REFRESH_RATE_HZ = 10 / SECONDS
    monitor = ScenarioMonitor(
        game,
        pause_per_turn=(1 / REFRESH_RATE_HZ),  # scenario_data=scenario_data
    )
    # monitor.run()
    # monitor.join()

    wait_for_trigger()
    show_fixation(2 * SECONDS)
    load_scenario(game, scenario_file="scenarios/hehe.json", kvals=kvals)

    logger.info("nothing left to do. gracefully terminating.")


if __name__ == "__main__":
    kmonad = KmonadProcessTracker()

    try:
        main(kmonad)
        kmonad.reset()
    # we want to ideally intercept Ctrl+C on main so we can restore the keymapping
    # this fails if there is a more general kind of exception
    except Exception as e:
        logger.warn(f"caught an exception. attempting to shut down `kmonad` process.")
        kmonad.reset()
        raise e
