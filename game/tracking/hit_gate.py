"""Require consecutive in-radius frames before passing a hit to gameplay."""

from __future__ import annotations

from game.tracking.tracking_config import tracking_config


class HitGate:
    """Filters noisy hits without changing game-manager logic."""

    def __init__(self) -> None:
        self._consecutive = 0

    def reset(self) -> None:
        self._consecutive = 0

    def filter(
        self,
        hit_point: tuple[int, int] | None,
        mole,
    ) -> tuple[int, int] | None:
        """Return hit_point only after stable in-radius frames."""
        if hit_point is None or not mole.is_hittable:
            self._consecutive = 0
            return None

        if mole.contains_point(*hit_point):
            self._consecutive += 1
        else:
            self._consecutive = 0
            return None

        if self._consecutive >= tracking_config.stable_hit_frames:
            return hit_point
        return None
