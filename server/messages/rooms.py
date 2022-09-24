""" This file contains game management messages.

Messages here allow you to enumerate the current games, join a game, or create a
new game.

"""

from server.hex import HecsCoord
from server.messages.map_update import MapUpdate

from enum import Enum
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config, LetterCase
from datetime import datetime
from marshmallow import fields
from mashumaro.mixins.json import DataClassJSONMixin
from typing import List, Optional

import dateutil.parser


class Role(Enum):
    """ The role of a player in a game."""
    NONE = 0
    FOLLOWER = 1
    LEADER = 2
    MAX = 3


@dataclass(frozen=True)
class JoinResponse(DataClassJSONMixin):
    joined: bool

    place_in_queue: Optional[int]  # If joined == false.
    role: Role  # If joined == true.
    booted_from_queue: bool = False
    boot_reason: Optional[str] = ""


@dataclass(frozen=True)
class LeaveRoomNotice(DataClassJSONMixin):
    """ Used to notify a user that they have left the room. 

        This is to allow the server to boot a player. Optionally,
        a reason can be left for the player explaining why.
    """
    reason: str

@dataclass(frozen=True)
class StatsResponse(DataClassJSONMixin):
    number_of_games: int
    players_in_game: int
    players_waiting: int

class RoomRequestType(Enum):
    """ Enumeration of the different types of management requests.  """
    NONE = 0
    STATS = 1
    JOIN = 2
    CANCEL = 3
    LEAVE = 4
    MAP_SAMPLE = 5
    JOIN_FOLLOWER_ONLY = 6
    JOIN_LEADER_ONLY = 7

@dataclass(frozen=True)
class RoomManagementRequest(DataClassJSONMixin):
    type: RoomRequestType
    # This is an optional parameter to add when making a JOIN request.  If
    # added, the server will resume the game from the provided instruction.  All
    # instruction UUIDs are unique, the server goes and finds the game
    # associated with this instruction, and reconstructs the game at that point
    # (mostly accurately, but not perfectly, see state.py for implementation
    # details).
    # If you provide this, it limits who you can be paired with.
    # TODO(sharf): For now, if this is empty you might match with someone who
    # provided it. In the future, add stricter matching.
    join_game_with_instruction_uuid: Optional[str] = None

class RoomResponseType(Enum):
    """ Enumeration of the different types of management responses.  """
    NONE = 0
    STATS = 1
    JOIN_RESPONSE = 2
    LEAVE_NOTICE = 3
    ERROR = 4
    MAP_SAMPLE = 5


@dataclass(frozen=True)
class RoomManagementResponse(DataClassJSONMixin):
    type: RoomResponseType

    # Depending on the type above, the below are optionally populated.
    stats: Optional[StatsResponse]
    join_response: Optional[JoinResponse]
    leave_notice: Optional[LeaveRoomNotice]
    map_update: Optional[MapUpdate] = None
    error: str = ""
