import uuid
from .cache_class import *  # 缓存库

false = False
true = True
null = None
undefined = "undefined"
F_keyword = 'keyword'


class BaseFr1997:

    def __init__(self):
        super().__init__()
        self.path = self.run_machine()['platform']
        self.path_info = self.run_machine()

    # 判断运行环境 在哪个机器
    @staticmethod
    def run_machine():
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1])
        machine_cfg = config_dict['machine_cfg']  # 计算机配置
        if mac_address in machine_cfg:
            return machine_cfg[mac_address]
        else:
            return {'type': 'other', 'platform': 0}


# 字段的统一(在之后的版本中 舍弃)
class FieldRule:
    __keyword__ = F_keyword
