"""
Atomic Operations Implementation

Implements the 4 core atomic operations:
- SAMPLE: Frame sampling from video/segment
- SEGMENT: Video segmentation
- CALL_MODEL: Model invocation (MLLM, ASR)
- BBOX: Bounding box annotation

This module bridges the gap between atomic operation definitions
and actual implementation using VideoProcessor and MLLMClient.
"""

import os
import uuid
import time
import cv2
from typing import Dict, Any, List, Union, Optional
from datetime import datetime
from pathlib import Path

# Import project dependencies
import sys
from pathlib import Path as PathLib
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from experiments import (
    VideoMeta,
    Segment,
    Frame,
    ModelResponse,
    MLLMRequest,
    MLLMResponse,
    AnalysisTask,
    AtomicOperations
)

from agents import MLLMClient, MLLMClientConfig
from processors import VideoProcessor, VideoProcessorError


class AtomicOperationError(Exception):
    """Atomic operation specific errors"""
    pass


class AtomicOperationsImplementation:
    """
    Atomic Operations Implementation

    Implements the 4 core atomic operations defined in the system:
    1. SAMPLE - Frame sampling
    2. SEGMENT - Video segmentation
    3. CALL_MODEL - Model invocation
    4. BBOX - Bounding box annotation

    This class connects high-level atomic operation definitions
    with low-level implementations (VideoProcessor, MLLMClient).
    """

    def __init__(
        self,
        video_processor: Optional[VideoProcessor] = None,
        mllm_client: Optional[MLLMClient] = None
    ):
        """
        Initialize Atomic Operations Implementation

        Args:
            video_processor: VideoProcessor instance for video operations
                           If None, creates a default instance
            mllm_client: MLLMClient instance for MLLM API calls
                        If None, creates a default instance (requires API key)
        """
        # Video processor
        if video_processor is None:
            self.video_processor = VideoProcessor()
        else:
            self.video_processor = video_processor

        # MLLM client
        if mllm_client is None:
            # Create default MLLM client (requires API key in env)
            self.mllm_client = MLLMClient(MLLMClientConfig())
        else:
            self.mllm_client = mllm_client

        # Statistics
        self.stats = {
            "sample_calls": 0,
            "segment_calls": 0,
            "call_model_calls": 0,
            "bbox_calls": 0,
            "total_frames_sampled": 0,
            "total_segments_created": 0,
            "total_api_calls": 0
        }

    # ==================== SAMPLE Operation ====================

    def sample(
        self,
        source: Union[VideoMeta, Segment],
        method: str,
        params: Dict[str, Any]
    ) -> List[Frame]:
        """
        SAMPLE - Frame sampling atomic operation

        Extract frames from video or segment using specified method.

        Args:
            source: VideoMeta or Segment to sample from
            method: Sampling method ("uniform", "keyframe", "timestamps")
            params: Method-specific parameters

        Returns:
            List[Frame]: Sampled frames with image_path set

        Raises:
            AtomicOperationError: If sampling fails

        Examples:
            >>> # Uniform sampling
            >>> frames = impl.sample(
            ...     source=video_meta,
            ...     method="uniform",
            ...     params={"num_frames": 10}
            ... )

            >>> # Timestamps sampling
            >>> frames = impl.sample(
            ...     source=segment,
            ...     method="timestamps",
            ...     params={"timestamps": [0, 5.0, 10.0]}
            ... )
        """
        self.stats["sample_calls"] += 1

        try:
            # Get video path and determine if sampling from segment
            if isinstance(source, VideoMeta):
                video_path = source.file_path
                video_meta = source
                segment = None
            elif isinstance(source, Segment):
                # Need to get video_meta from somewhere
                # For now, assume video_path is accessible
                # In practice, should pass video_meta along with segment
                raise AtomicOperationError(
                    "Segment source requires video_meta to be provided. "
                    "Please use VideoMeta as source or implement segment-based sampling."
                )
            else:
                raise AtomicOperationError(f"Invalid source type: {type(source)}")

            # Execute sampling based on method
            if method == "uniform":
                frames = self._sample_uniform(video_path, video_meta, segment, params)

            elif method == "keyframe":
                frames = self._sample_keyframe(video_path, video_meta, segment, params)

            elif method == "timestamps":
                frames = self._sample_timestamps(video_path, video_meta, segment, params)

            else:
                raise AtomicOperationError(f"Unknown sampling method: {method}")

            self.stats["total_frames_sampled"] += len(frames)
            return frames

        except VideoProcessorError as e:
            raise AtomicOperationError(f"Video processing error in SAMPLE: {str(e)}")
        except Exception as e:
            raise AtomicOperationError(f"Unexpected error in SAMPLE: {str(e)}")

    def _sample_uniform(
        self,
        video_path: str,
        video_meta: VideoMeta,
        segment: Optional[Segment],
        params: Dict[str, Any]
    ) -> List[Frame]:
        """Uniform sampling implementation"""
        num_frames = params.get("num_frames")
        if num_frames is None:
            raise AtomicOperationError("uniform sampling requires 'num_frames' parameter")

        return self.video_processor.sample_frames_uniform(
            video_path=video_path,
            video_meta=video_meta,
            num_frames=num_frames,
            segment=segment
        )

    def _sample_keyframe(
        self,
        video_path: str,
        video_meta: VideoMeta,
        segment: Optional[Segment],
        params: Dict[str, Any]
    ) -> List[Frame]:
        """Keyframe sampling implementation (placeholder)"""
        # TODO: Implement actual keyframe detection
        # For now, fall back to uniform sampling
        threshold = params.get("threshold", 0.3)
        max_frames = params.get("max_frames", 20)

        print(f"Warning: keyframe sampling not fully implemented. "
              f"Using uniform sampling with max_frames={max_frames}")

        return self.video_processor.sample_frames_uniform(
            video_path=video_path,
            video_meta=video_meta,
            num_frames=max_frames,
            segment=segment
        )

    def _sample_timestamps(
        self,
        video_path: str,
        video_meta: VideoMeta,
        segment: Optional[Segment],
        params: Dict[str, Any]
    ) -> List[Frame]:
        """Timestamps sampling implementation"""
        timestamps = params.get("timestamps")
        if timestamps is None:
            raise AtomicOperationError("timestamps sampling requires 'timestamps' parameter")

        segment_id = segment.segment_id if segment else None

        return self.video_processor.extract_frames_at_timestamps(
            video_path=video_path,
            video_meta=video_meta,
            timestamps=timestamps,
            segment_id=segment_id
        )

    # ==================== SEGMENT Operation ====================

    def segment(
        self,
        video_meta: VideoMeta,
        strategy: str,
        params: Dict[str, Any]
    ) -> List[Segment]:
        """
        SEGMENT - Video segmentation atomic operation

        Segment video into multiple clips using specified strategy.

        Args:
            video_meta: Video metadata
            strategy: Segmentation strategy ("fixed_duration", "scene_change", "custom")
            params: Strategy-specific parameters

        Returns:
            List[Segment]: Segmented video clips

        Raises:
            AtomicOperationError: If segmentation fails

        Examples:
            >>> # Fixed duration segmentation
            >>> segments = impl.segment(
            ...     video_meta=video_meta,
            ...     strategy="fixed_duration",
            ...     params={"duration_sec": 30.0}
            ... )

            >>> # Custom breakpoints
            >>> segments = impl.segment(
            ...     video_meta=video_meta,
            ...     strategy="custom",
            ...     params={"breakpoints": [0, 60, 120, 180]}
            ... )
        """
        self.stats["segment_calls"] += 1

        try:
            # Execute segmentation based on strategy
            if strategy == "fixed_duration":
                segments = self._segment_fixed_duration(video_meta, params)

            elif strategy == "scene_change":
                segments = self._segment_scene_change(video_meta, params)

            elif strategy == "custom":
                segments = self._segment_custom(video_meta, params)

            else:
                raise AtomicOperationError(f"Unknown segmentation strategy: {strategy}")

            self.stats["total_segments_created"] += len(segments)
            return segments

        except VideoProcessorError as e:
            raise AtomicOperationError(f"Video processing error in SEGMENT: {str(e)}")
        except Exception as e:
            raise AtomicOperationError(f"Unexpected error in SEGMENT: {str(e)}")

    def _segment_fixed_duration(
        self,
        video_meta: VideoMeta,
        params: Dict[str, Any]
    ) -> List[Segment]:
        """Fixed duration segmentation implementation"""
        duration_sec = params.get("duration_sec")
        if duration_sec is None:
            raise AtomicOperationError("fixed_duration strategy requires 'duration_sec' parameter")

        return self.video_processor.segment_video_fixed_duration(
            video_meta=video_meta,
            duration_sec=duration_sec
        )

    def _segment_scene_change(
        self,
        video_meta: VideoMeta,
        params: Dict[str, Any]
    ) -> List[Segment]:
        """Scene change segmentation implementation (placeholder)"""
        # TODO: Implement actual scene change detection
        threshold = params.get("threshold", 0.3)
        min_duration = params.get("min_duration", 10.0)

        print(f"Warning: scene_change segmentation not fully implemented. "
              f"Using fixed_duration={min_duration}s")

        return self.video_processor.segment_video_fixed_duration(
            video_meta=video_meta,
            duration_sec=min_duration
        )

    def _segment_custom(
        self,
        video_meta: VideoMeta,
        params: Dict[str, Any]
    ) -> List[Segment]:
        """Custom breakpoints segmentation implementation"""
        breakpoints = params.get("breakpoints")
        if breakpoints is None:
            raise AtomicOperationError("custom strategy requires 'breakpoints' parameter")

        return self.video_processor.segment_video_custom(
            video_meta=video_meta,
            breakpoints=breakpoints
        )

    # ==================== CALL_MODEL Operation ====================

    def call_model(
        self,
        model_type: str,
        model_name: str,
        inputs: Dict[str, Any],
        params: Dict[str, Any]
    ) -> ModelResponse:
        """
        CALL_MODEL - Model invocation atomic operation

        Call MLLM or ASR models with unified interface.

        Args:
            model_type: Model type ("mllm" or "asr")
            model_name: Specific model name (e.g., "gpt-4-vision-preview")
            inputs: Model-specific inputs
            params: Model parameters (temperature, max_tokens, etc.)

        Returns:
            ModelResponse: Unified model response

        Raises:
            AtomicOperationError: If model call fails

        Examples:
            >>> # MLLM call
            >>> response = impl.call_model(
            ...     model_type="mllm",
            ...     model_name="gpt-4-vision-preview",
            ...     inputs={
            ...         "prompt": "Describe this video",
            ...         "frames": [frame1, frame2, frame3]
            ...     },
            ...     params={"temperature": 0.7, "max_tokens": 500}
            ... )
        """
        self.stats["call_model_calls"] += 1
        self.stats["total_api_calls"] += 1

        try:
            if model_type == "mllm":
                return self._call_mllm(model_name, inputs, params)

            elif model_type == "asr":
                return self._call_asr(model_name, inputs, params)

            else:
                raise AtomicOperationError(f"Unknown model type: {model_type}")

        except Exception as e:
            # Return error response instead of raising
            return ModelResponse(
                response_id=f"resp_{uuid.uuid4().hex[:8]}",
                request_id="",
                model_type=model_type,
                model_name=model_name,
                success=False,
                error_message=str(e),
                output="",
                total_tokens=0,
                cost_usd=0.0,
                response_time_ms=0.0
            )

    def _call_mllm(
        self,
        model_name: str,
        inputs: Dict[str, Any],
        params: Dict[str, Any]
    ) -> ModelResponse:
        """MLLM call implementation"""
        start_time = time.time()

        # Extract inputs
        prompt = inputs.get("prompt", "")
        frames = inputs.get("frames", [])
        system_prompt = inputs.get("system_prompt")

        # Extract params
        temperature = params.get("temperature", 0.7)
        max_tokens = params.get("max_tokens", 1000)

        # Prepare images from frames
        images = []
        for frame in frames:
            if frame.image_path and os.path.exists(frame.image_path):
                images.append(frame.image_path)

        # Create MLLM request
        request_id = f"req_{uuid.uuid4().hex[:8]}"
        mllm_request = MLLMRequest(
            request_id=request_id,
            model_name=model_name,
            api_endpoint="",  # Will use default from client
            prompt=prompt,
            images=images,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            task=AnalysisTask.OTHER
        )

        # Call MLLM
        mllm_response: MLLMResponse = self.mllm_client.call(mllm_request)

        # Convert to ModelResponse
        response_time_ms = (time.time() - start_time) * 1000

        return ModelResponse(
            response_id=mllm_response.response_id,
            request_id=request_id,
            model_type="mllm",
            model_name=model_name,
            success=mllm_response.success,
            error_message=mllm_response.error_message,
            output=mllm_response.text,
            total_tokens=mllm_response.total_tokens,
            cost_usd=mllm_response.cost_usd,
            response_time_ms=response_time_ms
        )

    def _call_asr(
        self,
        model_name: str,
        inputs: Dict[str, Any],
        params: Dict[str, Any]
    ) -> ModelResponse:
        """ASR call implementation (placeholder)"""
        # TODO: Implement actual ASR call
        raise AtomicOperationError("ASR model calls not yet implemented")

    # ==================== BBOX Operation ====================

    def bbox(
        self,
        frame: Frame,
        boxes: List[Dict[str, Any]]
    ) -> Frame:
        """
        BBOX - Bounding box annotation atomic operation

        Draw bounding boxes on frame.

        Args:
            frame: Input frame
            boxes: List of bounding boxes, each containing:
                  - bbox: [x, y, w, h]
                  - label: str
                  - confidence: float (optional)
                  - color: str (optional, e.g., "red", "green")

        Returns:
            Frame: New frame with annotations (new image_path)

        Raises:
            AtomicOperationError: If bbox drawing fails

        Examples:
            >>> annotated_frame = impl.bbox(
            ...     frame=frame,
            ...     boxes=[
            ...         {
            ...             "bbox": [100, 100, 200, 150],
            ...             "label": "person",
            ...             "confidence": 0.95,
            ...             "color": "green"
            ...         }
            ...     ]
            ... )
        """
        self.stats["bbox_calls"] += 1

        try:
            # Read frame image
            if not os.path.exists(frame.image_path):
                raise AtomicOperationError(f"Frame image not found: {frame.image_path}")

            image = cv2.imread(frame.image_path)
            if image is None:
                raise AtomicOperationError(f"Cannot read frame image: {frame.image_path}")

            # Draw bounding boxes
            for box in boxes:
                bbox_coords = box.get("bbox")
                label = box.get("label", "")
                confidence = box.get("confidence")
                color_name = box.get("color", "green")

                if bbox_coords is None:
                    continue

                # Parse color
                color = self._parse_color(color_name)

                # Draw rectangle
                x, y, w, h = bbox_coords
                cv2.rectangle(image, (int(x), int(y)), (int(x+w), int(y+h)), color, 2)

                # Draw label
                label_text = label
                if confidence is not None:
                    label_text += f" {confidence:.2f}"

                cv2.putText(
                    image, label_text, (int(x), int(y-10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                )

            # Save annotated frame
            annotated_path = self._save_annotated_frame(frame, image)

            # Create new Frame object
            annotated_frame = Frame(
                frame_id=f"{frame.frame_id}_annotated",
                video_id=frame.video_id,
                segment_id=frame.segment_id,
                frame_index=frame.frame_index,
                timestamp_sec=frame.timestamp_sec,
                image_path=annotated_path,
                width=image.shape[1],
                height=image.shape[0]
            )

            return annotated_frame

        except Exception as e:
            raise AtomicOperationError(f"Error in BBOX operation: {str(e)}")

    def _parse_color(self, color_name: str) -> tuple:
        """Parse color name to BGR tuple"""
        color_map = {
            "red": (0, 0, 255),
            "green": (0, 255, 0),
            "blue": (255, 0, 0),
            "yellow": (0, 255, 255),
            "cyan": (255, 255, 0),
            "magenta": (255, 0, 255),
            "white": (255, 255, 255),
            "black": (0, 0, 0)
        }
        return color_map.get(color_name.lower(), (0, 255, 0))  # Default green

    def _save_annotated_frame(self, original_frame: Frame, image) -> str:
        """Save annotated frame to temp directory"""
        # Use video processor's temp directory
        temp_dir = self.video_processor.temp_dir

        # Generate filename
        filename = f"{original_frame.frame_id}_annotated.jpg"
        save_path = temp_dir / filename

        # Save image
        cv2.imwrite(str(save_path), image)

        return str(save_path)

    # ==================== Utility Methods ====================

    def get_stats(self) -> Dict[str, Any]:
        """Get operation statistics"""
        return self.stats.copy()

    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "sample_calls": 0,
            "segment_calls": 0,
            "call_model_calls": 0,
            "bbox_calls": 0,
            "total_frames_sampled": 0,
            "total_segments_created": 0,
            "total_api_calls": 0
        }
