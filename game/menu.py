"""Game speed selection menu."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

import config
from game.game_speed import GameSpeed


@dataclass
class SpeedButton:
    """One selectable speed on the start menu."""

    speed: GameSpeed
    rect: pygame.Rect
    emoji: str
    title: str
    subtitle: str
    accent: tuple[int, int, int]


class SpeedMenu:
    """Colorful arcade-style speed picker shown before gameplay begins."""

    TITLE = "Choose Game Speed"

    def __init__(self, fonts: dict[str, pygame.font.Font]) -> None:
        self.fonts = fonts
        self.buttons = self._build_buttons()
        self._hover_index: int | None = None

    def _build_buttons(self) -> list[SpeedButton]:
        w, h = 340, 210
        gap = 28
        total_width = w * 3 + gap * 2
        start_x = (config.SCREEN_WIDTH - total_width) // 2
        y = config.SCREEN_HEIGHT // 2 - h // 2 + 20

        specs = [
            (
                GameSpeed.FAST,
                "⚡",
                "Fast Mode",
                "Moles disappear after 0.5 seconds if not hit.",
                (255, 120, 90),
            ),
            (
                GameSpeed.NORMAL,
                "🎯",
                "Normal Mode",
                "Balanced gameplay.",
                (120, 200, 255),
            ),
            (
                GameSpeed.SLOW,
                "🐢",
                "Slow Mode",
                "Moles remain for 2 seconds if not hit.",
                (140, 220, 140),
            ),
        ]

        buttons: list[SpeedButton] = []
        for index, (speed, emoji, title, subtitle, accent) in enumerate(specs):
            x = start_x + index * (w + gap)
            buttons.append(
                SpeedButton(
                    speed=speed,
                    rect=pygame.Rect(x, y, w, h),
                    emoji=emoji,
                    title=title,
                    subtitle=subtitle,
                    accent=accent,
                )
            )
        return buttons

    def handle_event(self, event: pygame.event.Event) -> GameSpeed | None:
        """Return the chosen speed when a button is clicked."""
        if event.type == pygame.MOUSEMOTION:
            self._hover_index = self._index_at(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            index = self._index_at(event.pos)
            if index is not None:
                return self.buttons[index].speed
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
            self._draw_button(surface, button, index == self._hover_index)

    def _index_at(self, pos: tuple[int, int]) -> int | None:
        for index, button in enumerate(self.buttons):
            if button.rect.collidepoint(pos):
                return index
        return None

    def _draw_backdrop(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 10, 50, 140))
        surface.blit(overlay, (0, 0))

        colors = [(255, 100, 100), (255, 220, 80), (100, 200, 255), (180, 255, 140)]
        for i, color in enumerate(colors * 8):
            x = 80 + i * 150
            pygame.draw.circle(surface, color, (x, 55), 14)
            pygame.draw.rect(surface, (255, 255, 255), (x - 2, 20, 4, 35))

    def _draw_button(self, surface: pygame.Surface, button: SpeedButton, hovered: bool) -> None:
        rect = button.rect
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
        surface.blit(emoji, emoji.get_rect(center=(rect.centerx, rect.top + 50)))

        title = self.fonts["body"].render(button.title, True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(rect.centerx, rect.centery + 5)))

        desc = self._wrap_subtitle(button.subtitle, rect.width - 40)
        desc_y = rect.centery + 38
        for line in desc:
            rendered = self.fonts["small"].render(line, True, (240, 240, 240))
            surface.blit(rendered, rendered.get_rect(center=(rect.centerx, desc_y)))
            desc_y += rendered.get_height() + 4

        if hovered:
            hint = self.fonts["small"].render("Click to play!", True, (255, 255, 200))
            surface.blit(hint, hint.get_rect(center=(rect.centerx, rect.bottom - 16)))

    def _wrap_subtitle(self, text: str, max_width: int) -> list[str]:
        """Split subtitle text to fit inside a button."""
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            if self.fonts["small"].render(trial, True, (255, 255, 255)).get_width() <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines or [text]
