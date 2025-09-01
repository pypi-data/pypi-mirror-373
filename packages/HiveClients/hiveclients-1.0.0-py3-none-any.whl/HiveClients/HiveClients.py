# -*- coding:utf-8 -*-
from functools import wraps
from itertools import zip_longest
from impala.dbapi import connect
from impala.util import as_pandas
import time
import warnings

warnings.filterwarnings("ignore")


class Retry(object):
    """重试装饰器（通用适配，支持任意参数方法）"""

    def __init__(self, retry=3):
        self.retry = retry

    def __call__(self, func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            retry_count = 0
            while retry_count < self.retry:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"执行失败（{retry_count + 1}/{self.retry}）：{str(e)}")
                    if hasattr(args[0], 'init_connection'):
                        args[0].init_connection()
                    retry_count += 1
                    time.sleep(1)
            raise Exception(
                f"多次重试仍然失败（共{self.retry}次），SQL语句：{kwargs.get('query_sql', args[1] if len(args) >= 2 else '')[:100]}...")

        return wrapped_func


class HiveClients(object):
    """基于impyla的Hive客户端（新增pdres方法，适配低版本impyla，支持中文）"""

    def __init__(self, host, port, username, password, auth='LDAP', database=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.auth = auth
        self.database = database
        self.conn = None
        self.init_connection()

    def init_connection(self):
        """初始化连接（适配低版本impyla，移除configuration参数）"""
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                print(f"关闭旧连接失败：{str(e)}")

        self.conn = connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            auth_mechanism=self.auth,
            database=self.database,
            timeout=30
        )

    @Retry()
    def query(self, query_sql):
        """执行查询，返回字典列表（处理中文解码）"""
        datas = []
        with self.conn.cursor() as cursor:
            cursor.execute(query_sql)
            columns = cursor.description
            for result in cursor.fetchall():
                item = {}
                for key, value in zip_longest(columns, result):
                    # 中文编码处理：确保字符串以UTF-8解码
                    if isinstance(value, str):
                        value = value.encode('utf-8', errors='ignore').decode('utf-8')
                    item[key[0]] = value
                datas.append(item)
        return datas

    @Retry()
    def ddl(self, query_sql):
        """执行单条DDL语句（打印执行日志）"""
        with self.conn.cursor() as cursor:
            cursor.execute(query_sql)
        print(f"DDL 执行成功：{query_sql[:50]}...")

    @Retry()
    def ddls(self, query_sql):
        """执行多条DDL语句（过滤空语句，避免无效执行）"""
        sql_list = [sql.strip() for sql in query_sql.split(';') if sql.strip()]  # 过滤空字符串
        with self.conn.cursor() as cursor:
            for sql in sql_list:
                cursor.execute(sql)
                print(f"批量 DDL 执行成功：{sql[:50]}...")

    @Retry()
    def pdre(self, query_sql):
        """执行单条查询，返回DataFrame（处理中文编码）"""
        with self.conn.cursor() as cursor:
            cursor.execute(query_sql)
            df = as_pandas(cursor)

        # 列名小写+中文处理
        df.columns = [col.lower() for col in df.columns]
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(
                lambda x: x.encode('utf-8', errors='ignore').decode('utf-8') if isinstance(x, str) else x)
        return df

    @Retry()
    def pdres(self, query_sql):
        """新增方法：先执行前N-1条DDL语句，最后1条语句作为查询并返回DataFrame"""
        # 1. 拆分SQL语句（按分号分割，过滤空语句）
        sql_list = [sql.strip() for sql in query_sql.split(';') if sql.strip()]
        if len(sql_list) < 1:
            raise ValueError("SQL语句不能为空")

        # 2. 执行前N-1条DDL（若只有1条，则直接执行查询）
        ddl_sqls = sql_list[:-1]  # 前N-1条为DDL
        query_sql_final = sql_list[-1]  # 最后1条为查询语句
        print(f"待执行DDL数量：{len(ddl_sqls)}，待执行查询：{query_sql_final[:50]}...")

        with self.conn.cursor() as cursor:
            # 执行所有DDL
            for ddl_sql in ddl_sqls:
                cursor.execute(ddl_sql)
                print(f"pdres 执行DDL成功：{ddl_sql[:50]}...")

            # 执行最后1条查询，返回DataFrame
            cursor.execute(query_sql_final)
            df = as_pandas(cursor)

        # 3. 处理DataFrame（列名小写+中文编码）
        df.columns = [col.lower() for col in df.columns]
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(
                lambda x: x.encode('utf-8', errors='ignore').decode('utf-8') if isinstance(x, str) else x)

        print(f"pdres 执行完成：查询返回 {len(df)} 行数据")
        return df