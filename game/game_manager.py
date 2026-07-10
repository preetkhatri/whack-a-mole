"""Game rules: score, timer, mole spawning, and fingertip collision."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto

import config
from game.audio import AudioManager
from game.game_speed import GameSpeed, mole_timeout_duration_ms
from game.mole import Mole, MoleState


class GamePhase(Enum):
    """High-level flow: pre-game countdown, active play, or game over."""

    COUNTDOWN = auto()
    PLAYING = auto()
    GAME_OVER = auto()


@dataclass
class WhackEvent:
    """Visual-only event emitted when the player hits a mole."""

    x: int
    y: int
    combo: int
    score: int


class GameManager:
    """Owns score, countdown timer, mole state, and win/loss conditions."""

    def __init__(self, audio: AudioManager) -> None:
        self.audio = audio
        self.mole = Mole()
        self.score = 0
        self.combo = 0
        self.time_remaining_ms = config.GAME_DURATION_SECONDS * 1000
        self.phase = GamePhase.COUNTDOWN
        self.countdown_ms = config.COUNTDOWN_SECONDS * 1000
        self.game_over = False
        self._pop_played_for_rise = False
        self._last_whack_ms = 0
        self._elapsed_ms = 0
        self.pending_whack: WhackEvent | None = None
        self.game_speed = GameSpeed.NORMAL

    def begin_round(self, speed: GameSpeed | None = None) -> None:
        """Start countdown and gameplay after the player picks a speed."""
        if speed is not None:
            self.game_speed = speed
        self.reset()

    @property
    def countdown_display(self) -> str:
        """Return '3', '2', '1', or 'GO!' for the intro overlay."""
        if self.phase != GamePhase.COUNTDOWN:
            return ""
        if self.countdown_ms <= 0:
            return "GO!"
        return str(int(math.ceil(self.countdown_ms / 1000)))

    def reset(self) -> None:
        """Start a fresh 60-second round."""
        self.mole = Mole(mole_timeout_duration_ms=mole_timeout_duration_ms(self.game_speed))
        self.score = 0
        self.combo = 0
        self.time_remaining_ms = config.GAME_DURATION_SECONDS * 1000
        self.phase = GamePhase.COUNTDOWN
        self.countdown_ms = config.COUNTDOWN_SECONDS * 1000
        self.game_over = False
        self._pop_played_for_rise = False
        self._last_whack_ms = 0
        self._elapsed_ms = 0
        self.pending_whack = None
        self.audio.play_countdown()

    def update(self, dt_ms: int, fingertip: tuple[int, int] | None) -> None:
        """Advance gameplay unless the round has ended."""
        self.pending_whack = None

        if self.phase == GamePhase.GAME_OVER:
            return

        if self.phase == GamePhase.COUNTDOWN:
            self._update_countdown(dt_ms)
            return

        self._elapsed_ms += dt_ms
        self.time_remaining_ms = max(0, self.time_remaining_ms - dt_ms)
        if self.time_remaining_ms == 0:
            self.phase = GamePhase.GAME_OVER
            self.game_over = True
            self.audio.play_game_over()
            return

        previous_state = self.mole.state
        self.mole.update(dt_ms)

        if self.mole.state == MoleState.RISING and previous_state != MoleState.RISING:
            self._pop_played_for_rise = False
        if self.mole.state == MoleState.RISING and not self._pop_played_for_rise:
            self.audio.play_pop()
            self._pop_played_for_rise = True

        # fingertip is pre-validated by HitGate (point + swept collision).
        if fingertip is not None:
            self._register_whack()

    def _update_countdown(self, dt_ms: int) -> None:
        """Tick the 3-2-1-GO intro without affecting the gameplay timer."""
        previous_second = int(math.ceil(self.countdown_ms / 1000)) if self.countdown_ms > 0 else 0
        self.countdown_ms = max(0, self.countdown_ms - dt_ms)
        current_second = int(math.ceil(self.countdown_ms / 1000)) if self.countdown_ms > 0 else 0

        if current_second != previous_second:
            if self.countdown_ms > 0:
                self.audio.play_countdown()
            else:
                self.audio.play_go()
                self.phase = GamePhase.PLAYING

    def _register_whack(self) -> None:
        """Score a hit — awards SCORE_PER_WHACK points per whack."""
        now = self._elapsed_ms
        if now - self._last_whack_ms <= config.COMBO_WINDOW_MS:
            self.combo += 1
        else:
            self.combo = 1
        self._last_whack_ms = now

        self.score += config.SCORE_PER_WHACK
        self.audio.play_whack(self.combo)
        if self.combo >= 3:
            self.audio.play_combo()

        pos = self.mole.display_pos
        self.pending_whack = WhackEvent(
            x=pos[0],
            y=pos[1],
            combo=self.combo,
            score=self.score,
        )
        self.mole.whack()

    def load_sprites(self, mole_frames, hole_image) -> None:
        """Attach PNG sprites to the mole after assets are loaded."""
        self.mole.load_sprites(mole_frames, hole_image)
