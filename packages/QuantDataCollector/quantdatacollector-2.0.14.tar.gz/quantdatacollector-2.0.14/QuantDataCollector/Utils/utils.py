import time
from datetime import datetime, timedelta
    
'''获取上市超过一定时间的股票列表
input:
    stock_list:需要过滤的股票列表。
    days:上市超过days天的股票才会被留下。
    base:基准时间。"%Y-%m-%d"格式。如2015-01-01。则本函数会过滤出在2015年1月1号这个时间点，上市超过days天的股票的列表。
output:
    过滤后的股票列表，list形式，每个元素为字符串形式的股票代码。
'''
def load_stock_IPO_above(stock_list, days, base):
    # TODO:
    pass

# 从YYYYMMDDHHMMSSsss转化到YYYY-MM-DD HH:MM:SS.sss
def convert_to_mysql_datetime(time_str):
    if len(time_str) != 17 or not time_str.isdigit():
        raise ValueError("输入格式必须为17位数字: YYYYMMDDHHMMSSsss")

    # 拆分日期、时间、毫秒
    date_part = time_str[:8]          # YYYYMMDD
    time_part = time_str[8:14]        # HHMMSS
    milliseconds = time_str[14:17]    # sss

    # 解析日期和时间
    dt = datetime.strptime(date_part + time_part, "%Y%m%d%H%M%S")
    return dt
    
    # 将毫秒转换为微秒（补3个零，如 "123" -> 123000 微秒）
    microseconds = int(milliseconds.ljust(6, '0'))  # 确保总为6位
    
    # 合并微秒到datetime对象
    dt = dt.replace(microsecond=microseconds)

    
    # 格式化为 MySQL DATETIME(3) 格式（保留3位毫秒）
    mysql_datetime = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # 截取到3位毫秒
    return mysql_datetime

def get_date():
    """返回当前日期

    返回当前日期

    Returns:
      String: 日期，格式为"2021-03-21"
    """
    lt = time.localtime()
    res = str(lt.tm_year) + "-"
    if lt.tm_mon > 9:
        res += str(lt.tm_mon) + "-"
    else:
        res += "0"+str(lt.tm_mon) + "-"

    if lt.tm_mday > 9:
        res += str(lt.tm_mday)
    else:
        res += "0"+str(lt.tm_mday)
    return res

def date_compare(date1, date2):
    """比较格式为"2021-3-21"的日期大小, date1大返回1，date2大返回-1，相等返回0
    """
    try:
        date1_strptime = datetime.strptime(date1, "%Y-%m-%d")
        date2_strptime = datetime.strptime(date2, "%Y-%m-%d")
    except ValueError:
        raise ValueError("输入日期格式不符合YYYY-MM-DD")
    if date1_strptime > date2_strptime:
        return 1

    if date1_strptime < date2_strptime:
        return -1
    return 0

def date_remove_zero_padding(date):
    """对于格式为YYYY-MM-DD的日期，如果月份/日不够两位数，去掉前面的0

    Args:
      date: String,格式为YYYY-MM-DD的日期，比如2022-01-02、2022-10-11等

    Returns:
      String: 去掉0的日期

    Raises:
      ValueError: 日期格式错误时
    """
    try:
        date_strptime = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("输入日期格式不符合YYYY-MM-DD")
    return date_strptime.strftime("%Y-") + date_strptime.strftime("%m-").lstrip("0") + date_strptime.strftime("%d").lstrip("0")

def date_add_zero_padding(date):
    """对于格式为YYYY-M-D的日期，如果月份/日不够两位数，前面加上0

    Args:
      date: String,格式为YYYY-MM-DD的日期，比如2022-1-2、2022-10-11等

    Returns:
      String: 加上0的日期

    Raises:
      ValueError: 日期格式错误时
    """
    try:
        date_strptime = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("输入日期格式不符合YYYY-M-D")
    return date_strptime.strftime("%Y-%m-%d")

def date_increase(date):
    """格式为YYYY-MM-DD的日期，增加一天"""
    try:
        date_strptime = datetime.strptime(date,"%Y-%m-%d")
    except ValueError:
        raise ValueError("输入日期格式不符合YYYY-MM-DD")

    return (date_strptime + timedelta(days=1)).strftime("%Y-%m-%d")

def date_decrease(date):
    """格式为YYYY-MM-DD的日期，减小一天"""
    try:
        date_strptime = datetime.strptime(date,"%Y-%m-%d")
    except ValueError:
        raise ValueError("输入日期格式不符合YYYY-MM-DD")

    return (date_strptime + timedelta(days=-1)).strftime("%Y-%m-%d")

def date_format(date, expect_format = "%Y-%m-%d"):
    try:
        datetime.strptime(date, expect_format)
    except ValueError:
        return False
    return True



if __name__ == '__main__':
    print(get_date.__doc__)
    print(get_date())
    print(date_decrease(get_date()))
