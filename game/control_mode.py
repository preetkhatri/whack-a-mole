"""Control mode constants for finger vs palm input."""

from enum import Enum, auto


class ControlMode(Enum):
    """How the player controls the on-screen cursor."""

    FINGER = auto()
    PALM = auto()
