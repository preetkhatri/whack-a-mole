"""Smoke test: verify imports, assets, mole logic, and camera access."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import pygame

import config
from game.assets_loader import assets_ready, load_mole_frames
from game.game_speed import GameSpeed
from game.mole import Mole, MoleState, build_mole_grid
from game.collision import point_in_circle, segment_intersects_circle
from game.tracking.hit_gate import HitGate
from game.tracking.input_tracker import InputTracker
from game.visual_config import MOLE_SQUASH_MS, MOLE_WHACK_SINK_MS


def test_grid() -> None:
    positions = build_mole_grid()
    assert len(positions) == 9


def test_collision_geometry() -> None:
    assert point_in_circle(0, 0, 0, 0, 10)
    assert not point_in_circle(11, 0, 0, 0, 10)

    # Segment passes through circle centre; endpoints are outside.
    assert segment_intersects_circle(-50, 0, 50, 0, 0, 0, 10)
    assert not segment_intersects_circle(-50, 0, 50, 0, 0, 0, 5)
    # Parallel segment misses.
    assert not segment_intersects_circle(-50, 30, 50, 30, 0, 0, 10)


def _raise_mole(mole: Mole) -> None:
    mole.update(1000)
    mole.update(config.MOLE_RISE_MS)
    assert mole.state == MoleState.UP


def test_swept_hit_detection() -> None:
    mole = Mole()
    _raise_mole(mole)
    cx, cy = mole.display_pos
    offset = int(mole.hit_radius + 80)

    assert not mole.intersects_motion_path((cx - offset, cy), (cx + offset, cy))

    gate = HitGate()
    start = (cx - offset, cy)
    end = (cx + offset, cy)
    assert gate.filter(start, mole) is None
    assert gate.filter(end, mole) == end

    gate.reset()
    _raise_mole(mole)
    assert gate.filter(mole.display_pos, mole) is None
    assert gate.filter(mole.display_pos, mole) == mole.display_pos


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
    app._start_speed(GameSpeed.NORMAL)
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
    test_collision_geometry()
    test_swept_hit_detection()
    test_mole_lifecycle()
    test_assets()
    test_camera()
    test_app_boot()
    print("All smoke tests passed.")
