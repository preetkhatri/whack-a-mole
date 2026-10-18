"""Bundled fonts for exhibition machines (no system-font dependency)."""

from __future__ import annotations

from functools import lru_cache

import pygame

import config


@lru_cache(maxsize=8)
def load_devanagari_font(size: int) -> pygame.font.Font:
    """Load Noto Sans Devanagari from assets/fonts, with Arial fallback."""
    path = config.DEVANAGARI_FONT_PATH
    if path.exists():
        return pygame.font.Font(str(path), size)
    return pygame.font.SysFont("arial", size, bold=True)
