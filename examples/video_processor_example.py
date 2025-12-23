"""
Video Processor Example

Demonstrates Phase 1 video processing capabilities:
1. Extract video metadata
2. Segment video (fixed duration)
3. Sample frames uniformly

Usage:
    python examples/video_processor_example.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from processors import (
    VideoProcessor,
    print_video_info,
    print_segments_info,
    print_frames_info
)


def example_1_extract_metadata():
    """Example 1: Extract video metadata"""
    print("\n" + "="*60)
    print("Example 1: Extract Video Metadata")
    print("="*60)

    # Check if test video exists
    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"\n⚠ Video file not found: {video_path}")
        print("Please place a video file at data/videos/source.mp4")
        return None

    # Create processor
    processor = VideoProcessor()

    # Extract metadata
    print(f"\nExtracting metadata from: {video_path}")
    video_meta = processor.extract_metadata(video_path)

    # Print information
    print_video_info(video_meta)

    print(f"\n✓ Metadata extraction successful!")
    return video_meta, processor


def example_2_segment_video(video_meta, processor):
    """Example 2: Segment video by fixed duration"""
    print("\n" + "="*60)
    print("Example 2: Segment Video (Fixed Duration)")
    print("="*60)

    # Segment video into 10-second clips
    duration_sec = 10.0
    print(f"\nSegmenting video into {duration_sec}s clips...")

    segments = processor.segment_video_fixed_duration(
        video_meta=video_meta,
        duration_sec=duration_sec
    )

    # Print segment information
    print_segments_info(segments)

    print(f"\n✓ Created {len(segments)} segments!")
    return segments


def example_3_sample_frames(video_meta, segments, processor):
    """Example 3: Sample frames uniformly"""
    print("\n" + "="*60)
    print("Example 3: Sample Frames (Uniform)")
    print("="*60)

    # Sample from entire video
    print(f"\n--- Sampling from entire video ---")
    num_frames = 5
    print(f"Extracting {num_frames} frames uniformly from entire video...")

    frames_full = processor.sample_frames_uniform(
        video_path=video_meta.file_path,
        video_meta=video_meta,
        num_frames=num_frames
    )

    print_frames_info(frames_full)

    # Sample from first segment
    if segments:
        print(f"\n--- Sampling from first segment ---")
        first_segment = segments[0]
        num_frames_seg = 3
        print(f"Extracting {num_frames_seg} frames from segment 0 "
              f"[{first_segment.time_span.start_sec:.2f}s - {first_segment.time_span.end_sec:.2f}s]...")

        frames_segment = processor.sample_frames_uniform(
            video_path=video_meta.file_path,
            video_meta=video_meta,
            num_frames=num_frames_seg,
            segment=first_segment
        )

        print_frames_info(frames_segment)

    print(f"\n✓ Frame sampling successful!")
    return frames_full


def example_4_custom_segmentation(video_meta, processor):
    """Example 4: Custom segmentation with breakpoints"""
    print("\n" + "="*60)
    print("Example 4: Custom Segmentation")
    print("="*60)

    # Define custom breakpoints
    breakpoints = [15.0, 30.0, 50.0]  # Split at 15s, 30s, 50s
    print(f"\nSegmenting video at custom breakpoints: {breakpoints}")

    segments = processor.segment_video_custom(
        video_meta=video_meta,
        breakpoints=breakpoints
    )

    print_segments_info(segments)

    print(f"\n✓ Custom segmentation successful!")
    return segments


def example_5_extract_at_timestamps(video_meta, processor):
    """Example 5: Extract frames at specific timestamps"""
    print("\n" + "="*60)
    print("Example 5: Extract Frames at Specific Timestamps")
    print("="*60)

    # Define specific timestamps to extract
    timestamps = [5.0, 15.0, 25.0, 35.0, 45.0]  # Extract at 5s, 15s, 25s, 35s, 45s
    print(f"\nExtracting frames at timestamps: {timestamps}")

    frames = processor.extract_frames_at_timestamps(
        video_path=video_meta.file_path,
        video_meta=video_meta,
        timestamps=timestamps
    )

    print_frames_info(frames)

    print(f"\n✓ Timestamp extraction successful!")
    return frames


def example_6_processor_stats(processor):
    """Example 6: Show processor statistics"""
    print("\n" + "="*60)
    print("Example 6: Processor Statistics")
    print("="*60)

    stats = processor.get_stats()
    print(f"\nVideo Processor Statistics:")
    print(f"  Videos processed: {stats['videos_processed']}")
    print(f"  Segments created: {stats['segments_created']}")
    print(f"  Frames extracted: {stats['frames_extracted']}")

    print(f"\n✓ Statistics retrieved!")


def main():
    """Run all examples"""
    print("="*60)
    print("Video Processor Examples (Phase 1)")
    print("="*60)

    # Example 1: Extract metadata
    result = example_1_extract_metadata()
    if result is None:
        return

    video_meta, processor = result

    # Example 2: Segment video
    segments = example_2_segment_video(video_meta, processor)

    # Example 3: Sample frames
    frames = example_3_sample_frames(video_meta, segments, processor)

    # Example 4: Custom segmentation
    custom_segments = example_4_custom_segmentation(video_meta, processor)

    # Example 5: Extract at timestamps
    timestamp_frames = example_5_extract_at_timestamps(video_meta, processor)

    # Example 6: Show statistics
    example_6_processor_stats(processor)

    # Summary
    print("\n" + "="*60)
    print("All Examples Completed Successfully!")
    print("="*60)
    print("\nSummary:")
    print(f"  ✓ Extracted metadata from video")
    print(f"  ✓ Created {len(segments)} segments (fixed duration)")
    print(f"  ✓ Created {len(custom_segments)} segments (custom breakpoints)")
    print(f"  ✓ Extracted {len(frames)} frames (uniform sampling)")
    print(f"  ✓ Extracted {len(timestamp_frames)} frames (specific timestamps)")
    print(f"\n  Total frames saved to: {processor.temp_dir}")

    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. ✅ Phase 1 Complete - Video processing works!")
    print("2. 📋 Phase 2 - Implement atomic operations")
    print("3. 📋 Phase 3 - Build end-to-end pipeline")
    print("4. 📋 Phase 4 - Test with actual MLLM API")

    # Cleanup option
    print("\n" + "="*60)
    print("Cleanup")
    print("="*60)
    print(f"Temporary frames are saved in: {processor.temp_dir}")
    print("To clean up, run: processor.cleanup_temp_files()")


if __name__ == "__main__":
    main()
