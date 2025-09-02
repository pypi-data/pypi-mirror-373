"""Object entities for MiniWorld environments."""

import math

import numpy as np
from pyglet.gl import *

from ..opengl import drawBox
from .base_entity import COLOR_NAMES, COLORS, Entity, MeshEnt


class Box(Entity):
    """
    Colored box object that can be placed in MiniWorld environments.

    Boxes can be static (immovable) or dynamic (pickupable by the agent).
    They support transparency effects and domain randomization of colors.
    """

    def __init__(self, color, size=0.8, transparentable=False, static=False):
        """
        Initialize a box entity.

        Args:
            color: Color name (must be in COLORS dictionary)
            size: Box size - scalar for cube, or 3-element array for [width, height, depth]
            transparentable: Whether box can become transparent during rendering
            static: Whether box is immovable (True) or pickupable (False)
        """
        super().__init__()

        # Store transparency and static properties with descriptive names
        self.is_transparentable = transparentable
        self.static_flag = static

        # Convert size to 3D dimensions
        if isinstance(size, (int, float)):
            size = np.array([size, size, size])
        size = np.array(size)

        # Extract dimensions with clear names
        size_x, size_y, size_z = size

        self.color = color
        self.size = size

        # Calculate collision radius (distance from center to corner in XZ plane)
        self.radius = math.sqrt(size_x * size_x + size_z * size_z) / 2
        self.height = size_y

    def randomize(self, params, rng):
        """
        Apply domain randomization to box appearance.

        This method randomizes the box color by adding a bias sampled from
        the environment parameters, then clips to valid color range.

        Args:
            params: Environment parameters containing randomization settings
            rng: Random number generator for sampling
        """
        base_color = COLORS[self.color]
        color_bias = params.sample(rng, "obj_color_bias")
        self.color_vec = base_color + color_bias
        self.color_vec = np.clip(self.color_vec, 0, 1)

    def render(self):
        """Render the box using OpenGL."""
        size_x, size_y, size_z = self.size

        # Set up OpenGL state for box rendering
        glDisable(GL_TEXTURE_2D)
        glColor3f(*self.color_vec)

        # Apply transformations
        glPushMatrix()
        glTranslatef(*self.pos)
        glRotatef(self.dir * (180 / math.pi), 0, 1, 0)

        # Draw the box geometry
        drawBox(
            x_min=-size_x / 2,
            x_max=+size_x / 2,
            y_min=0,
            y_max=size_y,
            z_min=-size_z / 2,
            z_max=+size_z / 2,
        )

        glPopMatrix()

    @property
    def is_static(self):
        """Return whether this box is static (cannot move)."""
        return self.static_flag

    @property
    def trable(self):
        """Legacy property for transparency - kept for backward compatibility."""
        return self.is_transparentable


class Key(MeshEnt):
    """Key the agent can pick up, carry, and use to open doors"""

    def __init__(self, color):
        assert color in COLOR_NAMES
        super().__init__(mesh_name="key_{}".format(color), height=0.35, static=False)


class Ball(MeshEnt):
    """Ball (sphere) the agent can pick up and carry"""

    def __init__(self, color, size=0.6):
        assert color in COLOR_NAMES
        super().__init__(mesh_name="ball_{}".format(color), height=size, static=False)
