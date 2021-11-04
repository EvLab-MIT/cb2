from enum import Enum
from hex import HecsCoord

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config, LetterCase
from datetime import datetime
from marshmallow import fields

import dateutil.parser

class ActionType(Enum):
    INIT = 0
    INSTANT = 1
    ROTATE = 2
    TRANSLATE = 3
    OUTLINE = 4

class AnimationType(Enum):
    NONE = 0
    IDLE = 1
    WALKING = 2
    INSTANT = 3
    TRANSLATE = 4
    ACCEL_DECEL = 5
    SKIPPING = 6
    ROTATE = 7

@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass(frozen=True)
class Action:
    id: int
    action_type: ActionType
    animation_type: AnimationType
    displacement: HecsCoord
    rotation: float
    border_radius: float
    duration_s: float
    expiration: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=dateutil.parser.isoparse,
            mm_field=fields.DateTime(format='iso')
        ))
