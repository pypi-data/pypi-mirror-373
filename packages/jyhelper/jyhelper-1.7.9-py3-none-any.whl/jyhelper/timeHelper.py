#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time : 2020/12/16 16:07
# @Author : JY

import datetime
import time

"""
以下函数默认服务器时区为东八区（北京时间）
"""


class timeHelper:
    # 获取时间
    @staticmethod
    def getDate(timestamp=0, format_str='%Y-%m-%d %H:%M:%S'):
        if timestamp == 0:
            return datetime.datetime.now().strftime(format_str)  # 现在
        else:
            return datetime.datetime.fromtimestamp(timestamp).strftime(format_str)

    # 获取日期
    @staticmethod
    def getDay(timestamp=0, format_str='%Y-%m-%d'):
        if timestamp == 0:
            return datetime.datetime.now().strftime(format_str)  # 现在
        else:
            return datetime.datetime.fromtimestamp(timestamp).strftime(format_str)

    # 把时间戳转为UTC的日期
    @staticmethod
    def getDayUTC(timestamp, format_str='%Y-%m-%d'):
        return datetime.datetime.fromtimestamp(timestamp - 8 * 3600).strftime(format_str)

    # 返回今天的日期
    @staticmethod
    def today(xcjt=0):
        return datetime.datetime.fromtimestamp(int(time.time()) + 86400 * xcjt).strftime('%Y-%m-%d')

    # 获取时间戳
    @staticmethod
    def getTime(date='', format_str=None):
        if date == '':
            return int(time.time())
        else:
            if format_str is None:
                if date.__len__() == 10:
                    format_str = '%Y-%m-%d'
                else:
                    format_str = '%Y-%m-%d %H:%M:%S'
            tm = time.strptime(date, format_str)
            return int(time.mktime(tm))

    @staticmethod
    def xcjt(small, big):
        big = big[:10] if big.__len__() != 10 else big
        small = small[:10] if small.__len__() != 10 else small
        format_str = '%Y-%m-%d'
        return int((int(time.mktime(time.strptime(big, format_str))) - int(
            time.mktime(time.strptime(small, format_str)))) / 86400 + 1)

    @staticmethod  # 用时间戳计算相差几天 自然天
    def xcjtStamp(small, big, timeZone=8):
        pianYi = (8 - timeZone) * 3600
        xcjt = (timeHelper.getTime(timeHelper.getDay(big - pianYi)) - timeHelper.getTime(
            timeHelper.getDay(small - pianYi))) / 86400 + 1
        return int(xcjt)

    @staticmethod
    def getMonthFirstDay(day=None):
        day = day if day is not None else timeHelper.getDay()
        return day[:8] + '01'

    @staticmethod
    def getMonthEndDay(day=None):
        day = day if day is not None else timeHelper.getDay()
        year, month, tmp = day.split('-')
        if month == '12':
            nextMonth = 1
            year = str(int(year) + 1)
        else:
            nextMonth = int(month) + 1
        nextMonth = str(nextMonth) if nextMonth >= 10 else '0' + str(nextMonth)
        nextMonth = year + '-' + nextMonth + '-01'
        return timeHelper.getDay(timeHelper.getTime(nextMonth) - 86400)

    @staticmethod
    def getWeekFirstDay(day=None):
        weekday = datetime.datetime.strptime(day, "%Y-%m-%d").weekday()
        firstDay = timeHelper.getDay(timeHelper.getTime(day) - 86400 * weekday)
        return firstDay

    @staticmethod
    def getWeekEndDay(day=None):
        return timeHelper.getDay(timeHelper.getTime(timeHelper.getWeekFirstDay(day)) + 86400 * 6)

    # 星期几
    @staticmethod
    def getWeekJi(day=None):
        return datetime.datetime.strptime(day, "%Y-%m-%d").weekday() + 1

    @staticmethod
    def addDay(event_day=None, add_day=1):
        if event_day is None:
            event_day = timeHelper.getDay()
        return timeHelper.getDay(timeHelper.getTime(event_day) + 86400 * add_day)

    # 转换时区
    @staticmethod
    def transDate(date, from_tz, to_tz):
        if not isinstance(from_tz, int) or not isinstance(to_tz, int):
            raise RuntimeError('from_tz 或者 to_tz 错误')
        stamp = timeHelper.getTime(date)
        stamp = stamp + (to_tz - from_tz) * 3600
        if date.__len__() == 10:
            return timeHelper.getDay(stamp)
        else:
            return timeHelper.getDate(stamp)

    @staticmethod
    def checkIsDay(day):
        if day.__len__() != 10:
            return False
        try:
            time.strptime(day, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def checkIsDate(date):
        if date.__len__() != 19:
            return False
        try:
            time.strptime(date, '%Y-%m-%d %H:%M:%S')
            return True
        except ValueError:
            return False

    @staticmethod
    def sleep(seconds):
        time.sleep(seconds)

    # 得到一个日期列表(默认包含首尾)
    @staticmethod
    def getDayList(startDate, endDate, stepLen=86400,includeTail=True):
        if timeHelper.checkIsDay(startDate) and timeHelper.checkIsDay(endDate):
            formatStr = '%Y-%m-%d'
        elif timeHelper.checkIsDate(startDate) and timeHelper.checkIsDate(endDate):
            formatStr = '%Y-%m-%d %H:%M:%S'
        else:
            return []
        timeStart = timeHelper.getTime(startDate)
        timeEnd = timeHelper.getTime(endDate)
        res = []
        for i in range(timeStart,timeEnd+int(includeTail),stepLen):
            res.append(timeHelper.getDay(i,formatStr))
        return res


if __name__ == '__main__':
    # day = '2023-11-12'
    # print(timeHelper.getWeekFirstDay(day=day), timeHelper.getWeekEndDay(day=day))
    # timeHelper.sleep(10)
    # print(timeHelper.getWeekJi(day))

    # for row in timeHelper.getDayList('2024-01-01 00:00:00','2024-01-02 00:00:00',includeTail=False,stepLen=3600):
    #     print(row)

    print(timeHelper.addDay())