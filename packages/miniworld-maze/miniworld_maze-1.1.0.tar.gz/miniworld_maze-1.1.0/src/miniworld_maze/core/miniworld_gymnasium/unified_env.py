"""Unified MiniWorld environment class combining CustomEnv and BaseEnv functionality."""

import math
from ctypes import POINTER
from enum import IntEnum
from typing import List, Optional

import gymnasium as gym
import numpy as np
import pyglet
from gymnasium import spaces
from pyglet.gl import *

from ..observation_types import ObservationLevel
from .entities import *
from .math import *
from .objmesh import *
from .occlusion_queries import OcclusionQueryManager
from .opengl import *
from .params import DEFAULT_PARAMS
from .random import RandGen
from .room import Room

# Optional architectural improvements
try:
    from .entity_manager import EntityManager
    from .rendering_engine import RenderingEngine

    ARCHITECTURAL_IMPROVEMENTS_AVAILABLE = True
except ImportError:
    RenderingEngine = None
    EntityManager = None
    ARCHITECTURAL_IMPROVEMENTS_AVAILABLE = False
from ..constants import (
    CARRY_POSITION_OFFSET,
    DEFAULT_DISPLAY_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    EDGE_FACING_THRESHOLD,
    EDGE_TOUCHING_THRESHOLD,
    FAR_CLIPPING_PLANE,
    FONT_SIZE,
    INTERACTION_DISTANCE_MULTIPLIER,
    NEAR_CLIPPING_PLANE,
    OCCLUSION_QUERY_BOX_HEIGHT,
    OCCLUSION_QUERY_BOX_SIZE,
    ORTHOGRAPHIC_DEPTH_RANGE,
    PICKUP_RADIUS_MULTIPLIER,
    PICKUP_REACH_MULTIPLIER,
    PORTAL_CONNECTION_TOLERANCE,
    TEXT_LABEL_WIDTH,
    TEXT_MARGIN_X,
    TEXT_MARGIN_Y,
    TOPDOWN_FRAMEBUFFER_SCALE,
)


