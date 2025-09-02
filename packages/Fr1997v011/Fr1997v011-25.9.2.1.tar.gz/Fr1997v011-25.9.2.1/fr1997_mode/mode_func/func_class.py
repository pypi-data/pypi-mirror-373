import re
import time
import hashlib


# 静态函数 【其它函数集合】
class ModeStatic:
    # 手机号判断
    @staticmethod
    def phone_num(num):
        num = str(num.strip())
        # 中国联通：130，131，132，155，156，185，186，145，176
        # 中国移动：134, 135 ,136, 137, 138, 139, 147, 150, 151, 152, 157, 158, 159, 178, 182, 183, 184, 187, 188
        # 中国电信：133,153,189
        pat_lt = re.compile(r'^1(3[0-2]|45|5[5-6]|8[5-6]|76)\d{8}$')
        pat_yd = re.compile(r'^1(3[4-9]|47|5[0-27-9]|8[2-47-8]|78)\d{8}$')
        pat_dx = re.compile(r'^1(33|53|89)\d{8}$')

        if pat_lt.match(num):
            return f"联通_{pat_lt.match(num).group()}"
        elif pat_yd.match(num):
            return f"移动_{pat_yd.match(num).group()}"
        elif pat_dx.match(num):
            return f"电信_{pat_dx.match(num).group()}"
        else:
            return 0

    # 文本截取手机号  --> dict
    @staticmethod
    def phone_text(text):
        # text 不需要去空白
        phone_dict = {}  # 号码 + 个数

        # 匹配出所有 以1开头 11位的数字
        pat = re.compile(r'1\d{10}')
        res = pat.findall(text)

        # 统计每个好吗 以及个数 判断是否是标准号码 以及 运营商
        for phone in res:
            if phone_dict.get(phone):
                phone_dict[phone] += 1
            else:
                phone_dict[phone] = 1
        return phone_dict

    # Windows合法文件名 转为Windows合法文件名
    @staticmethod
    def title_path(title: str):
        lst = ['\r', '\n', '\\', '/', ':', '*', '?', '"', '<', '>', '|']
        for key in lst:
            title = title.replace(key, '-')
        if len(title) > 60:
            title = title[:60]
        return title.strip()

    # md5
    @staticmethod
    def md5_base(text, salt=None):
        md5 = hashlib.md5()
        if salt:
            md5 = hashlib.md5(salt.encode('utf-8'))
        md5.update(text.encode('utf-8'))
        result = md5.hexdigest()
        return result

    # ua 详情
    @staticmethod
    def ua_info(ua_string):
        from user_agents import parse
        user_agent = parse(ua_string)

        if user_agent.is_pc:
            user_use = '电脑'
        elif user_agent.is_mobile:
            user_use = '手机'
        elif user_agent.is_tablet:
            user_use = '平板'
        else:
            user_use = '其他'

        return {
            'browser': user_agent.browser.family,  # 浏览器
            'user_use': user_use,
            'browser_sys': user_agent.os.family,  # 系统
            'browser_device_brand': user_agent.device.brand,  # '品牌'
            'browser_device_type': user_agent.device.model,  # 'iPhone'
            'browser_all': str(user_agent),  # "iPhone / iOS 5.1 / Mobile Safari 5.1"
        }

    # 图片转base64
    @staticmethod
    def img_md5(pic_path):
        import base64
        # 将本地图片转换为base64编码和md5值
        with open(pic_path, 'rb') as f:
            image = f.read()
            image_base64 = str(base64.b64encode(image), encoding='utf-8')
            my_md5 = hashlib.md5()
            img_data = base64.b64decode(image_base64)
            my_md5.update(img_data)
            myhash = my_md5.hexdigest()
        return image_base64, myhash

    # cookie解析
    @staticmethod
    def cookies_split(cookie_str: str) -> str:
        # 判断是否为字符串
        if not isinstance(cookie_str, str):
            raise TypeError("cookie_str must be str")

        # 拆分Set-Cookie字符串,避免错误地在expires字段的值中分割字符串。
        cookies_list = re.split(', (?=[a-zA-Z])', cookie_str)

        # 拆分每个Cookie字符串，只获取第一个分段（即key=value部分）
        cookies_list = [cookie.split(';')[0] for cookie in cookies_list]

        # 拼接所有的Cookie
        cookie_str = ";".join(cookies_list)

        return cookie_str

    # 增长率
    @staticmethod
    def add_rate(v_new, v_old):
        if v_new == 0 or v_old == 0:
            rate = 0
        else:
            rate = round((v_new - v_old) / v_old * 100, 2)
        return rate

    # 增长率
    @staticmethod
    def cookie_str_to_cookie_dict(cookie_str: str):
        cookie_blocks = [cookie_block.split("=")
                         for cookie_block in cookie_str.split(";") if cookie_block]
        return {cookie[0].strip(): cookie[1].strip() for cookie in cookie_blocks}

    # 省份统一
    @staticmethod
    def extract_first_province(input_string):
        # 所有省份（简称和全称）
        province_list = [
            "北京市", "天津市", "上海市", "重庆市",
            "河北省", "山西省", "辽宁省", "吉林省", "黑龙江省", "江苏省",
            "浙江省", "安徽省", "福建省", "江西省", "山东省", "河南省",
            "湖北省", "湖南省", "广东省", "海南省", "四川省", "贵州省",
            "云南省", "陕西省", "甘肃省", "青海省", "台湾省",
            "内蒙古自治区", "广西壮族自治区", "西藏自治区", "宁夏回族自治区", "新疆维吾尔自治区",
            "香港特别行政区", "澳门特别行政区",
            # 简称
            "北京", "天津", "上海", "重庆",
            "河北", "山西", "辽宁", "吉林", "黑龙江", "江苏",
            "浙江", "安徽", "福建", "江西", "山东", "河南",
            "湖北", "湖南", "广东", "海南", "四川", "贵州",
            "云南", "陕西", "甘肃", "青海", "台湾",
            "内蒙古", "广西", "西藏", "宁夏", "新疆",
            "香港", "澳门"
        ]
        # 构建正则表达式（匹配任意省份名称）
        pattern = "|".join(province_list)
        province_regex = re.compile(pattern)

        match = province_regex.search(input_string)
        if match:
            return match.group(0)  # 返回第一个匹配的省份
        return ''

    # 性别统一
    @staticmethod
    def sex_mode(p, v):
        base_sex = {
            '男': 1,
            '女': 2,
        }

        if p == 'douyin':
            if v == 2 or v == '2':
                return 1
            if v == 1 or v == '1':
                return 2

        return -1


