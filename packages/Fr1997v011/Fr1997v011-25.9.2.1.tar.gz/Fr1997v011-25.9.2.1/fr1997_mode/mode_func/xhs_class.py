import re
import json
import time
import math
import execjs  # pip install PyExecJS
import random
import requests
from .base_class import *
from .mysql_class import MysqlDb
from .text_class import TextJike
from .func_class import ModeStatic
from .http_class import HttpJike

mode_text = TextJike()  # 文本
mode_pros = ModeStatic()  # 静态函数


# 小红书
class XhsJike(BaseFr1997, MysqlDb):
    cookie_table = 'cd_xiaohongshu_cookie'
    db_cookie = 'cd_xhs_cookies'
    base_host = "https://edith.xiaohongshu.com"

    def __init__(self):
        super().__init__()
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1])
        path_js = config_dict['machine_cfg'][mac_address]['js_path']['xhs_js']  # 计算机配置
        try:
            self.js3 = execjs.compile(open(path_js, 'r', encoding='utf-8').read())
        except:
            print("需要修改小红书js路径")
            self.js3 = None

    @staticmethod
    def xhs_web_note_into(text, note_id):
        def ret_json(code=200, msg=None, data=None):
            return {'code': code, 'msg': msg, 'data': data}

        if '当前内容无法展示' in text or '你访问的页面不见了' in text:
            return ret_json(500, '内容不见了')

        text = text.split('window.__INITIAL_STATE__=')[-1]
        text = text.split('</script>')[0]
        data_json = json.loads(json.dumps(eval(text)))

        errorCode = data_json['note']['serverRequestInfo']['errorCode']
        if errorCode == -510000:
            return ret_json(500, '内容不见了')

        note_info = data_json['note']['noteDetailMap'][note_id]['note']
        aweme_type = note_info.get('type')
        if aweme_type is None:
            return ret_json(500, '类型 错误')

        # 关于视频链接
        dld_video_url = ''
        duration = 0
        try:
            find_dld_video_url = 0
            dld_video_url = None
            stream = note_info['video']['media']['stream']
            for m in stream:
                if stream[m] and find_dld_video_url == 0:
                    # 有？无法转译
                    dld_video_url = stream[m][0]['backupUrls'][-1]

            duration = note_info['video']['capa']['duration']
        except:
            pass

        # 获取封面
        try:
            note_cover = note_info['imageList'][0]['urlDefault']
        except:
            note_cover = ''

        # 全部封面
        note_cover_list = []
        try:
            res_note_cover = note_info['imageList']
            for nc in res_note_cover:
                note_cover_list.append(nc['urlDefault'])
        except:
            note_cover = []

        # 话题
        topic = []
        try:
            tagList = note_info['tagList']
            for ti in tagList:
                topic.append(ti['name'])
        except:
            pass

        interactInfo = note_info['interactInfo']
        like_count = interactInfo['likedCount']
        collect_count = interactInfo['collectedCount']
        share_count = interactInfo['shareCount']
        comment_count = interactInfo['commentCount']

        return ret_json(200, 'ok', {
            'aweme_type': aweme_type,
            'note_id': note_id,
            'create_date': int(note_info['time'] / 1000),
            'title': mode_text.word_change(note_info['title']),
            'desc': mode_text.word_change(note_info['desc']),
            'location': note_info.get('ipLocation', ''),
            'duration': duration,
            'dld_video_url': dld_video_url,
            'note_cover': note_cover,
            'note_cover_list': note_cover_list,
            'topic': topic,

            'nickname': mode_text.word_change(note_info['user']['nickname']),
            'user_id': note_info['user']['userId'],
            'avatar': note_info['user']['avatar'],

            'like_count': like_count,
            'collect_count': collect_count,
            'share_count': share_count,
            'comment_count': comment_count,
        })

    @staticmethod
    def xhs_web_video_main_data(data_json, note_id):
        def ret_json(code=200, msg=None, data=None):
            return {'code': code, 'msg': msg, 'data': data}

        try:
            note_info = data_json['note']['noteDetailMap'][note_id]['note']

            aweme_type = note_info.get('type')
            if aweme_type is None or aweme_type != 'video':
                return ret_json(200, '请输入视频作品')

            # 关于视频链接
            find_dld_video_url = 0
            dld_video_url = None
            stream = note_info['video']['media']['stream']
            for m in stream:
                if stream[m] and find_dld_video_url == 0:
                    try:
                        # 有？无法转译
                        dld_video_url = stream[m][0]['backupUrls'][-1]
                    except:
                        pass

            if not dld_video_url:
                return ret_json(200, '未找到url')

            # 获取封面
            try:
                note_cover = note_info['imageList'][0]['urlDefault']
            except:
                note_cover = ''

            note_cover_list = []
            try:
                note_cover = note_info['imageList']
                for nc in note_cover:
                    note_cover_list.append(nc['urlDefault'])
            except:
                note_cover = ''

            return ret_json(200, 'ok', {
                'note_id': note_id,
                'aweme_type': 1,
                'create_date': int(note_info['time'] / 1000),
                'title': mode_text.word_change(note_info['title']),
                'desc': mode_text.word_change(note_info['desc']),
                'location': note_info.get('ipLocation', ''),
                'duration': note_info['video']['capa']['duration'],
                'dld_video_url': dld_video_url,
                'note_cover': note_cover,
                'note_cover_list': note_cover_list,

                'nickname': mode_text.word_change(note_info['user']['nickname']),
                'user_id': note_info['user']['userId'],
                'avatar': note_info['user']['avatar'],
            })
        except Exception as e:
            return ret_json(500, e)

    @staticmethod
    def xhs_video_id_pc(url):
        note_id = None
        if '://www.xiaohongshu.com/discovery' in url:
            note_id = url.split('://www.xiaohongshu.com/discovery/item/')[-1].split('?')[0]

        if '://www.xiaohongshu.com/explore/' in url:
            note_id = url.split('://www.xiaohongshu.com/explore/')[-1].split('?')[0]
        return note_id

    @staticmethod
    def xhs_app_url_302(url):
        pattern = r'://xhslink\.com(/?[A-Za-z0-9]+/[A-Za-z0-9]{6,13})|://xhslink\.com/([A-Za-z0-9]{6})'
        match = re.search(pattern, url)

        if match:
            if match.group(1):
                app_url = f'http://xhslink.com{match.group(1)}'
            else:
                app_url = f'http://xhslink.com/{match.group(2)}'
            return requests.get(app_url, headers=config_dict['base_headers']).url
        else:
            return None

    def xhs_cookie(self, cookie_status=1, use_status=1):
        """
            ret
            {
                '65ee99ca000000000d025711': {
                    'user_id': '65ee99ca000000000d025711',
                    'nickname': 'Sp2',
                    'cookie': 'a1=187d2defea8dz1fgwydnci40kw265ikh9fsxn66qs50000726043;gid=yYWfJfi820jSyYWfJfdidiKK0YfuyikEvfISMAM348TEJC28K23TxI888WJK84q8S4WfY2Sy;gid.sign=PSF1M3U6EBC/Jv6eGddPbmsWzLI=;webId=ba57f42593b9e55840a289fa0b755374;web_session=040069b49ada82640747c5e8ba344bd27cba68;acw_tc=007e1ba81f48bb265761f2ca4e2ca2b6e56437254e85e2c0b78814337ee9525e',
                    'cookie_dict': {
                        'a1': '187d2defea8dz1fgwydnci40kw265ikh9fsxn66qs50000726043',
                        'gid': 'yYWfJfi820jSyYWfJfdidiKK0YfuyikEvfISMAM348TEJC28K23TxI888WJK84q8S4WfY2Sy',
                        'gid.sign': 'PSF1M3U6EBC/Jv6eGddPbmsWzLI',
                        'webId': 'ba57f42593b9e55840a289fa0b755374',
                        'web_session': '040069b49ada82640747c5e8ba344bd27cba68',
                        'acw_tc': '007e1ba81f48bb265761f2ca4e2ca2b6e56437254e85e2c0b78814337ee9525e'
                    }
                }
            }
        """
        cache_key = f'xhs_cookie_v1'
        all_cookie = cache_get(cache_key)
        if not all_cookie:

            all_cookie = {}
            sql = f'SELECT user_id,nickname,cookie FROM {self.cookie_table} where use_status = {cookie_status} and cookie_status = {cookie_status}'
            all_data = self.mysql_db(method='s', table=self.cookie_table, sql=sql)
            if all_data:
                for i in all_data:
                    user_id = i[0]
                    nickname = i[1]
                    cookie = i[2]
                    cookie_dict = mode_pros.cookie_str_to_cookie_dict(cookie)
                    all_cookie[user_id] = {'user_id': user_id, 'nickname': nickname,
                                           'cookie': cookie, 'cookie_dict': cookie_dict}
            if not all_cookie:
                print("-- cookie 耗尽了！！！！！")
                sql = f'SELECT user_id,nickname,cookie FROM {self.cookie_table} where use_status = {cookie_status} and cookie_status = {cookie_status}'
                all_data = self.mysql_db(method='s', table=self.cookie_table, sql=sql)
                if all_data:
                    for i in all_data:
                        user_id = i[0]
                        nickname = i[1]
                        cookie = i[2]
                        cookie_dict = mode_pros.cookie_str_to_cookie_dict(cookie)
                        all_cookie[user_id] = {'user_id': user_id, 'nickname': nickname,
                                               'cookie': cookie, 'cookie_dict': cookie_dict}

            print(f"-- 当前可用cookie:{len(all_cookie.keys())}")
            cache_set(cache_key, all_cookie, 60)
        return all_cookie

    def xhs_video_main(self, req_url, proxies=None, user_cookie=0, user_cookie_str=''):
        def ret_json(code=200, msg=None, data=None):
            return {'code': code, 'msg': msg, 'data': data}

        # app端要特殊处理
        if 'xhslink' in req_url:
            req_url = self.xhs_app_url_302(req_url)
            if req_url is None:
                return ret_json(500, '未找到该视频 XHS009')

        # 获取小红书xsec_token
        matches = re.findall(r'xsec_token=([^&]+)', req_url)
        xsec_token = matches[0] if matches else ''

        # 获取id
        note_id = self.xhs_video_id_pc(req_url)
        if note_id is None:
            return ret_json(500, '未找到该视频 XHS008')

        xhs_url = f'https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsec_token}&xsec_source=pc_feed'
        headers = config_dict['base_headers']
        if user_cookie == 1:
            cookies = self.xhs_cookie()
            a1 = None
            web_session = None
            for c in cookies:
                a1 = cookies[c]['cookie_dict']['a1']
                web_session = cookies[c]['cookie_dict']['web_session']
            headers['cookie'] = f"a1={a1}; web_session={web_session};"
            if user_cookie_str:
                headers['cookie'] = user_cookie_str

        if proxies:
            response = requests.get(xhs_url, headers=headers, proxies=proxies)
        else:
            response = requests.get(xhs_url, headers=headers)

        ret_data = self.xhs_web_note_into(response.text, note_id)
        return ret_data

    @staticmethod
    def get_xsec_tokens():
        cache_key = 'xsec_tokens_loc'
        data_list = cache_get(cache_key)
        if data_list:
            return data_list
        try:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
            }
            data = {
                'token': '6auY6Ziz5piv5LiW55WM5LiK5pyA5Y6J5a6z55qE54is6Jmr5bel56iL5biI'
            }
            res = requests.post('http://42.193.7.147:7666/api/xhs/xsec_tokens', headers=headers, data=data)
            data_list = res.json()['data_list']
        except:
            data_list = ['ABEYLLyVLWG08-G_kO1QjaRUbpEaR29Qp3x4FDuVu426Q=',
                         'ABvV_W-E_VoxQSWCz1XendH268Med-HREFf7yno5IHCGo=',
                         'ABtBwHcu7rrk2ZOH0uuALyQI9oodA7sxPQyLRTfPhG5og=',
                         'ABDqV1xAR3SEoDdoB40_yD09avHnKGui_9VILZWXg3KWU=',
                         'ABuVs-3eDbtBfMHKwjHNr_hSMspIejizaqy51WQ9PoZEs=',
                         'ABsyzeuCaB5MPqaxXLX4KN89uhUiR-mLFAScprAu8x3bU=',
                         'ABe4gWUH7BK_r6Kgr8MkH2KPgMhKsPelpyE5dYYaIDoyg=',
                         'ABB7yHf8D8NW7IKk8dannxhwtSt3Xe2pWBw8UA6X14nzY=',
                         'ABho-zF_Jgw0LOiTT7J_5Y41slfUKZqL7QSu6xNHP-074=',
                         'ABiKahsJveydyvyBLdalMttlsQkENKAi9rbj6jIUPEdYc=',
                         'ABwMlOi53Bwe0jUAImDKByPaN2LFoGTn9zUb1URi8rYOY=',
                         'ABVbNcwQ0f1BWXtmtonOugs6o3g9T79LKtjcWwjDwQJBI=',
                         'ABm2t24JDR3esni55egnOcYn_gbldE9YdTCbUqnnmHQcU=',
                         'ABgOqOeYao7rUrNtI7XReJiykIDAYpSb6l9yF7_GOdJrs=',
                         'ABDhb0tLEyG-h7GadFcad3JT0PE-GGAWd6Hr1I3BDmu00=',
                         'ABlOZqc5waGwnbRWh4_-8FAzXlvBK-hNdFSXaDbyO80b0=',
                         'ABrtj6WWKntX-NsHZYowrMD3nyFjTgyOUz8RBe5TWJCyY=',
                         'ABoq-5CYRk-V0DY3iMSrHu-W7SFDhxh_Z_82f9j3KkC-k=',
                         'ABmNO7UiQrtbj3C254ulqkv6sM2uebgGtK0SySVNpvVbU=',
                         'ABzAhu8qQ1S24JcioVxkWeNRgv03FoSO83klaJRMeiDoI=',
                         'AB7F7OTfM7z8Wy4FYWzkdUpmMHMs0zUJVPb5GZKRhZatA=',
                         'ABLoiHV-amiurHpzoLHH6U6Y3SUXuil-syWnCzN-TkbuQ=',
                         'ABho-zF_Jgw0LOiTT7J_5Y4-JeR1W4mkWkwfh_MstqHc4=',
                         'ABEe6GwZ6YvsATZpGFwBMaKyikgFVqRRQ06dr4j4TLtgY=',
                         'ABUUOADRu6dI8NlNWT9_SMJwLK5SEn67LB320ru9tj7O4=']
        cache_set(cache_key, data_list, 600)
        return data_list

    # 聚光
    def h(self, keyword, js_path):
        # 聚光
        def js_e():
            e = ""
            for t in range(16):
                e += "abcdef0123456789"[math.floor(16 * random.random())]
            return e

        sign = self.js_go(keyword, js_path)
        headers = {
            'authority': 'ad.xiaohongshu.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://ad.xiaohongshu.com',
            'pragma': 'no-cache',
            'referer': 'https://ad.xiaohongshu.com/aurora/ad/tools/keywordTool',
            'sec-ch-ua': '^\\^Chromium^\\^;v=^\\^110^\\^, ^\\^Not',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '^\\^Windows^\\^',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63',
            'x-b3-traceid': js_e(),
            'x-s': sign['X-s'],
            'x-t': str(sign['X-t'])
        }
        return headers

    # 聚光
    @staticmethod
    def js_go(keyword, js_path='/www/wwwroot/gy_pyhton_project/all_project/xiaohongshu/keyword/j2.js'):
        if js_path == 'loc':
            js_path = ('C://Users/30844\Documents\project_all\python_project\mofan\gy_pyhton_project/all_project/'
                       'xiaohongshu/keyword/j2.js')
        with open(js_path, 'r', encoding='utf-8-sig') as w:
            s = w.readline()
            js_code = ''
            while s:
                js_code = js_code + s
                s = w.readline()

        ctx1 = execjs.compile(js_code)
        return ctx1.call('sign', '/api/leona/rtb/tool/keyword/search', "{keyword: " + f'{keyword}' + "}")

    # 聚光 小红书关键词
    @classmethod
    def target_word(cls, target_word):
        if '/' in str(target_word):
            return None
        return target_word

    # 聚光 小红书关键词
    @classmethod
    def mounth_search_index(cls, monthpv):
        if monthpv <= 0:
            monthpv = 0
        return monthpv

    # 聚光 小红书关键词
    @classmethod
    def competition(cls, completionLevel):
        if completionLevel == '高':
            return 3
        elif completionLevel == '中':
            return 2
        elif completionLevel == '低':
            return 1
        else:
            return 0

    # 聚光 小红书关键词
    @classmethod
    def suggested_bid(cls, suggestedBid):
        return float(suggestedBid)

    # 聚光 小红书关键词
    @classmethod
    def recommend_reason(cls, recommendReason):
        if recommendReason:
            return ','.join(recommendReason)
        else:
            return ''

    # 去除标点
    @classmethod
    def is_symbol_keyword(cls, keyword):
        if re.compile(r'[^\w]').search(keyword):
            return 1
        return 0

    # 聚光
    def bad_word(self):
        cache_key = 'xhs_bad_keyword'
        bad_keyword = cache_get(cache_key)
        if not bad_keyword:
            sql = 'SELECT good_word,all_word FROM `cd_xhs_repeat_keyword` where good_word is not null'
            all_data = self.mysql_db(method='s', table='cd_xhs_repeat_keyword', sql=sql)
            bad_keyword = ['没家']
            for i in all_data:
                good_word = i[0]
                all_word = i[1]
                good_word_list = good_word.split(',')
                all_word_list = all_word.split(',')
                for j in all_word_list:
                    if j not in good_word_list:
                        bad_keyword.append(j)
            cache_set(cache_key, bad_keyword, 5 * 60)

        return bad_keyword

    @staticmethod
    def base36encode(number, digits='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        base36 = ""
        while number:
            number, i = divmod(number, 36)
            base36 = digits[i] + base36
        return base36.lower()

    def generate_search_id(self):
        timestamp = int(time.time() * 1000) << 64
        random_value = int(random.uniform(0, 2147483646))
        return self.base36encode(timestamp + random_value)

    # 存储小红书cookie
    def add_xhs_cookie(self, cookie_data):
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
        acc = cookie_data['acc']
        cookie_str = cookie_data['cookie_str']
        # 查询
        is_in = self.mysql_db(
            method='s',
            table='cd_xhs_cookies',
            sql=f'SELECT id FROM {self.db_cookie} where acc = "{acc}"'
        )
        # 存储更新
        if is_in:
            self.mysql_db(method='up', table=self.db_cookie, save_data=[{
                'cookie_str': cookie_str,
                'is_work': 1,
                'time_str': time_str,
                'id': is_in[0][0],
            }])
        else:
            self.mysql_db(method='iss', table=self.db_cookie, save_data=[{
                'acc': acc,
                'cookie_str': cookie_str,
                'time_str': time_str,
                'is_work': 1,
            }])
        return

    # 获取小红书cookie (每分钟缓存)
    def get_xhs_cookie(self):
        cache_key = 'xhs_v22_cookie'
        cache_data = cache_get(cache_key)
        if cache_data:
            return cache_data

        all_cookie = []
        sql = f'SELECT id,acc,cookie_str,is_work,time_str FROM {self.db_cookie} where is_work = 1'
        all_data = self.mysql_db(method='s', table=self.db_cookie, sql=sql)
        for i in all_data:
            all_cookie.append({
                'cookie': i[2],
                'c_id': i[0],
                'cookie_dict': mode_pros.cookie_str_to_cookie_dict(i[2])}
            )
        cache_set(cache_key, all_cookie, 70)
        return all_cookie

    # 小红书请求头
    def get_headers(self, api, a1, data=None):
        headers = {
            "authority": "edith.xiaohongshu.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://www.xiaohongshu.com",
            "referer": "https://www.xiaohongshu.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "x-s": "",
            "x-t": ""
        }
        ret = self.js3.call('get_xs', api, data, a1)
        headers['x-s'], headers['x-t'] = ret['X-s'], str(ret['X-t'])
        return headers

    # 关键词搜索
    def search_v2_lhf(self, keyword, page, search_id=None, cookie_dict=None):
        if not cookie_dict:
            cookie = random.choice(self.get_xhs_cookie())
            cookie_dict = cookie['cookie_dict']

        api = '/api/sns/web/v1/search/notes'
        search_id = search_id if search_id is not None else self.generate_search_id()
        data = {
            F_keyword: keyword,
            "page": page,
            "page_size": 20,
            "search_id": search_id,
            "sort": "general",
            "note_type": 0
        }
        data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        res = requests.post(
            url=f'{self.base_host}{api}',
            headers=self.get_headers(api, cookie_dict['a1'], data),
            cookies=cookie_dict,
            data=data_json.encode()
        )
        return res

    def xhs_search_data_do(self, keyword, page, search_id=None, cookie_dict=None):
        save_data = []
        ret = {'code': 0, 'has_more': True, 'save_data': save_data}
        try:
            res = self.search_v2_lhf(keyword, page, search_id=search_id, cookie_dict=cookie_dict)
            if res.status_code == 200:
                data_data = res.json()
                code = data_data['code']
                success = data_data['success']
                msg = data_data['msg']
                if code == 0 and msg == '成功' and success:
                    data_info = data_data['data']
                    has_more = data_info['has_more']

                    if has_more is False:
                        return {'code': 1, 'has_more': has_more, 'save_data': save_data}

                    ret['code'] = 1
                    items = data_info['items']
                    for index, it in enumerate(items):
                        model_type = it['model_type']
                        if model_type == 'note':
                            note_id = it['id']
                            xsec_token = it['xsec_token']
                            note_card = it['note_card']

                            title = note_card.get('display_title', '')
                            like_count = note_card['interact_info']['liked_count']
                            # 搜索结果里面所有的 发布时间，如果接口里面有其他有用的参数你可以加，excel导出给我一下。
                            note_url = f'https://www.xiaohongshu.com/explore/{note_id}'

                            # 用户
                            user = note_card['user']
                            nick_name = user['nick_name']
                            user_avatar = user.get('avatar', '')
                            user_id = user['user_id']
                            user_url = f'https://www.xiaohongshu.com/user/profile/{user_id}'
                            this_type = note_card.get('type')
                            if this_type == 'video':
                                note_type = 'video'
                            else:
                                note_type = 'normal'
                            save_data.append({
                                F_keyword: keyword,
                                'page': page,
                                'note_type': note_type,
                                'page_index': index + 1,
                                'note_id': note_id,
                                'user_id': user_id,
                                'title': title,
                                'like_count': like_count,
                                'note_url': note_url,
                                'nick_name': nick_name,
                                'user_url': user_url,
                                'xsec_token': xsec_token,
                                'user_avatar': user_avatar,
                            })
        except Exception as E:
            print(E)
        return ret

    # 小红书个人信息
    def xhs_me(self, cookie):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'origin': 'https://www.xiaohongshu.com',
            'priority': 'u=1, i',
            'referer': 'https://www.xiaohongshu.com/',
            'sec-ch-ua': '\\Google',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '\\Windows\\',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'cookie': cookie,
            'user-agent': HttpJike.us
        }

        response = requests.get('https://edith.xiaohongshu.com/api/sns/web/v2/user/me', headers=headers)
        return response.json()
