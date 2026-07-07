"""Load PNG sprites and backgrounds from the assets folder."""

from __future__ import annotations

import pygame

import config


def load_image(path_under_images: str, *, alpha: bool = True) -> pygame.Surface:
    """Load a PNG relative to assets/images/."""
    path = config.IMAGES_DIR / path_under_images
    if not path.exists():
        raise FileNotFoundError(f"Missing image asset: {path}")
    image = pygame.image.load(str(path))
    if pygame.display.get_surface() is not None:
        return image.convert_alpha() if alpha else image.convert()
    return image


def load_mole_frames() -> list[pygame.Surface]:
    """Load all animated mole frames from assets/images/mole/."""
    frames: list[pygame.Surface] = []
    for index in range(config.MOLE_FRAME_COUNT):
        name = config.MOLE_FRAME_PATTERN.format(index)
        path = config.MOLE_FRAMES_DIR / name
        if not path.exists():
            break
        frames.append(load_image(f"mole/{name}"))
    return frames


def load_hole_sprite() -> pygame.Surface | None:
    path = config.IMAGES_DIR / config.HOLE_SPRITE
    if not path.exists():
        return None
    return load_image(config.HOLE_SPRITE)


def load_background() -> pygame.Surface | None:
    path = config.IMAGES_DIR / config.BACKGROUND_IMAGE
    if not path.exists():
        return None
    return load_image(config.BACKGROUND_IMAGE, alpha=False)


def assets_ready() -> bool:
    hole_ok = (config.IMAGES_DIR / config.HOLE_SPRITE).exists()
    bg_ok = (config.IMAGES_DIR / config.BACKGROUND_IMAGE).exists()
    frame_ok = (config.MOLE_FRAMES_DIR / config.MOLE_FRAME_PATTERN.format(0)).exists()
    sound_ok = (config.SOUNDS_DIR / config.SOUND_WHACK).exists()
    return hole_ok and bg_ok and frame_ok and sound_ok
