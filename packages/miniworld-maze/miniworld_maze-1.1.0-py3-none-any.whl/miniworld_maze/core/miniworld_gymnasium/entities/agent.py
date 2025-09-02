"""Agent entity for MiniWorld environments."""

import math

import numpy as np
from pyglet.gl import *

from ..math import *
from .base_entity import Entity


class Agent(Entity):
    """The agent entity that represents the player/robot in the environment."""

    def __init__(self, mode="triangle"):
        super().__init__()
        self.mode = mode
        self.trable = False

        # Distance between the camera and the floor
        self.cam_height = 1.5

        # Camera up/down angles in degrees
        # Positive angles tilt the camera upwards
        self.cam_pitch = 0

        # Vertical field of view in degrees
        self.cam_fov_y = 60

        # Bounding cylinder size for the agent
        if self.mode == "circle":
            self.radius = 0.5
        else:
            self.radius = 0.6
            self.height = 1.6

        # Object currently being carried by the agent
        self.carrying = None

    @property
    def cam_pos(self):
        """Camera position in 3D space"""
        rot_y = gen_rot_matrix(Y_VEC, self.dir)
        cam_disp = np.array([self.cam_fwd_disp, self.cam_height, 0])
        cam_disp = np.dot(cam_disp, rot_y)

        return self.pos + cam_disp

    @property
    def cam_dir(self):
        """Camera direction (lookat) vector

        Note: this is useful even if just for slight domain
        randomization of camera angle
        """
        rot_z = gen_rot_matrix(Z_VEC, self.cam_pitch * math.pi / 180)
        rot_y = gen_rot_matrix(Y_VEC, self.dir)

        dir = np.dot(X_VEC, rot_z)
        dir = np.dot(dir, rot_y)

        return dir

    def randomize(self, params, rng):
        params.sample_many(
            rng,
            self,
            [
                "cam_height",
                "cam_fwd_disp",
                "cam_pitch",
                "cam_fov_y",
            ],
        )

    def render(self):
        """Draw the agent"""
        # Note: this is currently only used in the top view
        # Eventually, we will want a proper 3D model

        if self.mode == "circle":

            def draw_circle(pos, radius, num_segments):
                glBegin(GL_LINE_STRIP)
                glVertex3f(*pos)  # Center vertex
                for i in range(num_segments + 1):
                    angle = 2.0 * math.pi * i / num_segments
                    x = radius * math.cos(angle) + pos[0]
                    y = radius * math.sin(angle) + pos[2]
                    glVertex3f(*self.pos)
                    glVertex3f(x, 100.0, y)
                glEnd()

            glColor3f(1, 0, 0)
            draw_circle(self.pos, self.radius, 1024)

        elif self.mode == "triangle":
            p = self.pos + Y_VEC * 100
            dv = self.dir_vec * self.radius
            rv = self.right_vec * self.radius

            p0 = p + dv
            p1 = p + 0.75 * (rv - dv)
            p2 = p + 0.75 * (-rv - dv)

            glColor3f(1, 0, 0)
            glBegin(GL_TRIANGLES)
            glVertex3f(*p0)
            glVertex3f(*p2)
            glVertex3f(*p1)
            glEnd()

        else:
            pass

    def step(self, delta_time):
        pass
