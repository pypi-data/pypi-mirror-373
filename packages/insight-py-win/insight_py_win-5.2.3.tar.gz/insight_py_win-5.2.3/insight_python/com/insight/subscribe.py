#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time

from .. import data_handle
from ..interface.mdc_gateway_base_define import SyncWait
from ..interface.mdc_enumerated_mapping_table import EnumeratedMapping


def subscribe_tick_by_id(htsc_code, mode='coverage'):
    '''
    :param htsc_code: 华泰证券ID，支持多ID查询，string或list类型
    :param mode: 订阅方式 覆盖(coverage)， 新增（add）， 减少(decrease)， 取消(cancel)， 默认为coverage
    '''

    mode_map = {"coverage": 1, "add": 2, "decrease": 3, "cancel": 4}
    exchange_suffix_list = list(EnumeratedMapping.exchange_suffix_map(
        ['XSHG', 'XSHE', 'CSI', 'CNI', 'XBSE', 'HKSC', 'XSGE', 'XDCE', 'XZCE', 'CCFX', 'HTIS', 'XHKG', 'NASDAQ', 'ICE',
         'CME', 'CBOT', 'COMEX', 'NYMEX', 'LME', 'SGX', 'LSE', 'BBG', 'SGEX']).values())

    if not htsc_code:
        print('htsc_code can not be empty')
        return False

    if isinstance(htsc_code, str):
        htsc_code = [htsc_code]

    if isinstance(htsc_code, list) and isinstance(mode, str):
        htsc_codes_list = []
        for code in htsc_code:
            try:
                suffix = code.split(".")[-1]
                if suffix in exchange_suffix_list:
                    htsc_codes_list.append({'HTSCSecurityID': code, 'EMarketDataType': 1})
                else:
                    print('htsc_code {} does not support'.format(code))
                    return False
            except:
                print('htsc_code {} format error'.format(code))
                return False

        datatype = mode_map.get(mode)
        if datatype:
            data_handle.get_interface().subscribebyid(datatype, htsc_codes_list)
            time.sleep(SyncWait.wait_time)
        else:
            print("mode dose not exist")
    else:
        print("query or mode format error")


def subscribe_tick_by_type(query=None, mode='coverage'):
    '''
    :param query: 交易市场及对应的证券类型，元组类型，支持多市场多交易类型订阅，list类型 [(exchange1,security_type1),(exchange2,security_type2)]
    :param mode: 订阅方式 覆盖(coverage)， 新增（add）， 减少(decrease)， 取消(cancel)， 默认为coverage
    '''

    mode_map = {"coverage": 1, "add": 2, "decrease": 3, "cancel": 4}

    exchange_code_map = EnumeratedMapping.exchange_num(
        ['XSHG', 'XSHE', 'CSI', 'CNI', 'XBSE', 'HKSC', 'XSGE', 'XDCE', 'XZCE', 'CCFX', 'HTIS', 'XHKG', 'NASDAQ', 'ICE',
         'CME', 'CBOT', 'COMEX', 'NYMEX', 'LME', 'SGX', 'LSE', 'SGEX'])

    security_type_num_map = EnumeratedMapping.security_type_num(
        ['index', 'stock', 'fund', 'bond', 'option', 'future', 'spfuture', 'warrant', 'rate', 'spot'])

    if not query:
        print('query can not be empty')
        return False

    if isinstance(query, list) and isinstance(mode, str):

        marketdatatype_list = []

        for marketdatatype in query:
            if isinstance(marketdatatype, tuple) and len(marketdatatype) == 2:
                try:
                    exchange = exchange_code_map[marketdatatype[0]]
                    security_type = security_type_num_map[marketdatatype[1]]
                    marketdatatype_list.append(
                        {'ESecurityIDSource': exchange, 'ESecurityType': security_type, 'EMarketDataType': 1})
                except:
                    print("exchange or security_type dose not exist")
                    return False

        datatype = mode_map.get(mode)
        if datatype:
            data_handle.get_interface().subscribebytype(datatype, marketdatatype_list)
            time.sleep(SyncWait.wait_time)
        else:
            print("mode dose not exist")
    else:
        print("query or mode format error")


