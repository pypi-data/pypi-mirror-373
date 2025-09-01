import traceback
from datetime import datetime
from .mdc_query_sync_mapping_table import MappingTable
from .mdc_enumerated_mapping_table import EnumeratedMapping


def subscribe_tick_handle(marketdatajson):

    tick_map_dict = MappingTable.tick_map()
    tick_map_rever = {v: k for k, v in tick_map_dict.items()}

    # 需要除的键
    divisor_list = ['max', 'min', 'prev_close', 'last', 'open', 'high', 'low', 'close', 'buy_price_queue',
                    'sell_price_queue', 'iopv', 'settle', 'pre_settle', 'reference_px', 'pre_market_last_px',
                    'change_value', 'pre_market_high_px', 'implied_sell_qty', 'after_hours_low_px', 'implied_buy_qty',
                    'after_hours_high_px', 'pre_market_low_px', 'swing', 'implied_buy_px', 'implied_sell_px',
                    'change_speed', 'change_rate', 'after_hours_last_px', 'position_trend', 'norminal_px', 'buy_px', 'sell_px']

    exchange_code_map = EnumeratedMapping.exchange_num(
        ['XSHG', 'XSHE', 'CSI', 'CNI', 'XBSE', 'HKSC', 'XSGE', 'XDCE', 'XZCE', 'CCFX', 'HTIS'])
    exchange_code_map = {v: k for k, v in exchange_code_map.items()}

    overseas_exchange_code_map = EnumeratedMapping.exchange_num(
        ['XHKG', 'NASDAQ', 'ICE', 'CME', 'CBOT', 'COMEX', 'NYMEX', 'LME', 'SGX', 'LSE', 'SGEX'])
    overseas_exchange_code_map = {v: k for k, v in overseas_exchange_code_map.items()}

    security_type_map = EnumeratedMapping.security_type_num(
        ['index', 'stock', 'fund', 'bond', 'option', 'future', 'spfuture', 'warrant', 'rate', 'spot'])
    security_type_map = {v: k for k, v in security_type_map.items()}

    try:
        data = None
        result = {}
        if "mdIndex" in marketdatajson:  # 指数

            data = marketdatajson["mdIndex"]
            result = {'htsc_code': '', 'time': '', 'exchange': '', 'security_type': '', 'prev_close': '', 'volume': '',
                      'value': '', 'last': '', 'open': '', 'high': '', 'low': '', 'close': ''}

        elif "mdStock" in marketdatajson:  # 股票

            data = marketdatajson["mdStock"]
            result = {'htsc_code': '', 'time': '', 'trading_phase_code': '', 'exchange': '', 'security_type': '',
                      'max': '', 'min': '', 'prev_close': '', 'num_trades': '', 'volume': '', 'value': '', 'last': '',
                      'open': '', 'high': '', 'low': '', 'buy_price_queue': '', 'buy_order_qty_queue': '',
                      'sell_price_queue': '', 'sell_order_qty_queue': '', 'close': ''}

        elif "mdFund" in marketdatajson:  # 基金

            data = marketdatajson["mdFund"]
            result = {'htsc_code': '', 'time': '', 'trading_phase_code': '', 'exchange': '', 'security_type': '',
                      'max': '', 'min': '', 'prev_close': '', 'num_trades': '', 'volume': '', 'value': '', 'last': '',
                      'open': '', 'high': '', 'low': '', 'iopv': '', 'buy_price_queue': '', 'buy_order_qty_queue': '',
                      'sell_price_queue': '', 'sell_order_qty_queue': '', 'close': '', 'purchase_number': '',
                      'purchase_amount': '', 'redemption_number': '', 'redemption_amount': ''}

        elif "mdBond" in marketdatajson:  # 债券

            data = marketdatajson["mdBond"]
            result = {'htsc_code': '', 'time': '', 'trading_phase_code': '', 'exchange': '', 'security_type': '',
                      'max': '', 'min': '', 'prev_close': '', 'num_trades': '', 'volume': '', 'value': '', 'last': '',
                      'open': '', 'high': '', 'low': '', 'buy_price_queue': '', 'buy_order_qty_queue': '',
                      'sell_price_queue': '', 'sell_order_qty_queue': '', 'close': ''}

        elif "mdOption" in marketdatajson:  # 期权

            data = marketdatajson["mdOption"]
            result = {'htsc_code': '', 'time': '', 'trading_phase_code': '', 'exchange': '', 'security_type': '',
                      'max': '', 'min': '', 'prev_close': '', 'num_trades': '', 'volume': '', 'value': '', 'last': '',
                      'open': '', 'high': '', 'low': '', 'pre_settle': '', 'open_interest': '', 'buy_price_queue': '',
                      'buy_order_qty_queue': '', 'sell_price_queue': '', 'sell_order_qty_queue': '', 'close': '',
                      'settle': ''}

        elif "mdFuture" in marketdatajson:  # 期货

            data = marketdatajson["mdFuture"]
            result = {'htsc_code': '', 'time': '', 'trading_phase_code': '', 'exchange': '', 'security_type': '',
                      'max': '', 'min': '', 'prev_close': '', 'volume': '', 'value': '', 'last': '', 'open': '',
                      'high': '', 'low': '', 'trading_day': '', 'pre_open_interest': '', 'pre_settle': '',
                      'open_interest': '', 'buy_price_queue': '', 'buy_order_qty_queue': '', 'sell_price_queue': '',
                      'sell_order_qty_queue': '', 'close': '', 'settle': ''}

        elif "spFuture" in marketdatajson:  # 期货组合合约

            data = marketdatajson["spFuture"]

        elif "mdRate" in marketdatajson:  # 利率

            data = marketdatajson["mdRate"]

        elif "mdWarrant" in marketdatajson:  # 权证

            data = marketdatajson["mdWarrant"]

        elif "mdSpot" in marketdatajson:  # 现货

            data = marketdatajson["mdSpot"]

        if data:

            exchange_code = data.get("securityIDSource")
            md_time = datetime.strptime(str(data['MDDate']) + f"{data['MDTime']:09d}", '%Y%m%d%H%M%S%f')
            md_time = datetime.strftime(md_time, '%Y-%m-%d %H:%M:%S.%f')
            security_type = security_type_map.get(data.get('securityType'))
            divisor = pow(10, int(data.get("DataMultiplePowerOf10")))  # 除数

            if overseas_exchange_code_map.get(exchange_code):

                exchange = overseas_exchange_code_map.get(exchange_code)

                result = {'htsc_code': '', 'time': md_time, 'exchange': exchange, 'security_type': security_type}
                for key, value in data.items():
                    new_key = tick_map_dict.get(key)
                    if new_key:
                        if isinstance(value, str):
                            result[new_key] = value
                        elif isinstance(value, int):
                            if new_key == 'trading_day':
                                result[new_key] = '{}-{}-{}'.format(str(value)[:4], str(value)[4:6], str(value)[6:])
                            else:
                                if new_key in divisor_list:
                                    value = value / divisor
                                result[new_key] = value
                        elif isinstance(value, list):
                            if new_key in divisor_list:
                                value = list(map(lambda x: x / divisor, value))
                            result[new_key] = value
                return result

            elif exchange_code_map.get(exchange_code):

                exchange = exchange_code_map.get(exchange_code)

                # 判断是否是南北向资金流向
                if data.get("HTSCSecurityID") in ['SCHKSBSH.HT', 'SCHKSBSZ.HT', 'SCSHNBHK.HT', 'SCSZNBHK.HT']:
                    name_map = {'SCHKSBSH.HT': '北向资金（香港-上海）', 'SCHKSBSZ.HT': '北向资金（香港-深圳）',
                                'SCSHNBHK.HT': '南向资金（上海-香港）', 'SCSZNBHK.HT': '南向资金（深圳-香港）'}
                    result = {'name': name_map.get(data.get("HTSCSecurityID")), 'htsc_code': '', 'time': '', 'exchange': '',
                              'security_type': '', 'value': '', 'total_buy_value_trade': '', 'total_sell_value_trade': ''}

                result['time'] = md_time
                result['exchange'] = exchange
                result['security_type'] = security_type

                for key in list(result.keys()):
                    if not result[key]:

                        value = data.get(tick_map_rever.get(key))

                        if isinstance(value, str):
                            result[key] = value

                        elif isinstance(value, int):

                            if key == 'trading_day':
                                result[key] = '{}-{}-{}'.format(str(value)[:4], str(value)[4:6], str(value)[6:])
                            else:
                                if key in divisor_list:
                                    value = value / divisor
                                result[key] = value

                        elif isinstance(value, list):
                            if key in divisor_list:
                                value = list(map(lambda x: x / divisor, value))

                            count = 1
                            key_name = ''
                            for i in value:
                                if key == 'buy_price_queue':
                                    key_name = 'bid' + str(count)
                                elif key == 'buy_order_qty_queue':
                                    key_name = 'bid_size' + str(count)
                                elif key == 'sell_price_queue':
                                    key_name = 'ask' + str(count)
                                elif key == 'sell_order_qty_queue':
                                    key_name = 'ask_size' + str(count)
                                result[key_name] = i
                                count += 1
                            del result[key]
                return result

    except Exception as e:
        traceback.print_exc()
        print(str(e))


