"""Game mode selection menu."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

import config
from game.control_mode import ControlMode


@dataclass
class ModeButton:
    """One selectable play mode on the start menu."""

    mode: ControlMode
    rect: pygame.Rect
    emoji: str
    title: str
    subtitle: str
    accent: tuple[int, int, int]


class ModeMenu:
    """Colorful arcade-style menu shown before gameplay begins."""

    TITLE = "Choose Your Play Mode"

    def __init__(self, fonts: dict[str, pygame.font.Font]) -> None:
        self.fonts = fonts
        self.buttons = self._build_buttons()
        self._hover_index: int | None = None

    def _build_buttons(self) -> list[ModeButton]:
        cx = config.SCREEN_WIDTH // 2
        cy = config.SCREEN_HEIGHT // 2 + 30
        w, h = 420, 220
        gap = 48
        left = cx - w - gap // 2
        right = cx + gap // 2

        return [
            ModeButton(
                mode=ControlMode.FINGER,
                rect=pygame.Rect(left, cy - h // 2, w, h),
                emoji="🎯",
                title="Finger Mode",
                subtitle="Fast and precise",
                accent=(255, 120, 90),
            ),
            ModeButton(
                mode=ControlMode.PALM,
                rect=pygame.Rect(right, cy - h // 2, w, h),
                emoji="✋",
                title="Palm Mode",
                subtitle="Easy for younger kids",
                accent=(120, 200, 255),
            ),
        ]

    def handle_event(self, event: pygame.event.Event) -> ControlMode | None:
        """Return the chosen mode when a button is clicked."""
        if event.type == pygame.MOUSEMOTION:
            self._hover_index = self._index_at(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            index = self._index_at(event.pos)
            if index is not None:
                return self.buttons[index].mode
        return None

    def draw(self, surface: pygame.Surface) -> None:
        self._draw_backdrop(surface)

        title = self.fonts["title"].render(self.TITLE, True, (255, 245, 120))
        shadow = self.fonts["title"].render(self.TITLE, True, (60, 30, 90))
        title_rect = title.get_rect(center=(config.SCREEN_WIDTH // 2, 120))
        shadow_rect = shadow.get_rect(center=(title_rect.centerx + 4, title_rect.centery + 4))
        surface.blit(shadow, shadow_rect)
        surface.blit(title, title_rect)

        subtitle = self.fonts["body"].render("WHACK-A-MOLE CARNIVAL", True, (255, 255, 255))
        surface.blit(subtitle, subtitle.get_rect(center=(config.SCREEN_WIDTH // 2, 175)))

        for index, button in enumerate(self.buttons):
            hovered = index == self._hover_index
            self._draw_button(surface, button, hovered)

    def _index_at(self, pos: tuple[int, int]) -> int | None:
        for index, button in enumerate(self.buttons):
            if button.rect.collidepoint(pos):
                return index
        return None

    def _draw_backdrop(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 10, 50, 140))
        surface.blit(overlay, (0, 0))

        # Decorative bunting dots
        colors = [(255, 100, 100), (255, 220, 80), (100, 200, 255), (180, 255, 140)]
        for i, color in enumerate(colors * 8):
            x = 80 + i * 150
            pygame.draw.circle(surface, color, (x, 55), 14)
            pygame.draw.rect(surface, (255, 255, 255), (x - 2, 20, 4, 35))

    def _draw_button(self, surface: pygame.Surface, button: ModeButton, hovered: bool) -> None:
        rect = button.rect
        scale = 1.04 if hovered else 1.0
        if hovered:
            rect = rect.inflate(int(rect.width * 0.04), int(rect.height * 0.04))
            rect.center = button.rect.center

        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        fill = (*button.accent, 210 if hovered else 180)
        border = (255, 255, 255) if hovered else config.UI_COLOR_PANEL_BORDER
        pygame.draw.rect(panel, fill, panel.get_rect(), border_radius=28)
        pygame.draw.rect(panel, border, panel.get_rect(), width=5, border_radius=28)
        surface.blit(panel, rect.topleft)

        emoji_font = pygame.font.Font(None, 72)
        emoji = emoji_font.render(button.emoji, True, (255, 255, 255))
        surface.blit(emoji, emoji.get_rect(center=(rect.centerx, rect.top + 55)))

        title = self.fonts["body"].render(button.title, True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(rect.centerx, rect.centery + 10)))

        desc = self.fonts["small"].render(button.subtitle, True, (240, 240, 240))
        surface.blit(desc, desc.get_rect(center=(rect.centerx, rect.bottom - 42)))

        if hovered:
            hint = self.fonts["small"].render("Click to play!", True, (255, 255, 200))
            surface.blit(hint, hint.get_rect(center=(rect.centerx, rect.bottom - 16)))
