"""Shared webcam + MediaPipe hand landmark session."""

from __future__ import annotations

import time
import urllib.request
from dataclasses import dataclass

import cv2
import mediapipe as mp

import config
from game.tracking.tracking_config import tracking_config

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


@dataclass
class HandFrame:
    """Normalized hand landmarks for one detected hand."""

    landmarks: list


def ensure_hand_model() -> None:
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    if config.HAND_LANDMARKER_MODEL.exists():
        return
    print("Downloading hand landmarker model...")
    urllib.request.urlretrieve(config.HAND_LANDMARKER_URL, config.HAND_LANDMARKER_MODEL)


class HandTrackingSession:
    """Reads one camera frame per call and returns hand landmarks."""

    def __init__(
        self,
        screen_width: int = config.SCREEN_WIDTH,
        screen_height: int = config.SCREEN_HEIGHT,
        camera_index: int = 0,
    ) -> None:
        ensure_hand_model()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self._cap = cv2.VideoCapture(camera_index)
        self._timestamp_ms = 0

        cfg = tracking_config
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(config.HAND_LANDMARKER_MODEL)),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=cfg.max_num_hands,
            min_hand_detection_confidence=cfg.min_detection_confidence,
            min_hand_presence_confidence=cfg.min_presence_confidence,
            min_tracking_confidence=cfg.min_tracking_confidence,
        )
        self._landmarker = HandLandmarker.create_from_options(options)

    def read(self) -> HandFrame | None:
        """Return the first detected hand, or None."""
        t0 = time.perf_counter()
        success, frame = self._cap.read()
        t_cap = (time.perf_counter() - t0) * 1000
        if not success:
            return None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        self._timestamp_ms += 33
        results = self._landmarker.detect_for_video(mp_image, self._timestamp_ms)
        t_mp = (time.perf_counter() - t0) * 1000 - t_cap

        if config.DEBUG_LOOP_TIMING and (t_cap > 20 or t_mp > 20):
            print(f"  camera={t_cap:.1f}ms mediapipe={t_mp:.1f}ms")

        if not results.hand_landmarks:
            return None
        return HandFrame(landmarks=results.hand_landmarks[0])

    def to_screen(self, landmark) -> tuple[int, int]:
        """Map a normalized landmark to screen coordinates (mirrored X)."""
        x = int((1.0 - landmark.x) * self.screen_width)
        y = int(landmark.y * self.screen_height)
        return (x, y)

    def release(self) -> None:
        self._cap.release()
        self._landmarker.close()