def subscribe_kline_by_id(htsc_code=None, frequency=None, mode='coverage'):
    '''
    :param htsc_code: 华泰证券ID，支持多ID查询，string或list类型
    :param mode: 订阅方式 覆盖(coverage)， 新增（add）， 减少(decrease)， 取消(cancel)， 默认为coverage
    :param frequency: 频率，list类型，秒K（15s），分钟K（‘1min’）
    '''

    frequency_map = {'15s': 26, '1min': 20}
    mode_map = {"coverage": 1, "add": 2, "decrease": 3, "cancel": 4}
    exchange_suffix_list = list(EnumeratedMapping.exchange_suffix_map(
        ['XSHG', 'XSHE', 'CSI', 'CNI', 'XBSE', 'HKSC', 'HGHQ', 'CCFX', 'XSGE', 'XDCE', 'XZCE', 'XHKG', 'SGEX']).values())

    if not frequency:
        frequency = ["1min"]

    if not htsc_code:
        print('htsc_code can not be empty')
        return False

    if isinstance(htsc_code, str):
        htsc_code = [htsc_code]

    if isinstance(htsc_code, list) and isinstance(frequency, list) and isinstance(mode, str):

        htsc_codes_list = []

        for fq in frequency:
            fq_code = frequency_map.get(fq)
            if fq_code:
                for code in htsc_code:
                    try:
                        suffix = code.split(".")[-1]
                        if suffix in exchange_suffix_list:
                            htsc_codes_list.append({'HTSCSecurityID': code, 'EMarketDataType': fq_code})
                        else:
                            print('htsc_code {} does not support'.format(code))
                            return False
                    except:
                        print('htsc_code {} format error'.format(code))
                        return False
            else:
                print(f"fq {fq} dose not exist")
                return False

        datatype = mode_map.get(mode)
        if datatype:
            data_handle.get_interface().subscribebyid(datatype, htsc_codes_list)
            time.sleep(SyncWait.wait_time)
        else:
            print("mode dose not exist")
    else:
        print("query or mode format error")


def subscribe_kline_by_type(query=None, frequency=None, mode='coverage'):
    '''
    :param query: 交易市场及对应的证券类型，元组类型，支持多市场多交易类型订阅，list类型 [(exchange1,security_type1),(exchange2,security_type2)]
    :param mode: 订阅方式  覆盖(coverage)， 新增（add）， 减少(decrease)， 取消(cancel)， 默认为coverage
    :param frequency: 频率，list类型，秒K（15s），分钟K（‘1min’）
    '''

    mode_map = {"coverage": 1, "add": 2, "decrease": 3, "cancel": 4}
    frequency_map = {'15s': 26, '1min': 20}
    exchange_map = EnumeratedMapping.exchange_num(
        ['XSHG', 'XSHE', 'CSI', 'CNI', 'XBSE', 'HKSC', 'HGHQ', 'CCFX', 'XSGE', 'XDCE', 'XZCE', 'XHKG', 'SGEX'])
    security_type_map = EnumeratedMapping.security_type_num(['index', 'stock', 'fund', 'bond', 'option', 'future', 'spot'])

    if not frequency:
        frequency = ["1min"]

    if not query:
        print('query can not be empty')
        return False

    if isinstance(query, list) and isinstance(frequency, list) and isinstance(mode, str):

        marketdatatype_list = []

        for fq in frequency:
            fq_code = frequency_map.get(fq)
            if fq_code:
                for marketdatatype in query:
                    if isinstance(marketdatatype, tuple) and len(marketdatatype) == 2:
                        try:
                            exchange = exchange_map[marketdatatype[0]]
                            security_type = security_type_map[marketdatatype[1]]
                            marketdatatype_list.append(
                                {'ESecurityIDSource': exchange, 'ESecurityType': security_type,
                                 'EMarketDataType': fq_code})
                        except:
                            print("exchange or security_type dose not exist")
                            return False
            else:
                print(f"{fq} dose not exist")
                return False

        datatype = mode_map.get(mode)
        if datatype:
            data_handle.get_interface().subscribebytype(datatype, marketdatatype_list)
            time.sleep(SyncWait.wait_time)
        else:
            print("mode dose not exist")
    else:
        print("query or mode format error")


