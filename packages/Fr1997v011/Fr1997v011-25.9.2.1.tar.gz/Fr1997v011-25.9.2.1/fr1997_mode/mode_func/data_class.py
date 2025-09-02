import os
import re


# 数据
class DataJike:
    # 列表_多个字典_排序  -----↓↓↓↓-----列表 字典 集合 -----↓↓↓↓-----
    @staticmethod
    def list_dicts_order(list_xxx, order_by, positive_or_negative=True):
        if list_xxx:
            return sorted(list_xxx, key=lambda x: x[order_by], reverse=positive_or_negative)

    # 列表 -> 变字典 自动计算 排序
    @staticmethod
    def dicts_order_auto(list_xxx, order_by=True):
        if list_xxx:
            ret_dict = {}
            for i in list_xxx:
                if i in ret_dict:
                    ret_dict[i] += 1
                else:
                    ret_dict[i] = 1
            lis = sorted(ret_dict.items(), key=lambda i: i[1], reverse=order_by)
            return lis

    # 两个列表操作 差集
    @staticmethod
    def diff(l1, l2):
        return list(set(l1).difference(set(l2)))

    # 平均分块
    @staticmethod
    def list_avg_split(list_data, each_num):
        all_list = []
        for i in range(0, len(list_data), each_num):
            all_list.append(list_data[i:i + each_num])
        return all_list

    # 字典合并
    @staticmethod
    def dict_marge(*dicts):
        result = {}
        for d in dicts:
            result.update(d)
        return result

    # 简单字典 返回最大键  {1: 82.0, 2: 18.0} --> max:1
    @staticmethod
    def dict_max(dict_data):
        result_max = max(dict_data, key=lambda x: dict_data[x])
        return result_max

    # 列表 平均值
    @staticmethod
    def list_avg(list_data):
        if len(list_data) < 1:
            return None
        else:
            return int(sum(list_data) / len(list_data))

    # 列表 去除指定元素
    @staticmethod
    def list_remove_by(list_old, removes=None):
        new_list = []
        if list_old and removes and type(removes) == list:
            removes = list(set(removes))  # 去重
            for i in list_old:
                if i not in removes:
                    new_list.append(i)
        return new_list

    # 列表 中位数
    @staticmethod
    def list_median(data):
        data = sorted(data)
        size = len(data)
        if size % 2 == 0:  # 判断列表长度为偶数
            median = (data[size // 2] + data[size // 2 - 1]) / 2
            data[0] = median
        if size % 2 == 1:  # 判断列表长度为奇数
            median = data[(size - 1) // 2]
            data[0] = median
        return data[0]

    # 文件 获取文件夹下所有文件信息
    @staticmethod
    def os_file_child_info(directory_path):
        all_file_info = []
        file_list = os.listdir(directory_path)

        # 遍历文件列表，获取每个文件的详细信息
        for file_name in file_list:
            file_path = os.path.join(directory_path, file_name)

            # 获取文件信息
            file_info = os.stat(file_path)

            # 打印文件信息（示例，你可以根据需求选择性输出）
            all_file_info.append({
                'name': file_name,
                'size': file_info.st_size,
                'last_up': int(file_info.st_mtime),
                'created': int(file_info.st_ctime),
                'is_directory': os.path.isdir(file_path),
                'is_file': os.path.isfile(file_path),
            })
        return all_file_info

    # dict 多重数据结构提取web链接
    def dict_web_url(self, data):
        links = []

        if isinstance(data, dict):
            for value in data.values():
                links.extend(self.dict_web_url(value))
        elif isinstance(data, list):
            for item in data:
                links.extend(self.dict_web_url(item))
        elif isinstance(data, str):
            # 使用正则表达式查找所有链接
            found_links = re.findall(r'https?://\S+', data)
            links.extend(found_links)

        return links
