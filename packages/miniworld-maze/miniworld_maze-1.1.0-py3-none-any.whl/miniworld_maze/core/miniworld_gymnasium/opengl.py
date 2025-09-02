"""OpenGL utilities for MiniWorld environments.

This module now imports from the refactored rendering modules for better organization.
"""

import os

import pyglet

# Solution to https://github.com/maximecb/gym-miniworld/issues/24
# until pyglet support egl officially
if os.environ.get("PYOPENGL_PLATFORM", None) == "egl":
    pyglet.options["headless"] = True

from pyglet.gl import *

# Import all classes and functions from the refactored modules
from .rendering import FrameBuffer, Texture, drawAxes, drawBox

# Export everything for backward compatibility
__all__ = ["Texture", "FrameBuffer", "drawAxes", "drawBox"]