class UnifiedMiniWorldEnv(gym.Env):
    """
    Unified base class for MiniWorld environments combining CustomEnv and BaseEnv functionality.

    This class eliminates code duplication by providing a single implementation that supports
    both the enhanced features of CustomMiniWorldEnv and the legacy BaseEnv functionality.
    """

    metadata = {"render.modes": ["human", "rgb_array"], "video.frames_per_second": 30}

    # Enumeration of possible actions
    class Actions(IntEnum):
        # Turn left or right by a small amount
        turn_left = 0
        turn_right = 1

        # Move forward or back by a small amount
        move_forward = 2
        move_back = 3

        # Pick up or drop an object being carried
        pickup = 4
        drop = 5

        # Toggle/activate an object
        toggle = 6

        # Done completing task
        done = 7

    def __init__(
        self,
        obs_level=3,
        continuous=False,
        agent_mode="circle",
        max_episode_steps=1500,
        obs_width=80,
        obs_height=80,
        window_width=DEFAULT_WINDOW_WIDTH,
        window_height=DEFAULT_WINDOW_HEIGHT,
        params=DEFAULT_PARAMS,
        domain_rand=False,
        info_obs: Optional[List[ObservationLevel]] = None,
    ):
        """
        Initialize unified MiniWorld environment.

        Args:
            obs_level: Observation level (1=TOP_DOWN_PARTIAL, 2=TOP_DOWN_FULL, 3=FIRST_PERSON)
            continuous: Whether to use continuous actions
            agent_mode: Agent rendering mode ('triangle', 'circle', 'empty')
            max_episode_steps: Maximum steps per episode
            obs_width: Observation width in pixels
            obs_height: Observation height in pixels
            window_width: Window width for human rendering
            window_height: Window height for human rendering
            params: Environment parameters for domain randomization
            domain_rand: Whether to enable domain randomization
            info_obs: List of observation levels to include in info dictionary
        """
        # Store configuration
        self.obs_level = obs_level
        self.agent_mode = agent_mode
        self.continuous = continuous
        self.max_episode_steps = max_episode_steps
        self.params = params
        self.domain_rand = domain_rand
        self.info_obs = info_obs

        # Setup action space
        self._setup_action_space()

        # Setup observation space
        self._setup_observation_space(obs_width, obs_height)

        # Initialize OpenGL context and rendering
        self._initialize_opengl_context()

        # Setup rendering buffers
        self._setup_rendering_buffers(
            obs_width, obs_height, window_width, window_height
        )

        # Initialize UI components
        self._initialize_ui_components(
            window_width, window_height, obs_width, obs_height
        )

        # Initialize optional architectural improvements
        self._initialize_architectural_systems()

        # Finalize initialization
        self._finalize_initialization()

    def _setup_action_space(self):
        """Setup action space based on continuous/discrete mode."""
        if not self.continuous:
            # Action enumeration for this environment
            self.actions = UnifiedMiniWorldEnv.Actions

            # Actions are discrete integer values
            self.action_space = spaces.Discrete(len(self.actions))
        else:
            # Actions are continuous, speed and the difference of direction
            self.action_space = spaces.Box(low=-1, high=1, shape=(2,), dtype=np.float32)

    def _setup_observation_space(self, obs_width, obs_height):
        """Setup observation space."""
        # Observations are RGB images with pixels in [0, 255]
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(obs_height, obs_width, 3), dtype=np.uint8
        )

        self.reward_range = (-math.inf, math.inf)

    def _initialize_opengl_context(self):
        """Initialize OpenGL context and window."""
        # Window for displaying the environment to humans
        self.window = None

        # Invisible window to render into (shadow OpenGL context)
        self.shadow_window = pyglet.window.Window(width=1, height=1, visible=False)

        # Enable depth testing and backface culling
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def _setup_rendering_buffers(
        self, obs_width, obs_height, window_width, window_height
    ):
        """Setup frame buffers for rendering."""
        # Frame buffer used to render observations
        self.obs_fb = FrameBuffer(obs_width, obs_height, 8)

        # Frame buffer used for human visualization
        self.vis_fb = FrameBuffer(window_width, window_height, 16)

        # Top-down frame buffer (created later when needed)
        self.topdown_fb = None

    def _initialize_ui_components(
        self, window_width, window_height, obs_width, obs_height
    ):
        """Initialize UI components for human rendering."""
        # Compute the observation display size
        self.obs_disp_width = DEFAULT_DISPLAY_WIDTH
        self.obs_disp_height = obs_height * (self.obs_disp_width / obs_width)

        # For displaying text
        self.text_label = pyglet.text.Label(
            font_name="Arial",
            font_size=FONT_SIZE,
            multiline=True,
            width=TEXT_LABEL_WIDTH,
            x=window_width + TEXT_MARGIN_X,
            y=window_height - (self.obs_disp_height + TEXT_MARGIN_Y),
        )

    def _initialize_architectural_systems(self):
        """Initialize optional architectural improvements if available."""
        self.use_rendering_engine = False
        self.use_entity_manager = False

        if ARCHITECTURAL_IMPROVEMENTS_AVAILABLE:
            # Initialize RenderingEngine (optional)
            try:
                self.rendering_engine = RenderingEngine(self.obs_width, self.obs_height)
                self.use_rendering_engine = True
            except Exception:
                # For debugging: print(f"RenderingEngine init failed: {e}")
                self.rendering_engine = None
                self.use_rendering_engine = False

            # Initialize EntityManager (optional)
            try:
                self.entity_manager = EntityManager()
                self.use_entity_manager = True
            except Exception:
                self.entity_manager = None
                self.use_entity_manager = False
        else:
            self.rendering_engine = None
            self.entity_manager = None

    def _finalize_initialization(self):
        """Complete initialization process."""
        # Initialize the state
        self.seed()
        self.reset()

    def close(self):
        """Clean up resources."""
        pass

    def seed(self, seed=None):
        """Set random seed."""
        self.rand = RandGen(seed)
        return [seed]

    def reset(self, seed=None, options=None, pos=None):
        """
        Reset the simulation at the start of a new episode.

        This also randomizes many environment parameters (domain randomization).
        """
        # Handle seed for Gymnasium compatibility
        if seed is not None:
            self.seed(seed)

        # Step count since episode start
        self.step_count = 0

        # Create the agent
        self.agent = Agent(mode=self.agent_mode)

        # Set agent in EntityManager if available
        if self.use_entity_manager:
            self.entity_manager.set_agent(self.agent)

        # List of entities contained
        self.entities = []

        # Separate lists for performance optimization
        self.static_entities = []
        self.dynamic_entities = []

        # List of rooms in the world
        self.rooms = []

        # Wall segments for collision detection
        # Shape is (N, 2, 3)
        self.wall_segs = []

        # Generate the world
        self._generate_world_layout(pos)

        # Check if domain randomization is enabled or not
        rand = self.rand if self.domain_rand else None

        # Randomize elements of the world (domain randomization)
        randomization_params = ["light_pos", "light_color", "light_ambient"]

        # Add 'black' for custom environments, 'sky_color' for base environments
        if hasattr(self, "_is_custom_env") and self._is_custom_env:
            randomization_params.insert(0, "black")
        else:
            randomization_params.insert(0, "sky_color")

        self.params.sample_many(rand, self, randomization_params)

        # Get the max forward step distance
        self.max_forward_step = self.params.get_max("forward_step")

        # Randomize parameters of the entities
        for ent in self.entities:
            ent.randomize(self.params, rand)

        # Compute the min and max x, z extents of the whole floorplan
        self.min_x = min([r.min_x for r in self.rooms])
        self.max_x = max([r.max_x for r in self.rooms])
        self.min_z = min([r.min_z for r in self.rooms])
        self.max_z = max([r.max_z for r in self.rooms])

        # Create top-down frame buffer if needed
        if self.topdown_fb is None:
            width = TOPDOWN_FRAMEBUFFER_SCALE * (int(self.max_x - self.min_x) + 1)
            height = TOPDOWN_FRAMEBUFFER_SCALE * (int(self.max_z - self.min_z) + 1)
            self.topdown_fb = FrameBuffer(width, height, 8)

        # Generate static data
        if len(self.wall_segs) == 0:
            self._generate_collision_and_rendering_data()

        # Pre-compile static parts of the environment into a display list
        self._render_static()

        # Generate the first camera image
        obs = self._generate_observation()

        # Generate additional observations for info dictionary if specified
        info = {}
        if self.info_obs is not None:
            for obs_level in self.info_obs:
                # Temporarily change obs_level to generate the desired observation
                original_obs_level = self.obs_level
                self.obs_level = obs_level
                info_obs = self._generate_observation()
                self.obs_level = original_obs_level
                # Use the observation level name as key
                info[str(obs_level)] = info_obs

        # Return first observation with info dict for Gymnasium compatibility
        return obs, info

    def _generate_observation(self, render_agent: bool = None):
        """Generate observation based on current observation level.

        Args:
            render_agent: Whether to render the agent in the observation.
                         If None, uses default behavior based on observation level.
        """
        # Import ObservationLevel here to avoid circular imports
        from ..observation_types import ObservationLevel

        if self.obs_level == ObservationLevel.TOP_DOWN_PARTIAL:
            if self.agent_mode == "empty":
                # Agent mode 'empty' always renders without agent
                render_ag = False
            elif render_agent is not None:
                # Use explicit render_agent parameter
                render_ag = render_agent
            else:
                # Default behavior: render agent
                render_ag = True
            return self.render_top_view(POMDP=True, render_ag=render_ag)

        elif self.obs_level == ObservationLevel.TOP_DOWN_FULL:
            # Use explicit render_agent parameter or default to True
            render_ag = render_agent if render_agent is not None else True
            return self.render_top_view(POMDP=False, render_ag=render_ag)

        elif self.obs_level == ObservationLevel.FIRST_PERSON:
            # First person view doesn't include the agent anyway
            return self.render_obs()

        else:
            valid_levels = list(ObservationLevel)
            raise ValueError(
                f"Invalid obs_level {self.obs_level}. Must be one of {valid_levels}"
            )

    def _calculate_carried_object_position(self, agent_pos, ent):
        """Compute the position at which to place an object being carried."""
        dist = self.agent.radius + ent.radius + self.max_forward_step
        pos = agent_pos + self.agent.dir_vec * CARRY_POSITION_OFFSET * dist

        # Adjust the Y-position so the object is visible while being carried
        y_pos = max(self.agent.cam_height - ent.height - 0.3, 0)
        pos = pos + Y_VEC * y_pos

        return pos

    def move_agent(self, fwd_dist, fwd_drift):
        """Move the agent forward."""
        next_pos = (
            self.agent.pos
            + self.agent.dir_vec * fwd_dist
            + self.agent.right_vec * fwd_drift
        )

        if self.intersect(self.agent, next_pos, self.agent.radius):
            return False

        carrying = self.agent.carrying
        if carrying:
            next_carrying_pos = self._calculate_carried_object_position(
                next_pos, carrying
            )

            if self.intersect(carrying, next_carrying_pos, carrying.radius):
                return False

            carrying.pos = next_carrying_pos

        self.agent.pos = next_pos
        return True

    def turn_agent(self, turn_angle):
        """Turn the agent left or right."""
        turn_angle *= math.pi / 180
        orig_dir = self.agent.dir

        self.agent.dir += turn_angle

        if self.intersect(self.agent, self.agent.pos, self.agent.radius):
            self.agent.dir -= turn_angle
            return False

        carrying = self.agent.carrying
        if carrying:
            pos = self._calculate_carried_object_position(self.agent.pos, carrying)

            if self.intersect(carrying, pos, carrying.radius):
                self.agent.dir = orig_dir
                return False

            carrying.pos = pos
            carrying.dir = self.agent.dir

        return True

    def turn_and_move_agent(self, fwd_dist, turn_angle):
        """
        Simultaneously turn and move the agent in a single action.

        This method is optimized for continuous control where the agent
        needs to change direction while moving forward.

        Args:
            fwd_dist: Forward movement distance in environment units
            turn_angle: Turn angle in degrees (positive = clockwise)

        Returns:
            bool: True if movement was successful, False if blocked by collision

        Note:
            This method modifies agent.pos and agent.dir directly.
            Original direction is restored on collision.
        """
        orig_dir = self.agent.dir
        self.agent.dir += turn_angle * (math.pi / 180)

        next_pos = self.agent.pos + self.agent.dir_vec * fwd_dist

        if self.intersect(self.agent, next_pos, self.agent.radius):
            self.agent.dir = orig_dir
            return False
        else:
            self.agent.pos = next_pos
            return True

    def pos_agent(self, fwd_dist, angle):
        """
        Position the agent at a specific distance and angle.

        This method sets the agent's direction to the specified angle
        and moves forward by the specified distance.

        Args:
            fwd_dist: Forward movement distance in environment units
            angle: Absolute angle in degrees (0 = facing positive Z)

        Returns:
            bool: True if positioning was successful, False if blocked
        """
        self.agent.dir = angle * (math.pi / 180)
        next_pos = self.agent.pos + self.agent.dir_vec * fwd_dist

        if self.intersect(self.agent, next_pos, self.agent.radius):
            return False
        else:
            self.agent.pos = next_pos
            return True

    def step(self, action):
        """Perform one action and update the simulation."""
        self.step_count += 1

        # Process the action based on environment mode
        self._process_action(action)

        # Generate observation
        observation = self._generate_observation()

        # Calculate step results
        reward, terminated, info = self._calculate_step_results(observation)

        return observation, reward, terminated, False, info

    def _process_action(self, action):
        """Process action based on continuous/discrete mode."""
        if self.continuous:
            self._handle_continuous_action(action)
        else:
            self._handle_discrete_action(action)

    def _handle_continuous_action(self, action):
        """Handle continuous action processing."""
        if self.agent.mode == "circle":
            self.pos_agent(action[0], 180 * action[1])
        else:
            self.turn_and_move_agent(action[0], 15 * action[1])

    def _handle_discrete_action(self, action):
        """Handle discrete action processing."""
        rand = self.rand if self.domain_rand else None
        fwd_step = self.params.sample(rand, "forward_step")
        fwd_drift = self.params.sample(rand, "forward_drift")
        turn_step = self.params.sample(rand, "turn_step")

        if action == self.actions.move_forward:
            self.move_agent(fwd_step, fwd_drift)

        elif action == self.actions.move_back:
            self.move_agent(-fwd_step, fwd_drift)

        elif action == self.actions.turn_left:
            self.turn_agent(turn_step)

        elif action == self.actions.turn_right:
            self.turn_agent(-turn_step)

        # Pick up an object
        elif action == self.actions.pickup:
            test_pos = (
                self.agent.pos
                + self.agent.dir_vec * PICKUP_REACH_MULTIPLIER * self.agent.radius
            )
            ent = self.intersect(
                self.agent, test_pos, PICKUP_RADIUS_MULTIPLIER * self.agent.radius
            )
            if not self.agent.carrying:
                if isinstance(ent, Entity):
                    if not ent.is_static:
                        self.agent.carrying = ent

        # Drop an object being carried
        elif action == self.actions.drop:
            if self.agent.carrying:
                self.agent.carrying.pos[1] = 0
                self.agent.carrying = None

        # Update carried object position
        if self.agent.carrying:
            ent_pos = self._calculate_carried_object_position(
                self.agent.pos, self.agent.carrying
            )
            self.agent.carrying.pos = ent_pos
            self.agent.carrying.dir = self.agent.dir

    def _calculate_step_results(self, observation):
        """Calculate reward, termination, and info for step."""
        # Generate topdown view for info if needed
        topdown = None
        if self.obs_level != 2:  # Not TOP_DOWN_FULL
            topdown = self.render_top_view(POMDP=False, frame_buffer=self.topdown_fb)

        # Generate additional observations for info dictionary if specified
        info = {}
        if self.info_obs is not None:
            for obs_level in self.info_obs:
                # Temporarily change obs_level to generate the desired observation
                original_obs_level = self.obs_level
                self.obs_level = obs_level
                info_obs = self._generate_observation()
                self.obs_level = original_obs_level
                # Use the observation level name as key
                info[str(obs_level)] = info_obs

        # Check termination
        if self.step_count >= self.max_episode_steps:
            terminated = True
            reward = 0
            info.update(
                {
                    "pos": self.agent.pos,
                    "mdp_view": topdown if topdown is not None else observation,
                }
            )
        else:
            reward = 0
            terminated = False
            info.update(
                {
                    "pos": self.agent.pos,
                    "mdp_view": topdown if topdown is not None else observation,
                }
            )

        return reward, terminated, info

    def add_rect_room(self, min_x, max_x, min_z, max_z, **kwargs):
        """Create a rectangular room."""
        # 2D outline coordinates of the room,
        # listed in counter-clockwise order when viewed from the top
        outline = np.array(
            [
                # East wall
                [max_x, max_z],
                # North wall
                [max_x, min_z],
                # West wall
                [min_x, min_z],
                # South wall
                [min_x, max_z],
            ]
        )

        return self.add_room(outline=outline, **kwargs)

    def add_room(self, **kwargs):
        """Create a new room."""
        if len(self.wall_segs) != 0:
            raise RuntimeError("Cannot add rooms after static data is generated")

        room = Room(**kwargs)
        self.rooms.append(room)

        return room

    def connect_rooms(
        self, room_a, room_b, min_x=None, max_x=None, min_z=None, max_z=None, max_y=None
    ):
        """Connect two rooms along facing edges."""
        edge_pair = self._find_facing_edges(room_a, room_b)
        portal_coords = self._calculate_portal_coordinates(
            room_a, room_b, edge_pair, min_x, max_x, min_z, max_z, max_y
        )

        if self._portals_directly_connected(portal_coords):
            return

        connecting_room = self._create_connecting_room(portal_coords, room_a, max_y)
        self._add_portals_to_connecting_room(connecting_room, portal_coords)

    def _find_facing_edges(self, room_a, room_b):
        """Extract the complex edge-finding logic."""
        for idx_a in range(room_a.num_walls):
            norm_a = room_a.edge_norms[idx_a]

            for idx_b in range(room_b.num_walls):
                norm_b = room_b.edge_norms[idx_b]

                # Reject edges that are not facing each other
                if np.dot(norm_a, norm_b) > EDGE_FACING_THRESHOLD:
                    continue

                dir = room_b.outline[idx_b] - room_a.outline[idx_a]

                # Reject edges that are not touching
                if np.dot(norm_a, dir) > EDGE_TOUCHING_THRESHOLD:
                    continue

                return idx_a, idx_b

        return None, None

    def _calculate_portal_coordinates(
        self, room_a, room_b, edge_pair, min_x, max_x, min_z, max_z, max_y
    ):
        """Extract portal coordinate calculations."""
        idx_a, idx_b = edge_pair

        if idx_a is None:
            raise ValueError(f"No matching edges found between {room_a} and {room_b}")

        start_a, end_a = room_a.add_portal(
            edge=idx_a, min_x=min_x, max_x=max_x, min_z=min_z, max_z=max_z, max_y=max_y
        )

        start_b, end_b = room_b.add_portal(
            edge=idx_b, min_x=min_x, max_x=max_x, min_z=min_z, max_z=max_z, max_y=max_y
        )

        a = room_a.outline[idx_a] + room_a.edge_dirs[idx_a] * start_a
        b = room_a.outline[idx_a] + room_a.edge_dirs[idx_a] * end_a
        c = room_b.outline[idx_b] + room_b.edge_dirs[idx_b] * start_b
        d = room_b.outline[idx_b] + room_b.edge_dirs[idx_b] * end_b

        return {
            "a": a,
            "b": b,
            "c": c,
            "d": d,
            "len_a": np.linalg.norm(b - a),
            "len_b": np.linalg.norm(d - c),
        }

    def _portals_directly_connected(self, portal_coords):
        """Check if portals are directly connected."""
        return (
            np.linalg.norm(portal_coords["a"] - portal_coords["d"])
            < PORTAL_CONNECTION_TOLERANCE
        )

    def _create_connecting_room(self, portal_coords, room_a, max_y):
        """Create connecting room between portals."""
        # Room outline points must be specified in counter-clockwise order
        outline = np.stack(
            [
                portal_coords["c"],
                portal_coords["b"],
                portal_coords["a"],
                portal_coords["d"],
            ]
        )
        outline = np.stack([outline[:, 0], outline[:, 2]], axis=1)

        max_y = max_y if max_y is not None else room_a.wall_height

        room = Room(
            outline,
            wall_height=max_y,
            wall_tex=room_a.wall_tex_name,
            floor_tex=room_a.floor_tex_name,
            ceil_tex=room_a.ceil_tex_name,
            no_ceiling=room_a.no_ceiling,
        )

        self.rooms.append(room)
        return room

    def _add_portals_to_connecting_room(self, connecting_room, portal_coords):
        """Add portals to the connecting room."""
        connecting_room.add_portal(1, start_pos=0, end_pos=portal_coords["len_a"])
        connecting_room.add_portal(3, start_pos=0, end_pos=portal_coords["len_b"])

    def place_entity(
        self,
        ent,
        room=None,
        pos=None,
        dir=None,
        min_x=None,
        max_x=None,
        min_z=None,
        max_z=None,
    ):
        """
        Place an entity/object in the world.
        Find a position that doesn't intersect with any other object.
        """
        if len(self.rooms) == 0:
            raise ValueError("Must create rooms before calling place_entity")
        if ent.radius is None:
            raise ValueError("Entity must have physical size (radius) defined")

        # Generate collision detection data
        if len(self.wall_segs) == 0:
            self._generate_collision_and_rendering_data()

        # If an exact position is specified
        if pos is not None:
            ent.dir = dir if dir is not None else self.rand.float(-math.pi, math.pi)
            ent.pos = pos
            self.entities.append(ent)

            # Add to EntityManager if available
            if self.use_entity_manager:
                self.entity_manager.add_entity(ent, pos)

            # Add to appropriate performance list
            if ent.is_static:
                self.static_entities.append(ent)
            else:
                self.dynamic_entities.append(ent)

            return ent

        # Keep retrying until we find a suitable position
        while True:
            # Pick a room, sample rooms proportionally to floor surface area
            selected_room = (
                room if room else self.rand.choice(self.rooms, probs=self.room_probs)
            )

            # Choose a random point within the square bounding box of the room
            low_x = selected_room.min_x if min_x is None else min_x
            high_x = selected_room.max_x if max_x is None else max_x
            low_z = selected_room.min_z if min_z is None else min_z
            high_z = selected_room.max_z if max_z is None else max_z

            pos = self.rand.float(
                low=[low_x + ent.radius, 0, low_z + ent.radius],
                high=[high_x - ent.radius, 0, high_z - ent.radius],
            )

            # Make sure the position is within the room's outline
            if not selected_room.point_inside(pos):
                continue

            # Pick a direction
            direction = dir if dir is not None else self.rand.float(-math.pi, math.pi)

            ent.pos = pos
            ent.dir = direction

            # Make sure the position doesn't intersect with any walls
            if self.intersect(ent, pos, ent.radius):
                continue

            break

        self.entities.append(ent)

        # Add to EntityManager if available
        if self.use_entity_manager:
            self.entity_manager.add_entity(ent, ent.pos)

        # Add to appropriate performance list
        if ent.is_static:
            self.static_entities.append(ent)
        else:
            self.dynamic_entities.append(ent)

        return ent

    def place_agent(
        self,
        room=None,
        pos=None,
        dir=None,
        min_x=None,
        max_x=None,
        min_z=None,
        max_z=None,
    ):
        """
        Place the agent in the environment at a random position and orientation.
        """
        return self.place_entity(
            self.agent,
            room=room,
            pos=pos,
            dir=dir,
            min_x=min_x,
            max_x=max_x,
            min_z=min_z,
            max_z=max_z,
        )

    def intersect(self, ent, pos, radius):
        """Check if an entity intersects with the world."""
        # Ignore the Y position
        entity_x, _, entity_z = pos
        pos = np.array([entity_x, 0, entity_z])

        # Check for intersection with walls
        if intersect_circle_segs(pos, radius, self.wall_segs):
            return True

        # Check for entity intersection
        for other_entity in self.entities:
            # Entities can't intersect with themselves
            if other_entity is ent:
                continue

            other_x, _, other_z = other_entity.pos
            other_pos = np.array([other_x, 0, other_z])

            distance = 0
            if ent.trable or other_entity.trable:
                distance = 10000000
            else:
                distance = np.linalg.norm(other_pos - pos)

            if distance < radius + other_entity.radius:
                return other_entity

        return None

    def is_within_interaction_distance(self, ent0, ent1=None):
        """
        Test if two entities are within interaction distance.
        Used for "go to" or "put next" type tasks.
        """
        if ent1 is None:
            ent1 = self.agent

        distance = np.linalg.norm(ent0.pos - ent1.pos)
        threshold = (
            ent0.radius
            + ent1.radius
            + INTERACTION_DISTANCE_MULTIPLIER * self.max_forward_step
        )
        return distance < threshold

    def _load_tex(self, tex_name):
        """Load a texture, with or without domain randomization."""
        rand = self.rand if self.params.sample(self.rand, "tex_rand") else None
        return Texture.get(tex_name, rand)

    def _generate_collision_and_rendering_data(self):
        """Generate static data needed for rendering and collision detection."""
        # Generate the static data for each room
        for room in self.rooms:
            room._gen_static_data(self.params, self.rand if self.domain_rand else None)

        # Concatenate the wall segments
        self.wall_segs = np.concatenate([r.wall_segs for r in self.rooms])

        # Room selection probabilities
        self.room_probs = np.array([r.area for r in self.rooms], dtype=float)
        self.room_probs /= np.sum(self.room_probs)

    def _generate_world_layout(self, pos=None):
        """Generate the world layout. Derived classes must implement this method."""
        raise NotImplementedError

    def _reward(self):
        """Default sparse reward computation."""
        return 1.0 - 0.2 * (self.step_count / self.max_episode_steps)

    def _render_static(self):
        """
        Render the static elements of the scene into a display list.
        Called once at the beginning of each episode.
        """
        # Manage OpenGL display list for static rendering
        # Note: Could be improved with automatic display list management
        glDeleteLists(1, 1)
        glNewList(1, GL_COMPILE)

        # Light position
        glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat * 4)(*self.light_pos + [1]))

        # Background/minimum light level
        glLightfv(GL_LIGHT0, GL_AMBIENT, (GLfloat * 4)(*self.light_ambient))

        # Diffuse light color
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (GLfloat * 4)(*self.light_color))

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        glShadeModel(GL_SMOOTH)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Render the rooms
        glEnable(GL_TEXTURE_2D)
        for room in self.rooms:
            room._render()

        # Render the static entities (performance optimization)
        for ent in self.static_entities:
            ent.render()

        glEndList()

    def _render_world(self, frame_buffer, render_agent, view_bounds=None):
        """
        Render the world from a given camera position into a frame buffer,
        and produce a numpy image array as output.
        """
        # Call the display list for the static parts of the environment
        glCallList(1)

        # Render dynamic entities only (performance optimization)
        for ent in self.dynamic_entities:
            if ent is not self.agent:
                # Frustum culling for POMDP mode (skip entities outside view bounds)
                if view_bounds is not None:
                    min_x, max_x, min_z, max_z = view_bounds
                    if (
                        ent.pos[0] < min_x - ent.radius
                        or ent.pos[0] > max_x + ent.radius
                        or ent.pos[2] < min_z - ent.radius
                        or ent.pos[2] > max_z + ent.radius
                    ):
                        continue

                ent.render()

        if render_agent:
            self.agent.render()

        # Resolve the rendered image into a numpy array
        img = frame_buffer.resolve()
        return img

    def render_top_view(self, frame_buffer=None, POMDP=False, render_ag=True):
        """Render a top view of the whole map (from above)."""
        if not isinstance(POMDP, bool):
            raise TypeError(f"POMDP parameter must be boolean, got {type(POMDP)}")

        frame_buffer = frame_buffer or self.obs_fb

        self._prepare_top_view_rendering(frame_buffer)
        scene_extents = self._calculate_scene_extents(POMDP)
        self._setup_top_view_camera(scene_extents, frame_buffer)

        return self._render_world(
            frame_buffer,
            render_agent=render_ag,
            view_bounds=scene_extents if POMDP else None,
        )

    def _prepare_top_view_rendering(self, frame_buffer):
        """Prepare top view rendering setup."""

        # Switch to the default OpenGL context
        # This is necessary on Linux Nvidia drivers
        self.shadow_window.switch_to()

        # Bind the frame buffer before rendering into it
        frame_buffer.bind()

        # Clear the color and depth buffers
        background_color = self.black if hasattr(self, "black") else self.sky_color
        glClearColor(*background_color, 1.0)
        glClearDepth(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def _calculate_scene_extents(self, POMDP):
        """Calculate scene extents for rendering."""
        if POMDP:
            # Import constants for POMDP view radius
            from ..constants import POMDP_VIEW_RADIUS

            agent_x, _, agent_z = self.agent.pos
            min_x = agent_x - POMDP_VIEW_RADIUS
            max_x = agent_x + POMDP_VIEW_RADIUS
            min_z = agent_z - POMDP_VIEW_RADIUS
            max_z = agent_z + POMDP_VIEW_RADIUS
        else:
            min_x = self.min_x - 1
            max_x = self.max_x + 1
            min_z = self.min_z - 1
            max_z = self.max_z + 1

        return (min_x, max_x, min_z, max_z)

    def _setup_top_view_camera(self, scene_extents, frame_buffer):
        """Setup camera for top view rendering."""
        min_x, max_x, min_z, max_z = scene_extents

        width = max_x - min_x
        height = max_z - min_z
        aspect = width / height
        framebuffer_aspect_ratio = frame_buffer.width / frame_buffer.height

        # Adjust the aspect extents to match the frame buffer aspect
        if aspect > framebuffer_aspect_ratio:
            # Want to add to denom, add to height
            new_h = width / framebuffer_aspect_ratio
            h_diff = new_h - height
            min_z -= h_diff / 2
            max_z += h_diff / 2
        elif aspect < framebuffer_aspect_ratio:
            # Want to add to num, add to width
            new_w = height * framebuffer_aspect_ratio
            w_diff = new_w - width
            min_x -= w_diff / 2
            max_x += w_diff / 2

        # Set the projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(
            min_x,
            max_x,
            -max_z,
            -min_z,
            -ORTHOGRAPHIC_DEPTH_RANGE,
            ORTHOGRAPHIC_DEPTH_RANGE,
        )

        # Setup the camera
        # Y maps to +Z, Z maps to +Y
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        m = [
            1,
            0,
            0,
            0,
            0,
            0,
            1,
            0,
            0,
            -1,
            0,
            0,
            0,
            0,
            0,
            1,
        ]
        glLoadMatrixf((GLfloat * len(m))(*m))

        return (min_x, max_x, min_z, max_z)

    def render_obs(self, frame_buffer=None):
        """Render an observation from the point of view of the agent."""
        if frame_buffer is None:
            frame_buffer = self.obs_fb

        # Switch to the default OpenGL context
        # This is necessary on Linux Nvidia drivers
        self.shadow_window.switch_to()

        # Bind the frame buffer before rendering into it
        frame_buffer.bind()

        # Clear the color and depth buffers
        background_color = self.black if hasattr(self, "black") else self.sky_color
        glClearColor(*background_color, 1.0)
        glClearDepth(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set the projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(
            self.agent.cam_fov_y,
            frame_buffer.width / float(frame_buffer.height),
            NEAR_CLIPPING_PLANE,
            FAR_CLIPPING_PLANE,
        )

        # Setup the camera
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(
            # Eye position
            *self.agent.cam_pos,
            # Target
            *(self.agent.cam_pos + self.agent.cam_dir),
            # Up vector
            0,
            1.0,
            0.0,
        )

        return self._render_world(frame_buffer, render_agent=False)

    def render_depth(self, frame_buffer=None):
        """
        Produce a depth map.
        Values are floating-point, map shape is (H,W,1)
        Distances are in meters from the observer.
        """
        if frame_buffer is None:
            frame_buffer = self.obs_fb

        # Render the world
        self.render_obs(frame_buffer)

        return frame_buffer.get_depth_map(NEAR_CLIPPING_PLANE, FAR_CLIPPING_PLANE)

    def get_visible_ents(self):
        """
        Get entities visible to agent using occlusion queries.

        Returns:
            set: Set of Entity objects that are visible to the agent
        """
        with OcclusionQueryManager(self.entities) as query_manager:
            self._setup_visibility_rendering()
            return self._perform_occlusion_queries(query_manager)

    def _setup_visibility_rendering(self):
        """Setup rendering for visibility queries."""
        # Switch to the default OpenGL context
        self.shadow_window.switch_to()

        # Use the small observation frame buffer
        frame_buffer = self.obs_fb
        frame_buffer.bind()

        # Clear the color and depth buffers
        background_color = self.black if hasattr(self, "black") else self.sky_color
        glClearColor(*background_color, 1.0)
        glClearDepth(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set the projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(
            self.agent.cam_fov_y,
            frame_buffer.width / float(frame_buffer.height),
            NEAR_CLIPPING_PLANE,
            FAR_CLIPPING_PLANE,
        )

        # Setup the camera
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(
            # Eye position
            *self.agent.cam_pos,
            # Target
            *(self.agent.cam_pos + self.agent.cam_dir),
            # Up vector
            0,
            1.0,
            0.0,
        )

        # Render the rooms, without texturing
        glDisable(GL_TEXTURE_2D)
        for room in self.rooms:
            room._render()

    def _perform_occlusion_queries(self, query_manager: OcclusionQueryManager):
        """
        Perform occlusion queries on all entities.

        Args:
            query_manager: Initialized occlusion query manager

        Returns:
            set: Set of visible entities
        """
        # Render occlusion query boxes for each entity
        for entity_index, entity in enumerate(self.entities):
            if entity is self.agent:
                continue

            query_manager.begin_query(entity_index)

            # Draw a small box at the entity's position for occlusion testing
            pos = entity.pos
            drawBox(
                x_min=pos[0] - OCCLUSION_QUERY_BOX_SIZE,
                x_max=pos[0] + OCCLUSION_QUERY_BOX_SIZE,
                y_min=pos[1],
                y_max=pos[1] + OCCLUSION_QUERY_BOX_HEIGHT,
                z_min=pos[2] - OCCLUSION_QUERY_BOX_SIZE,
                z_max=pos[2] + OCCLUSION_QUERY_BOX_SIZE,
            )

            query_manager.end_query()

        # Get results using the query manager
        return query_manager.get_visible_entities(self.agent)

    def render(self, mode="human", close=False, view="agent"):
        """Render the environment for human viewing."""
        if close:
            return self._close_rendering()

        rendered_image = self._render_scene(view)

        if mode == "rgb_array":
            return rendered_image

        return self._display_human_view(rendered_image, mode)

    def _close_rendering(self):
        """Handle rendering cleanup."""
        if self.window:
            self.window.close()

    def _render_scene(self, view):
        """Handle core scene rendering logic."""
        # Render the human-view image
        if view not in ["agent", "top"]:
            raise ValueError(f"Invalid view '{view}'. Must be 'agent' or 'top'")
        if view == "agent":
            img = self.render_obs(self.vis_fb)
        else:
            # Import ObservationLevel here to avoid circular imports
            from ..observation_types import ObservationLevel

            if self.obs_level == ObservationLevel.TOP_DOWN_PARTIAL:
                img = self.render_top_view(self.vis_fb, POMDP=True)
            else:
                img = self.render_top_view(self.vis_fb, POMDP=False)

        return img

    def _display_human_view(self, img, mode):
        """Handle human visualization display."""
        img_width = img.shape[1]
        img_height = img.shape[0]

        # Render the agent's view
        obs = self.render_obs()
        obs_width = obs.shape[1]
        obs_height = obs.shape[0]

        window_width = img_width + self.obs_disp_width
        window_height = img_height

        if self.window is None:
            config = pyglet.gl.Config(double_buffer=True)
            self.window = pyglet.window.Window(
                width=window_width, height=window_height, resizable=False, config=config
            )

        self.window.clear()
        self.window.switch_to()

        # Bind the default frame buffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # Clear the color and depth buffers
        glClearColor(0, 0, 0, 1.0)
        glClearDepth(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Setup orthogonal projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glOrtho(0, window_width, 0, window_height, 0, 10)

        # Draw the human render to the rendering window
        img_flip = np.ascontiguousarray(np.flip(img, axis=0))
        img_data = pyglet.image.ImageData(
            img_width,
            img_height,
            "RGB",
            img_flip.ctypes.data_as(POINTER(GLubyte)),
            pitch=img_width * 3,
        )
        img_data.blit(0, 0, 0, width=img_width, height=img_height)

        # Draw the observation
        obs = np.ascontiguousarray(np.flip(obs, axis=0))
        obs_data = pyglet.image.ImageData(
            obs_width,
            obs_height,
            "RGB",
            obs.ctypes.data_as(POINTER(GLubyte)),
            pitch=obs_width * 3,
        )
        obs_data.blit(
            img_width,
            img_height - self.obs_disp_height,
            0,
            width=self.obs_disp_width,
            height=self.obs_disp_height,
        )

        # Draw the text label in the window
        self.text_label.text = "pos: (%.2f, %.2f, %.2f)\nangle: %d\nsteps: %d" % (
            *self.agent.pos,
            int(self.agent.dir * 180 / math.pi) % 360,
            self.step_count,
        )
        self.text_label.draw()

        # Force execution of queued commands
        glFlush()

        # If we are not running the Pyglet event loop,
        # we have to manually flip the buffers and dispatch events
        if mode == "human":
            self.window.flip()
            self.window.dispatch_events()

        return img
