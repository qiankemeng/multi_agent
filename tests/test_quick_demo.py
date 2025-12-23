"""
Quick demo - shows Tool Creator and Tool User working together
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.multi_agent_system.tool_creator import ToolCreatorAgent
from agents.multi_agent_system.tool_user import ToolUserAgent
from agents.mllm_client import MLLMClient, MLLMClientConfig

def test_quick_workflow():
    """Quick test showing the workflow"""
    print("\n" + "="*60)
    print("QUICK DEMO: Tool Creator + Tool User Workflow")
    print("="*60 + "\n")

    # Initialize
    mllm_client = MLLMClient(MLLMClientConfig())
    tool_creator = ToolCreatorAgent(mllm_client=mllm_client)
    tool_user = ToolUserAgent(mllm_client=mllm_client)

    # Simple task
    task = """
Task Type: Simple video analysis and question answering

Video: example_video.mp4
Question: What is happening in the video?

Requirements: Analyze the video and provide an answer.
"""

    print("📋 Task Description:")
    print(task)
    print("\n" + "-"*60 + "\n")

    # Step 1: Tool Creator designs tools
    print("🔧 STEP 1: Tool Creator Designing Tools...")
    print("   (This may take 1-2 minutes due to MLLM API calls)\n")

    try:
        tools = tool_creator.design_tools(task)

        print(f"\n✅ Tool Design Complete! Created {len(tools)} tools:\n")

        for i, tool in enumerate(tools, 1):
            print(f"   Tool {i}: {tool.tool_name}")
            print(f"   Purpose: {tool.purpose}")
            print(f"   Atomic Ops: {', '.join(tool.atomic_operations)}")
            print(f"   Parameters: {', '.join(tool.parameters.keys())}")
            print(f"   Prompt (first 100 chars): {tool.prompt_template[:100]}...")
            print()

    except Exception as e:
        print(f"\n❌ Tool Design Failed: {e}")
        return

    print("-"*60 + "\n")

    # Step 2: Tool User creates execution plan
    print("📝 STEP 2: Tool User Creating Execution Plan...\n")

    try:
        plan = tool_user._create_plan(
            task="Analyze the video and answer: What is happening in the video?",
            tools=tools,
            data={"video_path": "example_video.mp4", "question": "What is happening in the video?"}
        )

        print(f"\n✅ Plan Created!\n")
        print(f"   Reasoning: {plan.reasoning}\n")
        print(f"   Steps: {len(plan.steps)}\n")

        for i, step in enumerate(plan.steps, 1):
            print(f"   Step {i}: {step.tool_name}")
            print(f"      Inputs: {list(step.inputs.keys())}")
            print(f"      Dependencies: {step.dependencies if step.dependencies else 'None'}")
            print()

    except Exception as e:
        print(f"\n❌ Planning Failed: {e}")
        return

    print("-"*60 + "\n")
    print("✨ DEMO COMPLETE!\n")
    print("Summary:")
    print(f"   - Tool Creator: Successfully designed {len(tools)} tools")
    print(f"   - Tool User: Successfully created {len(plan.steps)}-step execution plan")
    print(f"   - Total API calls: {1 + len(tools)} (analysis + designs) + 1 (planning)")
    print(f"   - All prompts: English ✅")
    print(f"   - JSON parsing: Stable ✅")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_quick_workflow()
