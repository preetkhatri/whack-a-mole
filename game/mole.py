"""Mole entity: grid positions, spawn timing, rise/sink animation, hit detection."""

from __future__ import annotations

import math
import random
import time
from enum import Enum, auto

import pygame

import config
from game.animations import ease_in_cubic, ease_out_back
from game.collision import point_in_circle, point_or_segment_hits_circle
from game.tracking.tracking_config import tracking_config
from game.visual_config import MOLE_HOVER_BOUNCE, MOLE_HOVER_GLOW_RADIUS, MOLE_SQUASH_MS, MOLE_WHACK_SINK_MS


class MoleState(Enum):
    """Lifecycle states for the mole."""

    HIDDEN = auto()
    RISING = auto()
    UP = auto()
    SQUASH = auto()
    SINKING = auto()


def build_mole_grid() -> list[tuple[int, int]]:
    """Return nine screen positions arranged in a centered 3x3 grid."""
    center_x = config.SCREEN_WIDTH // 2
    center_y = config.SCREEN_HEIGHT // 2 + 20
    spacing = config.MOLE_GRID_SPACING
    positions: list[tuple[int, int]] = []

    for row in range(config.MOLE_GRID_ROWS):
        for col in range(config.MOLE_GRID_COLS):
            x = center_x + (col - 1) * spacing
            y = center_y + (row - 1) * spacing
            positions.append((x, y))

    return positions


