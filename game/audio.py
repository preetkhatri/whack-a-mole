"""Arcade sound effects loaded from generated WAV files."""

from __future__ import annotations

from pathlib import Path

import pygame

import config


class AudioManager:
    """Thin wrapper around pygame.mixer for game sound effects."""

    def __init__(self) -> None:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self._whack = self._load(config.SOUNDS_DIR / config.SOUND_WHACK)
        self._pop = self._load(config.SOUNDS_DIR / config.SOUND_POP)
        self._combo = self._load(config.SOUNDS_DIR / config.SOUND_COMBO)
        self._countdown = self._load(config.SOUNDS_DIR / config.SOUND_COUNTDOWN)
        self._go = self._load(config.SOUNDS_DIR / config.SOUND_GO)
        self._game_over = self._load(config.SOUNDS_DIR / config.SOUND_GAME_OVER)

    def play_whack(self, combo: int = 1) -> None:
        """Play whack sound; pitch rises slightly with combo streak."""
        channel = self._whack.play()
        if channel is not None and combo > 1:
            channel.set_volume(min(1.0, 0.7 + combo * 0.05))

    def play_pop(self) -> None:
        self._pop.play()

    def play_combo(self) -> None:
        self._combo.play()

    def play_countdown(self) -> None:
        self._countdown.play()

    def play_go(self) -> None:
        self._go.play()

    def play_game_over(self) -> None:
        self._game_over.play()

    @staticmethod
    def _load(path: Path) -> pygame.mixer.Sound:
        if not path.exists():
            raise FileNotFoundError(f"Missing sound asset: {path}")
        return pygame.mixer.Sound(str(path))
