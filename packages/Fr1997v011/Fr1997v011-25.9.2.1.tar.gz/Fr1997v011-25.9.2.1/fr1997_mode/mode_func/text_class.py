import re


# 文本
class TextJike:
    # 清除字符串渣滓
    @staticmethod
    def word_change(xxx):
        """
        适用于mysql
        :param xxx:
        :return:
        """
        if xxx is not None:
            xxx = str(xxx)
            xxx = str(xxx).replace("'", " ")
            xxx = str(xxx).replace('"', ' ')
            xxx = str(xxx).replace('◕', ' ')
            xxx = str(xxx).replace('\\', ' ')
            xxx = str(xxx).replace('\n', ' ')
            xxx = str(xxx).replace('\r', ' ')
            xxx = str(xxx).replace('\t', ' ')
            xxx = str(xxx).replace('\f', ' ')
            xxx = str(xxx).replace('\v', ' ')
        return xxx

    # 字符串修改 --> 只要数字
    @staticmethod
    def only_number(xxx):
        try:
            if xxx:
                return int(re.sub('\D+', '', xxx))
        except:
            pass

    # 字符串修改 --> 全是数字
    @staticmethod
    def is_all_number(input_string):
        try:
            float(input_string)  # 尝试将字符串转换为浮点数
            return True  # 如果成功转换，说明字符串都是数字
        except ValueError:
            return False  # 如果转换失败，说明字符串包含非数字字符

    # 字符串修改 --> 去除数字
    @staticmethod
    def clear_number(xxx):
        try:
            if xxx:
                return int(re.sub('\d+', '', xxx))
        except:
            pass

    # 字符串修改 --> 去除html符号
    @staticmethod
    def clear_html(xxx):
        try:
            if xxx:
                return re.sub(pattern='<.+?>', repl='', string=xxx)
        except:
            pass

    # 字符串100万 --> 1000000
    @staticmethod
    def str_num_to_int(xxx):
        xxx = xxx.replace(' ', '')  # 去除空格
        if '万' in xxx:
            xxx_num = float(xxx[:-1])
            ret_xxx = xxx_num * 10000

        elif '亿' in xxx:
            xxx_num = float(xxx[:-1])
            ret_xxx = xxx_num * 100000000

        else:
            ret_xxx = xxx
        return ret_xxx

    # 分词处理
    @staticmethod
    def word_split_type2(word="拨片"):
        import jieba.posseg as pseg
        # 只会对单个词进行分析 如果存在两个分词以上 返回 NO
        word_types = []
        word_cls = pseg.cut(word)
        for word, flag in word_cls:
            if flag not in word_types:
                word_types.append(flag)
        return word_types

    # 去除标点
    @staticmethod
    def is_symbol_keyword(keyword):
        if re.compile(r'[^\w]').search(keyword):
            return 1
        return 0

    # 去除标点 忽略#号
    @staticmethod
    def is_symbol_keyword2(keyword):
        if re.compile(r'[^\w#]').search(keyword):
            return 1
        return 0
