"""Connects to a remote server from the command line and plays a game using the specified agent."""
import logging
from datetime import timedelta

import fire

from agents.config import CreateAgent, ReadAgentConfigOrDie
from py_client.game_endpoint import Action
from py_client.remote_client import RemoteClient
from server.messages.rooms import Role

logger = logging.getLogger(__name__)


def main(
    host,
    render=False,
    lobby="bot-sandbox",
    pause_per_turn=0,
    agent_config_filepath: str = "agents/simple_follower.yaml",
):
    # Create client and connect to server.
    client = RemoteClient(host, render, lobby_name=lobby)
    connected, reason = client.Connect()
    assert connected, f"Unable to connect: {reason}"

    agent = CreateAgent(ReadAgentConfigOrDie(agent_config_filepath))

    queue_type = RemoteClient.QueueType.NONE
    if agent.role() == Role.LEADER:
        queue_type = RemoteClient.QueueType.LEADER_ONLY
    elif agent.role() == Role.FOLLOWER:
        queue_type = RemoteClient.QueueType.FOLLOWER_ONLY
    else:
        raise Exception(f"Invalid role: {agent.role()}")

    # Wait in the queue for a game to start.
    game, reason = client.JoinGame(
        timeout=timedelta(minutes=5),
        queue_type=queue_type,
    )
    assert game is not None, f"Unable to join game: {reason}"

    game_state = game.initial_state()

    if agent.role() == Role.FOLLOWER:
        # Leader's turn first. Wait for follower turn by executing a noop.
        action = Action.NoopAction()
        game_state = game.step(action)

    while not game.over():
        action = agent.choose_action(game_state)
        logger.info(f"step({action})")
        game_state = game.step(action)


if __name__ == "__main__":
    fire.Fire(main)
