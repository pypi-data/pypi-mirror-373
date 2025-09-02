"""OpenGL occlusion query utilities for MiniWorld environments."""

from typing import List, Set

from pyglet.gl import *

from .entities import Entity


class OcclusionQueryManager:
    """
    Manages OpenGL occlusion queries for entity visibility detection.

    This class handles the lifecycle of OpenGL occlusion queries, providing
    a clean interface for determining which entities are visible to the agent.
    """

    def __init__(self, entities: List[Entity]):
        """
        Initialize occlusion query manager.

        Args:
            entities: List of entities to test for visibility
        """
        self.entities = entities
        self.num_entities = len(entities)

        # Allocate OpenGL query IDs
        self.query_ids = (GLuint * self.num_entities)()
        glGenQueries(self.num_entities, self.query_ids)

    def begin_query(self, entity_index: int) -> None:
        """
        Begin occlusion query for specific entity.

        Args:
            entity_index: Index of entity in the entities list
        """
        if entity_index >= self.num_entities:
            raise IndexError(f"Entity index {entity_index} out of range")

        glBeginQuery(GL_ANY_SAMPLES_PASSED, self.query_ids[entity_index])

    def end_query(self) -> None:
        """End the current occlusion query."""
        glEndQuery(GL_ANY_SAMPLES_PASSED)

    def get_query_result(self, entity_index: int) -> bool:
        """
        Get the result of an occlusion query.

        Args:
            entity_index: Index of entity in the entities list

        Returns:
            True if entity is visible (any samples passed), False otherwise
        """
        if entity_index >= self.num_entities:
            raise IndexError(f"Entity index {entity_index} out of range")

        visible = (GLuint * 1)(1)
        glGetQueryObjectuiv(self.query_ids[entity_index], GL_QUERY_RESULT, visible)
        return visible[0] != 0

    def get_visible_entities(self, agent: Entity) -> Set[Entity]:
        """
        Get all entities that are visible (excluding the agent).

        Args:
            agent: The agent entity to exclude from results

        Returns:
            Set of visible entities
        """
        visible_entities = set()

        for entity_index, entity in enumerate(self.entities):
            if entity is agent:
                continue

            if self.get_query_result(entity_index):
                visible_entities.add(entity)

        return visible_entities

    def cleanup(self) -> None:
        """Clean up OpenGL resources."""
        if hasattr(self, "query_ids"):
            glDeleteQueries(self.num_entities, self.query_ids)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.cleanup()
