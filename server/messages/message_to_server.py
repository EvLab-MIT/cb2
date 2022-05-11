""" Defines message structure sent to server.  """

from enum import Enum
from messages.action import Action
from messages.rooms import RoomManagementRequest
from messages.live_feedback import LiveFeedback
from messages.objective import ObjectiveMessage, ObjectiveCompleteMessage
from messages.pong import Pong
from messages.turn_state import TurnComplete
from messages.tutorials import TutorialRequest, TutorialRequestType

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config, LetterCase
from datetime import datetime
from marshmallow import fields
from typing import List, Optional

import dateutil.parser
import typing


class MessageType(Enum):
    ACTIONS = 0
    STATE_SYNC_REQUEST = 1
    ROOM_MANAGEMENT = 2
    OBJECTIVE = 3
    OBJECTIVE_COMPLETED = 4
    TURN_COMPLETE = 5
    TUTORIAL_REQUEST = 6
    PONG = 7
    LIVE_FEEDBACK = 8


@dataclass_json
@dataclass(frozen=True)
class MessageToServer:
    transmit_time: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=dateutil.parser.isoparse,
            mm_field=fields.DateTime(format='iso')
        ))
    type: MessageType
    actions: Optional[List[Action]] = None
    room_request: Optional[RoomManagementRequest] = None
    objective: Optional[ObjectiveMessage] = None
    objective_complete: Optional[ObjectiveCompleteMessage] = None
    turn_complete: Optional[TurnComplete] = None
    tutorial_request: Optional[TutorialRequest] = None
    pong: Optional[Pong] = None
    live_feedback: Optional[LiveFeedback] = None
