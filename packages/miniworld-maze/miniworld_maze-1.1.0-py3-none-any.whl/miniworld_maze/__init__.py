"""
MiniWorld DrStrategy - Multi-Room Maze Environment Package

This package contains complete implementations of multi-room maze environment
variants used in the DrStrategy paper, along with tools for generating observations.

Available environment variants:
- NineRooms: Classic 3x3 grid of rooms (9 rooms total)
- SpiralNineRooms: 3x3 grid with spiral connections (9 rooms total)
- TwentyFiveRooms: Large 5x5 grid with 40 connections (25 rooms total)

Main modules:
- environments: Environment implementations
- wrappers: Gymnasium wrappers for PyTorch compatibility
- tools: Observation generation and utilities
"""

from .core import ObservationLevel
from .environments.factory import (
    NineRoomsEnvironmentWrapper,
)
from .environments.nine_rooms import NineRooms
from .environments.spiral_nine_rooms import SpiralNineRooms
from .environments.twenty_five_rooms import TwentyFiveRooms

__version__ = "1.0.0"
__all__ = [
    "NineRoomsEnvironmentWrapper",
    "NineRooms",
    "SpiralNineRooms",
    "TwentyFiveRooms",
    "ObservationLevel",
]
