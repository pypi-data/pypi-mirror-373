"""Constants for Nine Rooms environments to improve code readability."""

from typing import Final

# ========================
# ENVIRONMENT DIMENSIONS
# ========================

# Default room and door sizes
DEFAULT_ROOM_SIZE: Final[int] = 5
DEFAULT_DOOR_SIZE: Final[int] = 2
FACTORY_ROOM_SIZE: Final[int] = 15  # Used in factory for larger environments
FACTORY_DOOR_SIZE: Final[float] = 2.5

# Agent dimensions
AGENT_RADIUS: Final[float] = 0.5
AGENT_START_POSITION: Final[tuple[float, float, float]] = (2.5, 0.0, 2.5)

# ========================
# OBSERVATION SETTINGS
# ========================

# Default observation dimensions
DEFAULT_OBS_WIDTH: Final[int] = 80
DEFAULT_OBS_HEIGHT: Final[int] = 80

# POMDP view radius (units around agent)
POMDP_VIEW_RADIUS: Final[float] = 2.5

# Image color channels
RGB_CHANNELS: Final[int] = 3
PIXEL_VALUE_MAX: Final[int] = 255

# ========================
# ENVIRONMENT GENERATION
# ========================

# Box entity generation
BOXES_PER_ROOM: Final[int] = 9
BOX_GRID_SIZE: Final[int] = 3  # 3x3 grid of boxes per room
BOX_SIZE_FRACTION: Final[float] = 2.0 / 15.0  # Box size relative to room size
BOX_OFFSET_FRACTION: Final[float] = 0.16  # Offset from room edges

# Room positioning
ROOM_BOUNDARY_MARGIN: Final[float] = 0.05  # 95% of room size for boundaries
ROOM_CENTER_FRACTION: Final[float] = 1.0 / 3.0  # Division for box positioning

# ========================
# PERFORMANCE SETTINGS
# ========================

# Episode limits
MAX_EPISODE_STEPS: Final[int] = 1000

# Warmup and benchmark defaults
DEFAULT_BENCHMARK_STEPS: Final[int] = 100
DEFAULT_WARMUP_STEPS: Final[int] = 10

# ========================
# OBSERVATION TEST POSITIONS
# ========================


# Convenient position calculations for standard room layouts
class RoomPositions:
    """Pre-calculated positions for standard room layouts."""

    # NineRooms (3x3) strategic positions
    NINE_ROOMS_CENTER: Final[tuple[float, float, float]] = (22.5, 0.0, 22.5)
    NINE_ROOMS_TOP_LEFT: Final[tuple[float, float, float]] = (7.5, 0.0, 7.5)
    NINE_ROOMS_BOTTOM_RIGHT: Final[tuple[float, float, float]] = (37.5, 0.0, 37.5)

    # TwentyFiveRooms (5x5) strategic positions
    TWENTY_FIVE_CENTER: Final[tuple[float, float, float]] = (75.0, 0.0, 75.0)
    TWENTY_FIVE_CORNER: Final[tuple[float, float, float]] = (37.5, 0.0, 37.5)
    TWENTY_FIVE_FAR_CORNER: Final[tuple[float, float, float]] = (112.5, 0.0, 112.5)


# ========================
# RENDERING CONSTANTS
# ========================

# Frame buffer settings
DEFAULT_FRAME_BUFFER_SIZE: Final[int] = 512
HIGH_RES_FRAME_BUFFER_SIZE: Final[int] = 512
DEPTH_BUFFER_BITS: Final[int] = 8

# Lighting
DEFAULT_LIGHT_HEIGHT: Final[float] = 2.5
AMBIENT_LIGHT_LEVEL: Final[float] = 0.45

# Memory calculations (for benchmarking)
FLOAT32_BYTES: Final[int] = 4
MB_TO_BYTES: Final[int] = 1024 * 1024

# ========================
# OPENGL RENDERING CONSTANTS
# ========================

# Framebuffer scaling
TOPDOWN_FRAMEBUFFER_SCALE: Final[int] = 20

# Physics and interaction constants
PICKUP_REACH_MULTIPLIER: Final[float] = 1.5
PICKUP_RADIUS_MULTIPLIER: Final[float] = 1.2
CARRY_POSITION_OFFSET: Final[float] = 1.05
INTERACTION_DISTANCE_MULTIPLIER: Final[float] = 1.1

# OpenGL clipping planes
NEAR_CLIPPING_PLANE: Final[float] = 0.04
FAR_CLIPPING_PLANE: Final[float] = 100.0
ORTHOGRAPHIC_DEPTH_RANGE: Final[float] = 100.0

# Occlusion query dimensions
OCCLUSION_QUERY_BOX_SIZE: Final[float] = 0.1
OCCLUSION_QUERY_BOX_HEIGHT: Final[float] = 0.2

# Rendering display constants
DEFAULT_DISPLAY_WIDTH: Final[int] = 256
DEFAULT_WINDOW_WIDTH: Final[int] = 800
DEFAULT_WINDOW_HEIGHT: Final[int] = 600
FONT_SIZE: Final[int] = 14
TEXT_LABEL_WIDTH: Final[int] = 400
TEXT_MARGIN_X: Final[int] = 5
TEXT_MARGIN_Y: Final[int] = 19

# Rendering thresholds and tolerances
EDGE_FACING_THRESHOLD: Final[float] = -0.9
EDGE_TOUCHING_THRESHOLD: Final[float] = 0.05
PORTAL_CONNECTION_TOLERANCE: Final[float] = 0.001
