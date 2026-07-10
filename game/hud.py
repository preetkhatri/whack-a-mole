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


def draw_branding_header(
    surface: pygame.Surface,
    fonts: dict[str, pygame.font.Font],
    *,
    top_y: int | None = None,
) -> int:
    """Draw the game title and tagline; return the y-coordinate below the tagline."""
    cx = config.SCREEN_WIDTH // 2
    y = top_y if top_y is not None else config.UI_PADDING + 12

    brand_title = fonts["title"].render(config.GAME_TITLE, True, (255, 245, 120))
    brand_shadow = fonts["title"].render(config.GAME_TITLE, True, (60, 30, 90))
    title_rect = brand_title.get_rect(midtop=(cx, y))
    shadow_rect = brand_shadow.get_rect(midtop=(title_rect.centerx + 4, title_rect.top + 4))
    surface.blit(brand_shadow, shadow_rect)
    surface.blit(brand_title, title_rect)

    y = title_rect.bottom + 10
    tagline = fonts["body"].render(config.GAME_TAGLINE, True, (255, 255, 255))
    tag_shadow = fonts["body"].render(config.GAME_TAGLINE, True, (80, 40, 120))
    tag_rect = tagline.get_rect(midtop=(cx, y))
    tag_shadow_rect = tag_shadow.get_rect(midtop=(tag_rect.centerx + 2, tag_rect.top + 2))
    surface.blit(tag_shadow, tag_shadow_rect)
    surface.blit(tagline, tag_rect)

    return tag_rect.bottom


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

    brand_bottom = draw_branding_header(surface, fonts)

    title = fonts["title"].render("Game Over!", True, (255, 220, 80))
    label = fonts["label"].render("FINAL SCORE", True, config.UI_COLOR_LABEL)
    score_line = fonts["score"].render(str(score), True, config.UI_COLOR_SCORE)
    hint = fonts["body"].render("Press R to play again", True, (220, 220, 220))
    quit_hint = fonts["small"].render("ESC: menu / exit fullscreen", True, (180, 180, 180))
    menu_label = fonts["label"].render("Back to Menu", True, (255, 255, 255))

    padding_x = 48
    padding_y = 40
    gaps = {
        "title": 28,
        "score_block": 12,
        "actions": max(40, score_line.get_height() // 3 + 16),
        "line": 16,
        "button": 28,
    }

    menu_btn_w = max(320, menu_label.get_width() + 48)
    menu_btn_h = max(56, menu_label.get_height() + 24)

    def _stack_height(g: dict[str, int]) -> int:
        return (
            title.get_height()
            + g["title"]
            + label.get_height()
            + g["score_block"]
            + score_line.get_height()
            + g["actions"]
            + hint.get_height()
            + g["line"]
            + quit_hint.get_height()
            + g["button"]
            + menu_btn_h
        )

    max_card_h = int(config.SCREEN_HEIGHT * 0.90)
    stack_h = _stack_height(gaps)
    available_stack = max_card_h - padding_y * 2
    if stack_h > available_stack:
        scale = available_stack / stack_h
        for key in gaps:
            gaps[key] = max(8, int(gaps[key] * scale))
        stack_h = _stack_height(gaps)

    content_w = max(
        title.get_width(),
        label.get_width(),
        score_line.get_width(),
        hint.get_width(),
        quit_hint.get_width(),
        menu_btn_w,
    )

    card_w = min(content_w + padding_x * 2, int(config.SCREEN_WIDTH * 0.75))
    card_h = stack_h + padding_y * 2
    card = pygame.Rect(0, 0, card_w, card_h)
    min_card_top = brand_bottom + 20
    card.top = max(min_card_top, (config.SCREEN_HEIGHT - card_h) // 2)
    if card.bottom > config.SCREEN_HEIGHT - config.UI_PADDING:
        card.bottom = config.SCREEN_HEIGHT - config.UI_PADDING
    card.top = max(min_card_top, card.top)
    card.centerx = config.SCREEN_WIDTH // 2
    _draw_panel(surface, card, radius=36)

    cx = card.centerx
    y = card.top + padding_y

    title_rect = title.get_rect(midtop=(cx, y))
    surface.blit(title, title_rect)
    y = title_rect.bottom + gaps["title"]

    label_rect = label.get_rect(midtop=(cx, y))
    surface.blit(label, label_rect)
    y = label_rect.bottom + gaps["score_block"]

    score_rect = score_line.get_rect(midtop=(cx, y))
    surface.blit(score_line, score_rect)
    y = score_rect.bottom + gaps["actions"]

    hint_rect = hint.get_rect(midtop=(cx, y))
    surface.blit(hint, hint_rect)
    y = hint_rect.bottom + gaps["line"]

    quit_rect = quit_hint.get_rect(midtop=(cx, y))
    surface.blit(quit_hint, quit_rect)
    y = quit_rect.bottom + gaps["button"]

    menu_btn = pygame.Rect(0, 0, menu_btn_w, menu_btn_h)
    menu_btn.midtop = (cx, y)
    menu_panel = pygame.Surface((menu_btn_w, menu_btn_h), pygame.SRCALPHA)
    pygame.draw.rect(menu_panel, (255, 160, 80, 220), menu_panel.get_rect(), border_radius=16)
    pygame.draw.rect(menu_panel, (255, 255, 255), menu_panel.get_rect(), width=3, border_radius=16)
    surface.blit(menu_panel, menu_btn.topleft)
    surface.blit(menu_label, menu_label.get_rect(center=menu_btn.center))

    return menu_btn


def draw_fps(surface: pygame.Surface, font: pygame.font.Font, fps: float) -> None:
    """Tiny FPS readout for debugging."""
    if not config.SHOW_FPS_DEBUG:
        return
    fps_text = font.render(f"FPS: {max(0, int(round(fps)))}", True, (200, 200, 200))
    surface.blit(fps_text, (config.UI_PADDING, config.SCREEN_HEIGHT - 50))
