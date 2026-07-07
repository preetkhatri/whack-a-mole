"""Backward-compatible re-export — prefer game.tracking.input_tracker."""

from game.tracking.finger_tracker import FingerTracker
from game.tracking.input_tracker import InputTracker
from game.tracking.session import HandTrackingSession, ensure_hand_model

__all__ = ["InputTracker", "FingerTracker", "HandTrackingSession", "ensure_hand_model"]
