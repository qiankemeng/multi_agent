"""
配置管理模块

从.env文件加载配置，提供统一的配置访问接口
支持环境变量覆盖和默认值
"""

import os
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field


def _get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve()
    # 向上查找，直到找到包含.env.example的目录
    for parent in [current.parent.parent, *current.parents]:
        if (parent / '.env.example').exists():
            return parent
    # 如果找不到，返回当前文件的父目录的父目录
    return current.parent.parent


# 项目根目录
PROJECT_ROOT = _get_project_root()


def _load_env_file(env_path: Path) -> None:
    """
    加载.env文件到环境变量

    Args:
        env_path: .env文件路径
    """
    if not env_path.exists():
        return

    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue

            # 解析key=value
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # 只在环境变量不存在时设置
                if key and not os.getenv(key):
                    os.environ[key] = value


# 加载.env文件
_env_file = PROJECT_ROOT / '.env'
if _env_file.exists():
    _load_env_file(_env_file)


def get_env(key: str, default: Any = None, cast_type: type = str) -> Any:
    """
    获取环境变量，支持类型转换

    Args:
        key: 环境变量名
        default: 默认值
        cast_type: 目标类型（str, int, float, bool）

    Returns:
        配置值
    """
    value = os.getenv(key)

    if value is None:
        return default

    # 类型转换
    if cast_type == bool:
        return value.lower() in ('true', '1', 'yes', 'on')
    elif cast_type == int:
        try:
            return int(value)
        except ValueError:
            return default
    elif cast_type == float:
        try:
            return float(value)
        except ValueError:
            return default
    else:
        return value


@dataclass
class OpenAIConfig:
    """OpenAI API配置"""
    api_key: str = field(default_factory=lambda: get_env('OPENAI_API_KEY', ''))
    base_url: str = field(default_factory=lambda: get_env('OPENAI_BASE_URL', 'https://api.openai.com/v1'))
    default_model: str = field(default_factory=lambda: get_env('OPENAI_DEFAULT_MODEL', 'gpt-4-vision-preview'))
    organization_id: str = field(default_factory=lambda: get_env('OPENAI_ORGANIZATION_ID', ''))

    # 价格配置（美元/1K tokens）
    price_prompt_1k: float = field(default_factory=lambda: get_env('OPENAI_PRICE_PROMPT_1K', 0.01, float))
    price_completion_1k: float = field(default_factory=lambda: get_env('OPENAI_PRICE_COMPLETION_1K', 0.03, float))


@dataclass
class ClaudeConfig:
    """Claude API配置"""
    api_key: str = field(default_factory=lambda: get_env('CLAUDE_API_KEY', ''))
    base_url: str = field(default_factory=lambda: get_env('CLAUDE_BASE_URL', 'https://api.anthropic.com'))
    default_model: str = field(default_factory=lambda: get_env('CLAUDE_DEFAULT_MODEL', 'claude-3-opus-20240229'))


@dataclass
class GeminiConfig:
    """Gemini API配置"""
    api_key: str = field(default_factory=lambda: get_env('GEMINI_API_KEY', ''))
    base_url: str = field(default_factory=lambda: get_env('GEMINI_BASE_URL', 'https://generativelanguage.googleapis.com'))
    default_model: str = field(default_factory=lambda: get_env('GEMINI_DEFAULT_MODEL', 'gemini-pro-vision'))


@dataclass
class MLLMConfig:
    """MLLM通用配置"""
    default_temperature: float = field(default_factory=lambda: get_env('MLLM_DEFAULT_TEMPERATURE', 0.7, float))
    default_max_tokens: int = field(default_factory=lambda: get_env('MLLM_DEFAULT_MAX_TOKENS', 1000, int))
    request_timeout: int = field(default_factory=lambda: get_env('MLLM_REQUEST_TIMEOUT', 60, int))
    max_retries: int = field(default_factory=lambda: get_env('MLLM_MAX_RETRIES', 3, int))
    retry_delay: float = field(default_factory=lambda: get_env('MLLM_RETRY_DELAY', 1.0, float))


@dataclass
class CostConfig:
    """成本控制配置"""
    max_request_cost: float = field(default_factory=lambda: get_env('MAX_REQUEST_COST', 0.0, float))
    max_daily_cost: float = field(default_factory=lambda: get_env('MAX_DAILY_COST', 0.0, float))