class KIL:
    field_kil = 'keyword_index_list'

    # 时间变量
    today = time.strftime("%Y%m%d", time.localtime(int(time.time())))
    today_int = int(time.mktime(time.strptime(today, '%Y%m%d')))

    # 记录转列表
    def kil_list(self, keyword_index_list):
        base_value = 0
        base_time_int = 0
        ret_kil_info = []
        data_list = keyword_index_list.split(';')

        # 每天只有一个数据
        time_str_set = []
        for i in data_list:
            # 初始值
            if '*' in i:
                base_time = int(i.split('*')[0])  # 初始时间
                base_value = int(i.split('*')[1])  # 初始值
                each_index = base_value
                time_int = int(time.mktime(time.strptime(str(base_time), '%Y%m%d')))
                base_time_int = time_int
                time_str = base_time
            # 减法操作
            elif '-' in i:
                each_day = int(i.split('_')[0])
                time_int = base_time_int + 86400 * each_day
                time_str = time.strftime("%Y%m%d", time.localtime(time_int))
                each_index = base_value - int(i.split('_')[-1].split('-')[1])  # 用初始值减去 '-' 后的值
            # 加法操作
            else:
                each_day = int(i.split('_')[0])
                time_int = base_time_int + 86400 * each_day
                time_str = time.strftime("%Y%m%d", time.localtime(time_int))
                each_index = base_value + int(i.split('_')[-1])  # 默认加法，取第6位及后续数字

            if str(time_str) not in time_str_set:
                ret_kil_info.append({
                    'time_str': time_str,
                    'time_int': time_int,
                    'value': each_index,  # 计算后的数值
                })
                time_str_set.append(str(time_str))

        return ret_kil_info

    # 增加新记录 限制天数 一天内重复更新要刷新
    def kul_add(self, kil_list_info, new_m):
        index9 = kil_list_info[-1]

        # 存在更新 不存在插入
        if self.today == index9['time_str']:
            kil_list_info[-1]['value'] = new_m
        else:
            kil_list_info.append({'time_str': self.today, 'time_int': self.today_int, 'value': new_m})

        return kil_list_info[-720:]

    # 记录列表转文本
    def kil_str(self, data_list):
        # 初始化结果字符串和基准值
        result = []
        base_value = None
        base_time_int = None

        for idx, entry in enumerate(data_list):
            value = entry['value']  # 提取数值
            time_int = entry['time_int']  # 提取数值

            if idx == 0:
                # 第一个元素作为初始值，格式为 time*value
                result.append(f"{entry['time_str']}*{value}")
                base_value = value
                base_time_int = time_int
            else:
                # 后续元素比较 value 和 base_value 的差异
                time_part = int((time_int - base_time_int) / 86400)
                diff = value - base_value
                if diff >= 0:
                    result.append(f"{time_part}_{diff}")  # 增加情况
                elif diff < 0:
                    result.append(f"{time_part}_{diff}")  # 减少情况

        return ";".join(result)  # 使用下划线连接结果

