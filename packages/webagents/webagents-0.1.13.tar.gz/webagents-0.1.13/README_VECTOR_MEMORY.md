# VectorMemorySkill - Semantic Vector Memory System

## Overview

The **VectorMemorySkill** provides intelligent semantic memory storage and retrieval using Milvus vector database. Unlike traditional keyword-based memory systems, this skill uses vector embeddings to find related memories by meaning rather than exact text matches.

## Key Features

### 🧠 **Semantic Memory Storage**
- Vector embeddings generated using OpenAI's text-embedding models
- Stores memories with rich metadata (category, importance, tags, scope)
- Automatic context preservation across conversations

### 🔍 **Intelligent Retrieval** 
- Similarity-based search using vector embeddings
- Finds related memories even with different wording
- Ranked results by relevance and importance

### 🏷️ **Categorized Organization**
- Memory categories: conversation, knowledge, context, solution, preference
- Importance scoring (1-10) for prioritization
- Flexible tagging system for filtering

### 🔒 **Scope-Based Access Control**
- **Owner** - Private memories for specific user/agent
- **Shared** - Accessible to authorized users
- **Public** - Generally accessible memories
- Default scope: "owner" for privacy

### ⚡ **High Performance**
- Milvus vector database for fast similarity search
- Configurable collection and connection parameters
- Automatic collection creation and indexing

## Architecture

### Technology Stack
```
VectorMemorySkill
├── OpenAI Embeddings (text-embedding-3-small)
├── Milvus Vector Database (local/cloud)
├── Vector Similarity Search (L2 distance)
└── Metadata Filtering & Ranking
```

### Memory Data Model
```python
@dataclass
class VectorMemoryItem:
    id: str                      # Unique identifier
    content: str                 # Memory content
    category: str                # Memory type
    importance: int              # 1-10 score
    source: str                  # Origin source
    tags: List[str]             # Searchable tags
    scope: str                  # Access control
    created_at: str             # Timestamp
    access_count: int           # Usage tracking
    embedding: List[float]      # Vector representation
```

## Configuration

### Basic Configuration

```python
from robutler.agents.skills.core.vector_memory import VectorMemorySkill

# Minimal configuration
vector_memory = VectorMemorySkill({
    'agent_name': 'my_assistant',
    'openai_api_key': 'your-openai-key'
})
```

### Advanced Configuration

```python
# Full configuration options
vector_memory = VectorMemorySkill({
    # Agent context
    'agent_name': 'my_assistant',
    
    # Milvus database configuration
    'milvus_host': 'localhost',           # or 'https://cloud-endpoint'
    'milvus_port': 19530,
    'milvus_token': '',                   # For cloud/auth
    'milvus_collection': 'agent_memory',
    
    # OpenAI embedding configuration
    'openai_api_key': 'your-openai-key',
    'embedding_model': 'text-embedding-3-small',
    
    # Memory management
    'max_memories': 1000,
    'auto_extract': True,
    'default_scope': 'owner',
    
    # Dependencies (if using dependency injection)
    'dependencies': {}
})
```

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional Milvus configuration
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_TOKEN=your-token
MILVUS_COLLECTION=agent_memory
```

## Usage

### Storing Memories

```python
# Store important conversation context
await vector_memory.store_vector_memory(
    content="User prefers to use TypeScript for all new projects due to better type safety",
    category="preference",
    importance=8,
    tags=["typescript", "development", "preferences"],
    scope="owner"
)

# Store technical knowledge
await vector_memory.store_vector_memory(
    content="To fix the authentication issue, we updated the JWT token validation middleware to handle edge cases with expired tokens",
    category="solution",
    importance=9,
    tags=["authentication", "jwt", "middleware", "bug-fix"]
)

# Store project context
await vector_memory.store_vector_memory(
    content="The project uses React with Next.js, PostgreSQL database, and deploys to Vercel",
    category="context",
    importance=7,
    tags=["react", "nextjs", "postgresql", "vercel", "stack"]
)
```

### Searching Memories

```python
# Semantic search - finds related memories by meaning
result = await vector_memory.search_vector_memories(
    query="authentication problems",
    limit=5,
    category="solution",
    min_importance=7
)

# Parse results
search_data = json.loads(result)
if search_data["success"]:
    for memory in search_data["memories"]:
        print(f"Relevance: {memory['similarity_score']:.2f}")
        print(f"Content: {memory['content']}")
        print(f"Tags: {memory['tags']}")
        print("---")
```

### Listing Memories

```python
# List memories with filtering
result = await vector_memory.list_vector_memories(
    category="preference",
    min_importance=5,
    scope_filter="owner",
    limit=20
)

