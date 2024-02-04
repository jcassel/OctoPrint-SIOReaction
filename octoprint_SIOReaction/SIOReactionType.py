from enum import Enum


class SIOReactionType(Enum):
    NONE = 0
    INPUT_ACTIVE = 1
    INPUT_NOT_ACTIVE = 2
    INPUT_CHANGE = 3
    OUTPUT_ACTIVE = 4
    OUTPUT_NOT_ACTIVE = 5
    OUTPUT_CHANGE = 6
    GCODE = 7
