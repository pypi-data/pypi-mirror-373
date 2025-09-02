import ctypes
import hashlib
import json
import os
import random
import socket
import struct
import time
import requests
from urllib.parse import urlparse
import execjs  # pip install PyExecJS
from pypinyin import pinyin, Style  # 汉字转拼音

from .base_class import *
from .es_class import EsDb
from .mysql_class import MysqlDb
from .pgsql_class import PgsqlDb
from .redis_class import RedisDb
from .time_class import TimeJike
from .http_class import HttpJike
from .func_class import ModeStatic
from .feishu_class import Feishu
from .zhihu_class import ZhihuSign

mode_time = TimeJike()  # 时间
mode_pros = ModeStatic()  # 静态函数
mode_feishu = Feishu()  # 飞书app api


# mode
class ModeFunc(EsDb, MysqlDb, RedisDb, PgsqlDb):
    def __init__(self):
        super().__init__()

    # >>>>----------------       数据库 redis数据库        ----------------<<<<<

    # 分词 老版本
    @staticmethod
    def word_split_old(txt, num=100, clear_myself="???"):
        import jieba

        try:
            num = int(num)
        except:
            num = 100

        # 文本过滤 [去空格 去数字]
        txt = str(txt).replace('\n', '').replace('\r', '').replace('\\', '')
        txt = str(txt).replace(' ', '')
        txt = str(txt).replace("'", " ").replace('"', ' ').replace('◕', ' ').replace(':', ' ').replace('：', ' ')
        words = jieba.lcut(txt)  # 使用精确模式对文本进行分词
        counts = {}  # 通过键值对的形式存储词语及其出现的次数

        # 单个词语不计算在内
        for word in words:
            if word != clear_myself:
                if len(word) == 1:
                    continue
                else:
                    counts[word] = counts.get(word, 0) + 1  # 遍历所有词语，每出现一次其对应的值加 1

        # 根据词语出现的次数进行从大到小排序
        items = list(counts.items())
        items.sort(key=lambda x: x[1], reverse=True)
        if num > len(items):
            num = len(items)

        # 分级选择
        data_list = []
        for i in range(num):
            data_dict = {}
            word, count = items[i]
            data_dict['word'] = word
            data_dict['count'] = count
            if count >= 100:
                data_dict['category'] = '100'
            elif count >= 50:
                data_dict['category'] = '50'
            elif count >= 10:
                data_dict['category'] = '10'
            elif count >= 7:
                data_dict['category'] = '7'
            elif count >= 4:
                data_dict['category'] = '4'
            else:
                data_dict['category'] = '1'
            data_list.append(data_dict)
            # print("{0:<5}{1:>5}".format(word, count))
        return data_list

    # 汉字 => 拼音
    def chinese_to_pinyin(self, chinese="你好", ret=1):
        """
            ret = 1  -->  [['ni3'], ['hao3']]
            ret = 2  -->  nh
            ret = 3  -->  n

            英文的全部转换为小写

            更多复杂判断 都在这里写
                符号开头的返回 ”other“
                数字开头的返回 ”number“
        """
        try:
            chinese = chinese.lower()
            if chinese:
                # 将中文转换为拼音，设置输出格式为带声调的拼音
                pinyin_list = pinyin(chinese, style=Style.TONE3)

                # 提取每个拼音的第一个字母
                first_letters = [p[0][0] for p in pinyin_list]

                # 将字母列表连接成字符串
                first_letters_string = ''.join(first_letters)
                if ret == 2:
                    return first_letters_string
                elif ret == 3:
                    first_word = first_letters_string[:1]
                    if first_word in config_dict['numbers'] or first_word in config_dict['numbers_str']:  # 数字开头
                        return "number"
                    elif first_word == ' ':
                        return "empty"
                    elif first_word not in config_dict['low_word']:  # 符号开头
                        return "other"
                    else:
                        return first_letters_string[:1]
                else:
                    return pinyin_list
            else:
                return "empty"
        except:
            return "other"

    # 关键词日数据 快速查询
    def keyword_day_index_select(self, keyword_list):
        # 获取今日时间戳 获取12个小时时间戳
        order_time = int(time.time()) - 600
        t0 = mode_time.zero_clock()
        if order_time < t0:
            order_time = t0 + 1
        if order_time < 1694491630:  # Bug修改
            order_time = 1694491630

        query1 = {
            "bool": {
                "filter": [
                    {
                        "terms": {
                            F_keyword: keyword_list
                        }
                    },
                    {
                        "range": {"update_time": {"gte": order_time}}
                    }
                ]
            }
        }
        is_in = []
        is_in_data = {}
        ret_hits_list = self.es_search_alias(table='douyin_keyword_index', query=query1, size=1000)
        if ret_hits_list:
            for index_x, i in enumerate(ret_hits_list):
                _s = i['_source']
                _id = i['_id']
                is_in.append(_id)
                is_in_data[f'{_id}'] = _s
        should_not = [i for i in keyword_list if str(i) not in is_in]
        return is_in, is_in_data, should_not

    # 巨量广告cookie
    def qianchuan_index_cookie(self):

        # 缓存到内存
        data_list = cache_get('jike_qianchuan_ad_cookie')
        if not data_list:
            data_list = []
            sql = f"SELECT * FROM `cd_task` WHERE id IN (17,27,33,38);"
            ret = self.mysql_db(method='s', table='cd_task', sql=sql)
            for i in ret:
                data_dict = {}
                json_data = eval(i[7])
                csrftoken = json_data['csrftoken']
                sid_tt = json_data['sid_tt']
                aadvid = json_data['aadvid']
                headers = {
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Origin': 'https://ad.ocean' + 'engine.com',
                    'Referer': f'https://ad.ocean' + f'engine.com/bp/material/traffic_analysis.html?aadvid={aadvid}',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                    'X-CSRFToken': csrftoken,
                }
                cookies = {'csrftoken': csrftoken, 'sid_tt': sid_tt}
                data_dict['headers'] = headers
                data_dict['cookies'] = cookies
                data_dict['aadvid'] = aadvid
                data_dict['sid_tt'] = sid_tt
                data_dict['csrftoken'] = csrftoken
                data_dict['id_id'] = i[0]
                data_list.append(data_dict)
            cache_set('jike_qianchuan_ad_cookie', data_list, 200)
        return data_list

    # 关键词日数据 数据分析
    @staticmethod
    def keyword_day_index_get(data):
        """
        原：[{'date': '2024-04-14', 'pv': 39078}, {'date': '2024-04-15', 'pv': 20346},
        变：[{'t': 1691164800, 'v': 2595}, {'t': 1691251200, 'v': 2292}, {'t': 1691337600, 'v': 2048}, {'t': 1691424000, 'v': 1965}, {'t': 1691510400, 'v': 2095}, {'t': 1691596800, 'v': 2503}, {'t': 1691683200, 'v': 2177}, {'t': 1691769600, 'v': 2166}, {'t': 1691856000, 'v': 1997}, {'t': 1691942400, 'v': 2025}, {'t': 1692028800, 'v': 2030}, {'t': 1692115200, 'v': 2159}, {'t': 1692201600, 'v': 2648}, {'t': 1692288000, 'v': 2107}, {'t': 1692374400, 'v': 2392}, {'t': 1692460800, 'v': 2378}, {'t': 1692547200, 'v': 2173}, {'t': 1692633600, 'v': 2093}, {'t': 1692720000, 'v': 2020}, {'t': 1692806400, 'v': 1969}, {'t': 1692892800, 'v': 2244}, {'t': 1692979200, 'v': 2924}, {'t': 1693065600, 'v': 2697}, {'t': 1693152000, 'v': 2454}, {'t': 1693238400, 'v': 2431}, {'t': 1693324800, 'v': 2221}, {'t': 1693411200, 'v': 2254}, {'t': 1693497600, 'v': 1748}, {'t': 1693584000, 'v': 2087}, {'t': 1693670400, 'v': 1912}]
        """
        day_index = []
        keyword_pv_trend = data.get('keyword_pv_trend')
        if keyword_pv_trend:
            for i in keyword_pv_trend:
                t = i['date']
                v = i['pv']
                timestamp1 = int(time.mktime(time.strptime(t, '%Y-%m-%d')))
                day_index.append({'t': timestamp1, 'v': v})
        return day_index

    # ip 信息
    def get_user_ip(self, ip):
        url = f'http://whois.pconline.com.cn/ipJson.jsp?ip={ip}&json=true'
        Default_return = {
            'ip': ip,
            'country': '',
            'province': '',
            'city': '',
            'isp': '',
            'city_id': '',
            'create_time': int(time.time()),
            'addr': '',
        }

        if ip == '101.35.29.36':
            return Default_return

        if ip.split('.')[0] == '127':
            return Default_return

        if ip.split('.')[0] == '192' and ip.split('.')[1] == '168':
            return Default_return

        # 请求
        try:
            res = HttpJike.post(url=url)
            if res.status_code == 200:
                data_data = res.json()
                country = data_data.get('country')
                city = data_data.get('city')
                city_id = data_data.get('cityCode')
                province = data_data.get('pro')
                addr = data_data.get('addr')

                isp = '其他'
                for k in ['电信', '移动', '联通']:
                    if k in addr:
                        isp = k
                        break

                self.mysql_db(method="insert", table='member_ips', save_data={
                    'ip': ip,
                    'country': country,
                    'province': province,
                    'city': city,
                    'isp': isp,
                    'city_id': str(city_id),
                    'create_time': int(time.time()),
                    'addr': addr,
                }, conn_tp=5)
                return {
                    'ip': ip,
                    'country': country,
                    'province': province,
                    'city': city,
                    'isp': isp,
                    'city_id': str(city_id),
                    'create_time': int(time.time()),
                    'addr': addr,
                }
        except:
            pass
        return Default_return

    # 抖查查 代理(缓存到mysql中的ip)
    def douchacha_ips_mysql(self, num=1):
        ips = cache_get('dcc_ip_v1')
        dcc_proxies = {
            'ip': [],
            'aiohttp_ip': [],
            'request_ip': [],
        }
        for ip in ips:
            dcc_proxies['ip'].append(ip)
            dcc_proxies['aiohttp_ip'].append(f"http://{ip}")
            dcc_proxies['request_ip'].append(HttpJike.http_ip(ip))
        return dcc_proxies

    # 获取js文件的绝对路径
    def get_js_base_path(self, js_name):
        base_path = f'gy_pyhton_project/all_project/old/js/{js_name}.js'
        if self.path == 1:
            return f'/www/wwwroot/{base_path}'
        else:
            # return f'E:\Fr1997_D\doc\project\python/{base_path}'
            return f'C://Users/30844\Documents\project_all\python_project\mofan/{base_path}'

    # 抖音xb
    def get_xbogus_new(self, url, ua, mstoken=''):
        # 获取js文件绝对路径
        js_path = self.get_js_base_path(js_name='dy_x_bogus_v2')

        # 重编url
        url_p = urlparse(url)
        params_dict = dict()
        for i in url_p.query.split("&"):
            key, values = i.split('=')[0], i.split('=')[-1]
            if key not in ["msToken", "X-Bogus"]:
                params_dict[key] = values
        param_str = "&".join([f"{i}={params_dict[i]}" for i in params_dict])
        url = f"{url_p.scheme}://{url_p.netloc}{url_p.path}?{param_str}"
        url_para = url.split('?')[1] + '&msToken='

        with open(js_path, 'r', encoding='UTF-8') as file:
            result = file.read()
            context = execjs.compile(result)

            # 提前对参数进行处理
            md5_url = mode_pros.md5_base(url_para)

            str1 = bytes.fromhex(md5_url)
            hash_object = hashlib.md5(str1)
            md5her = hash_object.hexdigest()
            res = context.call("get_xbogus", url_para, ua, md5her)
            result_url = f'{url}&msToken={mstoken}&X-Bogus={res}'
            return result_url

    # 抖音xb
    def get_xbogus_new_gbk(self, url, ua, mstoken=''):
        # 获取js文件绝对路径
        js_path = self.get_js_base_path(js_name='dy_x_bogus_v2')

        # 重编url
        url_p = urlparse(url)
        params_dict = dict()
        for i in url_p.query.split("&"):
            key, values = i.split('=')[0], i.split('=')[-1]
            if key not in ["msToken", "X-Bogus"]:
                params_dict[key] = values
        param_str = "&".join([f"{i}={params_dict[i]}" for i in params_dict])
        url = f"{url_p.scheme}://{url_p.netloc}{url_p.path}?{param_str}"
        url_para = url.split('?')[1] + '&msToken='

        with open(js_path, 'r', encoding='gbk') as file:
            result = file.read()
            context = execjs.compile(result)

            # 提前对参数进行处理
            md5_url = mode_pros.md5_base(url_para)

            str1 = bytes.fromhex(md5_url)
            hash_object = hashlib.md5(str1)
            md5her = hash_object.hexdigest()
            res = context.call("get_xbogus", url_para, ua, md5her)
            result_url = f'{url}&msToken={mstoken}&X-Bogus={res}'
            return result_url

    # 抖音xb
    def get_xbogus_news_gbk(self, urls, ua, mstoken=''):
        ret_sign_urls = []

        # 获取js文件绝对路径
        js_path = self.get_js_base_path(js_name='dy_x_bogus_v2')

        # 重编url
        url_paras = []
        for url in urls:
            url_p = urlparse(url)
            params_dict = dict()
            for i in url_p.query.split("&"):
                key, values = i.split('=')[0], i.split('=')[-1]
                if key not in ["msToken", "X-Bogus"]:
                    params_dict[key] = values
            param_str = "&".join([f"{i}={params_dict[i]}" for i in params_dict])
            url = f"{url_p.scheme}://{url_p.netloc}{url_p.path}?{param_str}"
            url_para = url.split('?')[1] + '&msToken='
            md5_url = mode_pros.md5_base(url_para)
            str1 = bytes.fromhex(md5_url)
            hash_object = hashlib.md5(str1)
            md5her = hash_object.hexdigest()
            url_paras.append([url_para, md5her])

        with open(js_path, 'r', encoding='gbk') as file:
            result = file.read()
            context = execjs.compile(result)
            res = context.call("get_xboguss", ua, url_paras)
            for url, xb in zip(urls, res):
                sign_url = f'{url}&msToken={mstoken}&X-Bogus={xb}'
                ret_sign_urls.append(sign_url)
        return ret_sign_urls

    # 抖音xb v3
    def douyin_v3_get_xb(self, url_path, user_agent):
        if self.path == 1:
            cwd = '/www/wwwroot/gy_pyhton_project/all_project/old/node_modules'
        else:
            cwd = 'C:/Users/30844\Documents\project_all\python_project\mofan\gy_pyhton_project/all_project\old/node_modules'
        js_path = self.get_js_base_path(js_name='dy_x_bogus_20250528')
        js = execjs.compile(open(js_path, 'r', encoding='utf-8').read(), cwd=cwd)
        return js.call('sign', url_path, user_agent)

    # 抖音 msToken生成方式
    @staticmethod
    def get_douyin_token(string_len=16):
        random_str = ''
        base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789='
        length = len(base_str) - 1
        for _ in range(string_len):
            random_str += base_str[random.randint(0, length)]
        return random_str

    # 抖音cookie ttwid版本 db数据库
    def ttwid_cookie_tt(self, num=200, get_cache=0):
        table = 'cd_cookie_douyin'
        if self.path == 1:  # 服务器运行强制默认缓存数据
            get_cache = 1

        cookie_tt = []
        if get_cache == 1:
            cookie_tt = cache_get('jike_ttwid_cookies')
            if cookie_tt:
                return cookie_tt

        # 实时的也要增加30秒缓存
        cookie_tt = []
        cookie_tt_30 = cache_get('jike_ttwid_cookies_30')
        if cookie_tt_30:
            return cookie_tt_30
        else:
            sql = f'SELECT douyin_cookie_ttwid FROM {table} where douyin_cookie_ttwid is not null order by rand() limit {num}'
            all_cookie = self.mysql_db(method='s', table=table, sql=sql)
            for i in all_cookie:
                cookie_tt.append(i[0])
            if cookie_tt:
                cache_set('jike_ttwid_cookies_30', cookie_tt, 30)
        return cookie_tt

    # 查看某个文件夹所有文件
    @staticmethod
    def get_all_file(directory_path):
        fs = []
        try:
            # 使用 os.listdir 获取目录中的所有文件和子目录
            files = os.listdir(directory_path)

            # 输出所有文件和子目录的名称
            for file in files:
                fs.append(file)

        except Exception as e:
            print(f"Error listing files in directory: {e}")
        return fs

    # 获取知乎cookie
    def get_zhihu_cookie(self):
        cookies = cache_get('jike_zhihu_cookies')
        if not cookies:
            cookies = []
            sql = f"SELECT * FROM cd_zhihu_cookie where id > 0"
            all_cookie = self.mysql_db(method='s', table='cd_zhihu_cookie', sql=sql)
            for each in all_cookie:
                cookie = each[1]
                cookies.append(cookie)
            cache_set('jike_zhihu_cookies', cookies, 50)
        return cookies

    # 知乎加密 python版本
    def x_zse_96_b64encode(self, md5_bytes: bytes):
        h = {
            "zk": [1170614578, 1024848638, 1413669199, -343334464, -766094290, -1373058082, -143119608, -297228157,
                   1933479194, -971186181, -406453910, 460404854, -547427574, -1891326262, -1679095901, 2119585428,
                   -2029270069, 2035090028, -1521520070, -5587175, -77751101, -2094365853, -1243052806, 1579901135,
                   1321810770, 456816404, -1391643889, -229302305, 330002838, -788960546, 363569021, -1947871109],
            "zb": [20, 223, 245, 7, 248, 2, 194, 209, 87, 6, 227, 253, 240, 128, 222, 91, 237, 9, 125, 157, 230, 93,
                   252,
                   205, 90, 79, 144, 199, 159, 197, 186, 167, 39, 37, 156, 198, 38, 42, 43, 168, 217, 153, 15, 103, 80,
                   189,
                   71, 191, 97, 84, 247, 95, 36, 69, 14, 35, 12, 171, 28, 114, 178, 148, 86, 182, 32, 83, 158, 109, 22,
                   255,
                   94, 238, 151, 85, 77, 124, 254, 18, 4, 26, 123, 176, 232, 193, 131, 172, 143, 142, 150, 30, 10, 146,
                   162,
                   62, 224, 218, 196, 229, 1, 192, 213, 27, 110, 56, 231, 180, 138, 107, 242, 187, 54, 120, 19, 44, 117,
                   228, 215, 203, 53, 239, 251, 127, 81, 11, 133, 96, 204, 132, 41, 115, 73, 55, 249, 147, 102, 48, 122,
                   145, 106, 118, 74, 190, 29, 16, 174, 5, 177, 129, 63, 113, 99, 31, 161, 76, 246, 34, 211, 13, 60, 68,
                   207, 160, 65, 111, 82, 165, 67, 169, 225, 57, 112, 244, 155, 51, 236, 200, 233, 58, 61, 47, 100, 137,
                   185, 64, 17, 70, 234, 163, 219, 108, 170, 166, 59, 149, 52, 105, 24, 212, 78, 173, 45, 0, 116, 226,
                   119,
                   136, 206, 135, 175, 195, 25, 92, 121, 208, 126, 139, 3, 75, 141, 21, 130, 98, 241, 40, 154, 66, 184,
                   49,
                   181, 46, 243, 88, 101, 183, 8, 23, 72, 188, 104, 179, 210, 134, 250, 201, 164, 89, 216, 202, 220, 50,
                   221, 152, 140, 33, 235, 214],
            "zm": [120, 50, 98, 101, 99, 98, 119, 100, 103, 107, 99, 119, 97, 99, 110, 111]
        }

        def left_shift(x, y):
            x, y = ctypes.c_int32(x).value, y % 32
            return ctypes.c_int32(x << y).value

        def Unsigned_right_shift(x, y):
            x, y = ctypes.c_uint32(x).value, y % 32
            return ctypes.c_uint32(x >> y).value

        def Q(e, t):
            return left_shift((4294967295 & e), t) | Unsigned_right_shift(e, 32 - t)

        def G(e):
            t = list(struct.pack(">i", e))
            n = [h['zb'][255 & t[0]], h['zb'][255 & t[1]], h['zb'][255 & t[2]], h['zb'][255 & t[3]]]
            r = struct.unpack(">i", bytes(n))[0]
            return r ^ Q(r, 2) ^ Q(r, 10) ^ Q(r, 18) ^ Q(r, 24)

        def g_r(e):
            n = list(struct.unpack(">iiii", bytes(e)))
            [n.append(n[r] ^ G(n[r + 1] ^ n[r + 2] ^ n[r + 3] ^ h['zk'][r])) for r in range(32)]
            return list(
                struct.pack(">i", n[35]) + struct.pack(">i", n[34]) + struct.pack(">i", n[33]) + struct.pack(">i",
                                                                                                             n[32]))

        def g_x(e, t):
            n = []
            i = 0
            for _ in range(len(e), 0, -16):
                o = e[16 * i: 16 * (i + 1)]
                a = [o[c] ^ t[c] for c in range(16)]
                t = g_r(a)
                n += t
                i += 1
            return n

        local_48 = [48, 53, 57, 48, 53, 51, 102, 55, 100, 49, 53, 101, 48, 49, 100, 55]
        local_50 = bytes([63, 0]) + md5_bytes  # 随机数  0 是环境检测通过
        local_50 = ZhihuSign.pad(bytes(local_50))
        local_34 = local_50[:16]
        local_35 = [local_34[local_11] ^ local_48[local_11] ^ 42 for local_11 in range(16)]
        local_36 = g_r(local_35)
        local_38 = local_50[16:]
        local_39 = g_x(local_38, local_36)
        local_53 = local_36 + local_39
        local_55 = "6fpLRqJO8M/c3jnYxFkUVC4ZIG12SiH=5v0mXDazWBTsuw7QetbKdoPyAl+hN9rgE"
        local_56 = 0
        local_57 = ""
        for local_13 in range(len(local_53) - 1, 0, -3):
            local_58 = 8 * (local_56 % 4)
            local_56 = local_56 + 1
            local_59 = local_53[local_13] ^ Unsigned_right_shift(58, local_58) & 255
            local_58 = 8 * (local_56 % 4)
            local_56 = local_56 + 1
            local_59 = local_59 | (local_53[local_13 - 1] ^ Unsigned_right_shift(58, local_58) & 255) << 8
            local_58 = 8 * (local_56 % 4)
            local_56 = local_56 + 1
            local_59 = local_59 | (local_53[local_13 - 2] ^ Unsigned_right_shift(58, local_58) & 255) << 16
            local_57 = local_57 + local_55[local_59 & 63]
            local_57 = local_57 + local_55[Unsigned_right_shift(local_59, 6) & 63]
            local_57 = local_57 + local_55[Unsigned_right_shift(local_59, 12) & 63]
            local_57 = local_57 + local_55[Unsigned_right_shift(local_59, 18) & 63]
        return '2.0_' + local_57

    # 巨量广告数据
    def qianchuan_ad_keyword_hot(self, industry_id="19060101", city=None, cookie=None, search_type='hot_search_words',
                                 business_words_num=500, offset=0, limit=0):
        ret_data = []
        ret_err = 0

        if cookie is None:
            all_cookie = self.qianchuan_index_cookie()
            cookie = random.choice(all_cookie)
        headers = cookie['headers']
        cookies = cookie['cookies']
        aadvid = cookie['aadvid']
        day0 = mode_time.zero_clock(0)
        day2 = mode_time.zero_clock(2)
        day7 = mode_time.zero_clock(7)

        city_change = {
            "北京-北京": "北京",
            "天津-天津": "天津",
            "台湾-台湾": "台湾",
            "香港-香港": "香港",
            "澳门-澳门": "澳门",
            "重庆-重庆": "重庆",
            "上海-上海": "上海",
        }

        # 热搜词=hot_search_words，商机词=business_words，飙升词=up_words
        if search_type == 'hot_search_words':
            stat_time_type = 7
            metric_type = 1
            filed1 = 'search_rank_pv_filter'
            metrics = ["search_rank_query_pv", "search_rank_pv_filter"]
            orderBy = 'search_rank_query_pv'
            startTime = day7 * 1000
        elif search_type == 'business_words':
            stat_time_type = 7
            metric_type = 2
            filed1 = 'search_rank_cost_filter'
            metrics = ["search_rank_cost", "search_rank_cost_filter"]
            orderBy = 'search_rank_cost'
            startTime = day7 * 1000
        else:
            stat_time_type = 2
            metric_type = 3
            filed1 = 'search_rank_surging_filter'
            metrics = ["search_rank_surging_pv", "search_rank_surging_rate", "search_rank_surging_filter"]
            orderBy = 'search_rank_surging_pv'
            startTime = day2 * 1000

        # 请求参数
        filters = [{"field": "stat_time_type", "operator": 7, "type": 3, "values": [f"{stat_time_type}"]},
                   {"field": "metric_type", "operator": 7, "type": 1, "values": [f"{metric_type}"]},
                   {"field": "industry_id", "operator": 7, "type": 3, "values": industry_id},
                   {"field": filed1, "operator": 1, "type": 3, "values": ["1"]}]
        city = eval(city)
        for index_ct, ct in enumerate(city):
            if ct in city_change:
                city[index_ct] = city_change[ct]
        filters.append({"field": "region", "operator": 7, "type": 2, "values": city})

        data = {
            "dataTopic": "ad_query_traffic_data",
            "dimensions": ["query"],
            "endTime": day0 * 1000,
            "filters": filters,
            "metrics": metrics,
            "orderBy": [{"field": orderBy, "type": 1}], "page": {"limit": limit, "offset": offset},
            "platform": 1,
            "startTime": startTime,
            "extraInfo": {"refer_origin": "ad.oceane" + "ngine.com/statistics_pages/tool_apps/flow_analysis/search",
                          "refer_code": "ad_platform_search_traffic_analysis"}
        }
        response = requests.post(
            f'https://ad.oceanengine.com/nbs/api/statistics/customize_report/data?aadvid={aadvid}',  # 分类热词
            headers=headers, cookies=cookies, data=json.dumps(data))
        if response.status_code == 200:
            data_data = response.json()
            code = data_data.get('code')
            msg = data_data.get('msg')
            if code == 0 and msg == '':
                ret_err = 1
                data_main = data_data.get('data')
                if data_main:
                    rows = data_main.get('rows')
                    rank = 1

                    if search_type == 'hot_search_words':
                        for r in rows:
                            ret_data.append({
                                F_keyword: r['dimensions']['query'],
                                'search_day7_value': r['metrics']['search_rank_query_pv'],
                                'search_day7_rank': rank
                            })
                            rank += 1
                    elif search_type == 'business_words':
                        for r in rows:
                            ret_data.append({
                                F_keyword: r['dimensions']['query'],
                                'search_rank_cost': r['metrics']['search_rank_cost'],
                                'search_rank': rank
                            })
                            rank += 1
                    else:
                        for r in rows:
                            ret_data.append({
                                F_keyword: r['dimensions']['query'],
                                'search_value': r['metrics']['search_rank_surging_pv'],
                                'search_value_rate': r['metrics']['search_rank_surging_rate'],
                                'search_rank': rank
                            })
                            rank += 1

        return ret_err, ret_data

    def api_chat_gpt(self, content):
        url = config_dict['ai']['api2d']['chat_url']

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {config_dict['ai']['api2d']['token']['token1']}"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": content}]
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            return response.json()
        except:
            pass

    # 巨量广告cookie
    def wechat_search_keyword_cookie(self):
        data_list = []
        sql = f"SELECT * FROM `cd_task` WHERE id IN (43);"
        ret = self.mysql_db(method='s', table='cd_task', sql=sql)
        for i in ret:
            data_dict = {}
            json_data = eval(i[7])
            gdt_token = json_data['gdt_token']
            g_tk = json_data['g_tk']
            owner = json_data['owner']
            mp_tk = json_data['mp_tk']
            campaign_id = json_data['campaign_id']
            data_dict['gdt_token'] = gdt_token
            data_dict['g_tk'] = g_tk
            data_dict['owner'] = owner
            data_dict['mp_tk'] = mp_tk
            data_dict['campaign_id'] = campaign_id

            data_list.append(data_dict)
        return data_list

    # 本地地址
    @classmethod
    def loc_ip(cls):
        hostname = socket.gethostname()
        ip_list = []
        # 获取IP地址信息
        addr_infos = socket.getaddrinfo(hostname, None)
        for addr in addr_infos:
            ip_list.append(addr[4][0])
        return ip_list

    # 公网ip
    @classmethod
    def public_ip(cls):
        return requests.get(r'https://jsonip.com').json()

    # 错误推送
    def err_log(self, func, p=4, err_times=3, sleep=30, err_msg="err!!!", save_mysql=0):
        """
        import inspect
        func_info = inspect.getframeinfo(inspect.currentframe())
        mode_pro.err_log(func_info, p=5, err_msg="这个错误啊!!!", err_times=1, sleep=10, save_mysql=1)

            如果函数发生错误，需要发送推送信息
                规则：
                    1.两次推送的间要有休眠时间 sleep
                    2.推送包含 错误等级p 错误信息 错误位置
                    3.要有错误阈值err_times，错误n次后再推送

            p等级 0-5 越小越紧急
            - 0  服务器挂了
            - 1  高度重视
            - 2  中等错误
            - 3  小错误
            - 4  日常错误
            - 5  except 抛出

            err_times 错误次数 1-100000次
        """

        func_name = func.function
        func_filename = func.filename
        func_lineno = func.lineno

        # 错误唯一标志
        v = 'v11132sd'
        key = f"err_log_{v}_{mode_pros.md5_base(f'{func_name}_{func_filename}_{func_lineno}')}"
        key_send = f"err_send_{v}_{mode_pros.md5_base(f'{func_name}_{func_filename}_{func_lineno}')}"

        def send(this_err_count):
            mode_feishu.feishu_send_message(f"""err {p}
        错误信息：{err_msg}
        错误次数：{this_err_count}
        错误函数：{func_name}
        错误位置：{func_filename}
        错误行数：{func_lineno}""")

        err_cache = cache_get(key)
        if err_cache:
            err_count = err_cache['err_count'] + 1
            cache_set(key, {'err_count': err_cache['err_count'] + 1})
        else:
            err_count = 1
            cache_set(key, {'err_count': err_count})

        if err_count >= err_times:
            err_send_cache = cache_get(key_send)
            if not err_send_cache:
                send(err_count)
                cache_set(key_send, 1, sleep)

                # 存储mysql
                self.mysql_db(method='iss', table='cd_err_log_python', save_data=[{
                    'p': p,
                    'err_msg': err_msg,
                    'err_count': err_count,
                    'func_name': func_name,
                    'func_filename': func_filename,
                    'func_lineno': func_lineno,
                    'create_time': int(time.time()),
                }])

    # 综合表
    def ak_name(self, keyword):
        all_k_table = config_dict['keyword']['关键词综合表']
        base_table = 'all_keyword_v90'
        alias_name = 'other'
        first_py = self.chinese_to_pinyin(chinese=keyword, ret=3)
        for i in all_k_table:
            if first_py in all_k_table[i]:
                alias_name = i
        return f'{base_table}_{alias_name}'

    # ip白名单
    def ip_white_list(self):
        cache_key = 'django_ips'
        cache_data = cache_get(cache_key)
        if cache_data:
            return cache_data
        ips = []
        sql = 'SELECT ip FROM `cd_python_django_ip` where s = 1'
        all_data = self.mysql_db(method='s', table='cd_python_django_ip', sql=sql)
        for i in all_data:
            ips.append(i[0])
        cache_set(cache_key, ips, 30)
        return ips


