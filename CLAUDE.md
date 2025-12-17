# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **long video understanding** multi-agent system featuring:
- **Tool Creator Agent**: Dynamically creates video processing tools via MLLM API calls
- **Tool User Agent**: Uses created tools to process video data via MLLM API calls
- Core focus: Understanding long videos through segmentation and MLLM-based analysis

**Core Task**: Segment long videos, use MLLM (Multimodal Large Language Models) to understand each segment, and integrate results into complete video understanding.

## Current Implementation Status

### ✅ Completed: Foundational Infrastructure

#### 1. Project Task Definition (`PROJECT_TASK.md`)

Clearly defines the core mission:
- **Domain**: Long video understanding and analysis
- **Agent Implementation**: Via MLLM API calls (GPT-4V, Claude, Gemini, etc.)
- **Key Challenges**: Video length, temporal understanding, segmentation, information integration

#### 2. Interaction Configuration (`config/interaction_config.py`)

Defines all variables for agent-to-agent and tool interaction:
- `Message`: Basic communication unit
- `ToolCallRequest/Response`: Tool invocation
- `Context`: System memory (conversation/task history)
- `AgentState`: Agent status tracking
- `InteractionConfig`: System-level configuration

#### 3. Tool Configuration (`config/tool_config.py`)

Defines tool properties and management:
- `ToolConfig`: Complete tool definition
- `ToolParameter`: Parameter definition with validation
- `ToolRegistry`: Global tool management

#### 4. Video Understanding Variables (`experiments/video_variables.py`)

**THIS IS THE CORE** - Defines all variables for long video understanding:

**Basic Video Variables**:
- `VideoMeta`: video_id, duration_sec, fps, num_frames, width, height
- `Segment`: video_id, time_span (start_sec, end_sec), segment_index
- `Frame`: frame_id, timestamp_sec, image_path/image_base64
- `TimeSpan`: start_sec, end_sec

**Video Understanding Results**:
- `FrameCaption`: Caption for a single frame
- `SegmentCaption`: Caption for a video segment
- `VideoUnderstanding`: Complete video understanding

**MLLM API Interaction**:
- `MLLMRequest`: API request (model_name, prompt, images, task)
- `MLLMResponse`: API response (text, tokens, cost)

**Atomic Operations**:
- `AtomicOperation`: Basic operation unit
- `AtomicOperations`: Predefined operations (segment_video, extract_frames, generate_caption, etc.)

**Experiment Tracking**:
- `VideoExperimentRun`: Complete experiment record (tracks API calls, token usage, cost)

## Development Guidelines

### Long Video Understanding Workflow

```
1. Extract VideoMeta
   ↓
2. Segment video → Segment × N
   ↓
3. For each segment:
   - Extract key frames → Frame
   - Call MLLM API → MLLMRequest
   - Generate caption → SegmentCaption
   ↓
4. Integrate → VideoUnderstanding
```

### Key Principles

1. **Cost Control**: MLLM API calls have cost - design segmentation strategy carefully
2. **Context Management**: Pass context information across segments using `Context`
3. **Error Handling**: API calls may fail - implement retry mechanism
4. **Async Processing**: API calls have latency - use async where possible

### Agent Implementation

Agents are implemented as **MLLM API callers**:
- Tool Creator Agent: Uses MLLM to generate tool code/config
- Tool User Agent: Uses MLLM to analyze video content

### Variable Organization

```
Config Layer (interaction/tool config)
    ↓
Video Variables Layer (experiments/video_variables.py)
    ├── VideoMeta → Segment → Frame
    ├── MLLMRequest → MLLMResponse
    ├── FrameCaption → SegmentCaption → VideoUnderstanding
    └── VideoExperimentRun (tracks everything)
```

## Commands

```bash
# Run interaction examples
python examples/interaction_example.py

# Run tool config examples
python examples/tool_config_example.py

# Run tests
python tests/test_interaction_config.py
python tests/test_tool_config.py
```

## Next Steps

When implementing the actual agents:
1. **Video Processing Module**: Extract metadata, segment video, sample frames
2. **MLLM API Wrapper**: Encapsulate API calls with retry/error handling
3. **Tool Creator Agent**: Generate video analysis tools using MLLM
4. **Tool User Agent**: Use tools to analyze video content via MLLM
5. **Integration**: End-to-end pipeline

## Important Documentation

### Core Docs (READ FIRST)
- **`PROJECT_TASK.md`**: Project mission and long video understanding task
- **`VIDEO_VARIABLES.md`**: Complete variable reference for video understanding
- **`INTERACTION_CONFIG_GUIDE.md`**: Interaction system guide

### Reference Docs
- `TOOL_CONFIG_GUIDE.md`: Tool configuration guide
- `VARIABLE_ORGANIZATION.md`: Variable organization summary
- `readme.md`: Project overview

## Key Variables Reference

```python
# Basic video processing
from experiments import VideoMeta, Segment, TimeSpan, Frame

# Video understanding
from experiments import FrameCaption, SegmentCaption, VideoUnderstanding

# MLLM API
from experiments import MLLMRequest, MLLMResponse, AnalysisTask

# Experiment tracking
from experiments import VideoExperimentRun, ProcessingStatus

# Agent interaction
from config import Message, Context, AgentState, ToolCallRequest
```

## Design Philosophy

1. **Task-Specific**: All variables designed for long video understanding
2. **MLLM-Centric**: Native support for MLLM API interaction
3. **Cost-Aware**: Track API calls, tokens, and costs
4. **Traceable**: Complete ID-based relationships across all data
5. **Maintainable**: Clear structure, easy to modify

---

**Remember**: This project is about **long video understanding** using multi-agent collaboration and MLLM API calls.
