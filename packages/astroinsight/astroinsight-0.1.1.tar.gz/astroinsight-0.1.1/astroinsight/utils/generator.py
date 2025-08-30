"""
Convenience functions for AstroInsight
"""

from typing import Any, Dict

from ..core.astroinsight import AstroInsight
from ..core.config import AstroInsightConfig


def generate_paper(keyword: str, search_paper_num: int = 2, **kwargs) -> Dict[str, Any]:
    """
    便捷的论文生成函数

    Args:
        keyword: 研究关键词
        search_paper_num: 搜索论文数量
        **kwargs: 其他配置参数

    Returns:
        包含生成结果的字典

    Example:
        >>> result = generate_paper("machine learning", 3)
        >>> print(f"Task ID: {result['task_id']}")
    """
    # 创建配置
    config = AstroInsightConfig(
        keyword=keyword, search_paper_num=search_paper_num, **kwargs
    )

    # 创建AstroInsight实例
    astro = AstroInsight(config)

    # 执行生成
    return astro.generate_paper()


def generate_paper_async(keyword: str, search_paper_num: int = 2, **kwargs) -> str:
    """
    异步论文生成函数（返回任务ID）

    Args:
        keyword: 研究关键词
        search_paper_num: 搜索论文数量
        **kwargs: 其他配置参数

    Returns:
        任务ID字符串

    Example:
        >>> task_id = generate_paper_async("AI research", 2)
        >>> print(f"Task started: {task_id}")
    """
    # 创建配置
    config = AstroInsightConfig(
        keyword=keyword, search_paper_num=search_paper_num, **kwargs
    )

    # 创建AstroInsight实例
    astro = AstroInsight(config)

    # 返回任务ID
    return astro.task_id
