"""Shared types for tracker output."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ControlSample:
    """Cursor position for display and optional hit point for collision."""

    cursor: tuple[int, int] | None
    hit_point: tuple[int, int] | None

    @staticmethod
    def empty() -> ControlSample:
        return ControlSample(cursor=None, hit_point=None)
