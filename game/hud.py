"""Desktop arcade HUD: score, timer, countdown, and game-over screen."""

from __future__ import annotations

import pygame

import config


def load_ui_fonts() -> dict[str, pygame.font.Font]:
    """Create fonts sized for a desktop window."""
    return {
        "score": pygame.font.Font(None, config.UI_FONT_SCORE),
        "timer": pygame.font.Font(None, config.UI_FONT_TIMER),
        "label": pygame.font.Font(None, config.UI_FONT_LABEL),
        "combo": pygame.font.Font(None, config.UI_FONT_COMBO),
        "title": pygame.font.Font(None, config.UI_FONT_TITLE),
        "body": pygame.font.Font(None, config.UI_FONT_BODY),
        "popup": pygame.font.Font(None, config.UI_FONT_COMBO),
        "countdown": pygame.font.Font(None, config.UI_FONT_COUNTDOWN),
        "small": pygame.font.Font(None, config.UI_FONT_SMALL),
    }


def _draw_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    *,
    radius: int = 24,
) -> None:
    """Draw a semi-transparent rounded panel behind HUD text."""
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, config.UI_COLOR_PANEL, panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, config.UI_COLOR_PANEL_BORDER, panel.get_rect(), width=4, border_radius=radius)
    surface.blit(panel, rect.topleft)


def draw_arcade_hud(
    surface: pygame.Surface,
    fonts: dict[str, pygame.font.Font],
    *,
    score: int,
    time_remaining_ms: int,
    combo: int,
) -> None:
    """Render full-width score and countdown timer panels."""
    # --- Score panel (top-left, large) ---
    score_label = fonts["label"].render("SCORE", True, config.UI_COLOR_LABEL)
    score_value = fonts["score"].render(str(score), True, config.UI_COLOR_SCORE)
    panel_w = max(score_label.get_width(), score_value.get_width()) + 60
    panel_h = score_label.get_height() + score_value.get_height() + 40
    score_rect = pygame.Rect(config.UI_PADDING, config.UI_PADDING, panel_w, panel_h)
    _draw_panel(surface, score_rect)
    surface.blit(score_label, (score_rect.x + 30, score_rect.y + 16))
    surface.blit(score_value, (score_rect.x + 30, score_rect.y + 16 + score_label.get_height()))

    # --- Timer panel (top-right, large) ---
    seconds = max(0, time_remaining_ms // 1000)
    timer_color = config.UI_COLOR_TIMER_LOW if seconds <= 10 else config.UI_COLOR_TIMER
    timer_label = fonts["label"].render("TIME", True, config.UI_COLOR_LABEL)
    timer_value = fonts["timer"].render(f"{seconds:02d}", True, timer_color)
    panel_w = max(timer_label.get_width(), timer_value.get_width()) + 60
    panel_h = timer_label.get_height() + timer_value.get_height() + 40
    timer_rect = pygame.Rect(
        config.SCREEN_WIDTH - config.UI_PADDING - panel_w,
        config.UI_PADDING,
        panel_w,
        panel_h,
    )
    _draw_panel(surface, timer_rect)
    surface.blit(timer_label, (timer_rect.x + 30, timer_rect.y + 16))
    surface.blit(timer_value, (timer_rect.x + 30, timer_rect.y + 16 + timer_label.get_height()))

    # --- Active combo indicator (small badge under score) ---
    if combo >= 2:
        combo_text = fonts["small"].render(f"Combo x{combo}", True, config.UI_COLOR_COMBO)
        surface.blit(combo_text, (score_rect.x + 30, score_rect.bottom + 12))


def draw_countdown_overlay(
    surface: pygame.Surface,
    fonts: dict[str, pygame.font.Font],
    text: str,
) -> None:
    """Full-screen 3-2-1-GO splash before gameplay begins."""
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surface.blit(overlay, (0, 0))

    color = (255, 240, 80) if text == "GO!" else (255, 255, 255)
    rendered = fonts["countdown"].render(text, True, color)
    shadow = fonts["countdown"].render(text, True, (40, 20, 80))
    center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
    shadow_rect = shadow.get_rect(center=(center[0] + 6, center[1] + 6))
    text_rect = rendered.get_rect(center=center)
    surface.blit(shadow, shadow_rect)
    surface.blit(rendered, text_rect)


def draw_title_banner(surface: pygame.Surface, fonts: dict[str, pygame.font.Font]) -> None:
    """Carnival title across the top centre."""
    title = fonts["body"].render("WHACK-A-MOLE CARNIVAL!", True, (255, 255, 255))
    shadow = fonts["body"].render("WHACK-A-MOLE CARNIVAL!", True, (80, 40, 120))
    rect = title.get_rect(midtop=(config.SCREEN_WIDTH // 2, config.UI_PADDING // 2))
    shadow_rect = shadow.get_rect(midtop=(rect.centerx + 3, rect.top + 3))
    surface.blit(shadow, shadow_rect)
    surface.blit(title, rect)


def draw_game_over(
    surface: pygame.Surface,
    fonts: dict[str, pygame.font.Font],
    score: int,
) -> pygame.Rect:
    """Full-screen game-over card; returns the Back to Menu button rect."""
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    card_w = int(config.SCREEN_WIDTH * 0.55)
    card_h = int(config.SCREEN_HEIGHT * 0.55)
    card = pygame.Rect(0, 0, card_w, card_h)
    card.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
    _draw_panel(surface, card, radius=36)

    title = fonts["title"].render("Game Over!", True, (255, 220, 80))
    score_line = fonts["score"].render(str(score), True, config.UI_COLOR_SCORE)
    label = fonts["label"].render("FINAL SCORE", True, config.UI_COLOR_LABEL)
    hint = fonts["body"].render("Press R to play again", True, (220, 220, 220))
    quit_hint = fonts["small"].render("ESC: menu / exit fullscreen", True, (180, 180, 180))

    menu_btn_w, menu_btn_h = 320, 56
    menu_btn = pygame.Rect(0, 0, menu_btn_w, menu_btn_h)
    menu_btn.center = (card.centerx, card.bottom - 55)
    menu_panel = pygame.Surface((menu_btn_w, menu_btn_h), pygame.SRCALPHA)
    pygame.draw.rect(menu_panel, (255, 160, 80, 220), menu_panel.get_rect(), border_radius=16)
    pygame.draw.rect(menu_panel, (255, 255, 255), menu_panel.get_rect(), width=3, border_radius=16)
    surface.blit(menu_panel, menu_btn.topleft)
    menu_label = fonts["label"].render("Back to Menu", True, (255, 255, 255))
    surface.blit(menu_label, menu_label.get_rect(center=menu_btn.center))

    surface.blit(title, title.get_rect(center=(card.centerx, card.top + 90)))
    surface.blit(label, label.get_rect(center=(card.centerx, card.centery - 30)))
    surface.blit(score_line, score_line.get_rect(center=(card.centerx, card.centery + 70)))
    surface.blit(hint, hint.get_rect(center=(card.centerx, card.bottom - 130)))
    surface.blit(quit_hint, quit_hint.get_rect(center=(card.centerx, card.bottom - 100)))

    return menu_btn


def draw_fps(surface: pygame.Surface, font: pygame.font.Font, fps: float) -> None:
    """Tiny FPS readout for debugging."""
    if not config.SHOW_FPS_DEBUG:
        return
    fps_text = font.render(f"FPS: {max(0, int(round(fps)))}", True, (200, 200, 200))
    surface.blit(fps_text, (config.UI_PADDING, config.SCREEN_HEIGHT - 50))
