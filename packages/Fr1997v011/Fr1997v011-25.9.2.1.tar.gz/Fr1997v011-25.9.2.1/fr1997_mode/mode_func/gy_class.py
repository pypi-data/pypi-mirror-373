from .base_class import *


# myself 高阳本人信息
class MyGy:

    def __init__(self, **kwargs):
        self.fr1997_config_dict = cache_get("fr1997_config_dict")

    # 获取信息
    def get_myself_info(self):
        return self.fr1997_config_dict

    # 获取出生年龄等信息
    def get_age_info(self):
        name = self.fr1997_config_dict['name']
        return name
