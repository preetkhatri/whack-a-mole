"""Display setup: fullscreen detection, letterboxed scaling, coordinate mapping."""

from __future__ import annotations

import pygame

import config


class DisplayManager:
    """Owns the OS window and maps design-space gameplay to the physical display.

    Game logic always renders to a fixed design resolution (``config.DESIGN_WIDTH``
    x ``config.DESIGN_HEIGHT``).  This class scales that surface uniformly to fit
    the monitor without stretching, adding letterbox bars when aspect ratios differ.
    """

    def __init__(self, *, fullscreen: bool = config.USE_FULLSCREEN) -> None:
        self.fullscreen = fullscreen
        self.screen: pygame.Surface
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.scaled_width = config.DESIGN_WIDTH
        self.scaled_height = config.DESIGN_HEIGHT
        self._scaled_buffer: pygame.Surface | None = None
        self._create_display()

    @property
    def design_size(self) -> tuple[int, int]:
        return (config.DESIGN_WIDTH, config.DESIGN_HEIGHT)

    def _desktop_size(self) -> tuple[int, int]:
        """Return the primary display resolution in pixels."""
        info = pygame.display.Info()
        return (max(1, info.current_w), max(1, info.current_h))

    def _create_display(self) -> None:
        if self.fullscreen:
            size = self._desktop_size()
            flags = pygame.FULLSCREEN
        else:
            size = (config.DESIGN_WIDTH, config.DESIGN_HEIGHT)
            flags = 0

        self.screen = pygame.display.set_mode(size, flags)
        pygame.display.set_caption(config.WINDOW_TITLE)
        self._update_layout()

    def _update_layout(self) -> None:
        screen_w, screen_h = self.screen.get_size()
        design_w, design_h = config.DESIGN_WIDTH, config.DESIGN_HEIGHT

        self.scale = min(screen_w / design_w, screen_h / design_h)
        self.scaled_width = max(1, int(design_w * self.scale))
        self.scaled_height = max(1, int(design_h * self.scale))
        self.offset_x = (screen_w - self.scaled_width) // 2
        self.offset_y = (screen_h - self.scaled_height) // 2
        self._scaled_buffer = pygame.Surface((self.scaled_width, self.scaled_height))

    def toggle_fullscreen(self) -> None:
        """Switch between fullscreen and a windowed design-resolution view."""
        self.fullscreen = not self.fullscreen
        self._create_display()

    def set_windowed(self) -> None:
        """Leave fullscreen without toggling off if already windowed."""
        if not self.fullscreen:
            return
        self.fullscreen = False
        self._create_display()

    def present(
        self,
        game_surface: pygame.Surface,
        shake_offset: tuple[int, int] = (0, 0),
    ) -> None:
        """Scale ``game_surface`` to the display with letterboxing and screen shake."""
        self.screen.fill(config.LETTERBOX_COLOR)
        shake_x, shake_y = shake_offset
        dest_x = self.offset_x + int(shake_x * self.scale)
        dest_y = self.offset_y + int(shake_y * self.scale)

        if (
            self.scale == 1.0
            and self.offset_x == 0
            and self.offset_y == 0
            and shake_x == 0
            and shake_y == 0
        ):
            self.screen.blit(game_surface, (0, 0))
        else:
            assert self._scaled_buffer is not None
            pygame.transform.scale(
                game_surface,
                (self.scaled_width, self.scaled_height),
                self._scaled_buffer,
            )
            self.screen.blit(self._scaled_buffer, (dest_x, dest_y))

        pygame.display.flip()

    def screen_to_design(self, pos: tuple[int, int]) -> tuple[int, int]:
        """Map a mouse position on the physical window to design coordinates."""
        if self.scale <= 0:
            return pos
        x = (pos[0] - self.offset_x) / self.scale
        y = (pos[1] - self.offset_y) / self.scale
        return (int(x), int(y))
