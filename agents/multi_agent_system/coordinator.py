"""
MultiAgent Coordinator

协调Tool Creator Agent和Tool User Agent，管理整个multi-agent工作流程。
"""

import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

# 导入项目数据结构
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.multi_agent_system.types import MultiAgentSession
from agents.multi_agent_system.tool_creator import ToolCreatorAgent
from agents.multi_agent_system.tool_user import ToolUserAgent
from agents.multi_agent_system.tool_executor import ToolExecutor


class MultiAgentCoordinator:
    """
    MultiAgent Coordinator - 多Agent协调器

    核心职责：
    1. 协调Tool Creator和Tool User两个agent
    2. 管理完整的multi-agent会话
    3. 追踪所有统计信息（tokens, cost, duration）
    4. 提供统一的任务处理接口

    工作流程：
    User Task
        ↓
    [Phase 1] Tool Creator Agent
        - 分析任务
        - 分解子任务
        - 设计工具（含prompt）
        ↓
    [Phase 2] Tool User Agent
        - 规划执行步骤
        - 选择工具
        - 执行工具（via Tool Executor）
        ↓
    Final Result + Complete Session Record
    """

    def __init__(self, mllm_client=None):
        """
        初始化MultiAgent Coordinator

        Args:
            mllm_client: MLLM客户端，如果不提供则使用默认配置
        """
        # 初始化两个Agent
        self.tool_creator = ToolCreatorAgent(mllm_client=mllm_client)
        self.tool_user = ToolUserAgent(mllm_client=mllm_client)

        # Tool Executor将在执行时创建
        self.tool_executor = None

    def process(
        self,
        video_path: str,
        question: str,
        atomic_ops: Any,
        constraints: Optional[Dict[str, Any]] = None
    ) -> MultiAgentSession:
        """
        处理视频问答任务 - 主入口

        完整的multi-agent工作流程：
        1. 创建会话
        2. Phase 1: Tool Creation（工具设计）
        3. Phase 2: Tool Usage（工具使用）
        4. 整合统计信息
        5. 返回完整会话记录

        Args:
            video_path: 视频路径
            question: 用户问题
            atomic_ops: 原子操作实现
            constraints: 约束条件（可选）

        Returns:
            完整的multi-agent会话记录
        """
        print(f"\n{'='*70}")
        print(f"{'MULTI-AGENT SYSTEM':^70}")
        print(f"{'='*70}\n")

        start_time = time.time()

        # 创建会话
        task_description = f"""
任务类型: 视频问答 (Video Question Answering)

视频: {video_path}
问题: {question}

要求: 分析视频内容并准确回答用户问题。
"""

        session = MultiAgentSession(
            session_id=f"session_{uuid.uuid4().hex[:8]}",
            task_description=task_description
        )

        try:
            # ========== Phase 1: Tool Creation ==========
            print(f"\n{'▶ PHASE 1: TOOL CREATION':^70}")
            print(f"{'─'*70}\n")

            phase1_start = time.time()

            tools = self.tool_creator.design_tools(
                task_description=task_description,
                constraints=constraints
            )

            session.designed_tools = tools
            session.tool_creator_actions = self.tool_creator.get_actions()

            phase1_duration = time.time() - phase1_start
            print(f"\n{'─'*70}")
            print(f"Phase 1 完成: 设计了 {len(tools)} 个工具 ({phase1_duration:.1f}秒)")
            print(f"{'─'*70}\n")

            # ========== Phase 2: Tool Usage ==========
            print(f"\n{'▶ PHASE 2: TOOL USAGE':^70}")
            print(f"{'─'*70}\n")

            phase2_start = time.time()

            # 准备数据
            # 需要从video_path提取VideoMeta
            from processors.video_processor import VideoProcessor
            video_processor = VideoProcessor()
            video_meta = video_processor.extract_metadata(video_path)

            data = {
                "video_path": video_path,
                "video_meta": video_meta,
                "question": question
            }

            # 设置Tool Executor
            self.tool_executor = ToolExecutor(atomic_ops=atomic_ops)
            self.tool_user.set_tool_executor(self.tool_executor)

            # 执行任务
            execution_result = self.tool_user.execute_task(
                task=task_description,
                tools=tools,
                data=data,
                atomic_ops=atomic_ops
            )

            session.execution_plan = execution_result["plan"]
            session.final_result = execution_result["result"]
            session.tool_user_actions = self.tool_user.get_actions()
            session.success = True

            phase2_duration = time.time() - phase2_start
            print(f"\n{'─'*70}")
            print(f"Phase 2 完成: 执行了 {len(execution_result['plan'].steps)} 个步骤 ({phase2_duration:.1f}秒)")
            print(f"{'─'*70}\n")

            # ========== 统计信息 ==========
            total_duration = time.time() - start_time

            # 汇总统计
            creator_stats = self.tool_creator.get_statistics()
            user_stats = self.tool_user.get_statistics()

            session.total_tokens = creator_stats["total_tokens"] + user_stats["total_tokens"]
            session.total_cost = creator_stats["total_cost_usd"] + user_stats["total_cost_usd"]
            session.total_duration_ms = total_duration * 1000
            session.completed_at = datetime.now().isoformat()

            # ========== 输出摘要 ==========
            print(f"\n{'='*70}")
            print(f"{'SESSION SUMMARY':^70}")
            print(f"{'='*70}")
            print(f"\n会话ID: {session.session_id}")
            print(f"状态: {'✓ 成功' if session.success else '✗ 失败'}")
            print(f"\n工具设计:")
            print(f"  - 设计工具数: {len(session.designed_tools)}")
            for i, tool in enumerate(session.designed_tools, 1):
                print(f"    {i}. {tool.tool_name}")
                print(f"       目的: {tool.purpose[:60]}...")
                print(f"       原子操作: {', '.join(tool.atomic_operations)}")

            print(f"\n执行计划:")
            if session.execution_plan:
                print(f"  - 计划步骤数: {len(session.execution_plan.steps)}")
                completed_steps = len([s for s in session.execution_plan.steps if s.status == "completed"])
                print(f"  - 成功步骤数: {completed_steps}")

            print(f"\n最终结果:")
            if isinstance(session.final_result, str):
                result_preview = session.final_result[:200]
                print(f"  {result_preview}...")
            else:
                print(f"  {session.final_result}")

            print(f"\n统计信息:")
            print(f"  ├─ Tool Creator:")
            print(f"  │   ├─ Actions: {len(session.tool_creator_actions)}")
            print(f"  │   ├─ Tokens: {creator_stats['total_tokens']}")
            print(f"  │   └─ Cost: ${creator_stats['total_cost_usd']:.4f}")
            print(f"  │")
            print(f"  ├─ Tool User:")
            print(f"  │   ├─ Actions: {len(session.tool_user_actions)}")
            print(f"  │   ├─ Tokens: {user_stats['total_tokens']}")
            print(f"  │   └─ Cost: ${user_stats['total_cost_usd']:.4f}")
            print(f"  │")
            print(f"  └─ Total:")
            print(f"      ├─ Tokens: {session.total_tokens}")
            print(f"      ├─ Cost: ${session.total_cost:.4f}")
            print(f"      └─ Duration: {total_duration:.1f}s")

            print(f"\n{'='*70}\n")

            return session

        except Exception as e:
            print(f"\n{'='*70}")
            print(f"✗ 执行失败: {e}")
            print(f"{'='*70}\n")

            session.success = False
            session.final_result = {"error": str(e)}
            session.completed_at = datetime.now().isoformat()
            session.total_duration_ms = (time.time() - start_time) * 1000

            return session

    def process_simple(
        self,
        task_description: str,
        data: Dict[str, Any],
        atomic_ops: Any,
        constraints: Optional[Dict[str, Any]] = None
    ) -> MultiAgentSession:
        """
        通用任务处理接口

        适用于非视频问答的其他任务类型。

        Args:
            task_description: 任务描述
            data: 输入数据
            atomic_ops: 原子操作实现
            constraints: 约束条件

        Returns:
            完整的multi-agent会话记录
        """
        print(f"\n{'='*70}")
        print(f"{'MULTI-AGENT SYSTEM':^70}")
        print(f"{'='*70}\n")

        start_time = time.time()

        session = MultiAgentSession(
            session_id=f"session_{uuid.uuid4().hex[:8]}",
            task_description=task_description
        )

        try:
            # Phase 1: Tool Creation
            print(f"\n{'▶ PHASE 1: TOOL CREATION':^70}")
            print(f"{'─'*70}\n")

            tools = self.tool_creator.design_tools(
                task_description=task_description,
                constraints=constraints
            )

            session.designed_tools = tools
            session.tool_creator_actions = self.tool_creator.get_actions()

            # Phase 2: Tool Usage
            print(f"\n{'▶ PHASE 2: TOOL USAGE':^70}")
            print(f"{'─'*70}\n")

            self.tool_executor = ToolExecutor(atomic_ops=atomic_ops)
            self.tool_user.set_tool_executor(self.tool_executor)

            execution_result = self.tool_user.execute_task(
                task=task_description,
                tools=tools,
                data=data,
                atomic_ops=atomic_ops
            )

            session.execution_plan = execution_result["plan"]
            session.final_result = execution_result["result"]
            session.tool_user_actions = self.tool_user.get_actions()
            session.success = True

            # 统计信息
            total_duration = time.time() - start_time
            creator_stats = self.tool_creator.get_statistics()
            user_stats = self.tool_user.get_statistics()

            session.total_tokens = creator_stats["total_tokens"] + user_stats["total_tokens"]
            session.total_cost = creator_stats["total_cost_usd"] + user_stats["total_cost_usd"]
            session.total_duration_ms = total_duration * 1000
            session.completed_at = datetime.now().isoformat()

            return session

        except Exception as e:
            session.success = False
            session.final_result = {"error": str(e)}
            session.completed_at = datetime.now().isoformat()
            session.total_duration_ms = (time.time() - start_time) * 1000

            return session
