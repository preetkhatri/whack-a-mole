"""Visual-only timing and constants for cursor, hits, and mole feedback."""

# Magic wand cursor
CURSOR_TRAIL_MAX = 18
CURSOR_GLOW_RADIUS = 36
CURSOR_ORB_RADIUS = 14
CURSOR_WAND_LENGTH = 52

# Mole hit presentation (gameplay timing unchanged)
MOLE_SQUASH_MS = 80
MOLE_WHACK_SINK_MS = 180
MOLE_HOVER_GLOW_RADIUS = 24
MOLE_HOVER_BOUNCE = 6

# Hit feel (visual pause — does not alter score or collision)
HIT_STOP_MS = 40
SCREEN_SHAKE_MS = 80
SCREEN_SHAKE_MAGNITUDE = 4

# Floating score text shown on whack (matches SCORE_PER_WHACK in config.py)
WHACK_POPUP_TEXT = "+10"

# Particle budgets (keep 60 FPS)
MAX_PARTICLES = 120
WHACK_STAR_COUNT = 16
WHACK_MAGIC_COUNT = 20
SMOKE_PUFF_COUNT = 12
