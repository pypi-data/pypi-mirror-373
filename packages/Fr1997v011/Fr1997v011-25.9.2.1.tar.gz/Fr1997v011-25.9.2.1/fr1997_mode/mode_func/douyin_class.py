import re
import time
import json
import requests
import random
import hashlib
import time
import base64
from urllib.parse import urlparse
from urllib.parse import urlencode
from .base_class import *
from .http_class import HttpJike
from .base_mode_class import ModeFunc
from .text_class import TextJike
from .time_class import TimeJike
from .data_class import DataJike
from .func_class import ModeStatic

mode_pro = ModeFunc()
mode_text = TextJike()  # 文本
mode_time = TimeJike()  # 时间
mode_data = DataJike()  # 数据分析
mode_pros = ModeStatic()  # 静态方法


# 抖音
class DouyinJike:
    api_web = 'https://www.douyin.com/aweme/v1/web'

    @staticmethod
    def url_user_video_list(sec_user_id, max_cursor=0, search_count=None):
        if max_cursor == '0' or max_cursor == 0:
            max_cursor = 0
        need_time_list = 0 if max_cursor == 0 else 1

        if not search_count:
            search_count = 100 if max_cursor == 0 else 18  # 首次请求尽可能多
        return f'https://www.douyin.com/aweme/v1/web/aweme/post/?device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id={sec_user_id}&max_cursor={max_cursor}&locate_query=false&show_live_replay_strategy=1&need_time_list={need_time_list}&time_list_query=0&whale_cut_token=&cut_version=1&count={search_count}&publish_video_strategy_type=2&pc_client_type=1&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=2048&screen_height=1280&browser_language=zh-CN&browser_platform=Win32&browser_name=Edge&browser_version=119.0.0.0&browser_online=true&engine_name=Blink&engine_version=119.0.0.0&os_name=Windows&os_version=10&cpu_core_num=32&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=50&'

    # 抖音视频分类
    def douyin_video_type(self, aweme_type):
        ret_aweme_type = 0  # 默认视频
        try:
            if aweme_type == 68 or aweme_type == '68':  # 图文笔记
                return 68
            else:
                return 0
        except:
            pass
        return ret_aweme_type

    # 抖音视频id短链
    def short_url(self, url):
        return HttpJike.get(url=url).ret_url

    # 抖音 链接 -> video_id
    def get_video_id(self, video_url, tp=1):
        # 最终 https://www.douy...in.com/video/7218785833724185917
        if '://v.douyin' in video_url:
            pat = re.compile(r'https://v.douyin.com/[-_a-zA-Z0-9]{5,20}/')
            res = pat.findall(video_url)
            if res:
                v_url = self.get_video_id(self.short_url(res[0]))
                return v_url
        if 'www.douyin.com' in video_url and 'modal_id' in video_url:
            url1 = video_url.split('modal_id=')
            if url1:
                url2 = url1[-1]
                video_ids = []
                for i in url2:
                    if i in '1234567890':
                        video_ids.append(i)
                    else:
                        break
                video_id = ''.join(video_ids)
                return video_id
        if '.douyin.com/video' in video_url:
            video_idstr1 = video_url.split('/')
            if len(video_url) >= 5:
                video_idstr2 = video_idstr1[4]
                # 去除末尾杂项
                video_ids = []
                for i in video_idstr2:
                    if i in '1234567890':
                        video_ids.append(i)
                    else:
                        break
                video_id = ''.join(video_ids)
                return video_id
        if '/www.douyin.com/user/' in video_url and 'modal_id' in video_url:  # 其他
            video_idstr1 = video_url.split('modal_id=')[-1]
            video_ids = []
            for i in video_idstr1:
                if i in '1234567890':
                    video_ids.append(i)
                else:
                    break
            video_id = ''.join(video_ids)
            return video_id
        if 'www.iesdouyin.com/share/video/' in video_url:
            video_id = video_url.split('www.iesdouyin.com/share/video/')[-1].split('/?')[0]
            return video_id

        # 强制识别 可能出现问题(强制识别 视频id为19位数字)
        pat = re.compile(r'\d{19}')
        res = pat.findall(video_url)
        if res:
            return res[0]

    # 抖音 链接 -> sec_uid
    def get_douyin_sec_uid(self, user_url, tp=1):  # https://v.douyin.com/i3TDetD
        try:
            if 'www.douyin.com' in user_url and 'MS4' in user_url:
                sec_uid = user_url.split('https://www.douyin.com/user/')[-1].split('?')[0]
                return sec_uid

            if '://v.douyin.com':
                url_pattern = r'https://v\.douyin\.com/\w+/'
                matches = re.findall(url_pattern, user_url)
                if matches:
                    user_url = matches[0]
                res = HttpJike.get(url=user_url).ret_url
                sec_uid = res.split('https://www.iesdouyin.com/share/user/')[-1].split('?')[0]
                return sec_uid
        except:
            pass

    # 抖音搜索 20231025 数据解析
    def douyin_search_data_20231025(self, keyword, data_data, res_page):
        status_code = data_data.get('status_code')
        data = data_data.get('data')
        if status_code == 0 and data:
            data_list = []
            for index, v in enumerate(data):
                aweme_info = v['aweme_info']
                aweme_type = self.douyin_video_type(aweme_info.get('aweme_type', 0))

                # 如何判断选集？ mixId？
                mixId = None
                mixInfo = aweme_info.get('mix_info')
                if mixInfo:
                    mixId = mixInfo.get('mix_id')

                # 播放时长
                try:
                    release_time = round(int(aweme_info['video']['duration']) / 1000)  # 视频长度
                except:
                    release_time = 0

                author = aweme_info['author']

                # 用户的介绍
                signature = author.get('signature', '')

                # unique_id
                unique_id = author.get('unique_id', '')
                if len(unique_id) == 0:
                    unique_id = author.get('short_id', '')
                data_dict = {
                    F_keyword: keyword,
                    'aweme_type': aweme_type,
                    'mixId': mixId,
                    'index': index,
                    'desc': aweme_info['desc'],
                    'aweme_id': aweme_info['aweme_id'],
                    'sec_uid': author['sec_uid'],
                    'user_id': author['uid'],
                    'unique_id': unique_id,
                    'enterprise_verify_reason': author.get('enterprise_verify_reason', ''),
                    'nickname': author['nickname'],
                    'followers_count': author['follower_count'],

                    'createTime': aweme_info['create_time'],
                    'like_count': aweme_info['statistics']['digg_count'],  # 电赞
                    'comment_num': aweme_info['statistics']['comment_count'],  # 评论
                    'share_count': aweme_info['statistics']['share_count'],  # 转发
                    'collect_count': aweme_info['statistics']['collect_count'],  # 收藏

                    'search_time': int(time.time()),
                    'source': 'app_dj_videopc',

                    'cover': aweme_info['video']['cover']['url_list'][0],  # 封面
                    'author_head': author['avatar_thumb']['url_list'][0],
                    'author_type': '其他',

                    # 至关重要的vid
                    'v_id': aweme_info['video']['play_addr']['uri'],
                    'p': res_page,  # 页数

                    # 视频时长
                    'release_time': release_time,

                    # 介绍
                    'signature': signature,
                }

                data_list.append(data_dict)
            return {'code': 200, 'msg': 'ok', 'data_list': data_list}
        else:
            return {'code': 500, 'msg': '没有数据'}

    # 缓存es 抖音关键词搜索视频
    @staticmethod
    def douyin_keyword_info_save(sava_data, source):
        sava_es_data = []
        for v in sava_data:
            keyword = v[F_keyword]
            index = v['index']
            aweme_id = v['aweme_id']
            desc = v['desc']
            sec_uid = v['sec_uid']
            nickname = v['nickname']
            createTime = v.get('createTime')
            like_count = v.get('like_count')
            mixId = v.get('mixId')
            v_id = v.get('v_id')
            sava_es_data.append({"index": {"_id": f"{keyword}__{index}"}})
            data_dict = {
                'aweme_id': aweme_id,
                'mixId': mixId,
                'index': index,  # 从1开始
                'desc': desc,
                'sec_uid': sec_uid,
                'nickname': nickname,
                F_keyword: keyword,
                'createTime': createTime,
                'like_count': like_count,
                'search_time': int(time.time()),
                'source': source,

                # 至关重要的vid
                'v_id': v_id,
            }
            sava_es_data.append(data_dict)
        return sava_es_data, 'douyin_search_keyword_data'

    # 【api】 用户详情
    def api_douyin_user(self, sec_uid):
        device_id = ''.join(random.choice("0123456789") for _ in range(16))
        url = f"https://www.douyin.com/aweme/v1/web/user/profile/other/?sec_user_id={sec_uid}&device_id={device_id}&aid=1128"
        url = mode_pro.get_xbogus_new_gbk(url, config_dict['base_ua'])
        response = HttpJike.get(url=url, headers=self.ttwid_headers(), proxies=HttpJike.proxies_choose())
        if response.status_code == 200:
            data_data = response.json
            user_detail = data_data.get('user')

            data_json = self.analysis_douyin_user(user_detail)  # 数据获取
            return data_json

    # 【api】 视频详情 html版本
    def api_douyin_video(self, video_id, use_proxies=1, res_tp='video_info', proxies_dcc=0, is_ocr=0):
        headers = self.ttwid_headers()
        url = f'https://www.douyin.com/note/{video_id}'
        try:
            if use_proxies:
                response = HttpJike.get(url=url, headers=headers, proxies=HttpJike.proxies_choose())
            else:
                if proxies_dcc == 1:
                    all_p = mode_pro.douchacha_ips_mysql()['request_ip']
                    response = HttpJike.get(url=url, headers=headers, proxies=random.choice(all_p))
                else:
                    response = HttpJike.get(url=url, headers=headers)

            if response.status_code == 200:
                res_info = self.res_html_data(response, is_ocr=is_ocr)
                if res_info['code'] == 200:
                    res_info_data = res_info['date']
                    base_ret_data = {'aweme_type': 1, 'is_alive': 1}

                    # 属于视频的 aweme_type=0 or  aweme_type=1
                    base_ret_data['aweme_type'] = res_info_data['aweme_type']
                    if res_info_data['aweme_type'] == 0 or res_info_data['aweme_type'] == '0':
                        base_ret_data['aweme_type'] = 1

                    base_ret_data['video_id'] = res_info_data["video_id"]
                    base_ret_data['v_id'] = res_info_data["v_id"]
                    base_ret_data['title'] = res_info_data["title"]
                    base_ret_data['video_cover'] = res_info_data["video_cover"]

                    base_ret_data['play_num'] = 0
                    base_ret_data['good_count'] = res_info_data["good_count"]
                    base_ret_data['share_count'] = res_info_data["share_count"]
                    base_ret_data['comment_count'] = res_info_data["comment_count"]
                    base_ret_data['collect_count'] = res_info_data["collect_count"]
                    base_ret_data['user_id'] = res_info_data["user_id"]

                    base_ret_data['update_time'] = int(time.time())
                    base_ret_data['create_date'] = res_info_data["create_date"]
                    base_ret_data['release_time'] = res_info_data["release_time"]
                    base_ret_data['nickname'] = res_info_data["nickname"]
                    base_ret_data['author_head'] = res_info_data["author_head"]
                    base_ret_data['describe'] = res_info_data["describe"]

                    base_ret_data['download_addr_url_list2'] = res_info_data["download_addr_url_list2"]
                    base_ret_data['download_addr_url_list'] = res_info_data["download_addr_url_list2"]
                    base_ret_data['mp3_url_list'] = res_info_data["mp3_url_list"]
                    return base_ret_data
            else:
                return {'aweme_type': 1, 'is_alive': 0, 'err': '没有数据'}
        except Exception as E:
            return {'aweme_type': 1, 'is_alive': 0, 'err': E}

    # 【api】 抖音合集列表
    def api_douyin_mix_list(self, cursor=0, limit=6, use_proxies=1):
        headers = self.ttwid_headers()
        url = f'https://www.douyin.com/aweme/v1/web/mix/list/?device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id=MS4wLjABAAAAqfJDRsNO2778Ye6WecYtOl1qISyLAwUoG2rgsZFqzS9ZAKpN7tMuqr7O6P2Acwos&req_from=channel_pc_web&cursor={cursor}&count={limit}&pc_client_type=1&version_code=290100&version_name=29.1.0&cookie_enabled=true&screen_width=2048&screen_height=1280&browser_language=zh-CN&browser_platform=Win32&browser_name=Edge&browser_version=123.0.0.0&browser_online=true&engine_name=Blink&engine_version=123.0.0.0&os_name=Windows&os_version=10&cpu_core_num=32&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=50'
        url = mode_pro.get_xbogus_new_gbk(url, config_dict['base_ua'])
        try:
            if use_proxies:
                response = HttpJike.get(url=url, headers=headers, proxies=HttpJike.proxies_choose())
            else:
                response = HttpJike.get(url=url, headers=headers)
            if response.status_code == 200:
                data_data = response.json
                print(data_data)
                return data_data
        except Exception as E:
            pass

    # 【api】 抖音合集详情
    def api_douyin_mix_page(self, mix_id):
        url = f'https://www.douyin.com/aweme/v1/web/mix/aweme/?device_platform=webapp&aid=6383&channel=channel_pc_web&mix_id={mix_id}&cursor=0&count=20&pc_client_type=1&version_code=290100&version_name=29.1.0&cookie_enabled=true&screen_width=2048&screen_height=1280&browser_language=zh-CN&browser_platform=Win32&browser_name=Edge&browser_version=123.0.0.0&browser_online=true&engine_name=Blink&engine_version=123.0.0.0&os_name=Windows&os_version=10&cpu_core_num=32&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=50'
        url = mode_pro.get_xbogus_new_gbk(url, config_dict['base_ua'])
        response = requests.get(
            url=url,
            headers=self.ttwid_headers(),
        )
        print(response.status_code)
        print(response.json())

    # 【api】 用户主页视频列表 amemv版本
    def user_video_list_mv(self, sec_uid, max_cursor='0', timeout=30):
        ret_data = {
            'list': []
        }
        headers = {
            'authority': 'www.douyin.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://www.douyin.com',
            "user-agent": config_dict['base_ua'],
        }
        params = {
            "sec_uid": sec_uid,
            'aid': '1128',
            "count": 21,
            "max_cursor": max_cursor,  # 需要 max_cursor 跳转到下一页
        }
        try:
            response = requests.get(f'https://www.amemv.com/web/api/v2/aweme/post/', params=params,
                                    headers=headers, proxies=HttpJike.proxies_choose(), timeout=timeout)
            if response.status_code == 200:
                data_data = response.json()
                max_cursor = data_data.get('max_cursor')
                has_more = data_data.get('has_more')
                ret_data['max_cursor'] = max_cursor
                ret_data['has_more'] = has_more
                status_code = data_data.get('status_code')
                if status_code == 0:
                    aweme_list = data_data["aweme_list"]
                    for v in aweme_list:
                        aweme_id = v['aweme_id']
                        author_info = v.get('author', {})
                        nickname = author_info.get('nickname', '')
                        uid = author_info.get('uid', '')
                        sec_uid = author_info.get('sec_uid', '')

                        statistics = v.get('statistics', {})
                        digg_count = statistics.get('digg_count', 0)
                        share_count = statistics.get('share_count', 0)
                        # comment_count = statistics.get('comment_count', 0)  # 没有
                        # collect_count = statistics.get('collect_count', 0)  # 没有
                        # create_time = statistics.get('create_time', 0)  # 没有

                        video_info = v.get('video', {})
                        release_time = round(int(video_info.get('duration', 0)) / 1000)
                        vid = video_info.get('vid', '')

                        ret_data['list'].append({
                            'aweme_id': aweme_id,
                            'aweme_type': self.douyin_video_type(v.get('aweme_type', 0)),
                            'title': v['desc'],
                            'digg_count': digg_count,
                            'share_count': share_count,

                            'nickname': nickname,
                            'sec_uid': sec_uid,
                            'uid': uid,

                            'release_time': release_time,
                            'vid': vid,
                        })
        except:
            pass

        return ret_data

    # api 抖音用户 来之于django
    def api_douyin_user_info(self, sec_uid):
        url = "http://pythonapi.yinliu.club/douyin_users_info/"
        data = {
            'token': config_dict['token']['django'],
            'user_ids': sec_uid,
        }
        res = requests.post(url=url, data=data)
        return res.json()

    # 【数据解析】 用户主页列表
    def analysis_douyin_video_list(self, aweme_list):
        save_data = []
        for v in aweme_list:
            author = v['author']

            # 链接，
            sec_uid = author['sec_uid']

            # 链接，
            aweme_id = v['aweme_id']

            # 类型
            aweme_type = self.douyin_video_type(v.get('aweme_type', 0))

            # 点赞数
            digg_count = v['statistics']['digg_count']

            # 评论数
            comment_count = v['statistics']['comment_count']

            # 评论数
            collect_count = v['statistics']['collect_count']

            # 评论数
            share_count = v['statistics']['share_count']

            release_time = round(int(v['duration']) / 1000)  # 视频长度

            # 标题
            desc = mode_text.word_change(v['desc'])
            if len(str(desc)) < 0:
                desc = ''

            # 发布时间。
            create_time = v['create_time']
            create_time_str = time.strftime("%Y-%m-%d %X", time.localtime(create_time))  # 2021-04-12 14:36:20
            save_data.append({
                'sec_uid': sec_uid,
                'aweme_id': aweme_id,
                'aweme_type': aweme_type,
                'title': desc,

                'digg_count': digg_count,
                'comment_count': comment_count,
                'collect_count': collect_count,
                'share_count': share_count,
                'release_time': release_time,
                'create_time': create_time,
                'create_time_str': create_time_str,
            })
        return save_data

    # 【数据解析】 用户详情
    def analysis_douyin_user(self, res_data):
        aweme_count = res_data['aweme_count']
        follower_count = res_data['follower_count']
        nickname = res_data['nickname']
        unique_id = res_data.get('unique_id', '')
        if len(unique_id) == 0:
            unique_id = res_data.get('short_id', '')
        user_id = res_data['uid']
        total_favorited = res_data['total_favorited']
        author_head = res_data['avatar_168x168']['url_list'][0]
        introduction = mode_text.word_change(res_data['signature'])
        # 用户类型 1=个人  2=黄V  3=蓝V  4=注销  5=未知
        user_type = 5
        organization = ''
        custom_verify = res_data['custom_verify']
        enterprise_verify_reason = res_data.get('enterprise_verify_reason', '')
        if len(custom_verify) > 0:
            user_type = 2
            organization = custom_verify
        if len(enterprise_verify_reason) > 0:
            user_type = 3
            organization = enterprise_verify_reason

        return {
            'nickname': nickname,
            'unique_id': unique_id,
            'user_id': user_id,
            'introduction': introduction,
            'video_count': aweme_count,
            'follower_count': follower_count,
            'good_count': total_favorited,
            'user_type': user_type,
            'organization': organization,
            'author_head': author_head,
            'user_update_date': int(time.time()),
        }

    # 【数据解析】 视频详情
    def douyin_video_response(self, res_data, tp='django_video_info'):
        base_ret_data = {'aweme_type': 1, 'is_alive': 1}

        # 是否存在
        if '因作品权限或已被删除，无法观看，去看看其他作品吧' in str(res_data):
            base_ret_data['is_alive'] = 0
            return base_ret_data

        # 获取视频类型
        aweme_type = self.douyin_video_type(res_data.get('aweme_type', 0))
        if aweme_type == 68:
            base_ret_data['aweme_type'] = 68
            return base_ret_data

        like_num = res_data["statistics"]["digg_count"]
        forward_num = res_data["statistics"]["share_count"]
        comment_num = res_data["statistics"]["comment_count"]
        collect_count = res_data["statistics"]["collect_count"]

        # 播放时长
        try:
            release_time = round(int(res_data['video']['duration']) / 1000)  # 视频长度
        except:
            release_time = 0

        # 昵称
        nickname = res_data["author"]["nickname"]

        # 描述
        describe = res_data["author"]["signature"]

        # 标题
        desc = res_data["desc"]

        # 封面
        try:
            cover_img = res_data['video']['cover']['url_list'][0]
        except:
            cover_img = ''

        # 视频 vid
        try:
            v_id = res_data['video']['vid']
        except:
            v_id = res_data['video']['play_addr']['uri']

        # 视频创建时间比较特殊，如果没有创建时间，默认一个值
        create_time = res_data.get('create_time', config_dict['douyin']['douyin_video_create_time'])

        # sec_uid
        sec_uid = res_data['author']['sec_uid']

        # user_id
        user_id = res_data['author']['uid']

        # author_head
        author_head = res_data['author']['avatar_thumb']['url_list'][0]
        base_ret_data['video_id'] = res_data["aweme_id"]
        base_ret_data['v_id'] = v_id
        base_ret_data['title'] = desc
        base_ret_data['video_cover'] = cover_img

        base_ret_data['play_num'] = 0
        base_ret_data['good_count'] = like_num
        base_ret_data['comment_count'] = comment_num
        base_ret_data['share_count'] = forward_num
        base_ret_data['collect_count'] = collect_count

        base_ret_data['update_time'] = int(time.time())
        base_ret_data['create_date'] = create_time
        base_ret_data['release_time'] = release_time
        base_ret_data['nickname'] = nickname
        base_ret_data['describe'] = describe

        if tp == 'django_video_info':
            return {
                "video_id": res_data["aweme_id"],
                "v_id": v_id,
                'video_description': desc,
                'video_cover': cover_img,

                'play_num': 0,  # 播放量
                'good_count': like_num,  # 点赞量
                'comment_count': comment_num,  # 评论量
                'share_count': forward_num,  # 分享数
                'collect_count': collect_count,  # 收藏数

                'update_time': int(time.time()),
                'create_date': create_time,
                'video_time_count': release_time,  # 视频时常
                'release_time': release_time,  # 视频时常
                'describe': describe,

                'nickname': nickname,
                'sec_uid': sec_uid,
                'user_id': user_id,
                'author_head': author_head,
            }
        elif tp == 'video_info':
            base_ret_data['follower_count'] = res_data['author']['follower_count']
            base_ret_data['sec_uid'] = res_data['author']['sec_uid']
            return base_ret_data
        elif tp == 'wav':
            # 获取音频
            bit_rate = res_data['video']['bit_rate'][-1]
            base_ret_data['sec_uid'] = sec_uid
            base_ret_data['wav_size'] = bit_rate['bit_rate']
            base_ret_data['wav_url'] = bit_rate['play_addr']['url_list']

            # 改版 bit_rate中有很多链接，找到&cs=2为标准音频链接
            bit_rate = res_data['video']['bit_rate'][0]  # 保底一个
            base_ret_data['sec_uid'] = sec_uid
            base_ret_data['wav_size'] = bit_rate['bit_rate']
            base_ret_data['wav_url'] = bit_rate['play_addr']['url_list']

            # 获取新的
            bit_rate = res_data['video']['bit_rate']
            for bt in bit_rate:
                wav_url_list = bt['play_addr']['url_list']
                if wav_url_list:
                    if '&cs=2' in wav_url_list[0]:
                        base_ret_data['wav_size'] = bt['bit_rate']
                        base_ret_data['wav_url'] = bt['play_addr']['url_list']
            return base_ret_data
        else:
            return base_ret_data

    # 获取ttwid
    @staticmethod
    def get_ttwid_20240111():
        result = None
        try:
            json = {"region": "cn", "aid": 1768, "needFid": False, "service": "www.ixigua.com",
                    "migrate_info": {"ticket": "", "source": "node"}, "cbUrlProtocol": "https", "union": True}
            r = requests.post("https://ttwid.bytedance.com/ttwid/union/register/", json=json,
                              proxies=HttpJike.proxies_choose())
            cookie = r.headers['Set-Cookie']
            match = re.search("ttwid=([^;]+)", cookie)
            if match:
                result = match.group(1)
            else:
                result = ""
        except:
            print("err ttwid_cookie获取失败")
        if result:
            return result

    # 千川指数
    def qianchuan_index_req(self, cookie_use, word):
        cookies = []
        all_cookie = mode_pro.qianchuan_index_cookie()  # 具有缓存性
        for cookie in all_cookie:
            if cookie['id_id'] in cookie_use:
                cookies.append(cookie)

        cookie = random.choice(cookies)
        acc = cookie['id_id']

        t0 = mode_time.zero_clock()
        t30 = t0 - 86400 * 30
        data = {"word": word, "start_datetime": t30, "end_datetime": t0}

        try:
            response = requests.post(
                f'https://ad.oceanengine.com/platform/api/v1/search_ad/search_trend_v2/?aadvid={cookie["aadvid"]}',
                # 监控
                headers=cookie['headers'],
                cookies=cookie['cookies'],
                data=json.dumps(data)
            )
            if response.status_code == 200:
                data_data = response.json()
                code = data_data.get('code')
                data = data_data.get('data')
                if code == 0 and data:
                    return {'code': 200, 'msg': 'ok', 'data': mode_pro.keyword_day_index_get(data=data), 'acc': acc}
                else:
                    return {'code': 500, 'msg': f'err 1', 'acc': acc}
            else:
                return {'code': 500, 'msg': f'err:{response.status_code}', 'acc': acc}
        except Exception as E:
            return {'code': 500, 'msg': 'err 2', 'acc': acc}

    # 千川指数
    def qianchuan_index_data_do(self, day_index, _id):
        # 日均值
        day_index_new = [i['v'] for i in day_index]
        day_index_new.sort()
        day_index_new = day_index_new[1:][:-1]
        index_avg = mode_data.list_avg(day_index_new)
        if index_avg is None:
            index_avg = 0

        # 计算中位数
        if index_avg:
            day_index_new = [i['v'] for i in day_index]
            median = mode_data.list_median(day_index_new)
        else:
            median = 0

        return {
            'is_open': 1,
            F_keyword: _id,
            'day_index': day_index,  # 日指数
            'median': median,  # 中位数
            'index_avg': index_avg,  # 平均数
        }

    # 千川指数 批量存储
    def qianchuan_index_save(self, save_data):
        should_keyword = []
        keyword_index_doc = []
        keyword_index_sign_doc = []
        if save_data:
            for i in save_data:
                _id = i[F_keyword]
                should_keyword.append(_id)
            is_in, is_in_data, shoulds_not = mode_pro.es_in_or_notins(config_dict['db_name']['table11'], should_keyword)
            for i in save_data:
                _id = i[F_keyword]
                keyword_index_doc.append({"index": {"_id": f"{_id}"}})
                keyword_index_doc.append({
                    'is_open': i['is_open'],
                    F_keyword: _id,  # 平均指数
                    'day_index': i['day_index'],  # 日指数
                    'median': i['median'],  # 中位数
                    'index_avg': i['index_avg'],  # 平均数
                    'create_time': int(time.time()),
                    'update_time': int(time.time()),
                })

                # 同步到关键词表
                if _id in is_in_data:
                    keyword_pinyin = mode_pro.chinese_to_pinyin(chinese=_id, ret=3)
                    keyword_index_sign_doc.append(
                        {'update': {'_index': f"dso_douyin_keyword_{keyword_pinyin}", '_id': _id}})
                    keyword_index_sign_doc.append({'doc': {
                        'index_avg_new': i['index_avg'],
                        'median_new': i.get('median', 0),
                        'update_index_time': int(time.time()),
                    }})
        mode_pro.es_create_update(doc=keyword_index_doc, index='douyin_keyword_index')
        mode_pro.es_create_update_noIndex(doc=keyword_index_sign_doc)

    # 视频分类
    @staticmethod
    def douyin_tag_info(video_tag):
        tag1 = ""
        tag1_id = ""
        tag2 = ""
        tag2_id = ""
        tag3 = ""
        tag3_id = ""
        try:
            for tg in video_tag:
                tag_id = tg['tag_id']
                tag_name = tg['tag_name']
                level = tg['level']

                if level == 1:
                    tag1 = tag_name
                    tag1_id = tag_id
                elif level == 2:
                    tag2 = tag_name
                    tag2_id = tag_id
                elif level == 3:
                    tag3 = tag_name
                    tag3_id = tag_id
        except:
            pass
        return tag1, tag2, tag3, tag1_id, tag2_id, tag3_id

    # 抖音批量视频详情请求url
    @staticmethod
    def douyin_video_batch_url(aweme_ids):
        url_start = 'https://aweme.snssdk.com/aweme/v1/multi/aweme/detail/?aweme_ids=['
        for v in aweme_ids:
            url_start += f'{v},'
        if aweme_ids:
            url_start = url_start[:-1]
        return url_start + ']'

    # mix
    @staticmethod
    def mix_str(mixId):
        if mixId is None:
            video_category = 2
            video_mixid = ''
        else:
            video_category = 1
            video_mixid = mixId
        return video_mixid, video_category

    # 视频分类
    @staticmethod
    def douyin_tag_info_html(video_tag):
        tag1 = ""
        tag1_id = ""
        tag2 = ""
        tag2_id = ""
        tag3 = ""
        tag3_id = ""
        try:
            for tg in video_tag:
                tag_id = tg['tagId']
                tag_name = tg['tagName']
                level = tg['level']

                if level == 1:
                    tag1 = tag_name
                    tag1_id = tag_id
                elif level == 2:
                    tag2 = tag_name
                    tag2_id = tag_id
                elif level == 3:
                    tag3 = tag_name
                    tag3_id = tag_id
        except:
            pass
        return tag1, tag2, tag3, tag1_id, tag2_id, tag3_id

    # 抖音 ttwid版本的cookie请求头
    @staticmethod
    def ttwid_headers(sec_user_id=None, ua=None):
        cookies = mode_pro.ttwid_cookie_tt(get_cache=1)
        base_header = {
            "authority": "www.douyin.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "accept": "application/json, text/plain, */*",
            "referer": "https://www.douy" + "in.com/user/MS4wLjABAAAAM5BxLLRhN2jrzttuOUI3LEmFClP8t6dp0bf67Oi3deE",
            "accept-language": "zh-CN,zh;q=0.9",
            'cookie': f'msToken={mode_pro.get_douyin_token(107)};odin_tt=;passport_csrf_token=1;{random.choice(cookies)}'
        }
        if sec_user_id:
            base_header['referer'] = f"https://www.douyin.com/user/{sec_user_id}"

        if ua:
            base_header['user-agent'] = ua
        else:
            base_header['user-agent'] = config_dict['base_ua']
        return base_header

    # 登录版本的cookie
    @staticmethod
    def user_headers(sec_user_id=None, ua=None, sid_tt=None):
        def douyin_cookie_login():
            cache_key = 'douyin_user_ck_v2'
            cached_data = cache_get(cache_key)
            if cached_data:
                return cached_data

            cl = []
            sql = f'SELECT id,task_status,json from cd_task where id IN (39,40);'
            all_data = mode_pro.mysql_db(method='s', table='task', sql=sql)
            for i in all_data:
                json_data = eval(i[2])
                cl.append(json_data)
            cache_set(cache_key, cl, 100)
            return cl

        if sid_tt:
            cookie = f'sid_tt={sid_tt};'
        else:
            user_cookies = douyin_cookie_login()  # 假cookie 账号登录的真实cookie
            cookie = f'sid_tt={random.choice(user_cookies)["sid_tt"]};'
        base_header = {
            "authority": "www.douyin.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "accept": "application/json, text/plain, */*",
            "referer": f"https://www.douyin.com/user/{sec_user_id}",
            "accept-language": "zh-CN,zh;q=0.9",
            "cookie": cookie
        }
        if ua:
            base_header['user-agent'] = ua
        else:
            base_header['user-agent'] = config_dict['base_ua']

        return base_header

    # 抖音视频 笔记 html版本 错误->【None】
    def api_douyin_html(self, video_id, use_proxies=1, is_ocr=0):
        headers = self.ttwid_headers()
        try:
            url = f'https://www.douyin.com/note/{video_id}'
            if use_proxies:
                response = HttpJike.get(url=url, headers=headers, proxies=HttpJike.proxies_choose())
            else:
                response = HttpJike.get(url=url, headers=headers)
            if response.status_code == 200:
                return self.res_html_data(response, is_ocr=is_ocr)
        except Exception as e:
            print(e)

    # 数据解析 抖音作品详情 html版本
    def res_html_data(self, response, is_ocr=0):
        base_ret_data = {'aweme_type': 1, 'is_alive': 1}
        is_alive = 1
        pattern = r'self\.__pace_f\.push\(\[1,"\d:\[\S+?({[\s\S]*?)\]\\n"\]\)</script>'
        render_data: str = re.findall(pattern, response.text)[-1]
        if render_data:
            render_data = render_data.replace(
                '\\"', '"').replace('\\\\', '\\')
            data_data_each = json.loads(render_data)

            # 失效的视频判断
            if data_data_each['statusCode'] == -404:
                if is_ocr:
                    base_ret_data['is_alive'] = 0
                    return base_ret_data
                return {'code': 501}

            detail = data_data_each['aweme']['detail']
            # 备用字段
            base_ret_data['desc'] = detail["desc"]
            base_ret_data['aweme_id'] = detail['awemeId']
            base_ret_data['like_count'] = detail["stats"]["diggCount"]
            base_ret_data['forward_num'] = detail["stats"]["shareCount"]
            base_ret_data['sce_uid'] = detail["authorInfo"]["secUid"]
            base_ret_data['cover_img'] = detail['video']['coverUrlList'][0]

            base_ret_data['title'] = detail["desc"]
            base_ret_data['aweme_type'] = self.douyin_video_type(detail.get('awemeType', 0))
            base_ret_data['video_id'] = detail['awemeId']

            base_ret_data['play_num'] = 0
            base_ret_data['good_count'] = detail["stats"]["diggCount"]
            base_ret_data['comment_count'] = detail["stats"]["commentCount"]
            base_ret_data['share_count'] = detail["stats"]["shareCount"]
            base_ret_data['collect_count'] = detail["stats"]["collectCount"]

            base_ret_data['nickname'] = detail["authorInfo"]["nickname"]
            base_ret_data['sec_uid'] = detail["authorInfo"]["secUid"]
            base_ret_data['follower_count'] = detail["authorInfo"]["followerCount"]
            base_ret_data['total_favorited'] = detail["authorInfo"]["totalFavorited"]
            base_ret_data['uid'] = detail["authorInfo"]["uid"]
            base_ret_data['author_head'] = detail['authorInfo']['avatarThumb']['urlList'][0]
            base_ret_data['video_cover'] = detail['video']['coverUrlList'][0]
            base_ret_data['user_id'] = detail['authorInfo']['uid']
            base_ret_data['describe'] = ''

            try:
                base_ret_data['images'] = detail['images'][0]['urlList']
            except:
                base_ret_data['images'] = []

            base_ret_data['update_time'] = int(time.time())

            try:
                base_ret_data['v_id'] = detail['video']['uri']
                if base_ret_data['aweme_type'] == 68:
                    base_ret_data['v_id'] = ''
            except:
                base_ret_data['v_id'] = ''

            try:
                base_ret_data['create_time'] = detail.get('createTime',
                                                          config_dict['douyin']['douyin_video_create_time'])
            except:
                base_ret_data['create_time'] = config_dict['douyin']['douyin_video_create_time']
            base_ret_data['create_date'] = base_ret_data['create_time']

            try:
                base_ret_data['release_time'] = round(int(detail['video']['duration']) / 1000)  # 视频长度
            except:
                base_ret_data['release_time'] = 0

            # mp3 url
            try:
                mp3_url_list = detail['music']['playUrl']['urlList']
                if '.mp3' in detail['music']['playUrl']['urlList'][0]:
                    pass
                else:
                    mp3_url_list = []
            except:
                mp3_url_list = []
            base_ret_data['mp3_url_list'] = mp3_url_list

            # 视频下载地址 第二类型
            try:
                download_addr_url_list2 = detail['video']['playAddr']
                download_addr_url = []
                for i in download_addr_url_list2:
                    each_src = i['src']
                    if 'https:' not in each_src:
                        each_src = f'https:{each_src}'
                    download_addr_url.append(each_src)
                base_ret_data['download_addr_url_list2'] = download_addr_url
            except Exception as E:
                base_ret_data['download_addr_url_list2'] = []

            # 获取tag
            tag1, tag2, tag3, tag1_id, tag2_id, tag3_id = self.douyin_tag_info_html(detail['videoTag'])
            base_ret_data['tag_info'] = {
                'tag1': tag1,
                'tag2': tag2,
                'tag3': tag3,
                'tag1_id': tag1_id,
                'tag2_id': tag2_id,
                'tag3_id': tag3_id,
            }

        if is_ocr:
            if base_ret_data['aweme_type'] == 0:
                base_ret_data['aweme_type'] = 1
            return base_ret_data
        return {'code': 200, 'is_alive': is_alive, 'date': base_ret_data}

    @staticmethod
    def is_hot_note(like_count, follower_count):
        """
        any 2024-10-22
            增加低粉爆款（笔记），低粉爆款的笔记取数逻辑为：
            1. 点赞数>=10000的视频
            2. 点赞数/粉丝数>=10
        """
        is_hot = 0
        try:
            if like_count >= 10000 and follower_count > 0:
                if like_count / follower_count >= 10:
                    is_hot = 1
        except:
            pass
        return is_hot

    # 抖音v3版本 请求参数
    @staticmethod
    def douyin_v3_common_params():
        return {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            # "sec_user_id":"MS4wLjABAAAAHBzaYq41eZhmDn9cOTQya8X3-YxoAYTOLm1BM947R_A",
            "max_cursor": "0",
            "locate_query": "false",
            "show_live_replay_strategy": "1",
            "need_time_list": "1",
            "time_list_query": "0",
            "whale_cut_token": "",
            "cut_version": "1",
            # "count":"18",
            "publish_video_strategy_type": "2",
            "pc_client_type": "1",
            "version_code": "170400",
            "version_name": "17.4.0",
            "cookie_enabled": "true",
            "screen_width": "354",
            "screen_height": "852",
            "browser_language": "zh-CN",
            "browser_platform": "Win32",
            "browser_name": "Edge",
            "browser_version": "120.0.0.0",
            "browser_online": "true",
            "engine_name": "Blink",
            "engine_version": "120.0.0.0",
            "os_name": "Android",
            "os_version": "6.0",
            "cpu_core_num": "12",
            "device_memory": "8",
            "platform": "Android",
            "downlink": "10",
            "effective_type": "4g",
            "round_trip_time": "250",
        }

    # 抖音v3版本 用户详情
    def douyin_v3_user_info(self, sec_uid, user_proxies=None):
        ret_ok, ret_spider_info = 0, {}
        try:
            session = HttpJike.requests_retry_session()  # 多次尝试
            base_ua = config_dict['base_ua']
            headers = {
                "cookie": random.choice(mode_pro.ttwid_cookie_tt(get_cache=1)),
                "referer": "https://www.douyin.com/user",
                "user-agent": base_ua
            }
            params = self.douyin_v3_common_params()
            params["sec_user_id"] = sec_uid
            params["X-Bogus"] = mode_pro.douyin_v3_get_xb(urlencode(params, safe='='), base_ua)
            url = "https://www.douyin.com/aweme/v1/web/user/profile/other/?" + urlencode(params, safe='=')
            response = session.get(url, headers=headers, timeout=3,
                                   proxies=HttpJike.proxies_choose() if user_proxies else None)
            if response.status_code == 200:
                data_data = response.json()
                data_user_info = data_data.get('user')
                if data_user_info:
                    # 未知 黄V 蓝V
                    user_type = '未知'
                    organization = ''
                    custom_verify = data_user_info.get('custom_verify', '')
                    enterprise_verify_reason = data_user_info.get('enterprise_verify_reason', '')
                    if len(custom_verify) > 0:
                        user_type = '黄V'
                        organization = custom_verify
                    if len(enterprise_verify_reason) > 0:
                        user_type = '蓝V'
                        organization = enterprise_verify_reason

                    try:
                        author_head = data_user_info['avatar_thumb']['url_list'][0]
                    except:
                        author_head = ''

                    # 性别
                    sex = -1
                    gender = data_user_info.get('gender', None)
                    if gender is not None:
                        sex = gender
                        if sex == 1:
                            sex = 1
                        else:
                            sex = 2

                    ret_spider_info = {
                        'nickname': data_user_info['nickname'],
                        'video_count': data_user_info['aweme_count'],
                        'follower_count': data_user_info['following_count'],
                        'good_count': data_user_info['total_favorited'],
                        'loc': data_user_info.get('ip_location', ''),
                        'sex': sex,
                        'introduce': data_user_info.get('signature', ''),
                        'user_id': data_user_info['uid'],
                        'author_head': author_head,
                        'user_update_time': int(time.time()),

                        # 抖音特有字段
                        'douyin_user_org_type': user_type,
                        'douyin_organization': organization,
                        'douyin_unique_id': data_user_info['unique_id'],
                        'douyin_sec_uid': data_user_info['sec_uid'],
                    }
                    ret_ok = 1
        except Exception as E:
            print(E)
        return ret_ok, ret_spider_info

    # 抖音v3版本 用户详情
    def douyin_v3_video_list(self, sec_uid, user_proxies=None):
        ret_ok, ret_spider_info = 0, []
        try:
            session = HttpJike.requests_retry_session()  # 多次尝试
            base_ua = config_dict['base_ua']
            headers = {
                "cookie": random.choice(mode_pro.ttwid_cookie_tt(get_cache=1)),
                "referer": "https://www.douyin.com/user",
                "user-agent": base_ua
            }
            params = self.douyin_v3_common_params()
            params["sec_user_id"] = sec_uid
            params["count"] = 18
            # params["max_cursor"] = 18  # '0'
            params["X-Bogus"] = mode_pro.douyin_v3_get_xb(urlencode(params, safe='='), base_ua)
            url = "https://www.douyin.com/aweme/v1/web/aweme/post/?" + urlencode(params, safe='=')
            response = session.get(url, headers=headers, timeout=3,
                                   proxies=HttpJike.proxies_choose() if user_proxies else None)
            if response.status_code == 200:
                data_data = response.json()
                data_aweme_list = data_data.get('aweme_list')
                if data_aweme_list:
                    for iv in data_aweme_list:
                        data_user_info = iv['author']
                        aweme_type = DouyinJike().douyin_video_type(iv.get("aweme_type", 0))

                        try:
                            v_id = iv['video']['play_addr']['uri']
                            if aweme_type == 68:
                                v_id = ''
                        except:
                            v_id = ''

                        # 播放时长
                        try:
                            release_time = round(int(iv['duration']) / 1000)  # 视频长度
                        except:
                            release_time = 0

                        # 视频下载地址
                        try:
                            download_addr_url_list = iv['video']['play_addr']['url_list']
                        except:
                            download_addr_url_list = []

                        # 视频下载地址 第二类型
                        download_addr_url_list2 = download_addr_url_list

                        # mp3 url
                        try:
                            mp3_url_list = iv['music']['play_url']['url_list']

                            if '.mp3' in iv['music']['play_url']['url_list'][0]:
                                pass
                            else:
                                mp3_url_list = []
                        except:
                            mp3_url_list = []

                        ret_spider_dict = {
                            '_id': iv['aweme_id'],
                            'video_url': f"https://www.douyin.com/note/{iv['aweme_id']}",
                            'aweme_type': aweme_type,
                            'title': iv['desc'],
                            'video_cover': iv['video']['cover']['url_list'][0],
                            'create_time': iv['create_time'],

                            'good_count': iv['statistics']['digg_count'],
                            'comment_count': iv['statistics']['comment_count'],
                            'share_count': iv['statistics']['share_count'],
                            'collect_count': iv['statistics']['collect_count'],
                            'release_time': release_time,
                            'v_id': v_id,

                            'download_addr_url_list': download_addr_url_list,
                            'download_addr_url_list2': download_addr_url_list2,
                            'mp3_url_list': mp3_url_list,

                            # 用户信息
                            'nickname': data_user_info['nickname'],
                            'user_id': data_user_info['uid'],
                            'douyin_sec_uid': data_user_info['sec_uid'],

                        }
                        ret_spider_info.append(ret_spider_dict)
                    ret_ok = 1
        except Exception as E:
            print(E)
        return ret_ok, ret_spider_info[:10]  # 固定返回10个

    # 抖音xb - 纯Python版本（无需Node.js环境）
    @staticmethod
    def douyin_xb(url, ua, ms_token=''):
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

        def rc4_crypt(key, data):
            """RC4加密算法 - 对应JavaScript中的_0x238632函数"""
            s = list(range(256))
            j = 0

            # Key-scheduling algorithm (KSA)
            for i in range(256):
                j = (j + s[i] + ord(key[i % len(key)])) % 256
                s[i], s[j] = s[j], s[i]

            # Pseudo-random generation algorithm (PRGA)
            i = j = 0
            result = []
            for char in data:
                i = (i + 1) % 256
                j = (j + s[i]) % 256
                s[i], s[j] = s[j], s[i]
                k = s[(s[i] + s[j]) % 256]
                result.append(chr(ord(char) ^ k))

            return ''.join(result)

        def hex_to_bytes_array(hex_string):
            """将十六进制字符串转换为字节数组 - 对应JavaScript中的_0x237a87函数"""
            return bytes.fromhex(hex_string)

        def get_one_list(url_para, md5her):
            """获取第一个列表"""
            return hex_to_bytes_array(md5her)

        def get_two_list():
            """获取第二个列表"""
            return hex_to_bytes_array('59adb24ef3cdbe0297f05b395827453f')

        def get_three_list(ua):
            """获取第三个列表"""
            str_3 = rc4_crypt("\u0001\u0001\b", ua)
            try:
                str_3_bytes = str_3.encode('latin-1')
                str_3 = base64.b64encode(str_3_bytes).decode('ascii')
            except:
                str_3 = base64.b64encode(str_3.encode('utf-8', errors='ignore')).decode('ascii')
            str_3 = hashlib.md5(str_3.encode('utf-8')).hexdigest()
            return hex_to_bytes_array(str_3)

        def get_time_sign(time_now):
            """获取时间签名"""
            time_int = int(float(time_now) * 1000)
            result = []
            for i in [24, 16, 8, 0]:
                result.append((time_int >> i) & 255)
            return result

        def get_num_sign():
            """获取固定数字签名"""
            num = 3963386674
            result = []
            for i in [24, 16, 8, 0]:
                result.append((num >> i) & 255)
            return result

        def get_last_sign(index_list):
            """计算异或签名"""
            result = 0
            for val in index_list:
                if result == 0:
                    result = int(val)
                else:
                    result ^= int(val)
            return result

        def get_index_str(url_para, ua, time_now, md5her):
            """生成索引字符串"""
            get_one_list_list = get_one_list(url_para, md5her)
            get_two_list_list = get_two_list()
            get_three_list_list = get_three_list(ua)

            # 注意：这里保持JavaScript中的浮点数
            index_list_1 = [64, 1.00390625, 1, 8,
                            get_one_list_list[14], get_one_list_list[15],
                            get_two_list_list[14], get_two_list_list[15],
                            get_three_list_list[14], get_three_list_list[15]]

            index_list_2 = get_time_sign(time_now)
            index_list_3 = get_num_sign()
            index_list = index_list_1 + index_list_2 + index_list_3

            index_list_last = get_last_sign(index_list)
            index_list.append(index_list_last)

            last_str = ""
            for val in index_list:
                last_str += chr(int(val))

            # 对应JavaScript中的最后处理
            last_str = "\u0002ÿ" + rc4_crypt("ÿ", last_str)
            return last_str

        def all_num(last_str):
            """将字符串转换为数值列表"""
            num_list = []
            for char in last_str:
                num_list.append(ord(char))

            result = []
            for i in range(0, len(num_list), 3):
                group = num_list[i:i + 3]
                if len(group) >= 3:
                    num = (group[0] << 16) ^ (group[1] << 8) ^ group[2]
                elif len(group) == 2:
                    num = (group[0] << 16) ^ (group[1] << 8)
                else:
                    num = group[0] << 16
                result.append(num)

            return result

        def get_xb(all_num_list):
            """生成最终的X-Bogus字符串"""
            _str = "Dkdpgh4ZKsQB80/Mfvw36XI1R25-WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe="
            result_str = ""

            for num in all_num_list:
                for mask, shift in [[16515072, 18], [258048, 12], [4032, 6], [63, 0]]:
                    num_1 = num & mask
                    num_2 = num_1 >> shift
                    result_str += _str[num_2]

            return result_str

        # 执行X-Bogus生成
        try:
            # 提前对参数进行处理
            md5_url = mode_pros.md5_base(url_para)

            str1 = bytes.fromhex(md5_url)
            hash_object = hashlib.md5(str1)
            md5her = hash_object.hexdigest()

            # 生成时间戳（保持和JavaScript一致的格式）
            time_now = "{:.3f}".format(time.time())

            # 生成X-Bogus
            last_str = get_index_str(url_para, ua, time_now, md5her)
            all_num_list = all_num(last_str)
            res = get_xb(all_num_list)

            result_url = f'{url}&msToken={ms_token}&X-Bogus={res}'
            return result_url
        except Exception as e:
            # 如果纯Python版本失败，可以在这里添加fallback逻辑
            print(f"X-Bogus生成失败: {e}")
            # 返回不带X-Bogus的URL作为fallback
            return f'{url}&msToken={ms_token}'

    #
