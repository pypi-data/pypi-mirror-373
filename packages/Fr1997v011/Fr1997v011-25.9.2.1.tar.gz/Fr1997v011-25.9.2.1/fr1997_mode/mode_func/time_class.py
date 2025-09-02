import time
from datetime import datetime, timedelta
from .base_class import *


# 时间
class TimeJike:
    @staticmethod
    def zero_clock(day=0) -> int:
        """
        获取某一天的零点时间戳。

        :param day: 距离今天的天数（正数表示之前的日期，负数表示之后的日期）
        :return: 指定日期的零点时间戳（整数）
        """
        # 获取当前日期时间并去除时分秒，获取当天零点
        target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # 计算目标日期零点
        target_date -= timedelta(days=day)

        # 转换为时间戳并返回
        return int(target_date.timestamp())

    @staticmethod
    def today_seconds() -> int:
        """
        获取现在是今天的第多少秒。

        :return: 当前时间距离今天零点的秒数。
        """
        # 获取当前时间
        now = datetime.now()

        # 获取今天零点的时间
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # 计算当前时间与今天零点之间的秒数差
        return int((now - midnight).total_seconds())

    @staticmethod
    def hours_start_time(hours=0) -> int:
        """
        获取指定小时的开始时间戳。

        :param hours: 与当前时间相差的小时数（正数表示过去的小时，负数表示未来的小时）
        :return: 指定小时的开始时间戳（整数）
        """
        # 获取当前时间，并将分钟、秒和微秒置零，得到本小时的开始时间
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)

        # 计算目标小时的开始时间
        target_hour = current_hour - timedelta(hours=hours)

        # 转换为时间戳并返回
        return int(target_hour.timestamp())

    @staticmethod
    def week(t=None) -> str:
        """
        返回指定时间戳的星期几。

        :param t: 时间戳，默认值为当前时间。
        :return: 周几的中文名称（字符串）。
        """
        if t is None:
            t = int(time.time())

        # 将星期几的数字映射到中文名称
        weekday_map = {
            0: "周日",
            1: "周一",
            2: "周二",
            3: "周三",
            4: "周四",
            5: "周五",
            6: "周六",
        }

        # 获取指定时间戳的星期几
        weekday_number = datetime.fromtimestamp(t).weekday()

        # 返回对应的中文名称
        return weekday_map[weekday_number]

    @staticmethod
    def ymd(t=None) -> str:
        """
        将时间戳转换为日期字符串（格式：YYYYMMDD）。

        :param t: 时间戳，默认为当前时间。
        :return: 格式化的日期字符串。
        """
        if t is None:
            t = datetime.now()
        else:
            t = datetime.fromtimestamp(t)

        return t.strftime("%Y%m%d")

    @staticmethod
    def y_m_d(t=None) -> str:
        """
        将时间戳转换为日期字符串（格式：YYYY-MM-DD）。

        :param t: 时间戳，默认为当前时间。
        :return: 格式化的日期字符串。
        """
        # 使用当前时间作为默认值
        t = datetime.fromtimestamp(t) if t is not None else datetime.now()

        return t.strftime("%Y-%m-%d")

    @staticmethod
    def y_m_d__h_m_s(t=None) -> str:
        """
        将时间戳转换为日期和时间字符串（格式：YYYY-MM-DD HH:MM:SS）。

        :param t: 时间戳，默认为当前时间。
        :return: 格式化的日期和时间字符串。
        """
        # 使用当前时间作为默认值
        t = datetime.fromtimestamp(t) if t is not None else datetime.now()

        return t.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def hour(t=None) -> int:
        """
        获取指定时间戳的小时（24小时制）。

        :param t: 时间戳，默认为当前时间。
        :return: 小时（整数）。
        """
        t = datetime.fromtimestamp(t) if t is not None else datetime.now()
        return t.hour

    @staticmethod
    def minute(t=None) -> int:
        """
        获取指定时间戳的分钟。

        :param t: 时间戳，默认为当前时间。
        :return: 分钟（整数）。
        """
        t = datetime.fromtimestamp(t) if t is not None else datetime.now()
        return t.minute

    @staticmethod
    def hour_minute_seconds(t=None):
        """
        获取指定时间戳的时、分、秒（整数）。

        :param t: 时间戳，默认为当前时间。
        :return: (小时, 分钟, 秒)
        """
        t = datetime.fromtimestamp(t) if t is not None else datetime.now()
        return t.hour, t.minute, t.second
