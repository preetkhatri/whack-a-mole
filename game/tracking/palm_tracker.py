"""Open-palm tracking — palm center cursor, hits only when palm is open."""

from __future__ import annotations

from game.tracking.control_sample import ControlSample
from game.tracking.session import HandFrame, HandTrackingSession

# Landmark indices used for palm detection and center.
_WRIST = 0
_THUMB_TIP = 4
_FINGER_TIP_PIP = ((8, 6), (12, 10), (16, 14), (20, 18))
_PALM_CENTER_IDS = (0, 5, 9, 13, 17)


class PalmTracker:
    """Returns palm center as cursor; hit point only for a fully open palm."""

    def __init__(self, session: HandTrackingSession) -> None:
        self._session = session

    def sample(self, frame: HandFrame | None) -> ControlSample:
        if frame is None:
            return ControlSample.empty()

        landmarks = frame.landmarks
        if not _is_open_palm(landmarks):
            return ControlSample.empty()

        center = _palm_center(landmarks)
        screen_pos = self._session.to_screen(center)
        return ControlSample(cursor=screen_pos, hit_point=screen_pos)


def _is_open_palm(landmarks) -> bool:
    """True when all four fingers are extended and the hand is not a fist."""
    extended = 0
    for tip_i, pip_i in _FINGER_TIP_PIP:
        if landmarks[tip_i].y < landmarks[pip_i].y - 0.015:
            extended += 1
    if extended < 4:
        return False

    wrist = landmarks[_WRIST]
    tips = [landmarks[i] for i in (8, 12, 16, 20)]
    avg_dist = sum(_dist2(t, wrist) for t in tips) / 4
    if avg_dist < 0.018:
        return False

    # Thumb should be spread away from the palm, not tucked in a fist.
    index_mcp = landmarks[5]
    thumb_tip = landmarks[_THUMB_TIP]
    if _dist2(thumb_tip, index_mcp) < 0.004:
        return False

    return True


def _palm_center(landmarks):
    """Average wrist and MCP joints for a stable palm center."""
    class _Point:
        def __init__(self, x: float, y: float) -> None:
            self.x = x
            self.y = y

    xs = [landmarks[i].x for i in _PALM_CENTER_IDS]
    ys = [landmarks[i].y for i in _PALM_CENTER_IDS]
    return _Point(sum(xs) / len(xs), sum(ys) / len(ys))


def _dist2(a, b) -> float:
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2
