"""
Debug segment analysis to see what's happening
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from processors import VideoProcessor, AtomicOperationsImplementation
from experiments import VideoMeta

def test_segment_analysis():
    """Test segment analysis exactly as pipeline does"""
    print("\n" + "="*60)
    print("Segment Analysis Debug")
    print("="*60)

    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"✗ Video not found: {video_path}")
        return

    # Create components
    video_processor = VideoProcessor()
    atomic_ops = AtomicOperationsImplementation(video_processor=video_processor)

    # Extract metadata
    print("\n[1] Extracting metadata...")
    video_meta = video_processor.extract_metadata(video_path)
    print(f"✓ Video: {video_meta.duration_sec:.1f}s")

    # Sample 3 frames from start
    print("\n[2] Sampling frames...")
    frames = atomic_ops.sample(
        source=video_meta,
        method="timestamps",
        params={"timestamps": [10.0, 30.0, 50.0]}
    )
    print(f"✓ Sampled {len(frames)} frames")
    for frame in frames:
        print(f"  - Frame at {frame.timestamp_sec}s: {frame.image_path}")

    # Analyze with MLLM (exactly as pipeline does)
    print("\n[3] Calling MLLM for analysis...")
    prompt = f"""Analyze this video segment from 0.0s to 60.0s.

Below are {len(frames)} frames sampled from this segment.

Please provide:
1. A concise description of what happens in this segment (2-3 sentences)
2. Main activities or events
3. Key objects or people visible

Format your response as:
Description: [your description]
Events: [list of events]
Objects: [list of objects]"""

    print(f"\nPrompt:\n{prompt}\n")
    print(f"Frames: {len(frames)}")
    print(f"Max tokens: 2000")

    response = atomic_ops.call_model(
        model_type="mllm",
        model_name=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5"),
        inputs={
            "prompt": prompt,
            "frames": frames,
            "system_prompt": "You are a helpful video analysis assistant."
        },
        params={
            "temperature": 0.7,
            "max_tokens": 2000  # 大幅增加，避免length限制
        }
    )

    print("\n[4] Response received:")
    print(f"  Success: {response.success}")
    print(f"  Error: {response.error_message}")
    print(f"  Output type: {type(response.output)}")
    print(f"  Output length: {len(str(response.output)) if response.output else 0}")
    print(f"  Output: '{response.output}'")
    print(f"  Tokens: {response.total_tokens}")
    print(f"  Cost: ${response.cost_usd:.4f}")

    if response.success and response.output:
        print(f"\n✓ Analysis successful!")
        print(f"\nFull output:\n{response.output}")
    else:
        print(f"\n✗ Analysis failed or empty")

if __name__ == "__main__":
    test_segment_analysis()
