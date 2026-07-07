"""Tracking health for the optional debug indicator."""

from enum import Enum, auto


class TrackingStatus(Enum):
    """Hand tracking quality this frame."""

    DETECTED = auto()   # Green — fresh detection
    UNSTABLE = auto()   # Yellow — holdover or recovery blend
    LOST = auto()       # Red — cursor hidden
