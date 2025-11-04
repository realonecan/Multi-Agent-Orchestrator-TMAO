"""
TMAO Memory System
------------------
Lightweight memory module for the Terminal Multi-Agent Orchestrator.

Each agent can store, search, and recall contextual information or results.
The system is fully local, async-safe, and terminal-friendly.

Author: TMAO Dev Team
License: MIT
"""

"""Memory system imports - organized for clarity and performance."""
import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
from uuid import uuid4

import numpy as np

# Set up logging for memory system
logger = logging.getLogger("memory")

# Create console handler for memory logging
memory_handler = logging.StreamHandler()
memory_formatter = logging.Formatter('%(asctime)s - Memory - %(levelname)s - %(message)s')
memory_handler.setFormatter(memory_formatter)
logger.addHandler(memory_handler)
logger.setLevel(logging.INFO)


# ================================
# ENUMS
# ================================
class MemoryType(Enum):
    EPISODIC = "episodic"      # Experiences / interactions
    SEMANTIC = "semantic"      # Facts / knowledge
    PROCEDURAL = "procedural"  # Skills / procedures
    WORKING = "working"        # Temporary short-term data


class MemoryPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


# ================================
# DATA CLASSES
# ================================
@dataclass
class MemoryItem:
    """Represents one stored memory unit."""
    id: str
    type: MemoryType
    content: Any
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    quality: float = 1.0
    access_count: int = 0
    expires_at: Optional[datetime] = None
    embedding: Optional[np.ndarray] = None


@dataclass
class MemoryQuery:
    """Query used for retrieval/search."""
    text: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    tags: Optional[Set[str]] = None
    limit: int = 10
    threshold: float = 0.7


