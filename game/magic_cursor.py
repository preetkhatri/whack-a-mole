"""Magical wand cursor — replaces the debug red dot."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from game.visual_config import (
    CURSOR_GLOW_RADIUS,
    CURSOR_ORB_RADIUS,
    CURSOR_TRAIL_MAX,
    CURSOR_WAND_LENGTH,
)


@dataclass
class TrailSparkle:
    """Single sparkle left behind by the wand tip."""

    x: float
    y: float
    life_ms: int
    max_life_ms: int
    size: float
    color: tuple[int, int, int]


class MagicCursor:
    """Glowing magic-wand cursor with trail, orb tip, and motion tilt."""

    SPARKLE_COLORS = [
        (255, 240, 120),
        (180, 220, 255),
        (255, 180, 255),
        (255, 255, 255),
    ]

    def __init__(self) -> None:
        self.position: tuple[int, int] | None = None
        self._prev: tuple[float, float] | None = None
        self.angle = -math.pi / 2
        self.trail: list[TrailSparkle] = []
        self._pulse = 0.0

    def update(self, fingertip: tuple[int, int] | None, dt_ms: int) -> None:
        """Track movement, rotation, and trail sparkles."""
        self._pulse += dt_ms * 0.008
        self._tick_trail(dt_ms)

        if fingertip is None:
            self.position = None
            self._prev = None
            return

        x, y = float(fingertip[0]), float(fingertip[1])
        if self._prev is not None:
            dx, dy = x - self._prev[0], y - self._prev[1]
            dist_sq = dx * dx + dy * dy
            if dist_sq > 9:
                target = math.atan2(dy, dx)
                # Smooth rotation toward movement direction.
                delta = (target - self.angle + math.pi) % (2 * math.pi) - math.pi
                self.angle += delta * 0.25
                self._spawn_trail(x, y, min(1.0, math.sqrt(dist_sq) / 18.0))

        self._prev = (x, y)
        self.position = fingertip

    def draw(self, surface: pygame.Surface) -> None:
        """Draw trail, glow, wand, and orb at the fingertip."""
        for sparkle in self.trail:
            self._draw_sparkle(surface, sparkle)

        if self.position is None:
            return

        tip_x, tip_y = self.position
        self._draw_soft_glow(surface, tip_x, tip_y)
        self._draw_wand(surface, tip_x, tip_y)
        self._draw_orb(surface, tip_x, tip_y)

    def _spawn_trail(self, x: float, y: float, intensity: float) -> None:
        if intensity < 0.15:
            return
        count = max(1, int(intensity * 2))
        for _ in range(count):
            if len(self.trail) >= CURSOR_TRAIL_MAX:
                self.trail.pop(0)
            self.trail.append(
                TrailSparkle(
                    x=x + random.uniform(-4, 4),
                    y=y + random.uniform(-4, 4),
                    life_ms=random.randint(180, 420),
                    max_life_ms=420,
                    size=random.uniform(3, 7),
                    color=random.choice(self.SPARKLE_COLORS),
                )
            )

    def _tick_trail(self, dt_ms: int) -> None:
        alive: list[TrailSparkle] = []
        for sparkle in self.trail:
            sparkle.life_ms -= dt_ms
            if sparkle.life_ms > 0:
                alive.append(sparkle)
        self.trail = alive

    def _draw_sparkle(self, surface: pygame.Surface, sparkle: TrailSparkle) -> None:
        alpha = int(200 * sparkle.life_ms / sparkle.max_life_ms)
        radius = max(1, int(sparkle.size * sparkle.life_ms / sparkle.max_life_ms))
        blob = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(blob, (*sparkle.color, alpha), (radius + 1, radius + 1), radius)
        surface.blit(blob, (int(sparkle.x - radius), int(sparkle.y - radius)))

    def _draw_soft_glow(self, surface: pygame.Surface, x: int, y: int) -> None:
        pulse = 0.85 + 0.15 * math.sin(self._pulse)
        for scale, alpha in ((1.6, 30), (1.2, 50), (0.9, 70)):
            r = int(CURSOR_GLOW_RADIUS * scale * pulse)
            glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (160, 120, 255, alpha), (r, r), r)
            surface.blit(glow, (x - r, y - r))

    def _draw_wand(self, surface: pygame.Surface, tip_x: int, tip_y: int) -> None:
        """Vector wand placeholder — swap with a sprite later."""
        length = CURSOR_WAND_LENGTH
        handle_x = tip_x - math.cos(self.angle) * length
        handle_y = tip_y - math.sin(self.angle) * length

        # Soft shadow
        pygame.draw.line(
            surface,
            (40, 20, 60),
            (int(handle_x + 2), int(handle_y + 2)),
            (tip_x + 2, tip_y + 2),
            7,
        )
        # Wooden shaft
        pygame.draw.line(
            surface,
            (120, 70, 30),
            (int(handle_x), int(handle_y)),
            (tip_x, tip_y),
            6,
        )
        pygame.draw.line(
            surface,
            (180, 120, 60),
            (int(handle_x), int(handle_y)),
            (tip_x, tip_y),
            2,
        )
        # Star pommel at handle end
        self._draw_star(surface, int(handle_x), int(handle_y), 9, (255, 220, 80))

    def _draw_orb(self, surface: pygame.Surface, x: int, y: int) -> None:
        pulse = 0.9 + 0.1 * math.sin(self._pulse * 2)
        r = int(CURSOR_ORB_RADIUS * pulse)
        for scale, color, alpha in (
            (1.8, (200, 160, 255), 40),
            (1.3, (140, 220, 255), 80),
            (1.0, (255, 255, 255), 220),
        ):
            radius = int(r * scale)
            orb = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(orb, (*color, alpha), (radius, radius), radius)
            surface.blit(orb, (x - radius, y - radius))

    @staticmethod
    def _draw_star(
        surface: pygame.Surface,
        cx: int,
        cy: int,
        size: int,
        color: tuple[int, int, int],
    ) -> None:
        points = []
        for i in range(10):
            angle = -math.pi / 2 + i * math.pi / 5
            radius = size if i % 2 == 0 else size * 0.45
            points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
        pygame.draw.polygon(surface, color, points)