def subscribe_kline_handle(marketdatajson):
    kline_map_dict = MappingTable.get_kline_map()
    kline_map_dict = {v: k for k, v in kline_map_dict.items()}

    exchange_code_map = EnumeratedMapping.exchange_num(
        ['XSHG', 'XSHE', 'CSI', 'CNI', 'XBSE', 'HKSC', 'CCFX', 'XSGE', 'XDCE', 'XZCE', 'XHKG', 'SGEX'])
    exchange_code_map = {v: k for k, v in exchange_code_map.items()}

    security_type_map = EnumeratedMapping.security_type_num(['index', 'stock', 'fund', 'bond', 'option', 'future', 'spot'])
    security_type_map = {v: k for k, v in security_type_map.items()}

    frequency_map = {1: "1min", 10: "15s"}

    try:
        # 需要除的键
        divisor_list = ['open', 'high', 'low', 'close', 'settle']
        if "mdKLine" in marketdatajson:
            if marketdatajson['mdKLine'].get('KLineCategory'):
                result = None
                data = marketdatajson["mdKLine"]
                security_type = security_type_map.get(data.get('securityType'))

                if data.get("securityIDSource") == 203:
                    result = {'htsc_code': '', 'time': '', 'exchange': '', 'security_type': '', 'frequency': '',
                              'open': '', 'close': '', 'high': '', 'low': '', 'num_trades': '', 'volume': '',
                              'value': '', 'open_interest': '', 'settle': ''}

                if not result and security_type in ["index", "stock", "fund", "bond"]:

                    result = {'htsc_code': '', 'time': '', 'exchange': '', 'security_type': '', 'frequency': '',
                              'open': '', 'close': '', 'high': '', 'low': '', 'volume': '', 'value': ''}

                elif not result and security_type in ['option', 'future']:

                    result = {'htsc_code': '', 'time': '', 'exchange': '', 'security_type': '', 'frequency': '',
                              'open': '', 'close': '', 'high': '', 'low': '', 'volume': '', 'value': '',
                              'open_interest': '', 'settle': ''}

                elif not result and security_type in ['spot']:
                    result = {'htsc_code': '', 'time': '', 'exchange': '', 'security_type': '', 'frequency': '',
                              'open': '', 'close': '', 'high': '', 'low': '', 'num_trades': '', 'volume': '',
                              'value': '', 'open_interest': '', 'settle': ''}

                if data and result:

                    md_time = datetime.strptime(str(data['MDDate']) + f"{data['MDTime']:09d}", '%Y%m%d%H%M%S%f')
                    md_time = datetime.strftime(md_time, '%Y-%m-%d %H:%M:%S.%f')
                    exchange = exchange_code_map.get(data.get("securityIDSource"))
                    frequency = frequency_map[data['PeriodType']]

                    result['time'] = md_time
                    result['exchange'] = exchange
                    result['security_type'] = security_type
                    result['frequency'] = frequency

                    divisor = pow(10, int(data.get("DataMultiplePowerOf10")))  # 除数

                    for key in list(result.keys()):



                        if not result[key]:
                            value = data.get(kline_map_dict.get(key))

                            if isinstance(value, str):
                                result[key] = value

                            elif isinstance(value, int):
                                if key in divisor_list:
                                    value = value / divisor
                                result[key] = value

                    return result

    except Exception as e:
        traceback.print_exc()
        print(str(e))