# ================================
# MEMORY MANAGER
# ================================
class MemoryManager:
    """
    In-memory, async-safe vector memory for agents.
    
    Provides efficient storage, retrieval, and semantic search capabilities
    with automatic JSON serialization for structured data.
    """

    def __init__(self):
        """Initialize the memory manager with empty storage and cache."""
        self._store: Dict[str, MemoryItem] = {}
        self._embedding_cache: Dict[str, np.ndarray] = {}  # Cache for embeddings

    # ---------- Embeddings ----------
    async def _embed(self, text: str) -> np.ndarray:
        """
        Generate deterministic small embeddings using MD5 hash with caching.
        
        Args:
            text: Input text to embed
            
        Returns:
            Normalized numpy array embedding
        """
        # Check cache first
        if text in self._embedding_cache:
            return self._embedding_cache[text]
        
        import hashlib
        h = hashlib.md5(text.encode()).digest()
        arr = np.array([b / 255.0 for b in h[:48]], dtype=np.float32)
        norm = np.linalg.norm(arr)
        embedding = arr / norm if norm > 0 else arr
        
        # Cache the result (limit cache size to prevent memory bloat)
        if len(self._embedding_cache) < 1000:
            self._embedding_cache[text] = embedding
        
        return embedding

    # ---------- Store ----------
    async def store(
        self,
        content: Any,
        memory_type: MemoryType = MemoryType.WORKING,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
        expires_in: Optional[int] = None,  # minutes
    ) -> str:
        """Store a new memory entry."""
        memory_id = str(uuid4())

        # Auto-type-safety: Serialize structured data to JSON for consistency
        processed_content = content

        # If content is a dict or list, serialize to JSON string for storage
        if isinstance(content, (dict, list)):
            try:
                processed_content = json.dumps(content, default=str)
                # Store original type info in metadata for retrieval
                if metadata is None:
                    metadata = {}
                metadata["_content_type"] = type(content).__name__
            except (TypeError, ValueError):
                # If serialization fails, store as-is
                pass
        # If content is already a string, check if it's JSON and mark accordingly
        elif isinstance(content, str):
            try:
                json.loads(content)
                if metadata is None:
                    metadata = {}
                metadata["_content_type"] = "json_string"
            except (json.JSONDecodeError, TypeError):
                # Plain string, no special handling needed
                pass

        embedding = None
        if isinstance(processed_content, str) and len(processed_content.strip()) > 0:
            embedding = await self._embed(processed_content)

        expires_at = None
        if expires_in:
            expires_at = datetime.now() + timedelta(minutes=expires_in)

        # Handle both MemoryType enum and string inputs
        if isinstance(memory_type, str):
            # Convert string to enum
            memory_type_enum = getattr(MemoryType, memory_type.upper(), MemoryType.WORKING)
        else:
            memory_type_enum = memory_type

        item = MemoryItem(
            id=memory_id,
            type=memory_type_enum,
            content=processed_content,
            metadata=metadata or {},
            tags=tags or set(),
            expires_at=expires_at,
            embedding=embedding,
        )

        self._store[memory_id] = item
        logger.info(f"Memory stored: {memory_id[:8]} ({memory_type_enum.value})")
        return memory_id

    # ---------- Retrieve ----------
    async def retrieve(self, query: MemoryQuery) -> List[MemoryItem]:
        """Retrieve memories matching filters."""
        results: List[MemoryItem] = list(self._store.values())

        if query.memory_type:
            results = [m for m in results if m.type == query.memory_type]
        if query.tags:
            results = [m for m in results if query.tags.intersection(m.tags)]

        # Vector search
        if query.text:
            q_embed = await self._embed(query.text)
            scored = []
            for m in results:
                if m.embedding is not None:
                    sim = np.dot(q_embed, m.embedding) / (
                        np.linalg.norm(q_embed) * np.linalg.norm(m.embedding)
                    )
                    if sim >= query.threshold:
                        scored.append((m, sim))
            results = [m for m, _ in sorted(scored, key=lambda x: x[1], reverse=True)]

        results = results[:query.limit]
        logger.info(f"Retrieved {len(results)} memories")

        # Auto-type-safety: Convert stringified JSON back to structured data
        for memory_item in results:
            if isinstance(memory_item.content, str):
                # Check if this was originally structured data
                content_type = memory_item.metadata.get("_content_type")

                # Parse JSON strings back to structured data
                if content_type in ["dict", "list", "json_string"]:
                    try:
                        memory_item.content = json.loads(memory_item.content)
                        # Remove the type marker since we've restored it
                        memory_item.metadata.pop("_content_type", None)
                    except (json.JSONDecodeError, TypeError):
                        # Keep as string if parsing fails
                        pass
                else:
                    # For plain strings, try to parse if it looks like JSON
                    # but only if it's not too long (to avoid parsing large text content)
                    stripped = memory_item.content.strip()
                    if (len(stripped) < 10000 and
                        ((stripped.startswith('{') and stripped.endswith('}')) or
                         (stripped.startswith('[') and stripped.endswith(']')))):
                        try:
                            memory_item.content = json.loads(memory_item.content)
                        except (json.JSONDecodeError, TypeError):
                            # Keep as string if it's not valid JSON
                            pass

        return results

    # ---------- Single Item Retrieval ----------
    def get(self, memory_id: str) -> Optional[MemoryItem]:
        """
        Retrieve a single memory item by ID.

        Args:
            memory_id: The memory ID to retrieve

        Returns:
            MemoryItem if found, None otherwise
        """
        if memory_id not in self._store:
            return None

        item = self._store[memory_id]

        # Apply same JSON parsing as in retrieve()
        if isinstance(item.content, str):
            content_type = item.metadata.get("_content_type")

            if content_type in ["dict", "list", "json_string"]:
                try:
                    item.content = json.loads(item.content)
                    item.metadata.pop("_content_type", None)
                except (json.JSONDecodeError, TypeError):
                    pass
            else:
                stripped = item.content.strip()
                if (len(stripped) < 10000 and
                    ((stripped.startswith('{') and stripped.endswith('}')) or
                     (stripped.startswith('[') and stripped.endswith(']')))):
                    try:
                        item.content = json.loads(item.content)
                    except (json.JSONDecodeError, TypeError):
                        pass

        return item
    async def cleanup(self) -> int:
        """
        Remove expired memories and clean up cache if needed.
        
        Returns:
            Number of expired memories removed
        """
        now = datetime.now()
        expired = [k for k, v in self._store.items() if v.expires_at and now > v.expires_at]
        for k in expired:
            del self._store[k]
        
        # Clean embedding cache if it's too large
        if len(self._embedding_cache) > 1000:
            # Keep only the most recent 500 entries (simple LRU-like behavior)
            self._embedding_cache = dict(list(self._embedding_cache.items())[-500:])
            logger.info(f"Cleaned embedding cache to 500 entries")
        
        if expired:
            logger.info(f"Cleaned {len(expired)} expired memories")
        
        return len(expired)

    # ---------- Delete ----------
    async def delete(self, memory_id: str):
        """Delete a memory by ID."""
        if memory_id in self._store:
            del self._store[memory_id]
            logger.info(f"Memory deleted: {memory_id[:8]}")

    # ---------- Summary ----------
    async def summary(self):
        """Print stats."""
        print("Memory Stats")
        print(f"Total: {len(self._store)}")
        types = {t.value: len([m for m in self._store.values() if m.type == t]) for t in MemoryType}
        for t, count in types.items():
            print(f"  {t:<12}: {count}")

    # ---------- Utilities ----------
    def is_structured_content(self, memory_id: str) -> bool:
        """
        Check if a memory item contains structured data.

        Args:
            memory_id: The memory ID to check

        Returns:
            True if content is structured (dict/list), False if string or other
        """
        if memory_id not in self._store:
            return False

        item = self._store[memory_id]
        return isinstance(item.content, (dict, list))
