from .gy_class import *
from .xhs_class import *
from .douyin_class import *
from .spider_class import *
from .django_class import *
from .mysql_class import *
from .cos_class import *
from .weixin_class import *
from .base_mode_class import *
from .func_class import *

mode_text = TextJike()  # 文本
mode_time = TimeJike()  # 时间
mode_myself = MyGy()  # 高阳
mode_xhs = XhsJike()  # 小红书
mode_data = DataJike()  # 数据分析
mode_pros = ModeStatic()  # 静态函数
mode_douyin = DouyinJike()  # douyin配置
mode_spider = SpiderJike()  # 数据请求
mode_pro = ModeFunc()
JFD = FieldRule()  # 字段约束
mode_feishu = Feishu()  # 飞书app api
mode_django = DjangoJike()  # django配置
mode_mysql = MysqlJike()  # 新版mysql控制未完成
mode_cos = Cos()  # cos
mode_fr_cos = Cos(server_select='personal')  # cos 高阳
mode_wx = WeiXinAuto()  # douyin配置
http_class = HttpJike()  # http

"""
    配置文件
        所有配置在这个地方读取
        使用内存缓存机制 memcache
        没有读取到内存中的配置，这个包相当于不能用
    pip3 cache purge
    pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple Fr1997v011==3.2.5

    pip3 install --upgrade Fr1997v011
    pip3 install redis
    pip3 install pymysql
    pip3 install elasticsearch
    pip3 install python-memcached
    pip3 install PyExecJS
    pip3 install -U cos-python-sdk-v5
    pip3 install pypinyin
    pip3 install django
    pip3 install lxml
    pip3 install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple moviepy==1.0.3

    pip install --upgrade Fr1997v011
    pip install redis
    pip install pymysql
    pip install elasticsearch
    pip install python-memcached
    pip install PyExecJS
    pip install -U cos-python-sdk-v5
    pip install pypinyin
    pip install django
    pip install lxml
    pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple moviepy==1.0.3

    pip38 install --upgrade Fr1997v011
    pip38 install redis
    pip38 install pymysql
    pip38 install elasticsearch
    pip38 install python-memcached
    pip38 install PyExecJS
    pip38 install -U cos-python-sdk-v5
    pip38 install pypinyin
    pip38 install django
    pip38 install lxml
    pip38 install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple moviepy==1.0.3
"""
