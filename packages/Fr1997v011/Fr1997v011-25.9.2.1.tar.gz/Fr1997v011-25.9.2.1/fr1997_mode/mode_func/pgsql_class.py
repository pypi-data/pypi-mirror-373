import time
import psycopg2
from psycopg2 import pool
from .cache_class import *  # 复用您的缓存系统


class PgsqlDb:
    _pool = None

    @staticmethod
    def db_pgsql(path=None, ret_config=None):
        config_pgsql = config_dict["pgsql"]  # 从缓存获取配置
        if path == 1:
            db_cfg = "pgsql_in"
        elif path == 2:
            db_cfg = "pgsql_test"
        elif path == 3:
            db_cfg = "pgsql_loc"
        else:
            db_cfg = "pgsql_out"

        # 寻找特定的数据库配置
        if path in config_pgsql:
            db_cfg = path

        pgsql_host = config_pgsql[db_cfg]['host']
        pgsql_user = config_pgsql[db_cfg]['user']
        pgsql_passwd = config_pgsql[db_cfg]['pwd']
        pgsql_db = config_pgsql[db_cfg]['db']
        pgsql_port = int(config_pgsql[db_cfg]['port'])

        if ret_config:
            return {
                'host': pgsql_host,
                'user': pgsql_user,
                'password': pgsql_passwd,
                'database': pgsql_db,
                'port': pgsql_port
            }

        # 使用连接池
        if PgsqlDb._pool is None:
            PgsqlDb._pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=pgsql_host,
                user=pgsql_user,
                password=pgsql_passwd,
                database=pgsql_db,
                port=pgsql_port
            )
        return PgsqlDb._pool.getconn()

    def pgsql_db(self, method, table, conn_tp=None, **kwargs):
        """
        method
            - s -- select
            - up -- update_more_byid
            - ins -- insert
            - iss -- insert_all
            - tc -- create_table
            - te -- table_exist
            - sql -- 执行sql
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
            conn = self.db_pgsql(path=conn_tp)
        # 通用sql 查看表是否存在
        sql_table_exist = f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"
        try:
            with conn.cursor() as cursor:
                if method == 'insert' or method == 'ins':
                    save_data = kwargs['save_data']
                    columns = ', '.join(save_data.keys())
                    placeholders = ', '.join(['%s'] * len(save_data))
                    params = tuple(save_data.values())
                    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                    cursor.execute(sql, params)
                    conn.commit()
                elif method == 'insert_all' or method == 'iss':
                    fields = list(save_data[0].keys())
                    placeholders = ', '.join(f'%({i})s' for i in fields)
                    fields_str = ','.join(fields)
                    sql_inserts = f"INSERT INTO {table} ({fields_str}) values({placeholders})"
                    n = cursor.executemany(sql_inserts, save_data)
                    conn.commit()
                    return n
                elif method == 'create_table' or method == 'tc':
                    table_exist = cursor.execute(sql_table_exist)
                    if table_exist:
                        del_and_create = kwargs.get('del_and_create', 0)
                        if del_and_create:
                            print('表已经存在 删除并创建')
                            self.pgsql_db(method='dt', table=table, conn_tp=conn_tp)
                        else:
                            print('表已经存在')
                            return '表已经存在'
                    fields_sql = []
                    field_cfg = kwargs['field_cfg']
                    # 直接使用 field_cfg['id'] 作为主键定义
                    fields_sql.append(field_cfg['id'])
                    # 处理其他字段
                    for f in field_cfg['fields']:
                        name = f[0]
                        field_type = f[1]
                        length = f[2]
                        default = f[3]
                        comment = f[4]
                        # 修改字符串默认值的处理
                        if field_type == 'TIMESTAMP':
                            fields_sql.append(f"{name} {field_type} WITH TIME ZONE DEFAULT {default}")
                        elif field_type == 'VARCHAR':
                            fields_sql.append(f"{name} {field_type}({length}) DEFAULT '{default}'")
                        elif field_type == 'INT':
                            fields_sql.append(f"{name} INTEGER DEFAULT {default}")
                        elif field_type == 'BIGINT':
                            fields_sql.append(f"{name} BIGINT DEFAULT {default}")
                        elif field_type == 'SMALLINT':
                            fields_sql.append(f"{name} SMALLINT DEFAULT {default}")
                        elif field_type == 'FLOAT':
                            fields_sql.append(f"{name} FLOAT DEFAULT {default}")
                        elif field_type == 'DOUBLE':
                            fields_sql.append(f"{name} DOUBLE PRECISION DEFAULT {default}")
                        elif field_type == 'DECIMAL':
                            fields_sql.append(f"{name} DECIMAL({length}) DEFAULT {default}")
                        elif field_type == 'TEXT':
                            fields_sql.append(f"{name} TEXT DEFAULT '{default}'")
                        elif field_type == 'CHAR':
                            fields_sql.append(f"{name} CHAR({length}) DEFAULT '{default}'")
                        elif field_type == 'BOOLEAN':
                            fields_sql.append(f"{name} BOOLEAN DEFAULT {default}")
                        elif field_type == 'JSON':
                            fields_sql.append(f"{name} JSONB DEFAULT NULL")
                        elif field_type == 'ARRAY':
                            fields_sql.append(f"{name} TEXT[] DEFAULT ARRAY[]::TEXT[]")
                        elif field_type == 'DATE':
                            fields_sql.append(f"{name} DATE DEFAULT {default}")
                        elif field_type == 'TIME':
                            fields_sql.append(f"{name} TIME DEFAULT {default}")
                        elif field_type == 'UUID':
                            fields_sql.append(f"{name} UUID DEFAULT gen_random_uuid()")
                        elif field_type == 'BYTEA':
                            fields_sql.append(f"{name} BYTEA DEFAULT NULL")
                        elif field_type == 'ENUM':
                            # 修改这里，使用单引号
                            fields_sql.append(f"{name} TEXT DEFAULT '{default}'")
                        elif field_type == 'MONEY':
                            fields_sql.append(f"{name} MONEY DEFAULT {default}")
                        elif field_type == 'INET':
                            fields_sql.append(f"{name} INET DEFAULT NULL")
                        elif field_type == 'CIDR':
                            fields_sql.append(f"{name} CIDR DEFAULT NULL")
                        else:
                            fields_sql.append(f"{name} {field_type} DEFAULT {default}")
                    if fields_sql:
                        this_time = time.strftime("%Y-%m-%d %X", time.localtime(int(time.time())))
                        table_notes = f'{this_time} 【高阳】创建此表'
                        # 打印SQL语句以便调试
                        sql_create_base = f"""
                            CREATE TABLE {table} (
                                {','.join(fields_sql)}
                            );
                            COMMENT ON TABLE {table} IS '{table_notes}';
                        """
                        print("创建表SQL:", sql_create_base)  # 添加调试输出
                        cursor.execute(sql_create_base)
                        # 增加唯一索引
                        field_index = field_cfg['field_index']
                        if field_index:
                            index_name = f"idx_{table}_{'_'.join(field_index)}"
                            if len(field_index) == 1:
                                sql_index = f"CREATE UNIQUE INDEX {index_name} ON {table} ({field_index[0]});"
                            else:
                                sql_index = f"CREATE UNIQUE INDEX {index_name} ON {table} ({','.join(field_index)});"
                            print("创建索引SQL:", sql_index)  # 添加调试输出
                            cursor.execute(sql_index)
                        conn.commit()
                        print(f"创建{table}成功")
                        return f"创建{table}成功"
                elif method == 'select' or method == 's':
                    cursor.execute(sql)
                    return cursor.fetchall()
                elif method == 'update_more_byid' or method == 'up':
                    if save_data:
                        fields = list(save_data[0].keys())  # 假设 save_data 至少有一个元素
                        update_fields = [f'{i}=%s' for i in fields[:-1]]
                        # 使用最后一个字段作为 WHERE 条件
                        where_field = fields[-1]
                        sql_update = f"UPDATE {table} SET {','.join(update_fields)} WHERE {where_field} = %s"

                        # 检查 save_data 是单个记录还是多条记录
                        if isinstance(save_data, list):
                            # 批量更新
                            tuple_data_list = [tuple(data.values()) for data in save_data]
                            cursor.executemany(sql_update, tuple_data_list)
                            conn.commit()
                            # 可以返回更新的记录数，如果需要的话
                            # return len(tuple_data_list)
                        else:
                            # 单条更新
                            params = tuple(save_data.values())
                            cursor.execute(sql_update, params)
                            conn.commit()
                    else:
                        print("更新操作需要提供 save_data")
                elif method == 'sql':
                    cursor.execute(sql)
                    conn.commit()

        except Exception as e:
            print(f"数据库链接错误:{e}")
            conn.rollback()
        finally:
            if not conn_other:  # 如果不是外部传入的连接，则归还到连接池
                PgsqlDb._pool.putconn(conn)
