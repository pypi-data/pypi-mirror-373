#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import pymysql
import datetime


class db:
    __host = None
    __port = None
    __user = None
    __password = None
    _db = None
    __charset = 'utf8'
    __read_timeout = 120
    __cursor = pymysql.cursors.DictCursor
    __conn = None
    __table = None
    __where = None
    __field = None
    __limit = None
    __group = None
    __having = None
    __order = None
    __getsql = None

    def __init__(self, config=None, host=None, port=None, user=None, password=None, db=None, charset=None,
                 read_timeout=None, cursor=__cursor):
        if config is None:
            config = {}
        if bool(config):
            host = config.get('host')
            port = config.get('port')
            user = config.get('user')
            password = config.get('password')
            db = config.get('db')
            charset = config.get('charset', charset)
            read_timeout = config.get('read_timeout', read_timeout)
            cursor = config.get('cursor', cursor)
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password
        self.__db = db
        self.__charset = charset if charset else self.__charset
        self.__read_timeout = read_timeout if read_timeout else self.__read_timeout
        self.__cursor = cursor if cursor else self.__cursor

    def setReadTimeout(self, seconds):
        self.__read_timeout = seconds
        return self

    # 返回一个迭代器一条一条取数据
    def setSSCursor(self):
        self.__cursor = pymysql.cursors.SSCursor
        return self

    # 返回一个list 所有数据全部返回
    def setDictCursor(self):
        self.__cursor = pymysql.cursors.DictCursor
        return self

    def setDatabase(self, database):
        self.__db = database
        return self

    def query(self, sql):
        if bool(self.__getsql):
            return sql
        if self.__conn is None:
            self.__connect()
        if isinstance(self.__conn.cursor(), pymysql.cursors.DictCursor):
            return self.__execute_dict(sql)
        elif isinstance(self.__conn.cursor(), pymysql.cursors.SSCursor):
            return self.__execute_ss(sql)

    def getsql(self, status=True):
        if bool(status):
            self.__getsql = status
        else:
            self.__getsql = None
        return self

    def table(self, table):
        self.__table = table
        return self

    # build where条件
    def where(self, where=None):
        if where is None:
            self.__where = None
        if isinstance(where, str):
            self.__where = where
        if isinstance(where, dict):
            if where.__len__() == 0:
                return self
            self.__where = ''
            for key, val in where.items():
                # 字符串 整数
                if isinstance(val, str) or isinstance(val, int):
                    self.__where += '`' + key + '`=' + self.buildStr(val) + ' AND '
                # list
                elif isinstance(val, list):
                    if val.__len__() == 0:
                        raise RuntimeError('where条件key %s,参数错误,空list' % key)
                    else:
                        if isinstance(val[0], str):
                            val0 = val[0].upper()
                            if val0 == 'IN' or val0 == 'NOT IN':
                                instr = '('
                                if isinstance(val[1], str):
                                    val.pop(0)
                                    for v in val:
                                        instr += self.buildStr(v) + ','
                                elif isinstance(val[1], list):
                                    if val[1].__len__() == 0:
                                        raise RuntimeError('where条件key %s,参数错误' % key)
                                    for v in val[1]:
                                        instr += self.buildStr(v) + ','
                                else:
                                    raise RuntimeError('where条件key %s,参数错误' % key)
                                instr = instr[:-1]
                                instr += ') AND '
                                self.__where += '`' + key + '` ' + val0 + instr
                            if val0 == 'BETWEEN' or val0 == 'NOT BETWEEN':
                                if val.__len__() == 3:
                                    self.__where += '`' + key + '` ' + val0 + ' ' + self.buildStr(
                                        val[1]) + ' AND ' + self.buildStr(val[2]) + ' AND '
                                else:
                                    raise RuntimeError('where条件key %s,参数错误' % key)
                            if val0 == '>=' or val0 == '<=' or val0 == '>' or val0 == '<' or val0 == '!=':
                                self.__where += '`' + key + '`' + val0 + self.buildStr(val[1]) + ' AND '
                                if val.__len__() == 4:
                                    self.__where += '`' + key + '`' + val[2] + self.buildStr(val[3]) + ' AND '
                        else:
                            raise RuntimeError('where条件key %s,参数错误' % key)
                else:
                    raise RuntimeError('where条件,参数错误')
            self.__where = self.__where[:-5]
        return self

    def field(self, field=None):
        if field is None or isinstance(field, str):
            self.__field = field
        return self

    def limit(self, limit=None):
        if limit is None or isinstance(limit, str):
            self.__limit = limit
        if isinstance(limit, int):
            self.__limit = str(limit)
        return self

    def group(self, group=None):
        if group is None or isinstance(group, str):
            self.__group = group
        return self

    def having(self, having=None):
        if having is None or isinstance(having, str):
            self.__having = having
        return self

    def order(self, order=None):
        if order is None or isinstance(order, str):
            self.__order = order
        return self

    # 普通查询
    def select(self):
        if self.__field is None:
            self.__field = '*'
        sql = 'SELECT %s FROM `%s`' % (self.__field, self.__table)
        if self.__where is not None:
            sql += ' WHERE ' + self.__where
        if self.__group is not None:
            sql += ' GROUP BY ' + self.__group
        if self.__having is not None:
            sql += ' HAVING ' + self.__having
        if self.__order is not None:
            sql += ' ORDER BY ' + self.__order
        if self.__limit is not None:
            sql += ' LIMIT ' + self.__limit
        data = self.query(sql)
        if data == ():
            data = []
        return data

    # 查询一个
    def find(self):
        self.limit('1')
        data = self.select()
        if isinstance(data, str):
            return data
        if data.__len__() == 1:
            return data[0]
        return {}

    # 得到一条数据的的某个值
    def getValue(self, field):
        self.field(field)
        data = self.find()
        if isinstance(data, str):
            return data
        return data.get(field)

    # 某个字段的一个list
    def getField(self, field):
        self.field(field)
        data = self.select()
        if isinstance(data, str):
            return data
        reda = []
        field = field.split()
        field.reverse()
        field = field[0]
        for item in data:
            reda.append(item[field])
        return reda

    # 返回一个字段 key-value
    def column(self, field, key=None):
        if key is None:
            return self.getField(field)
        self.field(field + ',' + key)
        data = self.select()
        if isinstance(data, str):
            return data
        reda = {}
        for item in data:
            reda[item[key]] = item[field]
        return reda

    # 返回count数量
    def count(self):
        if self.__field is None:
            self.__field = '*'
        self.__field = 'count(%s)' % self.__field
        data = list(self.select()[0].values())[0]
        return data

    # 返回求和的数量
    def sum(self):
        if self.__field is None:
            raise RuntimeError('求和的field必须设置为字符串')
        self.__field = 'sum(%s)' % self.__field
        data = list(self.select()[0].values())[0]
        return data

    # 接收一个字典
    def insert(self, data):
        if self.__table is None:
            raise RuntimeError('插入数据错误，未指定表明')
        if isinstance(data, dict):
            if data.__len__() == 0:
                raise RuntimeError('插入数据错误，数据为空')
            keys = ''
            vals = ''
            for key, val in data.items():
                keys += '`' + key + '`,'
                vals += self.buildStr(val) + ','
            keys = keys[:-1]
            vals = vals[:-1]
            sql = 'INSERT INTO `%s`(%s) VALUES(%s)' % (self.__table, keys, vals)
            return self.query(sql)
        else:
            raise RuntimeError('插入数据错误,只能接收一个字典')

    # 接收一个list，list中的每一个是一个字典
    def insertAll(self, data):
        if self.__table is None:
            raise RuntimeError('插入数据错误，未指定表明')
        if not isinstance(data, list):
            raise RuntimeError('参数错误，接收一个list，list中的每一个是一个字典')
        if data.__len__() == 0:
            raise RuntimeError('参数错误，接收一个list，list不能为空')
        # 判断有几个字段
        field_len = data[0].__len__()
        if field_len == 0:
            raise RuntimeError('参数错误，字段位0')
        filed_str = ''
        field_list = []
        for filed in data[0]:
            filed_str += '`' + filed + '`,'
            field_list.append(filed)
        filed_str = filed_str[:-1]
        sql = 'INSERT INTO `%s`(%s) VALUES' % (self.__table, filed_str)
        for item in data:
            if item.__len__() != field_len:
                raise RuntimeError('批量插入数据错误，插入数据长度不统一' + str(item))
            sql += '('
            for filed in field_list:
                sql += self.buildStr(item[filed]) + ','
            sql = sql[:-1]
            sql += '),'
        sql = sql[:-1]
        return self.query(sql)

    # 接收一个字典 更新
    def update(self, data):
        if self.__table is None:
            raise RuntimeError('更新数据错误，未指定表明')
        if self.__where is None:
            raise RuntimeError('更新数据错误，必须指定where条件')
        if data.__len__() == 0:
            raise RuntimeError('更新数据错误，upda Error')
        set_str = ''
        for item in data:
            set_str += '`' + item + '`=' + self.buildStr(data[item]) + ','
        set_str = set_str[:-1]
        sql = 'UPDATE `%s` SET %s WHERE %s' % (self.__table, set_str, self.__where)
        return self.query(sql)

    # 删除
    def delete(self):
        if self.__table is None:
            raise RuntimeError('更新数据错误，未指定表明')
        if self.__where is None:
            raise RuntimeError('更新数据错误，必须指定where条件')
        sql = 'DELETE FROM %s WHERE %s' % (self.__table, self.__where)
        return self.query(sql)

    # 如果是整数直接返回如果是字符串加上引号
    @staticmethod
    def buildStr(string):
        if isinstance(string, str):
            if '"' in string:
                string = string.replace('"', '\\"')
            return '"' + string + '"'
        elif string is None:
            return "0"
        else:
            return str(string)

    # 执行SQL 根据游标不同选择不用的方法
    def __execute_dict(self, sql, except_time=0):
        try:
            with self.__conn.cursor() as cursor:
                cursor.execute(sql)
                self.__conn.commit()
                data = cursor.fetchall()
                return data
        except Exception as e:
            print(self.getDate(), self.__host, '第%s次执行SQL失败...' % str(except_time + 1), sql, e)
            # common.debug(self.__host+'---- '+sql+' ----'+str(e))
            if except_time == 0:
                except_time = 1
                print(self.getDate(), self.__host, '第%s次执行SQL尝试...' % str(except_time + 1), sql)
                reda = self.__execute_dict(sql, except_time)
                return reda if bool(reda) else []
        finally:
            self.__closeConn()
            self.__clearWhere()

    def __execute_ss(self, sql, except_time=0):
        try:
            with self.__conn.cursor() as cursor:
                cursor.execute(sql)
                for oneItem in cursor:
                    yield oneItem
        except Exception as e:
            print(self.getDate(), self.__host, '第%s次执行SQL失败...' % str(except_time + 1), sql, e)
            # if except_time == 0:
            #     except_time = 1
            #     print(self.getDate(), self.__host, '第%s次执行SQL尝试...' % str(except_time + 1), sql)
            #     reda = self.__execute_ss(sql, except_time)
            #     return reda if bool(reda) else []
        finally:
            self.__closeConn()
            self.__clearWhere()

    # 关闭连接
    def __closeConn(self):
        if self.__conn is not None:
            self.__conn.close()
            self.__conn = None

    # 清空掉where等条件 以便下次调用的时候正常
    def __clearWhere(self):
        self.__table = None
        self.__where = None
        self.__field = None
        self.__limit = None
        self.__group = None
        self.__having = None
        self.__order = None
        self.__getsql = None

    def __connect(self, except_time=0):
        if self.__conn is None:
            try:
                self.__conn = pymysql.connect(host=self.__host, port=self.__port, user=self.__user,
                                              password=self.__password, db=self.__db, charset=self.__charset,
                                              cursorclass=self.__cursor, read_timeout=self.__read_timeout)
            except Exception as e:
                print(self.getDate(), f'{self.__host}:{self.__port}', '第%s次连接数据库失败...' % str(except_time + 1), e)
                if except_time == 0:
                    except_time = 1
                    print(self.getDate(), f'{self.__host}:{self.__port}', '第%s次连接尝试...' % str(except_time + 1))
                    self.__connect(except_time)
            finally:
                pass
        return self

    @staticmethod
    def getDate():
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'db': 'laravel'
    }

    data = db(config).setSSCursor().table('ax_video').where('id=177 or id=178 or id=179').select()
    for row in data:
        print(row)