class AllKeyword:
    table = config_dict['db_name']['table12']

    df_wx_index = 1
    df_wx_competition = 1

    df_xhs_index = 0
    df_xhs_competition = 1
    df_xhs_company_count = 0

    def __init__(self):
        pass

    # 综合指数
    @staticmethod
    def all_index(dy_index, wx_index, xhs_index):
        """
        计算逻辑：
        1. 用关键词在（每个平台中的搜索指数/三个平台中的搜索指数总和）计算出三个平台的比例
        2. 抖音搜索指数 * 1中计算出的抖音的比例 + 微信搜索指数 * 1中计算出的微信的比例 + 小红书搜索指数 * 1中计算出的小红书的比例

        :param dy_index: 抖音指数
        :param wx_index: 微信指数
        :param xhs_index: 小红书指数
        :return: 综合指数
        """
        # 计算总搜索指数
        index_all = dy_index + wx_index + xhs_index

        # 避免除以零的情况
        if index_all == 0:
            return 0

        # 计算各个平台的比例
        dy_ratio = dy_index / index_all
        wx_ratio = wx_index / index_all
        xhs_ratio = xhs_index / index_all
        keyword_all_index = (dy_index * dy_ratio) + (wx_index * wx_ratio) + (xhs_index * xhs_ratio)
        return round(keyword_all_index, 2)

    # 综合备注
    @staticmethod
    def all_record(dy_record, xhs_record):
        """
        1. 抖音关键词备注和小红书关键词的推荐理由。
        2. 同一个关键词在抖音和小红书平台都有备注和推荐理由，取合集后去重，比如在抖音和小红书中均为蓝海词，备注则显示一次蓝海词
        3. 筛选条件也为抖音和小红书备注和推荐理由合集去重

        :return:
        """
        record_info = config_dict['keyword']['record_info']
        dy_record_list = dy_record.split(',')
        xhs_record_list = xhs_record.split(',')
        for i in xhs_record_list:
            if i in record_info:
                record_str = record_info[i]['record_type']
                if record_str not in dy_record_list:
                    dy_record_list.append(record_str)
        return ','.join(dy_record_list)

    # 综合竞争度
    @staticmethod
    def all_competition(dy, wx, xhs):
        return round((dy + wx + (xhs + 1)) / 3, 2)

    # 综合竞价
    @staticmethod
    def all_company_count(dy, wx):
        return round((dy + wx) / 2, 2)

    # 指数处理
    @staticmethod
    def index_30(index):
        index30 = round(index / 30, 2)
        return index30
