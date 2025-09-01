#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
# @Time    : 2025-08-31 22:36
# @Author  : crawl-coder
# @Desc    : 命令行入口：crawlo run <spider_name>|all，用于运行指定爬虫。
"""
import sys
import asyncio
import configparser
from pathlib import Path
from importlib import import_module

from crawlo.crawler import CrawlerProcess
from crawlo.utils.log import get_logger
from crawlo.utils.project import get_settings
from crawlo.commands.stats import record_stats  # 自动记录 stats

logger = get_logger(__name__)


def get_project_root():
    """
    向上查找 crawlo.cfg 来确定项目根目录
    """
    current = Path.cwd()

    for _ in range(10):
        cfg = current / "crawlo.cfg"
        if cfg.exists():
            return current

        if current == current.parent:
            break
        current = current.parent

    return None


def main(args):
    """
    主函数：运行指定爬虫
    用法:
        crawlo run <spider_name>
        crawlo run all
    """
    if len(args) < 1:
        print("❌ Usage: crawlo run <spider_name>|all")
        print("💡 Examples:")
        print("   crawlo run baidu")
        print("   crawlo run all")
        return 1

    spider_arg = args[0]

    try:
        # 1. 查找项目根目录
        project_root = get_project_root()
        if not project_root:
            print("❌ Error: Cannot find 'crawlo.cfg'. Are you in a crawlo project?")
            print("💡 Tip: Run this command inside your project directory.")
            return 1

        project_root_str = str(project_root)
        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)

        # 2. 读取 crawlo.cfg 获取 settings 模块
        cfg_file = project_root / "crawlo.cfg"
        if not cfg_file.exists():
            print(f"❌ Error: crawlo.cfg not found in {project_root}")
            return 1

        config = configparser.ConfigParser()
        config.read(cfg_file, encoding="utf-8")

        if not config.has_section("settings") or not config.has_option("settings", "default"):
            print("❌ Error: Missing [settings] section or 'default' option in crawlo.cfg")
            return 1

        settings_module = config.get("settings", "default")
        project_package = settings_module.split(".")[0]

        # 3. 确保项目包可导入
        try:
            import_module(project_package)
        except ImportError as e:
            print(f"❌ Failed to import project package '{project_package}': {e}")
            return 1

        # 4. 加载 settings 和爬虫模块
        settings = get_settings()  # 此时已安全
        spider_modules = [f"{project_package}.spiders"]
        process = CrawlerProcess(settings=settings, spider_modules=spider_modules)

        # === 情况1：运行所有爬虫 ===
        if spider_arg.lower() == "all":
            spider_names = process.get_spider_names()
            if not spider_names:
                print("❌ No spiders found.")
                print("💡 Make sure:")
                print("   • Spiders are defined in 'spiders/'")
                print("   • They have a `name` attribute")
                print("   • Modules are imported (e.g. via __init__.py)")
                return 1

            print(f"🚀 Starting ALL {len(spider_names)} spider(s):")
            print("-" * 60)
            for name in sorted(spider_names):
                cls = process.get_spider_class(name)
                print(f"🕷️  {name:<20} {cls.__name__}")
            print("-" * 60)

            # 注册 stats 记录（每个爬虫结束时保存）
            for crawler in process.crawlers:
                crawler.signals.connect(record_stats, signal="spider_closed")

            # 并行运行所有爬虫（可改为串行：for name in ... await process.crawl(name)）
            asyncio.run(process.crawl(spider_names))
            print("✅ All spiders completed.")
            return 0

        # === 情况2：运行单个爬虫 ===
        spider_name = spider_arg
        if not process.is_spider_registered(spider_name):
            print(f"❌ Spider '{spider_name}' not found.")
            available = process.get_spider_names()
            if available:
                print("💡 Available spiders:")
                for name in sorted(available):
                    cls = process.get_spider_class(name)
                    print(f"   • {name} ({cls.__name__})")
            else:
                print("💡 No spiders found. Check your spiders module.")
            return 1

        spider_class = process.get_spider_class(spider_name)

        # 打印启动信息
        print(f"🚀 Starting spider: {spider_name}")
        print(f"📦 Project: {project_package}")
        print(f"CppClass: {spider_class.__name__}")
        print(f"📄 Module: {spider_class.__module__}")
        print("-" * 50)

        # 注册 stats 记录
        for crawler in process.crawlers:
            crawler.signals.connect(record_stats, signal="spider_closed")

        # 运行爬虫
        asyncio.run(process.crawl(spider_name))

        print("-" * 50)
        print("✅ Spider completed successfully!")
        return 0

    except KeyboardInterrupt:
        print("\n⚠️  Spider interrupted by user.")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.exception("Exception during 'crawlo run'")
        return 1


if __name__ == "__main__":
    """
    支持直接运行：
        python -m crawlo.commands.run spider_name
    """
    sys.exit(main(sys.argv[1:]))