"""
Centralized rendering system for MiniWorld environments.

This module provides a comprehensive rendering architecture that separates
OpenGL state management from high-level rendering logic, providing better
maintainability and testability.
"""

from typing import Any, Optional

import numpy as np
from pyglet.gl import *
from pyglet.gl.glu import *

from ..observation_types import ObservationLevel
from .rendering.framebuffer import FrameBuffer


class OpenGLContextManager:
    """Manage OpenGL state and context switching."""

    def __init__(self):
        """Initialize OpenGL context manager."""
        self._saved_state = {}

    def save_state(self):
        """Save current OpenGL state."""
        self._saved_state = {
            "viewport": (GLint * 4)(),
            "projection_matrix": (GLfloat * 16)(),
            "modelview_matrix": (GLfloat * 16)(),
        }
        glGetIntegerv(GL_VIEWPORT, self._saved_state["viewport"])
        glGetFloatv(GL_PROJECTION_MATRIX, self._saved_state["projection_matrix"])
        glGetFloatv(GL_MODELVIEW_MATRIX, self._saved_state["modelview_matrix"])

    def restore_state(self):
        """Restore previously saved OpenGL state."""
        if self._saved_state:
            glViewport(*self._saved_state["viewport"])
            glMatrixMode(GL_PROJECTION)
            glLoadMatrixf(self._saved_state["projection_matrix"])
            glMatrixMode(GL_MODELVIEW)
            glLoadMatrixf(self._saved_state["modelview_matrix"])

    def rendering_context(self):
        """Context manager for safe rendering state management."""
        return RenderingContext(self)