@dataclass
class AgentConfig:
    """Agent配置"""
    # 工具创建Agent
    tool_creator_model: str = field(default_factory=lambda: get_env('TOOL_CREATOR_MODEL', 'gpt-4-turbo-preview'))
    tool_creator_temperature: float = field(default_factory=lambda: get_env('TOOL_CREATOR_TEMPERATURE', 0.3, float))
    tool_creator_max_tokens: int = field(default_factory=lambda: get_env('TOOL_CREATOR_MAX_TOKENS', 2000, int))

    # 工具使用Agent
    tool_user_model: str = field(default_factory=lambda: get_env('TOOL_USER_MODEL', 'gpt-4-vision-preview'))
    tool_user_temperature: float = field(default_factory=lambda: get_env('TOOL_USER_TEMPERATURE', 0.7, float))
    tool_user_max_tokens: int = field(default_factory=lambda: get_env('TOOL_USER_MAX_TOKENS', 1000, int))


@dataclass
class VideoConfig:
    """视频处理配置"""
    segmentation_strategy: str = field(default_factory=lambda: get_env('VIDEO_SEGMENTATION_STRATEGY', 'fixed_duration'))
    segment_duration: int = field(default_factory=lambda: get_env('VIDEO_SEGMENT_DURATION', 30, int))
    max_segments: int = field(default_factory=lambda: get_env('VIDEO_MAX_SEGMENTS', 100, int))

    frame_sampling_method: str = field(default_factory=lambda: get_env('FRAME_SAMPLING_METHOD', 'uniform'))
    frames_per_segment: int = field(default_factory=lambda: get_env('FRAMES_PER_SEGMENT', 5, int))
    max_image_size: int = field(default_factory=lambda: get_env('MAX_IMAGE_SIZE', 1024, int))


@dataclass
class PathConfig:
    """路径配置"""
    data_dir: Path = field(default_factory=lambda: Path(get_env('DATA_DIR', './data')))
    video_dir: Path = field(default_factory=lambda: Path(get_env('VIDEO_DIR', './data/videos')))
    output_dir: Path = field(default_factory=lambda: Path(get_env('OUTPUT_DIR', './data/output')))
    cache_dir: Path = field(default_factory=lambda: Path(get_env('CACHE_DIR', './data/cache')))
    temp_dir: Path = field(default_factory=lambda: Path(get_env('TEMP_DIR', './data/temp')))

    def ensure_dirs(self):
        """确保所有目录存在"""
        for dir_path in [self.data_dir, self.video_dir, self.output_dir,
                         self.cache_dir, self.temp_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)


