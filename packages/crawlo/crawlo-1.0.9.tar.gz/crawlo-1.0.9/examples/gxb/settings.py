import platform

PROXY_ENABLED = True
PROJECT_PACKAGE = 'gxb'

# API 地址
PROXY_API_URL = 'http://123.56.42.142:5000/proxy/getitem/'

# 提取方式（根据实际返回结构选择）
PROXY_EXTRACTOR = "proxy"
# 或
# from utils.proxy_extractors import custom_extractor_proxy
# PROXY_EXTRACTOR = custom_extractor_proxy

# 刷新间隔
PROXY_REFRESH_INTERVAL = 5

CONCURRENCY = 3

# 超时时间
PROXY_API_TIMEOUT = 10

if platform.system() == "Windows":
    MYSQL_HOST = "pc-2ze9oh2diu5e5firh.rwlb.rds.aliyuncs.com"
else:
    MYSQL_HOST = "tianmai-k8s-dmadmin-x.rwlb.rds.aliyuncs.com"

# 数据库端口
MYSQL_PORT = 3306
# 数据库用户名
MYSQL_USER = "data_collection"
# 数据库密码
MYSQL_PASSWORD = "CRNabzFQ2H"
# 数据库名
MYSQL_DB = "cxzx_xm"
# 数据库编码
MYSQL_TABLE = "telecom_device_licenses_v4"

MYSQL_BATCH_SIZE = 100

PIPELINES = [
    'crawlo.pipelines.console_pipeline.ConsolePipeline',
    # 'crawlo.pipelines.mysql_pipeline.AsyncmyMySQLPipeline', # 可选：存入 MySQL
]


HEADERS = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Authorization": "null",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://ythzxfw.miit.gov.cn",
            "Pragma": "no-cache",
            "Referer": "https://ythzxfw.miit.gov.cn/oldyth/resultQuery",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        }

COOKIES = {
    "wzws_sessionid": "oGivsIOAMjQwZTozYjM6MzBiMjo3MWMwOjg0NmY6MzQ4OTozNWZjOjEyMTGBOGY2OTQ2gjdjYmMyNQ==",
    "ariauseGraymode": "false",
    "Hm_lvt_a73626d298a849004aacc34159f68abd": "1755909741,1756084244,1756256541,1756344453",
    "Hm_lpvt_a73626d298a849004aacc34159f68abd": "1756344453",
    "HMACCOUNT": "08DF0D235A291EAA"
}
