# Chat CLI Memory Management Features

This document describes the memory management features added to the DSAT chat CLI system.

## Overview

The chat CLI now supports comprehensive memory management for conversation history, including:
- Configurable memory limits
- Automatic response truncation
- Smart memory compaction
- Persistent conversation storage
- Memory usage monitoring

## New Features

### 1. Agent Configuration Memory Settings

Added three new fields to `AgentConfig`:

```python
memory_enabled: bool = True              # Enable/disable chat history persistence
max_memory_tokens: int = 8000           # Maximum tokens to keep in memory
response_truncate_length: int = 1000    # Truncate responses longer than this
```

### 2. Memory Management Components

#### MemoryManager Class (`src/dsat/cli/memory.py`)
- Token counting and estimation
- Memory compaction algorithms
- Persistent storage management
- Memory statistics calculation

#### ConversationMessage Class
- Structured message representation with token counting
- JSON serialization support
- Timestamp tracking

#### TokenCounter Class
- Simple but effective token estimation
- Heuristic-based counting (~4 chars per token)
- Role and formatting overhead calculation

### 3. Enhanced ChatSession

The `ChatSession` class now includes:
- Automatic memory management during message addition
- Response truncation for lengthy assistant responses
- Persistent conversation storage in `~/.dsat/chat_history/`
- Memory compaction when limits are exceeded
- Token counting for all messages

### 4. New CLI Commands

#### `/memory`
Shows detailed memory usage statistics:
- Total messages and tokens
- Memory usage percentage
- Tokens remaining
- Memory status with color coding

#### `/compact`
Manually compacts conversation memory:
- Preserves recent messages
- Shows before/after statistics
- Reduces memory usage while maintaining context

#### Enhanced `/clear`
Now properly integrates with memory system:
- Clears conversation history
- Updates persistent storage
- Maintains session continuity

#### Enhanced `/history`
Shows conversation history with memory stats:
- Message count and token usage in header
- Memory usage percentage
- Compatible with both memory-enabled and disabled agents

### 5. Context Window Management

#### Smart Truncation
- Response truncation at sentence or word boundaries
- Configurable length limits per agent
- Visual indicator ("...") for truncated content

#### Memory Compaction
- Sliding window approach preserving recent messages
- Configurable number of recent messages to preserve
- Automatic triggering when memory limits exceeded
- Manual triggering via `/compact` command

#### Token Limit Enforcement
- Automatic compaction when exceeding `max_memory_tokens`
- Preserves conversation flow while staying within limits
- Configurable limits per agent configuration

## Usage Examples

### Basic Configuration

```json
{
  "my_agent": {
    "agent_name": "my_agent",
    "model_provider": "anthropic",
    "model_family": "claude",
    "model_version": "claude-3-5-haiku-latest",
    "prompt": "assistant:v1",
    "memory_enabled": true,
    "max_memory_tokens": 4000,
    "response_truncate_length": 800
  }
}
```

### Memory-Disabled Agent

```json
{
  "simple_agent": {
    "agent_name": "simple_agent",
    "model_provider": "anthropic",
    "model_family": "claude", 
    "model_version": "claude-3-5-haiku-latest",
    "prompt": "assistant:v1",
    "memory_enabled": false
  }
}
```

### CLI Usage

```bash
# Start chat with memory-enabled agent
dsat chat --config agents.json --agent my_agent

# Check memory usage
/memory

# Compact memory manually
/compact

# View conversation history with memory stats
/history

# Clear conversation (persisted if memory enabled)
/clear
```

## Memory Statistics Display

The chat interface shows memory status in multiple places:

1. **Startup Display**: Shows memory status and current usage
2. **Memory Command**: Detailed statistics with color-coded status
3. **History Command**: Message and token counts in header
4. **Compact Command**: Before/after comparison

## Storage Format

Conversations are stored as JSON files in `~/.dsat/chat_history/`:

```json
{
  "session_id": "agent_name_20250120",
  "timestamp": "2025-01-20T10:30:00",
  "agent_config": {...},
  "messages": [...],
  "total_tokens": 1234
}
```

## Performance Considerations

- Token counting uses lightweight heuristics for speed
- Memory compaction only triggers when necessary
- Persistent storage is asynchronous and non-blocking
- Failed storage operations don't crash the chat session

## Backward Compatibility

- All existing functionality preserved
- Memory features are enabled by default but configurable
- Legacy `history` property maintained for existing code
- Existing agent configurations work without modification

## Testing

Comprehensive test suite covers:
- Memory manager functionality
- Token counting accuracy
- Conversation persistence
- Response truncation
- Memory compaction algorithms
- CLI command integration
- Backward compatibility

Run tests with:
```bash
uv run python -m pytest test/test_cli_chat.py -v
```