@dataclass
class LogConfig:
    """日志配置"""
    level: str = field(default_factory=lambda: get_env('LOG_LEVEL', 'INFO'))
    file: Optional[str] = field(default_factory=lambda: get_env('LOG_FILE', './logs/app.log'))
    format: str = field(default_factory=lambda: get_env('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    to_console: bool = field(default_factory=lambda: get_env('LOG_TO_CONSOLE', True, bool))


@dataclass
class ExperimentConfig:
    """实验配置"""
    name: str = field(default_factory=lambda: get_env('EXPERIMENT_NAME', 'default_experiment'))
    id: str = field(default_factory=lambda: get_env('EXPERIMENT_ID', ''))
    save_intermediate_results: bool = field(default_factory=lambda: get_env('SAVE_INTERMEDIATE_RESULTS', True, bool))
    verbose: bool = field(default_factory=lambda: get_env('VERBOSE', False, bool))


@dataclass
class PerformanceConfig:
    """性能配置"""
    max_concurrent_requests: int = field(default_factory=lambda: get_env('MAX_CONCURRENT_REQUESTS', 3, int))
    enable_cache: bool = field(default_factory=lambda: get_env('ENABLE_CACHE', True, bool))
    cache_expiry: int = field(default_factory=lambda: get_env('CACHE_EXPIRY', 3600, int))


@dataclass
class DevConfig:
    """开发配置"""
    environment: str = field(default_factory=lambda: get_env('ENVIRONMENT', 'development'))
    debug: bool = field(default_factory=lambda: get_env('DEBUG', False, bool))
    mock_mode: bool = field(default_factory=lambda: get_env('MOCK_MODE', False, bool))


@dataclass
class Settings:
    """
    全局配置类

    整合所有配置模块，提供统一的访问接口
    """
    # API配置
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    claude: ClaudeConfig = field(default_factory=ClaudeConfig)
    gemini: GeminiConfig = field(default_factory=GeminiConfig)

    # MLLM配置
    mllm: MLLMConfig = field(default_factory=MLLMConfig)
    cost: CostConfig = field(default_factory=CostConfig)

    # Agent配置
    agent: AgentConfig = field(default_factory=AgentConfig)

    # 视频处理配置
    video: VideoConfig = field(default_factory=VideoConfig)

    # 路径配置
    path: PathConfig = field(default_factory=PathConfig)

    # 日志配置
    log: LogConfig = field(default_factory=LogConfig)

    # 实验配置
    experiment: ExperimentConfig = field(default_factory=ExperimentConfig)

    # 性能配置
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)

    # 开发配置
    dev: DevConfig = field(default_factory=DevConfig)

    # 项目根目录
    project_root: Path = PROJECT_ROOT

    def __post_init__(self):
        """初始化后处理"""
        # 确保必要的目录存在
        if not self.dev.mock_mode:
            self.path.ensure_dirs()

    def validate(self) -> list[str]:
        """
        验证配置

        Returns:
            错误列表，如果为空则配置有效
        """
        errors = []

        # 检查API key
        if not self.openai.api_key and not self.dev.mock_mode:
            errors.append("OPENAI_API_KEY is required (set MOCK_MODE=true to skip)")

        # 检查温度参数范围
        if not 0 <= self.mllm.default_temperature <= 2:
            errors.append(f"MLLM_DEFAULT_TEMPERATURE must be between 0 and 2 (got {self.mllm.default_temperature})")

        # 检查token数量
        if self.mllm.default_max_tokens <= 0:
            errors.append(f"MLLM_DEFAULT_MAX_TOKENS must be positive (got {self.mllm.default_max_tokens})")

        # 检查视频配置
        if self.video.segment_duration <= 0:
            errors.append(f"VIDEO_SEGMENT_DURATION must be positive (got {self.video.segment_duration})")

        if self.video.frames_per_segment <= 0:
            errors.append(f"FRAMES_PER_SEGMENT must be positive (got {self.video.frames_per_segment})")

        return errors

    def print_summary(self):
        """打印配置摘要"""
        print("="*60)
        print("Configuration Summary")
        print("="*60)
        print(f"\n【Environment】")
        print(f"  Mode: {self.dev.environment}")
        print(f"  Debug: {self.dev.debug}")
        print(f"  Mock Mode: {self.dev.mock_mode}")

        print(f"\n【OpenAI API】")
        print(f"  Model: {self.openai.default_model}")
        print(f"  API Key: {'✓ Set' if self.openai.api_key else '✗ Not Set'}")
        print(f"  Base URL: {self.openai.base_url}")

        print(f"\n【MLLM Settings】")
        print(f"  Temperature: {self.mllm.default_temperature}")
        print(f"  Max Tokens: {self.mllm.default_max_tokens}")
        print(f"  Timeout: {self.mllm.request_timeout}s")
        print(f"  Max Retries: {self.mllm.max_retries}")

        print(f"\n【Agent Settings】")
        print(f"  Tool Creator Model: {self.agent.tool_creator_model}")
        print(f"  Tool User Model: {self.agent.tool_user_model}")

        print(f"\n【Video Processing】")
        print(f"  Segmentation: {self.video.segmentation_strategy}")
        print(f"  Segment Duration: {self.video.segment_duration}s")
        print(f"  Frames per Segment: {self.video.frames_per_segment}")

        print(f"\n【Paths】")
        print(f"  Project Root: {self.project_root}")
        print(f"  Data Dir: {self.path.data_dir}")
        print(f"  Output Dir: {self.path.output_dir}")

        # 验证配置
        errors = self.validate()
        if errors:
            print(f"\n【Configuration Errors】")
            for error in errors:
                print(f"  ✗ {error}")
        else:
            print(f"\n✓ Configuration is valid")

        print("="*60)


# 全局配置实例
settings = Settings()


# 便捷函数
def get_settings() -> Settings:
    """获取全局配置实例"""
    return settings


def reload_settings():
    """重新加载配置"""
    global settings
    # 重新加载.env文件
    _load_env_file(PROJECT_ROOT / '.env')
    settings = Settings()
    return settings


if __name__ == "__main__":
    # 测试配置加载
    settings.print_summary()
