from ..interface.mdc_query_sync_handle_data_class import *
from datetime import datetime, timedelta


def query_fin_info(query_type, params):
    return data_handle.get_interface().queryfininfosynchronous(query_type, params)


#
#
# def query_basicInfo_by_type(dictmarketdatatypes, isToday=True):
#     security_id_list = []  # 置空表示不额外查询某些标的
#     if isToday:
#         query_last_mdcontant(dictmarketdatatypes, security_id_list)
#     else:
#         query_mdcontant(dictmarketdatatypes, security_id_list)
#
#
# def query_basicInfo_by_id(listsecurityid, isToday=True):
#     listmarketdatatype = []  # 置空表示不额外查询某些标的
#     if isToday:
#         query_last_mdcontant(listmarketdatatype, listsecurityid)
#     else:
#         query_mdcontant(listmarketdatatype, listsecurityid)


# 查询证券的分钟K，日K，周K，月K数据，调用方式：同步返回，注：当日的日K需要在闭市后获取。
def get_kline(htsc_code=None, time=None, frequency='daily', fq="pre"):
    """
    :param htsc_code: 华泰证券代码，支持多个code查询，列表类型
    :param time: 时间范围，list类型，开始结束时间为datetime
    :param frequency: 频率，分钟K（‘1min’，’5min’，’15min’，’60min’），日K（‘daily’），周K（‘weekly’），月K（‘monthly’）
    :param fq: 复权，默认前复权”pre”，后复权为”post”，不复权“None”
    :return:pandas.DataFrame
    """

    if htsc_code:
        if not isinstance(htsc_code, str) and not isinstance(htsc_code, list):
            return "htsc_code format is not str or list"
    else:
        return 'htsc_code is null'

    if time:
        if isinstance(time, list):
            if len(time) > 2:
                return "time format is not [start_date, end_date]"
            if len(time) == 1:
                time = [time[0], time[0]]
            if not isinstance(time[0], datetime) or not isinstance(time[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "time format is not list"
    else:
        return 'time is null'

    result = get_kline_handle(htsc_code, time, frequency, fq)
    return result


# 查询股票每日衍生指标信息
def get_derived(htsc_code=None, trading_day=None, type=None):
    """
    :param htsc_code:华泰证券代码，支持多个code查询，列表类型
    :param trading_day: 时间范围，list类型，开始结束时间为datetime
    :param type:衍生指标类型，可选成本均价线amv，人气和买卖医院指标明细ar_br，乖离率明细bias，布林线明细boll，中间意愿指标明细cr，
    成交量平均线和移动平均线vma_ma，成交量变异率vr，威廉指标明细wr， 北向资金north_bound
    :return: pandas.DataFrame
    """

    if htsc_code:
        if not isinstance(htsc_code, str) and not isinstance(htsc_code, list):
            return "htsc_code format is not str or list"
    else:
        return 'htsc_code is null'

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_date format is not list"
    else:
        return 'trading_day is null'

    if type:
        if not isinstance(type, str):
            return "type format is not str"
    else:
        return 'type is null'

    result = get_derived_handle(htsc_code, trading_day, type)
    return result


# 查询成交分价
def get_trade_distribution(htsc_code=None, trading_day=None):
    """
    :param htsc_code: 华泰证券代码，支持多个code查询，列表类型
    :param trading_day: 时间范围，list类型，开始结束时间为datetime
    :return: pandas.DataFrame
    """

    if htsc_code:
        if not isinstance(htsc_code, str) and not isinstance(htsc_code, list):
            return "htsc_code format is not str or list"
    else:
        return 'htsc_code is null'

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"
    else:
        return 'trading_day is null'

    result = get_trade_distribution_handle(htsc_code, trading_day)
    return result


# 筹码分布
def get_chip_distribution(htsc_code=None, trading_day=None):
    """
    :param htsc_code: 华泰证券代码，支持多个code查询，列表类型
    :param trading_day: 时间范围，list类型，开始结束时间为datetime
    :return: pandas.DataFrame
    """

    if htsc_code:
        if not isinstance(htsc_code, str) and not isinstance(htsc_code, list):
            return "htsc_code format is not str or list"
    else:
        return 'htsc_code is null'

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"
    else:
        return 'trading_day is null'

    result = get_chip_distribution_handle(htsc_code, trading_day)
    return result


# 查询资金流向
def get_money_flow(htsc_code=None, trading_day=None):
    """
    :param htsc_code: 华泰证券代码，支持多个code查询，列表类型
    :param trading_day: 时间范围，list类型，开始结束时间为datetime
    :return: pandas.DataFrame
    """

    if htsc_code:
        if not isinstance(htsc_code, str) and not isinstance(htsc_code, list):
            return "htsc_code format is not str or list"
    else:
        return 'htsc_code is null'

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"
    else:
        return 'trading_day is null'

    result = get_money_flow_handle(htsc_code, trading_day)
    return result


# 查询涨跌分析
def get_change_summary(market=None, trading_day=None):
    """
    :param market: 证券市场代码，支持多个市场查询，列表类型
    :param trading_day: 时间范围，list类型，开始结束时间为datetime
    :return: pandas.DataFrame
    """

    if market:
        if not isinstance(market, str) and not isinstance(market, list):
            return "market format is not str or list"
    else:
        return 'market is null'

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"
    else:
        return 'trading_day is null'

    result = get_change_summary_handle(market, trading_day)
    return result


# 查询指标排行榜数据
def get_billboard(type=None, market=None):
    """
    :param type: 排行榜类别 涨幅榜:inc_list, 跌幅榜:dec_list, 振幅榜:amp_list, 量比榜:quant_list,
                        委比榜:comm_list, 换手率榜:turnover_rate_list, 成交额榜:trade_val,
                        成交量榜:trade_vol, 5分钟涨幅榜:inc_list_5min, 5分钟跌幅榜:dec_list_5min,
                        5分钟成交额榜:trade_val_5min, 5分钟成交量榜:trade_vol_5min
    :param market: 交易市场 多市场查询列表类型 沪A: sh_a_share, 深A: sz_a_share, 全A: a_share, 全B: b_share,
                            创业板: gem, 中小板: sme, 科创板: star
    :return: pandas.DataFrame
    """

    result = get_billboard_handle(type, market)
    return result


# 股票基础信息-按证券ID查询
def get_stock_info(htsc_code=None, listing_date=None, listing_state=None):
    """
    :param htsc_code: 华泰证券代码，支持多标的查询，列表类型
    :param listing_date: 上市时间范围，列表类型，datetime格式 [start_date, end_date]
    :param listing_state: 上市状态: 上市交易/终止上市
    :return: pandas.DataFrame
    """

    if listing_date:
        if isinstance(listing_date, list):
            if len(listing_date) > 2:
                return "listing_date format is not [start_date, end_date]"
            if len(listing_date) == 1:
                listing_date = [listing_date[0], listing_date[0]]
            if not isinstance(listing_date[0], datetime) or not isinstance(listing_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "listing_date format is not list"

    if listing_state and listing_state not in ["上市交易", "终止上市"]:
        return "listing_state does not exist"

    result = get_stock_info_handle(htsc_code, listing_date, listing_state)
    return result


# 股票基础信息-按市场查询
def get_all_stocks_info(listing_date=None, exchange=None, listing_state=None):
    """
    :param listing_date: 上市时间范围，列表类型，datetime格式 [start_date, end_date]
    :param exchange: 交易市场代码
    :param listing_state: 上市状态: 上市交易/终止上市
    :return: pandas.DataFrame
    """

    if listing_date:
        if isinstance(listing_date, list):
            if len(listing_date) > 2:
                return "listing_date format is not [start_date, end_date]"
            if len(listing_date) == 1:
                listing_date = [listing_date[0], listing_date[0]]
            if not isinstance(listing_date[0], datetime) or not isinstance(listing_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "listing_date format is not list"

    if listing_state and listing_state not in ["上市交易", "终止上市"]:
        return "listing_state does not exist"

    result = get_all_stocks_info_handle(listing_date, exchange, listing_state)
    return result


# 交易日历
def get_trading_days(exchange=None, trading_day=None, count=None):
    """
    :param exchange: 交易市场代码
    :param trading_day: 查询时间范围
    :param count: 倒计时，0代表今天， -1代表返回前一天到今天的交易日，1代表返回今天到后一天，和trading_day二选一
    :return: pandas.DataFrame
    """

    if exchange:
        exchange = str(exchange)

    if trading_day and count:
        return "trading_day and count only choose one of two"

    if not trading_day and not count:
        trading_day = [datetime.today(), datetime.today()]

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "listing_date format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    if count:
        if isinstance(count, int):
            add_day_datetime = (datetime.today() + timedelta(days=count))
            if count > 0:
                trading_day = [datetime.today(), add_day_datetime]
            if count < 0:
                trading_day = [add_day_datetime, datetime.today()]
            if count == 0:
                trading_day = [datetime.today(), datetime.today()]
        else:
            return "count format is not int"

    result = get_trading_days_handle(exchange, trading_day)
    return result


# 行业分类-按行业查询
def get_industries(classified=None):
    """
    :param classified: 行业分类，"sw_l1": 申万一级行业
                               "sw_l2": 申万二级行业
                               "sw_l3": 申万三级行业
                               "zjh_l1": 证监会一级行业
                               "zjh_l2": 证监会二级行业
    :return: pandas.DataFrame
    """

    if classified in ["sw_l1", "sw_l2", "sw_l3", "zjh_l1", "zjh_l2"]:

        result = get_industries_handle(classified)
        return result

    else:
        return "classified does not exist"


# 行业分类-按标的查询
def get_industry(htsc_code=None, classified='sw'):
    """
    :param htsc_code: 华泰证券代码
    :param classified: 行业分类 申万行业划分“sw”，证监会行业划分“zjh”，默认为申万行业划分
    :return: pandas.DataFrame
    """

    if not htsc_code:
        return 'htsc_code is null or empty'

    if not isinstance(htsc_code, str):
        return 'htsc_code format error'

    if classified in ['sw', 'zjh']:
        result = get_industry_handle(htsc_code, classified)
        return result

    else:
        return "classified does not exist"


# 行业分类-按行业代码查询
def get_industry_stocks(industry_code=None, classified='sw'):
    """
    :param industry_code: 行业代码
    :param classified: 行业分类 申万行业划分“sw”，证监会行业划分“zjh”，默认为申万行业划分
    :return: pandas.DataFrame
    """

    if not industry_code:
        return 'industry_code is null or empty'

    if not isinstance(industry_code, str):
        return 'industry_code format error'

    if classified in ['sw', 'zjh']:
        result = get_industry_stocks_handle(industry_code, classified)
        return result

    else:
        return "classified does not exist"


# 新股上市
def get_new_share(htsc_code=None, book_start_date_online=None, listing_date=None):
    """
    :param htsc_code: 华泰证券ID
    :param book_start_date_online: 网上申购开始日期时间范围
    :param listing_date: 上市日期时间范围
    :return: pandas.DataFrame
    """

    if htsc_code:
        if isinstance(htsc_code, str):
            pass
        else:
            return "htsc_code format is not str"

    if book_start_date_online:
        if isinstance(book_start_date_online, list):
            if len(book_start_date_online) > 2:
                return "book_start_date_online format is not [start_date, end_date]"
            if len(book_start_date_online) == 1:
                book_start_date_online = [book_start_date_online[0], book_start_date_online[0]]
            if not isinstance(book_start_date_online[0], datetime) or not isinstance(book_start_date_online[1],
                                                                                     datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "book_start_date_online format is not list"

    if listing_date:
        if isinstance(listing_date, list):
            if len(listing_date) > 2:
                return "listing_date format is not [start_date, end_date]"
            if len(listing_date) == 1:
                listing_date = [listing_date[0], listing_date[0]]
            if not isinstance(listing_date[0], datetime) or not isinstance(listing_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "listing_date format is not list"

    result = get_new_share_handle(htsc_code, book_start_date_online, listing_date)
    return result


# 日行情接口
def get_daily_basic(htsc_code=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID
    :param trading_day: 交易日期
    :return: pandas.DataFrame
    """

    if htsc_code:
        if not isinstance(htsc_code, str):
            return "htsc_code format is not str"

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    result = get_daily_basic_handle(htsc_code, trading_day)
    return result


# 市值数据
def get_stock_valuation(htsc_code=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID
    :param trading_day: 交易日期
    :return: pandas.DataFrame
    """

    if htsc_code:
        if not isinstance(htsc_code, str):
            return "htsc_code format is not str"

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    result = get_stock_valuation_handle(htsc_code, trading_day)
    return result


# 债券基础信息-按证券ID查询
def get_bond_info(htsc_code=None, secu_category_code=None, listing_date=None, issue_start_date=None, end_date=None):
    """
    :param htsc_code: 华泰证券ID
    :param secu_category_code: 证券类别代码（细分）
                                1    1301    国债
                                2    1302    央行票据
                                3    1310    政策性金融债
                                4    1319    普通金融债
                                5    1320    普通企业债
                                6    1326    资产支持票据
                                7    1327    大额可转让同业存单
                                8    1328    项目收益票据
                                9    1329    大额存单
                                10   1331    标准化票据
                                11   1340    国际开发机构债券
                                12   1350    常规可转债
                                13   1360    地方政府债
                                14   1370    可交换公司债券
                                15   1380    特种金融债券
                                16   1390    券商专项资产管理
                                17   1391    场外债券
                                18   133002    资产支持证券化(ABS)
                                19   13300101    住房抵押贷款证券化
                                20   13300102    汽车抵押贷款证券化
    :param listing_date: 上市时间范围，列表类型，datetime格式 [start_date, end_date]
    :param issue_start_date: 发行时间范围，列表类型，datetime格式 [start_date, end_date]
    :param end_date: 到期时间范围，列表类型，datetime格式 [start_date, end_date]
    :return: pandas.DataFrame
    """

    if listing_date:
        if isinstance(listing_date, list):
            if len(listing_date) > 2:
                return "listing_date format is not [start_date, end_date]"
            if len(listing_date) == 1:
                listing_date = [listing_date[0], listing_date[0]]
            if not isinstance(listing_date[0], datetime) or not isinstance(listing_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "listing_date format is not list"

    if issue_start_date:
        if isinstance(issue_start_date, list):
            if len(issue_start_date) > 2:
                return "issue_start_date format is not [start_date, end_date]"
            if len(issue_start_date) == 1:
                issue_start_date = [issue_start_date[0], issue_start_date[0]]
            if not isinstance(issue_start_date[0], datetime) or not isinstance(issue_start_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "issue_start_date format is not list"

    if end_date:
        if isinstance(end_date, list):
            if len(end_date) > 2:
                return "end_date format is not [start_date, end_date]"
            if len(end_date) == 1:
                end_date = [end_date[0], end_date[0]]
            if not isinstance(end_date[0], datetime) or not isinstance(end_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "end_date format is not list"

    result = get_bond_info_handle(htsc_code, secu_category_code, listing_date, issue_start_date, end_date)
    return result


# 债券基础信息-按市场查询
def get_all_bonds(exchange=None, secu_category_code=None, listing_date=None, issue_start_date=None, end_date=None):
    """
    :param exchange: 交易市场
    :param secu_category_code: 证券类别代码（细分），str类型
                                1    1301    国债
                                2    1302    央行票据
                                3    1310    政策性金融债
                                4    1319    普通金融债
                                5    1320    普通企业债
                                6    1326    资产支持票据
                                7    1327    大额可转让同业存单
                                8    1328    项目收益票据
                                9    1329    大额存单
                                10   1331    标准化票据
                                11   1340    国际开发机构债券
                                12   1350    常规可转债
                                13   1360    地方政府债
                                14   1370    可交换公司债券
                                15   1380    特种金融债券
                                16   1390    券商专项资产管理
                                17   1391    场外债券
                                18   133002    资产支持证券化(ABS)
                                19   13300101    住房抵押贷款证券化
                                20   13300102    汽车抵押贷款证券化
    :param listing_date: 上市时间范围，列表类型，datetime格式 [start_date, end_date]
    :param issue_start_date: 发行时间范围，列表类型，datetime格式 [start_date, end_date]
    :param end_date: 到期时间范围，列表类型，datetime格式 [start_date, end_date]
    :return: pandas.DataFrame
    """

    if listing_date:
        if isinstance(listing_date, list):
            if len(listing_date) > 2:
                return "listing_date format is not [start_date, end_date]"
            if len(listing_date) == 1:
                listing_date = [listing_date[0], listing_date[0]]
            if not isinstance(listing_date[0], datetime) or not isinstance(listing_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "listing_date format is not list"

    if issue_start_date:
        if isinstance(issue_start_date, list):
            if len(issue_start_date) > 2:
                return "issue_start_date format is not [start_date, end_date]"
            if len(issue_start_date) == 1:
                issue_start_date = [issue_start_date[0], issue_start_date[0]]
            if not isinstance(issue_start_date[0], datetime) or not isinstance(issue_start_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "issue_start_date format is not list"

    if end_date:
        if isinstance(end_date, list):
            if len(end_date) > 2:
                return "end_date format is not [start_date, end_date]"
            if len(end_date) == 1:
                end_date = [end_date[0], end_date[0]]
            if not isinstance(end_date[0], datetime) or not isinstance(end_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "end_date format is not list"

    result = get_all_bonds_handle(exchange, secu_category_code, listing_date, issue_start_date, end_date)
    return result


# 债券回购行情
def get_repo_price(htsc_code=None, exchange=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID
    :param exchange: 交易市场
    :param trading_day: 交易日期（范围）
    :return: pandas.DataFrame
    """

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    result = get_repo_price_handle(htsc_code, exchange, trading_day)
    return result


# 可转债发行列表
def get_new_con_bond(htsc_code=None, exchange=None, book_start_date_online=None, listing_date=None, issue_date=None,
                     convert_code=None):
    """
    :param htsc_code: 华泰证券ID
    :param exchange: 交易市场
    :param book_start_date_online: 网上申购开始日期时间范围
    :param listing_date: 上市日期时间范围
    :param issue_date: 发行日期范围
    :param convert_code: 转股代码
    :return: pandas.DataFrame
    """

    if book_start_date_online:
        if isinstance(book_start_date_online, list):
            if len(book_start_date_online) > 2:
                return "book_start_date_online format is not [start_date, end_date]"
            if len(book_start_date_online) == 1:
                book_start_date_online = [book_start_date_online[0], book_start_date_online[0]]
            if not isinstance(book_start_date_online[0], datetime) or not isinstance(book_start_date_online[1],
                                                                                     datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "book_start_date_online format is not list"

    if listing_date:
        if isinstance(listing_date, list):
            if len(listing_date) > 2:
                return "listing_date format is not [start_date, end_date]"
            if len(listing_date) == 1:
                listing_date = [listing_date[0], listing_date[0]]
            if not isinstance(listing_date[0], datetime) or not isinstance(listing_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "listing_date format is not list"

    if issue_date:
        if isinstance(issue_date, list):
            if len(issue_date) > 2:
                return "issue_date format is not [start_date, end_date]"
            if len(issue_date) == 1:
                issue_date = [issue_date[0], issue_date[0]]
            if not isinstance(issue_date[0], datetime) or not isinstance(issue_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "issue_date format is not list"

    result = get_new_con_bond_handle(htsc_code, exchange, book_start_date_online, listing_date, issue_date,
                                     convert_code)
    return result


# 债券市场行情
def get_bond_price(htsc_code=None, exchange=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID
    :param exchange: 交易市场代码
    :param trading_day: 交易日期（范围）
    :return: pandas.DataFrame
    """

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "end_date format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    result = get_bond_price_handle(htsc_code, exchange, trading_day)
    return result


# 可转债赎回信息
def get_con_bond_redemption(htsc_code=None, exchange=None, register_date=None):
    """
    :param htsc_code: 华泰证券ID
    :param exchange: 交易市场代码
    :param register_date: 登记时间范围
    :return: pandas.DataFrame
    """

    if register_date:
        if isinstance(register_date, list):
            if len(register_date) > 2:
                return "end_date format is not [start_date, end_date]"
            if len(register_date) == 1:
                register_date = [register_date[0], register_date[0]]
            if not isinstance(register_date[0], datetime) or not isinstance(register_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "register_date format is not list"

    result = get_con_bond_redemption_handle(htsc_code, exchange, register_date)
    return result


# 可转债转股价变动
def get_con_bond_2_shares_change(htsc_code=None, exchange=None, pub_date=None, convert_code=None):
    """
    :param htsc_code: 华泰证券ID
    :param exchange: 交易市场代码
    :param pub_date: 公告日期范围
    :param convert_code: 转股代码
    :return: pandas.DataFrame
    """

    if pub_date:
        if isinstance(pub_date, list):
            if len(pub_date) > 2:
                return "pub_date format is not [start_date, end_date]"
            if len(pub_date) == 1:
                pub_date = [pub_date[0], pub_date[0]]
            if not isinstance(pub_date[0], datetime) or not isinstance(pub_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "pub_date format is not list"

    result = get_con_bond_2_shares_change_handle(htsc_code, exchange, pub_date, convert_code)
    return result


# 可转债转股结果
def get_con_bond_2_shares(htsc_code=None, pub_date=None, exer_begin_date=None, exer_end_date=None, convert_code=None,
                          exchange=None):
    """
    :param htsc_code: 华泰证券ID
    :param pub_date: 信息发布日期范围
    :param exer_begin_date: 行权起始日范围
    :param exer_end_date: 行权截止日范围
    :param convert_code: 转股代码
    :param exchange: 交易市场
    :return: pandas.DataFrame
    """

    if pub_date:
        if isinstance(pub_date, list):
            if len(pub_date) > 2:
                return "pub_date format is not [start_date, end_date]"
            if len(pub_date) == 1:
                pub_date = [pub_date[0], pub_date[0]]
            if not isinstance(pub_date[0], datetime) or not isinstance(pub_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "pub_date format is not list"

    if exer_begin_date:
        if isinstance(exer_begin_date, list):
            if len(exer_begin_date) > 2:
                return "exer_begin_date format is not [start_date, end_date]"
            if len(exer_begin_date) == 1:
                exer_start_date = [exer_begin_date[0], exer_begin_date[0]]
            if not isinstance(exer_begin_date[0], datetime) or not isinstance(exer_begin_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "exer_begin_date format is not list"

    if exer_end_date:
        if isinstance(exer_end_date, list):
            if len(exer_end_date) > 2:
                return "exer_end_date format is not [start_date, end_date]"
            if len(exer_end_date) == 1:
                exer_end_date = [exer_end_date[0], exer_end_date[0]]
            if not isinstance(exer_end_date[0], datetime) or not isinstance(exer_end_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "exer_end_date format is not list"

    result = get_con_bond_2_shares_handle(htsc_code, pub_date, exer_begin_date, exer_end_date, convert_code, exchange)
    return result


# 利润表
def get_income_statement(htsc_code=None, end_date=None, period=None):
    """
    :param htsc_code: 华泰证券ID
    :param end_date: 限定时间范围
    :param period: 报表类型，Q1，Q2，Q3，Q4
    :return: pandas.DataFrame
    """

    if end_date:
        if isinstance(end_date, list):
            if len(end_date) > 2:
                return "end_date format is not [start_date, end_date]"
            if len(end_date) == 1:
                end_date = [end_date[0], end_date[0]]
            if not isinstance(end_date[0], datetime) or not isinstance(end_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "end_date format is not list"

    result = get_income_statement_handle(htsc_code, end_date, period)
    return result


# 资产负债表
def get_balance_sheet(htsc_code=None, end_date=None, period=None):
    """
    :param htsc_code: 华泰证券ID
    :param end_date: 限定时间范围
    :param period: 报表类型，Q1，Q2，Q3，Q4
    :return: pandas.DataFrame
    """

    if end_date:
        if isinstance(end_date, list):
            if len(end_date) > 2:
                return "end_date format is not [start_date, end_date]"
            if len(end_date) == 1:
                end_date = [end_date[0], end_date[0]]
            if not isinstance(end_date[0], datetime) or not isinstance(end_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "end_date format is not list"

    result = get_balance_sheet_handle(htsc_code, end_date, period)
    return result


# 现金流量表
def get_cashflow_statement(htsc_code=None, end_date=None, period=None):
    """
    :param htsc_code: 华泰证券ID
    :param end_date: 限定时间范围
    :param period: 报表类型，Q1，Q2，Q3，Q4
    :return: pandas.DataFrame
    """

    if end_date:
        if isinstance(end_date, list):
            if len(end_date) > 2:
                return "end_date format is not [start_date, end_date]"
            if len(end_date) == 1:
                end_date = [end_date[0], end_date[0]]
            if not isinstance(end_date[0], datetime) or not isinstance(end_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "end_date format is not list"

    result = get_cashflow_statement_handle(htsc_code, end_date, period)
    return result


# 财务指标
def get_fin_indicator(htsc_code=None, end_date=None, period=None):
    """
    :param htsc_code: 华泰证券ID
    :param end_date: 限定时间范围
    :param period: 报表类型，Q1，Q2，Q3，Q4
    :return: pandas.DataFrame
    """

    if end_date:
        if isinstance(end_date, list):
            if len(end_date) > 2:
                return "end_date format is not [start_date, end_date]"
            if len(end_date) == 1:
                end_date = [end_date[0], end_date[0]]
            if not isinstance(end_date[0], datetime) or not isinstance(end_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "end_date format is not list"

    result = get_fin_indicator_handle(htsc_code, end_date, period)
    return result


# 个股最新估值
def get_newest_stock_value(htsc_code=None, exchange=None):
    """
    :param htsc_code: 华泰证券ID
    :param exchange: 证券市场
    :return: pandas.DataFrame
    """

    if htsc_code:
        try:
            htsc_code_suffix = htsc_code.split('.')[-1]
            if htsc_code_suffix not in ["SH", "SZ"]:
                return 'htsc_code does not exist'
        except:
            return 'htsc_code format error'

    if exchange and exchange not in ['XSHE', 'XSHG']:
        return 'exchange does not exist'

    result = get_newest_stock_value_handle(htsc_code, exchange)
    return result


# 公司概况
def get_company_info(htsc_code=None, name=None):
    """
    :param htsc_code: 华泰证券ID
    :param name: 证券简称 与htsc_code选填一个)
    :return: pandas.DataFrame
    """

    if htsc_code and name:
        return 'htsc_code and com_name only one can be selected'

    result = get_company_info_handle(htsc_code, name)
    return result


# 股东人数
def get_shareholder_num(htsc_code=None, name=None, end_date=None):
    """
    param htsc_code: 华泰证券ID
    param name: 证券简称(和htsc_code任选其一)
    param end_date: 时间范围
    return: pandas.DataFrame
    """

    if end_date:
        if isinstance(end_date, list):
            if len(end_date) > 2:
                return "end_date format is not [start_date, end_date]"
            if len(end_date) == 1:
                end_date = [end_date[0], end_date[0]]
            if not isinstance(end_date[0], datetime) or not isinstance(end_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "end_date format is not list"

    result = get_shareholder_num_handle(htsc_code, name, end_date)
    return result


# 股票增发
def get_additional_share(htsc_code=None, listing_date=None):
    """
    :param htsc_code: 华泰证券ID
    :param listing_date: 上市日期范围
    :return: pandas.DataFrame
    """

    if listing_date:
        if isinstance(listing_date, list):
            if len(listing_date) > 2:
                return "listing_date format is not [start_date, end_date]"
            if len(listing_date) == 1:
                listing_date = [listing_date[0], listing_date[0]]
            if not isinstance(listing_date[0], datetime) or not isinstance(listing_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "listing_date format is not list"

    result = get_additional_share_handle(htsc_code, listing_date)
    return result


# 股票配售
def get_allotment_share(htsc_code=None, ini_pub_date=None, is_allot_half_year=None):
    """
    :param htsc_code: 华泰证券ID
    :param ini_pub_date: 首次公告日期范围
    :param is_allot_half_year: 半年内是否有配股事件
    :return: pandas.DataFrame
    """

    if ini_pub_date:
        if isinstance(ini_pub_date, list):
            if len(ini_pub_date) > 2:
                return "ini_pub_date format is not [start_date, end_date]"
            if len(ini_pub_date) == 1:
                ini_pub_date = [ini_pub_date[0], ini_pub_date[0]]
            if not isinstance(ini_pub_date[0], datetime) or not isinstance(ini_pub_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "Ini_pub_date format is not list"

    result = get_allotment_share_handle(htsc_code, ini_pub_date, is_allot_half_year)
    return result


# 股本结构
def get_capital_structure(htsc_code=None, end_date=None):
    """
    :param htsc_code: 华泰证券ID
    :param end_date: 到期日期范围
    :return: pandas.DataFrame
    """

    if end_date:
        if isinstance(end_date, list):
            if len(end_date) > 2:
                return "end_date format is not [start_date, end_date]"
            if len(end_date) == 1:
                end_date = [end_date[0], end_date[0]]
            if not isinstance(end_date[0], datetime) or not isinstance(end_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "end_date format is not list"

    result = get_capital_structure_handle(htsc_code, end_date)
    return result


# 股票分红
def get_dividend(htsc_code=None, right_reg_date=None, ex_divi_date=None, divi_pay_date=None):
    """
    :param htsc_code: 华泰证券ID
    :param right_reg_date: 股权登记日范围
    :param ex_divi_date:  除息日范围
    :param divi_pay_date: 现金红利发放日范围
    :return: pandas.DataFrame
    """

    if right_reg_date:
        if isinstance(right_reg_date, list):
            if len(right_reg_date) > 2:
                return "right_reg_date format is not [start_date, end_date]"
            if len(right_reg_date) == 1:
                right_reg_date = [right_reg_date[0], right_reg_date[0]]
            if not isinstance(right_reg_date[0], datetime) or not isinstance(right_reg_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "right_reg_date format is not list"

    if ex_divi_date:
        if isinstance(ex_divi_date, list):
            if len(ex_divi_date) > 2:
                return "listing_date format is not [start_date, end_date]"
            if len(ex_divi_date) == 1:
                ex_divi_date = [ex_divi_date[0], ex_divi_date[0]]
            if not isinstance(ex_divi_date[0], datetime) or not isinstance(ex_divi_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "ex_divi_date format is not list"

    if divi_pay_date:
        if isinstance(divi_pay_date, list):
            if len(divi_pay_date) > 2:
                return "divi_pay_date format is not [start_date, end_date]"
            if len(divi_pay_date) == 1:
                divi_pay_date = [divi_pay_date[0], divi_pay_date[0]]
            if not isinstance(divi_pay_date[0], datetime) or not isinstance(divi_pay_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "divi_pay_date format is not list"

    result = get_dividend_handle(htsc_code, right_reg_date, ex_divi_date, divi_pay_date)
    return result


# 沪深港通持股记录
def get_north_bound(htsc_code=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID
    :param trading_day: 时间范围
    :return: pandas.DataFrame
    """

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    result = get_north_bound_handle(htsc_code, trading_day)
    return result


# 融资融券列表
def get_margin_target(htsc_code=None, exchange=None):
    """
    :param htsc_code: 华泰证券ID
    :param exchange: 交易市场
    :return: pandas.DataFrame
    """

    result = get_margin_target_handle(htsc_code, exchange)
    return result


# 融资融券交易汇总
def get_margin_summary(htsc_code=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID
    :param trading_day: 时间范围
    :return: pandas.DataFrame
    """

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    result = get_margin_summary_handle(htsc_code, trading_day)
    return result


# 融资融券交易明细
def get_margin_detail(exchange=None, trading_day=None):
    """
    :param exchange: 交易市场，101 上海证券交易所 105 深圳证券交易所
    :param trading_day: 时间范围
    :return: pandas.DataFrame
    """

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    result = get_margin_detail_handle(exchange, trading_day)
    return result


# 十大股东
def get_shareholders_top10(htsc_code=None, change_date=None):
    """
    :param htsc_code: 华泰证券ID
    :param change_date: 变动时间范围
    :return: pandas.DataFrame
    """

    if change_date:
        if isinstance(change_date, list):
            if len(change_date) > 2:
                return "change_date format is not [start_date, end_date]"
            if len(change_date) == 1:
                change_date = [change_date[0], change_date[0]]
            if not isinstance(change_date[0], datetime) or not isinstance(change_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "change_date format is not list"

    result = get_shareholders_top10_handle(htsc_code, change_date)
    return result


# 十大流通股东
def get_shareholders_floating_top10(htsc_code=None, change_date=None):
    """
    :param htsc_code: 华泰证券ID
    :param change_date: 变动时间范围
    :return: pandas.DataFrame
    """

    if change_date:
        if isinstance(change_date, list):
            if len(change_date) > 2:
                return "change_date format is not [start_date, end_date]"
            if len(change_date) == 1:
                change_date = [change_date[0], change_date[0]]
            if not isinstance(change_date[0], datetime) or not isinstance(change_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "change_date format is not list"

    result = get_shareholders_floating_top10_handle(htsc_code, change_date)
    return result


# tick数据
def get_tick(htsc_code=None, security_type=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID（沪深市场）
    :param trading_day: 时间范围
    :param security_type: 证券类型（stock,index,fund,bond,option）
    :return: pandas.DataFrame
    """

    if not all([htsc_code, security_type]):
        return 'htsc_code or security_type is null'

    if not trading_day:
        trading_day = [datetime.today()]

    try:
        suffix = htsc_code.split('.')[-1]
        if suffix not in ['SH', 'SZ']:
            return 'htsc_code does not support'

        if security_type not in ['stock', 'index', 'bond', 'fund', 'option']:
            return 'security_type does not support'

    except:
        return 'htsc_code or security_type format error'

    if isinstance(trading_day, list):
        if len(trading_day) > 2:
            return "trading_day format is not [start_date, end_date]"
        if len(trading_day) == 1:
            trading_day = [trading_day[0], trading_day[0]]
        if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
            return "start_date,end_date format is not datetime"
    else:
        return "trading_day format is not list"

    result = get_tick_handle(htsc_code, security_type, trading_day)
    return result


# 复权因子
def get_adj_factor(htsc_code=None, begin_date=None):
    """
    :param htsc_code: 华泰证券ID
    :param begin_date: 时间范围
    :return: pandas.DataFrame
    """

    if begin_date:
        if isinstance(begin_date, list):
            if len(begin_date) > 2:
                return "begin_date format is not [start_date, end_date]"
            if len(begin_date) == 1:
                begin_date = [begin_date[0], begin_date[0]]
            if not isinstance(begin_date[0], datetime) or not isinstance(begin_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "begin_date format is not list"

    result = get_adj_factor_handle(htsc_code, begin_date)
    return result


# 限售股解禁
def get_locked_shares(htsc_code=None, listing_date=None):
    """
    :param htsc_code: 华泰证券ID
    :param listing_date: 时间范围
    :return: pandas.DataFrame
    """

    if listing_date:
        if isinstance(listing_date, list):
            if len(listing_date) > 2:
                return "listing_date format is not [start_date, end_date]"
            if len(listing_date) == 1:
                listing_date = [listing_date[0], listing_date[0]]
            if not isinstance(listing_date[0], datetime) or not isinstance(listing_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "listing_date format is not list"

    result = get_locked_shares_handle(htsc_code, listing_date)
    return result


# 股权质押
def get_frozen_shares(htsc_code=None, freezing_start_date=None):
    """
    :param htsc_code: 华泰证券ID
    :param freezing_start_date: 冻结起始日范围
    :return: pandas.DataFrame
    """

    if freezing_start_date:
        if isinstance(freezing_start_date, list):
            if len(freezing_start_date) > 2:
                return "freezing_start_date format is not [start_date, end_date]"
            if len(freezing_start_date) == 1:
                freezing_start_date = [freezing_start_date[0], freezing_start_date[0]]
            if not isinstance(freezing_start_date[0], datetime) or not isinstance(freezing_start_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "freezing_start_date format is not list"

    result = get_frozen_shares_handle(htsc_code, freezing_start_date)
    return result


# 港股行业分类-按证券ID查询
def get_hk_industry(htsc_code=None):
    """
    :param htsc_code: 华泰证券代码
    :return: pandas.DataFrame
    """

    if not htsc_code:
        return 'htsc_code is null or empty'

    if not isinstance(htsc_code, str):
        return 'htsc_code format error'

    result = get_hk_industry_handle(htsc_code)
    return result


# 港股行业分类-按行业代码查询
def get_hk_industry_stocks(industry_code=None):
    """
    :param industry_code: 行业代码
    :return: pandas.DataFrame
    """

    if not industry_code:
        return 'industry_code is null or empty'

    if not isinstance(industry_code, str):
        return 'industry_code format error'

    result = get_hk_industry_stocks_handle(industry_code)
    return result


# 港股交易日行情
def get_hk_daily_basic(htsc_code=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID
    :param trading_day: 查询时间范围
    :return: pandas.DataFrame
    """

    if htsc_code and not isinstance(htsc_code, str):
        return 'htsc_code format is not str'

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    result = get_hk_daily_basic_handle(htsc_code, trading_day)
    return result


# 港股估值
def get_hk_stock_valuation(htsc_code=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID
    :param trading_day: 查询时间范围
    :return: pandas.DataFrame
    """

    if htsc_code and not isinstance(htsc_code, str):
        return 'htsc_code format is not str'

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    result = get_hk_stock_valuation_handle(htsc_code, trading_day)
    return result


# 港股基本信息
def get_hk_stock_basic_info(htsc_code=None, listing_date=None, listing_state=None):
    """
    :param htsc_code: 华泰证券代码 字符串类型
    :param listing_date: 上市时间范围，列表类型，datetime格式 [start_date, end_date]
    :param listing_state: 上市状态: 未上市/上市/退市
    :return: pandas.DataFrame
    """

    if htsc_code and not isinstance(htsc_code, str):
        return 'htsc_code format is not str'

    if listing_date:
        if isinstance(listing_date, list):
            if len(listing_date) > 2:
                return "listing_date format is not [start_date, end_date]"
            if len(listing_date) == 1:
                listing_date = [listing_date[0], listing_date[0]]
            if not isinstance(listing_date[0], datetime) or not isinstance(listing_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "listing_date format is not list"

    if listing_state and listing_state not in ["未上市", "上市", "退市"]:
        return "listing_state error"

    result = get_hk_stock_basic_info_handle(htsc_code, listing_date, listing_state)
    return result


# 个股主营产品
def get_main_product_info(htsc_code=None, product_code=None, product_level=None):
    """
    :param htsc_code: 华泰证券ID
    :param product_code: 产品编码
    :param product_level: 主营产品层级
    :return: pandas.DataFrame
    """

    if htsc_code and not isinstance(htsc_code, str):
        return 'htsc_code format error'

    if product_code and not isinstance(product_code, str):
        return 'product_code format error'

    if product_level and not isinstance(product_level, str):
        return 'product_level format error'

    result = get_main_product_info_handle(htsc_code, product_code, product_level)
    return result


# 华泰融券通
def get_htsc_margin_target():
    """
    :return: pandas.DataFrame
    """

    result = get_htsc_margin_target_handle()
    return result


# 融券通行情-ID查询
def get_htsc_margin_by_id(htsc_code=None, data_type=None):
    """
    :param htsc_code: 华泰证券ID, 支持多ID查询, 必填
    :param data_type: 数据类型,必填   security_lending 融券通行情,
                                    security_lending_estimation 长期限券行情,
                                    security_lending_statistics 融券通日行情,
                                    security_lending_indicative_quote 融券通浏览行情数据
    :return: pandas.DataFrame
    """

    if not htsc_code:
        return 'htsc_code cannot be null or empty'

    if not isinstance(htsc_code, (list, str)):
        return 'htsc_code format error'

    if data_type not in ['security_lending', 'security_lending_estimation', 'security_lending_statistics',
                         'security_lending_indicative_quote']:
        return 'data_type error'

    result = get_htsc_margin_by_id_handle(htsc_code, data_type)
    return result


# 融券通行情-类型查询
def get_htsc_margin_by_type(data_type=None, security_type=None):
    """
    :param data_type: 数据类型,必填   security_lending 融券通行情,
                                    security_lending_estimation 长期限券行情,
                                    security_lending_statistics 融券通日行情,
                                    security_lending_indicative_quote 融券通浏览行情数据
    :param security_type: 证券类型, 股票stock, 基金fund, 必填
    :return: pandas.DataFrame
    """

    if data_type not in ['security_lending', 'security_lending_estimation', 'security_lending_statistics',
                         'security_lending_indicative_quote']:
        return 'data_type error'

    if security_type not in ['stock', 'fund']:
        return 'security_type error'

    result = get_htsc_margin_by_type_handle(data_type, security_type)
    return result


# 指数基本信息-ID查询
def get_index_info(htsc_code=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID
    :param trading_day: 交易日，datetime类型
    :return: pandas.DataFrame
    """

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    result = get_index_info_handle(htsc_code=htsc_code, trading_day=trading_day)
    return result


# 指数基本信息-市场查询
def get_all_index(exchange=None, trading_day=None):
    """
    :param exchange: 交易市场
    :param trading_day: 交易日，datetime类型
    :return: pandas.DataFrame
    """

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    result = get_all_index_handle(exchange=exchange, trading_day=trading_day)
    return result


# 指数成分股
def get_index_component(htsc_code=None, name=None, stock_code=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID
    :param name: 指数简称
    :param stock_code: 成分股代码
    :param trading_day: 交易日，datetime类型
    :return: pandas.DataFrame
    """

    if trading_day and not isinstance(trading_day, datetime):
        return "trading_day format is not datetime"

    result = get_index_component_handle(htsc_code, name, stock_code, trading_day)
    return result


# 指数成分股详细数据
def get_index_component_pro(htsc_code=None, name=None, stock_code=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID
    :param name: 指数简称
    :param stock_code: 成分股代码
    :param trading_day: 交易日，datetime类型
    :return: pandas.DataFrame
    """

    if trading_day and not isinstance(trading_day, datetime):
        return "trading_day format is not datetime"

    result = get_index_component_pro_handle(htsc_code, name, stock_code, trading_day)
    return result


# 量化因子
def get_factors(htsc_code=None, factor_name=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID
    :param factor_name: 因子名
    :param trading_day: 时间范围
    :return: pandas.DataFrame
    """

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    result = get_factors_handle(htsc_code, factor_name, trading_day)
    return result


# 基金交易状态
def get_fund_info(htsc_code=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID
    :param trading_day: 时间范围
    :return: pandas.DataFrame
    """

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    result = get_fund_info_handle(htsc_code, trading_day)
    return result


# 基金衍生数据
def get_fund_target(htsc_code=None, exchange=None, end_date=None):
    """
    :param htsc_code: 华泰证券ID
    :param exchange: 交易市场，101：上海证券交易所 105：深圳证券交易所 999：其他
    :param end_date: 截止日期
    :return: pandas.DataFrame
    """

    if end_date:
        if isinstance(end_date, list):
            if len(end_date) > 2:
                return "end_date format is not [start_date, end_date]"
            if len(end_date) == 1:
                end_date = [end_date[0], end_date[0]]
            if not isinstance(end_date[0], datetime) or not isinstance(end_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "end_date format is not list"

    result = get_fund_target_handle(htsc_code, exchange, end_date)
    return result


# ETF申赎成份券汇总表
def get_etf_component(htsc_code=None, pub_date=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID
    :param pub_date: 公告日期范围
    :param trading_day: 交易日期范围
    :return: pandas.DataFrame
    """

    if pub_date:
        if isinstance(pub_date, list):
            if len(pub_date) > 2:
                return "pub_date format is not [start_date, end_date]"
            if len(pub_date) == 1:
                pub_date = [pub_date[0], pub_date[0]]
            if not isinstance(pub_date[0], datetime) or not isinstance(pub_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "pub_date format is not list"

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    result = get_etf_component_handle(htsc_code, pub_date, trading_day)
    return result


# 个股公募持仓
def get_public_fund_portfolio(htsc_code=None, name=None, exchange=None, end_date=None):
    """
    :param htsc_code: 华泰证券ID
    :param name: 证券简称
    :param exchange: 交易市场:
                    XSHG	上海证券交易所
                    XSHE	深圳证券交易所
                    XBSE    北京证券交易所
                    NEEQ	三板交易市场
                    XHKG	香港联合交易所
    :param end_date: 期末日期范围
    :return: pandas.DataFrame
    """

    if end_date:
        if isinstance(end_date, list):
            if len(end_date) > 2:
                return "end_date format is not [start_date, end_date]"
            if len(end_date) == 1:
                end_date = [end_date[0], end_date[0]]
            if not isinstance(end_date[0], datetime) or not isinstance(end_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "end_date format is not list"

    result = get_public_fund_portfolio_handle(htsc_code, name, exchange, end_date)
    return result


# ETF申购赎回清单
def get_etf_redemption(htsc_code=None, exchange=None, trading_day=None):
    """
    :param htsc_code: 华泰证券ID
    :param exchange: 交易市场，101：上海证券交易所 105：深圳证券交易所
    :param trading_day: 交易日期范围
    :return: pandas.DataFrame
    """

    if trading_day:
        if isinstance(trading_day, list):
            if len(trading_day) > 2:
                return "trading_day format is not [start_date, end_date]"
            if len(trading_day) == 1:
                trading_day = [trading_day[0], trading_day[0]]
            if not isinstance(trading_day[0], datetime) or not isinstance(trading_day[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "trading_day format is not list"

    result = get_etf_redemption_handle(htsc_code, exchange, trading_day)
    return result


# 静态信息-按标的查询
def get_basic_info(htsc_code=None):
    """
    :param htsc_code: 华泰证券ID,入参为list或者string
    """

    if not htsc_code:
        return 'htsc_code is empty'

    if not isinstance(htsc_code, (str, list)):
        return 'htsc_code format error'

    result = get_basic_info_handle(htsc_code)
    return result


# 静态信息-按证券类型和市场查询
def get_all_basic_info(security_type=None, exchange=None, today=True):
    """
    :param security_type: 证券类型
    :param exchange: 证券市场，支持多市场查询
    :param today: 是否查询当天最新数据，布尔类型，默认True
    :return: pandas.DataFrame
    """

    if security_type:
        if security_type not in ['index', 'stock', 'fund', 'bond', 'option', 'future', 'spfuture', 'warrant', 'rate', 'spot']:
            return 'security_type dose not exist'
    else:
        return 'security_type is null'

    if not exchange:
        return 'exchange is null'

    if not isinstance(exchange, (str, list)):
        return 'exchange format error'

    if not isinstance(today, bool):
        return 'today format error'

    result = get_all_basic_info_handle(security_type, exchange, today)
    return result


# 资讯数据查询
def get_news(htsc_code=None, event_ids=None, pub_date=None):
    """
    :param htsc_code: 华泰证券ID,入参为list或者string
    :param event_ids: 事件ID,入参为list或者string
    :param pub_date: 公告日期范围
    :return: pandas.DataFrame
    """

    if htsc_code and not isinstance(htsc_code, (list, str)):
        return 'htsc_code format error'

    if event_ids and not isinstance(event_ids, (list, str)):
        return 'event_ids format error'

    if pub_date:
        if isinstance(pub_date, list):
            if len(pub_date) > 2:
                return "pub_date format is not [start_date, end_date]"
            if len(pub_date) == 1:
                pub_date = [pub_date[0], pub_date[0]]
            if not isinstance(pub_date[0], datetime) or not isinstance(pub_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "pub_date format is not list"

    result = get_news_handle(htsc_code, event_ids, pub_date)
    return result


# EDB基本信息
def find_edb_index(name=None):
    """
    :param name: 指标名称
    :return: pandas.DataFrame
    """

    if name and not isinstance(name, str):
        return 'name format error'

    result = find_edb_index_handle(name)
    return result


# EDB数据
def edb(indexes=None, pub_date=None):
    """
    :param indexes: 指标id
    :param pub_date: 发布日期
    :return: pandas.DataFrame
    """

    if indexes and not isinstance(indexes, list):
        return 'indexes format error'

    if pub_date:
        if isinstance(pub_date, list):
            if len(pub_date) > 2:
                return "pub_date format is not [start_date, end_date]"
            if len(pub_date) == 1:
                pub_date = [pub_date[0], pub_date[0]]
            if not isinstance(pub_date[0], datetime) or not isinstance(pub_date[1], datetime):
                return "start_date,end_date format is not datetime"
        else:
            return "pub_date format is not list"

    result = edb_handle(indexes, pub_date)
    return result


# 华泰研报基本信息表
def get_rpt_basicinfo_ht(id=None, report_code=None, time=None, title=None, language=None, is_valid=None):
    """
    :param id: 主键
    :param report_code: 研究报告编码
    :param time: 撰写日期范围，list类型，开始结束时间为datetime
    :param title: 标题
    :param language: 语言种类代码(1-中文,2-英文)
    :param is_valid: 是否有效(0-否1-是)
    :return: pandas.DataFrame
    """

    if id and not isinstance(id, str):
        return 'id format must be string'

    if report_code and not isinstance(report_code, str):
        return 'report_code format must be string'

    if title and not isinstance(title, str):
        return 'title format must be string'

    if language and language not in ['1', '2']:
        return 'language format error'

    if is_valid and is_valid not in ['0', '1']:
        return 'is_valid format error'

    if time:
        if isinstance(time, list):
            if len(time) == 2 and isinstance(time[0], datetime) and isinstance(time[1], datetime):
                time = [time[0], time[1] + timedelta(days=1)]
            elif len(time) == 1 and isinstance(time[0], datetime):
                time = [time[0], time[0] + timedelta(days=1)]
            else:
                return "[start_data, end_date] format error"
        else:
            return "time format is not list"

    result = get_rpt_basicinfo_ht_handle(id, report_code, time, title, language, is_valid)
    return result


# 研报股票表
def get_rpt_stk_ht(report_code=None):
    """
    :param report_code: 研究报告编码
    :return: pandas.DataFrame
    """

    if report_code and not isinstance(report_code, str):
        return 'report_code format must be string'

    result = get_rpt_stk_ht_handle(report_code)
    return result


# 研报行业表
def get_rpt_industry_ht(report_code=None):
    """
    :param report_code: 研究报告编码
    :return: pandas.DataFrame
    """

    if report_code and not isinstance(report_code, str):
        return 'report_code format must be string'

    result = get_rpt_industry_ht_handle(report_code)
    return result


# 研报作者表
def get_rpt_author_ht(report_code=None):
    """
    :param report_code: 研究报告编码
    :return: pandas.DataFrame
    """

    if report_code and not isinstance(report_code, str):
        return 'report_code format must be string'

    result = get_rpt_author_ht_handle(report_code)
    return result


# 研报附件表
def get_rpt_annex_ht(report_code=None):
    """
    :param report_code: 研究报告编码
    :return: pandas.DataFrame
    """

    if report_code and not isinstance(report_code, str):
        return 'report_code format must be string'

    result = get_rpt_annex_ht_handle(report_code)
    return result


# 研报盈利预测表
def get_rpt_stkpredict_ht(report_code=None):
    """
    :param report_code: 研究报告编码
    :return: pandas.DataFrame
    """

    if report_code and not isinstance(report_code, str):
        return 'report_code format must be string'

    result = get_rpt_stkpredict_ht_handle(report_code)
    return result


# 查询指定证券的ETF的基础信息
def get_etf_info(query):
    """
    :param query: 交易市场及对应的证券类型，元组类型，支持多市场多交易类型订阅，list类型 [(exchange1,security_type1),(exchange2,security_type2)]
    """

    exchange_map = {'XSHG': 101, 'XSHE': 102}
    security_type_map = {'fund': 3}

    marketdatatype_list = []

    for marketdatatype in query:
        try:
            exchange = exchange_map[marketdatatype[0]]
            security_type = security_type_map[marketdatatype[1]]
            marketdatatype_list.append(
                {'ESecurityIDSource': exchange, 'ESecurityType': security_type})
        except:
            return "Input parameter error:'query'"

    security_id_list = []  # 置空表示不额外查询某些标的
    data_handle.get_interface().queryETFInfoCallback(marketdatatype_list, security_id_list)


# 查询历史上所有的指定证券的基础信息 -- 在data_handle.py 数据回调接口OnMarketData()中marketdata.marketDataType = MD_CONSTANT
# params:securityIdSource 为市场ESecurityIDSource 枚举值;securityType 为 ESecurityType枚举值
def query_mdcontant(security_idsource_and_types,security_id_list):


    # ecurity_idsource_and_types = [{'ESecurityIDSource': 102, 'ESecurityType': 3},{'ESecurityIDSource': 102, 'ESecurityType': 2}]
    # ecurity_idsource_and_types = [('XSHG', 'fund'),('XSHE','stock')]
    all_security_idsource_and_types = []
    for market_datatype in security_idsource_and_types:
        market = market_datatype[0]
        securityType = market_datatype[1]
        
        all_security_idsource_and_types.extend([{'ESecurityIDSource': EnumeratedMapping.exchange_num([market]).get(market),'ESecurityType': EnumeratedMapping.security_type_num([securityType]).get(securityType)}])
    print(all_security_idsource_and_types)
 
    data_handle.get_interface().queryMdContantCallback(all_security_idsource_and_types, security_id_list)
#
#
# # 查询今日最新的指定证券的基础信息 -- 在data_handle.py 数据回调接口OnMarketData()中marketdata.marketDataType = MD_CONSTANT
# # params:securityIdSource 为市场ESecurityIDSource 枚举值;securityType 为 ESecurityType枚举值
# def query_last_mdcontant(security_idsource_and_types, security_id_list):
#     # 按市场查询
#     # 沪市 股票
#     data_handle.get_interface().queryLastMdContantCallback(security_idsource_and_types, security_id_list)
#
#
# # 查询指定证券的ETF的基础信息 -- 在data_handle.py 数据回调接口OnMarketData()中marketdata.marketDataType = MD_ETF_BASICINFO
# # params:securityIdSource 为市场ESecurityIDSource 枚举值;securityType 为 ESecurityType枚举值
# def query_ETFinfo(securityIDSource, securityType):  # 查询指定证券的ETF的基础信息
#     # params:securityIDSource 为 ESecurityIDSource枚举值
#     # params:securityType 为 ESecurityType枚举值
#     security_idsource_and_types = []
#     # 沪市 股票
#     idsource_and_type = {"ESecurityIDSource": securityIDSource, "ESecurityType": securityType}
#     security_idsource_and_types.append(idsource_and_type)
#
#     # securityIDSourceAndTypes 与 securityIdList并集
#     security_id_list = []  # 置空表示不额外查询某些标的
#     # params:security_id_list 为 标的集合
#     data_handle.get_interface().queryETFInfoCallback(security_idsource_and_types, security_id_list)
