#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time : 2025/05/19 14:38 
# @Author : JY
"""
MySQL操作
"""
import pymysql
from pymysql.cursors import DictCursor
import datetime
import time


class mysql:
    def __init__(self, config=None, host=None, user=None, password=None, database=None, port=3306, charset='utf8mb4'):
        """初始化数据库连接参数"""
        if config is None:
            config = {}
        self.config = {
            'host': config['host'] if config.get('host', False) else host,
            'user': config['user'] if config.get('user', False) else user,
            'password': config['password'] if config.get('password', False) else password,
            'database': config['db'] if config.get('db', False) else database,
            'port': config['port'] if config.get('port', False) else port,
            'charset': config['charset'] if config.get('charset', False) else charset,
            'cursorclass': config['cursor'] if config.get('cursor', False) else DictCursor,
            'autocommit': False  # 手动控制事务
        }

    def _get_connection(self):
        """获取数据库连接"""
        # return pymysql.connect(**self.config) # python=3.8.0会出问题，改成下面的
        conn = pymysql.connect(**self.config)

        # 包装连接对象，确保实现上下文管理器
        class ConnectionWrapper:
            def __init__(self, conn):
                self.conn = conn

            def __enter__(self):
                return self.conn

            def __exit__(self, exc_type, exc_val, exc_tb):
                try:
                    self.conn.close()
                except Exception as e:
                    print(f"Warning: Failed to close connection: {e}")
                return False  # 不抑制异常，继续向上传播

        return ConnectionWrapper(conn)

    def select(self, sql, params=None, printInfo=False):
        """执行查询语句（SELECT），返回多行结果"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                if printInfo:
                    start = time.time()
                    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '开始', sql)
                cursor.execute(sql, params)
                result = cursor.fetchall()
                if printInfo:
                    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '结束',
                          '耗时: %s秒' % round((time.time() - start), 2), sql)
                return result if result else []

    def select_one(self, sql, params=None, printInfo=False):
        """执行查询语句，返回单行结果"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                if printInfo:
                    start = time.time()
                    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '开始', sql)
                cursor.execute(sql, params)
                result = cursor.fetchone()
                if printInfo:
                    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '结束',
                          '耗时: %s秒' % round((time.time() - start), 2), sql)
                return result if result else {}

    def execute_sql(self, sql, params=None, printInfo=False):
        """执行更新操作（INSERT/UPDATE/DELETE）"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    if printInfo:
                        start = time.time()
                        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '开始', sql)
                    cursor.execute(sql, params)
                    conn.commit()
                    if printInfo:
                        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '结束',
                              '耗时: %s秒' % round((time.time() - start), 2), '影响: %s条' % cursor.rowcount, sql)
                    return cursor.rowcount
        except pymysql.Error as e:
            # 发生异常时回滚
            conn.rollback()
            raise e

    def update(self, table, setDict, whereStr, returnSQL=False, printInfo=False):
        sql = f"""UPDATE {table} SET """
        for key, value in setDict.items():
            if isinstance(value, str):
                if '"' in value:
                    value = value.replace('"', '\\"')
                value = '"' + value + '"'
            if value is None:
                value = 'NULL'
            sql += f"""{key}={value},"""
        sql = sql[:-1]
        sql += f""" WHERE {whereStr}"""
        if returnSQL:
            return sql
        return self.execute_sql(sql,None,printInfo)

    def delete(self, table, whereStr, limit=None, returnSQL=False, printInfo=False):
        sql = f"DELETE FROM {table} WHERE {whereStr}"
        if limit is not None:
            if isinstance(limit, int):
                sql += f" LIMIT {limit}"
            else:
                raise "limit参数需要为整数"
        if returnSQL:
            return sql
        return self.execute_sql(sql,None,printInfo)

    # INSERT IGNORE 的核心作用是静默处理违反约束的行，但它的影响范围不仅限于唯一索引冲突，还包括数据类型、空值、外键等约束
    def insert(self, table, data, returnSQL=False, printInfo=False, ignoreMode=False):
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            return 0
        if data.__len__() == 0:
            return 0
        # 判断有几个字段
        field_len = data[0].__len__()
        if field_len == 0:
            return 0
        filed_str = ''
        field_list = []
        for filed in data[0]:
            filed_str += '`' + filed + '`,'
            field_list.append(filed)
        filed_str = filed_str[:-1]
        ignoreMode = " IGNORE " if ignoreMode else ""
        sql = """INSERT %s INTO %s(%s) VALUES""" % (ignoreMode, table, filed_str)
        for item in data:
            if item.__len__() != field_len:
                raise RuntimeError('insert方法批量插入数据错误，插入数据长度不统一' + str(item))
            sql += """("""
            for filed in field_list:
                value = item[filed]
                if isinstance(value, str):
                    if '"' in value:
                        value = value.replace('"', '\\"')
                    value = '"' + value + '"'
                if value is None:
                    value = 'NULL'
                sql += f"""{value},"""
            sql = sql[:-1]
            sql += """),"""
        sql = sql[:-1]
        if returnSQL:
            return sql
        return self.execute_sql(sql,None,printInfo)

    def execute_manySQLs(self, sqls, printInfo=False):
        """执行事务（多个SQL操作）"""
        if not isinstance(sqls,list):
            sqls = [sqls]
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    res_rowcount = []
                    for sql in sqls:
                        if printInfo:
                            start = time.time()
                            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '开始', sql)
                        cursor.execute(sql, None)
                        res_rowcount.append(cursor.rowcount)
                        if printInfo:
                            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '结束', '耗时: %s秒' % round((time.time() - start),2), '影响: %s条' % cursor.rowcount, sql)
                    conn.commit()
                    return res_rowcount
        except pymysql.Error as e:
            conn.rollback()
            raise e


if __name__ == '__main__':
    db_config = {
        'host': '',
        'port': 3306,
        'user': 'root',
        'password': '',
        'db': 'test'
    }
    dbIns = mysql(db_config)
    res = mysql(db_config).select('select * from payflow limit 10')
    # res = dbIns.execute_sql('update payflow set iLevel=9 where iEventTime=1717776886',printInfo=True)
    # res = dbIns.update(table='payflow',setDict={'iLevel':None,'iVipLevel':88,'vName':'xxx','vLang':'1"2\'1"2',},whereStr="iEventTime=1720602342")
    # res = dbIns.delete('payflow','iEventTime=1720601151',10,printInfo=True)
    # res = dbIns.insert('payflow',[{'iRoleID':1234,'vName':'1"2中文'},{'iRoleID':1236,'vName':None}],printInfo=True)
    # res = dbIns.execute_manySQLs([
    #     "SET @time := 1720602342;",
    #     "update payflow set vName='a1' WHERE iEventTime = @time;",
    #     "update payflow set vName='a2' WHERE iEventTime = @time;",
    #     "update payflow set vName='asd' WHERE iEventTime = 1720597390;",
    #     "update payflow set vName='a3' WHERE iEventTime = @time;",
    #     "update payflow set vName='aaas1' WHERE vUID='990791'",
    #     "DELETE FROM payflow WHERE vUID='990791' LIMIT 1",
    #     "update payflow set vName='a4' WHERE iEventTime = @time;",
    # ],printInfo=True)
    # print(res)