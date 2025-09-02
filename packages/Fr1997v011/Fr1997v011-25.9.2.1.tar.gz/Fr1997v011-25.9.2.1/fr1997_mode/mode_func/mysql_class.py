import time
import pymysql
from .cache_class import *  # 缓存库


class MysqlDb:

    @staticmethod
    def db_mysql(path=None, ret_config=None):
        config_mysql = config_dict["mysql"]
        if path == 1:
            db_cfg = "mysql_jike_in"
        elif path == 2:
            db_cfg = "mysql_jike_test"
        elif path == 3:
            db_cfg = "mysql_loc"
        elif path == 5:
            db_cfg = "mysql_my_tx"
        else:
            db_cfg = "mysql_jike_out"

        # 寻找特定的数据库配置
        if path in config_mysql:
            db_cfg = path

        mysql_host = config_mysql[db_cfg]['host']
        mysql_user = config_mysql[db_cfg]['user']
        mysql_passwd = config_mysql[db_cfg]['pwd']
        mysql_db = config_mysql[db_cfg]['db']
        mysql_port = int(config_mysql[db_cfg]['port'])
        if ret_config:
            return {'host': mysql_host, 'user': mysql_user, 'passwd': mysql_passwd, 'db': mysql_db, 'port': mysql_port}
        conn = pymysql.connect(host=mysql_host, user=mysql_user, passwd=mysql_passwd, db=mysql_db, port=int(mysql_port))
        return conn

    # db Mysql 操作 20230719新
    def mysql_db(self, method, table, conn_tp=None, **kwargs):
        """
        method
            - s -- select
            - up --date_more_byid
            - ins -- insert
            - iss -- insert_all
            - tc -- create_table 创建表
            - te -- table_exist 查询 表是否存在
            - sql -- 执行sql -> commit()
        :param method: 方法
        :param table: 表明
        :param conn_tp: 链接
        :return:
        """
        if conn_tp is None:
            conn_tp = 0

        sql = kwargs.get('sql', '')
        save_data = kwargs.get('save_data')

        # 其他链接
        conn_other = kwargs.get('conn_other')
        if conn_other:
            conn = conn_other
        else:
            # mysql链接 【自动】0=内网 1=外网
            conn = self.db_mysql(path=conn_tp)

        # 通用sql 查看表是否存在
        sql_table_exist = f"SELECT * FROM information_schema.tables WHERE table_name = '{table}'"

        # 数据库操作
        try:
            with conn.cursor() as cursor:
                if method == 'insert' or method == 'ins':
                    save_data = kwargs['save_data']
                    columns = ', '.join(save_data.keys())
                    placeholders = ', '.join(['%s'] * len(save_data))
                    params = tuple(save_data.values())
                    sql = f"INSERT ignore INTO {table} ({columns}) VALUES ({placeholders})"
                    cursor.execute(sql, params)
                    conn.commit()
                elif method == 'insert_all' or method == 'iss':
                    fields = list(save_data[0].keys())
                    placeholders = ', '.join(f'%({i})s' for i in fields)
                    fields_str = ','.join(fields)
                    sql_inserts = f"INSERT ignore INTO {table} ({fields_str}) values({placeholders})"
                    n = cursor.executemany(sql_inserts, save_data)
                    conn.commit()
                    return n
                elif method == 'insert_creat_all' or method == 'isc':
                    pass
                    # # 根据索引插入或更新 没有索引最后 没有更新默认
                    # key = kwargs.get('key')
                    # if key in None:
                    #
                    # update_key = []
                    #
                    # fields = list(save_data[0].keys())
                    # placeholders = ', '.join(f'%({i})s' for i in fields)
                    # fields_str = ','.join(fields)
                    # sql_inserts = f"INSERT INTO {table} ({fields_str}) values({placeholders}) on DUPLICATE {key} update"
                    # return sql_inserts
                    # # n = cursor.executemany(sql_inserts, save_data)
                    # # conn.commit()
                    # # return n
                elif method == 'table_exist' or method == 'te':
                    # 查询 表是否存在
                    return cursor.execute(sql_table_exist)
                elif method == 'create_table' or method == 'tc':  # 创建一个表
                    table_exist = cursor.execute(sql_table_exist)
                    if table_exist:
                        del_and_create = kwargs.get('del_and_create', 0)
                        if del_and_create:
                            print('表已经存在 删除并创建')
                            self.mysql_db(method='dt', table=table, conn_tp=conn_tp)
                        else:
                            print('表已经存在')
                            return '表已经存在'
                    """
                        TINYINT = [-128,127]
                        SMALLINT = [-32768,32767]
                    """
                    fields_sql = []
                    field_cfg = kwargs['field_cfg']
                    for f in field_cfg['fields']:
                        name = f[0]
                        field_type = f[1]
                        length = f[2]
                        default = f[3]
                        comment = f[4]

                        if field_type == 'VARCHAR':
                            fields_sql.append(f"{name} {field_type}({length}) DEFAULT '{default}' COMMENT '{comment}'")
                        elif field_type == 'INT' or field_type == 'TINYINT' or field_type == 'SMALLINT':
                            fields_sql.append(f"{name} {field_type}({length}) DEFAULT {default} COMMENT '{comment}'")
                        elif field_type == 'TEXT':  # 新增条件处理 TEXT 类型
                            fields_sql.append(f"{name} {field_type} DEFAULT '{default}' COMMENT '{comment}'")
                        elif field_type == 'JSON':
                            fields_sql.append(f"{name} {field_type} DEFAULT NULL COMMENT '{comment}'")
                    if fields_sql:
                        this_time = time.strftime("%Y-%m-%d %X", time.localtime(int(time.time())))
                        table_notes = f'{this_time} 【高阳】创建此表'  # 表备注
                        sql_create_base = f"CREATE TABLE {table} ({field_cfg['id']} INT AUTO_INCREMENT PRIMARY KEY,{','.join(fields_sql)}) COMMENT='{table_notes}'"
                        cursor.execute(sql_create_base)

                        # 增加唯一索引
                        field_index = field_cfg['field_index']
                        if field_index:
                            if len(field_index) == 1:
                                sql_index = f"ALTER TABLE {table} ADD UNIQUE INDEX field_index ({field_index[0]});"
                            else:
                                sql_index = f"ALTER TABLE {table} ADD CONSTRAINT field_index UNIQUE ({','.join(field_index)});"
                            cursor.execute(sql_index)
                        print(f"创建{table}成功")
                        return f"创建{table}成功"
                elif method == 'field_add':
                    # 查看一个表所有字段
                    sql_columns = f"SHOW COLUMNS FROM {table};"
                    cursor.execute(sql_columns)
                    columns = cursor.fetchall()
                    columns_list = [i[0] for i in columns]
                    field_change = kwargs.get('field_change')  # ['user', 'VARCHAR', 50, '', '用户名称']
                    field_name = field_change[0]
                    if field_name in columns_list:
                        print(f"{field_name}字段已经存在")
                        return

                    # 增加字段
                    field_type = field_change[1]
                    length = field_change[2]
                    default = field_change[3]
                    comment = field_change[4]
                    if field_type == 'VARCHAR':
                        query = f"ALTER TABLE {table} ADD COLUMN {field_name} {field_type}({length}) COMMENT '{comment}'"
                    elif field_type == 'INT' or field_type == 'TINYINT' or field_type == 'SMALLINT':
                        query = f"ALTER TABLE {table} ADD COLUMN {field_name} {field_type}({length}) DEFAULT {default} COMMENT '{comment}'"
                    elif field_type == 'TEXT':  # 新增条件处理 TEXT 类型
                        query = f"ALTER TABLE {table} ADD COLUMN {field_name} {field_type} COMMENT '{comment}'"
                    elif field_type == 'JSON':
                        query = f"ALTER TABLE {table} ADD COLUMN {field_name} {field_type} DEFAULT NULL COMMENT '{comment}'"
                    cursor.execute(query)
                    print(f"字段{field_name}增加成功")
                elif method == 'field_del':
                    sql_columns = f"SHOW COLUMNS FROM {table};"
                    cursor.execute(sql_columns)
                    columns = cursor.fetchall()
                    columns_list = [i[0] for i in columns]
                    field_del = kwargs.get('field_del')  # ['user', 'VARCHAR', 50, '', '用户名称']
                    if field_del not in columns_list:
                        print(f"{field_del}字段不存在")
                        return

                    query = f"ALTER TABLE {table} DROP COLUMN {field_del}"
                    cursor.execute(query)
                    print(f"字段{field_del}删除成功")
                elif method == 'field_up':
                    sql_columns = f"SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}'"

                    cursor.execute(sql_columns)
                    columns = cursor.fetchall()
                    field_old = kwargs.get('field_old')
                    field_dict = {i[3]: i for i in columns}
                    if field_old not in field_dict:
                        print(f"{field_old} 老字段不存在")
                        return

                    change_name = kwargs.get('change_name')
                    if change_name is None:
                        change_name = field_old

                    change_type = kwargs.get('change_type')
                    if change_type is None:
                        change_type = field_dict[field_old][15]

                    change_comment = kwargs.get('change_comment')
                    if change_comment is None:
                        change_comment = field_dict[field_old][-3]

                    query = f"ALTER TABLE {table} CHANGE COLUMN {field_old} {change_name} {change_type} COMMENT '{change_comment}'"
                    cursor.execute(query)
                    print(f"字段{field_old}修改名字成功")
                elif method == 'sql':
                    cursor.execute(sql)
                    conn.commit()
                elif method == 'update_more_byid' or method == 'up':  # 更新 根据id进行批量更新
                    if save_data:
                        fields = list(save_data[0].keys())
                        update_fields = [f'{i}=%s' for i in fields[:-1]]
                        sql_update = f"UPDATE {table} SET {','.join(update_fields)} WHERE {fields[-1]} = %s"
                        tuple_data_list = [tuple(data.values()) for data in save_data]
                        cursor.executemany(sql_update, tuple_data_list)
                        conn.commit()
                elif method == 'select' or method == 's':
                    cursor.execute(sql)
                    return cursor.fetchall()
                elif method == 'del_table' or method == 'dt':
                    sql_del = f'DROP TABLE {table}'
                    cursor.execute(sql_del)
                    conn.commit()
                elif method == 'in':
                    field = kwargs.get('field')
                    by_id = kwargs.get('by_id')
                    id_list = kwargs.get('id_list')
                    if not id_list or not field or not by_id:
                        return ()
                    format_strings = ','.join(['%s'] * len(id_list))
                    sql_in = f"SELECT {field} FROM {table} WHERE {by_id} IN ({format_strings})"
                    cursor.execute(sql_in, id_list)
                    return cursor.fetchall()
                else:
                    cursor.execute(sql)
                    return cursor.fetchall()
        except Exception as e:
            print(f"数据库链接错误:{e}")
        finally:
            conn.close()


class MysqlJike:
    """
        conn_tp 0外网(自动) 1内网(自动) 2测试 3本地 5腾讯
        mysql 方法
            常用：select，insert，update，delete，create，commit
            其他：alter, drop, grant, revoke, start, transaction, rollback, show, describe, use, explain, lock, unlock
    """

    def __init__(self, **kwargs):
        self.conn_tp = kwargs.get('conn_tp', 0)

    def select(self, **kwargs):
        print(kwargs)
        sql = "SELECT id,hightitle FROM `cd_shool_list` WHERE id > 0 LIMIT 10"

    def do_select(self, method, sql):
        conn = MysqlDb().db_mysql(path=self.conn_tp)
        try:
            with conn.cursor() as cursor:
                if method == 'select':
                    cursor.execute(sql)
                    return cursor.fetchall()
                else:
                    cursor.execute(sql)
                    return cursor.fetchall()
        except Exception as e:
            print(f"数据库链接错误:{e}")
        finally:
            conn.close()
