"""
Video QA Pipeline Example

Demonstrates Phase 3: End-to-End Video Question Answering Pipeline

This is the complete workflow:
1. Input: Video file + Question
2. Extract metadata
3. Segment video
4. Sample & analyze each segment
5. Aggregate understanding
6. Answer question
7. Output: Answer + Experiment metrics

Usage:
    # Without API key (dry run):
    python examples/video_qa_pipeline_example.py

    # With API key (full run):
    export OPENAI_API_KEY='your-key'
    python examples/video_qa_pipeline_example.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from processors import (
    VideoProcessor,
    AtomicOperationsImplementation,
    VideoQAPipeline,
    print_video_info
)


def example_1_basic_qa():
    """Example 1: Basic Video QA"""
    print("\n" + "="*60)
    print("Example 1: Basic Video QA Pipeline")
    print("="*60)

    # Check if test video exists
    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"\n⚠ Video file not found: {video_path}")
        return

    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ OPENAI_API_KEY not set - running in dry-run mode")
        print("Set API key: export OPENAI_API_KEY='your-key'")
        print("\nNote: Pipeline will still run but MLLM calls will fail gracefully")

    # Create pipeline components
    print("\nInitializing pipeline...")
    video_processor = VideoProcessor()
    atomic_ops = AtomicOperationsImplementation(video_processor=video_processor)

    # Create pipeline with configuration
    pipeline = VideoQAPipeline(
        atomic_ops=atomic_ops,
        config={
            "segment_duration_sec": 60.0,  # 60s segments for faster processing
            "frames_per_segment": 3,        # 3 frames per segment
            "max_segments": 3,              # Process only first 3 segments
            "mllm_model": os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4-turbo-preview"),  # Use configured model
            "temperature": 0.7,
            "max_tokens_per_segment": 4000,  # 设置足够大的上限，不限制模型输出
            "max_tokens_qa": 3000            # QA设置足够大的上限
        }
    )

    print("✓ Pipeline initialized")
    print(f"  Config: {pipeline.get_config()}")

    # Define question
    question = "What is happening in this video? Describe the main content and activities."

    # Run pipeline
    print(f"\n{'='*60}")
    print(f"Running Video QA Pipeline")
    print(f"{'='*60}")
    print(f"Video: {video_path}")
    print(f"Question: {question}")
    print(f"{'='*60}")

    try:
        answer, experiment = pipeline.run_video_qa(
            video_path=video_path,
            question=question
        )

        # Display results
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)

        print(f"\nQuestion: {question}")
        print(f"\nAnswer:\n{answer}")

        print(f"\n{'='*60}")
        print("Experiment Metrics")
        print(f"{'='*60}")
        print(f"Run ID: {experiment.run_id}")
        print(f"Video ID: {experiment.video_meta.video_id if experiment.video_meta else 'N/A'}")
        print(f"Status: {experiment.status.value}")
        print(f"Processing time: {(experiment.total_duration_ms / 1000):.2f}s" if experiment.total_duration_ms else "N/A")
        print(f"\nVideo Info:")
        print(f"  Segments processed: {len(experiment.segments)}")
        print(f"  Frames processed: {len(experiment.frames)}")
        print(f"\nAPI Usage:")
        print(f"  Total API calls: {experiment.total_api_calls}")
        print(f"  Total tokens: {experiment.total_tokens_used}")
        print(f"  Estimated cost: ${experiment.total_cost_usd:.4f}")

        print(f"\n✓ Pipeline completed successfully!")

        return answer, experiment

    except Exception as e:
        print(f"\n✗ Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def example_2_custom_config():
    """Example 2: Custom Pipeline Configuration"""
    print("\n" + "="*60)
    print("Example 2: Custom Configuration")
    print("="*60)

    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"\n⚠ Video file not found: {video_path}")
        return

    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ Skipping (requires OPENAI_API_KEY)")
        return

    # Create pipeline with different configuration
    video_processor = VideoProcessor()
    atomic_ops = AtomicOperationsImplementation(video_processor=video_processor)

    # Configuration for detailed analysis
    pipeline = VideoQAPipeline(
        atomic_ops=atomic_ops,
        config={
            "segment_duration_sec": 30.0,   # Shorter segments
            "frames_per_segment": 5,         # More frames per segment
            "max_segments": 5,               # More segments
            "temperature": 0.5,              # Lower temperature for more focused answers
            "max_tokens_per_segment": 400,
            "max_tokens_qa": 800
        }
    )

    question = "What are the key events in chronological order?"

    print(f"\nRunning with detailed analysis config...")
    print(f"Question: {question}")

    try:
        answer, experiment = pipeline.run_video_qa(video_path, question)

        print(f"\n✓ Answer: {answer[:200]}...")
        print(f"✓ Cost: ${experiment.total_cost_usd:.4f}")

    except Exception as e:
        print(f"\n✗ Failed: {str(e)}")


def example_3_multiple_questions():
    """Example 3: Multiple Questions on Same Video"""
    print("\n" + "="*60)
    print("Example 3: Multiple Questions")
    print("="*60)

    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"\n⚠ Video file not found: {video_path}")
        return

    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ Skipping (requires OPENAI_API_KEY)")
        return

    # Questions to ask
    questions = [
        "What is the main topic of this video?",
        "Who are the key people or characters?",
        "What happens at the beginning, middle, and end?"
    ]

    # Create pipeline
    video_processor = VideoProcessor()
    atomic_ops = AtomicOperationsImplementation(video_processor=video_processor)
    pipeline = VideoQAPipeline(
        atomic_ops=atomic_ops,
        config={
            "segment_duration_sec": 60.0,
            "frames_per_segment": 3,
            "max_segments": 2  # Quick processing for demo
        }
    )

    print(f"\nAsking {len(questions)} questions about the video...")

    results = []
    for i, question in enumerate(questions, 1):
        print(f"\n--- Question {i}/{len(questions)} ---")
        print(f"Q: {question}")

        try:
            answer, experiment = pipeline.run_video_qa(video_path, question)
            print(f"A: {answer[:150]}...")
            print(f"   Cost: ${experiment.total_cost_usd:.4f}")

            results.append((question, answer, experiment))

        except Exception as e:
            print(f"   Failed: {str(e)}")

    # Summary
    if results:
        total_cost = sum(exp.total_cost_usd for _, _, exp in results)
        total_time = sum((exp.total_duration_ms / 1000) if exp.total_duration_ms else 0 for _, _, exp in results)
        print(f"\n{'='*60}")
        print(f"Summary")
        print(f"{'='*60}")
        print(f"Questions answered: {len(results)}")
        print(f"Total cost: ${total_cost:.4f}")
        print(f"Total time: {total_time:.2f}s")


def example_4_video_metadata_preview():
    """Example 4: Preview Video Metadata Before Processing"""
    print("\n" + "="*60)
    print("Example 4: Preview Video Metadata")
    print("="*60)

    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"\n⚠ Video file not found: {video_path}")
        return

    # Just extract and display metadata
    video_processor = VideoProcessor()
    video_meta = video_processor.extract_metadata(video_path)

    print_video_info(video_meta)

    # Estimate processing
    segment_duration = 60.0
    frames_per_segment = 3
    num_segments = int(video_meta.duration_sec / segment_duration) + 1

    print(f"\n{'='*60}")
    print("Processing Estimates")
    print(f"{'='*60}")
    print(f"Segment duration: {segment_duration}s")
    print(f"Frames per segment: {frames_per_segment}")
    print(f"Total segments: {num_segments}")
    print(f"Total frames to process: {num_segments * frames_per_segment}")
    print(f"\nEstimated API calls: {num_segments + 1}")  # segment analysis + final QA
    print(f"Estimated tokens (rough): ~{(num_segments * 500) + 1000}")
    print(f"Estimated cost (rough): $0.01 - $0.05")
    print(f"Estimated time: {num_segments * 3}s - {num_segments * 5}s")


def main():
    """Run all examples"""
    print("="*60)
    print("Video QA Pipeline Examples (Phase 3)")
    print("="*60)

    # Example 4: Preview metadata first
    example_4_video_metadata_preview()

    # Example 1: Basic QA (always runs, handles missing API key gracefully)
    result = example_1_basic_qa()

    if os.getenv("OPENAI_API_KEY"):
        # Example 2: Custom config (requires API key)
        # example_2_custom_config()

        # Example 3: Multiple questions (requires API key)
        # example_3_multiple_questions()

        print("\n" + "="*60)
        print("Note: Examples 2 & 3 are commented out to save API costs")
        print("Uncomment in main() to run them")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("Set OPENAI_API_KEY to run full examples with MLLM")
        print("="*60)

    # Final summary
    print("\n" + "="*60)
    print("Examples Completed!")
    print("="*60)
    print("\nWhat we demonstrated:")
    print("  ✓ End-to-end video QA pipeline")
    print("  ✓ Automatic video segmentation & frame sampling")
    print("  ✓ MLLM-based segment analysis")
    print("  ✓ Question answering based on full video understanding")
    print("  ✓ Complete experiment tracking (API calls, tokens, cost)")

    print("\n" + "="*60)
    print("Phase 3 Complete!")
    print("="*60)
    print("1. ✅ Phase 1 - Video processing")
    print("2. ✅ Phase 2 - Atomic operations")
    print("3. ✅ Phase 3 - End-to-end VideoQA pipeline")
    print("4. 📋 Phase 4 - Real-world testing & optimization")


if __name__ == "__main__":
    main()