def subscribe_trans_and_order_handle(marketdatajson):
    columns_map = MappingTable.subscribe_trans_map()
    columns_map_rever = {v: k for k, v in columns_map.items()}
    exchange_code_map = EnumeratedMapping.exchange_num(['XSHG', 'XSHE', 'XHKG'])
    exchange_code_map = {v: k for k, v in exchange_code_map.items()}
    security_type_map = EnumeratedMapping.security_type_num(['stock', 'fund', 'bond', 'warrant'])
    security_type_map = {v: k for k, v in security_type_map.items()}

    try:
        # 需要除的键
        divisor_list = ['trade_price', 'trade_money', 'order_price']

        data = None
        data_type = None
        if "mdTransaction" in marketdatajson:
            data = marketdatajson["mdTransaction"]
            data_type = 'transaction'

        elif 'mdOrder' in marketdatajson:
            data = marketdatajson['mdOrder']
            data_type = 'order'

        if data:

            result = {}

            security_type = security_type_map.get(data.get('securityType'))
            md_time = datetime.strptime(str(data['MDDate']) + f"{data['MDTime']:09d}", '%Y%m%d%H%M%S%f')
            md_time = datetime.strftime(md_time, '%Y-%m-%d %H:%M:%S.%f')
            exchange = exchange_code_map.get(data.get("securityIDSource"))
            divisor = pow(10, int(data.get("DataMultiplePowerOf10")))  # 除数

            if data_type == 'transaction':
                if exchange == 'XHKG':
                    result = {'htsc_code': '', 'time': md_time, 'data_type': data_type, 'exchange': exchange,
                              'security_type': security_type, 'hk_trade_type': 0}
                    for key, value in data.items():
                        if columns_map.get(key):
                            if isinstance(value, str):
                                result[columns_map.get(key)] = value
                            elif isinstance(value, int):
                                if columns_map.get(key) in divisor_list:
                                    value = value / divisor
                                result[columns_map.get(key)] = value

                else:
                    result = {'htsc_code': '', 'time': md_time, 'data_type': data_type, 'exchange': exchange,
                              'security_type': security_type, 'trade_index': '', 'trade_buy_no': '',
                              'trade_sell_no': '', 'trade_type': '', 'trade_bs_flag': '', 'trade_price': '',
                              'trade_qty': '', 'trade_money': '', 'app_seq_num': '', 'channel_no': ''}

            elif data_type == 'order':
                if exchange == 'XSHG':
                    result = {'htsc_code': '', 'time': md_time, 'data_type': data_type, 'exchange': exchange,
                              'security_type': security_type, 'order_index': '', 'order_type': '',
                              'order_price': '', 'order_qty': '', 'order_bs_flag': '', 'order_no': '', 'traded_qty': '',
                              'app_seq_num': '', 'channel_no': ''}
                elif exchange == 'XSHE':
                    result = {'htsc_code': '', 'time': md_time, 'data_type': data_type, 'exchange': exchange,
                              'security_type': security_type, 'order_index': '', 'order_type': '',
                              'order_price': '', 'order_qty': '', 'order_bs_flag': '',
                              'app_seq_num': '', 'channel_no': ''}

            for key in list(result.keys()):
                if not result[key]:

                    value = data.get(columns_map_rever.get(key))

                    if isinstance(value, str):
                        result[key] = value

                    elif isinstance(value, int):
                        if key in divisor_list:
                            value = value / divisor
                        result[key] = value

                    elif key == 'trade_type' and value is None:
                        result[key] = 0


            return result

    except Exception as e:
        traceback.print_exc()
        print(str(e))


