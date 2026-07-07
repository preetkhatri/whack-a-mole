"""Smoke test: verify imports, assets, mole logic, and camera access."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import pygame

import config
from game.assets_loader import assets_ready, load_mole_frames
from game.control_mode import ControlMode
from game.mole import Mole, MoleState, build_mole_grid
from game.tracking.input_tracker import InputTracker
from game.visual_config import MOLE_SQUASH_MS, MOLE_WHACK_SINK_MS


def test_grid() -> None:
    positions = build_mole_grid()
    assert len(positions) == 9


def test_mole_lifecycle() -> None:
    mole = Mole()
    assert mole.state == MoleState.HIDDEN
    mole.update(1000)
    assert mole.state == MoleState.RISING
    mole.update(config.MOLE_RISE_MS)
    assert mole.state == MoleState.UP
    assert mole.contains_point(*mole.display_pos)
    mole.whack()
    assert mole.state == MoleState.SQUASH
    mole.update(MOLE_SQUASH_MS)
    assert mole.state == MoleState.SINKING

    mole.update(MOLE_WHACK_SINK_MS)
    assert mole.state == MoleState.RISING


def test_assets() -> None:
    assert assets_ready(), "Assets missing — run tools/generate_assets.py"
    frames = load_mole_frames()
    assert len(frames) == config.MOLE_FRAME_COUNT


def test_camera() -> None:
    tracker = InputTracker()
    sample = tracker.poll()
    tracker.release()
    print(f"Camera OK — control sample: {sample}")


def test_app_boot() -> None:
    pygame.init()
    from game.app import GameApp

    config.USE_FULLSCREEN = False
    app = GameApp()
    app._start_mode(ControlMode.FINGER)
    for _ in range(5):
        pygame.event.pump()
        dt = app.clock.tick(config.TARGET_FPS)
        sample = app.input_tracker.poll()
        app._last_sample = sample
        app.game.update(dt, sample.hit_point)
        app._update_hover()
        app.feel.update(dt)
        app.effects.update(dt)
        app.cursor.update(sample.cursor, dt)
        app.render(app.clock.get_fps())

    app.input_tracker.release()
    pygame.quit()
    print("App boot OK — 5 frames rendered")


if __name__ == "__main__":
    pygame.init()
    test_grid()
    test_mole_lifecycle()
    test_assets()
    test_camera()
    test_app_boot()
    print("All smoke tests passed.")
