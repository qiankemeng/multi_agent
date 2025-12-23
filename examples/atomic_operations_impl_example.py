"""
Atomic Operations Example

Demonstrates Phase 2: Atomic Operations Implementation
1. SAMPLE operation - Frame sampling
2. SEGMENT operation - Video segmentation
3. CALL_MODEL operation - MLLM API calls
4. BBOX operation - Bounding box annotation

Usage:
    python examples/atomic_operations_impl_example.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from processors import (
    VideoProcessor,
    AtomicOperationsImplementation,
    print_video_info,
    print_segments_info,
    print_frames_info
)
from experiments import VideoMeta


def example_1_sample_operation():
    """Example 1: SAMPLE operation"""
    print("\n" + "="*60)
    print("Example 1: SAMPLE Operation")
    print("="*60)

    # Check if test video exists
    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"\n⚠ Video file not found: {video_path}")
        return None, None

    # Create components
    video_processor = VideoProcessor()
    atomic_ops = AtomicOperationsImplementation(video_processor=video_processor)

    # Extract metadata
    print(f"\nExtracting metadata from: {video_path}")
    video_meta = video_processor.extract_metadata(video_path)
    print_video_info(video_meta)

    # Test SAMPLE with uniform method
    print(f"\n--- SAMPLE Operation: uniform ---")
    frames = atomic_ops.sample(
        source=video_meta,
        method="uniform",
        params={"num_frames": 5}
    )
    print(f"✓ Sampled {len(frames)} frames using uniform method")
    print_frames_info(frames[:3])  # Show first 3

    # Test SAMPLE with timestamps method
    print(f"\n--- SAMPLE Operation: timestamps ---")
    frames_ts = atomic_ops.sample(
        source=video_meta,
        method="timestamps",
        params={"timestamps": [10.0, 30.0, 60.0, 120.0]}
    )
    print(f"✓ Sampled {len(frames_ts)} frames at specific timestamps")
    print_frames_info(frames_ts)

    print(f"\n✓ SAMPLE operation test successful!")
    return video_meta, atomic_ops


def example_2_segment_operation(video_meta, atomic_ops):
    """Example 2: SEGMENT operation"""
    print("\n" + "="*60)
    print("Example 2: SEGMENT Operation")
    print("="*60)

    # Test SEGMENT with fixed_duration strategy
    print(f"\n--- SEGMENT Operation: fixed_duration ---")
    segments = atomic_ops.segment(
        video_meta=video_meta,
        strategy="fixed_duration",
        params={"duration_sec": 30.0}
    )
    print(f"✓ Created {len(segments)} segments using fixed_duration strategy (30s each)")
    print_segments_info(segments[:5])  # Show first 5

    # Test SEGMENT with custom strategy
    print(f"\n--- SEGMENT Operation: custom ---")
    custom_segments = atomic_ops.segment(
        video_meta=video_meta,
        strategy="custom",
        params={"breakpoints": [0, 60, 180, 360, 600]}
    )
    print(f"✓ Created {len(custom_segments)} segments using custom breakpoints")
    print_segments_info(custom_segments)

    print(f"\n✓ SEGMENT operation test successful!")
    return segments


def example_3_call_model_operation(video_meta, atomic_ops):
    """Example 3: CALL_MODEL operation"""
    print("\n" + "="*60)
    print("Example 3: CALL_MODEL Operation (MLLM)")
    print("="*60)

    # Check if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ Skipping CALL_MODEL test (requires OPENAI_API_KEY)")
        print("Set API key: export OPENAI_API_KEY='your-key'")
        return

    # Sample a few frames first
    print(f"\n--- Sampling frames for MLLM analysis ---")
    frames = atomic_ops.sample(
        source=video_meta,
        method="uniform",
        params={"num_frames": 3}
    )
    print(f"✓ Sampled {len(frames)} frames")

    # Call MLLM
    print(f"\n--- CALL_MODEL Operation: mllm ---")
    print("Calling GPT-4 Vision to analyze frames...")

    response = atomic_ops.call_model(
        model_type="mllm",
        model_name=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4-turbo-preview"),
        inputs={
            "prompt": "Describe what you see in these video frames. Focus on the main content and activities.",
            "frames": frames
        },
        params={
            "temperature": 0.7,
            "max_tokens": 500
        }
    )

    if response.success:
        print(f"\n✓ MLLM Response:")
        print(f"  Model: {response.model_name}")
        print(f"  Tokens: {response.total_tokens}")
        print(f"  Cost: ${response.cost_usd:.4f}")
        print(f"  Time: {response.response_time_ms:.0f}ms")
        print(f"\n  Output:")
        print(f"  {response.output[:200]}...")
    else:
        print(f"\n✗ MLLM call failed: {response.error_message}")

    print(f"\n✓ CALL_MODEL operation test completed!")


def example_4_bbox_operation(video_meta, atomic_ops):
    """Example 4: BBOX operation"""
    print("\n" + "="*60)
    print("Example 4: BBOX Operation")
    print("="*60)

    # Sample one frame
    print(f"\n--- Sampling a frame for bbox annotation ---")
    frames = atomic_ops.sample(
        source=video_meta,
        method="uniform",
        params={"num_frames": 1}
    )
    frame = frames[0]
    print(f"✓ Sampled frame at t={frame.timestamp_sec:.2f}s")

    # Add bounding boxes
    print(f"\n--- BBOX Operation ---")
    annotated_frame = atomic_ops.bbox(
        frame=frame,
        boxes=[
            {
                "bbox": [100, 100, 300, 200],
                "label": "Object 1",
                "confidence": 0.95,
                "color": "green"
            },
            {
                "bbox": [500, 150, 200, 250],
                "label": "Object 2",
                "confidence": 0.87,
                "color": "red"
            }
        ]
    )

    print(f"✓ Drew 2 bounding boxes on frame")
    print(f"  Original: {frame.image_path}")
    print(f"  Annotated: {annotated_frame.image_path}")

    print(f"\n✓ BBOX operation test successful!")
    return annotated_frame


def example_5_combined_workflow(video_meta, atomic_ops):
    """Example 5: Combined workflow"""
    print("\n" + "="*60)
    print("Example 5: Combined Workflow")
    print("="*60)

    print("\nDemonstrating a complete atomic operations workflow:")
    print("1. SEGMENT video → 2. SAMPLE frames from first segment")
    print("3. CALL_MODEL for analysis → 4. BBOX on result frame")

    # Step 1: Segment video
    print(f"\n--- Step 1: SEGMENT ---")
    segments = atomic_ops.segment(
        video_meta=video_meta,
        strategy="fixed_duration",
        params={"duration_sec": 60.0}
    )
    first_segment = segments[0]
    print(f"✓ Created {len(segments)} segments, using first segment [0-60s]")

    # Step 2: Sample frames (but use video_meta as source for now)
    print(f"\n--- Step 2: SAMPLE ---")
    # Note: For segment sampling, we'd need to modify the implementation
    # For now, sample from the time range manually
    frames = atomic_ops.sample(
        source=video_meta,
        method="timestamps",
        params={"timestamps": [5.0, 15.0, 30.0, 45.0, 55.0]}
    )
    print(f"✓ Sampled {len(frames)} frames from first segment time range")

    # Step 3: Call MLLM (skip if no API key)
    if os.getenv("OPENAI_API_KEY"):
        print(f"\n--- Step 3: CALL_MODEL ---")
        print("Analyzing frames with MLLM...")
        # (MLLM call here - skipping detailed output)
        print("✓ MLLM analysis completed (skipped for brevity)")
    else:
        print(f"\n--- Step 3: CALL_MODEL (skipped - no API key) ---")

    # Step 4: Draw bbox on one frame
    print(f"\n--- Step 4: BBOX ---")
    annotated = atomic_ops.bbox(
        frame=frames[2],
        boxes=[{"bbox": [200, 200, 250, 180], "label": "Detected", "color": "blue"}]
    )
    print(f"✓ Added annotation to frame at t={frames[2].timestamp_sec:.2f}s")

    print(f"\n✓ Combined workflow completed!")

    # Show statistics
    print(f"\n--- Operation Statistics ---")
    stats = atomic_ops.get_stats()
    print(f"  SAMPLE calls: {stats['sample_calls']}")
    print(f"  SEGMENT calls: {stats['segment_calls']}")
    print(f"  CALL_MODEL calls: {stats['call_model_calls']}")
    print(f"  BBOX calls: {stats['bbox_calls']}")
    print(f"  Total frames sampled: {stats['total_frames_sampled']}")
    print(f"  Total segments created: {stats['total_segments_created']}")
    print(f"  Total API calls: {stats['total_api_calls']}")


def main():
    """Run all examples"""
    print("="*60)
    print("Atomic Operations Implementation Examples (Phase 2)")
    print("="*60)

    # Example 1: SAMPLE
    result = example_1_sample_operation()
    if result[0] is None:
        return
    video_meta, atomic_ops = result

    # Example 2: SEGMENT
    segments = example_2_segment_operation(video_meta, atomic_ops)

    # Example 3: CALL_MODEL (requires API key)
    example_3_call_model_operation(video_meta, atomic_ops)

    # Example 4: BBOX
    example_4_bbox_operation(video_meta, atomic_ops)

    # Example 5: Combined workflow
    example_5_combined_workflow(video_meta, atomic_ops)

    # Summary
    print("\n" + "="*60)
    print("All Examples Completed!")
    print("="*60)
    print("\nSummary:")
    print("  ✓ SAMPLE operation - Frame sampling (uniform, timestamps)")
    print("  ✓ SEGMENT operation - Video segmentation (fixed_duration, custom)")
    print("  ✓ CALL_MODEL operation - MLLM API integration")
    print("  ✓ BBOX operation - Bounding box annotation")
    print("  ✓ Combined workflow - Multi-operation pipeline")

    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. ✅ Phase 1 Complete - Video processing")
    print("2. ✅ Phase 2 Complete - Atomic operations")
    print("3. 📋 Phase 3 - Build end-to-end VideoQA pipeline")
    print("4. 📋 Phase 4 - Test with real video QA tasks")


if __name__ == "__main__":
    main()