class RenderingContext:
    """Context manager for OpenGL rendering state."""

    def __init__(self, context_manager: OpenGLContextManager):
        """Initialize rendering context with OpenGL context manager."""
        self.context_manager = context_manager

    def __enter__(self):
        """Enter rendering context and save OpenGL state."""
        self.context_manager.save_state()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit rendering context and restore OpenGL state."""
        self.context_manager.restore_state()


class FrameBufferManager:
    """Manage frame buffers and resolution handling."""

    def __init__(self, obs_width: int, obs_height: int):
        """Initialize framebuffer manager with default observation dimensions."""
        self.obs_width = obs_width
        self.obs_height = obs_height
        self.frame_buffers = {}

    def get_or_create_framebuffer(
        self, name: str, width: Optional[int] = None, height: Optional[int] = None
    ) -> FrameBuffer:
        """Get existing framebuffer or create new one."""
        width = width or self.obs_width
        height = height or self.obs_height
        key = (name, width, height)

        if key not in self.frame_buffers:
            self.frame_buffers[key] = FrameBuffer(width, height)

        return self.frame_buffers[key]

    def cleanup(self):
        """Clean up all frame buffers."""
        for fb in self.frame_buffers.values():
            if hasattr(fb, "cleanup"):
                fb.cleanup()
        self.frame_buffers.clear()


class CameraSystem:
    """Handle camera positioning and projection matrices."""

    def __init__(self):
        """Initialize camera system with configuration cache."""
        self.camera_configs = {}

    def get_config(self, obs_level: ObservationLevel, agent: Any) -> dict:
        """Get camera configuration for observation level."""
        if obs_level == ObservationLevel.FIRST_PERSON:
            return {
                "type": "perspective",
                "position": agent.pos + np.array([0, agent.cam_height, 0]),
                "direction": agent.dir_vec,
                "up": np.array([0, 1, 0]),
                "fov": agent.cam_fov_y,
            }
        elif obs_level in [
            ObservationLevel.TOP_DOWN_PARTIAL,
            ObservationLevel.TOP_DOWN_FULL,
        ]:
            return {
                "type": "orthographic",
                "position": agent.pos + np.array([0, 10, 0]),  # High above
                "direction": np.array([0, -1, 0]),  # Looking down
                "up": np.array([0, 0, -1]),  # Z-axis points up in top view
                "bounds": self._calculate_view_bounds(obs_level, agent),
            }
        else:
            raise ValueError(f"Unsupported observation level: {obs_level}")

    def _calculate_view_bounds(self, obs_level: ObservationLevel, agent: Any) -> dict:
        """Calculate view bounds for top-down rendering."""
        if obs_level == ObservationLevel.TOP_DOWN_PARTIAL:
            # POMDP view - limited around agent
            view_size = 8.0  # Configurable view size
            return {
                "left": agent.pos[0] - view_size,
                "right": agent.pos[0] + view_size,
                "bottom": agent.pos[2] - view_size,
                "top": agent.pos[2] + view_size,
            }
        else:
            # Full view - would need environment bounds
            return {"left": -20, "right": 20, "bottom": -20, "top": 20}

    def setup_camera(self, config: dict, frame_buffer: FrameBuffer):
        """Setup camera projection and view matrices."""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        if config["type"] == "perspective":
            aspect_ratio = frame_buffer.width / frame_buffer.height
            # Setup perspective projection
            gluPerspective(config["fov"], aspect_ratio, 0.04, 100.0)
        elif config["type"] == "orthographic":
            bounds = config["bounds"]
            glOrtho(
                bounds["left"],
                bounds["right"],
                bounds["bottom"],
                bounds["top"],
                0.01,
                100.0,
            )

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Setup view matrix
        pos = config["position"]
        direction = config["direction"]
        up = config["up"]
        target = pos + direction

        gluLookAt(
            pos[0], pos[1], pos[2], target[0], target[1], target[2], up[0], up[1], up[2]
        )


class RenderingEngine:
    """Centralized rendering system for MiniWorld environments."""

    def __init__(self, obs_width: int, obs_height: int):
        """Initialize rendering engine with all subsystems."""
        self.context_manager = OpenGLContextManager()
        self.framebuffer_manager = FrameBufferManager(obs_width, obs_height)
        self.camera_system = CameraSystem()

        self.obs_width = obs_width
        self.obs_height = obs_height

    def render_observation(
        self,
        obs_level: ObservationLevel,
        agent: Any,
        entities: list,
        rooms: list,
        frame_buffer: Optional[FrameBuffer] = None,
    ) -> np.ndarray:
        """Unified observation rendering."""
        if frame_buffer is None:
            frame_buffer = self.framebuffer_manager.get_or_create_framebuffer("obs")

        camera_config = self.camera_system.get_config(obs_level, agent)

        with self.context_manager.rendering_context():
            frame_buffer.bind()
            self.camera_system.setup_camera(camera_config, frame_buffer)
            self._setup_scene()
            self._render_entities_and_rooms(
                entities,
                rooms,
                agent,
                render_agent=(obs_level != ObservationLevel.FIRST_PERSON),
            )
            img = frame_buffer.resolve()

        return img

    def render_top_view(
        self,
        agent: Any,
        entities: list,
        rooms: list,
        POMDP: bool = False,
        render_agent: bool = True,
        frame_buffer: Optional[FrameBuffer] = None,
    ) -> np.ndarray:
        """Render top-down view of the environment."""
        if frame_buffer is None:
            frame_buffer = self.framebuffer_manager.get_or_create_framebuffer("topview")

        obs_level = (
            ObservationLevel.TOP_DOWN_PARTIAL
            if POMDP
            else ObservationLevel.TOP_DOWN_FULL
        )
        camera_config = self.camera_system.get_config(obs_level, agent)

        with self.context_manager.rendering_context():
            frame_buffer.bind()
            self.camera_system.setup_camera(camera_config, frame_buffer)
            self._setup_scene()
            self._render_entities_and_rooms(entities, rooms, agent, render_agent)
            img = frame_buffer.resolve()

        return img

    def _setup_scene(self):
        """Setup basic OpenGL scene state."""
        # Clear buffers
        glClearColor(0.8, 0.9, 1.0, 1.0)  # Light blue background
        glClearDepth(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        # Enable face culling
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)

        # Setup lighting (basic ambient light)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        light_pos = (GLfloat * 4)(10.0, 10.0, 10.0, 1.0)
        light_ambient = (GLfloat * 4)(0.2, 0.2, 0.2, 1.0)
        light_diffuse = (GLfloat * 4)(0.8, 0.8, 0.8, 1.0)

        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)

    def _render_entities_and_rooms(
        self, entities: list, rooms: list, agent: Any, render_agent: bool = True
    ):
        """Render all entities and rooms in the scene."""
        # Render rooms first (floors, walls, ceilings)
        for room in rooms:
            if hasattr(room, "_render"):
                room._render()

        # Render entities
        for entity in entities:
            if entity is agent and not render_agent:
                continue
            if hasattr(entity, "render"):
                entity.render()

    def cleanup(self):
        """Clean up rendering resources."""
        self.framebuffer_manager.cleanup()
