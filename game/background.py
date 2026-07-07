"""Background rendering — colourful cartoon backdrop."""

from __future__ import annotations

import pygame

import config

_background: pygame.Surface | None = None


def set_background(image: pygame.Surface) -> None:
    """Cache the loaded background, scaled to the current window size."""
    global _background
    target = (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    if image.get_size() != target:
        _background = pygame.transform.smoothscale(image, target)
    else:
        _background = image


def draw_background(surface: pygame.Surface) -> None:
    """Blit the cartoon background, or fall back to a solid colour."""
    if _background is not None:
        surface.blit(_background, (0, 0))
    else:
        surface.fill(config.BACKGROUND_COLOR)
