"""
视频问答Multi-Agent系统可视化器
专门为长视频理解系统设计的可视化工具
"""

import json
from typing import Dict, List, Any
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class Agent:
    """Agent定义"""
    name: str
    role: str
    description: str
    capabilities: List[str]
    mllm_model: str
    color: str


@dataclass
class AtomicOp:
    """原子操作定义"""
    name: str
    description: str
    input_type: str
    output_type: str
    methods: List[Dict[str, str]]
    examples: List[str]


@dataclass
class WorkflowStep:
    """工作流步骤"""
    step_num: int
    name: str
    description: str
    operation: str
    input_data: str
    output_data: str
    agent: str


class VideoQAVisualizer:
    """视频问答系统可视化器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.agents = self._define_agents()
        self.atomic_operations = self._define_atomic_operations()
        self.workflow = self._define_workflow()
        self.example_scenario = self._define_example_scenario()
        self.system_architecture = self._define_system_architecture()

    def _define_agents(self) -> List[Agent]:
        """定义系统中的Agents"""
        return [
            Agent(
                name="Tool Creator Agent",
                role="tool_creator",
                description="通过MLLM API动态创建视频处理工具，组合原子操作生成可执行的Python函数",
                capabilities=[
                    "理解用户需求",
                    "组合原子操作",
                    "生成Python代码",
                    "创建工具函数"
                ],
                mllm_model="gpt-4o (配置可调)",
                color="#4A90E2"
            ),
            Agent(
                name="Tool User Agent",
                role="tool_user",
                description="使用MLLM API分析视频内容，理解视频帧并回答用户问题",
                capabilities=[
                    "视频帧分析",
                    "片段理解",
                    "问题回答",
                    "内容摘要生成"
                ],
                mllm_model="gpt-4o (Vision支持)",
                color="#50C878"
            )
        ]

    def _define_atomic_operations(self) -> List[AtomicOp]:
        """定义4个核心原子操作"""
        return [
            AtomicOp(
                name="SAMPLE",
                description="从视频或片段中提取帧图像",
                input_type="VideoMeta | Segment",
                output_type="List[Frame]",
                methods=[
                    {"name": "uniform", "desc": "均匀采样N帧"},
                    {"name": "keyframe", "desc": "基于内容变化检测关键帧"},
                    {"name": "timestamps", "desc": "按指定时间点采样"}
                ],
                examples=[
                    "uniform: 从30秒视频中均匀提取10帧",
                    "keyframe: 检测场景变化提取关键帧",
                    "timestamps: 在第0、10、20秒提取帧"
                ]
            ),
            AtomicOp(
                name="SEGMENT",
                description="将视频按策略分割成多个片段",
                input_type="VideoMeta",
                output_type="List[Segment]",
                methods=[
                    {"name": "fixed_duration", "desc": "按固定时长分割"},
                    {"name": "scene_change", "desc": "基于场景变化分割"},
                    {"name": "custom", "desc": "按自定义时间点分割"}
                ],
                examples=[
                    "fixed_duration: 每30秒一个片段",
                    "scene_change: 自动检测场景切换",
                    "custom: 在指定时间点[0, 45, 120, 300]分割"
                ]
            ),
            AtomicOp(
                name="CALL_MODEL",
                description="统一的模型调用接口（MLLM视觉理解 / ASR语音识别）",
                input_type="prompt + frames/audio",
                output_type="ModelResponse",
                methods=[
                    {"name": "mllm", "desc": "多模态大语言模型 (GPT-4o, Claude, Gemini)"},
                    {"name": "asr", "desc": "语音识别 (Whisper)"}
                ],
                examples=[
                    "mllm: 描述视频帧中的内容",
                    "mllm: 回答关于视频的问题",
                    "asr: 转写视频中的语音"
                ]
            ),
            AtomicOp(
                name="BBOX",
                description="在帧图像上绘制边界框和标注",
                input_type="Frame + boxes",
                output_type="Frame",
                methods=[],
                examples=[
                    "在检测到的人脸位置画框",
                    "标注视频中的重要对象",
                    "可视化分析结果"
                ]
            )
        ]

    def _define_workflow(self) -> List[WorkflowStep]:
        """定义视频问答完整工作流"""
        return [
            WorkflowStep(
                step_num=1,
                name="视频输入",
                description="用户提供视频文件和问题",
                operation="VideoMeta提取",
                input_data="video_file + user_question",
                output_data="VideoMeta (duration, fps, resolution)",
                agent="system"
            ),
            WorkflowStep(
                step_num=2,
                name="视频分段",
                description="将长视频分割成多个可处理的片段",
                operation="SEGMENT",
                input_data="VideoMeta",
                output_data="List[Segment] (N个片段)",
                agent="system"
            ),
            WorkflowStep(
                step_num=3,
                name="关键帧采样",
                description="从每个片段中提取关键帧",
                operation="SAMPLE",
                input_data="Segment",
                output_data="List[Frame] (每段3-10帧)",
                agent="system"
            ),
            WorkflowStep(
                step_num=4,
                name="片段视觉理解",
                description="Tool User Agent使用MLLM分析每个片段的视觉内容",
                operation="CALL_MODEL (mllm)",
                input_data="List[Frame] + prompt",
                output_data="SegmentCaption (片段描述)",
                agent="tool_user"
            ),
            WorkflowStep(
                step_num=5,
                name="整合片段理解",
                description="收集所有片段的描述，构建完整视频理解",
                operation="Aggregation",
                input_data="List[SegmentCaption]",
                output_data="VideoUnderstanding (完整理解)",
                agent="system"
            ),
            WorkflowStep(
                step_num=6,
                name="问题回答",
                description="Tool User Agent基于完整视频理解回答用户问题",
                operation="CALL_MODEL (mllm)",
                input_data="VideoUnderstanding + user_question",
                output_data="Answer (答案)",
                agent="tool_user"
            )
        ]

    def _define_example_scenario(self) -> Dict[str, Any]:
        """定义实际应用案例"""
        return {
            "title": "新闻视频问答示例",
            "video": {
                "title": "10分钟新闻节目",
                "duration": "10:00",
                "segments": 20,
                "question": "这个新闻节目主要报道了哪些话题？"
            },
            "processing_steps": [
                {
                    "step": "1. 分段 (SEGMENT)",
                    "action": "将10分钟视频分成20个30秒片段",
                    "result": "20个Segment对象"
                },
                {
                    "step": "2. 采样 (SAMPLE)",
                    "action": "从每个片段提取3个关键帧",
                    "result": "60个Frame对象"
                },
                {
                    "step": "3. 理解片段 (CALL_MODEL)",
                    "action": "对每组3帧调用GPT-4o生成描述",
                    "result": "20个片段描述"
                },
                {
                    "step": "4. 回答问题 (CALL_MODEL)",
                    "action": "基于20个片段描述回答用户问题",
                    "result": "该节目报道了：科技新品发布、体育赛事结果、天气预报"
                }
            ],
            "metrics": {
                "total_api_calls": 21,
                "total_frames_analyzed": 60,
                "estimated_tokens": "~15000 tokens",
                "estimated_cost": "~$0.50 USD",
                "processing_time": "~45 seconds"
            }
        }

    def _define_system_architecture(self) -> Dict[str, Any]:
        """定义系统架构"""
        return {
            "layers": [
                {
                    "name": "User Interface Layer",
                    "components": ["Video Input", "Question Input", "Answer Display"],
                    "description": "用户交互层"
                },
                {
                    "name": "Agent Layer",
                    "components": ["Tool Creator Agent", "Tool User Agent"],
                    "description": "智能代理层 - 核心业务逻辑"
                },
                {
                    "name": "Atomic Operations Layer",
                    "components": ["SAMPLE", "SEGMENT", "CALL_MODEL", "BBOX"],
                    "description": "原子操作层 - 基础视频处理单元"
                },
                {
                    "name": "MLLM API Layer",
                    "components": ["GPT-4o", "Claude-3.5", "Gemini-1.5", "Whisper"],
                    "description": "模型API层 - 提供AI能力"
                },
                {
                    "name": "Data Layer",
                    "components": ["VideoMeta", "Segment", "Frame", "ModelResponse"],
                    "description": "数据层 - 标准化数据结构"
                }
            ],
            "data_flow": [
                "Video → VideoMeta → Segment → Frame → MLLM → Understanding → Answer"
            ],
            "key_features": [
                "模块化设计：4个原子操作可灵活组合",
                "统一接口：ModelResponse支持多种模型",
                "成本可控：通过调整采样策略控制API调用",
                "可扩展性：易于添加新的原子操作和模型"
            ]
        }

    def generate_visualization_data(self) -> Dict[str, Any]:
        """生成所有可视化数据"""
        return {
            "project_info": {
                "name": "Multi-Agent Long Video Understanding System",
                "description": "长视频理解的多代理系统，专注于视频问答任务",
                "version": "MVP",
                "key_tech": ["Multi-Agent", "MLLM API", "Video Processing", "Q&A"]
            },
            "agents": [asdict(agent) for agent in self.agents],
            "atomic_operations": [asdict(op) for op in self.atomic_operations],
            "workflow": [asdict(step) for step in self.workflow],
            "example_scenario": self.example_scenario,
            "system_architecture": self.system_architecture,
            "statistics": {
                "total_agents": len(self.agents),
                "total_atomic_ops": len(self.atomic_operations),
                "workflow_steps": len(self.workflow),
                "supported_models": ["GPT-4o", "GPT-4o-mini", "Claude-3.5-Sonnet", "Claude-3-Haiku", "Gemini-1.5-Pro", "Gemini-1.5-Flash", "Whisper-large-v3"]
            }
        }

    def generate_agent_interaction_sequence(self) -> List[Dict[str, Any]]:
        """生成Agent交互时序图数据"""
        return [
            {
                "seq": 1,
                "from": "User",
                "to": "System",
                "message": "提交视频 + 问题",
                "type": "input"
            },
            {
                "seq": 2,
                "from": "System",
                "to": "System",
                "message": "提取VideoMeta, 执行SEGMENT + SAMPLE",
                "type": "processing"
            },
            {
                "seq": 3,
                "from": "System",
                "to": "Tool User Agent",
                "message": "请求分析片段1的视觉内容",
                "type": "request"
            },
            {
                "seq": 4,
                "from": "Tool User Agent",
                "to": "MLLM API",
                "message": "CALL_MODEL: prompt + frames",
                "type": "api_call"
            },
            {
                "seq": 5,
                "from": "MLLM API",
                "to": "Tool User Agent",
                "message": "返回片段描述",
                "type": "response"
            },
            {
                "seq": 6,
                "from": "Tool User Agent",
                "to": "System",
                "message": "片段1理解完成",
                "type": "result"
            },
            {
                "seq": 7,
                "from": "System",
                "to": "System",
                "message": "重复步骤3-6处理所有片段...",
                "type": "loop"
            },
            {
                "seq": 8,
                "from": "System",
                "to": "Tool User Agent",
                "message": "请求基于完整理解回答问题",
                "type": "request"
            },
            {
                "seq": 9,
                "from": "Tool User Agent",
                "to": "MLLM API",
                "message": "CALL_MODEL: question + video_understanding",
                "type": "api_call"
            },
            {
                "seq": 10,
                "from": "MLLM API",
                "to": "Tool User Agent",
                "message": "返回答案",
                "type": "response"
            },
            {
                "seq": 11,
                "from": "Tool User Agent",
                "to": "System",
                "message": "问答完成",
                "type": "result"
            },
            {
                "seq": 12,
                "from": "System",
                "to": "User",
                "message": "返回最终答案",
                "type": "output"
            }
        ]

    def generate_atomic_op_composition_examples(self) -> List[Dict[str, Any]]:
        """生成原子操作组合示例"""
        return [
            {
                "name": "快速单帧分析",
                "description": "分析视频特定时间点的内容",
                "composition": ["SAMPLE(timestamps)", "CALL_MODEL(mllm)"],
                "use_case": "检查视频第30秒发生了什么",
                "code_sketch": "frames = SAMPLE(video, method='timestamps', params={'timestamps': [30]})\nresult = CALL_MODEL('mllm', 'gpt-4o', inputs={'prompt': 'Describe', 'frames': frames})"
            },
            {
                "name": "完整视频理解",
                "description": "理解整个长视频的内容",
                "composition": ["SEGMENT(fixed_duration)", "SAMPLE(uniform)", "CALL_MODEL(mllm)", "Aggregate"],
                "use_case": "生成10分钟视频的完整摘要",
                "code_sketch": "segments = SEGMENT(video, strategy='fixed_duration', params={'duration_sec': 30})\nfor seg in segments:\n    frames = SAMPLE(seg, method='uniform', params={'num_frames': 3})\n    caption = CALL_MODEL(...)\nagg_result = aggregate(all_captions)"
            },
            {
                "name": "多模态理解（视觉+语音）",
                "description": "同时分析视频的视觉和音频内容",
                "composition": ["SEGMENT", "SAMPLE", "CALL_MODEL(mllm)", "CALL_MODEL(asr)", "Fusion"],
                "use_case": "理解新闻节目的画面和解说",
                "code_sketch": "visual = CALL_MODEL('mllm', ...)\naudio = CALL_MODEL('asr', 'whisper-large-v3', ...)\nfusion_result = combine(visual, audio)"
            },
            {
                "name": "关键帧提取与标注",
                "description": "提取关键帧并标注重要区域",
                "composition": ["SAMPLE(keyframe)", "CALL_MODEL(detection)", "BBOX"],
                "use_case": "提取并标注视频中的关键对象",
                "code_sketch": "keyframes = SAMPLE(video, method='keyframe', params={'threshold': 0.3})\ndetections = CALL_MODEL('detection', ...)\nannotated = BBOX(frame, boxes=detections)"
            }
        ]

    def export_all(self, output_dir: Path) -> None:
        """导出所有可视化数据"""
        output_dir.mkdir(parents=True, exist_ok=True)

        # 导出主数据
        main_data = self.generate_visualization_data()
        with open(output_dir / "main_data.json", "w", encoding="utf-8") as f:
            json.dump(main_data, f, indent=2, ensure_ascii=False)

        # 导出Agent交互序列
        interaction_seq = self.generate_agent_interaction_sequence()
        with open(output_dir / "interaction_sequence.json", "w", encoding="utf-8") as f:
            json.dump(interaction_seq, f, indent=2, ensure_ascii=False)

        # 导出原子操作组合示例
        composition_examples = self.generate_atomic_op_composition_examples()
        with open(output_dir / "composition_examples.json", "w", encoding="utf-8") as f:
            json.dump(composition_examples, f, indent=2, ensure_ascii=False)

        print(f"✅ 所有可视化数据已导出到: {output_dir}")