def subscribe_trans_and_order_by_id(htsc_code=None, mode='coverage'):
    '''
    :param htsc_code: 华泰证券ID，支持多ID查询，string或list类型
    :param mode: 订阅方式
    '''

    mode_map = {"coverage": 1, "add": 2, "decrease": 3, "cancel": 4}
    exchange_suffix_list = list(EnumeratedMapping.exchange_suffix_map(['XSHG', 'XSHE', 'XHKG']).values())

    if not htsc_code:
        print('htsc_code can not be empty')
        return False

    if isinstance(htsc_code, str):
        htsc_code = [htsc_code]

    if isinstance(htsc_code, list) and isinstance(mode, str):
        htsc_codes_list = []
        for code in htsc_code:
            try:
                suffix = code.split(".")[-1]
                if suffix in exchange_suffix_list:
                    htsc_codes_list.append({'HTSCSecurityID': code, 'EMarketDataType': 3})
                    htsc_codes_list.append({'HTSCSecurityID': code, 'EMarketDataType': 2})
                else:
                    print('htsc_code {} does not support'.format(code))
                    return False
            except:
                print('htsc_code {} format error'.format(code))
                return False

        datatype = mode_map.get(mode)
        if datatype:
            data_handle.get_interface().subscribebyid(datatype, htsc_codes_list)
            time.sleep(SyncWait.wait_time)
        else:
            print("mode dose not exist")
    else:
        print("query or mode format error")


def subscribe_trans_and_order_by_type(query=None, mode='coverage'):
    '''
    :param query: 交易市场，支持多市场查询，list类型 [(exchange1,security_type1),(exchange2,security_type2)]
    :param mode: 订阅方式
    '''

    mode_map = {"coverage": 1, "add": 2, "decrease": 3, "cancel": 4}
    exchange_map = EnumeratedMapping.exchange_num(['XSHG', 'XSHE', 'XHKG'])
    security_type_map = EnumeratedMapping.security_type_num(['stock', 'fund', 'bond', 'warrant'])

    if isinstance(query, list) and isinstance(mode, str):

        marketdatatype_list = []

        for marketdatatype in query:
            if isinstance(marketdatatype, tuple) and len(marketdatatype) == 2:
                try:
                    exchange = exchange_map[marketdatatype[0]]
                    security_type = security_type_map[marketdatatype[1]]
                    marketdatatype_list.append(
                        {'ESecurityIDSource': exchange, 'ESecurityType': security_type, 'EMarketDataType': 2})
                    marketdatatype_list.append(
                        {'ESecurityIDSource': exchange, 'ESecurityType': security_type, 'EMarketDataType': 3})
                except:
                    print("exchange or security_type dose not exist")
                    return False

        datatype = mode_map.get(mode)
        if datatype:
            data_handle.get_interface().subscribebytype(datatype, marketdatatype_list)
            time.sleep(SyncWait.wait_time)
        else:
            print("mode dose not exist")
    else:
        print("query or mode format error")


