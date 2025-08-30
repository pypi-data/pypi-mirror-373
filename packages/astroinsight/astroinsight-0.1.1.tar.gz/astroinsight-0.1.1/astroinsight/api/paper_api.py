"""
Paper API class for AstroInsight
"""

import logging
from typing import Any, Dict, Optional

from ..core.astroinsight import AstroInsight
from ..core.config import AstroInsightConfig

logger = logging.getLogger(__name__)


class PaperAPI:
    """论文API封装类 - 提供论文生成的API接口"""

    def __init__(self, api_config: Optional[Dict[str, Any]] = None):
        """
        初始化PaperAPI

        Args:
            api_config: API配置字典
        """
        self.api_config = api_config or {}
        logger.info("PaperAPI initialized")

    def generate_paper(
        self, keyword: str, search_paper_num: int = 2, **kwargs
    ) -> Dict[str, Any]:
        """
        生成论文API

        Args:
            keyword: 研究关键词
            search_paper_num: 搜索论文数量
            **kwargs: 其他配置参数

        Returns:
            API响应字典

        Example:
            >>> api = PaperAPI()
            >>> response = api.generate_paper("machine learning", 3)
            >>> print(f"Success: {response['success']}")
        """
        try:
            logger.info(f"API: Starting paper generation for keyword: {keyword}")

            # 创建配置
            config = AstroInsightConfig(
                keyword=keyword, search_paper_num=search_paper_num, **kwargs
            )

            # 创建AstroInsight实例
            astro = AstroInsight(config)

            # 执行生成
            result = astro.generate_paper()

            logger.info(f"API: Paper generation completed successfully")

            return {
                "success": True,
                "data": {
                    "task_id": result.get("task_id"),
                    "status": result.get("status"),
                    "steps": result.get("steps", []),
                    "result_file": result.get("result_file", ""),
                    "keyword": keyword,
                    "search_paper_num": search_paper_num,
                },
                "message": "论文生成任务已创建并完成",
            }

        except Exception as e:
            logger.error(f"API: Paper generation failed: {str(e)}")

            return {
                "success": False,
                "error": str(e),
                "message": "论文生成失败",
                "data": {"keyword": keyword, "search_paper_num": search_paper_num},
            }

    def generate_paper_async(
        self, keyword: str, search_paper_num: int = 2, **kwargs
    ) -> Dict[str, Any]:
        """
        异步生成论文API（立即返回任务ID）

        Args:
            keyword: 研究关键词
            search_paper_num: 搜索论文数量
            **kwargs: 其他配置参数

        Returns:
            API响应字典
        """
        try:
            logger.info(f"API: Starting async paper generation for keyword: {keyword}")

            # 创建配置
            config = AstroInsightConfig(
                keyword=keyword, search_paper_num=search_paper_num, **kwargs
            )

            # 创建AstroInsight实例
            astro = AstroInsight(config)

            logger.info(f"API: Async paper generation task created")

            return {
                "success": True,
                "data": {
                    "task_id": astro.task_id,
                    "status": "created",
                    "keyword": keyword,
                    "search_paper_num": search_paper_num,
                },
                "message": "异步论文生成任务已创建",
            }

        except Exception as e:
            logger.error(f"API: Async paper generation failed: {str(e)}")

            return {
                "success": False,
                "error": str(e),
                "message": "异步论文生成任务创建失败",
                "data": {"keyword": keyword, "search_paper_num": search_paper_num},
            }

    def get_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态API

        Args:
            task_id: 任务ID

        Returns:
            API响应字典
        """
        try:
            logger.info(f"API: Getting status for task: {task_id}")

            # 这里应该实现任务状态查询逻辑
            # 暂时返回模拟状态
            return {
                "success": True,
                "data": {
                    "task_id": task_id,
                    "status": "completed",
                    "message": "任务已完成",
                },
            }

        except Exception as e:
            logger.error(f"API: Failed to get status for task {task_id}: {str(e)}")

            return {
                "success": False,
                "error": str(e),
                "message": "获取任务状态失败",
                "data": {"task_id": task_id},
            }