class Mole:
    """A single mole that pops up from one of nine holes."""

    def __init__(self, positions: list[tuple[int, int]] | None = None, mole_timeout_duration_ms: int | None = None) -> None:
        self.positions = positions or build_mole_grid()
        self.slot_index = 0
        self.base_x, self.base_y = self.positions[0]
        self.state = MoleState.HIDDEN
        self.spawn_timer_ms = 0
        self.animation_timer_ms = 0
        self.visible_timer_ms = 0
        self.mole_timeout_duration_ms = (
            mole_timeout_duration_ms
            if mole_timeout_duration_ms is not None
            else config.MOLE_VISIBLE_MS
        )
        self.y_offset = 0.0
        self._active_sink_ms = config.MOLE_SINK_MS
        self._is_hovered = False

        self.mole_frames: list[pygame.Surface] = []
        self.hole_sprite: pygame.Surface | None = None
        self._hidden_travel = float(config.MOLE_RADIUS * 2)
        self.vice_name: str | None = None
        self._last_vice: str | None = None
        self._vice_font_obj: pygame.font.Font | None = None

    def load_sprites(
        self,
        mole_frames: list[pygame.Surface],
        hole_image: pygame.Surface,
    ) -> None:
        self.mole_frames = mole_frames
        self.hole_sprite = hole_image
        if mole_frames:
            self._hidden_travel = float(mole_frames[0].get_height())

    @property
    def display_pos(self) -> tuple[int, int]:
        """Logical position used for collision — excludes visual-only offsets."""
        bob = 0
        if self.state == MoleState.UP:
            bob = int(math.sin(time.monotonic() * 8) * 4)
        return (self.base_x, int(self.base_y + self.y_offset + bob))

    @property
    def is_hittable(self) -> bool:
        """True when the mole is fully raised and can be whacked."""
        return self.state == MoleState.UP

    @property
    def rise_progress(self) -> float:
        return min(1.0, self.animation_timer_ms / config.MOLE_RISE_MS)

    @property
    def sink_progress(self) -> float:
        return min(1.0, self.animation_timer_ms / max(1, self._active_sink_ms))

    @property
    def squash_progress(self) -> float:
        return min(1.0, self.animation_timer_ms / MOLE_SQUASH_MS)

    def set_hover(self, active: bool) -> None:
        """Visual-only hover flag — does not affect collision."""
        self._is_hovered = active and self.state == MoleState.UP

    def update(self, dt_ms: int) -> None:
        if self.state == MoleState.HIDDEN:
            self.spawn_timer_ms += dt_ms
            if self.spawn_timer_ms >= config.MOLE_SPAWN_INTERVAL_MS:
                self.spawn_timer_ms = 0
                self._spawn_at_random_slot()
            return

        self.animation_timer_ms += dt_ms

        if self.state == MoleState.RISING:
            eased = ease_out_back(self.rise_progress)
            self.y_offset = self._hidden_travel * (1.0 - eased)
            if self.rise_progress >= 1.0:
                self.state = MoleState.UP
                self.y_offset = 0.0
                self.visible_timer_ms = 0
        elif self.state == MoleState.UP:
            self.visible_timer_ms += dt_ms
            if self.visible_timer_ms >= self.mole_timeout_duration_ms:
                self.state = MoleState.SINKING
                self.animation_timer_ms = 0
                self._active_sink_ms = MOLE_WHACK_SINK_MS
                self._is_hovered = False
        elif self.state == MoleState.SQUASH:
            if self.squash_progress >= 1.0:
                self.state = MoleState.SINKING
                self.animation_timer_ms = 0
                self._active_sink_ms = MOLE_WHACK_SINK_MS
        elif self.state == MoleState.SINKING:
            eased = ease_in_cubic(self.sink_progress)
            self.y_offset = self._hidden_travel * eased
            if self.sink_progress >= 1.0:
                self._finish_sink()

    def whack(self) -> None:
        """Squash briefly, then shrink into the hole."""
        if self.state != MoleState.UP:
            return
        self.state = MoleState.SQUASH
        self.animation_timer_ms = 0
        self._is_hovered = False

    @property
    def hit_radius(self) -> float:
        """Invisible whack radius — slightly larger than the visible mole."""
        return config.MOLE_RADIUS * tracking_config.hit_radius_multiplier

    def contains_point(self, x: int, y: int) -> bool:
        if not self.is_hittable:
            return False
        cx, cy = self.display_pos
        return point_in_circle(x, y, cx, cy, self.hit_radius)

    def intersects_motion_path(
        self,
        current: tuple[int, int],
        previous: tuple[int, int] | None,
    ) -> bool:
        """True when the cursor point or its path since last frame hits the mole."""
        if not self.is_hittable:
            return False
        return point_or_segment_hits_circle(
            (float(current[0]), float(current[1])),
            (float(previous[0]), float(previous[1])) if previous is not None else None,
            (float(self.display_pos[0]), float(self.display_pos[1])),
            self.hit_radius,
        )

    def draw_holes(self, surface: pygame.Surface) -> None:
        for x, y in self.positions:
            self._draw_hole(surface, x, y)

    def draw(self, surface: pygame.Surface) -> None:
        if self.state == MoleState.HIDDEN:
            return

        frame = self._pick_frame()
        x, y = self.display_pos

        # Visual-only hover bounce — does not move the hit box.
        if self._is_hovered:
            y += int(math.sin(time.monotonic() * 12) * MOLE_HOVER_BOUNCE)

        if self._is_hovered:
            self._draw_hover_glow(surface, x, y)

        scale_x, scale_y = self._visual_scale()
        sprite_half_h = config.MOLE_RADIUS
        if frame is not None:
            self._blit_scaled(surface, frame, x, y, scale_x, scale_y)
            sprite_half_h = max(1, int(frame.get_height() * scale_y)) // 2
        else:
            rx, ry = int(config.MOLE_RADIUS * scale_x), int(config.MOLE_RADIUS * scale_y)
            pygame.draw.ellipse(surface, config.MOLE_COLOR, (x - rx, y - ry, rx * 2, ry * 2))
            sprite_half_h = ry

        self._draw_vice_label(surface, x, y, sprite_half_h)

    def _visual_scale(self) -> tuple[float, float]:
        if self.state == MoleState.SQUASH:
            t = self.squash_progress
            return (1.0 + 0.35 * (1 - t), 1.0 - 0.35 * (1 - t))
        if self.state == MoleState.SINKING:
            t = self.sink_progress
            shrink = 1.0 - t * 0.85
            return (shrink, shrink)
        return (1.0, 1.0)

    def _draw_hover_glow(self, surface: pygame.Surface, x: int, y: int) -> None:
        pulse = 0.75 + 0.25 * math.sin(time.monotonic() * 10)
        radius = int((config.MOLE_RADIUS + MOLE_HOVER_GLOW_RADIUS) * pulse)
        glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 240, 120, 55), (radius, radius), radius)
        pygame.draw.circle(glow, (255, 255, 200, 90), (radius, radius), config.MOLE_RADIUS + 6)
        surface.blit(glow, (x - radius, y - radius))

    def _blit_scaled(
        self,
        surface: pygame.Surface,
        frame: pygame.Surface,
        x: int,
        y: int,
        scale_x: float,
        scale_y: float,
    ) -> None:
        w = max(1, int(frame.get_width() * scale_x))
        h = max(1, int(frame.get_height() * scale_y))
        scaled = pygame.transform.smoothscale(frame, (w, h)) if (scale_x, scale_y) != (1.0, 1.0) else frame
        rect = scaled.get_rect(center=(x, y))
        surface.blit(scaled, rect)

    def _pick_frame(self) -> pygame.Surface | None:
        if not self.mole_frames:
            return None

        count = len(self.mole_frames)
        if self.state == MoleState.RISING:
            index = min(count - 1, int(self.rise_progress * 3))
            return self.mole_frames[index]
        if self.state in (MoleState.UP, MoleState.SQUASH):
            idle_index = 3 if count > 3 else count - 1
            return self.mole_frames[min(idle_index, count - 1)]
        if self.state == MoleState.SINKING:
            index = min(count - 1, 4 + int(self.sink_progress * 1.5))
            return self.mole_frames[index]
        return self.mole_frames[0]

    def _pick_vice(self) -> str:
        """Pick a vice label, avoiding the previous one when possible."""
        choices = [name for name in config.VICE_NAMES if name != self._last_vice]
        if not choices:
            choices = list(config.VICE_NAMES)
        return random.choice(choices)

    def _get_vice_font(self) -> pygame.font.Font:
        if self._vice_font_obj is None:
            # Slightly larger than UI_FONT_LABEL for TV / exhibition readability.
            size = config.UI_FONT_LABEL + 6
            self._vice_font_obj = pygame.font.SysFont("arial", size, bold=True)
        return self._vice_font_obj

    _VICE_OUTLINE_OFFSETS = (
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    )

    def _draw_vice_label(self, surface: pygame.Surface, x: int, y: int, sprite_half_h: int) -> None:
        if self.vice_name is None:
            return

        font = self._get_vice_font()
        gap = 8
        anchor = (x, y - sprite_half_h - gap)
        outline_color = (0, 0, 0)
        text_color = (255, 255, 255)

        for dx, dy in self._VICE_OUTLINE_OFFSETS:
            outline = font.render(self.vice_name, True, outline_color)
            outline_rect = outline.get_rect(midbottom=anchor)
            surface.blit(outline, (outline_rect.x + dx, outline_rect.y + dy))

        label = font.render(self.vice_name, True, text_color)
        surface.blit(label, label.get_rect(midbottom=anchor))

    def _spawn_at_random_slot(self, exclude: int | None = None) -> None:
        choices = [index for index in range(len(self.positions)) if index != exclude]
        self.slot_index = random.choice(choices)
        self.base_x, self.base_y = self.positions[self.slot_index]
        self.vice_name = self._pick_vice()
        self._last_vice = self.vice_name
        self.state = MoleState.RISING
        self.animation_timer_ms = 0
        self.y_offset = self._hidden_travel

    def _finish_sink(self) -> None:
        previous_slot = self.slot_index
        self.state = MoleState.HIDDEN
        self.vice_name = None
        self.spawn_timer_ms = 0
        self.y_offset = self._hidden_travel
        self._spawn_at_random_slot(exclude=previous_slot)

    def _draw_hole(self, surface: pygame.Surface, x: int, y: int) -> None:
        if self.hole_sprite is not None:
            rect = self.hole_sprite.get_rect(center=(x, y + 10))
            surface.blit(self.hole_sprite, rect)
        else:
            pygame.draw.ellipse(
                surface,
                config.HOLE_COLOR,
                (x - config.MOLE_RADIUS - 10, y - 10, (config.MOLE_RADIUS + 10) * 2, 40),
            )
