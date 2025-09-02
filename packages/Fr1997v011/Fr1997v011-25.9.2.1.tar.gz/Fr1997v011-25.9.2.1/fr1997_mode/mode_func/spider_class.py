import time
from .base_class import *
from .http_class import HttpJike
from .douyin_class import DouyinJike

mode_douyin = DouyinJike()


# 采集
class SpiderJike:
    # >>>>----------------       spider_func         ----------------<<<<<
    # ai api2d 余额查询
    @staticmethod
    def ai_api2d_token_count():
        url = config_dict['ai']['api2d']['balance_url']
        token = config_dict['ai']['api2d']['token']['token1']
        headers = {
            'Authorization': f'Bearer {token}',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }
        res = HttpJike.get(url=url, headers=headers)
        if res.status_code == 200:
            data_data = res.json
            token_count = data_data['total_granted']
            return token_count

    # 获取 moonshot 余额
    @staticmethod
    def ai_moonshot_token_count():
        url = config_dict['ai']['moonshot']['balance_url']
        token = config_dict['ai']['moonshot']['token']['token1']
        headers = {
            'Authorization': f'Bearer {token}',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }
        res = HttpJike.get(url=url, headers=headers)
        if res.status_code == 200:
            data_data = res.json
            available_balance = data_data['data']['available_balance']
            return available_balance

    # 百度IP定位
    @staticmethod
    def api_baidu_ip(ip='60.12.139.18'):
        """
        http://api.map.baidu.com/location/ip?ak=您的AK&ip=您的IP&coor=bd09ll //HTTP协议
        https://api.map.baidu.com/location/ip?ak=您的AK&ip=您的IP&coor=bd09ll //HTTPS协议

        --参数
        ak    密钥   string    必填    E4jYvwZbl9slCjUALZpnl1xawvoIAlrP
        ip          string    可选
        sn    校验   string    可选
        coor  详细请求  string  可选
        -coor不出现、或为空：百度墨卡托坐标，即百度米制坐标
        -coor = bd09ll：百度经纬度坐标，在国测局坐标基础之上二次加密而来
        -coor = gcj02：国测局02坐标，在原始GPS坐标基础上，按照国家测绘行业统一要求，加密后的坐标
        """
        city = '北京'
        province = '北京'

        try:
            ak = 'E4jYvwZbl9slCjUALZpnl1xawvoIAlrP'
            url = f'http://api.map.baidu.com/location/ip?ak={ak}&ip={ip}&coor=bd09ll'
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; WOW64; MSIE 10.0; Windows NT 6.2)'
            }
            response = HttpJike.get(url=url, headers=headers)
            if response.status_code == 200:
                data_data = response.json
                content = data_data.get('content')
                status = data_data.get('status')
                if content is not None and status == 0:
                    address_detail = content.get('address_detail')
                    if address_detail is not None:
                        city_data = address_detail.get('city')
                        province_data = address_detail.get('province')

                        # 省会 城市 判断
                        if len(province_data) > 0:
                            province = province_data
                            if len(city_data) > 0:
                                city = city_data
                            else:
                                city = province
                        else:
                            pass
                        print(f'省会:{province},城市:{city}')
                        return data_data
                    else:
                        pass
                else:
                    pass
            else:
                pass
        except:
            pass
        return [province, city]

    # 和风天气
    @staticmethod
    def api_qweather(location):
        key = 'fd9e6c4c11254fe19f2b4f46c3653397'
        url = f'https://geoapi.qweather.com/v2/city/lookup?&location={location}&key={key}'
        response = HttpJike.get(url=url)
        if response.status_code == 200:
            j = response.json
            id = j['location'][0]['id']

            # 二,根据城市id 获取城市天气
            url = f'https://devapi.qweather.com/v7/weather/now?location={id}&key={key}'
            headers = {
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)'
            }
            response = HttpJike.get(url=url)
            if response.status_code == 200:
                weather_now = response.json
                t_s = time.strftime("%X", time.localtime(time.time()))

                location = f'{location}'
                t_s = f'{t_s}'
                temp = f"{weather_now['now']['temp']}℃"  # 当前温度
                feelsLike = f"{weather_now['now']['feelsLike']}℃"  # 体感温度
                text_now = f"{weather_now['now']['text']}"  # 当前天气
                feng = f"{weather_now['now']['windDir']}{weather_now['now']['windScale']}级 {weather_now['now']['windSpeed']}公里/小时"  # 风
                humidity = f"{weather_now['now']['humidity']}%"  # 湿度
                precip = f"{weather_now['now']['precip']}毫米"  # 降水量值
                pressure = f"{weather_now['now']['pressure']}百帕"  # 大气压强
                vis = f"{weather_now['now']['vis']}公里"  # 能见度值
                cloud = f"{weather_now['now']['cloud']}%"  # 当前云量
                return {'location': location,
                        't_s': t_s,
                        'temp': temp,
                        'feelsLike': feelsLike,
                        'text_now': text_now,
                        'feng': feng,
                        'humidity': humidity,
                        'precip': precip,
                        'pressure': pressure,
                        'vis': vis,
                        'cloud': cloud,
                        }

    # 发送QQ邮件
    @staticmethod
    def send_email(title, text):
        """
        pip install PyEmail
        pip install email
        pip install smtplib
        """

        # 发送邮件配置
        import smtplib
        from email.mime.text import MIMEText
        # email 用于构建邮件内容
        from email.header import Header

        from_addr = '1079146598@qq.com'  # 发信方邮箱
        password = 'ouacnpxmtbavjecc'  # 收信方授权码
        to_addr = '3084447185@qq.com'  # 收信方邮箱
        # to_addr = '1048995287@qq.com'  # 王伟南

        smtp_server = 'smtp.qq.com'  # 发信服务器

        # ，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
        msg = MIMEText(text, 'plain', 'utf-8')  # 正文内容

        # 邮件头信息
        msg['From'] = Header(from_addr)
        msg['To'] = Header(to_addr)
        msg['Subject'] = Header(title)

        server = smtplib.SMTP_SSL(host=smtp_server)  # 开启发信服务
        server.connect(smtp_server, 465)  # 加密传输

        server.login(from_addr, password)  # 登录发信邮箱
        server.sendmail(from_addr, to_addr, msg.as_string())  # 发送邮件
        server.quit()  # 关闭服务器

    # fr1997 web 请求ip
    @staticmethod
    def api_fr1997_ip():
        url = 'https://dv.fr1997.cn/test_ip'
        res = HttpJike.get(url=url, proxies=HttpJike.proxies_choose(1))
        if res.status_code == 200:
            return res.json['test_ip']

    # 抖音视频数据解析
    @staticmethod
    def douyin_video_response(res_data, tp='django_video_info'):
        base_ret_data = {'aweme_type': 1, 'is_alive': 1}

        # 是否存在
        if '因作品权限或已被删除，无法观看，去看看其他作品吧' in str(res_data):
            base_ret_data['is_alive'] = 0
            return base_ret_data

        # 获取视频类型
        aweme_type = mode_douyin.douyin_video_type(res_data.get("aweme_type", 0))
        if aweme_type == 68:
            base_ret_data['aweme_type'] = aweme_type
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

        # 视频下载地址
        try:
            download_addr_url_list = res_data['video']['download_addr']['url_list']
        except:
            download_addr_url_list = []

        # 视频下载地址 第二类型
        try:
            download_addr_url_list2 = res_data['video']['play_addr']['url_list']
        except:
            download_addr_url_list2 = []

        # mp3 url
        try:
            mp3_url_list = res_data['music']['play_url']['url_list']

            if '.mp3' in res_data['music']['play_url']['url_list'][0]:
                pass
            else:
                mp3_url_list = []
        except:
            mp3_url_list = []

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
        base_ret_data['user_id'] = user_id

        base_ret_data['update_time'] = int(time.time())
        base_ret_data['create_date'] = create_time
        base_ret_data['release_time'] = release_time
        base_ret_data['nickname'] = nickname
        base_ret_data['author_head'] = author_head
        base_ret_data['describe'] = describe

        base_ret_data['download_addr_url_list2'] = download_addr_url_list2
        base_ret_data['download_addr_url_list'] = download_addr_url_list
        base_ret_data['mp3_url_list'] = mp3_url_list

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
            try:
                base_ret_data['follower_count'] = res_data['author']['follower_count']
            except:
                base_ret_data['follower_count'] = 0
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
        elif tp == 'wav_small':
            # 获取音频
            bit_rate = res_data['video']['bit_rate'][-1]
            base_ret_data['sec_uid'] = sec_uid
            base_ret_data['wav_size'] = bit_rate['bit_rate']
            base_ret_data['wav_url'] = bit_rate['play_addr']['url_list']
            return base_ret_data
        else:
            return base_ret_data

    # 【api】 视频详情 2024-05-28
    @staticmethod
    def douyin_video_response2(res_data, tp='django_video_info'):
        base_ret_data = {'aweme_type': 1, 'is_alive': 1}

        # 是否存在
        if '因作品权限或已被删除，无法观看，去看看其他作品吧' in str(res_data):
            base_ret_data['is_alive'] = 0
            return base_ret_data

        # 获取视频类型
        aweme_type = mode_douyin.douyin_video_type(res_data.get('aweme_type', 0))
        if aweme_type == 68:
            base_ret_data['aweme_type'] = aweme_type
            return base_ret_data

        like_num = res_data["statistics"]["digg_count"]
        forward_num = res_data["statistics"]["share_count"]
        comment_num = res_data["statistics"]["comment_count"]
        collect_count = res_data["statistics"]["collect_count"]

        # 播放时长
        try:
            release_time = round(int(res_data['duration']) / 1000)  # 视频长度
        except:
            release_time = 0

        # 昵称
        nickname = res_data["author"]["nickname"]

        # 描述
        describe = res_data["author"]["signature"]

        # sec_uid
        sec_uid = res_data['author']['sec_uid']

        # user_id
        user_id = res_data['author']['uid']

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

        # 视频下载地址
        try:
            download_addr_url_list = res_data['video']['download_addr']['url_list']
        except:
            download_addr_url_list = []

        # 视频下载地址 第二类型
        try:
            download_addr_url_list2 = res_data['video']['play_addr']['url_list']
        except:
            download_addr_url_list2 = []

        # mp3 url
        try:
            mp3_url_list = res_data['music']['play_url']['url_list']

            if '.mp3' in res_data['music']['play_url']['url_list'][0]:
                pass
            else:
                mp3_url_list = []
        except:
            mp3_url_list = []

        # 增加视频分类
        """
            [
                {'tag_id': 2013, 'tag_name': '体育', 'level': 1},
                {'tag_id': 2013004, 'tag_name': '球类项目', 'level': 2},
                {'tag_id': 2013004001, 'tag_name': '足球', 'level': 3}
            ]
            为视频分类，tag1 tag2 tag3 
        """
        video_tag = res_data.get('video_tag', [])
        tag1, tag2, tag3, tag1_id, tag2_id, tag3_id = mode_douyin.douyin_tag_info(video_tag)

        # 视频创建时间比较特殊，如果没有创建时间，默认一个值
        create_time = res_data.get('create_time', config_dict['douyin']['douyin_video_create_time'])

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
        base_ret_data['user_id'] = user_id

        base_ret_data['update_time'] = int(time.time())
        base_ret_data['create_date'] = create_time
        base_ret_data['release_time'] = release_time
        base_ret_data['nickname'] = nickname
        base_ret_data['author_head'] = author_head
        base_ret_data['describe'] = describe

        base_ret_data['download_addr_url_list2'] = download_addr_url_list2
        base_ret_data['download_addr_url_list'] = download_addr_url_list
        base_ret_data['mp3_url_list'] = mp3_url_list

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
            try:
                base_ret_data['follower_count'] = res_data['author']['follower_count']
            except:
                base_ret_data['follower_count'] = 0
            base_ret_data['sec_uid'] = res_data['author']['sec_uid']
            base_ret_data['tag1'] = tag1
            base_ret_data['tag2'] = tag2
            base_ret_data['tag3'] = tag3

            base_ret_data['tag1_id'] = tag1_id
            base_ret_data['tag2_id'] = tag2_id
            base_ret_data['tag3_id'] = tag3_id
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
        elif tp == 'wav_small':
            # 获取音频
            bit_rate = res_data['video']['bit_rate'][-1]
            base_ret_data['sec_uid'] = sec_uid
            base_ret_data['wav_size'] = bit_rate['bit_rate']
            base_ret_data['wav_url'] = bit_rate['play_addr']['url_list']
            return base_ret_data
        else:
            return base_ret_data