memories = json.loads(result)["memories"]
```

### Memory Statistics

```python
# Get comprehensive statistics
stats = await vector_memory.get_vector_memory_stats()
stats_data = json.loads(stats)

print(f"Total memories: {stats_data['total_memories']}")
print(f"Categories: {stats_data['categories']}")
print(f"Connection: {stats_data['connection_status']}")
```

## LLM Integration

### Automatic Prompting

The skill provides comprehensive guidance to the LLM through the `@prompt` decorator:

```python
@prompt(priority=20, scope="all")
def vector_memory_guidance(self, context) -> str:
    """Guide the LLM on when and how to use vector memory"""
```

### LLM Usage Examples

The LLM automatically learns to:

**Store Important Information:**
```
User: "I always prefer to use pytest for testing because it's more flexible"
→ LLM calls: store_vector_memory("User prefers pytest for testing due to flexibility", "preference", 7)
```

**Retrieve Relevant Context:**
```
User: "How should I set up testing for this project?"
→ LLM calls: search_vector_memories("testing setup preferences")
→ Retrieves: "User prefers pytest for testing due to flexibility"
→ Response: "Based on our previous discussions, I'd recommend pytest since you prefer it for its flexibility..."
```

## Memory Categories

### **Conversation**
- Important dialogue and decisions made
- Key points from discussions
- User feedback and reactions

```python
await store_vector_memory(
    "User decided to use microservices architecture after discussing scalability concerns",
    "conversation", 8
)
```

### **Knowledge** 
- Technical facts and explanations
- Procedures and how-to information
- Domain-specific knowledge

```python
await store_vector_memory(
    "CORS errors occur when frontend and backend are on different ports. Fix by configuring Access-Control-Allow-Origin header",
    "knowledge", 9
)
```

### **Context**
- Project requirements and constraints
- Environmental setup and configuration
- Background information

```python
await store_vector_memory(
    "Project must support IE11 compatibility and has a strict deadline of Q2",
    "context", 8
)
```

### **Solution**
- Problem-solving approaches
- Bug fixes and workarounds
- Implementation strategies

```python
await store_vector_memory(
    "Resolved memory leak by implementing proper cleanup in useEffect hooks",
    "solution", 9
)
```

### **Preference**
- User preferences and working styles
- Tool and technology choices
- Workflow patterns

```python
await store_vector_memory(
    "User prefers functional components over class components in React",
    "preference", 7
)
```

## Agent Integration

### With BaseAgent

```python
from robutler.agents.core.base_agent import BaseAgent
from robutler.agents.skills.core.vector_memory import VectorMemorySkill

# Create vector memory skill
vector_memory = VectorMemorySkill({
    'agent_name': 'code_assistant',
    'openai_api_key': os.getenv('OPENAI_API_KEY'),
    'milvus_host': 'localhost'
})

# Create agent with vector memory
agent = BaseAgent(
    name="code_assistant",
    instructions="""
    You are a helpful coding assistant. Use vector memory to:
    - Remember user preferences and coding styles
    - Store important technical solutions
    - Recall project context and requirements
    - Build on previous conversations
    """,
    model="gpt-4o-mini",
    skills={
        "vector_memory": vector_memory
    }
)
```

### Skill Combination

```python
from robutler.agents.skills.core import LongTermMemorySkill, VectorMemorySkill

# Use both traditional and vector memory
long_term_memory = LongTermMemorySkill({'agent_name': 'assistant'})
vector_memory = VectorMemorySkill({'agent_name': 'assistant'})

agent = BaseAgent(
    name="assistant",
    skills={
        "memory": long_term_memory,      # For structured memories
        "vector_memory": vector_memory    # For semantic search
    }
)
```

## Milvus Setup

### Local Milvus with Docker

```bash
# Start Milvus standalone
docker run -d \
  --name milvus-standalone \
  -p 19530:19530 \
  -v $(pwd)/volumes/milvus:/var/lib/milvus \
  milvusdb/milvus:latest

# Verify connection
curl http://localhost:19530/health
```

### Zilliz Cloud (Managed Milvus)

```python
vector_memory = VectorMemorySkill({
    'milvus_host': 'https://your-cluster.zillizcloud.com',
    'milvus_token': 'your-api-token',
    'milvus_collection': 'production_memory'
})
```

### Collection Schema

The skill automatically creates collections with this schema:

```python
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True),
    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name="importance", dtype=DataType.INT64),
    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=255),
    FieldSchema(name="tags", dtype=DataType.VARCHAR, max_length=1000),
    FieldSchema(name="scope", dtype=DataType.VARCHAR, max_length=50),
    FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=50),
    FieldSchema(name="access_count", dtype=DataType.INT64),
    FieldSchema(name="agent_name", dtype=DataType.VARCHAR, max_length=255),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536)
]
```

## Testing

### Unit Tests

```bash
# Run vector memory tests
cd robutler
python3 tests/test_vector_memory_skill.py

