"""EMA cursor smoothing, missed-frame holdover, and recovery blending."""

from __future__ import annotations

from game.tracking.control_sample import ControlSample
from game.tracking.tracking_config import tracking_config
from game.tracking.tracking_status import TrackingStatus


class CursorSmoother:
    """Smooths cursor motion and tolerates brief detection drop-outs."""

    def __init__(self) -> None:
        self._x: float | None = None
        self._y: float | None = None
        self._missed_frames = 0
        self._recovering = False

    def reset(self) -> None:
        self._x = None
        self._y = None
        self._missed_frames = 0
        self._recovering = False

    def process(
        self,
        raw_cursor: tuple[int, int] | None,
        raw_hit: tuple[int, int] | None,
    ) -> ControlSample:
        cfg = tracking_config

        if raw_cursor is not None:
            return self._process_detected(raw_cursor, raw_hit, cfg)

        self._missed_frames += 1
        if self._x is not None and self._missed_frames <= cfg.lost_tracking_frames:
            return ControlSample(
                cursor=(int(self._x), int(self._y)),
                hit_point=None,
                status=TrackingStatus.UNSTABLE,
            )

        self._recovering = self._x is not None
        self._x = None
        self._y = None
        return ControlSample.empty()

    def _process_detected(
        self,
        raw_cursor: tuple[int, int],
        raw_hit: tuple[int, int] | None,
        cfg,
    ) -> ControlSample:
        rx, ry = float(raw_cursor[0]), float(raw_cursor[1])

        if self._x is None:
            self._x, self._y = rx, ry
            self._missed_frames = 0
            self._recovering = False
            return ControlSample(
                cursor=(int(self._x), int(self._y)),
                hit_point=raw_hit,
                status=TrackingStatus.DETECTED,
            )

        alpha = cfg.recovery_smoothing_factor if self._recovering else cfg.smoothing_factor
        self._x = alpha * rx + (1.0 - alpha) * self._x
        self._y = alpha * ry + (1.0 - alpha) * self._y

        was_recovering = self._recovering or self._missed_frames > 0
        self._missed_frames = 0
        self._recovering = False

        status = TrackingStatus.UNSTABLE if was_recovering else TrackingStatus.DETECTED
        return ControlSample(
            cursor=(int(self._x), int(self._y)),
            hit_point=raw_hit,
            status=status,
        )
