from jyhelper import timeHelper
from jyhelper.sysHelper import sysHelper
import hashlib
from urllib.parse import quote, unquote
import concurrent.futures
import base64
import random
import re


class common:

    # 打印日志
    @staticmethod
    def debug(*args, path=None):
        path = './debug.log' if path is None else path
        with open(path, 'a', encoding='utf-8') as f:
            f.write("\n---------------" + timeHelper.getDate() + "---------------\n")
            for arg in args:
                f.write(str(arg) + "\n")

    # 带时间输出
    @staticmethod
    def print(*args):
        print(timeHelper.getDate(), '--->', *args)

    def print_in_line(*args, show_time=True, show_ok=None):
        """
        在一行输出
        :param args:
        :param show_time:是否显示时间
        :param show_ok:是否显示成功表示
        :return:
        """
        param = list(args)
        if show_time:
            param = [timeHelper.getDate(), '--->'] + param
        if show_ok:
            if isinstance(show_ok, str):
                param.append(show_ok)
            else:
                param.append(sysHelper.green('[OK]'))

        param[0] = "\r" + param[0]
        print(*param, end='', flush=True)

    @staticmethod
    def print_table(data, table_name=None, data_has_title=True, show_num=True, sort_col_index=None,sort_lambda=None,sort_reverse=False):
        """
        打印输出整齐的表格
        :param data:待打印的二维数组
        :param table_name:表格名字
        :param data_has_title:数据是否包含标题
        :param show_num:是否显示数据总量在标提上
        :param sort_col_index:排序列 0 1 2...
        :param sort_lambda:排序的函数，默认按字符串顺序排列 x表示那一列那个表格的值 sort_lambda=lambda x:len(x)
        :param sort_reverse:排列顺序 默认正序排列
        :return:
        """
        if not bool(data):
            data = [['No Data']]

        def delStrColor(string):
            string = str(string)
            string = string.replace('\033[91m', '')
            string = string.replace('\033[0m', '')
            string = string.replace('\033[92m', '')
            return string

        def getRowWidth(string):
            """
            此函数使用正则表达式计算字符串 s 的长度，其中汉字及中文标点算 1.5 个长度，英文及英文标点算 1 个长度
            """
            string = str(string)
            # 去掉颜色的标识
            string = delStrColor(string)
            # 查找所有汉字和中文标点
            chinese_chars = re.findall(r'[\u4e00-\u9fff\u3000-\u303f]', string)
            # 总长度 = 汉字和中文标点的数量 * 2 + 其余字符的数量
            length = len(chinese_chars) * 1.5 + (len(string) - len(chinese_chars))
            return round(length)

        # 对数据排序
        if sort_col_index is not None and data != [['No Data']]:
            if sort_lambda is None:
                def sort_lambda(x):
                    return x
            if data_has_title:
                data = data[:1] + sorted(data[1:], key=lambda x: sort_lambda(delStrColor(x[sort_col_index])),reverse=sort_reverse)
            else:
                data = sorted(data, key=lambda x: sort_lambda(delStrColor(x[sort_col_index])),reverse=sort_reverse)

        # 得到每一列的宽度
        widths = []
        for i in range(len(data[0])):
            widths.append(0)
        for row in data:
            for index, item in enumerate(row):
                thisWidth = getRowWidth(item)
                if thisWidth > widths[index]:
                    widths[index] = thisWidth
        if table_name is None:
            table_name = ''
        if show_num:
            table_name += " - Num: %s" % (data.__len__() - 1 if data_has_title else data.__len__())
        if bool(table_name):
            titleWidth = sum(widths)
            titleWidth += (len(data[0]) - 1) * 3 + 4
            print('+' + (titleWidth - 2) * '-' + '+')
            titleEmpty = round((titleWidth - 2 - getRowWidth(table_name)) / 2)
            print('|' + titleEmpty * ' ' + table_name + (
                    titleWidth - 2 - getRowWidth(table_name) - titleEmpty) * ' ' + '|')
        # 打印
        i = 0
        dataLen = len(data)
        for row in data:
            printRow = ""
            fenGe = ""
            for index, item in enumerate(row):
                item = str(item)
                printOneItem = (f"\033[1m{item}\033[0m" if i == 0 and data_has_title else item) + (widths[index] - getRowWidth(item)) * ' '
                printOneItem = '| ' + printOneItem + ' '
                printRow += printOneItem
                if i == 0 or i == dataLen - 1:
                    fenGeOneItem = widths[index] * '-'
                    fenGeOneItem = '+ ' + fenGeOneItem + ' '
                    fenGe += fenGeOneItem
            printRow += "|"
            if i == 0:
                fenGe += "+"
                print(fenGe)
            print(printRow)
            if i == dataLen - 1:
                if dataLen - 1 != 0:
                    fenGe += "+"
                print(fenGe)
            i += 1

    # 将列表分割 每一份n的长度
    @staticmethod
    def explodeList(data, n):
        if isinstance(data, list):
            return [data[i:i + n] for i in range(0, len(data), n)]
        else:
            return []

    @staticmethod
    def re_split(string, pattern=None):
        """默认用空格分割字符串，多个空格会合并成一个处理"""
        pattern = r'\s+' if pattern is None else pattern
        return re.split(pattern, string)

    # 把英文的引号转换程中文的引号
    @staticmethod
    def replaceYinHao(strings):
        return strings.replace('"', '“').replace("'", "‘")

    # 把值转为int
    @staticmethod
    def transInt(val, default=0):
        try:
            val = int(val)
        except ValueError:
            val = default
        return val

    @staticmethod
    def transFloat(val, default=0):
        try:
            val = float(val)
        except ValueError:
            val = default
        return val

    # 转化为保留两位小数的格式
    @staticmethod
    def switch2(data1, data2=None, returnDefault=0.00, precision=2):
        if data1 == 0 or data2 == 0:
            return returnDefault
        if data2 is not None:
            data = data1 / data2
        else:
            data = data1
        return round(data, precision)

    # 转换为百分比
    @staticmethod
    def switchRate(data1, data2=None, returnDefault='0.00%', precision=2):
        if data1 == 0 or data2 == 0:
            return returnDefault
        if data2 is not None:
            data = data1 / data2 * 100
        else:
            data = data1 * 100
        return ('{:.%sf}' % precision).format(data) + '%'

    # 从list中删除数据
    @staticmethod
    def delListValue(needList, delValues):
        if not isinstance(delValues, list):
            delValues = [delValues]
        for delValue in delValues:
            needList = [x for x in needList if x != delValue]
        return needList

    # 查找二维数组的某一行 demo [{'iType': 1, 'num': 3972}, {'iType': 2, 'num': 6315}, {'iType': 3, 'num': 6250}]
    @staticmethod
    def search2ListRow(data, keyField, value):
        for row in data:
            if row[keyField] == value:
                return row
        return {}

    # 把二维数组根据某一个key转为字典 demo [{'iType': 1, 'num': 3972}, {'iType': 2, 'num': 6315}, {'iType': 3, 'num': 6250}]
    @staticmethod
    def trans2ListDict(data, keyField):
        retDict = {}
        for row in data:
            retDict[row[keyField]] = row
        return retDict

    # 排序字典的key
    @staticmethod
    def sortDictByKey(myDict, reverse=False):
        return dict(sorted(myDict.items(), key=lambda x: x[0], reverse=reverse))

    # 排序字典的value
    @staticmethod
    def sortDictByValue(myDict, reverse=False):
        return dict(sorted(myDict.items(), key=lambda x: x[1], reverse=reverse))

    """
    根据条件，删除字典中的数据
    myDict = {'key1': 1, 'key2': 2, 'key3': 3}
    common.delDictItem(myDict, "key == 'key1'")
    common.delDictItem(myDict, "value == 1")
    common.delDictItem(myDict, "value > 1")
    """

    @staticmethod
    def delDictItem(myDict=None, delWhere=None):
        if not isinstance(myDict, dict):
            return {}
        if delWhere is None:
            return myDict
        # 使用字典推导式创建新字典，排除要删除的键
        myDict = {key: value for key, value in myDict.items() if not eval(delWhere)}
        return myDict

    @staticmethod
    def getMD5(string):
        string = string if isinstance(string, str) else str(string)
        md5 = hashlib.md5()
        md5.update(string.encode('utf-8'))
        return md5.hexdigest()

    @staticmethod
    def urlEncode(string):
        string = string if isinstance(string, str) else str(string)
        return quote(string, 'utf-8')

    @staticmethod
    def urlDecode(string):
        string = string if isinstance(string, str) else str(string)
        return unquote(string, 'utf-8')

    # 多线程运行任务
    """
    tasks = [[funcName, p1,p2],[funcName, p1,p2],[funcName, p1,p2],[funcName, p1,p2]]
    返回的exception里面是None就表示正常
    返回的result里面有None，大概率就是出现异常了 None not in result 表示全部正常
    """

    @staticmethod
    def multipleThreadRunTasks(max_workers, tasks, get_result=False, get_exceptions=False, print_info=True):
        # 创建一个拥有 max_workers 个线程的线程池
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for oneTask in tasks:
                #  executor.submit(funcName, p1, p2,..)
                future = executor.submit(*oneTask)
                futures.append(future)
            # 监控线程池中剩余的任务数量
            all_futures = futures.__len__()
            while True:
                timeHelper.sleep(1)
                unfinished_count = sum(not future.done() for future in futures)
                if print_info:
                    common.print(f"完成进度: {all_futures - unfinished_count}/{all_futures}")
                if unfinished_count == 0:
                    break
            results = []
            exceptions = []
            if get_result:
                for future in futures:
                    if future.exception() is None:
                        results.append(future.result())
                    else:
                        results.append(None)
            if get_exceptions:
                for future in futures:
                    exceptions.append(future.exception())
            if get_result and not get_exceptions:
                return results
            if not get_result and get_exceptions:
                return exceptions
            if get_result and get_exceptions:
                return results, exceptions
            return None

    # 多进程运行任务
    @staticmethod
    def multipleProcessRunTasks(max_workers, tasks, get_result=False, get_exceptions=False, print_info=True):
        # 创建一个拥有 max_workers 个线程的线程池
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for oneTask in tasks:
                #  executor.submit(funcName, p1, p2,..)
                future = executor.submit(*oneTask)
                futures.append(future)
            # 监控线程池中剩余的任务数量
            all_futures = futures.__len__()
            while True:
                timeHelper.sleep(1)
                unfinished_count = sum(not future.done() for future in futures)
                if print_info:
                    common.print(f"完成进度: {all_futures - unfinished_count}/{all_futures}")
                if unfinished_count == 0:
                    break
            results = []
            exceptions = []
            if get_result:
                for future in futures:
                    if future.exception() is None:
                        results.append(future.result())
                    else:
                        results.append(None)
            if get_exceptions:
                for future in futures:
                    exceptions.append(future.exception())
            if get_result and not get_exceptions:
                return results
            if not get_result and get_exceptions:
                return exceptions
            if get_result and get_exceptions:
                return results, exceptions
            return None

    # base64编码
    @staticmethod
    def base64Encode(string):
        string = str(string) if not isinstance(string, str) else string
        return base64.b64encode(string.encode('utf-8')).decode('utf-8')

    # Base64 编码在最后可能需要添加填充字符 '=' 以使编码后的字符串长度是 4 的倍数。如果输入的字符串没有正确的填充，就会导致解码错误。
    @staticmethod
    def base64Decode(string):
        string = str(string)
        stringLen = string.__len__()
        yuShu = stringLen % 4
        addString = ''
        if yuShu > 0:
            addString = (4 - yuShu) * '='
        return base64.b64decode(string + addString).decode('utf-8')

    # 得到一个随机整数，包含start和end
    @staticmethod
    def getRandomInt(startInt, endInt):
        return random.randint(startInt, endInt)


