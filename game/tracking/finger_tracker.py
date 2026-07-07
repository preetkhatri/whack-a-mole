"""Index-fingertip tracking — identical behaviour to the original HandTracker."""

from __future__ import annotations

from game.tracking.control_sample import ControlSample
from game.tracking.session import HandFrame, HandTrackingSession

INDEX_FINGER_TIP = 8


class FingerTracker:
    """Returns the index fingertip as both cursor and hit point."""

    def __init__(self, session: HandTrackingSession) -> None:
        self._session = session

    def sample(self, frame: HandFrame | None) -> ControlSample:
        if frame is None:
            return ControlSample.empty()

        tip = frame.landmarks[INDEX_FINGER_TIP]
        cursor = self._session.to_screen(tip)
        return ControlSample(cursor=cursor, hit_point=cursor)
