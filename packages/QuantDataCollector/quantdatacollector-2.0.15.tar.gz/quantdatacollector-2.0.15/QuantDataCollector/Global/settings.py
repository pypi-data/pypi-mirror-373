"""
全局使用的静态变量

包括运行结果、日志所在路径等
"""

from enum import IntEnum, unique
import sys
import os
import logging

# -------------- 私有方法 ---------------
def get_parent_path(path, level=1):
    """获取父路径
    
    由于不同的系统中，获取父路径的方式不同，利用os的接口实现

    Args:
      path: String，当前路径
      level: Number，父路径的级别，比如level=2，相当于linux中的path/../../

    Returns:
      String: 父路径
    """
    res_path = path
    for i in range(level):
        res_path = os.path.split(res_path)[0]
    return res_path

REPO_ROOT_PATH=get_parent_path(os.path.abspath(__file__),2)
RESULTS_ROOT_PATH=REPO_ROOT_PATH + "/results"

# ------------- 日志相关配置 -----------
LOGGING_LEVEL=logging.DEBUG
LOGGING_FILE_DIR=RESULTS_ROOT_PATH + "/log"
LOGGING_FILE_NAME=LOGGING_FILE_DIR + "/log.txt"

# ------------- 数据库相关 --------------




STOCK_DATABASE_NAME = "quant_data_database"

STOCK_BASIC_INFO_TABLE_NAME = "stock_basic_info_table"
STOCK_DAILY_BASIC_TABLE_NAME = "stock_daily_basic_table"
STOCK_DAILY_TABLE_NAME = "stock_daily_table"
STOCK_LIMIT_LIST_DAY_TABLE_NAME = "stock_limit_list_day_table"
STOCK_ADJUST_FACTOR_TABLE_NAME = "stock_adjust_factor_table"
STOCK_HOLDER_NUMBER_TABLE_NAME = "stock_holder_number_table"
STOCK_TRADE_CALENDAR_TABLE_NAME = "stock_trade_calendar_table"
STOCK_TONGHUASHUN_INDEX_TABLE_NAME = "stock_tonghuashun_index_table" # 同花顺概念和行业指数
STOCK_TONGHUASHUN_INDEX_MEMBER_TABLE_NAME = "stock_tonghuashun_index_member_table" # 同花顺概念板块成分
STOCK_CHIP_YARDSTICK_QUOTIENT_TABLE_NAME= "chip_yardstick_quotient_table"
STOCK_TOP_INSTITUTION_TABLE_NAME = "stock_top_institution_table"
STOCK_INDEX_BASIC_INFO_TABLE_NAME = "stock_index_basic_table"
STOCK_INDEX_DAILY_TABLE_NAME = "stock_index_daily_table"