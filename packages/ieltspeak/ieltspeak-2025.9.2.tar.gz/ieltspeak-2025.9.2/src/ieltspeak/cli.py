import click
from typing import Dict, Any, Union
from .data_loader import TopicDataLoader
from .update_data import IELTSSpider
import asyncio


# 创建全局数据加载器实例
data_loader = TopicDataLoader()


@click.group()
def cli() -> None:
    """IELTS口语话题生成工具，题目来源雅思哥口语题库（ieltsbro.com）"""
    pass

@cli.command()
def update_data():
    """更新题库，数据来源（https://ielts-bro-proxy.duzhuo.icu/）"""
    spider = IELTSSpider()
    asyncio.run(spider.run())


@cli.command()
@click.option(
    "--part",
    "-p",
    required=True,
    type=click.Choice(["1", "2and3"], case_sensitive=False),
    help="话题部分（P1 或 P2&3）",
)
@click.option(
    "--category",
    "-c",
    required=True,
    type=click.Choice(["event", "thing", "person", "location"], case_sensitive=False),
    help="话题类别（事件，事物，人物，地点）",
)
def get_topic(part: str, category: str) -> int:
    """获取随机话题"""
    result: Union[Dict[str, Any], str] = data_loader.get_topic(part, category)

    # 检查返回值是否为字符串（错误信息）
    if isinstance(result, str):
        click.echo(result)
        return 1

    # 获取话题数据和part信息
    topic = result['topic']
    part_info = result['part_info']

    # 输出话题信息
    click.echo(f"Part: {part_info.get('part_name', 'N/A')}")
    click.echo(f"Topic: {topic.get('topic_name', 'N/A')}")
    click.echo("---")
    questions = topic.get("questions")
    if part == '1':
        for q in questions:
            click.echo(f"{q}")
    elif part == '2and3':
        click.echo("Part 2:")
        click.echo(topic.get("preview_question", "No Part2 question available."))
        click.echo("\nPart 3:")
        for q in questions:
            click.echo(f"- {q}")

    return 0


def main() -> None:
    """主入口函数"""
    cli()


if __name__ == "__main__":
    main()