if __name__ == '__main__':
    # print(common.re_split('1    2  3 4'))

    common.print_table(data=[
        ["Nameaaa", "Age", "ZCity"],
        [sysHelper.red("Alice"), "25", "New York中文"],
        ["Boba", "30", "San Francisco"],
        [sysHelper.red("Chardlie"), "22", "Los Angeles"],
        ["Charlie", "22", sysHelper.green("Los Angeles")],
        ["Charlieaa", "22", "Los Angeles"],
        ["Charlieaa", "22", "Los Angeles"],
    ], table_name='list of names', data_has_title=True, sort_col_index=0,sort_lambda=lambda x:len(x),sort_reverse=True)

    # print(common.trans2ListDict([{'iType': 1, 'num': 3972}, {'iType': 2, 'num': 6315}, {'iType': 3, 'num': 6250}],'iType'))

    """
    def test(p1):
        return p1

    tasks = []
    for i in range(100):
        tasks.append([common.urlEncode, i])
    common.print('start')
    result = common.multipleThreadRunTasks(50,tasks=tasks,get_result=True)
    print(result)
    common.print('end')
    exit()
    """

    # test = ['a','b','a','c','d',None]
    # print(common.delListValue(test,['f',None,'a']))
    # print(test)
    # print(common.delDictItem({'c_actual收入': 900.0, 'a日期': '2023-11-09', 'b新增': 62, 'd留存1': 62, 'e收入1': 0, 'f付费人数1': 0, 'd留存2': 0, 'e收入2': 0, 'f付费人数2': 0, 'd留存3': 0, 'e收入3': 0, 'f付费人数3': 0},"key=='c_actual收入' and value==900"))
    # print(common.switchRate(0,0,precision=4,returnDefault='0.0000%'))
    # print(common.urlDecode('%E4%BD%A0%E5%A5%BD'))
