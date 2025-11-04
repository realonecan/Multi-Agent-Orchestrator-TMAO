Memory System Documentation
Overview

The Memory Layer is the backbone of the Terminal Multi-Agent Orchestrator.
It records every thought, action, result, and error from the agents, letting the system maintain context across steps or sessions.
The goal: simple, reliable, transparent memory — not a heavy database.

### 🔄 **Auto-Type-Safety System**

The memory system includes intelligent JSON serialization and parsing:

**Storage Enhancement:**
- **Structured Data**: Dictionaries and lists are automatically serialized to JSON
- **Type Tracking**: Metadata tracks original content types (`_content_type`)
- **Backward Compatibility**: Plain strings remain unchanged

**Retrieval Enhancement:**
- **Smart Parsing**: JSON strings are automatically parsed back to structured data
- **Content Detection**: System detects JSON vs plain text automatically
- **Fallback Safety**: Invalid JSON remains as strings to prevent data loss

**Example:**
```python
# Store structured data
await memory.store({
    "task": "API Development",
    "subtasks": ["design", "implement", "test"],
    "priority": "high"
})

# Retrieve - automatically parsed back to dict
results = await memory.retrieve(query)
content = results[0].content  # This is now a dict, not a JSON string
print(content["subtasks"])   # Works directly!
```

### 📊 **Memory Types**

| Type | Purpose | Use Case |
|------|---------|----------|
| **EPISODIC** | Experiences & interactions | Agent conversations, user inputs, logs |
| **SEMANTIC** | Facts & knowledge | Research data, API documentation |
| **PROCEDURAL** | Skills & procedures | Code snippets, execution results, templates |
| **WORKING** | Temporary data | Plans, intermediate results, context |

### 🔍 **Query System**

The memory system supports sophisticated querying:

**Basic Queries:**
```python
# Search by text similarity
query = MemoryQuery(text="API development")

# Filter by memory type
query = MemoryQuery(memory_type=MemoryType.WORKING)

# Combine filters
query = MemoryQuery(
    text="error handling",
    memory_type=MemoryType.EPISODIC,
    tags={"error", "recovery"}
)
```

**Advanced Features:**
- **Vector Similarity**: Semantic search using embeddings
- **Metadata Filtering**: Query by agent, timestamp, custom fields
- **Tag-Based Search**: Find memories by topic or category
- **Time-Based Queries**: Recent memories, time range filtering

### 🏗️ **Architecture Overview**

```
┌──────────────────────────┐
│     MemoryManager        │
│   (src/core/memory.py)   │
│                          │
│ • Async store/retrieve   │
│ • Vector embeddings      │
│ • Type-safe JSON parsing │
│ • Metadata filtering     │
└────────────┬─────────────┘
             │
┌──────────────────────────┐
│   In-Memory Cache        │
│   Dict[str, MemoryItem]  │
└──────────────────────────┘
```

### 💾 **Data Model**

**MemoryItem Structure:**
```python
@dataclass
class MemoryItem:
    id: str                    # UUID
    type: MemoryType          # EPISODIC, SEMANTIC, PROCEDURAL, WORKING
    content: Any              # Auto-parsed JSON or plain text
    created_at: datetime      # Timestamp
    metadata: Dict[str, Any]  # Custom fields (agent, context, etc.)
    tags: Set[str]            # Categories for filtering
    embedding: np.ndarray     # Vector for similarity search
```

**MemoryQuery Structure:**
```python
@dataclass
class MemoryQuery:
    text: Optional[str] = None      # Search term for similarity
    memory_type: Optional[MemoryType] = None
    tags: Optional[Set[str]] = None
    limit: int = 10
    threshold: float = 0.7
```

### 🔧 **Public API**

**Core Methods:**
```python
# Store structured data (auto-serialized to JSON)
await memory.store(
    content={"task": "API", "subtasks": ["design", "implement"]},
    memory_type=MemoryType.WORKING,
    metadata={"agent": "Planner", "plan_type": "decomposition"},
    tags={"plan", "api"}
)

# Retrieve with auto-parsing (JSON → dict)
results = await memory.retrieve(MemoryQuery(text="API", limit=5))
content = results[0].content  # Already parsed back to dict!

# Single item access
item = memory.get("memory_id_123")
if item and isinstance(item.content, dict):
    print(item.content["task"])  # Direct access works!
```

**Utility Methods:**
```python
# Check if content is structured
is_structured = memory.is_structured_content("memory_id")

# Get memory statistics
await memory.summary()

# Clean expired memories
await memory.cleanup()
```

### 🚀 **Key Improvements**

**✅ Auto-Type-Safety:**
- **Storage**: Dicts/lists → JSON strings with type metadata
- **Retrieval**: JSON strings → original types automatically
- **Compatibility**: Plain strings work unchanged

**✅ Robust Error Handling:**
- Invalid JSON stays as strings (no data loss)
- Serialization failures fall back to original content
- Comprehensive logging for debugging

**✅ Performance Optimized:**
- In-memory cache for fast access
- Vector similarity search for semantic queries
- Efficient filtering by metadata and tags

This enhancement makes the memory system **production-ready** and **developer-friendly**! 🎉