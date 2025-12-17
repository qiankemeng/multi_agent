# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-agent system implementation featuring:
- **Tool Creator Agent**: An agent that dynamically creates tools
- **Tool User Agent**: An agent that uses the created tools
- Core focus on context management, API parameter design, and multi-agent interaction

The codebase is designed to be maintainable with easily modifiable atomic operations and variable definitions.

## Current Implementation Status

### ✅ Completed: Core Configuration System

The project has implemented comprehensive configuration systems that define the foundation for multi-agent interaction:

#### 1. Interaction Configuration (Most Important - `config/interaction_config.py`)

This is the **core of the system** - defines all variables for agent-agent and tool interaction:

**Key Data Structures:**
- `Message`: Basic unit of communication between agents
  - Contains sender/receiver info, content, priority, context linkage
- `ToolCallRequest`: Request sent when an agent needs to call a tool
  - Includes tool name, parameters, caller info, timeout settings
- `ToolCallResponse`: Result returned after tool execution
  - Contains status, result, error info, execution metrics
- `Context`: Maintains conversation/task history and state (the "memory" of the system)
  - Tracks message history, tool call history, shared state between agents
  - Auto-manages history length, provides state get/set methods
- `AgentState`: Tracks current state of each agent
  - Status, current task, capabilities, available tools, performance metrics
- `InteractionConfig`: System-level interaction rules and parameters

**Key Enums:**
- `MessageType`: REQUEST, RESPONSE, NOTIFICATION, COMMAND, EVENT, ERROR
- `AgentRole`: TOOL_CREATOR, TOOL_USER, COORDINATOR, MONITOR
- `AgentStatus`: IDLE, BUSY, WAITING, ERROR, OFFLINE
- `ExecutionStatus`: PENDING, RUNNING, SUCCESS, FAILED, TIMEOUT, CANCELLED
- `Priority`: LOW, NORMAL, HIGH, URGENT

**Usage Pattern:**
```python
# Create context
context = Context(participants=["user", "creator"])

# Send message
msg = Message(
    message_type=MessageType.REQUEST,
    sender_id="user",
    receiver_id="creator",
    content={"action": "create_tool"},
    context_id=context.context_id
)
context.add_message(msg)

# Call tool
request = ToolCallRequest(tool_name="calc", parameters={"x": 1})
response = ToolCallResponse(request_id=request.request_id, status=ExecutionStatus.SUCCESS, result=2)
context.add_tool_call(request, response)
```

#### 2. Tool Configuration (`config/tool_config.py`)

Defines tool properties and management:
- `ToolConfig`: Complete tool definition (name, parameters, execution config, metadata)
- `ToolParameter`: Parameter definition with validation rules
- `ToolRegistry`: Global registry for tool management (register/unregister/query/update)

**Commands:**
```bash
# Run interaction examples (recommended first)
python examples/interaction_example.py

# Run tool config examples
python examples/tool_config_example.py

# Run tests
python tests/test_interaction_config.py
python tests/test_tool_config.py
```

## Development Guidelines

### Code Organization
- `config/`: All configuration and variable definitions
  - `interaction_config.py`: **Core interaction variables (most important)**
  - `tool_config.py`: Tool definitions
- `examples/`: Example usage code
- `tests/`: Unit tests

### Key Principles for Multi-Agent Architecture

1. **Always Use Context**: Every interaction should be associated with a Context for history tracking
2. **Message Chaining**: Use `parent_message_id` to track conversation threads
3. **State Management**: Update AgentState synchronously with agent activities
4. **Error Handling**: Always populate error details in ToolCallResponse when failures occur

### Context Management (Critical)
- Context is the "memory" of the system - maintains all interaction history
- Use `context.add_message()` for every message
- Use `context.add_tool_call()` for every tool invocation
- Use `context.shared_state` for inter-agent state sharing
- Context auto-manages history length to prevent unbounded growth

### Multi-Agent Interaction Pattern
```
Tool User Agent
    ↓ Creates Message (REQUEST)
    ↓ Sends to Tool Creator Agent
Tool Creator Agent
    ↓ Creates Message (RESPONSE)
    ↓ Creates/registers tool
    ↓ Returns tool info
Tool User Agent
    ↓ Creates ToolCallRequest
    ↓ Executes tool
    ↓ Gets ToolCallResponse
    ↓ Records in Context
```

## Next Steps

When implementing the actual agents:
1. **Message Router**: Route messages between agents based on sender/receiver IDs
2. **Tool Creator Agent**:
   - Receives tool creation requests via Messages
   - Dynamically generates ToolConfig
   - Registers tools in TOOL_REGISTRY
3. **Tool User Agent**:
   - Sends tool creation requests
   - Issues ToolCallRequests
   - Processes ToolCallResponses
4. **Coordinator**: Manage agent lifecycle and task distribution
5. **Persistence**: Save/restore Context and AgentState

## Important Documentation

- `INTERACTION_CONFIG_GUIDE.md`: Comprehensive guide to interaction variables (READ THIS FIRST)
- `TOOL_CONFIG_GUIDE.md`: Tool configuration system guide
- `readme.md`: Project overview and quick start
