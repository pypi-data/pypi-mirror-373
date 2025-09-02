import time
from concurrent.futures import ThreadPoolExecutor  # 线程次
from elasticsearch import Elasticsearch  # ES
from .base_class import *
from .data_class import DataJike

mode_data = DataJike()  # 数据分析


# Es数据库
class EsDb(BaseFr1997):
    def __init__(self):
        super().__init__()

    # 数据库链接
    def db_es(self):
        if self.path == 1:
            es_cfg = 'es_jike_in'
        else:
            es_cfg = 'es_jike_out'
        es_ip = config_dict['es'][es_cfg]['ip']
        es_user = config_dict['es'][es_cfg]['user']
        es_pwb = config_dict['es'][es_cfg]['pwd']
        es_port = config_dict['es'][es_cfg]['port']
        es = Elasticsearch([f'{es_ip}:{es_port}'], http_auth=(es_user, es_pwb))
        return es

    # 查询
    def es_search_new_20231215(self, table, query, _source, size=1, sort_info=None, is_ret_num=1, ret_num=0):
        body = {
            "query": query,
            "track_total_hits": True if is_ret_num == 1 else False,
            "size": size,
            "_source": _source,
        }

        # 排序
        if sort_info and sort_info != 0:
            body['sort'] = sort_info
        else:
            body['sort'] = {
                "_script": {
                    "script": "Math.random()",
                    "type": "number"
                }
            }

        es = self.db_es()
        response = es.search(
            index=table,
            body=body
        )
        _shards = response.get('_shards')
        if _shards:
            successful = _shards.get('successful')
            if successful > 0:
                value = response.get('hits')['total']['value']
                hits_list = response.get('hits')['hits']
                print(f'总个数:{value} 取出:{len(hits_list)}')
                if ret_num == 0:
                    return hits_list
                else:
                    return [hits_list, value]

    # 查询 适配es8 【jike_api py3.8.5✅】 【py3.6 目前不支持】
    def es_search(self, table, query, _source=None, size=1, sort_info=None, is_ret_num=1, ret_num=0):
        """
        优化后的 Es 查询函数。

        :param table: 索引名称
        :param query: 查询条件
        :param _source: 返回字段的筛选列表，默认为 None，表示返回所有字段
        :param size: 返回结果的数量，默认为 1
        :param sort_info: 排序信息，默认为 None
        :param is_ret_num: 是否返回总条数，默认为 1（True）
        :param ret_num: 返回结果模式，0 为只返回数据，1 为返回数据和总数
        :return: 返回的结果集或结果集和总数
        """
        # 构建参数字典
        params = {
            "index": table,
            "query": query,
            "track_total_hits": is_ret_num == 1,  # 是否追踪总匹配数
            "size": size
        }

        # 处理 _source 参数：如果提供，则使用它；否则返回所有字段
        if _source is not None:
            params["_source"] = _source

        # 排序处理
        if sort_info:
            params['sort'] = sort_info
        else:
            # 默认排序：随机排序
            params['sort'] = [{
                "_script": {
                    "script": "Math.random()",
                    "type": "number"
                }
            }]

        # 获取 ES 客户端
        es = self.db_es()

        # 执行搜索请求
        response = es.search(**params)

        # 处理响应
        _shards = response.get('_shards', {})
        successful = _shards.get('successful', 0)
        if successful > 0:
            value = response.get('hits', {}).get('total', {}).get('value', 0)
            hits_list = response.get('hits', {}).get('hits', [])
            print(f'总个数:{value} 取出:{len(hits_list)}')
            if ret_num == 0:
                return hits_list
            else:
                return [hits_list, value]
        else:
            print("ES查询失败或无结果")
            return [] if ret_num == 0 else [[], 0]

    # 查询 单条
    def es_search_one(self, table, _id, is_print=1):
        body = {
            "track_total_hits": True,
            "query": {
                "match": {"_id": _id}
            }
        }
        es = self.db_es()
        response = es.search(
            index=table,
            body=body
        )
        hits_list = response.get('hits')['hits']
        if is_print:
            value = response.get('hits')['total']['value']
            hits_list = response.get('hits')['hits']
            print(f'总个数:{value} 取出:{len(hits_list)}')
        return hits_list

    # 查询 纯es
    def es_search_es(self, table, query):

        es = self.db_es()
        response = es.search(
            index=table,
            body=query
        )
        return response

    # 数量
    def es_count(self, table):
        try:
            body = {
                "size": 1,
                "track_total_hits": True
            }
            es = self.db_es()
            response = es.search(
                index=table,
                body=body
            )
            count = response.get('hits')['total']['value']
            return count
        except:
            return -1

    # 数量
    def es_count_with_query(self, table, query):
        try:
            body = {
                "query": query,
                "size": 1,
                "track_total_hits": True
            }
            es = self.db_es()
            response = es.search(
                index=table,
                body=body
            )
            count = response.get('hits')['total']['value']
            return count
        except:
            return -1

    # 合并查询
    def es_search_merge(self, queries, table):
        es = self.db_es()

        def process_query(query):
            result = es.search(index=table, body=query)
            return result

        # 创建线程池
        pool = ThreadPoolExecutor(max_workers=5)  # 根据需求设置最大工作线程数

        # 提交查询任务到线程池
        futures = [pool.submit(process_query, query) for query in queries]

        # 获取查询结果
        results = [future.result() for future in futures]

        return results

    # 查询 分页
    def es_search_page(self, table, query, sort, size=1, offset=0, is_ret_num=1, is_print=0, **kwargs):
        body = {
            "query": query,
            "track_total_hits": True if is_ret_num == 1 else False,
            "size": size,
            "from": offset,
            "sort": sort,
        }

        _source = kwargs.get("_source")
        if _source is not None:
            body['_source'] = _source

        # 排序方式
        es = self.db_es()
        response = es.search(
            index=table,
            body=body
        )
        _shards = response.get('_shards')
        if _shards:
            successful = _shards.get('successful')
            if successful > 0:
                hits_list = response.get('hits')['hits']
                if is_print:
                    value = response.get('hits')['total']['value']
                    hits_list = response.get('hits')['hits']
                    print(f'总个数:{value} 取出:{len(hits_list)}')
                return hits_list

    # 查询 多表合并查询
    def es_search_alias(self, table, query, size=1, sort_info=None, is_ret_num=1, ret_num=0, **kwargs):
        body = {
            "query": query,
            "track_total_hits": True if is_ret_num == 1 else False,
            "size": size,
        }

        _source = kwargs.get("_source")
        if _source is not None:
            body['_source'] = _source

        # 根据规则排序
        if sort_info:
            body['sort'] = sort_info
        else:
            body['sort'] = {
                "_script": {
                    "script": "Math.random()",
                    "type": "number"
                }
            }

        es = self.db_es()
        response = es.search(
            index=table,
            body=body
        )

        hits = response['hits']
        db_total = hits['total']['value']
        hits_list = hits['hits']
        print(f'总个数:{db_total} 取出:{len(hits_list)}')

        if ret_num == 0:
            return hits_list
        else:
            return [hits_list, db_total]

    # 更新
    def es_create_update(self, doc, index, split_num=0):
        es = self.db_es()
        if doc:
            if split_num:
                each_item = mode_data.list_avg_split(doc, split_num * 2)
                for it_doc in each_item:
                    time.sleep(1)
                    es.bulk(body=it_doc, index=index)
            else:
                es.bulk(body=doc, index=index)

    # 更新 (自动判断内外网)
    def es_create_update_noIndex(self, doc, split_num=0):
        es = self.db_es()
        if doc:
            if split_num:
                each_item = mode_data.list_avg_split(doc, split_num * 2)
                for it_doc in each_item:
                    time.sleep(1)
                    es.bulk(body=it_doc)
            else:
                es.bulk(body=doc)

    # 更新 分表
    def es_create_update_alias(self, doc):
        es = self.db_es()
        if doc:
            es.bulk(body=doc)

    # 删除
    def es_del(self, query, index):
        es = self.db_es()
        es.delete_by_query(index=index, body=query, doc_type='_doc')

    # 多id查询
    def es_in_or_notin_20231215(self, table, shoulds, _source, split_num=200):
        """
        :param table: 数据表
        :param shoulds: 需要查询的 _id
        :return: [存在,数据info,不存在]
        """
        is_in = []
        is_in_data = {}
        shoulds_not = []
        es = self.db_es()

        each_item = mode_data.list_avg_split(shoulds, split_num)
        for it_shoulds in each_item:
            time.sleep(1)
            if it_shoulds:
                query = {
                    "bool": {
                        "must": [
                            {"terms": {"_id": it_shoulds}}
                        ],
                    }
                }
                body = {
                    "query": query,
                    "size": split_num,
                    "_source": _source,
                    "track_total_hits": 'true',
                }
                response = es.search(index=table, body=body)
                if response:
                    _shards = response.get('_shards')
                    if _shards:
                        successful = _shards.get('successful')
                        if successful > 0:
                            # 数据集
                            hits_list = response.get('hits')['hits']
                            print('本次取出符合条件的总数:', len(hits_list))

                            for index_x, i in enumerate(hits_list):
                                _s = i['_source']
                                _id = i['_id']
                                is_in.append(_id)
                                is_in_data[f'{_id}'] = _s

            it_shoulds_not = [i for i in it_shoulds if str(i) not in is_in]
            shoulds_not += it_shoulds_not
        return is_in, is_in_data, shoulds_not

    # 多id查询(多表)
    def es_in_or_notins(self, table, shoulds, query=None, is_print=0, is_index=0):
        """
        :param table: 数据表
        :param shoulds: 需要查询的 _id
        :return: [存在,数据info,不存在]
        """
        is_in = []
        is_in_data = {}
        es = self.db_es()
        if shoulds:
            if query is None:
                query = {
                    "bool": {
                        "must": [
                            {"terms": {"_id": shoulds}}
                        ],
                        # "must_not": {"match": {"update_time_1": 0}}
                    }
                }
            response = es.search(
                index=table,
                body={
                    "query": query,
                    "size": 1500,  # 返回数量
                    "track_total_hits": 'true',  # 显示总量有多少条
                }
            )
            if response:
                _shards = response.get('_shards')
                if _shards:
                    successful = _shards.get('successful')
                    if successful > 0:
                        # 数据集
                        hits_list = response.get('hits')['hits']
                        if is_print:
                            print('本次取出符合条件的总数:', len(hits_list))

                        for index_x, i in enumerate(hits_list):
                            _s = i['_source']
                            _id = i['_id']
                            is_in.append(_id)
                            if is_index == 1:
                                _s['_index'] = i['_index']
                            is_in_data[f'{_id}'] = _s

        shoulds_not = [i for i in shoulds if str(i) not in is_in]
        return is_in, is_in_data, shoulds_not

    # 返回所有的表
    def es_all_table(self):
        es_table_list = {}
        indices = self.db_es().cat.indices(format="json")
        for item in indices:
            table_name = eval(str(item))['index']
            docs_count = eval(str(item))['docs.count']
            store_size = eval(str(item))['store.size']
            es_table_list[table_name] = {'table_name': table_name, 'docs_count': docs_count, 'store_size': store_size, }
        return es_table_list
