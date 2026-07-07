"""Central configuration for hand-tracking stability (exhibition tuning)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TrackingConfig:
    """All tracking parameters in one place for easy exhibition tuning."""

    # EMA weight on the new sample (0.25–0.35 = smooth but responsive).
    smoothing_factor: float = 0.30

    # Invisible hit area = MOLE_RADIUS * this (1.25 = 25% larger).
    hit_radius_multiplier: float = 1.25

    # Keep cursor at last position for this many missed frames before hiding.
    lost_tracking_frames: int = 5

    # Slower blend when tracking resumes after a gap (prevents jumps).
    recovery_smoothing_factor: float = 0.18

    # Frames the cursor must stay inside the hit circle before a stationary
    # whack registers.  Fast swipes bypass this via swept-path detection.
    stable_hit_frames: int = 2

    # MediaPipe Hand Landmarker thresholds (Tasks API).
    # model_complexity is fixed by the bundled .task model (see HAND_LANDMARKER_MODEL).
    min_detection_confidence: float = 0.7
    min_tracking_confidence: float = 0.7
    min_presence_confidence: float = 0.7
    max_num_hands: int = 1

    # Small green/yellow/red debug dot (does not affect gameplay).
    show_debug_indicator: bool = False


# Shared singleton used across the tracking stack.
tracking_config = TrackingConfig()
