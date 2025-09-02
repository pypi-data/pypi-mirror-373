"""Base entity classes for MiniWorld environments."""

import math

import numpy as np
from pyglet.gl import *

from ..math import *
from ..objmesh import ObjMesh

# Map of color names to RGB values
COLORS = {
    "red": np.array([1.0, 0.0, 0.0]),
    "green": np.array([0.0, 1.0, 0.0]),
    "blue": np.array([0.0, 0.0, 1.0]),
    "purple": np.array([0.44, 0.15, 0.76]),
    "yellow": np.array([1.00, 1.00, 0.00]),
    # 'grey'  : np.array([0.39, 0.39, 0.39]),
    "light_yellow": np.array([0.5, 0.00, 0.39]),
    "color1": np.array([0.7, 0.9, 0.39]),
    "color2": np.array([0.15, 0.3, 0.39]),
    "color3": np.array([1.0, 0.5, 0.0]),
    "color4": np.array([1.0, 0.0, 0.5]),
    "color5": np.array([0.3, 0.7, 0.1]),
}

# List of color names, sorted alphabetically
COLOR_NAMES = sorted(list(COLORS.keys()))


class Entity:
    """Base class for all entities in the MiniWorld environment."""

    def __init__(self):
        # World position
        # Note: for most entities, the position is at floor level
        self.pos = None

        # Direction/orientation angle in radians
        self.dir = None

        # Radius for bounding circle/cylinder
        self.radius = 0

        # Height of bounding cylinder
        self.height = 0

    def randomize(self, params, rng):
        """Set the domain randomization parameters"""
        pass

    def render(self):
        """Draw the object"""
        raise NotImplementedError

    def step(self, delta_time):
        """Update the state of the object"""
        pass

    def draw_bound(self):
        """Draw the bounding circle (used for debugging purposes)"""
        x, _, z = self.pos

        glColor3f(1, 0, 0)
        glBegin(GL_LINES)

        for i in range(60):
            a = i * 2 * math.pi / 60
            cx = x + self.radius * math.cos(a)
            cz = z + self.radius * math.sin(a)
            glVertex3f(cx, 0.01, cz)

        glEnd()

    @property
    def dir_vec(self):
        """Vector pointing in the direction of forward movement"""
        x = math.cos(self.dir)
        z = -math.sin(self.dir)
        return np.array([x, 0, z])

    @property
    def right_vec(self):
        """Vector pointing to the right of the agent"""
        x = math.sin(self.dir)
        z = math.cos(self.dir)
        return np.array([x, 0, z])

    @property
    def is_static(self):
        """True for objects that cannot move or animate (can be rendered statically)"""
        return False


class MeshEnt(Entity):
    """Entity whose appearance is defined by a mesh file

    Args:
        mesh_name: Name of the mesh file
        height: Scale the model to this height
        static: Flag indicating this object cannot move
        transparentable: Whether this entity can be made transparent
    """

    def __init__(self, mesh_name, height, static=True, transparentable=False):
        super().__init__()
        self.trable = transparentable
        self.static = static

        # Load the mesh
        self.mesh = ObjMesh.get(mesh_name)

        # Get the mesh extents
        sx, sy, sz = self.mesh.max_coords

        # Compute the mesh scaling factor
        self.scale = height / sy

        # Compute the radius and height
        self.radius = math.sqrt(sx * sx + sz * sz) * self.scale
        self.height = height

    def render(self):
        """Draw the object"""
        glPushMatrix()
        glTranslatef(*self.pos)
        glScalef(self.scale, self.scale, self.scale)
        glRotatef(self.dir * 180 / math.pi, 0, 1, 0)
        glColor3f(1, 1, 1)
        self.mesh.render()
        glPopMatrix()

    @property
    def is_static(self):
        return self.static
