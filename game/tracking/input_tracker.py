"""Facade: finger tracking → EMA smoothing → stable control sample."""

from __future__ import annotations

from game.tracking.control_sample import ControlSample
from game.tracking.cursor_smoother import CursorSmoother
from game.tracking.finger_tracker import FingerTracker
from game.tracking.hit_gate import HitGate
from game.tracking.session import HandTrackingSession


class InputTracker:
    """Single entry point for gameplay — one camera read per frame."""

    def __init__(self) -> None:
        self._session = HandTrackingSession()
        self._finger = FingerTracker(self._session)
        self._smoother = CursorSmoother()
        self.hit_gate = HitGate()

    def poll(self) -> ControlSample:
        """Read camera, smooth cursor, and return hit candidate + status."""
        frame = self._session.read()
        raw = self._finger.sample(frame)
        return self._smoother.process(raw.cursor, raw.hit_point)

    def stable_hit_point(
        self,
        sample: ControlSample,
        mole,
    ) -> tuple[int, int] | None:
        """Apply consecutive-frame gating before gameplay collision."""
        return self.hit_gate.filter(sample.hit_point, mole)

    def reset(self) -> None:
        self._smoother.reset()
        self.hit_gate.reset()

    def release(self) -> None:
        self._session.release()
