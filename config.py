"""Shared configuration for screen size, timing, and display settings."""

from pathlib import Path

# Project root (parent of this file)
ROOT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = ROOT_DIR / "assets"
MODELS_DIR = ASSETS_DIR / "models"
IMAGES_DIR = ASSETS_DIR / "images"
MOLE_FRAMES_DIR = IMAGES_DIR / "mole"
SOUNDS_DIR = ASSETS_DIR / "sounds"

# Window dimensions (desktop window)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Windowed desktop mode
USE_FULLSCREEN = False

# Target frame rate for the game loop
TARGET_FPS = 60

# Window title shown in the OS title bar
WINDOW_TITLE = "Whack-A-Mole Carnival"

# Background fallback color if the PNG is missing
BACKGROUND_COLOR = (86, 180, 255)

# --- Cursor (magic wand replaces debug dot) ---
SHOW_FINGERTIP_DEBUG = False
SHOW_FPS_DEBUG = False

# --- Mole grid (3x3) — gameplay unchanged ---
MOLE_GRID_COLS = 3
MOLE_GRID_ROWS = 3
MOLE_GRID_SPACING = 200
MOLE_RADIUS = 42
MOLE_SPAWN_INTERVAL_MS = 1000
MOLE_RISE_MS = 200
MOLE_SINK_MS = 700
# How long the mole stays fully up before ducking back down (if not whacked).
MOLE_VISIBLE_MS = 1200

# Placeholder circle colors (fallback when sprites are missing)
MOLE_COLOR = (139, 90, 43)
HOLE_COLOR = (62, 39, 20)

# --- Game rules — unchanged ---
GAME_DURATION_SECONDS = 60
COUNTDOWN_SECONDS = 3
COMBO_WINDOW_MS = 2500

# --- Desktop UI typography ---
UI_FONT_SCORE = 64
UI_FONT_TIMER = 52
UI_FONT_LABEL = 28
UI_FONT_COMBO = 48
UI_FONT_TITLE = 80
UI_FONT_BODY = 36
UI_FONT_COUNTDOWN = 120
UI_FONT_SMALL = 24
UI_PADDING = 20

# UI palette
UI_COLOR_SCORE = (255, 245, 120)
UI_COLOR_TIMER = (255, 255, 255)
UI_COLOR_TIMER_LOW = (255, 90, 90)
UI_COLOR_LABEL = (255, 255, 255)
UI_COLOR_COMBO = (255, 200, 50)
UI_COLOR_PANEL = (30, 20, 60, 180)
UI_COLOR_PANEL_BORDER = (255, 220, 80)

# MediaPipe hand landmarker model (downloaded on first run)
HAND_LANDMARKER_MODEL = MODELS_DIR / "hand_landmarker.task"
HAND_LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)

# Image assets (replace files in assets/images/ to customize)
BACKGROUND_IMAGE = "background.png"
HOLE_SPRITE = "hole.png"
MOLE_FRAME_PATTERN = "frame_{:02d}.png"
MOLE_FRAME_COUNT = 6

# Sound assets (replace files in assets/sounds/ to customize)
SOUND_WHACK = "whack.wav"
SOUND_POP = "pop.wav"
SOUND_COMBO = "combo.wav"
SOUND_COUNTDOWN = "countdown_beep.wav"
SOUND_GO = "go.wav"
SOUND_GAME_OVER = "game_over.wav"
