"""Base MiniWorld environment class."""

from .params import DEFAULT_PARAMS
from .unified_env import UnifiedMiniWorldEnv


class MiniWorldEnv(UnifiedMiniWorldEnv):
    """
    Legacy base class for MiniWorld environments.

    This class provides backward compatibility with the original MiniWorld
    environment interface while leveraging the unified implementation.
    """

    def __init__(
        self,
        max_episode_steps=1500,
        obs_width=80,
        obs_height=80,
        window_width=800,
        window_height=600,
        params=DEFAULT_PARAMS,
        domain_rand=False,
    ):
        """
        Initialize base MiniWorld environment.

        Args:
            max_episode_steps: Maximum steps per episode
            obs_width: Observation width in pixels
            obs_height: Observation height in pixels
            window_width: Window width for human rendering
            window_height: Window height for human rendering
            params: Environment parameters for domain randomization
            domain_rand: Whether to enable domain randomization
        """
        # Mark this as a base environment (not custom) for background color handling
        self._is_custom_env = False

        # Initialize using unified base with base environment defaults
        super().__init__(
            obs_level=3,  # Default to FIRST_PERSON for base environments
            continuous=False,  # Base environments use discrete actions
            agent_mode="circle",  # Default agent mode
            max_episode_steps=max_episode_steps,
            obs_width=obs_width,
            obs_height=obs_height,
            window_width=window_width,
            window_height=window_height,
            params=params,
            domain_rand=domain_rand,
        )
