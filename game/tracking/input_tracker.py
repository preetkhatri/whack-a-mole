"""Facade that reads the active control mode and returns a ControlSample."""

from __future__ import annotations

from game.control_mode import ControlMode
from game.tracking.control_sample import ControlSample
from game.tracking.finger_tracker import FingerTracker
from game.tracking.palm_tracker import PalmTracker
from game.tracking.session import HandTrackingSession


class InputTracker:
    """Single entry point for gameplay — one camera read per frame."""

    def __init__(self) -> None:
        self._session = HandTrackingSession()
        self._finger = FingerTracker(self._session)
        self._palm = PalmTracker(self._session)
        self.current_control_mode = ControlMode.FINGER

    def poll(self) -> ControlSample:
        """Process the webcam once and return cursor/hit data for the active mode."""
        frame = self._session.read()
        if self.current_control_mode == ControlMode.PALM:
            return self._palm.sample(frame)
        return self._finger.sample(frame)

    def release(self) -> None:
        self._session.release()
