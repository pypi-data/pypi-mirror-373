# -*- coding:utf-8 -*-
from functools import wraps
from itertools import zip_longest
from pyhive import hive
import pandas  as pd
import warnings
warnings.filterwarnings("ignore")

class Retry(object):
    def __init__(self, retry=3):
        self.retry = retry

    def __call__(self, func):
        @wraps(func)
        def wrapped_func(conn, query_sql):
            retry_count = 0
            while retry_count < self.retry:
                try:
                    return func(conn, query_sql)
                except Exception as e:
                    print(str(e))
                    conn.init_connection()
                    retry_count += 1
                    continue
            raise Exception("多次重试仍然失败，sql语句为: " + query_sql)

        return wrapped_func


class HiveClient(object):

    def __init__(self, host, port, username, password, auth='CUSTOM'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.auth = auth
        self.init_connection()

    def init_connection(self):
        self.conn = hive.Connection(host=self.host, port=self.port, username=self.username,password=self.password, auth=self.auth)

    @Retry()
    def query(self, query_sql):
        datas = []
        curosr = self.conn.cursor()
        curosr.execute(query_sql)
        clumns = curosr.description
        for result in curosr.fetchall():
            item = {}
            for key, value in zip_longest(clumns, result):
                item[key[0]] = value
            datas.append(item)

        curosr.close()
        #data=pd.DataFrame(datas)
        return datas

    @Retry()
    def ddl(self, query_sql):
        curosr = self.conn.cursor()
        curosr.execute(query_sql)
        curosr.close()

    @Retry()
    def ddls(self, query_sql):
        sql_gs=query_sql.split(';')
        for  i  in range(0,len(sql_gs)):
            #print(sql_gs[i])
            curosr = self.conn.cursor()
            curosr.execute(sql_gs[i])
            curosr.close()

    @Retry()
    def pdre(self, query_sql):
        #curosr = self.conn.cursor()
        df = pd.read_sql(query_sql, self.conn)
        return df

    @Retry()
    def pdres(self, query_sql):
        sql_gs=query_sql.split(';')
        les=len(sql_gs)
        for  i  in range(0,les-1):
                  curosr = self.conn.cursor()
                  curosr.execute(sql_gs[i])
                  curosr.close()        
        df = pd.read_sql(sql_gs[les-1], self.conn)
        return df