def subscribe_htsc_margin_by_id(htsc_code=None, data_type=None, mode="coverage"):
    """
    :param htsc_code : 华泰证券ID，支持多ID订阅，string或list类型
    :param data_type: 数据类型,必填   security_lending 融券通行情,
                                    security_lending_estimation 长期限券行情,
                                    security_lending_statistics 融券通日行情,
                                    security_lending_indicative_quote 融券通浏览行情数据
    :param mode: 订阅方式 覆盖(coverage)， 新增（add）， 减少(decrease)， 取消(cancel)， 默认为coverage
    """

    mode_map = {"coverage": 1, "add": 2, "decrease": 3, "cancel": 4}
    data_type_map = {'security_lending': 59, 'security_lending_estimation': 82,
                     'security_lending_statistics': 80, 'security_lending_indicative_quote': 79}
    exchange_suffix_list = ['SH', 'SZ', 'HTSM']

    if all([htsc_code, data_type, mode]):
        if isinstance(htsc_code, str):
            htsc_code = [htsc_code]

        if isinstance(htsc_code, list) and isinstance(data_type, str) and isinstance(mode, str):

            htsc_codes_list = []

            EMarketDataType = data_type_map.get(data_type)
            if EMarketDataType:
                for code in htsc_code:
                    try:
                        suffix = code.split(".")[-1]
                        if suffix in exchange_suffix_list:
                            htsc_codes_list.append({'HTSCSecurityID': code, 'EMarketDataType': EMarketDataType})
                    except:
                        print('htsc_code {} format error'.format(code))
                        return False

                datatype = mode_map.get(mode)
                if datatype:
                    data_handle.get_interface().subscribebyid(datatype, htsc_codes_list)
                    time.sleep(SyncWait.wait_time)
                else:
                    print("mode dose not exist")

            else:
                print('data_type dose not exist')
        else:
            print("htsc_code or data_type or mode format error")
    else:
        print("htsc_code or data_type or mode is null")


def subscribe_htsc_margin_by_type(security_type=None, data_type=None, mode='coverage'):
    """
    :param security_type: 证券类型, 股票stock, 基金fund, 必填
    :param data_type: 数据类型,必填   security_lending 融券通行情,
                                    security_lending_estimation 长期限券行情,
                                    security_lending_statistics 融券通日行情,
                                    security_lending_indicative_quote 融券通浏览行情数据
    :param mode: 订阅方式 覆盖(coverage)， 新增（add）， 减少(decrease)， 取消(cancel)， 默认为coverage
    """

    mode_map = {"coverage": 1, "add": 2, "decrease": 3, "cancel": 4}
    security_type_map = {'stock': 2, 'fund': 3}
    data_type_map = {'security_lending': 59, 'security_lending_estimation': 82,
                     'security_lending_statistics': 80, 'security_lending_indicative_quote': 79}

    if all([security_type, data_type, mode]):

        if isinstance(security_type, str):
            security_type = [security_type]

        if isinstance(security_type, list) and isinstance(data_type, str) and isinstance(mode, str):

            marketdatatype_list = []

            try:
                data_type_num = data_type_map[data_type]
            except:
                print(f'{data_type} dose not exist')
                return False

            for security_type_one in security_type:

                try:
                    security_type_one_num = security_type_map[security_type_one]
                except:
                    print(f'{security_type_one} dose not exist')
                    return False

                marketdatatype_list.append(
                    {'ESecurityIDSource': 101, 'ESecurityType': security_type_one_num,
                     'EMarketDataType': data_type_num})
                marketdatatype_list.append(
                    {'ESecurityIDSource': 102, 'ESecurityType': security_type_one_num,
                     'EMarketDataType': data_type_num})
                marketdatatype_list.append(
                    {'ESecurityIDSource': 805, 'ESecurityType': security_type_one_num,
                     'EMarketDataType': data_type_num})

            datatype = mode_map.get(mode)
            if datatype:
                data_handle.get_interface().subscribebytype(datatype, marketdatatype_list)
                time.sleep(SyncWait.wait_time)
            else:
                print("mode dose not exist")

        else:
            print("security_type or data_type or format error")
    else:
        print("security_type or data_type or mode is null")


