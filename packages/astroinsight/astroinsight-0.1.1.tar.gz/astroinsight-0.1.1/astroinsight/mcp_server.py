#!/usr/bin/env python3
"""
AstroInsight MCP (Model Context Protocol) 服务器
为阿里云等平台提供AI天文洞察服务
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

# MCP 相关导入
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool
except ImportError:
    print("❌ 需要安装 mcp 包: pip install mcp")
    sys.exit(1)

# AstroInsight 相关导入
try:
    from .core.astroinsight import AstroInsight
    from .core.config import Config
except ImportError:
    # 如果作为独立脚本运行
    sys.path.append(str(Path(__file__).parent.parent))
    try:
        from astroinsight.core.astroinsight import AstroInsight
        from astroinsight.core.config import Config
    except ImportError:
        print("❌ 无法导入 AstroInsight 核心模块")
        sys.exit(1)


class AstroInsightMCPServer:
    """AstroInsight MCP 服务器"""

    def __init__(self):
        self.server = Server("astroinsight")
        self.astroinsight = None
        self.config = None
        self.setup_handlers()

    def setup_handlers(self):
        """设置 MCP 处理器"""

        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """列出可用工具"""
            tools = [
                Tool(
                    name="analyze_paper",
                    description="分析天文论文，提取关键信息和洞察",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "paper_path": {
                                "type": "string",
                                "description": "论文PDF文件路径或arXiv ID",
                            },
                            "analysis_type": {
                                "type": "string",
                                "enum": [
                                    "summary",
                                    "entities",
                                    "hypothesis",
                                    "technical",
                                ],
                                "description": "分析类型",
                            },
                        },
                        "required": ["paper_path"],
                    },
                ),
                Tool(
                    name="generate_insights",
                    description="基于论文内容生成天文洞察和假设",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "context": {
                                "type": "string",
                                "description": "分析上下文或问题描述",
                            },
                            "focus_area": {
                                "type": "string",
                                "description": "关注的天文领域",
                            },
                        },
                        "required": ["context"],
                    },
                ),
                Tool(
                    name="search_related_work",
                    description="搜索相关的研究工作和论文",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "搜索查询"},
                            "max_results": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 50,
                                "default": 10,
                                "description": "最大结果数量",
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="technical_optimization",
                    description="提供技术优化建议",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "current_approach": {
                                "type": "string",
                                "description": "当前的技术方法描述",
                            },
                            "optimization_goal": {
                                "type": "string",
                                "description": "优化目标",
                            },
                        },
                        "required": ["current_approach"],
                    },
                ),
            ]
            return ListToolsResult(tools=tools)

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> CallToolResult:
            """处理工具调用"""
            try:
                # 初始化 AstroInsight
                if self.astroinsight is None:
                    await self.initialize_astroinsight()

                if name == "analyze_paper":
                    result = await self.analyze_paper(arguments)
                elif name == "generate_insights":
                    result = await self.generate_insights(arguments)
                elif name == "search_related_work":
                    result = await self.search_related_work(arguments)
                elif name == "technical_optimization":
                    result = await self.technical_optimization(arguments)
                else:
                    result = {"error": f"未知工具: {name}"}

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(result, ensure_ascii=False, indent=2),
                        )
                    ]
                )

            except Exception as e:
                logging.error(f"工具调用失败: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"错误: {str(e)}")]
                )

    async def initialize_astroinsight(self):
        """初始化 AstroInsight"""
        try:
            # 加载配置
            config_path = Path("config.yaml")
            if config_path.exists():
                self.config = Config.from_yaml(str(config_path))
            else:
                # 使用默认配置
                self.config = Config()

            # 初始化 AstroInsight
            self.astroinsight = AstroInsight(self.config)
            logging.info("AstroInsight 初始化成功")

        except Exception as e:
            logging.error(f"AstroInsight 初始化失败: {e}")
            raise

    async def analyze_paper(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """分析论文"""
        paper_path = arguments.get("paper_path")
        analysis_type = arguments.get("analysis_type", "summary")

        if not paper_path:
            return {"error": "论文路径不能为空"}

        try:
            # 根据分析类型执行不同的分析
            if analysis_type == "summary":
                result = await self.astroinsight.analyze_paper_summary(paper_path)
            elif analysis_type == "entities":
                result = await self.astroinsight.extract_entities(paper_path)
            elif analysis_type == "hypothesis":
                result = await self.astroinsight.generate_hypotheses(paper_path)
            elif analysis_type == "technical":
                result = await self.astroinsight.technical_analysis(paper_path)
            else:
                result = await self.astroinsight.analyze_paper_summary(paper_path)

            return {
                "success": True,
                "analysis_type": analysis_type,
                "paper_path": paper_path,
                "result": result,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "paper_path": paper_path}

    async def generate_insights(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """生成洞察"""
        context = arguments.get("context")
        focus_area = arguments.get("focus_area", "general")

        if not context:
            return {"error": "上下文不能为空"}

        try:
            insights = await self.astroinsight.generate_insights(context, focus_area)
            return {
                "success": True,
                "context": context,
                "focus_area": focus_area,
                "insights": insights,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "context": context}

    async def search_related_work(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """搜索相关工作"""
        query = arguments.get("query")
        max_results = arguments.get("max_results", 10)

        if not query:
            return {"error": "搜索查询不能为空"}

        try:
            results = await self.astroinsight.search_related_work(query, max_results)
            return {
                "success": True,
                "query": query,
                "max_results": max_results,
                "results": results,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "query": query}

    async def technical_optimization(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """技术优化建议"""
        current_approach = arguments.get("current_approach")
        optimization_goal = arguments.get("optimization_goal", "general")

        if not current_approach:
            return {"error": "当前方法描述不能为空"}

        try:
            suggestions = await self.astroinsight.technical_optimization(
                current_approach, optimization_goal
            )
            return {
                "success": True,
                "current_approach": current_approach,
                "optimization_goal": optimization_goal,
                "suggestions": suggestions,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "current_approach": current_approach,
            }

    async def run(self):
        """运行服务器"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="astroinsight",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None, experimental_capabilities=None
                    ),
                ),
            )


async def main():
    """主函数"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    server = AstroInsightMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
