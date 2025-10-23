"""
配置管理模块
负责加载和管理所有系统配置
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """系统配置类"""
    
    # API配置
    siliconflow_api_key: str = Field(alias="SILICONFLOW_API_KEY")
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
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
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