# Run with pytest
pytest tests/test_vector_memory_skill.py -v
```

### Integration Testing

```python
# Test with real Milvus instance
@pytest.mark.integration
async def test_real_milvus_integration():
    skill = VectorMemorySkill({
        'agent_name': 'test_agent',
        'milvus_host': 'localhost',
        'openai_api_key': os.getenv('OPENAI_API_KEY')
    })
    
    # Store memory
    result = await skill.store_vector_memory(
        "Test memory for integration",
        "test", 5
    )
    assert json.loads(result)["success"] == True
    
    # Search memory
    search_result = await skill.search_vector_memories("test memory")
    assert json.loads(search_result)["success"] == True
```

## Performance Considerations

### Embedding Generation
- OpenAI API calls: ~100-500ms per embedding
- Batch processing for multiple memories
- Consider caching for frequently accessed content

### Vector Search
- Milvus L2 distance: ~1-10ms for typical collections
- IVF_FLAT index balances speed and accuracy
- Collection size affects search performance

### Memory Management
- Default limit: 1000 memories per agent
- Automatic cleanup based on importance and access patterns
- Configurable memory limits per use case

### Optimization Tips

```python
# Batch store multiple memories
memories = [
    ("Memory 1", "category1", 7),
    ("Memory 2", "category2", 8),
    ("Memory 3", "category3", 6)
]

for content, category, importance in memories:
    await skill.store_vector_memory(content, category, importance)

# Use appropriate search limits
result = await skill.search_vector_memories(
    "query", 
    limit=5,  # Don't over-fetch
    min_importance=6  # Filter by relevance
)
```

## Error Handling

### Graceful Degradation

```python
# Check requirements before use
if not skill._check_requirements():
    print("Vector memory not available - falling back to regular memory")
    # Use alternative memory system
    
# Handle API failures
result = await skill.store_vector_memory("content", "category", 5)
result_data = json.loads(result)

if not result_data["success"]:
    print(f"Storage failed: {result_data['error']}")
    # Handle failure (retry, log, fallback, etc.)
```

### Common Issues

**1. Missing Dependencies**
```bash
pip install pymilvus openai
```

**2. Milvus Connection Failed**
- Check if Milvus is running
- Verify host/port configuration
- Check network connectivity

**3. OpenAI API Issues**
- Verify API key is valid
- Check account billing/usage limits
- Handle rate limiting appropriately

**4. Embedding Dimension Mismatch**
- text-embedding-3-small: 1536 dimensions
- text-embedding-ada-002: 1536 dimensions
- Update collection schema if changing models

## Security Considerations

### API Key Management
```python
# Use environment variables
import os
vector_memory = VectorMemorySkill({
    'openai_api_key': os.getenv('OPENAI_API_KEY')
})
```

### Data Privacy
- Memories stored with agent-specific scoping
- Default "owner" scope ensures privacy
- Content filtered by agent_name in all operations

### Access Control
```python
# Restrict to owner scope only
result = await skill.search_vector_memories(
    "query",
    scope_filter="owner"  # Explicit scope filtering
)
```

## Best Practices

### ✅ **Do:**
- Store contextually rich memories with good descriptions
- Use appropriate importance scores (1-10) 
- Include relevant tags for filtering
- Set proper scopes for access control
- Search memories before responding to provide context
- Monitor memory usage and cleanup old memories

### ❌ **Don't:**
- Store sensitive personal information without encryption
- Use overly broad search queries
- Ignore embedding API rate limits
- Store duplicate or redundant memories
- Skip error handling for API failures
- Use very long content (>64KB) without chunking

### Memory Content Guidelines

**Good Memory Content:**
```python
# Specific and contextual
"User prefers React functional components with TypeScript for better type safety and cleaner code. Mentioned they had issues with class component lifecycle methods in previous projects."

# Solution-oriented  
"Fixed CORS issue by adding proxy configuration to Next.js config file. The problem occurred when API calls went from localhost:3000 to localhost:8000."
```

**Poor Memory Content:**
```python
# Too vague
"User likes React"

# No context
"Fixed bug"
```

## Future Enhancements

- **Multi-modal Embeddings**: Support for image and code embeddings
- **Federated Search**: Search across multiple collections/agents
- **Memory Clustering**: Automatic grouping of related memories
- **Importance Learning**: AI-driven importance scoring
- **Memory Summarization**: Automatic condensation of old memories
- **Real-time Sync**: Live memory updates across agent instances

The VectorMemorySkill provides a powerful foundation for building context-aware agents that can learn and remember from interactions, making conversations more intelligent and personalized over time. 🧠✨ 