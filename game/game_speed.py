"""Game speed presets — controls how long an unhit mole stays visible."""

from __future__ import annotations

from enum import Enum, auto

import config


class GameSpeed(Enum):
    """How long a mole remains on screen if the player does not hit it."""

    FAST = auto()
    NORMAL = auto()
    SLOW = auto()


# Seconds an unhit mole stays fully raised before ducking down.
_SPEED_TIMEOUT_SECONDS: dict[GameSpeed, float] = {
    GameSpeed.FAST: 0.5,
    GameSpeed.NORMAL: config.MOLE_VISIBLE_MS / 1000.0,
    GameSpeed.SLOW: 2.0,
}


def mole_timeout_duration(speed: GameSpeed) -> float:
    """Return mole visibility timeout in seconds for the given speed."""
    return _SPEED_TIMEOUT_SECONDS[speed]


def mole_timeout_duration_ms(speed: GameSpeed) -> int:
    """Return mole visibility timeout in milliseconds for the given speed."""
    return int(mole_timeout_duration(speed) * 1000)
