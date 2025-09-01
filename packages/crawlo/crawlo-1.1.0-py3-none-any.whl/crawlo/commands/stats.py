#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
# @Time    : 2025-08-31 22:36
# @Author  : crawl-coder
# @Desc    : 命令行入口：crawlo stats，查看最近运行的爬虫统计信息。
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from crawlo.utils.log import get_logger


logger = get_logger(__name__)

# 默认存储目录（相对于项目根目录）
STATS_DIR = "logs/stats"


def get_stats_dir() -> Path:
    """
    获取统计文件存储目录，优先使用项目根下的 logs/stats/
    如果不在项目中，回退到当前目录
    """
    # 尝试查找项目根目录（通过 crawlo.cfg）
    current = Path.cwd()
    for _ in range(10):
        if (current / "crawlo.cfg").exists():
            return current / STATS_DIR
        if current == current.parent:
            break
        current = current.parent

    # 回退：使用当前目录下的 logs/stats
    return Path.cwd() / STATS_DIR


def record_stats(crawler):
    """
    【供爬虫运行时调用】记录爬虫结束后的统计信息到 JSON 文件
    需在 Crawler 的 closed 回调中调用
    """
    spider_name = getattr(crawler.spider, "name", "unknown")
    stats = crawler.stats.get_stats() if crawler.stats else {}

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stats_dir = Path(get_stats_dir())
    stats_dir.mkdir(parents=True, exist_ok=True)

    filename = stats_dir / f"{spider_name}_{timestamp}.json"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({
                "spider": spider_name,
                "timestamp": datetime.now().isoformat(),
                "stats": stats
            }, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"📊 Stats saved for spider '{spider_name}' → {filename}")
    except Exception as e:
        logger.error(f"Failed to save stats for '{spider_name}': {e}")


def load_all_stats() -> Dict[str, list]:
    """
    加载所有已保存的统计文件，按 spider name 分组
    返回: {spider_name: [stats_record, ...]}
    """
    stats_dir = get_stats_dir()
    if not stats_dir.exists():
        return {}

    result = {}
    json_files = sorted(stats_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)

    for file in json_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            spider_name = data.get("spider", "unknown")
            result.setdefault(spider_name, []).append(data)
        except Exception as e:
            logger.warning(f"Failed to load stats file {file}: {e}")
    return result


def format_value(v: Any) -> str:
    """格式化值，防止太长或不可打印"""
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def main(args):
    """
    主函数：查看统计信息
    用法:
        crawlo stats                 → 显示所有爬虫最近一次运行
        crawlo stats myspider        → 显示指定爬虫所有历史记录
        crawlo stats myspider --all  → 显示所有历史（同上）
    """
    if len(args) > 2:
        print("Usage: crawlo stats [spider_name] [--all]")
        return 1

    spider_name = None
    show_all = False

    if args:
        spider_name = args[0]
        show_all = "--all" in args or "-a" in args

    # 加载所有 stats
    all_stats = load_all_stats()
    if not all_stats:
        print("📊 No stats found. Run a spider first.")
        print(f"💡 Stats are saved in: {get_stats_dir()}")
        return 0

    if not spider_name:
        # 显示每个爬虫最近一次运行
        print("📊 Recent Spider Statistics (last run):")
        print("-" * 60)
        for name, runs in all_stats.items():
            latest = runs[0]
            print(f"🕷️  {name} ({latest['timestamp'][:19]})")
            stats = latest["stats"]
            for k in sorted(stats.keys()):
                print(f"    {k:<30} {format_value(stats[k])}")
            print()
        return 0

    else:
        # 查看指定爬虫
        if spider_name not in all_stats:
            print(f"📊 No stats found for spider '{spider_name}'")
            available = ', '.join(all_stats.keys())
            if available:
                print(f"💡 Available spiders: {available}")
            return 1

        runs = all_stats[spider_name]
        if show_all:
            print(f"📊 All runs for '{spider_name}' ({len(runs)} runs):")
        else:
            runs = runs[:1]
            print(f"📊 Last run for '{spider_name}':")

        print("-" * 60)
        for run in runs:
            print(f"⏱️  Timestamp: {run['timestamp']}")
            stats = run["stats"]
            for k in sorted(stats.keys()):
                print(f"    {k:<30} {format_value(stats[k])}")
            print("─" * 60)
        return 0


if __name__ == "__main__":
    """
    支持直接运行：
        python -m crawlo.commands.stats
    """
    sys.exit(main(sys.argv[1:]))