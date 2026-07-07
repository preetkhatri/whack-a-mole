"""Shared types for tracker output."""

from __future__ import annotations

from dataclasses import dataclass

from game.tracking.tracking_status import TrackingStatus


@dataclass(frozen=True)
class ControlSample:
    """Smoothed cursor, hit candidate, and tracking health."""

    cursor: tuple[int, int] | None
    hit_point: tuple[int, int] | None
    status: TrackingStatus = TrackingStatus.LOST

    @staticmethod
    def empty() -> ControlSample:
        return ControlSample(cursor=None, hit_point=None, status=TrackingStatus.LOST)
