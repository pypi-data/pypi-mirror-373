
from datetime import datetime


def query_response_handle(marketdatas):

    if marketdatas:
        # etf
        if marketdatas[0].get('mdETFBasicInfo'):
            result = get_etf_info_handle(marketdatas)
            return result
        # 静态信息
        if marketdatas[0].get('mdConstant'):
            result = get_basic_info_handle(marketdatas)
            return result


def get_etf_info_handle(marketdatas):
    etf_map = {
        'htsc_code': 'HTSCSecurityID', 'name': 'Symbol', 'creation_name': 'CreationSymbol', 'creation_id': 'CreationID',
        'redemption_id': 'RedemptionID', 'redemption_name': 'RedemptionSymbol',
        'creation_redemption_capital_id': 'CreationRedemptionCapitalID',
        'creation_redemption_capital_name': 'CreationRedemptionCapitalSymbol',
        'cross_source_capital_id': 'CrossSourceCapitalID', 'cross_source_capital_name': 'CrossSourceCapitalSymbol',
        'min_pr_units': 'CreationRedemptionUnit', 'esti_cash': 'EstimateCashComponent', 'con_num': 'RecordNum',
        'trading_day': 'TradingDay', 'cash_dif': 'CashComponent', 'min_pr_aset': 'NAVperCU', 'net_asset': 'NAV',
        'cross_market': 'CrossMarket',
        'fund_company': 'FundManagementCompany', 'underlying_id': 'UnderlyingSecurityID',
        'underlying_exchange': 'UnderlyingSecurityIDSource', 'purchase_cap': 'CreationLimit',
        'redemption_cap': 'RedemptionLimit',
        'purchase_cap_per_user': 'CreationLimitPerUser', 'redemption_cap_per_user': 'RedemptionLimitPerUser',
        'net_purchase_cap': 'NetCreationLimit', 'net_redemption_cap': 'NetRedemptionLimit',
        'net_purchase_cap_per_user': 'NetCreationLimitPerUser',
        'net_redemption_cap_per_user': 'NetRedemptionLimitPerUser',

    }

    exchange_code_map = {101: 'XSHG', 102: 'XSHE'}
    security_type_map = {
        1: 'index',
        2: 'stock',
        3: 'fund',
        4: 'bond',
        7: 'option',
        8: 'future',
    }

    result = []
    for marketdata in marketdatas:
        etf_data = marketdata['mdETFBasicInfo']
        md_time = datetime.strptime(str(etf_data['MDDate']) + str(etf_data['MDTime']), '%Y%m%d%H%M%S%f')
        md_time = datetime.strftime(md_time, '%Y-%m-%d %H:%M:%S.%f')
        exchange = exchange_code_map.get(etf_data.get("securityIDSource"))
        security_type = security_type_map.get(etf_data.get('securityType'))
        cash_sub_up_limit = etf_data['MaxCashRatio'] * 100

        if etf_data.get('IsPublish'):
            is_iopv = 1
        else:
            is_iopv = 0

        if etf_data.get('IsAllowCreation'):
            isallowcreation = True
        else:
            isallowcreation = False

        if etf_data.get('IsAllowRedemption'):
            isallowredemption = True
        else:
            isallowredemption = False

        if isallowcreation and isallowredemption:
            pr_permit = "1"
        elif isallowcreation and not isallowredemption:
            pr_permit = "2"
        elif not isallowcreation and isallowredemption:
            pr_permit = "3"
        else:
            pr_permit = "0"

        etf_result = None
        if exchange == 'XSHG':
            etf_result = {'htsc_code': '', 'name': '', 'time': '', 'exchange': '', 'security_type': '',
                          'creation_id': '', 'creation_name': '', 'redemption_id': '', 'redemption_name': '',
                          'creation_redemption_capital_id': '', 'creation_redemption_capital_name': '',
                          'cross_source_capital_id': '', 'cross_source_capital_name': '', 'min_pr_units': '',
                          'esti_cash': '', 'cash_sub_up_limit': '', 'is_iopv': '', 'pr_permit': '', 'con_num': '',
                          'trading_day': '', 'cash_dif': '', 'min_pr_aset': '', 'net_asset': '', 'cross_market': ''}

        elif exchange == 'XSHE':
            etf_result = {'htsc_code': '', 'name': '', 'time': '', 'exchange': '', 'security_type': '',
                          'fund_company': '', 'underlying_id': '', 'underlying_exchange': '', 'min_pr_units': '',
                          'esti_cash': '', 'cash_sub_up_limit': '', 'is_iopv': '', 'pr_permit': '', 'con_num': '',
                          'trading_day': '', 'cash_dif': '', 'min_pr_aset': '', 'net_asset': '', 'purchase_cap': '',
                          'redemption_cap': '', 'purchase_cap_per_user': '', 'redemption_cap_per_user': '',
                          'net_purchase_cap': '', 'net_redemption_cap': '', 'net_purchase_cap_per_user': '',
                          'net_redemption_cap_per_user': '', 'cross_market': ''}

        etf_result['time'] = md_time
        etf_result['exchange'] = exchange
        etf_result['security_type'] = security_type
        etf_result['cash_sub_up_limit'] = cash_sub_up_limit
        etf_result['is_iopv'] = is_iopv
        etf_result['pr_permit'] = pr_permit

        for key in list(etf_result.keys()):

            if not etf_result[key]:
                value = etf_data.get(etf_map.get(key))
                if key == 'trading_day' and value:
                    etf_result[key] = '{}-{}-{}'.format(str(value)[:4], str(value)[4:6], str(value)[6:])
                else:
                    etf_result[key] = value

        result.append(etf_result)

    return result


