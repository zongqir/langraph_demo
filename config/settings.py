"""
配置管理模块
负责加载和管理所有系统配置
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# 项目根目录（settings.py的上两级）
_PROJECT_ROOT = Path(__file__).parent.parent

# 尝试多个可能的环境文件位置
_POSSIBLE_ENV_FILES = [
    _PROJECT_ROOT / "config.env",
    _PROJECT_ROOT / ".env",
]

# 找到第一个存在的环境文件
_ENV_FILE = None
for env_file in _POSSIBLE_ENV_FILES:
    if env_file.exists():
        _ENV_FILE = env_file
        break

# 如果都不存在，使用 config.env（会在后续创建时使用）
if _ENV_FILE is None:
    _ENV_FILE = _PROJECT_ROOT / "config.env"


class Settings(BaseSettings):
    """系统配置类"""
    
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )
    
    # API配置
    siliconflow_api_key: str = Field(
        default="sk-rqjbncqjhegvtuuogbnpalmmpjwkqlzolqjqrwnevfavngly",
        alias="SILICONFLOW_API_KEY"
    )
    siliconflow_base_url: str = Field(
        default="https://api.siliconflow.cn/v1",
        alias="SILICONFLOW_BASE_URL"
    )
    
    # 模型配置
    default_model: str = Field(
        default="Qwen/Qwen2.5-7B-Instruct",
        alias="DEFAULT_MODEL"
    )
    embedding_model: str = Field(
        default="BAAI/bge-large-zh-v1.5",
        alias="EMBEDDING_MODEL"
    )
    
    # 系统配置
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    max_conversation_history: int = Field(default=10, alias="MAX_CONVERSATION_HISTORY")
    vector_store_path: str = Field(default="./data/vector_store", alias="VECTOR_STORE_PATH")
    
    # 业务配置
    customer_service_name: str = Field(default="智能客服小助手", alias="CUSTOMER_SERVICE_NAME")
    company_name: str = Field(default="示例科技有限公司", alias="COMPANY_NAME")
    
    # 项目路径
    project_root: Path = Field(default_factory=lambda: _PROJECT_ROOT)
    
    @property
    def data_dir(self) -> Path:
        """数据目录"""
        return self.project_root / "data"
    
    @property
    def logs_dir(self) -> Path:
        """日志目录"""
        return self.project_root / "logs"
    
    def ensure_dirs(self):
        """确保必要的目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        Path(self.vector_store_path).mkdir(parents=True, exist_ok=True)


# 全局配置实例
settings = Settings()
settings.ensure_dirs()

