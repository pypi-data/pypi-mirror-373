"""MemoryStore: Unified YAML-driven memory storage class.

Clean, class-based interface that handles both graph and vector operations.
Follows Option 3 (Composite Interface) pattern with full YAML schema compliance.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
import warnings

from ...utils import generate_hrid
from ...utils.db_clients import DatabaseClients
from ...utils.hrid_tracker import HridTracker
from ..exceptions import DatabaseError, ProcessingError
from ..interfaces.embedder import Embedder
from ..interfaces.kuzu import KuzuInterface
from ..interfaces.qdrant import QdrantInterface
from ..yaml_translator import YamlTranslator


class MemoryService:
    """Unified memory service - handles indexing, search, and deletion operations.

    Provides a clean, class-based interface for all memory operations using
    DatabaseClients for both DDL initialization and CRUD interface access.
    Eliminates the need for scattered interface creation.

    Attributes:
        qdrant: Qdrant interface instance.
        kuzu: Kuzu interface instance.
        embedder: Embedder instance.
        yaml_translator: YAML translator instance.
        hrid_tracker: HRID tracker instance.
    """

    def __init__(self, db_clients):
        """Initialize MemoryService with DatabaseClients.

        Args:
            db_clients: DatabaseClients instance (after init_dbs() called).
        """
        if not isinstance(db_clients, DatabaseClients):
            raise TypeError("db_clients must be a DatabaseClients instance")

        # Get interfaces from DatabaseClients (reuses DDL-created clients)
        self.qdrant = db_clients.get_qdrant_interface()
        self.kuzu = db_clients.get_kuzu_interface()
        self.embedder = db_clients.get_embedder()
        self.yaml_translator = db_clients.get_yaml_translator()
        self.hrid_tracker = HridTracker(self.kuzu)

    def add_memory(
        self,
        memory_type: str,
        payload: dict[str, Any],
        user_id: str,
        collection: str | None = None,
    ) -> str:
        """Add a memory to both graph and vector storage.

        Args:
            memory_type: Entity type from YAML schema (e.g., 'task', 'note').
            payload: Memory data conforming to YAML schema.
            user_id: Owner of the memory.
            collection: Optional Qdrant collection override.

        Returns:
            str: Memory HRID (Human-readable ID string).

        Raises:
            ProcessingError: If validation fails or storage operations fail.
        """
        try:
            # Create and validate memory from YAML schema using our instance
            memory = self.yaml_translator.create_memory_from_yaml(memory_type, payload, user_id)

            # Stamp timestamps
            now = datetime.now(UTC)
            if not memory.created_at:
                memory.created_at = now
            memory.updated_at = now

            # Generate HRID using tracker
            hrid = generate_hrid(memory_type, user_id, self.hrid_tracker)

            # Get anchor text from YAML-defined anchor field using our instance
            anchor_text = self.yaml_translator.build_anchor_text(memory)
            if not anchor_text:
                raise ProcessingError(
                    f"Empty anchor text for memory type '{memory_type}'",
                    operation="add_memory",
                    context={"memory_id": memory.id, "memory_type": memory_type},
                )

            # Generate embedding from anchor text
            vector = self.embedder.get_embedding(anchor_text)

            # Create complete flat payload for Qdrant (includes system fields for filtering)
            flat_payload = {
                "user_id": memory.user_id,  # Required for user filtering
                "memory_type": memory.memory_type,  # Required for type filtering
                "created_at": memory.created_at.isoformat(),  # Required for time filtering
                "updated_at": memory.updated_at.isoformat(),  # Required for time filtering
                "hrid": hrid,  # Include HRID for user-facing operations
                **memory.payload,  # Include all YAML-validated entity fields
            }

            # Add to Qdrant (vector storage) with complete payload
            success, _point_id = self.qdrant.add_point(
                vector=vector,
                payload=flat_payload,  # Complete flat payload with system + entity fields
                point_id=memory.id,
                collection=collection,
            )
            if not success:
                raise ProcessingError(
                    "Failed to add memory to vector storage",
                    operation="add_memory",
                    context={"memory_id": memory.id},
                )

            # Add to Kuzu (graph storage) - use entity-specific table
            kuzu_data = {
                "id": memory.id,
                "user_id": memory.user_id,
                "memory_type": memory.memory_type,
                "created_at": memory.created_at.isoformat(),
                "updated_at": memory.updated_at.isoformat(),
                **memory.payload,  # Include all YAML-validated fields
            }
            self.kuzu.add_node(memory_type, kuzu_data)

            # Create HRID mapping after successful storage
            self.hrid_tracker.create_mapping(hrid, memory.id, memory_type, user_id)

            return hrid  # Return HRID, not UUID

        except Exception as e:
            if isinstance(e, ProcessingError):
                raise
            raise ProcessingError(
                "Failed to add memory",
                operation="add_memory",
                context={"memory_type": memory_type, "user_id": user_id},
                original_error=e,
            ) from e

    def add_relationship(
        self,
        from_memory_hrid: str,
        to_memory_hrid: str,
        relation_type: str,
        from_memory_type: str,
        to_memory_type: str,
        user_id: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """Add a relationship between two memories using HRIDs.

        Args:
            from_memory_hrid: Source memory HRID.
            to_memory_hrid: Target memory HRID.
            relation_type: Relationship type from YAML schema (e.g., 'ANNOTATES').
            from_memory_type: Source memory entity type.
            to_memory_type: Target memory entity type.
            user_id: User ID for ownership verification.
            properties: Optional relationship properties.

        Raises:
            ProcessingError: If relationship creation fails.
        """
        try:
            # Translate HRIDs to UUIDs
            from_uuid = self.hrid_tracker.get_uuid(from_memory_hrid, user_id)
            to_uuid = self.hrid_tracker.get_uuid(to_memory_hrid, user_id)

            self.kuzu.add_relationship(
                from_table=from_memory_type,
                to_table=to_memory_type,
                rel_type=relation_type,
                from_id=from_uuid,
                to_id=to_uuid,
                user_id=user_id,
                props=properties or {},
            )
        except Exception as e:
            raise ProcessingError(
                "Failed to add relationship",
                operation="add_relationship",
                context={
                    "from_hrid": from_memory_hrid,
                    "to_hrid": to_memory_hrid,
                    "relation_type": relation_type,
                },
                original_error=e,
            ) from e

    def search_memories(
        self,
        query_text: str,
        limit: int = 5,
        user_id: str | None = None,
        memory_types: list[str] | None = None,
        collection: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search memories using vector similarity.

        Args:
            query_text: Text to search for.
            limit: Maximum number of results.
            user_id: Filter by user ID.
            memory_types: Filter by memory types.
            collection: Optional Qdrant collection override.

        Returns:
            list[dict[str, Any]]: List of memory results with scores.
        """
        try:
            # Generate query vector
            query_vector = self.embedder.get_embedding(query_text)

            # Build filters with mandatory user_id
            filters: dict[str, Any] = {}

            # CRITICAL SECURITY: user_id is mandatory
            if not user_id:
                raise DatabaseError(
                    "user_id is required for search operations",
                    operation="indexer_search_validation",
                    context={"user_id": user_id},
                )
            filters["user_id"] = user_id

            if memory_types:
                filters["memory_type"] = memory_types

            # Search in Qdrant (user_id now included in filters)
            results = self.qdrant.search_points(
                vector=query_vector,
                limit=limit,
                collection=collection,
                filters=filters,
            )

            return results

        except Exception as e:
            raise ProcessingError(
                "Failed to search memories",
                operation="search_memories",
                context={"query_text": query_text, "user_id": user_id},
                original_error=e,
            ) from e

    def get_memory_neighbors(
        self,
        memory_id: str,
        memory_type: str,
        user_id: str,
        relation_types: list[str] | None = None,
        direction: str = "any",
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get related memories through graph relationships.

        Args:
            memory_id: Memory ID to find neighbors for
            memory_type: Memory entity type
            user_id: User ID for isolation
            relation_types: Filter by specific relationship types
            direction: "in", "out", or "any"
            limit: Maximum number of neighbors

        Returns:
            List of neighbor memories with relationship info
        """
        try:
            return self.kuzu.neighbors(
                node_label=memory_type,
                node_uuid=memory_id,
                user_id=user_id,
                rel_types=relation_types,
                direction=direction,
                limit=limit,
            )
        except Exception as e:
            raise ProcessingError(
                "Failed to get memory neighbors",
                operation="get_memory_neighbors",
                context={"memory_id": memory_id, "memory_type": memory_type},
                original_error=e,
            ) from e

    def delete_memory(self, memory_hrid: str, memory_type: str, user_id: str) -> bool:
        """Delete a memory from both storages using HRID.

        Args:
            memory_hrid: Memory HRID to delete.
            memory_type: Memory entity type.
            user_id: User ID for ownership verification.

        Returns:
            bool: True if deletion succeeded.
        """
        try:
            # Translate HRID to UUID
            uuid = self.hrid_tracker.get_uuid(memory_hrid, user_id)

            # Delete from Qdrant (with user ownership verification)
            qdrant_success = self.qdrant.delete_points([uuid], user_id)

            # Delete from Kuzu (with user_id verification)
            kuzu_success = self.kuzu.delete_node(memory_type, uuid, user_id)

            # Mark HRID as deleted (soft delete in mapping)
            if qdrant_success and kuzu_success:
                self.hrid_tracker.mark_deleted(memory_hrid)

            return qdrant_success and kuzu_success

        except Exception as e:
            raise ProcessingError(
                "Failed to delete memory",
                operation="delete_memory",
                context={"memory_hrid": memory_hrid, "memory_type": memory_type},
                original_error=e,
            ) from e


def create_memory_service(db_clients) -> MemoryService:
    """Factory function to create a MemoryService instance.

    Args:
        db_clients: DatabaseClients instance (after init_dbs() called).

    Returns:
        MemoryService: Configured MemoryService instance.
    """
    return MemoryService(db_clients)


# Legacy compatibility (DEPRECATED)
def create_memory_store(
    kuzu_interface: KuzuInterface,
    qdrant_interface: QdrantInterface,
    embedder: Embedder,
    yaml_translator: YamlTranslator,
) -> MemoryService:
    """DEPRECATED: Use create_memory_service(db_clients) instead.

    This function is kept for backward compatibility but will be removed.
    """
    warnings.warn(
        "create_memory_store() is deprecated. Use create_memory_service(db_clients) instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Create a temporary wrapper for legacy compatibility
    class LegacyWrapper:
        """Temporary wrapper for backward compatibility with legacy interface access."""

        def get_qdrant_interface(self):
            """Get Qdrant interface instance."""
            return qdrant_interface

        def get_kuzu_interface(self):
            """Get Kuzu interface instance."""
            return kuzu_interface

        def get_embedder(self):
            """Get embedder interface instance."""
            return embedder

        def get_yaml_translator(self):
            """Get YAML translator instance."""
            return yaml_translator

    return MemoryService(LegacyWrapper())
