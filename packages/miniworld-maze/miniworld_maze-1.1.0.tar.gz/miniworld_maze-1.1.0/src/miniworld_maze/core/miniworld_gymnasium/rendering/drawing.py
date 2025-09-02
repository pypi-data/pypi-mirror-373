"""Drawing utility functions for MiniWorld environments."""

from pyglet.gl import *


def drawAxes(axis_length=0.1):
    """
    Draw coordinate system axes in red/green/blue colors.

    Renders X, Y, Z axes as colored line segments for debugging and visualization.
    X-axis is red, Y-axis is green, Z-axis is blue.

    Args:
        axis_length (float): Length of each axis line, defaults to 0.1 units
    """

    glBegin(GL_LINES)

    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(axis_length, 0, 0)

    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, axis_length, 0)

    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, axis_length)

    glEnd()


def drawBox(x_min, x_max, y_min, y_max, z_min, z_max):
    """
    Draw a 3D box
    """

    glBegin(GL_QUADS)

    glNormal3f(0, 0, 1)
    glVertex3f(x_max, y_max, z_max)
    glVertex3f(x_min, y_max, z_max)
    glVertex3f(x_min, y_min, z_max)
    glVertex3f(x_max, y_min, z_max)

    glNormal3f(0, 0, -1)
    glVertex3f(x_min, y_max, z_min)
    glVertex3f(x_max, y_max, z_min)
    glVertex3f(x_max, y_min, z_min)
    glVertex3f(x_min, y_min, z_min)

    glNormal3f(-1, 0, 0)
    glVertex3f(x_min, y_max, z_max)
    glVertex3f(x_min, y_max, z_min)
    glVertex3f(x_min, y_min, z_min)
    glVertex3f(x_min, y_min, z_max)

    glNormal3f(1, 0, 0)
    glVertex3f(x_max, y_max, z_min)
    glVertex3f(x_max, y_max, z_max)
    glVertex3f(x_max, y_min, z_max)
    glVertex3f(x_max, y_min, z_min)

    glNormal3f(0, 1, 0)
    glVertex3f(x_max, y_max, z_max)
    glVertex3f(x_max, y_max, z_min)
    glVertex3f(x_min, y_max, z_min)
    glVertex3f(x_min, y_max, z_max)

    glNormal3f(0, -1, 0)
    glVertex3f(x_max, y_min, z_min)
    glVertex3f(x_max, y_min, z_max)
    glVertex3f(x_min, y_min, z_max)
    glVertex3f(x_min, y_min, z_min)

    glEnd()