def subscribe_news_handle(marketdatajson):
    try:
        if 'mdNews' in marketdatajson:

            search_type_map = {'0': '新闻', '1': '公告', '2': '舆情'}
            is_valid_map = {'0': '已删除的消息', '1': '有效的消息'}
            exchange_code_map = {
                101: 'XSHG',  # 上交所
                102: 'XSHE',  # 深交所
            }

            data = marketdatajson['mdNews']

            md_time = datetime.strptime(str(data['MDDate']) + f"{data['MDTime']:09d}", '%Y%m%d%H%M%S%f')
            md_time = datetime.strftime(md_time, '%Y-%m-%d %H:%M:%S.%f')
            exchange = exchange_code_map.get(data.get("securityIDSource"))

            result = {'time': md_time, 'exchange': exchange, 'security_type': 'stock'}

            content_list = data.get('sentimentContent')
            if content_list:
                for column_dict in content_list:

                    column_key = column_dict['key']
                    column_value = column_dict['value']

                    if column_key == 'is_valid':
                        column_value = is_valid_map.get(column_value)

                    elif column_key == 'search_type':
                        column_value = search_type_map.get(column_value)

                    result[column_key] = column_value
            return result

        else:
            return marketdatajson

    except Exception as e:
        traceback.print_exc()
        print(str(e))


