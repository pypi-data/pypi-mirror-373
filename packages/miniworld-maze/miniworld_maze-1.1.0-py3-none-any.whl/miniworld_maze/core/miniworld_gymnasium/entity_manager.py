"""
Centralized entity management system for MiniWorld environments.

This module provides a comprehensive entity management architecture that handles
entity lifecycle, spatial organization, and optimized queries for rendering
and collision detection.
"""

from typing import List, Optional, Tuple

import numpy as np

from .entities import Entity


class EntityCollection:
    """Optimized entity collection with spatial indexing."""

    def __init__(self, spatial_grid_size: float = 5.0):
        """Initialize entity collection with spatial grid indexing.

        Args:
            spatial_grid_size: Size of spatial grid cells for indexing (default: 5.0)
        """
        self.entities: List[Entity] = []
        self.spatial_grid_size = spatial_grid_size
        self.spatial_grid: dict = {}  # Grid cell -> list of entities
        self._entity_to_cell: dict = {}  # Entity -> current grid cell

    def add(self, entity: Entity) -> None:
        """Add entity to collection with spatial indexing."""
        if entity not in self.entities:
            self.entities.append(entity)
            self._update_spatial_index(entity)

    def remove(self, entity: Entity) -> bool:
        """Remove entity from collection."""
        if entity in self.entities:
            self.entities.remove(entity)
            self._remove_from_spatial_index(entity)
            return True
        return False

    def update_position(self, entity: Entity) -> None:
        """Update entity position in spatial index."""
        if entity in self.entities:
            self._update_spatial_index(entity)

    def get_all(self) -> List[Entity]:
        """Get all entities in collection."""
        return self.entities.copy()

    def get_in_radius(self, position: np.ndarray, radius: float) -> List[Entity]:
        """Get all entities within radius of position."""
        candidates = self._get_spatial_candidates(position, radius)

        result = []
        for entity in candidates:
            if hasattr(entity, "pos") and entity.pos is not None:
                distance = np.linalg.norm(entity.pos - position)
                if distance <= radius:
                    result.append(entity)

        return result

    def get_in_bounds(self, min_pos: np.ndarray, max_pos: np.ndarray) -> List[Entity]:
        """Get all entities within bounding box."""
        result = []
        for entity in self.entities:
            if hasattr(entity, "pos") and entity.pos is not None:
                pos = entity.pos
                if (
                    min_pos[0] <= pos[0] <= max_pos[0]
                    and min_pos[2] <= pos[2] <= max_pos[2]
                ):
                    result.append(entity)

        return result

    def clear(self) -> None:
        """Remove all entities from collection."""
        self.entities.clear()
        self.spatial_grid.clear()
        self._entity_to_cell.clear()

    def _get_grid_cell(self, position: np.ndarray) -> Tuple[int, int]:
        """Get grid cell coordinates for position."""
        x_cell = int(position[0] // self.spatial_grid_size)
        z_cell = int(position[2] // self.spatial_grid_size)
        return (x_cell, z_cell)

    def _update_spatial_index(self, entity: Entity) -> None:
        """Update entity in spatial index."""
        if not hasattr(entity, "pos") or entity.pos is None:
            return

        new_cell = self._get_grid_cell(entity.pos)
        old_cell = self._entity_to_cell.get(entity)

        if old_cell != new_cell:
            # Remove from old cell
            if old_cell is not None and old_cell in self.spatial_grid:
                if entity in self.spatial_grid[old_cell]:
                    self.spatial_grid[old_cell].remove(entity)
                if not self.spatial_grid[old_cell]:
                    del self.spatial_grid[old_cell]

            # Add to new cell
            if new_cell not in self.spatial_grid:
                self.spatial_grid[new_cell] = []
            if entity not in self.spatial_grid[new_cell]:
                self.spatial_grid[new_cell].append(entity)

            self._entity_to_cell[entity] = new_cell

    def _remove_from_spatial_index(self, entity: Entity) -> None:
        """Remove entity from spatial index."""
        old_cell = self._entity_to_cell.get(entity)
        if old_cell is not None and old_cell in self.spatial_grid:
            if entity in self.spatial_grid[old_cell]:
                self.spatial_grid[old_cell].remove(entity)
            if not self.spatial_grid[old_cell]:
                del self.spatial_grid[old_cell]

        if entity in self._entity_to_cell:
            del self._entity_to_cell[entity]

    def _get_spatial_candidates(
        self, position: np.ndarray, radius: float
    ) -> List[Entity]:
        """Get entities from spatial grid cells that could be within radius."""
        candidates = []
        center_cell = self._get_grid_cell(position)

        # Calculate how many grid cells to check based on radius
        cell_range = int(np.ceil(radius / self.spatial_grid_size)) + 1

        for dx in range(-cell_range, cell_range + 1):
            for dz in range(-cell_range, cell_range + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dz)
                if cell in self.spatial_grid:
                    candidates.extend(self.spatial_grid[cell])

        return candidates


class EntityLifecycleManager:
    """Manages entity lifecycle events and state transitions."""

    def __init__(self):
        """Initialize entity lifecycle manager with callback lists."""
        self.creation_callbacks = []
        self.removal_callbacks = []
        self.position_update_callbacks = []

    def register_creation_callback(self, callback):
        """Register callback for entity creation events."""
        self.creation_callbacks.append(callback)

    def register_removal_callback(self, callback):
        """Register callback for entity removal events."""
        self.removal_callbacks.append(callback)

    def register_position_update_callback(self, callback):
        """Register callback for entity position updates."""
        self.position_update_callbacks.append(callback)

    def on_entity_created(self, entity: Entity) -> None:
        """Handle entity creation event."""
        for callback in self.creation_callbacks:
            callback(entity)

    def on_entity_removed(self, entity: Entity) -> None:
        """Handle entity removal event."""
        for callback in self.removal_callbacks:
            callback(entity)

    def on_entity_position_updated(self, entity: Entity, old_pos: np.ndarray) -> None:
        """Handle entity position update event."""
        for callback in self.position_update_callbacks:
            callback(entity, old_pos)


class EntityManager:
    """Centralized entity management system."""

    def __init__(self, spatial_grid_size: float = 5.0):
        """Initialize entity manager with spatial collections and lifecycle management.

        Args:
            spatial_grid_size: Size of spatial grid cells for indexing (default: 5.0)
        """
        self.static_entities = EntityCollection(spatial_grid_size)
        self.dynamic_entities = EntityCollection(spatial_grid_size)
        self.agent: Optional[Entity] = None
        self.lifecycle_manager = EntityLifecycleManager()

        # Register internal callbacks for spatial index updates
        self.lifecycle_manager.register_position_update_callback(
            self._on_entity_position_updated
        )

    def set_agent(self, agent: Entity) -> None:
        """Set the agent entity."""
        self.agent = agent
        # Agent is typically dynamic
        if agent not in self.dynamic_entities.entities:
            self.add_entity(agent)

    def add_entity(
        self, entity: Entity, position: Optional[np.ndarray] = None, **kwargs
    ) -> None:
        """Add entity with automatic categorization."""
        if position is not None and hasattr(entity, "pos"):
            entity.pos = position.copy()

        # Categorize entity
        if self._is_static_entity(entity):
            self.static_entities.add(entity)
        else:
            self.dynamic_entities.add(entity)

        # Trigger lifecycle event
        self.lifecycle_manager.on_entity_created(entity)

    def remove_entity(self, entity: Entity) -> bool:
        """Remove entity from management."""
        removed = self.static_entities.remove(entity) or self.dynamic_entities.remove(
            entity
        )

        if removed:
            self.lifecycle_manager.on_entity_removed(entity)

        if entity is self.agent:
            self.agent = None

        return removed

    def get_all_entities(self) -> List[Entity]:
        """Get all entities (static + dynamic)."""
        return self.static_entities.get_all() + self.dynamic_entities.get_all()

    def get_dynamic_entities(self) -> List[Entity]:
        """Get all dynamic entities."""
        return self.dynamic_entities.get_all()

    def get_static_entities(self) -> List[Entity]:
        """Get all static entities."""
        return self.static_entities.get_all()

    def get_entities_in_radius(
        self,
        position: np.ndarray,
        radius: float,
        include_static: bool = True,
        include_dynamic: bool = True,
    ) -> List[Entity]:
        """Get entities within radius of position."""
        result = []

        if include_static:
            result.extend(self.static_entities.get_in_radius(position, radius))

        if include_dynamic:
            result.extend(self.dynamic_entities.get_in_radius(position, radius))

        return result

    def get_visible_entities(self, camera_frustum: dict) -> List[Entity]:
        """Get entities within camera view frustum."""
        # Simplified frustum culling - use bounding box for now
        min_pos = np.array(
            [
                camera_frustum.get("min_x", -100),
                camera_frustum.get("min_y", -100),
                camera_frustum.get("min_z", -100),
            ]
        )
        max_pos = np.array(
            [
                camera_frustum.get("max_x", 100),
                camera_frustum.get("max_y", 100),
                camera_frustum.get("max_z", 100),
            ]
        )

        result = []
        result.extend(self.static_entities.get_in_bounds(min_pos, max_pos))
        result.extend(self.dynamic_entities.get_in_bounds(min_pos, max_pos))

        return result

    def update_entity_position(self, entity: Entity, new_position: np.ndarray) -> None:
        """Update entity position and spatial indices."""
        if hasattr(entity, "pos"):
            old_pos = entity.pos.copy() if entity.pos is not None else None
            entity.pos = new_position.copy()

            # Update spatial indices
            if entity in self.static_entities.entities:
                self.static_entities.update_position(entity)
            elif entity in self.dynamic_entities.entities:
                self.dynamic_entities.update_position(entity)

            # Trigger lifecycle event
            if old_pos is not None:
                self.lifecycle_manager.on_entity_position_updated(entity, old_pos)

    def find_entity_by_type(self, entity_type: type) -> List[Entity]:
        """Find all entities of specific type."""
        result = []
        for entity in self.get_all_entities():
            if isinstance(entity, entity_type):
                result.append(entity)
        return result

    def clear_all(self) -> None:
        """Remove all entities."""
        entities_to_remove = self.get_all_entities()
        for entity in entities_to_remove:
            self.remove_entity(entity)

    def get_collision_candidates(self, entity: Entity, radius: float) -> List[Entity]:
        """Get entities that could collide with given entity."""
        if not hasattr(entity, "pos") or entity.pos is None:
            return []

        candidates = self.get_entities_in_radius(entity.pos, radius)
        # Remove self from candidates
        if entity in candidates:
            candidates.remove(entity)

        return candidates

    def _is_static_entity(self, entity: Entity) -> bool:
        """Determine if entity should be categorized as static."""
        return (hasattr(entity, "is_static") and entity.is_static) or (
            hasattr(entity, "static") and entity.static
        )

    def _on_entity_position_updated(self, entity: Entity, old_pos: np.ndarray) -> None:
        """Internal callback for entity position updates."""
        # Update spatial indices when entity positions change
        if entity in self.static_entities.entities:
            self.static_entities.update_position(entity)
        elif entity in self.dynamic_entities.entities:
            self.dynamic_entities.update_position(entity)

    def get_statistics(self) -> dict:
        """Get entity management statistics."""
        return {
            "total_entities": len(self.get_all_entities()),
            "static_entities": len(self.static_entities.entities),
            "dynamic_entities": len(self.dynamic_entities.entities),
            "spatial_grid_cells": len(self.static_entities.spatial_grid)
            + len(self.dynamic_entities.spatial_grid),
        }
