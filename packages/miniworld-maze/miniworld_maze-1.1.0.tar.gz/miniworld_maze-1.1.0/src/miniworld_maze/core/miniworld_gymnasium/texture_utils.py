"""Texture utility functions for MiniWorld environments."""

import numpy as np

# Texture size/density in texels/meter
TEX_DENSITY = 512


def gen_texcs_wall(tex, min_x, min_y, width, height):
    """
    Generate texture coordinates for a wall quad.

    Maps wall surface dimensions to texture coordinates based on texture density.

    Args:
        tex: Texture object with width/height properties
        min_x (float): Minimum x coordinate of wall surface
        min_y (float): Minimum y coordinate of wall surface
        width (float): Width of wall surface
        height (float): Height of wall surface

    Returns:
        np.ndarray: 4x2 array of texture coordinates for wall quad vertices
    """
    xc = TEX_DENSITY / tex.width
    yc = TEX_DENSITY / tex.height

    min_u = (min_x) * xc
    max_u = (min_x + width) * xc
    min_v = (min_y) * yc
    max_v = (min_y + height) * yc

    return np.array(
        [
            [min_u, min_v],
            [min_u, max_v],
            [max_u, max_v],
            [max_u, min_v],
        ],
        dtype=np.float32,
    )


def gen_texcs_floor(tex, poss):
    """
    Generate texture coordinates for floor or ceiling surfaces.

    Maps 3D world positions directly to 2D texture coordinates by projecting
    x,z coordinates onto texture space using texture density scaling.

    Args:
        tex: Texture object with width/height properties
        poss (np.ndarray): Nx3 array of 3D world positions

    Returns:
        np.ndarray: Nx2 array of texture coordinates
    """
    texc_mul = np.array(
        [TEX_DENSITY / tex.width, TEX_DENSITY / tex.height], dtype=float
    )

    coords = np.stack([poss[:, 0], poss[:, 2]], axis=1) * texc_mul

    return coords
