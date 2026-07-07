"""Visual effects: particles, pop-ups, bursts, and combo banners."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum, auto

import pygame

import config
from game.visual_config import (
    MAX_PARTICLES,
    SMOKE_PUFF_COUNT,
    WHACK_MAGIC_COUNT,
    WHACK_POPUP_TEXT,
    WHACK_STAR_COUNT,
)


class ParticleKind(Enum):
    SPARK = auto()
    STAR = auto()
    MAGIC = auto()
    SMOKE = auto()


@dataclass
class Particle:
    """Single effect particle."""

    x: float
    y: float
    vx: float
    vy: float
    life_ms: int
    max_life_ms: int
    color: tuple[int, int, int]
    size: float
    kind: ParticleKind = ParticleKind.SPARK
    rotation: float = 0.0
    spin: float = 0.0


@dataclass
class ScorePopup:
    """Floating text that rises and fades after a whack."""

    x: float
    y: float
    text: str
    life_ms: int
    max_life_ms: int
    color: tuple[int, int, int]
    scale: float = 1.0


class EffectsManager:
    """Manages short-lived visual feedback without affecting gameplay."""

    POPUP_DURATION_MS = 900
    COMBO_DISPLAY_MS = 1200

    def __init__(self) -> None:
        self.particles: list[Particle] = []
        self.popups: list[ScorePopup] = []
        self.combo_text: str = ""
        self.combo_timer_ms: int = 0
        self.combo_scale: float = 1.0

    def reset(self) -> None:
        self.particles.clear()
        self.popups.clear()
        self.combo_text = ""
        self.combo_timer_ms = 0
        self.combo_scale = 1.0

    def on_whack(self, x: int, y: int, combo: int) -> None:
        """Magical burst, stars, and floating '+10' on contact."""
        self._spawn_magic_burst(x, y, combo)
        self._spawn_stars(x, y, combo)
        self.popups.append(
            ScorePopup(
                x=float(x),
                y=float(y - config.MOLE_RADIUS),
                text=WHACK_POPUP_TEXT,
                life_ms=0,
                max_life_ms=self.POPUP_DURATION_MS,
                color=config.UI_COLOR_SCORE,
                scale=1.2 if combo <= 1 else 1.4,
            )
        )
        if combo >= 2:
            self.combo_text = f"{combo}x COMBO!"
            self.combo_timer_ms = self.COMBO_DISPLAY_MS
            self.combo_scale = 1.4

    def spawn_smoke_puff(self, x: int, y: int) -> None:
        """Small smoke puff when the mole vanishes into its hole."""
        for _ in range(SMOKE_PUFF_COUNT):
            self._add_particle(
                Particle(
                    x=float(x) + random.uniform(-12, 12),
                    y=float(y) + random.uniform(-6, 10),
                    vx=random.uniform(-0.8, 0.8),
                    vy=random.uniform(-2.5, -0.5),
                    life_ms=random.randint(400, 700),
                    max_life_ms=700,
                    color=(200, 200, 210),
                    size=random.uniform(8, 18),
                    kind=ParticleKind.SMOKE,
                )
            )

    def update(self, dt_ms: int) -> None:
        self._update_particles(dt_ms)
        self._update_popups(dt_ms)
        if self.combo_timer_ms > 0:
            self.combo_timer_ms = max(0, self.combo_timer_ms - dt_ms)
            self.combo_scale = max(1.0, self.combo_scale - dt_ms * 0.001)

    def draw(self, surface: pygame.Surface, fonts: dict[str, pygame.font.Font]) -> None:
        for particle in self.particles:
            self._draw_particle(surface, particle)

        for popup in self.popups:
            progress = popup.life_ms / popup.max_life_ms
            alpha = int(255 * (1.0 - progress))
            offset_y = progress * 90
            font = fonts["popup"]
            text = font.render(popup.text, True, popup.color)
            if popup.scale != 1.0:
                w = max(1, int(text.get_width() * popup.scale))
                h = max(1, int(text.get_height() * popup.scale))
                text = pygame.transform.smoothscale(text, (w, h))
            text.set_alpha(alpha)
            rect = text.get_rect(center=(int(popup.x), int(popup.y - offset_y)))
            surface.blit(text, rect)

        if self.combo_timer_ms > 0 and self.combo_text:
            self._draw_combo_banner(surface, fonts["combo"])

    def _spawn_magic_burst(self, x: int, y: int, combo: int) -> None:
        palette = [(200, 160, 255), (140, 220, 255), (255, 240, 160), (255, 180, 220)]
        for _ in range(WHACK_MAGIC_COUNT + combo * 2):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(3, 11 + combo)
            self._add_particle(
                Particle(
                    x=float(x),
                    y=float(y),
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed - random.uniform(1, 4),
                    life_ms=random.randint(300, 550),
                    max_life_ms=550,
                    color=random.choice(palette),
                    size=random.uniform(4, 10),
                    kind=ParticleKind.MAGIC,
                )
            )

    def _spawn_stars(self, x: int, y: int, combo: int) -> None:
        for _ in range(WHACK_STAR_COUNT + combo):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(5, 16)
            self._add_particle(
                Particle(
                    x=float(x),
                    y=float(y),
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed - random.uniform(3, 8),
                    life_ms=random.randint(350, 650),
                    max_life_ms=650,
                    color=random.choice([(255, 230, 80), (255, 255, 200), (255, 200, 100)]),
                    size=random.uniform(8, 16),
                    kind=ParticleKind.STAR,
                    rotation=random.uniform(0, math.tau),
                    spin=random.uniform(-0.2, 0.2),
                )
            )

    def _add_particle(self, particle: Particle) -> None:
        if len(self.particles) >= MAX_PARTICLES:
            self.particles.pop(0)
        self.particles.append(particle)

    def _draw_particle(self, surface: pygame.Surface, particle: Particle) -> None:
        life_ratio = particle.life_ms / particle.max_life_ms
        alpha = int(255 * life_ratio)

        if particle.kind == ParticleKind.STAR:
            self._draw_star(surface, particle, alpha)
            return
        if particle.kind == ParticleKind.SMOKE:
            radius = max(3, int(particle.size * (0.6 + 0.4 * life_ratio)))
            blob = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(blob, (*particle.color, int(alpha * 0.5)), (radius, radius), radius)
            surface.blit(blob, (int(particle.x - radius), int(particle.y - radius)))
            return

        radius = max(2, int(particle.size * life_ratio))
        blob = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        glow_alpha = alpha if particle.kind == ParticleKind.MAGIC else int(alpha * 0.85)
        pygame.draw.circle(blob, (*particle.color, glow_alpha), (radius, radius), radius)
        surface.blit(blob, (int(particle.x - radius), int(particle.y - radius)))

    def _draw_star(self, surface: pygame.Surface, particle: Particle, alpha: int) -> None:
        size = max(4, int(particle.size * (particle.life_ms / particle.max_life_ms)))
        points = []
        for i in range(10):
            angle = particle.rotation + i * math.pi / 5
            radius = size if i % 2 == 0 else size * 0.45
            points.append(
                (particle.x + math.cos(angle) * radius, particle.y + math.sin(angle) * radius)
            )
        star = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        shifted = [(p[0] - particle.x + size * 1.5, p[1] - particle.y + size * 1.5) for p in points]
        pygame.draw.polygon(star, (*particle.color, alpha), shifted)
        surface.blit(star, (int(particle.x - size * 1.5), int(particle.y - size * 1.5)))

    def _update_particles(self, dt_ms: int) -> None:
        gravity = 0.28
        alive: list[Particle] = []
        for particle in self.particles:
            particle.life_ms -= dt_ms
            if particle.life_ms <= 0:
                continue
            particle.x += particle.vx
            particle.y += particle.vy
            if particle.kind == ParticleKind.SMOKE:
                particle.vy -= 0.02
                particle.vx *= 0.96
            else:
                particle.vy += gravity
                particle.vx *= 0.98
            particle.rotation += particle.spin
            alive.append(particle)
        self.particles = alive

    def _update_popups(self, dt_ms: int) -> None:
        alive: list[ScorePopup] = []
        for popup in self.popups:
            popup.life_ms += dt_ms
            if popup.life_ms < popup.max_life_ms:
                alive.append(popup)
        self.popups = alive

    def _draw_combo_banner(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        text = font.render(self.combo_text, True, config.UI_COLOR_COMBO)
        if self.combo_scale > 1.0:
            w = int(text.get_width() * self.combo_scale)
            h = int(text.get_height() * self.combo_scale)
            text = pygame.transform.smoothscale(text, (max(1, w), max(1, h)))
        rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, int(config.SCREEN_HEIGHT * 0.22)))
        surface.blit(text, rect)
