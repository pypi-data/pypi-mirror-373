import json
import random
import requests
from .base_class import *
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

us = config_dict['base_ua']

# url 分析
import re


class SpiderUrlType:
    """
    解析用户传入的 URL，返回平台、类型、work_url 和 work_id
    平台:抖音,小红书
    类型:视频,用户,笔记
    return {
            "platform": "douyin",  如果platform="" 代表获取实拍
            "work_type": "user",
            "work_url": "http_xxxxxxxxxx",
            "work_id": "xxxxxx"
        }
    """

    def __init__(self, spider_url, url_type='video'):
        self.url_type = url_type
        self.spider_url = spider_url.strip()
        self.result = {
            "platform": "",
            "work_type": "",
            "work_url": "",
            "work_id": ""
        }
        if 'http' not in self.spider_url:
            return
        self._parse()

    def _parse(self):
        url = self.spider_url

        if 'douyin.com' in url:
            self.result['platform'] = 'douyin'
            self._parse_douyin(url)
        elif 'xiaohongshu.com' in url or 'xhslink.com' in url:
            self.result['platform'] = 'xhs'
            self._parse_xhs(url)
        elif 'weixin.' in url:
            self.result['platform'] = 'wx'
            self._parse_wechat(url)
        else:
            self.result['platform'] = ''

    def _parse_douyin(self, url):
        if self.url_type == 'video':
            # https://www.douyin.com/video/7212458016895292672
            match = re.search(r'/video/(\d+)', url)
            if match:
                self.result['work_type'] = 'video'
                self.result['work_id'] = match.group(1)
                self.result['work_url'] = f"https://www.douyin.com/video/{self.result['work_id']}"
        elif self.url_type == 'user':
            sec_uid = None

            # https://www.douyin.com/user/MS4wLjABAAAA6F3tMONSZUMg6fkxAyJP-bXtf1VlHsPFMq_ORQ1-zhE?from_tab_name=main
            if 'www.douyin.com' in url and 'MS4' in url:
                sec_uid = url.split('https://www.douyin.com/user/')[-1].split('?')[0]

            elif '://v.douyin.com' in url:
                url_pattern = r'://v\.douyin\.com/\w+/'
                matches = re.findall(url_pattern, url)
                if matches:
                    res = HttpJike.get(url=f'https{matches[0]}').ret_url
                    sec_uid = res.split('https://www.iesdouyin.com/share/user/')[-1].split('?')[0]

            if sec_uid:
                self.result['work_type'] = 'user'
                self.result['work_id'] = sec_uid
                self.result['work_url'] = f"https://www.douyin.com/user/{sec_uid}"

    def _parse_xhs(self, url):
        # 示例：https://www.xiaohongshu.com/explore/5f73e5f30000000001001a7a
        if '/explore/' in url:
            match = re.search(r'/explore/([a-zA-Z0-9]+)', url)
            if match:
                self.result['work_type'] = 'note'
                self.result['work_id'] = match.group(1)
                self.result['work_url'] = f"https://www.xiaohongshu.com/explore/{self.result['work_id']}"
        elif '/user/profile/' in url:
            match = re.search(r'/user/profile/([a-zA-Z0-9]+)', url)
            if match:
                self.result['work_type'] = 'user'
                self.result['work_id'] = match.group(1)
                self.result['work_url'] = f"https://www.xiaohongshu.com/user/profile/{self.result['work_id']}"

    def _parse_wechat(self, url):
        # 示例：https://mp.weixin.qq.com/s?__biz=MzA5NDY1NjMyMQ==&mid=2657502275&idx=1
        self.result['work_type'] = 'article'
        self.result['work_url'] = url
        biz_match = re.search(r'__biz=([a-zA-Z0-9+=]+)', url)
        if biz_match:
            self.result['work_id'] = biz_match.group(1)

    def get_result(self):
        return self.result


