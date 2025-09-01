# -*- coding: utf-8 -*-
import json
from crawlo import Spider, Request
from crawlo.utils.log import get_logger

from examples.gxb.items import TelecomLicenseItem
from examples.gxb.settings import HEADERS, COOKIES


logger = get_logger(__name__)

class TelecomDeviceLicensesSpider(Spider):
    name = 'telecom_device'
    allowed_domains = ['ythzxfw.miit.gov.cn']
    # API 的基础 URL
    base_api_url = 'https://ythzxfw.miit.gov.cn/oldyth/user-center/tbAppSearch/selectResult'

    # 配置：起始页码和结束页码
    start_page = 1
    end_page = 26405
    data = {
        "categoryId": "144",
        "currentPage": 1,
        "pageSize": 5,
        "searchContent": ""
    }


    def start_requests(self):
        """从第一页开始，逐页发起请求"""

        yield Request(
            url=self.base_api_url,
            method='POST',
            headers=HEADERS,
            cookies=COOKIES,
            body=json.dumps(self.data),
            callback=self.parse,
            meta={'page': 1},
            dont_filter=True
        )


    def parse(self, response):
        """
        解析 API 响应
        :param response: Scrapy Response 对象
        """
        page = response.meta['page']
        self.logger.info(f"正在解析第 {page} 页，状态码: {response.status_code}")

        try:
            json_data = response.json()

            if not json_data.get('success'):
                self.logger.error(f"第 {page} 页请求失败: {json_data.get('msg', 'Unknown error')}")
                return

            # 提取总页数和总记录数（可选，用于验证）
            total_records = json_data.get("params", {}).get("tbAppArticle", {}).get("total", 0)
            self.logger.info(f"第 {page} 页，总记录数: {total_records}")

            article_list = json_data.get("params", {}).get("tbAppArticle", {}).get("list", [])

            if not article_list:
                self.logger.warning(f"第 {page} 页未找到数据")
                return

            self.logger.info(f"第 {page} 页成功解析到 {len(article_list)} 条记录")

            # 将每条记录作为独立的 item yield 出去
            for item in article_list:
                # 清洗数据：移除 HTML 标签
                cleaned_item = self.clean_item(item)
                item = TelecomLicenseItem()
                item['license_number'] = cleaned_item.get('articleField01')
                item['device_name'] = cleaned_item.get('articleField02')
                item['device_model'] = cleaned_item.get('articleField03')
                item['applicant'] = cleaned_item.get('articleField04')
                item['manufacturer'] = cleaned_item.get('articleField05')
                item['issue_date'] = cleaned_item.get('articleField06')
                item['expiry_date'] = cleaned_item.get('articleField07')
                item['certificate_type'] = cleaned_item.get('articleField08')
                item['remarks'] = cleaned_item.get('articleField09')
                item['certificate_status'] = cleaned_item.get('articleField10')
                item['origin'] = cleaned_item.get('articleField11')
                item['article_id'] = cleaned_item.get('articleId')
                item['article_edit_date'] = cleaned_item.get('articleEdate')
                item['create_time'] = cleaned_item.get('createTime')
                yield item

            # --- 自动翻页逻辑 ---
            # 检查是否还有下一页
            # 方法1：根据当前页码和预设的总页数
            if page < self.end_page:
                next_page = page + 1
                self.data['currentPage'] = next_page
                self.logger.debug(f"准备爬取下一页: {next_page}")
                yield Request(
                    url=self.base_api_url,
                    method='POST',
                    headers=HEADERS,
                    cookies=COOKIES,
                    body=json.dumps(self.data),
                    callback=self.parse,
                    meta={'page': next_page},
                    dont_filter=True
                )

        except Exception as e:
            self.logger.error(f"解析第 {page} 页响应失败: {e}", exc_info=True)

    @staticmethod
    def clean_item(item: dict) -> dict:
        """
        清洗单条记录，移除 HTML 标签等
        :param item: 原始字典
        :return: 清洗后的字典
        """
        import re
        html_tag_re = re.compile(r'<[^>]+>')
        cleaned = {}
        for k, v in item.items():
            if isinstance(v, str):
                # 移除 HTML 标签并去除首尾空白
                cleaned[k] = html_tag_re.sub('', v).strip()
            else:
                cleaned[k] = v
        return cleaned