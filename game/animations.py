"""Easing curves for smooth rise/fall motion."""

from __future__ import annotations

import math


def ease_out_back(t: float) -> float:
    """Overshoot ease-out — bouncy pop-up feel."""
    t = max(0.0, min(1.0, t))
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def ease_in_cubic(t: float) -> float:
    """Accelerating ease-in — quick drop back into the hole."""
    t = max(0.0, min(1.0, t))
    return t * t * t


def ease_out_cubic(t: float) -> float:
    """Decelerating ease-out — soft landing."""
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3
