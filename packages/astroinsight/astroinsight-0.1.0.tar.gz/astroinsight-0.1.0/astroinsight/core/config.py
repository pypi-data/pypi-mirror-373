"""
Configuration classes for AstroInsight
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class AstroInsightConfig:
    """配置类 - 用于AstroInsight的主要配置"""

    keyword: str
    search_paper_num: int = 2
    user_id: str = "default_user"
    compression: bool = True
    output_path: str = "./temp"

    def __post_init__(self):
        """初始化后处理"""
        # 确保输出路径存在
        Path(self.output_path).mkdir(parents=True, exist_ok=True)

        # 验证参数
        if self.search_paper_num <= 0:
            raise ValueError("search_paper_num must be positive")
        if not self.keyword.strip():
            raise ValueError("keyword cannot be empty")


@dataclass
class APIConfig:
    """API配置类"""

    # 大模型API配置
    mineru_api_token: Optional[str] = None
    qwen_api_token: Optional[str] = None
    deepseek_api_token: Optional[str] = None
    deepseek_api_base_url: str = "https://api.deepseek.com/v1"

    # 数据库配置
    neo4j_username: Optional[str] = None
    neo4j_password: Optional[str] = None
    neo4j_host: str = "localhost"
    neo4j_port: str = "7687"

    # Redis配置
    redis_server: str = "127.0.0.1"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db_index: int = 0

    def __post_init__(self):
        """从环境变量加载配置"""
        self.mineru_api_token = self.mineru_api_token or os.getenv("MINERU_API_TOKEN")
        self.qwen_api_token = self.qwen_api_token or os.getenv("QWEN_API_TOKEN")
        self.deepseek_api_token = self.deepseek_api_token or os.getenv(
            "DEEPSEEK_API_TOKEN"
        )
        self.neo4j_username = self.neo4j_username or os.getenv("NEO4J_USERNAME")
        self.neo4j_password = self.neo4j_password or os.getenv("NEO4J_PASSWORD")
        self.redis_password = self.redis_password or os.getenv("REDIS_PASSWORD")