# requests 封装
class HttpJike(object):
    us = us

    def __init__(self):
        self.status_code = 500
        self.msg = 'ok'
        self.text = None
        self.json = None
        self.ret_url = None

    # cookie 分隔
    @staticmethod
    def cookie_format(cookie):
        cookie_dict = {}
        c = cookie.split(";")
        for i in c:
            cc = i.split('=')
            if len(cc) > 1:
                cookie_dict[str(cc[0]).strip()] = str(cc[1]).strip()
            else:
                cookie_dict[str(cc[0]).strip()] = ''
        return cookie_dict

    # ip代理 隧道代理
    @staticmethod
    def proxies_choose(p=1, httpx=0):
        # 注意:目前只有 1,2 两个可以使用  httpx特殊请求
        if p is None:
            p = random.randint(1, 2)

        proxy = config_dict["proxy"]["tunnel"][f"proxy_{p}"]['proxy']
        port = config_dict["proxy"]["tunnel"][f"proxy_{p}"]['port']
        acc = config_dict["proxy"]["tunnel"][f"proxy_{p}"]['acc']
        pwd = config_dict["proxy"]["tunnel"][f"proxy_{p}"]['pwd']

        proxies = {
            "http": f"http://{acc}:{pwd}@{proxy}:{port}/",
            "https": f"http://{acc}:{pwd}@{proxy}:{port}/"
        }
        if httpx == 1:
            proxies = {
                "http://": f"http://{acc}:{pwd}@{proxy}:{port}/",
                "https://": f"http://{acc}:{pwd}@{proxy}:{port}/"
            }
        return proxies

    # scrapy 代理选择 数据返回
    @classmethod
    def proxies_choose_dict(cls, p):
        # 注意:目前只有 1,2,3 两个可以使用
        proxies_dict = {
            'proxy': config_dict["proxy"]["tunnel"][f"proxy_{p}"]['proxy'],
            'port': config_dict["proxy"]["tunnel"][f"proxy_{p}"]['port'],
            'acc': config_dict["proxy"]["tunnel"][f"proxy_{p}"]['acc'],
            'pwd': config_dict["proxy"]["tunnel"][f"proxy_{p}"]['pwd']
        }
        return proxies_dict

    # 异步代理 的使用
    @staticmethod
    def aiohttp_proxy():
        ret = []
        ip_tunnel = config_dict['proxy']['tunnel']
        for i in ip_tunnel:
            ret.append({
                'proxy': f'http://{ip_tunnel[i]["proxy"]}:15818',
                'a': ip_tunnel[i]['acc'],
                'p': ip_tunnel[i]['pwd'],
            })
        return ret

    @staticmethod
    def get_headers(headers):
        if headers is None:
            return config_dict['base_headers']
        return headers

    @classmethod
    def get(cls, url, headers=None, proxies=None):
        req = cls()
        try:
            response = requests.get(
                url=url,
                headers=cls.get_headers(headers=headers),
                proxies=proxies
            )
            req.status_code = response.status_code
            req.ret_url = response.url
            req.text = response.text
            req.json = response.json()

            if response.status_code != 200:
                req.msg = '状态码错误'
        except Exception as e:
            req.msg = f'err {e}'
        return req

    @classmethod
    def post(cls, url, headers=None, data=None):
        req = cls()
        try:
            response = requests.post(
                url=url,
                headers=cls.get_headers(headers=headers),
                data=json.dumps(data),
            )
            req.status_code = response.status_code
            req.text = response.text
            req.json = response.json()

            if response.status_code != 200:
                req.msg = '状态码错误'
        except Exception as e:
            req.msg = f'err {e}'
        return req

    # 代理
    @classmethod
    def http_ip(cls, ip):
        proxies = {
            'https': ip,
            'http': ip
        }
        return proxies

    # 返回一个http代理
    @classmethod
    def http_proxy(cls):
        return {'https': '49.70.176.21:31919', 'http': '49.70.176.21:31919'}

    @classmethod
    def params_link(cls, url, params):
        return f"{url}?" f"{'&'.join([f'{k}={v}' for k, v in params.items()])}"

    @classmethod
    def base_headers(cls):
        try:
            return config_dict['base_headers']
        except:
            return {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.46'}

    @staticmethod
    def scrapy_simple_sitting(ts=0.1, tt=8, log=False, cookie=True):
        def_sitting = {
            "LOG_ENABLED": log,  # 日志开启
            "HTTPERROR_ALLOWED_CODES": [i for i in range(999)],  # 允许所有 HTTP 错误码
            "REDIRECT_ENABLED": False,  # 禁用重定向
            "DOWNLOAD_DELAY": ts,  # 每次请求间隔 1 秒
            "CONCURRENT_REQUESTS": tt,  # 最大并发请求数
            "DOWNLOADER_MIDDLEWARES": {
                'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 1,  # 启用代理中间件
            }
        }
        if cookie:
            def_sitting['COOKIES_ENABLED'] = False
        return def_sitting

    @staticmethod
    def requests_retry_session(
            retries=3,
            backoff_factor=0.5,
            status_forcelist=(500, 502, 503, 504),
            session=None,
    ):
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    @staticmethod
    def spider_url_type(spider_url, url_type='video'):
        return SpiderUrlType(spider_url, url_type=url_type).get_result()
