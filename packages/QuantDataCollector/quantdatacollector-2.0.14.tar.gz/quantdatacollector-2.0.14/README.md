# 数据收集

## 简介

> QuantDataCollector的目的是提供统一、稳定的数据接口，用户可以不用考虑数据获取问题，专注策略开发。



## 使用

> 使用Cache前需要先完成环境变量配置，比如使用MYSQL作为缓存，则需要设置MYSQL环境变量，具体参考下文

通过DataCollector类向外提供统一接口，以获取所有股票sz.399995的基本信息为例：

```python
import QuantDataCollector as qdc
data_collector = qdc()
data = data_collector.get_stock_basic('000001.SZ')
print(data)
```

> code  name are exchage market list_status   list_date unlist_date act_name act_type
> 
> 0  000001.SZ  平安银行  深圳    SZSE     主板           L  1991-04-03        None   无实际控制人        无


### 日志查看

通过`get_data_collector_info`接口查看日志路径，进而查看日志

```python
import QuantDataCollector as qdc

data_collector = qdc()
print(data_collector.get_data_collector_info())
```


## 如何设置MySQL

目前仅支持MySQL作为缓存，为了使用缓存，需要设置环境变量：

* MYSQL_HOST: MySQL服务器地址
* MYSQL_PORT: MySQL服务器端口
* MYSQL_USER: MySQL用户名
* MYSQL_PASSWORD: MySQL密码

环境变量设置方法

* Windows
    `set MYSQL_HOST=192.168.71.17`
    
* Linux / MacOS
    相比Windows要简单一些，只需要`export MYSQL_HOST=192.168.6.19`即可


## 数据源及其特点


### [baostock](http://baostock.com/baostock/index.php/%E9%A6%96%E9%A1%B5)

已经包装好的**股票数据拉取**Python库，数据覆盖

- 股票
- 公司业绩
- 货币
- 存款利率

优点：

- 使用简单

缺点：

- 服务由他人提供，已有收费趋势，可用性不高



### [tushare](https://tushare.pro/)

tushare的数据比较全面，使用也很方便，但很多功能是需要付费使用的


## API接口

### get_stock_basic

获取股票基本信息

* 输入参数
    * code_list: 类型为list，指定需要的股票代码列表，格式为['000001.SZ','000002.SZ']，可选参数，如果不指定，则返回所有股票的基本信息
* 输出参数

    输入为pandas的DataFrame
    * code: 股票代码
    * name: 股票名称
    * area: 上市公司所在省份
    * exchage: 交易所代码
    * market: 市场类型（主板/创业板/科创板/CDR）
    * list_status： 上市状态 L上市 D退市 P暂停上市，默认是L
    * list_date：上市日期
    * unlist_date：退市日期
    * act_name：实控人名称
    * act_type：实控人性质

### get_daily_basic

获取股票每日行情数据（数据不完全，注意检查）

* 输入参数
    * code_list: 股票代码列表, 比如['000001.SZ', '000002.SZ']，可选参数，如果不指定，则返回所有股票的基本信息
    * date: 行情数据日期
    * start_date: 指定需要的起始日期，比如2020-01-01，不指定表示从1990-12-19号开始
    * end_date：指定需要的结束日期，比如2023-12-30，不指定表示到今天截止
* 输出参数
    * code
    * date
    * close：当日收盘价
    * turnover_rate：换手率（%）
    * turnover_rate_f：换手率（自由流通股）
    * volume_ratio：量比
    * pe：市盈率（总市值/净利润， 亏损的PE为空）
    * pe_ttm：市盈率（TTM，亏损的PE为空）
    * pb：市净率（总市值/净资产）
    * ps：市销率
    * ps_ttm：市销率（TTM）
    * dv_ratio：股息率 （%）
    * dv_ttm：股息率（TTM） （%）
    * total_share：总股本 （万股）
    * float_share：流通股本 （万股）
    * free_share：自由流通股本 （万）
    * total_mv：总市值 （万元）
    * circ_mv：流通市值（万元）

### get_daily

获取股票日线数据不完全，注意检查）

* 输入参数
    * code: 指定需要的股票代码，格式为000001.SZ，可选参数，如果不指定，则返回所有股票的基本信息
    * date: 日线数据日期
    * start_date: 指定需要的起始日期，比如2020-01-01，不指定表示从1990-12-19号开始
    * end_date：指定需要的结束日期，比如2023-12-30，不指定表示到今天截止
    * fap_std_day: forward adjust price前复权价格基准日期，，不指定则不返回前复权价格
* 输出参数
    * code：股票代码
    * date：交易日期
    * open：开盘价
    * close：收盘价
    * high：最高价
    * low：最低价
    * fa_open:经过前复权的开盘价（可能不存在，比如为传参fap_std_day，或者计算错误）
    * fa_close: 经过前复权的收盘价（可能不存在，比如为传参fap_std_day，或者计算错误）
    * fa_high: 经过前复权的最高价（可能不存在，比如为传参fap_std_day，或者计算错误）
    * fa_low: 经过前复权的最低价（可能不存在，比如为传参fap_std_day，或者计算错误）
    * change_amount：涨跌额
    * vol：成交量 （手）
    * amount：成交额 （千元）

### get_limit_list

获取股票涨停、跌停、炸板信息

* 输入参数
    * code: 指定需要的股票代码，格式为000001.SZ，可选参数，如果不指定，则不限制代码
    * date: 出现涨停、跌停、炸板信息的日期，格式为'yyyy-mm-dd'。可选参数，不指定表示不限制日期
    * type: 涨跌停、炸板类型：U涨停D跌停Z炸板，可选参数，不指定表示不限制类型
    * start_date: 指定需要的起始日期，比如2020-01-01，不指定表示从1990-12-19号开始
    * end_date：指定需要的结束日期，比如2023-12-30，不指定表示到今天截止

