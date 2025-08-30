"""
Main AstroInsight class for research paper generation
"""

import logging
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..utils.paper_generator import PaperGenerator
from .config import AstroInsightConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AstroInsight:
    """AstroInsight主类 - 提供研究论文生成的核心功能"""

    def __init__(self, config: AstroInsightConfig):
        """
        初始化AstroInsight

        Args:
            config: 配置对象
        """
        self.config = config
        self.task_id = self._generate_task_id()
        self.status = "initialized"
        self.result = None

        logger.info(f"AstroInsight initialized with task_id: {self.task_id}")

    def _generate_task_id(self) -> str:
        """生成唯一的任务ID"""
        return str(uuid.uuid4())

    def generate_paper(self) -> Dict[str, Union[str, List[str], str]]:
        """
        生成论文的主要方法

        Returns:
            包含任务信息的字典
        """
        try:
            self.status = "processing"
            logger.info(f"Starting paper generation for keyword: {self.config.keyword}")

            # 创建论文生成器
            generator = PaperGenerator(self.config)

            # 执行生成流程
            result = generator.generate()

            self.status = "completed"
            self.result = result

            logger.info(f"Paper generation completed successfully")

            return {
                "task_id": self.task_id,
                "steps": result.get("steps", []),
                "result_file": result.get("result_file", ""),
                "status": self.status,
                "keyword": self.config.keyword,
                "search_paper_num": self.config.search_paper_num,
            }

        except Exception as e:
            self.status = "failed"
            logger.error(f"Paper generation failed: {str(e)}")

            return {
                "task_id": self.task_id,
                "status": self.status,
                "error": str(e),
                "keyword": self.config.keyword,
            }

    def get_status(self) -> Dict[str, str]:
        """获取任务状态"""
        return {
            "task_id": self.task_id,
            "status": self.status,
            "keyword": self.config.keyword,
        }

    def get_result(self) -> Optional[Dict]:
        """获取任务结果"""
        return self.result

    def cancel(self) -> bool:
        """取消任务"""
        if self.status == "processing":
            self.status = "cancelled"
            logger.info(f"Task {self.task_id} cancelled")
            return True
        return False
