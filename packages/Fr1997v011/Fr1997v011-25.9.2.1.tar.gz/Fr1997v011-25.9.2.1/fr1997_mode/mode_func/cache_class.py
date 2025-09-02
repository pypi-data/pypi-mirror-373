import sys
import memcache  # pip3 install python-memcached


# 存储内存数据
def cache_set(key, data, save_time=None):
    mc = memcache.Client(['127.0.0.1:11211'], debug=True)
    if save_time:
        mc.set(key=key, val=data, time=save_time)
    else:
        mc.set(key=key, val=data)  # 永久存储


# 获取内存数据
def cache_get(key):
    mc = memcache.Client(['127.0.0.1:11211'], debug=True)
    return mc.get(key)


# 内存缓存所有数据
config_dict = cache_get("my_config_dict")
if not config_dict:
    print("私人包 禁止使用")
    sys.exit(0)
