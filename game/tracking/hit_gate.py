"""Require consecutive in-radius frames before passing a hit to gameplay."""

from __future__ import annotations

from game.tracking.tracking_config import tracking_config


class HitGate:
    """Filters noisy point hits and passes fast swept-path hits immediately."""

    def __init__(self) -> None:
        self._consecutive = 0
        self._prev_hit_point: tuple[int, int] | None = None

    def reset(self) -> None:
        self._consecutive = 0
        self._prev_hit_point = None

    def filter(
        self,
        hit_point: tuple[int, int] | None,
        mole,
    ) -> tuple[int, int] | None:
        """Return hit_point when a whack should register this frame.

        Point hits require ``stable_hit_frames`` consecutive frames inside the
        hit circle to reject tracking jitter.  Swept hits (movement path crosses
        the circle while the current point is outside) register on the first
        qualifying frame so fast swipes cannot tunnel through.
        """
        if hit_point is None or not mole.is_hittable:
            self._consecutive = 0
            self._prev_hit_point = None
            return None

        current = hit_point
        previous = self._prev_hit_point
        point_inside = mole.contains_point(*current)
        swept_hit = (
            previous is not None
            and not point_inside
            and mole.intersects_motion_path(current, previous)
        )

        self._prev_hit_point = current

        if swept_hit:
            self._consecutive = 0
            return current

        if point_inside:
            self._consecutive += 1
            if self._consecutive >= tracking_config.stable_hit_frames:
                return current
            return None

        self._consecutive = 0
        return None
