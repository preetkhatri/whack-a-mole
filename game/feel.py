"""Hit stop and screen shake — visual feedback only."""

from __future__ import annotations

import random

from game.visual_config import HIT_STOP_MS, SCREEN_SHAKE_MAGNITUDE, SCREEN_SHAKE_MS


class GameFeel:
    """Brief freeze and camera shake to sell successful hits."""

    def __init__(self) -> None:
        self.hit_stop_ms = 0
        self.shake_ms = 0
        self.shake_offset = (0, 0)

    def reset(self) -> None:
        self.hit_stop_ms = 0
        self.shake_ms = 0
        self.shake_offset = (0, 0)

    def trigger_hit(self) -> None:
        """Start hit-stop and screen shake on a successful whack."""
        self.hit_stop_ms = HIT_STOP_MS
        self.shake_ms = SCREEN_SHAKE_MS

    def is_frozen(self) -> bool:
        """True while gameplay animations should pause for hit-stop."""
        return self.hit_stop_ms > 0

    def update(self, dt_ms: int) -> None:
        """Tick hit-stop and decay screen shake."""
        if self.hit_stop_ms > 0:
            self.hit_stop_ms = max(0, self.hit_stop_ms - dt_ms)

        if self.shake_ms > 0:
            self.shake_ms = max(0, self.shake_ms - dt_ms)
            mag = SCREEN_SHAKE_MAGNITUDE
            t = self.shake_ms / SCREEN_SHAKE_MS
            scale = t * mag
            self.shake_offset = (
                int(random.uniform(-scale, scale)),
                int(random.uniform(-scale, scale)),
            )
        else:
            self.shake_offset = (0, 0)

    def get_offset(self) -> tuple[int, int]:
        """Pixel offset to apply when blitting the game layer."""
        return self.shake_offset
