"""
Video Processor Module

Implements basic video processing operations:
- Video metadata extraction
- Video segmentation
- Frame sampling

Dependencies: opencv-python (cv2)
"""

import os
import uuid
import cv2
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

# Import project dependencies
import sys
from pathlib import Path as PathLib
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from experiments import (
    VideoMeta,
    Segment,
    Frame,
    TimeSpan,
    VideoFormat
)


class VideoProcessorError(Exception):
    """Video processor specific errors"""
    pass


class VideoProcessor:
    """
    Video Processor

    Handles basic video processing operations:
    1. Extract video metadata
    2. Segment video into clips
    3. Sample frames from video/segments

    Uses opencv-python (cv2) for video I/O
    """

    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize Video Processor

        Args:
            temp_dir: Directory to save temporary frame images
                     Defaults to data/temp/frames/
        """
        if temp_dir is None:
            # Use project's data/temp directory
            project_root = PathLib(__file__).parent.parent
            self.temp_dir = project_root / "data" / "temp" / "frames"
        else:
            self.temp_dir = PathLib(temp_dir)

        # Create temp directory if not exists
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            "videos_processed": 0,
            "frames_extracted": 0,
            "segments_created": 0
        }

    def extract_metadata(self, video_path: str) -> VideoMeta:
        """
        Extract video metadata using opencv

        Args:
            video_path: Path to video file

        Returns:
            VideoMeta object with video information

        Raises:
            VideoProcessorError: If video cannot be opened or read
        """
        if not os.path.exists(video_path):
            raise VideoProcessorError(f"Video file not found: {video_path}")

        # Open video with opencv
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise VideoProcessorError(f"Cannot open video file: {video_path}")

        try:
            # Extract metadata
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Calculate duration
            duration_sec = frame_count / fps if fps > 0 else 0.0

            # Detect format from file extension
            file_ext = os.path.splitext(video_path)[1].lower()
            format_map = {
                '.mp4': VideoFormat.MP4,
                '.avi': VideoFormat.AVI,
                '.mov': VideoFormat.MOV,
                '.mkv': VideoFormat.MKV,
                '.webm': VideoFormat.WEBM
            }
            video_format = format_map.get(file_ext, VideoFormat.OTHER)

            # Get file size in MB
            file_size_bytes = os.path.getsize(video_path)
            file_size_mb = file_size_bytes / (1024 * 1024)

            # Create VideoMeta
            video_meta = VideoMeta(
                video_id=f"vid_{uuid.uuid4().hex[:8]}",
                file_path=str(Path(video_path).absolute()),
                duration_sec=duration_sec,
                fps=fps,
                num_frames=frame_count,
                width=width,
                height=height,
                format=video_format,
                file_size_mb=file_size_mb,
                source=os.path.basename(video_path)
            )

            self.stats["videos_processed"] += 1

            return video_meta

        finally:
            cap.release()

    def segment_video_fixed_duration(
        self,
        video_meta: VideoMeta,
        duration_sec: float = 10.0
    ) -> List[Segment]:
        """
        Segment video by fixed duration

        Args:
            video_meta: Video metadata
            duration_sec: Duration of each segment in seconds

        Returns:
            List of Segment objects
        """
        segments = []
        total_duration = video_meta.duration_sec
        current_time = 0.0
        segment_index = 0

        while current_time < total_duration:
            # Calculate segment end time
            end_time = min(current_time + duration_sec, total_duration)

            # Calculate frame indices
            start_frame = int(current_time * video_meta.fps)
            end_frame = int(end_time * video_meta.fps)
            num_frames = end_frame - start_frame

            # Create segment
            segment = Segment(
                segment_id=f"{video_meta.video_id}_seg_{segment_index:03d}",
                video_id=video_meta.video_id,
                time_span=TimeSpan(start_sec=current_time, end_sec=end_time),
                segment_index=segment_index,
                total_segments=0,  # Will update later
                start_frame=start_frame,
                end_frame=end_frame,
                num_frames=num_frames
            )

            segments.append(segment)

            current_time = end_time
            segment_index += 1

        # Update total_segments for all segments
        total_segments = len(segments)
        for seg in segments:
            seg.total_segments = total_segments

        self.stats["segments_created"] += len(segments)

        return segments

    def segment_video_custom(
        self,
        video_meta: VideoMeta,
        breakpoints: List[float]
    ) -> List[Segment]:
        """
        Segment video by custom breakpoints

        Args:
            video_meta: Video metadata
            breakpoints: List of time points (seconds) to split at
                        e.g., [10.0, 25.0, 40.0] creates 4 segments

        Returns:
            List of Segment objects
        """
        # Sort breakpoints and add boundaries
        time_points = sorted([0.0] + breakpoints + [video_meta.duration_sec])

        # Remove duplicates
        time_points = sorted(list(set(time_points)))

        segments = []
        for i in range(len(time_points) - 1):
            start_time = time_points[i]
            end_time = time_points[i + 1]

            # Calculate frame indices
            start_frame = int(start_time * video_meta.fps)
            end_frame = int(end_time * video_meta.fps)
            num_frames = end_frame - start_frame

            segment = Segment(
                segment_id=f"{video_meta.video_id}_seg_{i:03d}",
                video_id=video_meta.video_id,
                time_span=TimeSpan(start_sec=start_time, end_sec=end_time),
                segment_index=i,
                total_segments=len(time_points) - 1,
                start_frame=start_frame,
                end_frame=end_frame,
                num_frames=num_frames
            )

            segments.append(segment)

        self.stats["segments_created"] += len(segments)

        return segments

    def sample_frames_uniform(
        self,
        video_path: str,
        video_meta: VideoMeta,
        num_frames: int,
        segment: Optional[Segment] = None
    ) -> List[Frame]:
        """
        Sample frames uniformly from video or segment

        Args:
            video_path: Path to video file
            video_meta: Video metadata
            num_frames: Number of frames to sample
            segment: Optional segment to sample from (if None, sample from entire video)

        Returns:
            List of Frame objects with image_path set
        """
        if not os.path.exists(video_path):
            raise VideoProcessorError(f"Video file not found: {video_path}")

        # Determine time range
        if segment:
            start_sec = segment.time_span.start_sec
            end_sec = segment.time_span.end_sec
            segment_id = segment.segment_id
        else:
            start_sec = 0.0
            end_sec = video_meta.duration_sec
            segment_id = None

        duration = end_sec - start_sec

        if duration <= 0:
            raise VideoProcessorError(f"Invalid time range: {start_sec} - {end_sec}")

        if num_frames <= 0:
            raise VideoProcessorError(f"Invalid num_frames: {num_frames}")

        # Calculate uniform sampling timestamps
        if num_frames == 1:
            # Sample from middle
            timestamps = [start_sec + duration / 2]
        else:
            # Uniformly distributed
            interval = duration / (num_frames - 1) if num_frames > 1 else duration
            timestamps = [start_sec + i * interval for i in range(num_frames)]

        # Extract frames at timestamps
        frames = self.extract_frames_at_timestamps(
            video_path=video_path,
            video_meta=video_meta,
            timestamps=timestamps,
            segment_id=segment_id
        )

        return frames

    def extract_frames_at_timestamps(
        self,
        video_path: str,
        video_meta: VideoMeta,
        timestamps: List[float],
        segment_id: Optional[str] = None
    ) -> List[Frame]:
        """
        Extract frames at specific timestamps

        Args:
            video_path: Path to video file
            video_meta: Video metadata
            timestamps: List of timestamps in seconds
            segment_id: Optional segment ID to associate with frames

        Returns:
            List of Frame objects with saved images
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise VideoProcessorError(f"Cannot open video file: {video_path}")

        frames = []

        try:
            for timestamp in timestamps:
                # Set video position to timestamp
                cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)

                # Read frame
                ret, frame_image = cap.read()

                if not ret:
                    print(f"Warning: Could not read frame at {timestamp}s")
                    continue

                # Calculate frame index
                frame_index = int(timestamp * video_meta.fps)

                # Generate unique frame ID
                frame_id = f"{video_meta.video_id}_frame_{frame_index:06d}"

                # Save frame to temp directory
                image_filename = f"{frame_id}.jpg"
                image_path = self.temp_dir / image_filename

                # Save image
                cv2.imwrite(str(image_path), frame_image)

                # Create Frame object
                frame = Frame(
                    frame_id=frame_id,
                    video_id=video_meta.video_id,
                    segment_id=segment_id,
                    frame_index=frame_index,
                    timestamp_sec=timestamp,
                    image_path=str(image_path),
                    width=frame_image.shape[1],
                    height=frame_image.shape[0]
                )

                frames.append(frame)
                self.stats["frames_extracted"] += 1

        finally:
            cap.release()

        return frames

    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics"""
        return self.stats.copy()

    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "videos_processed": 0,
            "frames_extracted": 0,
            "segments_created": 0
        }

    def cleanup_temp_files(self, video_id: Optional[str] = None):
        """
        Clean up temporary frame files

        Args:
            video_id: If provided, only delete frames for this video
                     If None, delete all temporary files
        """
        if video_id:
            # Delete frames for specific video
            pattern = f"{video_id}_frame_*.jpg"
            for file_path in self.temp_dir.glob(pattern):
                try:
                    file_path.unlink()
                except Exception as e:
                    print(f"Warning: Could not delete {file_path}: {e}")
        else:
            # Delete all frame files
            for file_path in self.temp_dir.glob("*.jpg"):
                try:
                    file_path.unlink()
                except Exception as e:
                    print(f"Warning: Could not delete {file_path}: {e}")


def print_video_info(video_meta: VideoMeta):
    """Helper function to print video metadata"""
    print("\n" + "="*60)
    print("Video Metadata")
    print("="*60)
    print(f"Video ID: {video_meta.video_id}")
    print(f"File: {video_meta.source if video_meta.source else os.path.basename(video_meta.file_path)}")
    print(f"Path: {video_meta.file_path}")
    print(f"Duration: {video_meta.duration_sec:.2f}s")
    print(f"FPS: {video_meta.fps:.2f}")
    print(f"Frames: {video_meta.num_frames}")
    print(f"Resolution: {video_meta.width}x{video_meta.height}")
    print(f"Format: {video_meta.format.value}")
    if video_meta.file_size_mb:
        print(f"Size: {video_meta.file_size_mb:.2f} MB")
    print("="*60)


def print_segments_info(segments: List[Segment]):
    """Helper function to print segment information"""
    print("\n" + "="*60)
    print(f"Video Segments ({len(segments)} total)")
    print("="*60)
    for seg in segments:
        duration = seg.time_span.end_sec - seg.time_span.start_sec
        print(f"Segment {seg.segment_index}: "
              f"[{seg.time_span.start_sec:.2f}s - {seg.time_span.end_sec:.2f}s] "
              f"({duration:.2f}s, {seg.num_frames} frames)")
    print("="*60)


def print_frames_info(frames: List[Frame]):
    """Helper function to print frame information"""
    print("\n" + "="*60)
    print(f"Extracted Frames ({len(frames)} total)")
    print("="*60)
    for frame in frames:
        print(f"Frame {frame.frame_index}: "
              f"t={frame.timestamp_sec:.2f}s, "
              f"{frame.width}x{frame.height}, "
              f"saved to {Path(frame.image_path).name}")
    print("="*60)
