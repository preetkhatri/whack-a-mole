"""Optional tracking-status debug dot (green / yellow / red)."""

from __future__ import annotations

import pygame

import config
from game.tracking.tracking_config import tracking_config
from game.tracking.tracking_status import TrackingStatus

_STATUS_COLORS = {
    TrackingStatus.DETECTED: (60, 220, 90),
    TrackingStatus.UNSTABLE: (255, 210, 60),
    TrackingStatus.LOST: (255, 70, 70),
}


def draw_tracking_indicator(
    surface: pygame.Surface,
    status: TrackingStatus,
) -> None:
    """Draw a small status lamp in the bottom-right corner."""
    if not tracking_config.show_debug_indicator:
        return

    x = config.SCREEN_WIDTH - config.UI_PADDING - 10
    y = config.SCREEN_HEIGHT - config.UI_PADDING - 10
    color = _STATUS_COLORS.get(status, (180, 180, 180))

    glow = pygame.Surface((28, 28), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*color, 80), (14, 14), 12)
    surface.blit(glow, (x - 14, y - 14))
    pygame.draw.circle(surface, color, (x, y), 8)
    pygame.draw.circle(surface, (255, 255, 255), (x, y), 8, 2)
