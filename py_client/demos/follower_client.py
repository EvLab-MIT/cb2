from math import degrees
from time import sleep
from py_client.remote_client import RemoteClient, Role
from py_client.game_endpoint import LeadAction, FollowAction, Role

import fire
import logging
import random

from datetime import timedelta

logger = logging.getLogger(__name__)

def actions_from_instruction(instruction):
    actions = []
    instruction_action_codes = instruction.split(",")
    for action_code in instruction_action_codes:
        action_code = action_code.strip().lower()
        if len(action_code) == 0:
            continue
        if "forward".startswith(action_code):
            actions.append(FollowAction(FollowAction.ActionCode.FORWARDS))
        elif "backward".startswith(action_code):
            actions.append(FollowAction(FollowAction.ActionCode.BACKWARDS))
        elif "left".startswith(action_code):
            actions.append(FollowAction(FollowAction.ActionCode.TURN_LEFT))
        elif "right".startswith(action_code):
            actions.append(FollowAction(FollowAction.ActionCode.TURN_RIGHT))
        elif "random".startswith(action_code):
            action_codes = [FollowAction.ActionCode.FORWARDS, FollowAction.ActionCode.BACKWARDS, FollowAction.ActionCode.TURN_LEFT, FollowAction.ActionCode.TURN_RIGHT]
            actions.append(FollowAction(random.choice(action_codes)))
    if len(actions) == 0:
        # Choose a random action.
        action_codes = [FollowAction.ActionCode.FORWARDS, FollowAction.ActionCode.BACKWARDS, FollowAction.ActionCode.TURN_LEFT, FollowAction.ActionCode.TURN_RIGHT]
        action = FollowAction(random.choice(action_codes))
    return actions

def get_active_instruction(instructions):
    for instruction in instructions:
        if not instruction.completed and not instruction.cancelled:
            return instruction
    return None
 
class NaiveFollower(object):
    def __init__(self, game_endpoint):
        self.instructions_processed = set()
        self.actions = []
        self.game = game_endpoint
        self.exc = None
    
    def run(self):
        try:
            map, cards, turn_state, instructions, actors, live_feedback = self.game.initial_state()
            logger.info(f"Initial instructions: {instructions}")
            if len(actors) == 1:
                follower = actors[0]
            else:
                (leader, follower) = actors
            if turn_state.turn != Role.FOLLOWER:
                action = FollowAction(FollowAction.ActionCode.NONE)
            else:
                action = self.get_action(self.game, map, cards, turn_state, instructions, actors, live_feedback)
            logger.info(f"step({str(action)})")
            map, cards, turn_state, instructions, actors, live_feedback = self.game.step(action)
            import time
            while not self.game.over():
                time.sleep(1) 
                action = self.get_action(self.game, map, cards, turn_state, instructions, (None, follower), live_feedback)
                logger.info(f"step({action})")
                map, cards, turn_state, instructions, actors, live_feedback = self.game.step(action)
            print(f"Game over. Score: {turn_state.score}")
        except Exception as e:
            self.exc = e

    def get_action(self, game, map, cards, turn_state, instructions, actors, feedback):
        if len(self.actions) == 0:
            active_instruction = get_active_instruction(instructions)
            actions = []
            if active_instruction is not None:
                actions = actions_from_instruction(active_instruction.text)
            else:
                logger.info(f"Num of instructions: {len(instructions)}")
                for instruction in instructions:
                    logger.info(f"INSTRUCTION: {instruction}")
                logger.info(f"step() returned but no active instruction.")
            self.actions.extend(actions)
            if active_instruction is not None:
                self.actions.append(FollowAction(FollowAction.ActionCode.INSTRUCTION_DONE, active_instruction.uuid))
                self.instructions_processed.add(active_instruction.uuid)
        if len(self.actions) > 0:
            action = self.actions[0]
            self.actions.pop(0)
            return action
        else:
            # Choose a random action.
            action_codes = [FollowAction.ActionCode.FORWARDS, FollowAction.ActionCode.BACKWARDS, FollowAction.ActionCode.TURN_LEFT, FollowAction.ActionCode.TURN_RIGHT]
            action = FollowAction(random.choice(action_codes))
            return action

    def join(self):
        super().join()
        if self.exc:
            raise self.exc

def main(host, render=False, i_uuid: str = ""):
    client = RemoteClient(host, render)
    connected, reason = client.Connect()
    assert connected, f"Unable to connect: {reason}"
    actions = []
    instructions_processed = set()
    instruction_in_progress = False
    active_uuid = None
    i_uuid = i_uuid.strip()

    with client.JoinGame(timeout=timedelta(minutes=5), queue_type=RemoteClient.QueueType.FOLLOWER_ONLY, i_uuid=i_uuid.strip()) as game:
        follower = NaiveFollower(game)
        follower.run()

if __name__ == "__main__":
    fire.Fire(main)