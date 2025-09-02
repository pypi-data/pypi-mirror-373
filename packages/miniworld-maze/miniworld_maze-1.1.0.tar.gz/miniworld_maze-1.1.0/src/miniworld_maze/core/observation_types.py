"""Observation type definitions for Nine Rooms environments."""

from enum import IntEnum


class ObservationLevel(IntEnum):
    """Defines the different observation levels available in the environments.

    Each level provides a different perspective and amount of information:
    - TOP_DOWN_PARTIAL: Agent-centered partial top-down view (POMDP)
    - TOP_DOWN_FULL: Complete environment top-down view
    - FIRST_PERSON: 3D first-person view from agent's perspective
    """

    TOP_DOWN_PARTIAL = 1  # Top-down POMDP view (agent-centered, limited range)
    TOP_DOWN_FULL = 2  # Full top-down view of entire environment
    FIRST_PERSON = 3  # First-person 3D view from agent's perspective

    def __str__(self):
        """Return descriptive string representation."""
        names = {1: "TOP_DOWN_PARTIAL", 2: "TOP_DOWN_FULL", 3: "FIRST_PERSON"}
        return names[self.value]

    @property
    def description(self):
        """Return detailed description of this observation level."""
        descriptions = {
            1: "Agent-centered partial top-down view with limited visibility range",
            2: "Complete top-down view showing the entire environment",
            3: "First-person 3D perspective view from the agent's current position",
        }
        return descriptions[self.value]
