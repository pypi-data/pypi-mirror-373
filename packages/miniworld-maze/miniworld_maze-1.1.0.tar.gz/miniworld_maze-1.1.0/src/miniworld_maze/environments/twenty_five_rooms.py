"""TwentyFiveRooms environment implementation."""

from ..core import ObservationLevel
from .base_grid_rooms import GridRoomsEnvironment


class TwentyFiveRooms(GridRoomsEnvironment):
    """
    Traverse the 25 rooms

    ---------------------
    | 0 | 1 | 2 | 3 | 4 |
    ---------------------
    | 5 | 6 | 7 | 8 | 9 |
    ---------------------
    |10 |11 |12 |13 |14 |
    ---------------------
    |15 |16 |17 |18 |19 |
    ---------------------
    |20 |21 |22 |23 |24 |
    ---------------------
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
        # Default configuration for TwentyFiveRooms
        default_connections = [
            (0, 1),
            (0, 5),
            (1, 2),
            (1, 6),
            (2, 3),
            (2, 7),
            (3, 4),
            (3, 8),
            (4, 9),
            (5, 6),
            (5, 10),
            (6, 7),
            (6, 11),
            (7, 8),
            (7, 12),
            (8, 9),
            (8, 13),
            (9, 14),
            (10, 11),
            (10, 15),
            (11, 12),
            (11, 16),
            (12, 13),
            (12, 17),
            (13, 14),
            (13, 18),
            (14, 19),
            (15, 16),
            (15, 20),
            (16, 17),
            (16, 21),
            (17, 18),
            (17, 22),
            (18, 19),
            (18, 23),
            (19, 24),
            (20, 21),
            (21, 22),
            (22, 23),
            (23, 24),
        ]
        default_textures = [
            "crimson",
            "beanpaste",
            "cobaltgreen",
            "lightnavyblue",
            "skyblue",
            "lightcobaltgreen",
            "oakbrown",
            "copperred",
            "lightgray",
            "lime",
            "turquoise",
            "violet",
            "beige",
            "morningglory",
            "silver",
            "magenta",
            "sunnyyellow",
            "blueberry",
            "lightbeige",
            "seablue",
            "lemongrass",
            "orchid",
            "redbean",
            "orange",
            "realblueberry",
        ]

        # Initialize goal positions for each room (1 goal per room at center)
        goal_positions = []
        for i in range(5):  # rows
            for j in range(5):  # columns
                center_x = room_size * j + room_size / 2
                center_z = room_size * i + room_size / 2
                # One goal per room at the center
                goal_positions.append(
                    [
                        [center_x, 0.0, center_z],
                    ]
                )

        super().__init__(
            grid_size=5,
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
