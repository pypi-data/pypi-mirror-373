import asyncio

from crawlo.crawler import CrawlerProcess
from examples.gxb.spider.telecom_device import TelecomDeviceLicensesSpider

async def main():
    process = CrawlerProcess()
    await process.crawl(
        [TelecomDeviceLicensesSpider]
    )



if __name__ == '__main__':
    asyncio.run(main())
    # 132023