def get_basic_info_handle(marketdatas):

    basic_info_map = {
        # 指数
        'htsc_code': 'HTSCSecurityID', 'name': 'Symbol', 'prev_close': 'PreClosePx',
        # 股票
        'security_sub_type': 'SecuritySubType', 'listing_date': 'ListDate', 'total_share': 'OutstandingShare',
        'listed_share': 'PublicFloatShareQuantity', 'trading_phase': 'TradingPhaseCode',
         'max': 'MaxPx', 'min': 'MinPx', 'lot_size': 'LotSize', 'tick_size': 'TickSize',
        'buy_qty_unit': 'BuyQtyUnit', 'sell_qty_unit': 'SellQtyUnit',
        'hk_spread_table_code': 'HKSpreadTableCode', 'sh_hk_connect': 'ShHkConnect', 'sz_hk_connect': 'SzHkConnect',
        'is_vcm': 'VCMFlag', 'is_cas': 'CASFlag', 'is_pos': 'POSFlag',
        'buy_qty_upper_limit': 'BuyQtyUpperLimit', 'sell_qty_upper_limit': 'SellQtyUpperLimit',
        # 基金
        'buy_qty_lower_limit': 'BuyQtyLowerLimit', 'sell_qty_lower_limit': 'SellQtyLowerLimit',
        # 债券
        'expire_date': 'ExpireDate', 'base_contract_id': 'BaseContractID',
        # 期权
        'currency': 'Currency','option_contract_id':'OptionContractID','option_contract_symbol':'OptionContractSymbol','option_underlying_security_id':'OptionUnderlyingSecurityID','option_option_type':'OptionOptionType','option_call_or_put':'OptionCallOrPut','option_contract_multiplier_unit':'OptionContractMultiplierUnit',
        'option_exercise_price':'OptionExercisePrice','option_start_date':'OptionStartDate','option_end_date':'OptionEndDate','option_exercise_date':'OptionExerciseDate','option_delivery_date':'OptionDeliveryDate','option_expire_date':'OptionExpireDate','option_security_close':'OptionSecurityClosePx','option_settl_price':'OptionSettlPrice',
        'option_daily_price_up_limit':'OptionDailyPriceUpLimit','option_daily_price_down_limit':'OptionDailyPriceDownLimit','option_margin_ratio_param1':'OptionMarginRatioParam1','option_margin_ratio_param2':'OptionMarginRatioParam2','option_round_lot':'OptionRoundLot','option_tick_size':'OptionTickSize',
        'option_underlying_type':'OptionUnderlyingType','option_up_date_version':'OptionUpdateVersion','option_total_long_position':'OptionTotalLongPosition','option_margin_unit':'OptionMarginUnit','option_round_lot':'OptionRoundLot','option_lmt_ord_min_floor':'OptionLmtOrdMinFloor',
        'option_lmt_ord_max_floor':'OptionLmtOrdMaxFloor','option_mkt_ord_min_floor':'OptionMktOrdMinFloor','option_mkt_ord_max_floor':'OptionMktOrdMaxFloor','option_security_status_flag':'OptionSecurityStatusFlag',
        'option_security_close':'OptionSecurityClosePx',
        # 期货
        'max_market_order_volume':'MaxMarketOrderVolume','min_market_order_volume':'MinMarketOrderVolume',
        'max_limit_order_volume':'MaxLimitOrderVolume','min_limit_order_volume':'MinLimitOrderVolume','volume_multiple':'VolumeMultiple','create_date':'CreateDate','expire_date':'ExpireDate',
        'start_deliv_date':'StartDelivDate','end_deliv_date':'EndDelivDate','position_type':'PositionType','long_margin_ratio':'LongMarginRatio','short_margin_ratio':'ShortMarginRatio',
        'max_margin_side_algorithm':'MaxMarginSideAlgorithm','pre_open_interest':'PreOpenInterest','delivery_year':'DeliveryYear','delivery_month':'DeliveryMonth','exchange_inst_id':'ExchangeInstID',

    }

    exchange_code_map = {
            101:'XSHG', 				#上交所
            102: 'XSHE', 				#深交所
            103: 'NEEQ',#中国全国中小企业股份转让系统（.OC）
            104: 'XSHGFI', 				#上交所固收平台
            105: 'XSHECA', 				#深交所综合协议平台
            106: 'XBSE', 			#北京证券交易所
            107: 'XSHGFC', 			#上交所基金通
            108: 'XSHEFC', 			#深交所基金通
            203: 'XHKG', 				#港交所
            204: 'HKSC', #HKSC(Hong Kong Stock Connect 205: 'HGHQ', #H股全流通
            301: 'CCFX', 				#中国金融期货交易所
            302: 'XSGE', 				#上海期货交易所
            303: 'INE', 	#上海国际能源交易中心
            401: 'SGEX', 				#上海黄金交易所
            501: 'XCFE', 				#中国外汇交易中心（全国银行间同业拆借中心）
            502: 'CCDC',				#中国债券登记结算（.CS）
            503: 'CNEX', #上海国际货币经济有限责任公司
            601: 'XDCE', 				#大连商品交易所
            602: 'XZCE', 				#郑州商品交易所
            603: 'XGFE', #广州期货交易所
            701: 'SWS', 	#上海申银万国证券研究所有限公司
            702: 'CNI', 	#国证指数有限公司
            703: 'CSI', 	#中证指数有限公司
            801: 'HTIS', 	#华泰Insight
            802: 'MORN', 	#晨星MORNINGSTAR
            803: 'QB', 	#宁波森浦信息技术有限公司
            804: 'SPDB',#中国上海浦东发展银行(.SPD)
            805: 'HTSM', #华泰券源融通平台
            806: 'SCB', #渣打银行
            807: 'CUBE', #华泰Cube系统
            901: 'LSE',#英国伦敦证券交易所(.L)
            902: 'LME',#英国伦敦金属交易所LME(.LME)
            903: 'LIFFE',#英国伦敦国际金融期货交易所(.LIFFE)
            904: 'ICEU',#英国伦敦ICE(.IPE)
            905: 'BSE',#印度孟买证券交易所(.BO)
            906: 'NSE',#印度国家证券交易所 907: 'NEX',#新西兰证券交易所（.NZ）
            908: 'APEX',#新加坡亚太交易所APEX(.APE)
            909: 'ICE_SG',#新加坡商品交易所(.ICESG)
            910: 'SGX',#新加坡交易所(.SG)
            911: 'TSE',#日本东京证券交易所(.T)
            912: 'TOCOM',#日本东京工业商品交易所TOCOM(.TCE)
            913: 'OSE',#日本大阪证券交易所（.OSE）
            914: 'EUREX',#欧洲期货交易所(.EUREX )
            915: 'ICE',#美国洲际交易所（.ICE）
            916: 'CME',#美国芝加哥商品交易所CME(.CME)
            917: 'CBOT',#美国芝加哥商品交易所CBOT(.CBT)
            918: 'CBOE',#美国芝加哥期权交易所(.CBOE)
            919: 'AMEX',#美国证券交易所(.A)
            920: 'US',#美国全美综合交易所代码(.US)
            921: 'NYSE',#美国纽约证券交易所(.N)
            922: 'NYMEX',#美国纽约商品交易所NYMEX(.NYM)
            923: 'COMEX',#美国纽约商品交易所COMEX(.CMX)
            924: 'ICUS',#美国纽约期货交易所ICE/NYBOT(.NYB)
            925: 'NASDAQ',#美国纳斯达克证券交易所(.O)
            926: 'BBG',#美国Bloomberg信息商(.BBG)
            927: 'BMD',#马来西亚衍生品交易所BMD（.MDE）
            928: 'LUXSE',#卢森堡Luxembourg Stock Exchange(卢森堡交易所)(.LX)
            929: 'KRX',#韩国交易所（.KS）2005年由原韩国证券交易所（KSE）、韩国期货交易所（KOFEX）和韩国创业板市场（KOSDAQ）合并而成
            930: 'MICEX',#俄罗斯莫斯科交易所，莫斯科MICEX(.MCX)
            931: 'ASE',#澳大利亚证券交易所（.AX）
            932: 'ISE',#爱尔兰Irish Stock Exchange(爱尔兰证券交易所)(.ID)
            933: 'DME',#阿联酋迪拜商品交易所（.DME）
            934: 'IHK',#IHK Assoc of Banks(.IHK)
            935: 'STOXX',#STOXX势拓有限公司(.STOXX) 
            936: 'SPI',#标准普尔（英语：Standard & Poor's，或又常译为史坦普）（.SPI）
            937: 'NIKKEI',#日本经济新闻(Nihon Keizai Shimbun)，简称日经(Nikkei)(.NIKKEI)
            938: 'DJI',				#道琼斯（.DJI）
            939: 'BATS',	#美国交易所运营商（.Z）
            940: 'IEX', #美股Investors Echange（.V）
            941: 'OPRA', #Options Price Reporting Authority （.OPRA）
            942: 'REFINITIV', #路孚特 （.RFV）
            943: 'OTCM', #OTC Market （.OTCM） 包括 美股粉单和ADR的行情
            944: 'EURONEXT', # 泛欧交易所（.EURONEXT）
            945: 'FSI', # 富时 FT-SE International（.FSI）
            946: 'DBDX', # 德交所（.DBDX）
            947: 'SAO', # 巴西圣保罗交易所：Sao Paolo Stock Exchange
            948: 'XASX',	#ASX - TRADE24(.SFE)
            949: 'XCBO', 	#Cobe Futures Exchange（.CBF）
            950: 'XMIL', 	#Borsa Italiana（.MIL)
            951: 'XMOD',	#Montreal Exchange(.MSE)
            952: 'XMEF',	#Meff Renta Variable(.MFM)
            953: 'XOME',	#OMX Nordic Exchange Stockholm(.SSE)
            954: 'UST',	# US Treasuries 美国国债（.UST）
            955: 'USB', # US 美国非国债债券，如企业债（.USB）
            956: 'HOSE', # 胡志明交易所（ HCM Stock Exchange)(.HOSE)
            957: 'HNX', # 河内交易所(Hanoi Stock Exchange)(.HNX)
            958: 'BOATS',# BOATS：BLUE OCEAN ALTERNATIVE TRADING SYSTEM(.BO)
            960 : 'ADSM',# Abu Dhabi Securities Exchange 阿布扎比证交所 (.ADSM)
            961 : 'AQIS',# Aquis Exchange PLC Aquis Exchange PLC (.AQIS)
            962 : 'STUT',# Boerse Stuttgart GmbH Boerse斯图加特有限公司 (.STUT)
            963 : 'HSI',# HSI Company Limited HSI有限公司 (.HSI)
            964 : 'LMAX',# LMAX Limited LMAX有限公司 (.LMAX)
            965 : 'MAEF',# MAE - Argentina MAE-阿根廷 (.MAEF)
            966 : 'MFM',# MEFF Derivatives MEFF衍生品 (.MFM)disuse
            967 : 'NEDL',# NEO Exchange NEO交易所 (.NEDL)
            968 : 'NIFC',# NSE IFSC Limited NSE IFSC有限公司 (.NIFC)
            969 : 'PFTS',# PFTS Stock Exchange PFTS证券交易所 (.PFTS)
            970 : 'BYMF',# Bolsas y Mercados Argentinos (BYMA) 阿根廷大市场（BYMA） (.BYMF)
            971 : 'AIXX',# Astana International Exchange 阿斯塔纳国际交易所 (.AIXX)
            972 : 'CAIR',# Egyptian Exchange (EGX) 埃及交易所（EGX） (.CAIR)
            973 : 'AMAN',# Amman Stock Exchange 安曼证券交易所 (.AMAN)
            974 : 'KRCH',# Pakistan Stock Exchange Ltd 巴基斯坦证券交易所有限公司 (.KRCH)
            975 : 'PEX',# Palestine Exchange 巴勒斯坦交易所 (.PEX)
            976 : 'BAHR',# Bahrain Bourse 巴林交易所 (.BAHR)
            977 : 'BLSE',# Banja Luka Stock Exchange 巴尼亚卢卡证券交易所 (.BLSE)
            978 : 'BMF',# Brasil Bolsa Balcao (B3) 巴西巴尔考证券交易所（B3） (.BMF)
            979 : 'BERM',# Bermuda Stock Exchange 百慕大证券交易所 (.BERM)
            980 : 'GREG',# Berlin Stock Exchange 柏林证券交易所 (.GREG)
            981 : 'BULI',# Bulgarian Stock Exchange 保加利亚证券交易所 (.BULI)
            982 : 'NGMS',# Nordic Growth Market NGM 北欧增长市场NGM (.NGMS)
            983 : 'BELX',# Beogradska Berza A.D. 贝尔格莱德证券交易所 (.BELX)
            984 : 'BEIR',# Beirut Stock Exchange 贝鲁特证券交易所 (.BEIR)
            985 : 'BALT',# The Baltic Exchange 波罗的海交易所 (.BALT)
            986 : 'BXSW',# Berne Exchange - BX Swiss 伯尔尼交易所-BX瑞士 (.BXSW)
            987 : 'BUCI',# Bucharest Stock Exchange 布加勒斯特证券交易所 (.BUCI)
            988 : 'BRAT',# Bratislava Stock Exchange 布拉迪斯拉发证券交易所 (.BRAT)
            989 : 'PRAI',# Prague Stock Exchange 布拉格证券交易所 (.PRAI)
            990 : 'DSE',# Dhaka Stock Exchange 达卡证券交易所 (.DSE)
            991 : 'DESS',# Dar Es Salaam Stock Exchange 达累斯萨拉姆证券交易所 (.DESS)
            992 : 'ODXE',# Osaka Digital Exchange 大阪数字交易所 (.ODXE)
            993 : 'DGCX',# Dubai Gold & Commodities Exchange 迪拜黄金和商品交易所 (.DGCX)
            994 : 'DFM',# Dubai Financial Market 迪拜金融市场 (.DFM)
            995 : 'TFXC',# Tokyo Financial Exchange Inc. 东京金融交易所股份有限公司 (.TFXC)
            996 : 'QTRX',# Boerse Dusseldorf 杜塞尔多夫证券交易所 (.QTRX)
            997 : 'CAN',# Toronto Stock Exchange 多伦多证券交易所 (.CAN)
            998 : 'MANI',# The Philippine Stock Exchange 菲律宾证券交易所 (.MANI)
            999 : 'BOGD',# Bolsa de Valores de Colombia 哥伦比亚银行 (.BOGD)
            1000 : 'KAZA',# Kazakhstan Stock Exchange 哈萨克斯坦证券交易所 (.KAZA)
            1001 : 'QSE',# Bolsa de Valores de Quito 基多价值银行 (.QSE)
            1002 : 'CARA',# Bolsa de Valores de Caracas 加拉加斯价值银行 (.CARA)
            1003 : 'CSE2',# Canadian Securities Exchange 加拿大证券交易所 (.CSE2)
            1004 : 'GHAN',# Ghana Stock Exchange 加纳证券交易所 (.GHAN)
            1005 : 'FEXA',# Financial and Energy Exchange Group 金融与能源交易集团 (.FEXA)
            1006 : 'CASA',# Casablanca Stock Exchange 卡萨布兰卡证券交易所 (.CASA)
            1007 : 'DOHA',# Qatar Exchange 卡塔尔交易所 (.DOHA)
            1008 : 'CSE',# Colombo Stock Exchange 科伦坡证券交易所 (.CSE)
            1009 : 'KSE',# Kuwait Stock Exchange 科威特证券交易所 (.KSE)
            1010 : 'LNGS',# Lang & Schwarz Exchange 郎与施瓦茨交易所 (.LNGS)
            1011 : 'LSX',# Lao Securities Exchange 老挝证券交易所 (.LSX)
            1012 : 'LIMA',# Bolsa de Valores de Lima S.A 利马证券交易所 (.LIMA)
            1013 : 'LJUB',# Ljubljana Stock Exchange 卢布尔雅那证券交易所 (.LJUB)
            1014 : 'LUSK',# Lusaka Stock Exchange 卢萨卡证券交易所 (.LUSK)
            1015 : 'MAPA',# Bolsa de Madrid 马德里证券交易所 (.MAPA)
            1016 : 'MALT',# Malta Stock Exchange 马耳他证券交易所 (.MALT)
            1017 : 'MDXC',# Bursa Malaysia 马来西亚证券交易所 (.MDXC)
            1018 : 'MACD',# Macedonia Stock Exchange 马其顿证券交易所 (.MACD)
            1019 : 'MAUI',# Stock Exchange of Mauritius 毛里求斯证券交易所 (.MAUI)
            1020 : 'MNGL',# Mongolia Stock Exchange 蒙古证券交易所 (.MNGL)
            1021 : 'MONT',# Montreal Exchange 蒙特利尔交易所 (.MONT)
            1022 : 'NAG',# Nagoya Stock Exchange 名古屋证券交易所 (.NAG)
            1023 : 'MGE',# Minneapolis Grain Exchange 明尼阿波利斯谷物交易所 (.MGE)
            1024 : 'JPMX7',# JP Morgan Chase 摩根大通 (.JPMX7)
            1025 : 'MSMT',# Morgan Stanley PLC 摩根士丹利股份有限公司 (.MSMT)
            1026 : 'MSCI',# MSCI 摩根士丹利资本国际指数 (.MSCI)
            1027 : 'MEXD',# MexDer 墨西哥衍生品交易所期货市场 (.MEXD)
            1028 : 'MXIN',# Bolsa Mexicana de Valores 墨西哥证券交易所 (.MXIN)
            1029 : 'GETX',# Munich Exchange 慕尼黑交易所 (.GETX)
            1030 : 'NAMI',# Namibia Stock Exchange 纳米比亚证券交易所 (.NAMI)
            1031 : 'NAIB',# Nairobi Securities Exchange 内罗毕证券交易所 (.NAIB)
            1032 : 'NIGR',# Nigerian Exchange Limited (NGX) 尼日利亚交易所有限公司（NGX） (.NIGR)
            1033 : 'LYNX',# Omega ATS 欧米茄ATS (.LYNX)
            1034 : 'EEXA',# European Energy Exchange 欧洲能源交易所 (.EEXA)
            1035 : 'WIBR',# Gielda Pepierow Wartosciowych 佩皮罗夫证券交易所 (.WIBR)
            1036 : 'BRVM',# Bourse Regionale des Valeurs Mobilieres 区域流动性证券交易所 (.BRVM)
            1037 : 'JSP',# Japan Standard Bond Price 日本标准债券价格 (.JSP)
            1038 : 'BBW',# Japan Bond Trading 日本债券交易 (.BBW)
            1039 : 'SWXD',# SIX Swiss Exchange 瑞士证券交易所 (.SWXD)
            1040 : 'ZAG',# Zagreb Exchange 萨格勒布交易所 (.ZAG)
            1041 : 'SASE',# Sarajevo Stock Exchange 萨拉热窝证券交易所 (.SASE)
            1042 : 'CYPR',# Cyprus Stock Exchange 塞浦路斯证券交易所 (.CYPR)
            1043 : 'SEYS',# MERJ Exchange 塞舌尔证券交易所 (.SEYS)
            1044 : 'TDW3',# Saudi Stock Exchange (Tadawul) 沙特证券交易所（Tadawul） (.TDW3)
            1045 : 'CHF1',# Bolsa de Comercio de Santiago 圣地亚哥商业银行 (.CHF1)
            1046 : 'TOTC',# Taipei Exchange 台北交易所 (.TOTC)
            1047 : 'TVIX',# Taiwan Futures Exchange 台湾期货交易所 (.TVIX)
            1048 : 'TFEX',# Thailand Futures Exchange - TFEX 泰国期货交易所 (.TFEX)
            1049 : 'BANG',# The Stock Exchange of Thailand 泰国证券交易所 (.BANG)
            1050 : 'TELA',# Tel Aviv Stock Exchange 特拉维夫证交所 (.TELA)
            1051 : 'TTSE',# Trinidad & Tobago Stock Exchange 特立尼达和多巴哥证券交易所 (.TTSE)
            1052 : 'OMAN',# Muscat Securities Market 马斯喀特证券市场 (.OMAN)
            1053 : 'TUNI',# Bourse de Tunis 突尼斯证券交易所 (.TUNI)
            1054 : 'VIXA',# Vienna Stock Exchange 维也纳证券交易所 (.VIXA)
            1055 : 'URUG',# Bolsa Electronica del Uruguay 乌拉圭电子银行 (.URUG)
            1056 : 'SORS',# Associations of Banks in Singapore 新加坡银行协会 (.SORS)
            1057 : 'NZBB',# New Zealand Stock Exchange 新西兰证券交易所 (.NZBB)disuse!!!
            1058 : 'JAMX',# Jamaica Stock Exchange 牙买加证券交易所 (.JAMX)
            1059 : 'ENAX',# Athens Exchange 雅典交易所 (.ENAX)
            1060 : 'ARME',# Armenia Securities Exchange 亚美尼亚证券交易所 (.ARME)
            1061 : 'BKYD',# Borsa Istanbul 伊斯坦布尔交易所 (.BKYD)
            1062 : 'NCDX',# India NCDEX 印度NCDEX (.NCDX)
            1063 : 'BINX',# India International Exchange (IFSC) Ltd 印度国际交易所（IFSC）有限公司 (.BINX)
            1064 : 'INDI',# National Stock Exchange India 印度国家证券交易所 (.INDI) disuse!!!
            1065 : 'MCX',# Multi Commodity Exchange of India 印度商品交易所 (.MCX) disuse!!!
            1066 : 'JAKA',# Indonesia Stock Exchange 印尼证券交易所 (.JAKA)
            1067 : 'SAFC',# Johannesburg Stock Exchange 约翰内斯堡证券交易所 (.SAFC)
            1068 : 'BRTI',# CME Group - Bitcoin Real Time Index 芝加哥商业交易所集团 (.BRTI)
            1069 : 'CMEI',# CME Group - Standard and Poor's (S&P) Indices 芝加哥商业交易所集团 (.CMEI)
            1070 : 'ELEC',# Bolsa Electronica de Chile 智利电子银行 (.ELEC)
            1071 : 'PAR',# Paris Bourse/Paris Stock Exchange 巴黎证券交易所 (.PAR)
            1072 : 'AEX',# Amsterdamse effectenbeurs 荷兰证券交易所 (.AEX)
            1073 : 'SIX',# SWX Swiss Exchange 瑞士证券交易所 (.SIX)
            1074 : 'DYSGE',# （通联DataYes渠道）上海期货交易所 (.DYSGE)
            1075 : 'DYINE',# （通联DataYes渠道）上海国际能源交易中心 (.DYINE)
            1076 : 'DYDCE',# （通联DataYes渠道）大连商品期货交易所 (.DYDCE)
            1077 : 'DYZCE',# （通联DataYes渠道）郑州商品期货交易所 (.DYZCE)
            1078 : 'DYGFE',# （通联DataYes渠道）广州期货交易所 (.DYGFE)
            1079: 'SCBRT',#渣打银行 实时（.SCBRT）
            1080: 'REFFX',#路孚特 FIX ALL实时（.REFFX）
            1081: 'FINRA',#美国金融业监管局 （.FINRA）,
        }

    security_type_map = {   
                            1:'index',
                            2:'stock',
                            3:'fund',
                            4:'bond',
                            5:'repo',
                            6:'warrant',
                            7:'option',
                            8:'future',
                            9:'forex',
                            10:'rate',
                            11:'nmetal',
                            12:'cashbond',
                            13:'spot',
                            14:'spfuture',
                            15:'currency',
                            16:'benchmark',
                        }

    security_sub_type_map = {1001: '交易所指数', 1002: '亚洲指数', 1003: '国际指数', 1004: '系统分类指数', 1005: '用户分类指数', 1006: '期货指数', 1007: '指数现货', 1101: '申万一级行业指数', 1102: '申万二级行业指数', 1103: '申万三级行业指数', 1201: '自定义指数 - 概念股指数', 1202: '自定义指数 - 行业指数', 1203: '自定义指数 - 策略指数', 
                             2001: 'A股（主板）', 2002: '中小板股', 2003: '创业板股', 2004: 'B股', 2005: '国际板', 2006: '战略新兴板', 2007: '新三板', 2008: '港股主板', 2009: '港股创业板', 2010: '香港上市NASD股票', 2011: '香港扩展板块股票', 2012: '美股', 2013: '美国存托凭证ADR', 2014: '英股',2015: 'CDR（暂只包括CDR）', 2016: '两网公司及退市公司A股（股转系统）', 2017: '两网公司及退市公司B股（股转系统）', 2018: '股转系统挂牌公司股票', 2019: 'B转H股/H股全流通', 2020: '主板、中小板存托凭证', 2021: '创业板存托凭证', 2022: '北交所（精选层）', 2023: '股转系统基础层', 2024: '股转系统创新层', 2025: '股转系统特殊交易业务',2100: '优先股', 2200: '科创板',
                            3001: '基金（封闭式）', 3002: '未上市开放基金（仅申赎）', 3003: '上市开放基金LOF', 3004: '交易型开放式指数基金ETF', 3005: '分级子基金', 3006: '扩展板块基金（港）', 3007: '仅申赎基金', 3008: '基础设施基金', 3009: '沪深基金通业务',
                            4001: '政府债券（国债）', 4002: '企业债券', 4003: '金融债券', 4004: '公司债', 4005: '可转债券', 4006: '私募债', 4007: '可交换私募债', 4008: '证券公司次级债', 4009: '证券公司短期债', 4010: '可交换公司债', 4011: '债券预发行', 4012: '固收平台特定债券', 4013: '定向可转债', 4020: '资产支持证券',
                            5001: '质押式国债回购', 5002: '质押式企债回购', 5003: '买断式债券回购', 5004: '报价回购', 5005: '质押式协议回购', 5006: '三方回购', 
                            6001: '企业发行权证', 6002: '备兑权证', 6003: '牛证（moo-cow）', 6004: '熊证（bear）', 
                            7001: '个股期权', 7002: 'ETF期权', 
                            8001: '指数期货', 8002: '商品期货', 8003: '股票期货', 8004: '债券期货', 8005: '同业拆借利率期货', 8006: 'Exchange Fund Note Futures外汇基金票据期货', 8007: 'Exchange For Physicals期货转现货', 8009: 'Exchange of Futures For Swaps', 8010: '指数期货连线CX', 8011: '指数期货连线CC', 8012: '商品期货连线CX', 8013: '商品期货连线CC', 8014: '股票期货连线CX', 8015: '股票期货连线CC', 8016: '期现差价线', 8017: '跨期差价线', 8018: '外汇期货', 8019: '贵金属期货', 8100: '上海国际能源交易中心（INE）', 
                            9000: '汇率', 
                            10000: '利率', 
                            11000: '贵金属', 
                            12001: '国债（银行间市场TB）', 12002: '政策性金融债（银行间市场PFB）', 12003: '央行票据（银行间市场CBB）', 12004: '政府支持机构债券（银行间市场GBAB）', 12005: '短期融资券（银行间市场CP）', 12006: '中期票据（银行间市场MTN）', 12007: '企业债（银行间市场CORP）', 12008: '同业存单（银行间市场CD）', 12009: '超短期融资券（银行间市场SCP）', 12010: '资产支持证券（银行间市场ABS）', 12999: '其它（银行间市场Other）', 
                            13002: '商品现货', 13018: '外汇现货', 13019: '贵金属期货', 
                            99001: 'A股新股申购', 99002: 'A股增发', 99010: '集合资产管理计划', 99020: '资产支持证券', 99030: '资金前端控制'}

    trading_phase_map = {'0': '开盘前，启动', '1': '开盘集合竞价', '2': '开盘集合竞价阶段结束到连续竞价阶段开始之前', '3': '连续竞价', '4': '中午休市', '5': '收盘集合竞价', '6': '已闭市', '7': '盘后交易', '8': '临时停牌', '9': '波动性中断', '10': '竞价交易收盘至盘后固定价格交易之前', '11': '盘后固定价格交易'}

    # 需要除的键
    divisor_list = ['prev_close', 'max', 'min']

    result = []
    for marketdata in marketdatas:
        constant_data = marketdata['mdConstant']

        divisor = pow(10, int(constant_data.get("DataMultiplePowerOf10")))  # 除数

        md_time = datetime.strptime(str(constant_data['MDDate']), '%Y%m%d')
        md_time = datetime.strftime(md_time, '%Y-%m-%d')
        
        exchange = exchange_code_map.get(constant_data.get("securityIDSource"))
        security_type = security_type_map.get(constant_data.get('securityType'))


        constant_result = {'htsc_code':'' , 'name':'','exchange':'','security_type': '', 'time': ''}
        if security_type =='index':

            constant_result = {'htsc_code': '', 'name': '', 'exchange': '', 'security_type': '', 'time': '', 'prev_close': ''}

        elif security_type == 'stock':

            constant_result = {'htsc_code': '', 'name': '', 'exchange': '', 'security_type': '', 'security_sub_type': '', 'listing_date': '', 'total_share': '','listed_share': '', 'time': '', 'trading_phase': '', 'prev_close': '', 'max': '', 'min': '', 'lot_size': '', 'tick_size': '','buy_qty_unit': '', 'sell_qty_unit': '', 'buy_qty_upper_limit': '', 'sell_qty_upper_limit': '', 'buy_qty_lower_limit': '', 'sell_qty_lower_limit': '','hk_spread_table_code': '', 'sh_hk_connect': '', 'sz_hk_connect': '', 'is_vcm': '', 'is_cas': '', 'is_pos': ''}
        

        elif security_type == 'fund':

            constant_result = {'htsc_code': '', 'name': '', 'exchange': '', 'security_type': '', 'security_sub_type': '', 'listing_date': '', 'total_share': '', 'listed_share': '','time': '', 'trading_phase': '', 'prev_close': '', 'max': '', 'min': '', 'buy_qty_unit': '', 'sell_qty_unit': '', 'buy_qty_upper_limit': '', 'sell_qty_upper_limit': '', 'buy_qty_lower_limit': '', 'sell_qty_lower_limit': ''}


        elif security_type == 'bond':

            constant_result = {'htsc_code': '', 'name': '', 'exchange': '', 'security_type': '', 'security_sub_type': '', 'listing_date': '', 'total_share': '', 'listed_share': '', 'time': '', 'trading_phase': '', 'prev_close': '', 'max': '', 'min': '','lot_size': '', 'tick_size': '', 'expire_date': '', 'buy_qty_unit': '', 'sell_qty_unit': '', 'buy_qty_upper_limit': '', 'sell_qty_upper_limit': '', 'buy_qty_lower_limit': '', 'sell_qty_lower_limit': '','base_contract_id': ''}

        elif security_type == 'future':

            constant_result = {'htsc_code': '', 'name': '', 'exchange': '', 'security_type': '','security_sub_type': '','listing_date': '', 'time': '','trading_phase': '','prev_close':'', 'max':'','min':'','tick_size':'','max_market_order_volume':'','min_market_order_volume':'','max_limit_order_volume':'','min_limit_order_volume':'','volume_multiple':'','create_date':'','expire_date':'','start_deliv_date':'','end_deliv_date':'','position_type':'','long_margin_ratio':'','short_margin_ratio':'','max_margin_side_algorithm':'','pre_open_interest':''}

        elif security_type == 'option':

            constant_result = {'htsc_code':'','name':'','exchange':'','security_type':'' ,'listing_date':'','time':'','currency':'' ,'prev_close':'','max':'','min':'' ,'option_contract_id':'','option_underlying_security_id':'','option_underlying_type':'','option_option_type':'','option_call_or_put':'','option_contract_multiplier_unit':'','option_exercise_price':'','option_start_date':'','option_end_date':'','option_exercise_date':'','option_delivery_date':'','option_expire_date':'','option_up_date_version':'','option_total_long_position':'','option_security_close':'','option_settl_price':'','option_daily_price_up_limit':'','option_daily_price_down_limit':'','option_margin_unit':'','option_margin_ratio_param1':'','option_margin_ratio_param2':'','option_round_lot':'','option_lmt_ord_min_floor':'','option_lmt_ord_max_floor':'','option_mkt_ord_min_floor':'','option_mkt_ord_max_floor':'','option_security_status_flag':'','option_tick_size':''}


        security_sub_type = constant_data.get('SecuritySubType')
        if security_sub_type:
            security_sub_type = security_sub_type_map.get(int(security_sub_type))
            if security_sub_type:
                constant_result['security_sub_type'] = security_sub_type

        trading_phase = constant_data.get('TradingPhaseCode')
        if trading_phase and 'trading_phase'in constant_result:
            constant_result['trading_phase'] = trading_phase_map.get(trading_phase)

       
    
            
        constant_result['time'] = md_time
        constant_result['exchange'] = exchange
        constant_result['security_type'] = security_type

        for key in list(constant_result.keys()):

            if not constant_result[key]:
                value = constant_data.get(basic_info_map.get(key))
                if key in divisor_list and value:
                    value = value / divisor
                if key in ['listing_date', 'expire_date','create_date','start_deliv_date','end_deliv_date','option_start_date','option_end_date','option_exercise_date','option_delivery_date','option_expire_date'] and value:
                    constant_result[key] = '{}-{}-{}'.format(str(value)[:4], str(value)[4:6], str(value)[6:])
                else:
                    constant_result[key] = value
        
        result.append(constant_result)

    return result



















