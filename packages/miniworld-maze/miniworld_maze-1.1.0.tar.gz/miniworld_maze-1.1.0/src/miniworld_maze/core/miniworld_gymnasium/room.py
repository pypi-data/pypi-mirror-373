"""Room class for MiniWorld environments."""

import numpy as np
from pyglet.gl import *

from .math import Y_VEC
from .opengl import Texture
from .texture_utils import gen_texcs_floor, gen_texcs_wall

# Default wall height for room
DEFAULT_WALL_HEIGHT = 2.74


class Room:
    """Represent an individual room and its contents"""

    def __init__(
        self,
        outline,
        wall_height=DEFAULT_WALL_HEIGHT,
        floor_tex="floor_tiles_bw",
        wall_tex="concrete",
        ceil_tex="concrete_tiles",
        no_ceiling=False,
    ):
        # The outlien should have shape Nx2
        assert len(outline.shape) == 2
        assert outline.shape[1] == 2
        assert outline.shape[0] >= 3

        # Add a Y coordinate to the outline points
        outline = np.insert(outline, 1, 0, axis=1)

        # Number of outline vertices / walls
        self.num_walls = outline.shape[0]

        # List of 2D points forming the outline of the room
        # Shape is Nx3
        self.outline = outline

        # Compute the min and max x, z extents
        self.min_x = self.outline[:, 0].min()
        self.max_x = self.outline[:, 0].max()
        self.min_z = self.outline[:, 2].min()
        self.max_z = self.outline[:, 2].max()

        # Compute midpoint coordinates
        self.mid_x = (self.max_x + self.min_x) / 2
        self.mid_z = (self.max_z + self.min_z) / 2

        # Compute approximate surface area
        self.area = (self.max_x - self.min_x) * (self.max_z - self.min_z)

        # Compute room edge directions and normals
        # Compute edge vectors (p1 - p0)
        # For the first point, p0 is the last
        # For the last point, p0 is p_n-1
        next_pts = np.concatenate(
            [self.outline[1:], np.expand_dims(self.outline[0], axis=0)], axis=0
        )
        self.edge_dirs = next_pts - self.outline
        self.edge_dirs = (self.edge_dirs.T / np.linalg.norm(self.edge_dirs, axis=1)).T
        self.edge_norms = -np.cross(self.edge_dirs, Y_VEC)
        self.edge_norms = (
            self.edge_norms.T / np.linalg.norm(self.edge_norms, axis=1)
        ).T

        # Height of the room walls
        self.wall_height = wall_height

        # No ceiling flag
        self.no_ceiling = no_ceiling

        # Texture names
        self.wall_tex_name = wall_tex
        self.floor_tex_name = floor_tex
        self.ceil_tex_name = ceil_tex

        # Lists of portals, indexed by wall/edge index
        self.portals = [[] for i in range(self.num_walls)]

        # List of neighbor rooms
        # Same length as list of portals
        self.neighbors = []

    def add_portal(
        self,
        edge,
        start_pos=None,
        end_pos=None,
        min_x=None,
        max_x=None,
        min_z=None,
        max_z=None,
        min_y=0,
        max_y=None,
    ):
        """Create a new portal/opening in a wall of this room"""

        if max_y is None:
            max_y = self.wall_height

        assert edge <= self.num_walls
        assert max_y > min_y

        # Get the edge points, compute the direction vector
        e_p0 = self.outline[edge]
        e_p1 = self.outline[(edge + 1) % self.num_walls]
        e_len = np.linalg.norm(e_p1 - e_p0)
        e_dir = (e_p1 - e_p0) / e_len
        x0, _, z0 = e_p0
        x1, _, z1 = e_p1
        dx, _, dz = e_dir

        # If the portal extents are specified by x coordinates
        if min_x is not None:
            assert min_z is None and max_z is None
            assert start_pos is None and end_pos is None
            assert x0 != x1

            m0 = (min_x - x0) / dx
            m1 = (max_x - x0) / dx

            if m1 < m0:
                m0, m1 = m1, m0

            start_pos, end_pos = m0, m1

        # If the portal extents are specified by z coordinates
        elif min_z is not None:
            assert min_x is None and max_x is None
            assert start_pos is None and end_pos is None
            assert z0 != z1

            m0 = (min_z - z0) / dz
            m1 = (max_z - z0) / dz

            if m1 < m0:
                m0, m1 = m1, m0

            start_pos, end_pos = m0, m1

        else:
            assert min_x is None and max_x is None
            assert min_z is None and max_z is None

        assert end_pos > start_pos
        assert start_pos >= 0, "portal outside of wall extents"
        assert end_pos <= e_len, "portal outside of wall extents"

        self.portals[edge].append(
            {"start_pos": start_pos, "end_pos": end_pos, "min_y": min_y, "max_y": max_y}
        )

        # Sort the portals by start position
        self.portals[edge].sort(key=lambda e: e["start_pos"])

        return start_pos, end_pos

    def point_inside(self, p):
        """Test if a point is inside the room"""

        # Vector from edge start to test point
        ap = p - self.outline

        # Compute the dot products of normals to AP vectors
        dotNAP = np.sum(self.edge_norms * ap, axis=1)

        # The point is inside if all the dot products are greater than zero
        return np.all(np.greater(dotNAP, 0))

    def _gen_static_data(self, params, rng):
        """Generate polygons and static data for this room

        Needed for rendering and collision detection
        Note: the wall polygons are quads, but the floor and
              ceiling can be arbitrary n-gons
        """
        self._load_textures(rng)
        self._generate_floor_geometry()
        self._generate_ceiling_geometry()
        self._generate_wall_geometry()
        self._finalize_wall_geometry()

    def _load_textures(self, rng):
        """Load and randomize room textures."""
        self.wall_tex = Texture.get(self.wall_tex_name, rng)
        self.floor_tex = Texture.get(self.floor_tex_name, rng)
        self.ceil_tex = Texture.get(self.ceil_tex_name, rng)

    def _generate_floor_geometry(self):
        """Generate floor vertices and texture coordinates."""
        self.floor_verts = self.outline
        self.floor_texcs = gen_texcs_floor(self.floor_tex, self.floor_verts)

    def _generate_ceiling_geometry(self):
        """Generate ceiling vertices and texture coordinates."""
        # Flip the ceiling vertex order because of backface culling
        self.ceil_verts = np.flip(self.outline, axis=0) + self.wall_height * Y_VEC
        self.ceil_texcs = gen_texcs_floor(self.ceil_tex, self.ceil_verts)

    def _generate_wall_geometry(self):
        """Generate wall vertices, normals, texture coordinates, and collision segments."""
        self.wall_verts = []
        self.wall_norms = []
        self.wall_texcs = []
        self.wall_segs = []

        def gen_seg_poly(edge_p0, side_vec, seg_start, seg_end, min_y, max_y):
            if seg_end == seg_start:
                return

            if min_y == max_y:
                return

            s_p0 = edge_p0 + seg_start * side_vec
            s_p1 = edge_p0 + seg_end * side_vec

            # If this polygon starts at ground level, add a collidable segment
            if min_y == 0:
                self.wall_segs.append(np.array([s_p1, s_p0]))

            # Generate the vertices
            # Vertices are listed in counter-clockwise order
            self.wall_verts.append(s_p0 + min_y * Y_VEC)
            self.wall_verts.append(s_p0 + max_y * Y_VEC)
            self.wall_verts.append(s_p1 + max_y * Y_VEC)
            self.wall_verts.append(s_p1 + min_y * Y_VEC)

            # Compute the normal for the polygon
            normal = np.cross(s_p1 - s_p0, Y_VEC)
            normal = -normal / np.linalg.norm(normal)
            for i in range(4):
                self.wall_norms.append(normal)

            # Generate the texture coordinates
            texcs = gen_texcs_wall(
                self.wall_tex, seg_start, min_y, seg_end - seg_start, max_y - min_y
            )
            self.wall_texcs.append(texcs)

        # For each wall
        for wall_idx in range(self.num_walls):
            edge_p0 = self.outline[wall_idx, :]
            edge_p1 = self.outline[(wall_idx + 1) % self.num_walls, :]
            wall_width = np.linalg.norm(edge_p1 - edge_p0)
            side_vec = (edge_p1 - edge_p0) / wall_width

            if len(self.portals[wall_idx]) > 0:
                seg_end = self.portals[wall_idx][0]["start_pos"]
            else:
                seg_end = wall_width

            # Generate the first polygon (going up to the first portal)
            gen_seg_poly(edge_p0, side_vec, 0, seg_end, 0, self.wall_height)

            # For each portal in this wall
            for portal_idx, portal in enumerate(self.portals[wall_idx]):
                portal = self.portals[wall_idx][portal_idx]
                start_pos = portal["start_pos"]
                end_pos = portal["end_pos"]
                min_y = portal["min_y"]
                max_y = portal["max_y"]

                # Generate the bottom polygon
                gen_seg_poly(edge_p0, side_vec, start_pos, end_pos, 0, min_y)

                # Generate the top polygon
                gen_seg_poly(
                    edge_p0, side_vec, start_pos, end_pos, max_y, self.wall_height
                )

                if portal_idx < len(self.portals[wall_idx]) - 1:
                    next_portal = self.portals[wall_idx][portal_idx + 1]
                    next_portal_start = next_portal["start_pos"]
                else:
                    next_portal_start = wall_width

                # Generate the polygon going up to the next portal
                gen_seg_poly(
                    edge_p0, side_vec, end_pos, next_portal_start, 0, self.wall_height
                )

    def _finalize_wall_geometry(self):
        """Convert wall geometry lists to numpy arrays."""
        self.wall_verts = np.array(self.wall_verts)
        self.wall_norms = np.array(self.wall_norms)

        if len(self.wall_segs) > 0:
            self.wall_segs = np.array(self.wall_segs)
        else:
            self.wall_segs = np.array([]).reshape(0, 2, 3)

        if len(self.wall_texcs) > 0:
            self.wall_texcs = np.concatenate(self.wall_texcs)
        else:
            self.wall_texcs = np.array([]).reshape(0, 2)

    def _render(self):
        """Render the static elements of the room"""

        glColor3f(1, 1, 1)

        # Draw the floor
        self.floor_tex.bind()
        glBegin(GL_POLYGON)
        glNormal3f(0, 1, 0)
        for i in range(self.floor_verts.shape[0]):
            glTexCoord2f(*self.floor_texcs[i, :])
            glVertex3f(*self.floor_verts[i, :])
        glEnd()

        # Draw the ceiling
        if not self.no_ceiling:
            self.ceil_tex.bind()
            glBegin(GL_POLYGON)
            glNormal3f(0, -1, 0)
            for i in range(self.ceil_verts.shape[0]):
                glTexCoord2f(*self.ceil_texcs[i, :])
                glVertex3f(*self.ceil_verts[i, :])
            glEnd()

        # Draw the walls
        self.wall_tex.bind()
        glBegin(GL_QUADS)
        for i in range(self.wall_verts.shape[0]):
            glNormal3f(*self.wall_norms[i, :])
            glTexCoord2f(*self.wall_texcs[i, :])
            glVertex3f(*self.wall_verts[i, :])
        glEnd()
