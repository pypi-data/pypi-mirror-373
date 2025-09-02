"""NineRooms environment implementation."""

from ..core import ObservationLevel
from .base_grid_rooms import GridRoomsEnvironment


class NineRooms(GridRoomsEnvironment):
    """
    Traverse the 9 rooms

    -------------
    | 0 | 1 | 2 |
    -------------
    | 3 | 4 | 5 |
    -------------
    | 6 | 7 | 8 |
    -------------
    """

    def __init__(
        self,
        connections=None,
        textures=None,
        placed_room=None,
        obs_level=ObservationLevel.TOP_DOWN_PARTIAL,
        continuous=False,
        room_size=5,
        door_size=2,
        agent_mode=None,
        obs_width=80,
        obs_height=80,
        **kwargs,
    ):
        # Default configuration for NineRooms
        default_connections = [
            (0, 1),
            (0, 3),
            (1, 2),
            (1, 4),
            (2, 5),
            (3, 4),
            (3, 6),
            (4, 5),
            (4, 7),
            (5, 8),
            (6, 7),
            (7, 8),
        ]
        default_textures = [
            "beige",
            "lightbeige",
            "lightgray",
            "copperred",
            "skyblue",
            "lightcobaltgreen",
            "oakbrown",
            "navyblue",
            "cobaltgreen",
        ]

        # Initialize goal positions for each room (2 goals per room)
        goal_positions = []
        for i in range(3):  # rows
            for j in range(3):  # columns
                center_x = room_size * j + room_size / 2
                center_z = room_size * i + room_size / 2
                # Two goals per room: center-left and center-right
                goal_positions.append(
                    [
                        [center_x - 1.0, 0.0, center_z],  # left goal
                        [center_x + 1.0, 0.0, center_z],  # right goal
                    ]
                )

        super().__init__(
            grid_size=3,
            connections=connections or default_connections,
            textures=textures or default_textures,
            goal_positions=goal_positions,
            placed_room=placed_room,
            obs_level=obs_level,
            continuous=continuous,
            room_size=room_size,
            door_size=door_size,
            agent_mode=agent_mode,
            obs_width=obs_width,
            obs_height=obs_height,
            **kwargs,
        )