def subscribe_htsc_margin_handle(marketdatajson):
    try:
        keys_to_check = ['mdSecurityLending', 'mdSLEstimation', 'mdSLStatistics', 'mdSLIndicativeQuote']
        data_type_json = [key for key in keys_to_check if key in marketdatajson]
        if data_type_json:

            security_type_map = {2: 'stock', 3: 'fund'}
            exchange_map = {101: 'XSHG', 102: 'XSHE', 805: 'HTSM'}

            # 一级目录映射
            key_map = MappingTable.perform_operation('get_htsc_margin_map')

            # 二级目录映射
            lendingentry_map = {'Level': 'level', 'Rate': 'rate', 'Term': 'term', 'Amount': 'amount',
                                'HtscProvided': 'htsc_provided', 'TotalAmount': 'total_amount',
                                'MatchedAmount': 'matched_amount', 'PostponeProbability': 'post_pone_probability'}

            # 二级目录列表
            data_type_lendingentry = {
                "security_lending": ['valid_borrows', 'valid_a_lends', 'valid_b_lends', 'valid_c_lends', 'a_lends',
                                     'b_lends', 'c_lends', 'valid_reservation_borrows', 'valid_reservation_lends',
                                     'reservation_borrows', 'reservation_lends', 'valid_otc_lends', 'htsc_borrows',
                                     'loans', 'external_lends', 'market_borrows', 'market_lends'],
                "security_lending_estimation": ['long_term_lends', 'valid_borrows', 'valid_a_lends', 'valid_b_lends',
                                                'borrows', 'a_lends', 'b_lends'],
            }

            # 一级除数
            divisor_columns = ['trade_money', 'best_loan_rate', 'weighted_rate', 'pre_htsc_borrow_weighted_rate',
                               'htsc_borrow_weighted_rate', 'htsc_borrow_rate', 'pre_low_rate', 'best_borrow_rate',
                               'pre_high_rate', 'htsc_lend_trade_volume', 'pre_weighted_rate',
                               'last', 'low_rate', 'high_rate', 'best_lend_rate', 'market_trade_volume', 'pre_close',
                               'pre_trade_money', 'htsc_best_lend_rate']

            # json提取映射
            data_type_json_map = {'mdSecurityLending': 'security_lending',
                                  'mdSLEstimation': 'security_lending_estimation',
                                  'mdSLStatistics': 'security_lending_statistics',
                                  'mdSLIndicativeQuote': 'security_lending_indicative_quote'}

            # 处理二级目录
            def process_lendingentry(lendingentry_list, divisor):
                for dictionary in lendingentry_list:
                    for old_key, new_key in lendingentry_map.items():
                        if old_key in dictionary:
                            if old_key == 'Rate':
                                dictionary[new_key] = dictionary.pop(old_key) / divisor
                            else:
                                dictionary[new_key] = dictionary.pop(old_key)
                return lendingentry_list

            data_type_str = data_type_json[0]
            dict_data = marketdatajson[data_type_str]
            data_type = data_type_json_map.get(data_type_str)

            if data_type == 'security_lending_statistics':
                divisor_columns.append('htsc_borrow_trade_volume')

            divisor = pow(10, int(dict_data.get("DataMultiplePowerOf10")))

            new_dict_data = {}
            for key_name, key_value in dict_data.items():

                new_key_name = key_map.get(key_name)

                if new_key_name:

                    if new_key_name == 'exchange':
                        key_value = exchange_map.get(key_value)

                    elif new_key_name == 'security_type':
                        key_value = security_type_map.get(key_value)

                    elif new_key_name == 'trade_date' and isinstance(key_value, str):
                        key_value = f'{key_value[:4]}-{key_value[4:6]}-{key_value[6:8]}'

                    elif new_key_name in divisor_columns:
                        key_value = key_value / divisor

                    elif data_type in ['security_lending', 'security_lending_estimation']:
                        if new_key_name in data_type_lendingentry.get(data_type):
                            key_value = process_lendingentry(key_value, divisor)

                    new_dict_data[new_key_name] = key_value

                else:
                    if key_name == 'MDDate':
                        md_time = datetime.strptime(str(dict_data['MDDate']) + f"{dict_data['MDTime']:09d}",
                                                    '%Y%m%d%H%M%S%f')
                        md_time = md_time.strftime('%Y-%m-%d %H:%M:%S.%f')
                        new_dict_data['time'] = md_time

                    elif key_name == 'MDTime':
                        new_dict_data['data_type'] = data_type

            return new_dict_data

        else:
            return marketdatajson

    except Exception as e:
        traceback.print_exc()
        print(str(e))