def subscribe_derived(type=None, htsc_code=None, exchange=None, frequency='1min', mode='coverage'):
    '''
    :param type: 订阅数据类型
    :param htsc_code : 华泰证券ID，支持多ID订阅，string或list类型
    :param exchange : 证券市场代码
    :param frequency: 频率
    :param mode: 订阅方式 覆盖(coverage)， 新增（add）， 减少(decrease)， 取消(cancel)， 默认为coverage
    :param additional:
    '''

    if isinstance(htsc_code, str):
        htsc_code = [htsc_code]

    if not isinstance(htsc_code, list):
        print('htsc_code format error')
        return False

    mode_map = {"coverage": 1, "add": 2, "decrease": 3, "cancel": 4}
    datatype = mode_map.get(mode)
    if not datatype:
        print("mode dose not exist")
        return False

    if type == 'north_bound':
        north_bound_htsc_code_list = ['SCHKSBSH.HT', 'SCHKSBSZ.HT', 'SCSHNBHK.HT', 'SCSZNBHK.HT']
        if htsc_code:
            sub_htsc_code_list = []
            for code in htsc_code:
                if code in north_bound_htsc_code_list:
                    sub_htsc_code_list.append(code)

            if sub_htsc_code_list:
                sub_params = []
                for sub_code in sub_htsc_code_list:
                    sub_params.append({'HTSCSecurityID': sub_code, 'EMarketDataType': 1})

                data_handle.get_interface().subscribebyid(datatype, sub_params)
                time.sleep(SyncWait.wait_time)

            else:
                print('invalid htsc_code')
                return False

        else:
            print('htsc_code can not be empty')
            return False

    else:
        print('type dose not exist')


def subscribe_news_by_type(query=None, mode='coverage'):
    """
    :param query: 交易市场，支持多市场查询，list类型 [('XSHG', 'stock'), ('XSHE', 'stock')]，仅支持沪深市场的股票查询
    :param mode: 订阅方式 覆盖(coverage)， 新增（add）， 减少(decrease)， 取消(cancel)， 默认为coverage
    """

    mode_map = {"coverage": 1, "add": 2, "decrease": 3, "cancel": 4}
    exchange_map = {'XSHG': 101, 'XSHE': 102}
    security_type_map = {'stock': 2}

    if all([query, mode]):

        if isinstance(query, list) and isinstance(mode, str):

            marketdatatype_list = []

            for marketdatatype in query:
                if isinstance(marketdatatype, tuple) and len(marketdatatype) == 2:
                    try:
                        exchange = exchange_map[marketdatatype[0]]
                        security_type = security_type_map[marketdatatype[1]]
                        marketdatatype_list.append(
                            {'ESecurityIDSource': exchange, 'ESecurityType': security_type, 'EMarketDataType': 60})
                    except:
                        print("exchange or security_type dose not exist")
                        return False

            datatype = mode_map.get(mode)
            if datatype:
                data_handle.get_interface().subscribebytype(datatype, marketdatatype_list)
                time.sleep(SyncWait.wait_time)
            else:
                print("mode dose not exist")

        else:
            print('query or mode format error')

    else:
        print("query or mode is null")


def subscribe_news_by_id(htsc_code=None, mode='coverage'):
    '''
    :param htsc_code: 华泰证券ID，支持多ID查询，string或list类型
    :param mode: 订阅方式
    '''

    mode_map = {"coverage": 1, "add": 2, "decrease": 3, "cancel": 4}
    exchange_suffix_list = ['SH', 'SZ']

    if all([htsc_code, mode]):

        if isinstance(htsc_code, str):
            htsc_code = [htsc_code]

        if isinstance(htsc_code, list) and isinstance(mode, str):

            htsc_codes_list = []
            for code in htsc_code:
                try:
                    suffix = code.split(".")[-1]
                    if suffix in exchange_suffix_list:
                        htsc_codes_list.append({'HTSCSecurityID': code, 'EMarketDataType': 60})
                    else:
                        print('htsc_code {} does not support'.format(code))
                        return False
                except:
                    print('htsc_code {} format error'.format(code))
                    return False

            datatype = mode_map.get(mode)
            if datatype:
                data_handle.get_interface().subscribebyid(datatype, htsc_codes_list)
                time.sleep(SyncWait.wait_time)
            else:
                print("mode dose not exist")

        else:
            print("query or mode format error")
    else:
        print('htsc_code or mode is null')


# 阻塞当前线程，防止本模块执行退出操作
def sync():
    # print("input any key to exit >>>")
    line = input()
    if len(str(line)) > 0:
        print("sync: input-->>" + str(line) + ",then exit this sync.")
