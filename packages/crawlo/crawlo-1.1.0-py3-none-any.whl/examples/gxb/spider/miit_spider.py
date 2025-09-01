import json
import logging
import re

from crawlo import Request, Spider

from examples.gxb.items import RadioApprovalItem, TelecomLicenseItem

logger = logging.getLogger(__name__)

# 基础配置
BASE_URL = "https://ythzxfw.miit.gov.cn"
API_URL = BASE_URL + "/oldyth/user-center/tbAppSearch/selectResult"

# 任务配置
TASKS = {
    "radio_approval": {
        "name": "无线电设备型号核准",
        "category_id": "352",
        "item_class": RadioApprovalItem,
        "table": "radio_equipment_approval_new",
        "field_mapping": {
            'articleField01': 'approval_number',
            'articleField02': 'device_name',
            'articleField03': 'device_model',
            'articleField04': 'applicant',
            'articleField05': 'remarks',
            'articleField06': 'validity_period',
            'articleField07': 'frequency_tolerance',
            'articleField08': 'frequency_range',
            'articleField09': 'transmit_power',
            'articleField10': 'occupied_bandwidth',
            'articleField11': 'spurious_emission_limit',
            'articleField12': 'issue_date',
            'articleField13': 'approval_code',
            'articleField14': 'cmiit_id',
            'articleField15': 'modulation_mode',
            'articleField16': 'technology_system',
        }
    },
    "telecom_license": {
        "name": "电信设备进网许可证",
        "category_id": "144",
        "item_class": TelecomLicenseItem,
        "table": "telecom_device_licenses_new",
        "field_mapping": {
            'articleField01': 'license_number',
            'articleField02': 'device_name',
            'articleField03': 'device_model',
            'articleField04': 'applicant',
            'articleField05': 'manufacturer',
            'articleField06': 'issue_date',
            'articleField07': 'expiry_date',
            'articleField08': 'certificate_type',
            'articleField09': 'remarks',
            'articleField10': 'certificate_status',
            'articleField11': 'origin',
        }
    }
}

def strip_html(text: str) -> str:
    """去除 HTML 标签"""
    if not text or not isinstance(text, str):
        return text
    return re.sub(r'<[^>]+>', '', text)

class MiitSpider(Spider):
    name = "miit_spider"
    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
        'COOKIES_ENABLED': True,
        'RETRY_TIMES': 3,
        'DEFAULT_REQUEST_HEADERS': {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Authorization": "null",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": BASE_URL,
            "Pragma": "no-cache",
            "Referer": f"{BASE_URL}/oldyth/resultQuery",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        },
        'COOKIES_DEBUG': False,
        'LOG_LEVEL': 'INFO',
        'ITEM_PIPELINES': {
            'kyqb_scrapy.pipelines.DedupAndMySQLPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'kyqb_scrapy.middlewares.RandomUserAgentMiddleware': 400,
        }
    }

    def __init__(self, task='telecom_license', start_page=1, end_page=100, *args, **kwargs):
        super(MiitSpider, self).__init__(*args, **kwargs)

        if task not in TASKS:
            raise ValueError(f"不支持的任务: {task}")

        self.task_config = TASKS[task]
        self.category_id = self.task_config["category_id"]
        self.item_class = self.task_config["item_class"]
        self.table_name = self.task_config["table"]
        self.field_mapping = self.task_config["field_mapping"]

        self.start_page = int(start_page)
        self.end_page = int(end_page)
        self.page_size = 5

        # 设置 custom_settings 中的表名（动态）
        self.custom_settings['MYSQL_TABLE'] = self.table_name

        logger.info(f"🚀 启动任务: {self.task_config['name']}，页码 {self.start_page} ~ {self.end_page}")

    def start_requests(self):
        for page in range(self.start_page, self.end_page + 1):
            data = {
                "categoryId": self.category_id,
                "currentPage": page,
                "pageSize": self.page_size,
                "searchContent": ""
            }
            yield Request(
                url=API_URL,
                method='POST',
                body=json.dumps(data, separators=(',', ':')),
                headers={'Content-Type': 'application/json;charset=UTF-8'},
                callback=self.parse,
                meta={'page': page},
                dont_filter=True
            )

    def parse(self, response):
        page = response.meta['page']

        # 检查响应
        if response.status_code != 200:
            self.logger.error(f"❌ 第 {page} 页请求失败: HTTP {response.status}")
            return

        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            text = response.text
            if "升级浏览器" in text or "请尝试" in text:
                self.logger.error(f"⚠️ 检测到反爬: 请升级浏览器。响应片段: {text[:300]}")
            else:
                self.logger.error(f"JSON解析失败: {text[:300]}")
            return

        if not result.get("success"):
            msg = result.get("msg", "未知错误")
            if "升级浏览器" in msg or "请尝试" in msg:
                self.logger.error(f"⚠️ 反爬提示: {msg}")
            else:
                self.logger.error(f"接口失败: {msg}")
            return

        raw_records = result["params"]["tbAppArticle"]["list"]
        self.logger.info(f"✅ 第 {page} 页获取 {len(raw_records)} 条数据")

        for record in raw_records:
            item = self.item_class()

            for src_key, dst_key in self.field_mapping.items():
                value = record.get(src_key, '')
                if isinstance(value, str):
                    value = strip_html(value)
                item[dst_key] = value

            yield item