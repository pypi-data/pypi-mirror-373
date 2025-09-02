"""Base Grid Rooms environment implementation."""

from typing import List, Optional, Tuple, Union

import cv2
import numpy as np
from gymnasium import spaces

from ..core import COLORS, Box, ObservationLevel
from ..core.constants import (
    AGENT_START_POSITION,
    BOX_GRID_SIZE,
    BOX_OFFSET_FRACTION,
    BOX_SIZE_FRACTION,
    BOXES_PER_ROOM,
    DEFAULT_DOOR_SIZE,
    DEFAULT_OBS_HEIGHT,
    DEFAULT_OBS_WIDTH,
    DEFAULT_ROOM_SIZE,
    MAX_EPISODE_STEPS,
    ROOM_BOUNDARY_MARGIN,
    ROOM_CENTER_FRACTION,
)
from ..core.miniworld_gymnasium.unified_env import UnifiedMiniWorldEnv


class GridRoomsEnvironment(UnifiedMiniWorldEnv):
    """
    Base class for grid-based room environments.

    Supports different grid sizes and connection patterns.
    Subclasses pass their specific configurations directly to __init__.
    """

    def __init__(
        self,
        grid_size: int,
        connections: List[Tuple[int, int]],
        textures: List[str],
        goal_positions: List[List[List[float]]],
        placed_room: Optional[int] = None,
        obs_level: ObservationLevel = ObservationLevel.TOP_DOWN_PARTIAL,
        continuous: bool = False,
        room_size: Union[int, float] = DEFAULT_ROOM_SIZE,
        door_size: Union[int, float] = DEFAULT_DOOR_SIZE,
        agent_mode: Optional[str] = None,
        obs_width: int = DEFAULT_OBS_WIDTH,
        obs_height: int = DEFAULT_OBS_HEIGHT,
        **kwargs,
    ):
        """
        Initialize a grid-based room environment.

        Args:
            grid_size: Size of the grid (e.g., 3 for 3x3 grid)
            connections: List of (room1, room2) tuples for connections
            textures: List of texture names for each room
            goal_positions: List of goal positions for each room
            placed_room: Initial room index (defaults to 0)
            obs_level: Observation level (defaults to 1)
            continuous: Whether to use continuous actions (defaults to False)
            room_size: Size of each room in environment units (defaults to 5)
            door_size: Size of doors between rooms (defaults to 2)
            agent_mode: Agent rendering mode ('triangle', 'circle', 'empty')
            obs_width: Observation width in pixels (defaults to DEFAULT_OBS_WIDTH)
            obs_height: Observation height in pixels (defaults to DEFAULT_OBS_HEIGHT)
            **kwargs: Additional arguments passed to parent class
        """

        # Set grid configuration
        self.grid_size = grid_size
        self.total_rooms = self.grid_size * self.grid_size

        # Validate and set connections
        assert len(connections) > 0, "Connection between rooms should be more than 1"
        self.connections = connections

        # Validate and set textures
        assert len(textures) == self.total_rooms, (
            f"Textures for floor should be same as the number of the rooms ({self.total_rooms})"
        )
        self.textures = textures

        # Set goal positions
        self.goal_positions = goal_positions

        # Set placed room
        if placed_room is None:
            self.placed_room = 0  # Start in the first room
        else:
            assert 0 <= placed_room < self.total_rooms, (
                f"placing point should be in 0~{self.total_rooms - 1}"
            )
            self.placed_room = placed_room

        # Set agent mode
        if agent_mode is None:
            self.agent_mode = "empty"
        else:
            assert agent_mode in ["triangle", "circle", "empty"], (
                "configuration cannot be done"
            )
            self.agent_mode = agent_mode

        self.room_size = room_size
        self.door_size = door_size

        # Mark this as a custom environment for background color handling
        self._is_custom_env = True

        # Store observation dimensions for rendering (needed before super().__init__)
        self.obs_width = obs_width
        self.obs_height = obs_height

        super().__init__(
            obs_level=obs_level,
            max_episode_steps=MAX_EPISODE_STEPS,
            continuous=continuous,
            agent_mode=self.agent_mode,
            obs_width=obs_width,
            obs_height=obs_height,
            **kwargs,
        )

        if not self.continuous:
            self.action_space = spaces.Discrete(self.actions.move_forward + 1)

        # Store original observation space before updating
        original_obs_space = self.observation_space

        # Update observation space to include desired_goal and achieved_goal
        self.observation_space = spaces.Dict(
            {
                "observation": original_obs_space,
                "desired_goal": original_obs_space,
                "achieved_goal": original_obs_space,
            }
        )

    def _generate_world_layout(self, pos=None):
        rooms = []

        # Create rooms in grid layout
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                rooms.append(
                    self.add_rect_room(
                        min_x=self.room_size * j,
                        max_x=self.room_size * (j + (1 - ROOM_BOUNDARY_MARGIN)),
                        min_z=self.room_size * i,
                        max_z=self.room_size * (i + (1 - ROOM_BOUNDARY_MARGIN)),
                        floor_tex=self.textures[self.grid_size * i + j],
                    )
                )

        # Connect rooms based on connection list
        for connection in self.connections:
            if rooms[connection[0]].mid_x == rooms[connection[1]].mid_x:
                self.connect_rooms(
                    rooms[connection[0]],
                    rooms[connection[1]],
                    min_x=rooms[connection[0]].mid_x - self.door_size,
                    max_x=rooms[connection[0]].mid_x + self.door_size,
                )
            else:
                self.connect_rooms(
                    rooms[connection[0]],
                    rooms[connection[1]],
                    min_z=rooms[connection[0]].mid_z - self.door_size,
                    max_z=rooms[connection[0]].mid_z + self.door_size,
                )

        # Place agent
        if pos is None:
            self.place_agent(pos=list(AGENT_START_POSITION))
        else:
            self.place_agent(pos=[pos[0], 0, pos[1]])

        # Place box entities in each room in a 3x3 grid pattern
        self._place_room_boxes()

    def _place_room_boxes(self):
        """Place colored box entities in each room using a 3x3 grid pattern."""
        available_colors = list(COLORS.keys())
        num_colors = len(available_colors)

        for room_row in range(self.grid_size):
            for room_col in range(self.grid_size):
                room_start_x = self.room_size * room_col
                room_start_z = self.room_size * room_row

                # Place boxes in a 3x3 grid within each room
                for box_index in range(BOXES_PER_ROOM):
                    box_row = box_index // BOX_GRID_SIZE
                    box_col = box_index % BOX_GRID_SIZE

                    # Calculate unique color index for variety
                    color_index = (
                        box_index + 1 + (room_row + 1) * (room_col + 1)
                    ) % num_colors
                    box_color = available_colors[color_index]

                    # Calculate box position within room
                    box_x = (
                        room_start_x
                        + ROOM_CENTER_FRACTION * self.room_size * box_col
                        + BOX_OFFSET_FRACTION * self.room_size
                    )
                    box_z = (
                        room_start_z
                        + ROOM_CENTER_FRACTION * self.room_size * box_row
                        + BOX_OFFSET_FRACTION * self.room_size
                    )

                    # Create and place the box
                    box = Box(
                        color=box_color,
                        transparentable=True,
                        size=BOX_SIZE_FRACTION * self.room_size,
                        static=True,
                    )

                    self.place_entity(ent=box, pos=[box_x, 0, box_z], dir=0)

    def step(self, action):
        obs, reward, terminated, truncated, info = super().step(action)

        # Check if goal is achieved
        if self.is_goal_achieved():
            terminated = True
            reward = 1.0  # Positive reward for achieving goal

        # Return observation as dict
        obs_dict = {
            "observation": obs,
            "desired_goal": self.desired_goal,
            "achieved_goal": obs,
        }
        return obs_dict, reward, terminated, truncated, info

    def reset(self, seed=None, options=None, pos=None):
        """
        Reset the environment and generate a new goal.

        Args:
            seed: Random seed
            options: Additional options
            pos: Agent starting position

        Returns:
            tuple: (observation, info)
        """
        # Call parent reset
        obs, info = super().reset(seed=seed, options=options, pos=pos)

        # Generate goal
        self.desired_goal = self.get_goal()

        # Return observation as dict with desired_goal and achieved_goal
        obs_dict = {
            "observation": obs,
            "desired_goal": self.desired_goal,
            "achieved_goal": obs,
        }
        return obs_dict, info

    def get_goal(self):
        """
        Generate a goal by randomly selecting a room and goal position.

        Returns:
            np.ndarray: Rendered goal image
        """
        # Select random room
        room_idx = np.random.randint(len(self.goal_positions))

        # Select random goal within room
        goal_idx = np.random.randint(len(self.goal_positions[room_idx]))

        # Get goal position
        goal_position = self.goal_positions[room_idx][goal_idx]
        self._current_goal_position = goal_position
        self._current_goal_room = room_idx
        self._current_goal_idx = goal_idx

        # Render goal image
        goal_image = self.render_on_pos(goal_position)

        return goal_image

    def render_on_pos(self, pos):
        """
        Render observation from a specific position.

        Args:
            pos: Position to render from [x, y, z]

        Returns:
            np.ndarray: Rendered observation
        """
        # Store current agent position
        current_pos = self.agent.pos.copy()

        # Move agent to target position
        self.place_agent(pos=pos)

        # Render observation from this position
        obs = self.render_top_view(POMDP=True, render_ag=False)

        # Resize to match observation dimensions if needed
        if obs.shape[:2] != (self.obs_height, self.obs_width):
            obs = cv2.resize(
                obs, (self.obs_width, self.obs_height), interpolation=cv2.INTER_AREA
            )

        # Restore agent position
        self.place_agent(pos=current_pos)

        return obs

    def is_goal_achieved(self, pos=None, threshold=0.5):
        """
        Check if the agent has achieved the current goal.

        Args:
            pos: Agent position to check (uses current agent pos if None)
            threshold: Distance threshold for goal achievement

        Returns:
            bool: True if goal is achieved
        """
        if pos is None:
            pos = self.agent.pos

        if not hasattr(self, "_current_goal_position"):
            return False

        # Convert to numpy arrays and calculate distance
        pos_array = np.array(pos)
        goal_array = np.array(self._current_goal_position)
        distance = np.linalg.norm(pos_array - goal_array)

        return bool(distance < threshold)
