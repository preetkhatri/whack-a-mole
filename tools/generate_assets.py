"""Generate placeholder PNG sprites and arcade WAV sounds."""

from __future__ import annotations

import math
import random
import struct
import sys
import wave
from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config


def _ensure_dirs() -> None:
    config.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    config.MOLE_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    config.SOUNDS_DIR.mkdir(parents=True, exist_ok=True)


def _draw_mole_face(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    *,
    eye_style: str = "normal",
    mouth_open: float = 0.0,
) -> None:
    """Draw a cartoon mole face — shared by all animation frames."""
    cx, cy = center
    pygame.draw.circle(surface, (130, 82, 42), (cx, cy), radius)
    pygame.draw.circle(surface, (95, 58, 28), (cx, cy), radius, 4)
    pygame.draw.circle(surface, (160, 110, 70), (cx, cy - radius // 3), radius // 2)

    eye_y = cy - 14
    if eye_style == "normal":
        for ox in (-20, 20):
            pygame.draw.circle(surface, (20, 20, 20), (cx + ox, eye_y), 9)
            pygame.draw.circle(surface, (255, 255, 255), (cx + ox - 2, eye_y - 3), 3)
    elif eye_style == "happy":
        for ox in (-20, 20):
            pygame.draw.arc(surface, (20, 20, 20), (cx + ox - 10, eye_y - 8, 20, 16), 0, math.pi, 4)
    elif eye_style == "stunned":
        for ox in (-20, 20):
            pygame.draw.circle(surface, (255, 255, 255), (cx + ox, eye_y), 10, 3)
            pygame.draw.circle(surface, (20, 20, 20), (cx + ox, eye_y), 3)

    nose_y = cy + 10
    pygame.draw.circle(surface, (240, 130, 130), (cx, nose_y), 11)
    if mouth_open > 0:
        pygame.draw.ellipse(surface, (60, 30, 20), (cx - 14, nose_y + 8, 28, int(12 + mouth_open * 10)))


def generate_mole_frame(path: Path, frame_index: int) -> None:
    """Draw one mole animation frame with pose variations."""
    size = config.MOLE_RADIUS * 2 + 40
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (size // 2, size // 2 + 10)

    if frame_index == 0:
        _draw_mole_face(surface, (center[0], center[1] + 30), config.MOLE_RADIUS - 8, eye_style="normal")
    elif frame_index == 1:
        _draw_mole_face(surface, (center[0], center[1] + 14), config.MOLE_RADIUS - 2, eye_style="normal")
    elif frame_index == 2:
        _draw_mole_face(surface, center, config.MOLE_RADIUS + 4, eye_style="happy", mouth_open=0.3)
    elif frame_index == 3:
        _draw_mole_face(surface, center, config.MOLE_RADIUS, eye_style="happy", mouth_open=0.5)
    elif frame_index == 4:
        _draw_mole_face(surface, center, config.MOLE_RADIUS, eye_style="stunned", mouth_open=0.8)
    else:
        _draw_mole_face(surface, (center[0], center[1] + 18), config.MOLE_RADIUS - 6, eye_style="stunned")

    pygame.image.save(surface, str(path))


def generate_hole_sprite(path: Path) -> None:
    """Draw a cartoon dirt hole with a grassy rim."""
    w = config.MOLE_RADIUS * 2 + 60
    h = config.MOLE_RADIUS + 50
    surface = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2 + 10

    pygame.draw.ellipse(surface, (55, 140, 55), (8, 0, w - 16, 36))
    pygame.draw.ellipse(surface, (30, 18, 8), (cx - config.MOLE_RADIUS - 16, cy - 10, (config.MOLE_RADIUS + 16) * 2, 44))
    pygame.draw.ellipse(surface, (12, 6, 2), (cx - config.MOLE_RADIUS, cy, config.MOLE_RADIUS * 2, 30))
    pygame.image.save(surface, str(path))


def generate_background(path: Path) -> None:
    """Paint a colourful carnival cartoon backdrop at 1920×1080."""
    w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
    surface = pygame.Surface((w, h))

    # Sky gradient
    for y in range(h):
        t = y / h
        r = int(120 + 40 * t)
        g = int(200 + 20 * t)
        b = int(255 - 30 * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (w, y))

    # Distant hills
    pygame.draw.ellipse(surface, (70, 170, 80), (-200, h - 380, 900, 320))
    pygame.draw.ellipse(surface, (55, 150, 70), (600, h - 420, 1100, 380))
    pygame.draw.ellipse(surface, (90, 190, 95), (1400, h - 360, 700, 280))

    # Carnival bunting across the top
    colors = [(255, 90, 90), (255, 210, 60), (90, 180, 255), (255, 130, 200), (130, 255, 130)]
    for i in range(14):
        x = i * 150 + 30
        tri_color = colors[i % len(colors)]
        pygame.draw.polygon(surface, tri_color, [(x, 60), (x + 70, 60), (x + 35, 110)])
        pygame.draw.line(surface, (255, 255, 255), (x + 35, 0), (x + 35, 60), 3)

    # Wooden play board
    board = pygame.Rect(260, 220, w - 520, h - 320)
    pygame.draw.rect(surface, (160, 100, 50), board, border_radius=28)
    pygame.draw.rect(surface, (110, 65, 30), board, width=8, border_radius=28)
    inner = board.inflate(-40, -40)
    pygame.draw.rect(surface, (95, 170, 75), inner, border_radius=20)
    pygame.draw.rect(surface, (70, 140, 60), inner, width=4, border_radius=20)

    # Decorative stars
    for _ in range(30):
        sx, sy = random.randint(40, w - 40), random.randint(120, 200)
        pygame.draw.circle(surface, (255, 255, 200), (sx, sy), random.randint(2, 5))

    pygame.image.save(surface, str(path))


def _save_wav(path: Path, samples: list[int], sample_rate: int = 44100) -> None:
    with wave.open(str(path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        frames = b"".join(struct.pack("<h", max(-32767, min(32767, s))) for s in samples)
        wav_file.writeframes(frames)


def _tone(freq: float, duration: float, volume: float = 0.4, decay: float = 4.0) -> list[int]:
    rate = 44100
    count = int(rate * duration)
    return [
        int(volume * math.exp(-decay * (i / rate) / duration) * math.sin(2 * math.pi * freq * i / rate) * 32767)
        for i in range(count)
    ]


def _noise_burst(duration: float, volume: float = 0.35) -> list[int]:
    rate = 44100
    count = int(rate * duration)
    return [
        int(volume * (1 - i / count) ** 2 * (random.random() * 2 - 1) * 32767)
        for i in range(count)
    ]


def generate_sounds() -> None:
    """Create arcade-style WAV effects."""
    whack = _noise_burst(0.1, 0.55) + _tone(180, 0.08, 0.35)
    pop = _tone(660, 0.07, 0.35) + _tone(880, 0.09, 0.3)
    combo = _tone(523, 0.08, 0.35) + _tone(784, 0.08, 0.35) + _tone(1047, 0.12, 0.35)
    countdown = _tone(440, 0.12, 0.4)
    go = _tone(523, 0.1, 0.4) + _tone(784, 0.15, 0.45) + _tone(1047, 0.2, 0.5)
    game_over = (
        _tone(440, 0.25, 0.35, decay=2.0)
        + _tone(330, 0.25, 0.35, decay=2.0)
        + _tone(220, 0.5, 0.35, decay=1.5)
    )

    _save_wav(config.SOUNDS_DIR / config.SOUND_WHACK, whack)
    _save_wav(config.SOUNDS_DIR / config.SOUND_POP, pop)
    _save_wav(config.SOUNDS_DIR / config.SOUND_COMBO, combo)
    _save_wav(config.SOUNDS_DIR / config.SOUND_COUNTDOWN, countdown)
    _save_wav(config.SOUNDS_DIR / config.SOUND_GO, go)
    _save_wav(config.SOUNDS_DIR / config.SOUND_GAME_OVER, game_over)


def generate_all_assets() -> None:
    """Generate every replaceable asset under assets/."""
    _ensure_dirs()
    pygame.init()
    generate_background(config.IMAGES_DIR / config.BACKGROUND_IMAGE)
    generate_hole_sprite(config.IMAGES_DIR / config.HOLE_SPRITE)
    for index in range(config.MOLE_FRAME_COUNT):
        name = config.MOLE_FRAME_PATTERN.format(index)
        generate_mole_frame(config.MOLE_FRAMES_DIR / name, index)
    generate_sounds()
    pygame.quit()


if __name__ == "__main__":
    generate_all_assets()
    print("Assets generated in", config.ASSETS_DIR)