* 输出参数

    输出为pandas的DataFrame
    * code: 股票代码
    * date: 发生涨跌停的日期
    * limit_amount: 板上成交金额(成交价格为该股票跌停价的所有成交额的总和，涨停无此数据)
    * fd_amount： 封单金额（以涨停价买入挂单的资金总量）
    * first_time： 首次封板时间（跌停无此数据）
    * last_time：最后封板时间
    * open_times：炸板次数(跌停为开板次数)
    * up_stat：涨停统计（N/T T天有N次涨停）
    * limit_times：连板数（个股连续封板数量）
    * limit_type：D跌停U涨停Z炸板

### get_holder_number
    获取股票的股东数量

* 输入参数
    * code_list: 股票代码列表, 比如['000001.SZ', '000002.SZ']，如果不传则查询所有股票的股东数量
    * cut_off_date: 指定数据统计的截止日期，格式为YYYY-MM-DD，返回数据统计的截止日期在该日期之前的所有数据，默认为查询所有截止日期的数据
    
* 输出参数
    输出为pandas的DataFrame
    * code: 股票代码
    * ann_pub_date: 公告发布的日期
    * cut_off_date: 股东人数数据统计的截止日期
    * holder_num: 股东人数

### get_trade_calendar

    获取交易日历
* 输入参数
    * is_open: 需要获取日期的交易状态，指定is_open=1表示只要交易中的日期，指定为0表示只要休市的日期，不指定表示不限制
    * start_date: 指定需要的起始日期，比如2020-01-01，不指定表示从1990-12-19号开始
    * end_date：指定需要的结束日期，比如2023-12-30，不指定表示到今天截止
    * exchange：A股的不同交易所交易/休市日期相同，一般不用指定，默认为上海交易所

* 输出参数
    输出为pandas的DataFrame
    * date: 日期
    * pre_trade_date: 距离该日期最近的上一个交易日
    * is_open: 交易状态， 1表示交易中，0表示休市

### get_tonghuashun_index
    获取同花顺行业概念板块数据

* 输入参数
    * index_code：行业板块代码，比如"700001.TI"
    * exchange：交易所，市场类型A-a股 HK-港股 US-美股
    * type：指数类型 N-概念指数 I-行业指数 R-地域指数 S-同花顺特色指数 ST-同花顺风格指数 TH-同花顺主题指数 BB-同花顺宽基指数
* 输出参数
    输出为pandas的DataFrame
    * index_code：行业板块代码
    * name：行业板块名称
    * count：指数成分股数量
    * exchange：交易所
    * list_date：上市日期
    * type：指数类型 N-概念指数 I-行业指数 R-地域指数 S-同花顺特色指数 ST-同花顺风格指数 TH-同花顺主题指数 BB-同花顺宽基指数

### get_tonghuashun_index_member
    获取同花顺行业概念板块成分股数据

* 输入参数
    * index_code：指数代码
    * code：成分股代码
* 输出参数
    输出为pandas的DataFrame
    * index_code：指数代码
    * code：成分股代码
    * name：成分股名称
    * weight：成分股权重（暂无数据）
    * in_date：纳入日期(暂无)
    * out_date：剔除日期(暂无)
    * is_new：是否最新Y是N否

### get_chip_yardstick_quotient
    获取筹码及胜率数据

* 输入参数
    * code_list: 股票代码列表, 比如['000001.SZ', '000002.SZ']，如果不传则查询所有股票的股东数量
    * date: 筹码数据日期
    * start_date: 指定需要的起始日期，比如2020-01-01，不指定表示从1990-12-19号开始
    * end_date：指定需要的结束日期，比如2023-12-30，不指定表示到今天截止
* 输出参数
    输出为pandas的DataFrame
    * code：股票代码
    * date：交易日期
    * his_low：历史最低价
    * his_high：历史最高价
    * cost_5pct：5分位成本
    * cost_15pct：15分位成本
    * cost_50pct：50分位成本
    * cost_85pct：85分位成本
    * cost_95pct：95分位成本
    * weight_avg：加权平均成本
    * winner_rate：胜率

### get_adjust_factor
    获取复权因子

* 输入参数
    * code: 指定需要的股票代码，格式为000001.SZ，可选参数，如果不指定，则返回所有股票的基本信息
    * date: 交易日期
    * start_date: 指定需要的起始日期，比如2020-01-01，不指定表示从1990-12-19号开始
    * end_date：指定需要的结束日期，比如2023-12-30，不指定表示到今天截止
* 输出参数
    输出为pandas的DataFrame
    * code：股票代码
    * date：交易日期
    * adj_factor：复权因子

### get_top_institution
  获取龙虎榜机构成交明细

* 输入参数
    * code_list: 股票代码列表, 比如['000001.SZ', '000002.SZ']，如果不传则查询所有股票的股东数量
    * date: 筹码数据日期
    * start_date: 指定需要的起始日期，比如2020-01-01，不指定表示从1990-12-19号开始
    * end_date：指定需要的结束日期，比如2023-12-30，不指定表示到今天截止

* 输出参数
    输出为pandas的DataFrame
    * code：股票代码
    * date：交易日期
    * exalter：营业部名称
    * side：买卖类型0：买入金额最大的前5名， 1：卖出金额最大的前5名
    * buy：买入额（元）
    * buy_rate：买入占总成交比例
    * sell：卖出额（元）
    * sell_rate：	卖出占总成交比例
    * net_buy：净成交额（元）
    * reason：上榜理由