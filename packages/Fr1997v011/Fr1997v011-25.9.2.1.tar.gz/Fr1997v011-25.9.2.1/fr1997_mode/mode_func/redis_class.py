import redis
from .base_class import *


class RedisDb(BaseFr1997):

    def db_redis(self, redis_db=0, db=0):
        redis_cfg = 'redis_loc'
        if redis_db == 0:
            redis_cfg = 'redis_loc'
        elif redis_db == 10:
            redis_cfg = 'redis_spider1'
        elif redis_db == 11:  # 内网
            redis_cfg = 'redis_spider1'
        elif redis_db == 3:
            redis_cfg = 'redis_spider3'

        if self.path == 1:
            redis_host = '127.0.0.1'
        else:
            redis_host = config_dict['redis'][redis_cfg]['host']
        redis_port = config_dict['redis'][redis_cfg]['port']
        redis_pwd = config_dict['redis'][redis_cfg]['pwd']
        return redis.StrictRedis(host=redis_host, port=int(redis_port), password=redis_pwd, db=db)

    # Redis 表记录
    @staticmethod
    def redis_task(task_name):
        """
            tp:选用哪个数据库
            type:存储类型
                kv=键值对   start_：前缀
        """
        redis_task = {
            'douyin_user_cloud': {
                'redis_db': 3, 'db': 6, 'type': 'kv', 'start_': 'douyin_user_cloud', 'ttl': 6000
            },  # 抖音用户云词 几万
            'douyin_user_krm': {
                'redis_db': 3, 'db': 6, 'type': 'kv', 'start_': 'douyin_user_krm', 'ttl': 6000
            },  # 抖音krm
            'douyin_user_ranks': {
                'redis_db': 3, 'db': 6, 'type': 'kv', 'start_': 'douyin_user_ranks', 'ttl': 6000
            }  # 抖音krm
        }
        return redis_task[task_name]
