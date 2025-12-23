"""
Video QA Pipeline

End-to-end pipeline for video question answering:
1. Extract video metadata
2. Segment video
3. Sample frames from each segment
4. Analyze each segment with MLLM
5. Aggregate segment understanding
6. Answer question based on full video understanding
7. Track experiment metrics (API calls, tokens, cost)

This is Phase 3 implementation.
"""

import os
import uuid
import time
from typing import Dict, Any, List, Tuple, Optional
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
    SegmentCaption,
    VideoUnderstanding,
    VideoExperimentRun,
    ProcessingStatus,
    AnalysisTask
)

from processors import (
    VideoProcessor,
    AtomicOperationsImplementation,
    AtomicOperationError
)


class VideoQAPipelineError(Exception):
    """Video QA pipeline specific errors"""
    pass


class VideoQAPipeline:
    """
    Video Question Answering Pipeline

    Complete end-to-end pipeline that:
    1. Takes a video file and a question
    2. Processes the video segment by segment
    3. Uses MLLM to analyze each segment
    4. Aggregates understanding across segments
    5. Answers the question
    6. Returns answer + experiment tracking data

    This implements the full workflow described in the project goal.
    """

    def __init__(
        self,
        atomic_ops: AtomicOperationsImplementation,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Video QA Pipeline

        Args:
            atomic_ops: Atomic operations implementation
            config: Pipeline configuration with options:
                - segment_duration_sec: Duration of each segment (default: 30)
                - frames_per_segment: Frames to sample per segment (default: 5)
                - sampling_method: Frame sampling method (default: "uniform")
                - mllm_model: MLLM model name (default: "gpt-4-turbo-preview")
                - temperature: MLLM temperature (default: 0.7)
                - max_tokens_per_segment: Max tokens for segment analysis (default: 4000, 上限)
                - max_tokens_qa: Max tokens for QA (default: 3000, 上限)
        """
        self.atomic_ops = atomic_ops
        self.video_processor = atomic_ops.video_processor

        # Default configuration
        default_config = {
            "segment_duration_sec": 30.0,
            "frames_per_segment": 5,
            "sampling_method": "uniform",
            "mllm_model": "gpt-4-turbo-preview",
            "temperature": 0.7,
            "max_tokens_per_segment": 4000,  # 上限，让模型自然完成
            "max_tokens_qa": 3000,           # 上限，让模型自然完成
            "max_segments": None,  # Process all segments if None
        }

        self.config = {**default_config, **(config or {})}

    def run_video_qa(
        self,
        video_path: str,
        question: str,
        context: Optional[str] = None
    ) -> Tuple[str, VideoExperimentRun]:
        """
        Run complete video QA pipeline

        Args:
            video_path: Path to video file
            question: Question to answer about the video
            context: Optional context information

        Returns:
            Tuple of (answer: str, experiment: VideoExperimentRun)

        Raises:
            VideoQAPipelineError: If pipeline fails

        Example:
            >>> pipeline = VideoQAPipeline(atomic_ops)
            >>> answer, experiment = pipeline.run_video_qa(
            ...     "data/videos/sample.mp4",
            ...     "What happens in this video?"
            ... )
            >>> print(f"Answer: {answer}")
            >>> print(f"Cost: ${experiment.estimated_cost_usd:.2f}")
        """
        # Initialize experiment tracking
        experiment = self._init_experiment(video_path, question)

        try:
            # Step 1: Extract video metadata
            print(f"\n[1/6] Extracting video metadata...")
            video_meta = self._extract_metadata(video_path, experiment)

            # Step 2: Segment video
            print(f"\n[2/6] Segmenting video...")
            segments = self._segment_video(video_meta, experiment)

            # Limit segments if configured
            if self.config["max_segments"]:
                segments = segments[:self.config["max_segments"]]
                print(f"  → Processing first {len(segments)} segments only")

            # Step 3-4: Process each segment (sample + analyze)
            print(f"\n[3/6] Processing segments ({len(segments)} total)...")
            segment_captions = self._process_segments(
                video_meta, segments, experiment
            )

            # Step 5: Aggregate segment understanding
            print(f"\n[4/6] Aggregating segment understanding...")
            video_understanding = self._aggregate_understanding(
                video_meta, segments, segment_captions, experiment
            )

            # Step 6: Answer question
            print(f"\n[5/6] Answering question...")
            answer = self._answer_question(
                question, video_understanding, context, experiment
            )

            # Finalize experiment
            print(f"\n[6/6] Finalizing experiment...")
            self._finalize_experiment(experiment, ProcessingStatus.COMPLETED)

            print(f"\n✓ Pipeline completed successfully!")
            print(f"  Total API calls: {experiment.total_api_calls}")
            print(f"  Total tokens: {experiment.total_tokens_used}")
            print(f"  Estimated cost: ${experiment.total_cost_usd:.4f}")

            return answer, experiment

        except Exception as e:
            self._finalize_experiment(experiment, ProcessingStatus.FAILED)
            experiment.notes.append(f"Error: {str(e)}")
            raise VideoQAPipelineError(f"Pipeline failed: {str(e)}")

    def _init_experiment(self, video_path: str, question: str) -> VideoExperimentRun:
        """Initialize experiment tracking"""
        return VideoExperimentRun(
            run_id=f"run_{uuid.uuid4().hex[:8]}",
            experiment_name=f"VideoQA: {question[:50]}",
            description=f"Video: {video_path}, Question: {question}",
            status=ProcessingStatus.PROCESSING
        )

    def _extract_metadata(
        self,
        video_path: str,
        experiment: VideoExperimentRun
    ) -> VideoMeta:
        """Extract video metadata"""
        try:
            video_meta = self.video_processor.extract_metadata(video_path)
            experiment.video_meta = video_meta

            print(f"  ✓ Video: {video_meta.duration_sec:.1f}s, "
                  f"{video_meta.width}x{video_meta.height}, "
                  f"{video_meta.fps:.1f}fps")

            return video_meta

        except Exception as e:
            raise VideoQAPipelineError(f"Failed to extract metadata: {str(e)}")

    def _segment_video(
        self,
        video_meta: VideoMeta,
        experiment: VideoExperimentRun
    ) -> List[Segment]:
        """Segment video"""
        try:
            segments = self.atomic_ops.segment(
                video_meta=video_meta,
                strategy="fixed_duration",
                params={"duration_sec": self.config["segment_duration_sec"]}
            )

            # Store segment IDs
            experiment.segments = [seg.segment_id for seg in segments]

            print(f"  ✓ Created {len(segments)} segments "
                  f"({self.config['segment_duration_sec']}s each)")

            return segments

        except AtomicOperationError as e:
            raise VideoQAPipelineError(f"Failed to segment video: {str(e)}")

    def _process_segments(
        self,
        video_meta: VideoMeta,
        segments: List[Segment],
        experiment: VideoExperimentRun
    ) -> List[SegmentCaption]:
        """Process each segment: sample frames + analyze with MLLM"""
        segment_captions = []

        for i, segment in enumerate(segments):
            print(f"  Processing segment {i+1}/{len(segments)} "
                  f"[{segment.time_span.start_sec:.1f}s - {segment.time_span.end_sec:.1f}s]...")

            try:
                # Sample frames from segment time range
                timestamps = self._generate_segment_timestamps(segment)
                frames = self.atomic_ops.sample(
                    source=video_meta,
                    method="timestamps",
                    params={"timestamps": timestamps}
                )

                # Store frame IDs
                experiment.frames.extend([f.frame_id for f in frames])

                print(f"    → Sampled {len(frames)} frames")

                # Analyze segment with MLLM
                caption = self._analyze_segment(
                    segment, frames, video_meta, experiment
                )

                segment_captions.append(caption)

                print(f"    ✓ Analyzed: {caption.caption[:60]}...")

            except Exception as e:
                print(f"    ✗ Failed to process segment {i+1}: {str(e)}")
                # Create error caption
                error_caption = SegmentCaption(
                    caption_id=f"caption_{segment.segment_id}",
                    segment_id=segment.segment_id,
                    caption=f"Error processing segment: {str(e)}",
                    confidence=0.0
                )
                segment_captions.append(error_caption)

        return segment_captions

    def _generate_segment_timestamps(self, segment: Segment) -> List[float]:
        """Generate timestamps for sampling within segment"""
        num_frames = self.config["frames_per_segment"]
        start = segment.time_span.start_sec
        end = segment.time_span.end_sec
        duration = end - start

        if num_frames == 1:
            return [start + duration / 2]

        interval = duration / (num_frames - 1) if num_frames > 1 else duration
        return [start + i * interval for i in range(num_frames)]

    def _analyze_segment(
        self,
        segment: Segment,
        frames: List[Frame],
        video_meta: VideoMeta,
        experiment: VideoExperimentRun
    ) -> SegmentCaption:
        """Analyze segment using MLLM"""
        # Build prompt for segment analysis
        prompt = f"""Analyze this video segment from {segment.time_span.start_sec:.1f}s to {segment.time_span.end_sec:.1f}s.

Below are {len(frames)} frames sampled from this segment.

Please provide:
1. A concise description of what happens in this segment (2-3 sentences)
2. Main activities or events
3. Key objects or people visible

Format your response as:
Description: [your description]
Events: [list of events]
Objects: [list of objects]"""

        try:
            # Call MLLM
            response = self.atomic_ops.call_model(
                model_type="mllm",
                model_name=self.config["mllm_model"],
                inputs={
                    "prompt": prompt,
                    "frames": frames,
                    "system_prompt": "You are a helpful video analysis assistant."
                },
                params={
                    "temperature": self.config["temperature"],
                    "max_tokens": self.config["max_tokens_per_segment"]
                }
            )

            # Update experiment tracking
            experiment.total_api_calls += 1
            if response.success:
                experiment.total_tokens_used += response.total_tokens
                experiment.total_cost_usd += response.cost_usd

            # Parse response into SegmentCaption
            caption = SegmentCaption(
                caption_id=f"caption_{segment.segment_id}",
                segment_id=segment.segment_id,
                caption=response.output if response.success else "Analysis failed",
                confidence=0.9 if response.success else 0.0,
                key_frames=[f.frame_id for f in frames],
                model_name=self.config["mllm_model"]
            )

            # Try to parse structured info
            self._parse_segment_analysis(response.output, caption)

            return caption

        except Exception as e:
            # Return error caption
            return SegmentCaption(
                caption_id=f"caption_{segment.segment_id}",
                segment_id=segment.segment_id,
                caption=f"Error: {str(e)}",
                confidence=0.0
            )

    def _parse_segment_analysis(self, text: str, caption: SegmentCaption):
        """Parse structured information from MLLM response"""
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("Description:"):
                caption.summary = line.replace("Description:", "").strip()
            elif line.startswith("Events:"):
                events_text = line.replace("Events:", "").strip()
                caption.main_events = [e.strip() for e in events_text.split(",") if e.strip()]
            elif line.startswith("Objects:"):
                objects_text = line.replace("Objects:", "").strip()
                caption.key_objects = [o.strip() for o in objects_text.split(",") if o.strip()]

    def _aggregate_understanding(
        self,
        video_meta: VideoMeta,
        segments: List[Segment],
        segment_captions: List[SegmentCaption],
        experiment: VideoExperimentRun
    ) -> VideoUnderstanding:
        """Aggregate segment understanding into complete video understanding"""
        # Create segment_id to time_span mapping
        segment_map = {seg.segment_id: seg.time_span for seg in segments}

        # Concatenate all segment descriptions with timestamps
        full_description = "\n\n".join([
            f"[{segment_map[cap.segment_id].start_sec:.1f}s - {segment_map[cap.segment_id].end_sec:.1f}s]: {cap.caption}"
            for cap in segment_captions
            if cap.confidence > 0 and cap.segment_id in segment_map
        ])

        # Create video understanding
        understanding = VideoUnderstanding(
            understanding_id=f"understanding_{video_meta.video_id}",
            video_id=video_meta.video_id,
            overall_caption=full_description,
            summary="",  # Will be generated if needed
            segment_captions=[cap.caption_id for cap in segment_captions],
            main_topics=[],
            timeline_events=[]
        )

        print(f"  ✓ Aggregated {len(segment_captions)} segment descriptions")

        return understanding

    def _answer_question(
        self,
        question: str,
        video_understanding: VideoUnderstanding,
        context: Optional[str],
        experiment: VideoExperimentRun
    ) -> str:
        """Answer question based on video understanding"""
        # Build comprehensive prompt with all segment information
        context_text = f"""Video Analysis Context:

{video_understanding.overall_caption}

"""
        if context:
            context_text += f"Additional Context: {context}\n\n"

        prompt = f"""{context_text}Based on the video analysis above, please answer the following question:

Question: {question}

Please provide a clear, concise answer based on the video content."""

        try:
            # Call MLLM for QA
            response = self.atomic_ops.call_model(
                model_type="mllm",
                model_name=self.config["mllm_model"],
                inputs={
                    "prompt": prompt,
                    "frames": [],  # No frames needed, using text context
                    "system_prompt": "You are a helpful assistant answering questions about video content."
                },
                params={
                    "temperature": self.config["temperature"],
                    "max_tokens": self.config["max_tokens_qa"]
                }
            )

            # Update experiment tracking
            experiment.total_api_calls += 1
            if response.success:
                experiment.total_tokens_used += response.total_tokens
                experiment.total_cost_usd += response.cost_usd

            if response.success:
                answer = response.output
                print(f"  ✓ Generated answer ({len(answer)} chars)")
                return answer
            else:
                error_msg = f"Failed to generate answer: {response.error_message}"
                print(f"  ✗ {error_msg}")
                return error_msg

        except Exception as e:
            error_msg = f"Error answering question: {str(e)}"
            print(f"  ✗ {error_msg}")
            return error_msg

    def _finalize_experiment(
        self,
        experiment: VideoExperimentRun,
        status: ProcessingStatus
    ):
        """Finalize experiment tracking"""
        experiment.end_time = datetime.now().isoformat()
        experiment.status = status

        # Calculate duration
        start = datetime.fromisoformat(experiment.start_time)
        end = datetime.fromisoformat(experiment.end_time)
        duration = (end - start).total_seconds()
        experiment.total_duration_ms = duration * 1000

    def get_config(self) -> Dict[str, Any]:
        """Get current pipeline configuration"""
        return self.config.copy()

    def update_config(self, config: Dict[str, Any]):
        """Update pipeline configuration"""
        self.config.update(config)
