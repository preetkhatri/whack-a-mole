"""Main Pygame application: window setup, event handling, and game loop."""

import time

import pygame

import config
from game.assets_loader import assets_ready, load_background, load_hole_sprite, load_mole_frames
from game.audio import AudioManager
from game.background import draw_background, set_background
from game.display import DisplayManager
from game.effects import EffectsManager
from game.feel import GameFeel
from game.game_manager import GamePhase, GameManager
from game.game_speed import GameSpeed
from game.magic_cursor import MagicCursor
from game.menu import SpeedMenu
from game.mole import MoleState
from game.hud import (
    draw_arcade_hud,
    draw_countdown_overlay,
    draw_fps,
    draw_game_over,
    draw_title_banner,
    load_ui_fonts,
)
from game.tracking.debug_indicator import draw_tracking_indicator
from game.tracking.input_tracker import InputTracker
from tools.generate_assets import generate_all_assets


class GameApp:
    """Owns the Pygame window and runs the 60 FPS update/render loop."""

    def __init__(self) -> None:
        pygame.init()
        self._ensure_assets()

        self.display = DisplayManager(fullscreen=config.USE_FULLSCREEN)
        self.screen = self.display.screen
        self.game_surface = pygame.Surface(self.display.design_size)
        self.clock = pygame.time.Clock()
        self.fonts = load_ui_fonts()
        self.running = False
        self.in_menu = True
        self.current_game_speed: GameSpeed | None = None
        self._last_sample = None
        self._prev_mole_state = MoleState.HIDDEN
        self._menu_back_rect: pygame.Rect | None = None

        self._mole_frames: list = []
        self._hole_sprite = None

        self._load_visual_assets()
        self.input_tracker = InputTracker()
        self.audio = AudioManager()
        self.effects = EffectsManager()
        self.feel = GameFeel()
        self.cursor = MagicCursor()
        self.menu = SpeedMenu(self.fonts)
        self.game = GameManager(self.audio)
        self._apply_sprites_to_game()

    def _ensure_assets(self) -> None:
        if not assets_ready():
            generate_all_assets()

    def _load_visual_assets(self) -> None:
        background = load_background()
        if background is not None:
            set_background(background)
        self._mole_frames = load_mole_frames()
        self._hole_sprite = load_hole_sprite()

    def _apply_sprites_to_game(self) -> None:
        if self._mole_frames and self._hole_sprite is not None:
            self.game.load_sprites(self._mole_frames, self._hole_sprite)

    def _start_speed(self, speed: GameSpeed) -> None:
        """Apply the selected speed and begin the round immediately."""
        self.current_game_speed = speed
        self.input_tracker.reset()
        self.in_menu = False
        self.effects.reset()
        self.feel.reset()
        self.cursor = MagicCursor()
        self.game.begin_round(speed)
        self._apply_sprites_to_game()
        self._prev_mole_state = MoleState.HIDDEN

    def _return_to_menu(self) -> None:
        """Show the speed selection screen again."""
        self.in_menu = True
        self.current_game_speed = None
        self._last_sample = None
        self._menu_back_rect = None
        self.input_tracker.reset()
        self.effects.reset()
        self.feel.reset()
        self.cursor = MagicCursor()

    def _design_mouse_pos(self, event: pygame.event.Event) -> tuple[int, int]:
        """Convert a pygame mouse event position to design-space coordinates."""
        return self.display.screen_to_design(event.pos)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.display.toggle_fullscreen()
                self.screen = self.display.screen
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.display.fullscreen:
                    self.display.set_windowed()
                    self.screen = self.display.screen
                elif not self.in_menu:
                    self._return_to_menu()
                else:
                    self.running = False
                continue

            if self.in_menu:
                if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    chosen = self.menu.handle_event(event, self._design_mouse_pos(event))
                    if chosen is not None:
                        self._start_speed(chosen)
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game.phase == GamePhase.GAME_OVER:
                    self.game.begin_round()
                    self.input_tracker.hit_gate.reset()
                    self.effects.reset()
                    self.feel.reset()
                    self.cursor = MagicCursor()
                    self._apply_sprites_to_game()
                elif event.key == pygame.K_m and self.game.phase == GamePhase.GAME_OVER:
                    self._return_to_menu()
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.game.phase == GamePhase.GAME_OVER
                and self._menu_back_rect is not None
            ):
                ox, oy = self.feel.get_offset()
                design_pos = self._design_mouse_pos(event)
                if self._menu_back_rect.collidepoint(design_pos[0] - ox, design_pos[1] - oy):
                    self._return_to_menu()

    def _update_hover(self) -> None:
        mole = self.game.mole
        cursor = self._last_sample.cursor if self._last_sample else None
        hovering = (
            cursor is not None
            and mole.is_hittable
            and mole.contains_point(*cursor)
        )
        mole.set_hover(hovering)

    def _check_smoke_on_sink(self) -> None:
        mole = self.game.mole
        if self._prev_mole_state == MoleState.SINKING and mole.state != MoleState.SINKING:
            self.effects.spawn_smoke_puff(mole.base_x, mole.base_y + 10)
        self._prev_mole_state = mole.state

    def _render_menu(self, fps: float) -> None:
        self.game_surface.fill((0, 0, 0))
        draw_background(self.game_surface)
        self.menu.draw(self.game_surface)
        draw_fps(self.game_surface, self.fonts["small"], fps)
        self.display.present(self.game_surface)

    def render(self, fps: float) -> None:
        self.game_surface.fill((0, 0, 0))
        draw_background(self.game_surface)

        if self.game.phase != GamePhase.COUNTDOWN:
            self.game.mole.draw_holes(self.game_surface)
            self.game.mole.draw(self.game_surface)

        self.effects.draw(self.game_surface, self.fonts)

        if self.game.phase == GamePhase.PLAYING:
            draw_title_banner(self.game_surface, self.fonts)
            draw_arcade_hud(
                self.game_surface,
                self.fonts,
                score=self.game.score,
                time_remaining_ms=self.game.time_remaining_ms,
                combo=self.game.combo,
            )
        elif self.game.phase == GamePhase.COUNTDOWN:
            draw_title_banner(self.game_surface, self.fonts)
            draw_countdown_overlay(self.game_surface, self.fonts, self.game.countdown_display)

        if self._last_sample and self._last_sample.cursor is not None:
            self.cursor.draw(self.game_surface)

        draw_fps(self.game_surface, self.fonts["small"], fps)

        if self._last_sample is not None:
            draw_tracking_indicator(self.game_surface, self._last_sample.status)

        if self.game.phase == GamePhase.GAME_OVER:
            ox, oy = self.feel.get_offset()
            self._menu_back_rect = draw_game_over(self.game_surface, self.fonts, self.game.score)
        else:
            ox, oy = self.feel.get_offset()
            self._menu_back_rect = None

        self.display.present(self.game_surface, (ox, oy))

    def run(self) -> None:
        self.running = True

        while self.running:
            dt_ms = self.clock.tick(config.TARGET_FPS)
            self.handle_events()

            if self.in_menu:
                self._render_menu(self.clock.get_fps())
                continue

            t_frame = time.perf_counter()

            t0 = time.perf_counter()
            sample = self.input_tracker.poll()
            t_poll = (time.perf_counter() - t0) * 1000

            self._last_sample = sample
            self.cursor.update(sample.cursor, dt_ms)

            stable_hit = self.input_tracker.stable_hit_point(sample, self.game.mole)

            t0 = time.perf_counter()
            if not self.feel.is_frozen():
                self.game.update(dt_ms, stable_hit)
                self._check_smoke_on_sink()

            self._update_hover()

            had_pending_whack = self.game.pending_whack is not None
            if had_pending_whack:
                event = self.game.pending_whack
                self.game.pending_whack = None
                self.effects.on_whack(event.x, event.y, event.combo)
                self.feel.trigger_hit()
            t_game = (time.perf_counter() - t0) * 1000

            self.feel.update(dt_ms)
            self.effects.update(dt_ms)

            t0 = time.perf_counter()
            self.render(self.clock.get_fps())
            t_render = (time.perf_counter() - t0) * 1000

            if config.DEBUG_LOOP_TIMING:
                t_total = (time.perf_counter() - t_frame) * 1000
                if had_pending_whack or t_total > 50:
                    print(
                        f"[{time.time():.3f}] dt={dt_ms}ms frozen={self.feel.is_frozen()} "
                        f"whack={had_pending_whack} "
                        f"poll={t_poll:.1f}ms game={t_game:.1f}ms render={t_render:.1f}ms "
                        f"total={t_total:.1f}ms particles={len(self.effects.particles)} "
                        f"cursor={sample.cursor}"
                    )

        self.input_tracker.release()
        pygame.quit()
