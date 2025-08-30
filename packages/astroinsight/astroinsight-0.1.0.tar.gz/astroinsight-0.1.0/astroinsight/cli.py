"""
Command line interface for AstroInsight
"""

import json
from pathlib import Path

import click

from .api.paper_api import PaperAPI
from .core.astroinsight import AstroInsight
from .core.config import AstroInsightConfig


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """AstroInsight - AI-powered research paper assistant"""
    pass


@cli.command()
@click.option("--keyword", "-k", required=True, help="研究关键词")
@click.option("--papers", "-p", default=2, help="搜索论文数量", type=int)
@click.option("--user-id", "-u", default="default", help="用户ID")
@click.option("--output", "-o", default="./temp", help="输出路径")
@click.option("--compression/--no-compression", default=True, help="是否启用论文压缩")
def generate(keyword, papers, user_id, output, compression):
    """生成研究论文"""
    try:
        click.echo(f"🚀 开始生成论文...")
        click.echo(f"📝 关键词: {keyword}")
        click.echo(f"📊 论文数量: {papers}")
        click.echo(f"👤 用户ID: {user_id}")
        click.echo(f"📁 输出路径: {output}")
        click.echo(f"🗜️  压缩: {'启用' if compression else '禁用'}")
        click.echo("-" * 50)

        # 创建配置
        config = AstroInsightConfig(
            keyword=keyword,
            search_paper_num=papers,
            user_id=user_id,
            compression=compression,
            output_path=output,
        )

        # 创建AstroInsight实例
        astro = AstroInsight(config)

        # 执行生成
        with click.progressbar(length=4, label="生成进度") as bar:
            result = astro.generate_paper()
            bar.update(4)

        click.echo("✅ 论文生成完成！")
        click.echo(f"🆔 任务ID: {result['task_id']}")
        click.echo(f"📄 结果文件: {result['result_file']}")
        click.echo(f"📋 执行步骤: {len(result['steps'])} 步")

        # 显示步骤详情
        for i, step in enumerate(result["steps"], 1):
            click.echo(f"  {i}. {step}")

    except Exception as e:
        click.echo(f"❌ 生成失败: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.option("--keyword", "-k", required=True, help="研究关键词")
@click.option("--papers", "-p", default=2, help="搜索论文数量", type=int)
@click.option("--user-id", "-u", default="default", help="用户ID")
@click.option("--output", "-o", default="./temp", help="输出路径")
def generate_async(keyword, papers, user_id, output):
    """异步生成研究论文（返回任务ID）"""
    try:
        click.echo(f"🚀 创建异步论文生成任务...")
        click.echo(f"📝 关键词: {keyword}")
        click.echo(f"📊 论文数量: {papers}")

        # 创建API实例
        api = PaperAPI()

        # 创建异步任务
        response = api.generate_paper_async(
            keyword=keyword,
            search_paper_num=papers,
            user_id=user_id,
            output_path=output,
        )

        if response["success"]:
            click.echo("✅ 异步任务创建成功！")
            click.echo(f"🆔 任务ID: {response['data']['task_id']}")
            click.echo(f"📊 状态: {response['data']['status']}")
            click.echo(f"💡 提示: 使用 'astroinsight status <task_id>' 查询进度")
        else:
            click.echo(f"❌ 任务创建失败: {response['message']}", err=True)

    except Exception as e:
        click.echo(f"❌ 操作失败: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("task_id")
def status(task_id):
    """查询任务状态"""
    try:
        click.echo(f"🔍 查询任务状态: {task_id}")

        # 创建API实例
        api = PaperAPI()

        # 查询状态
        response = api.get_status(task_id)

        if response["success"]:
            click.echo("✅ 状态查询成功！")
            click.echo(f"🆔 任务ID: {response['data']['task_id']}")
            click.echo(f"📊 状态: {response['data']['status']}")
            if "message" in response["data"]:
                click.echo(f"💬 消息: {response['data']['message']}")
        else:
            click.echo(f"❌ 状态查询失败: {response['message']}", err=True)

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.option("--keyword", "-k", required=True, help="研究关键词")
@click.option("--papers", "-p", default=2, help="搜索论文数量", type=int)
@click.option("--user-id", "-u", default="default", help="用户ID")
@click.option("--output", "-o", default="./temp", help="输出路径")
@click.option(
    "--format",
    "-f",
    default="text",
    type=click.Choice(["text", "json"]),
    help="输出格式",
)
def analyze(keyword, papers, user_id, output, format):
    """分析研究领域（不生成论文）"""
    try:
        click.echo(f"🔍 开始分析研究领域...")
        click.echo(f"📝 关键词: {keyword}")
        click.echo(f"📊 论文数量: {papers}")

        # 这里可以添加领域分析逻辑
        analysis_result = {
            "keyword": keyword,
            "paper_count": papers,
            "analysis": "研究领域分析功能正在开发中...",
        }

        if format == "json":
            click.echo(json.dumps(analysis_result, indent=2, ensure_ascii=False))
        else:
            click.echo("📊 分析结果:")
            click.echo(f"  关键词: {analysis_result['keyword']}")
            click.echo(f"  论文数量: {analysis_result['paper_count']}")
            click.echo(f"  分析: {analysis_result['analysis']}")

    except Exception as e:
        click.echo(f"❌ 分析失败: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
def config():
    """显示当前配置"""
    try:
        click.echo("⚙️  AstroInsight 配置信息")
        click.echo("=" * 40)

        # 显示环境变量配置
        import os

        config_vars = [
            "MINERU_API_TOKEN",
            "QWEN_API_TOKEN",
            "DEEPSEEK_API_TOKEN",
            "NEO4J_USERNAME",
            "NEO4J_PASSWORD",
            "REDIS_PASSWORD",
        ]

        for var in config_vars:
            value = os.getenv(var, "未设置")
            if var.endswith("_TOKEN") or var.endswith("_PASSWORD"):
                value = "***" if value != "未设置" else value
            click.echo(f"{var}: {value}")

        click.echo("=" * 40)
        click.echo("💡 提示: 在 .env 文件中设置这些环境变量")

    except Exception as e:
        click.echo(f"❌ 配置查询失败: {str(e)}", err=True)


def main():
    """主函数入口"""
    cli()


if __name__ == "__main__":
    main()
