class EnumeratedMapping(object):

    @staticmethod
    def table_handle(table_list, table_dict):
        if table_list:
            result_dict = {}
            for i in table_list:
                if table_dict.get(i):
                    result_dict[i] = table_dict[i]
            return result_dict
        else:
            return table_dict

    @staticmethod
    def security_type_map(security_type_list):

        security_type_map = {
            'IndexType': 'index',
            'StockType': 'stock',
            'FundType': 'fund',
            'BondType': 'bond',
            'OptionType': 'option',
            'FuturesType': 'future',
            'SPFuturesType': 'spfuture',
            'WarrantType': 'warrant',
            'RateType': 'rate',
            'SpotType': 'spot',
        }

        return EnumeratedMapping.table_handle(security_type_list, security_type_map)

    @staticmethod
    def security_type_num(security_type_list):

        security_type_num = {
            'index': 1,
            'stock': 2,
            'fund': 3,
            'bond': 4,
            'repo': 5,
            'warrant':6,
            'option': 7,
            'future': 8,
            'forex':9,
            'rate': 10,
            'nmetal':11,
            'cashbond':12,
            'spot': 13,
            'spfuture': 14,
            'currency':15,
            'benchmark':16,
            
        }

        return EnumeratedMapping.table_handle(security_type_list, security_type_num)

    @staticmethod
    def exchange_num(exchange_list):

        exchange_num = {
            'XSHG':101, 				#上交所
            'XSHE':102, 				#深交所
            'NEEQ':103,#中国全国中小企业股份转让系统（.OC）
            'XSHGFI':104, 				#上交所固收平台
            'XSHECA':105, 				#深交所综合协议平台
            'XBSE':106, 			#北京证券交易所
            'XSHGFC':107, 			#上交所基金通
            'XSHEFC':108, 			#深交所基金通
            'XHKG':203, 				#港交所
            'HKSC':204, #HKSC(Hong Kong Stock Connect, 港股通)
            'HGHQ':205, #H股全流通
            'CCFX':301, 				#中国金融期货交易所
            'XSGE':302, 				#上海期货交易所
            'INE':303, 	#上海国际能源交易中心
            'SGEX':401, 				#上海黄金交易所
            'XCFE':501, 				#中国外汇交易中心（全国银行间同业拆借中心）
            'CCDC':502,				#中国债券登记结算（.CS）
            'CNEX':503, #上海国际货币经济有限责任公司
            'XDCE':601, 				#大连商品交易所
            'XZCE':602, 				#郑州商品交易所
            'XGFE':603, #广州期货交易所
            'SWS':701, 	#上海申银万国证券研究所有限公司
            'CNI':702, 	#国证指数有限公司
            'CSI':703, 	#中证指数有限公司
            'HTIS':801, 	#华泰Insight
            'MORN':802, 	#晨星MORNINGSTAR
            'QB':803, 	#宁波森浦信息技术有限公司
            'SPDB':804,#中国上海浦东发展银行(.SPD)
            'HTSM':805, #华泰券源融通平台
            'SCB':806, #渣打银行
            'CUBE':807, #华泰Cube系统
            'LSE':901,#英国伦敦证券交易所(.L)
            'LME':902,#英国伦敦金属交易所LME(.LME)
            'LIFFE':903,#英国伦敦国际金融期货交易所(.LIFFE)
            'ICEU':904,#英国伦敦ICE(.IPE)
            'BSE':905,#印度孟买证券交易所(.BO)
            'NSE':906,#印度国家证券交易所,印度NISE（.NS）
            'NEX':907,#新西兰证券交易所（.NZ）
            'APEX':908,#新加坡亚太交易所APEX(.APE)
            'ICE_SG':909,#新加坡商品交易所(.ICESG)
            'SGX':910,#新加坡交易所(.SG)
            'TSE':911,#日本东京证券交易所(.T)
            'TOCOM':912,#日本东京工业商品交易所TOCOM(.TCE)
            'OSE':913,#日本大阪证券交易所（.OSE）
            'EUREX':914,#欧洲期货交易所(.EUREX )
            'ICE':915,#美国洲际交易所（.ICE）
            'CME':916,#美国芝加哥商品交易所CME(.CME)
            'CBOT':917,#美国芝加哥商品交易所CBOT(.CBT)
            'CBOE':918,#美国芝加哥期权交易所(.CBOE)
            'AMEX':919,#美国证券交易所(.A)
            'US':920,#美国全美综合交易所代码(.US)
            'NYSE':921,#美国纽约证券交易所(.N)
            'NYMEX':922,#美国纽约商品交易所NYMEX(.NYM)
            'COMEX':923,#美国纽约商品交易所COMEX(.CMX)
            'ICUS':924,#美国纽约期货交易所ICE/NYBOT(.NYB)
            'NASDAQ':925,#美国纳斯达克证券交易所(.O)
            'BBG':926,#美国Bloomberg信息商(.BBG)
            'BMD':927,#马来西亚衍生品交易所BMD（.MDE）
            'LUXSE':928,#卢森堡Luxembourg Stock Exchange(卢森堡交易所)(.LX)
            'KRX':929,#韩国交易所（.KS）2005年由原韩国证券交易所（KSE）、韩国期货交易所（KOFEX）和韩国创业板市场（KOSDAQ）合并而成
            'MICEX':930,#俄罗斯莫斯科交易所，莫斯科MICEX(.MCX)
            'ASE':931,#澳大利亚证券交易所（.AX）
            'ISE':932,#爱尔兰Irish Stock Exchange(爱尔兰证券交易所)(.ID)
            'DME':933,#阿联酋迪拜商品交易所（.DME）
            'IHK':934,#IHK Assoc of Banks(.IHK)
            'STOXX':935,#STOXX势拓有限公司(.STOXX) 
            'SPI':936,#标准普尔（英语：Standard & Poor's，或又常译为史坦普）（.SPI）
            'NIKKEI':937,#日本经济新闻(Nihon Keizai Shimbun)，简称日经(Nikkei)(.NIKKEI)
            'DJI':938,				#道琼斯（.DJI）
            'BATS':939,	#美国交易所运营商（.Z）
            'IEX':940, #美股Investors Echange（.V）
            'OPRA':941, #Options Price Reporting Authority （.OPRA）
            'REFINITIV':942, #路孚特 （.RFV）
            'OTCM':943, #OTC Market （.OTCM） 包括 美股粉单和ADR的行情
            'EURONEXT':944, # 泛欧交易所（.EURONEXT）
            'FSI':945, # 富时 FT-SE International（.FSI）
            'DBDX':946, # 德交所（.DBDX）
            'SAO':947, # 巴西圣保罗交易所：Sao Paolo Stock Exchange
            'XASX':948,	#ASX - TRADE24(.SFE)
            'XCBO':949, 	#Cobe Futures Exchange（.CBF）
            'XMIL':950, 	#Borsa Italiana（.MIL)
            'XMOD':951,	#Montreal Exchange(.MSE)
            'XMEF':952,	#Meff Renta Variable(.MFM)
            'XOME':953,	#OMX Nordic Exchange Stockholm(.SSE)
            'UST':954,	# US Treasuries 美国国债（.UST）
            'USB':955, # US 美国非国债债券，如企业债（.USB）
            'HOSE':956, # 胡志明交易所（ HCM Stock Exchange)(.HOSE)
            'HNX':957, # 河内交易所(Hanoi Stock Exchange)(.HNX)
            'BOATS':958,# BOATS：BLUE OCEAN ALTERNATIVE TRADING SYSTEM(.BO)
            'ADSM':960 ,# Abu Dhabi Securities Exchange 阿布扎比证交所 (.ADSM)
            'AQIS':961 ,# Aquis Exchange PLC Aquis Exchange PLC (.AQIS)
            'STUT':962 ,# Boerse Stuttgart GmbH Boerse斯图加特有限公司 (.STUT)
            'HSI':963 ,# HSI Company Limited HSI有限公司 (.HSI)
            'LMAX':964 ,# LMAX Limited LMAX有限公司 (.LMAX)
            'MAEF':965 ,# MAE - Argentina MAE-阿根廷 (.MAEF)
            'MFM':966 ,# MEFF Derivatives MEFF衍生品 (.MFM)disuse
            'NEDL':967 ,# NEO Exchange NEO交易所 (.NEDL)
            'NIFC':968 ,# NSE IFSC Limited NSE IFSC有限公司 (.NIFC)
            'PFTS':969 ,# PFTS Stock Exchange PFTS证券交易所 (.PFTS)
            'BYMF':970 ,# Bolsas y Mercados Argentinos (BYMA) 阿根廷大市场（BYMA） (.BYMF)
            'AIXX':971 ,# Astana International Exchange 阿斯塔纳国际交易所 (.AIXX)
            'CAIR':972 ,# Egyptian Exchange (EGX) 埃及交易所（EGX） (.CAIR)
            'AMAN':973 ,# Amman Stock Exchange 安曼证券交易所 (.AMAN)
            'KRCH':974 ,# Pakistan Stock Exchange Ltd 巴基斯坦证券交易所有限公司 (.KRCH)
            'PEX':975 ,# Palestine Exchange 巴勒斯坦交易所 (.PEX)
            'BAHR':976 ,# Bahrain Bourse 巴林交易所 (.BAHR)
            'BLSE':977 ,# Banja Luka Stock Exchange 巴尼亚卢卡证券交易所 (.BLSE)
            'BMF':978 ,# Brasil Bolsa Balcao (B3) 巴西巴尔考证券交易所（B3） (.BMF)
            'BERM':979 ,# Bermuda Stock Exchange 百慕大证券交易所 (.BERM)
            'GREG':980 ,# Berlin Stock Exchange 柏林证券交易所 (.GREG)
            'BULI':981 ,# Bulgarian Stock Exchange 保加利亚证券交易所 (.BULI)
            'NGMS':982 ,# Nordic Growth Market NGM 北欧增长市场NGM (.NGMS)
            'BELX':983 ,# Beogradska Berza A.D. 贝尔格莱德证券交易所 (.BELX)
            'BEIR':984 ,# Beirut Stock Exchange 贝鲁特证券交易所 (.BEIR)
            'BALT':985 ,# The Baltic Exchange 波罗的海交易所 (.BALT)
            'BXSW':986 ,# Berne Exchange - BX Swiss 伯尔尼交易所-BX瑞士 (.BXSW)
            'BUCI':987 ,# Bucharest Stock Exchange 布加勒斯特证券交易所 (.BUCI)
            'BRAT':988 ,# Bratislava Stock Exchange 布拉迪斯拉发证券交易所 (.BRAT)
            'PRAI':989 ,# Prague Stock Exchange 布拉格证券交易所 (.PRAI)
            'DSE':990 ,# Dhaka Stock Exchange 达卡证券交易所 (.DSE)
            'DESS':991 ,# Dar Es Salaam Stock Exchange 达累斯萨拉姆证券交易所 (.DESS)
            'ODXE':992 ,# Osaka Digital Exchange 大阪数字交易所 (.ODXE)
            'DGCX':993 ,# Dubai Gold & Commodities Exchange 迪拜黄金和商品交易所 (.DGCX)
            'DFM':994 ,# Dubai Financial Market 迪拜金融市场 (.DFM)
            'TFXC':995 ,# Tokyo Financial Exchange Inc. 东京金融交易所股份有限公司 (.TFXC)
            'QTRX':996 ,# Boerse Dusseldorf 杜塞尔多夫证券交易所 (.QTRX)
            'CAN':997 ,# Toronto Stock Exchange 多伦多证券交易所 (.CAN)
            'MANI':998 ,# The Philippine Stock Exchange 菲律宾证券交易所 (.MANI)
            'BOGD':999 ,# Bolsa de Valores de Colombia 哥伦比亚银行 (.BOGD)
            'KAZA':1000 ,# Kazakhstan Stock Exchange 哈萨克斯坦证券交易所 (.KAZA)
            'QSE':1001 ,# Bolsa de Valores de Quito 基多价值银行 (.QSE)
            'CARA':1002 ,# Bolsa de Valores de Caracas 加拉加斯价值银行 (.CARA)
            'CSE2':1003 ,# Canadian Securities Exchange 加拿大证券交易所 (.CSE2)
            'GHAN':1004 ,# Ghana Stock Exchange 加纳证券交易所 (.GHAN)
            'FEXA':1005 ,# Financial and Energy Exchange Group 金融与能源交易集团 (.FEXA)
            'CASA':1006 ,# Casablanca Stock Exchange 卡萨布兰卡证券交易所 (.CASA)
            'DOHA':1007 ,# Qatar Exchange 卡塔尔交易所 (.DOHA)
            'CSE':1008 ,# Colombo Stock Exchange 科伦坡证券交易所 (.CSE)
            'KSE':1009 ,# Kuwait Stock Exchange 科威特证券交易所 (.KSE)
            'LNGS':1010 ,# Lang & Schwarz Exchange 郎与施瓦茨交易所 (.LNGS)
            'LSX':1011 ,# Lao Securities Exchange 老挝证券交易所 (.LSX)
            'LIMA':1012 ,# Bolsa de Valores de Lima S.A 利马证券交易所 (.LIMA)
            'LJUB':1013 ,# Ljubljana Stock Exchange 卢布尔雅那证券交易所 (.LJUB)
            'LUSK':1014 ,# Lusaka Stock Exchange 卢萨卡证券交易所 (.LUSK)
            'MAPA':1015 ,# Bolsa de Madrid 马德里证券交易所 (.MAPA)
            'MALT':1016 ,# Malta Stock Exchange 马耳他证券交易所 (.MALT)
            'MDXC':1017 ,# Bursa Malaysia 马来西亚证券交易所 (.MDXC)
            'MACD':1018 ,# Macedonia Stock Exchange 马其顿证券交易所 (.MACD)
            'MAUI':1019 ,# Stock Exchange of Mauritius 毛里求斯证券交易所 (.MAUI)
            'MNGL':1020 ,# Mongolia Stock Exchange 蒙古证券交易所 (.MNGL)
            'MONT':1021 ,# Montreal Exchange 蒙特利尔交易所 (.MONT)
            'NAG':1022 ,# Nagoya Stock Exchange 名古屋证券交易所 (.NAG)
            'MGE':1023 ,# Minneapolis Grain Exchange 明尼阿波利斯谷物交易所 (.MGE)
            'JPMX7':1024 ,# JP Morgan Chase 摩根大通 (.JPMX7)
            'MSMT':1025 ,# Morgan Stanley PLC 摩根士丹利股份有限公司 (.MSMT)
            'MSCI':1026 ,# MSCI 摩根士丹利资本国际指数 (.MSCI)
            'MEXD':1027 ,# MexDer 墨西哥衍生品交易所期货市场 (.MEXD)
            'MXIN':1028 ,# Bolsa Mexicana de Valores 墨西哥证券交易所 (.MXIN)
            'GETX':1029 ,# Munich Exchange 慕尼黑交易所 (.GETX)
            'NAMI':1030 ,# Namibia Stock Exchange 纳米比亚证券交易所 (.NAMI)
            'NAIB':1031 ,# Nairobi Securities Exchange 内罗毕证券交易所 (.NAIB)
            'NIGR':1032 ,# Nigerian Exchange Limited (NGX) 尼日利亚交易所有限公司（NGX） (.NIGR)
            'LYNX':1033 ,# Omega ATS 欧米茄ATS (.LYNX)
            'EEXA':1034 ,# European Energy Exchange 欧洲能源交易所 (.EEXA)
            'WIBR':1035 ,# Gielda Pepierow Wartosciowych 佩皮罗夫证券交易所 (.WIBR)
            'BRVM':1036 ,# Bourse Regionale des Valeurs Mobilieres 区域流动性证券交易所 (.BRVM)
            'JSP':1037 ,# Japan Standard Bond Price 日本标准债券价格 (.JSP)
            'BBW':1038 ,# Japan Bond Trading 日本债券交易 (.BBW)
            'SWXD':1039 ,# SIX Swiss Exchange 瑞士证券交易所 (.SWXD)
            'ZAG':1040 ,# Zagreb Exchange 萨格勒布交易所 (.ZAG)
            'SASE':1041 ,# Sarajevo Stock Exchange 萨拉热窝证券交易所 (.SASE)
            'CYPR':1042 ,# Cyprus Stock Exchange 塞浦路斯证券交易所 (.CYPR)
            'SEYS':1043 ,# MERJ Exchange 塞舌尔证券交易所 (.SEYS)
            'TDW3':1044 ,# Saudi Stock Exchange (Tadawul) 沙特证券交易所（Tadawul） (.TDW3)
            'CHF1':1045 ,# Bolsa de Comercio de Santiago 圣地亚哥商业银行 (.CHF1)
            'TOTC':1046 ,# Taipei Exchange 台北交易所 (.TOTC)
            'TVIX':1047 ,# Taiwan Futures Exchange 台湾期货交易所 (.TVIX)
            'TFEX':1048 ,# Thailand Futures Exchange - TFEX 泰国期货交易所 (.TFEX)
            'BANG':1049 ,# The Stock Exchange of Thailand 泰国证券交易所 (.BANG)
            'TELA':1050 ,# Tel Aviv Stock Exchange 特拉维夫证交所 (.TELA)
            'TTSE':1051 ,# Trinidad & Tobago Stock Exchange 特立尼达和多巴哥证券交易所 (.TTSE)
            'OMAN':1052 ,# Muscat Securities Market 马斯喀特证券市场 (.OMAN)
            'TUNI':1053 ,# Bourse de Tunis 突尼斯证券交易所 (.TUNI)
            'VIXA':1054 ,# Vienna Stock Exchange 维也纳证券交易所 (.VIXA)
            'URUG':1055 ,# Bolsa Electronica del Uruguay 乌拉圭电子银行 (.URUG)
            'SORS':1056 ,# Associations of Banks in Singapore 新加坡银行协会 (.SORS)
            'NZBB':1057 ,# New Zealand Stock Exchange 新西兰证券交易所 (.NZBB)disuse!!!
            'JAMX':1058 ,# Jamaica Stock Exchange 牙买加证券交易所 (.JAMX)
            'ENAX':1059 ,# Athens Exchange 雅典交易所 (.ENAX)
            'ARME':1060 ,# Armenia Securities Exchange 亚美尼亚证券交易所 (.ARME)
            'BKYD':1061 ,# Borsa Istanbul 伊斯坦布尔交易所 (.BKYD)
            'NCDX':1062 ,# India NCDEX 印度NCDEX (.NCDX)
            'BINX':1063 ,# India International Exchange (IFSC) Ltd 印度国际交易所（IFSC）有限公司 (.BINX)
            'INDI':1064 ,# National Stock Exchange India 印度国家证券交易所 (.INDI) disuse!!!
            'MCX':1065 ,# Multi Commodity Exchange of India 印度商品交易所 (.MCX) disuse!!!
            'JAKA':1066 ,# Indonesia Stock Exchange 印尼证券交易所 (.JAKA)
            'SAFC':1067 ,# Johannesburg Stock Exchange 约翰内斯堡证券交易所 (.SAFC)
            'BRTI':1068 ,# CME Group - Bitcoin Real Time Index 芝加哥商业交易所集团 (.BRTI)
            'CMEI':1069 ,# CME Group - Standard and Poor's (S&P) Indices 芝加哥商业交易所集团 (.CMEI)
            'ELEC':1070 ,# Bolsa Electronica de Chile 智利电子银行 (.ELEC)
            'PAR':1071 ,# Paris Bourse/Paris Stock Exchange 巴黎证券交易所 (.PAR)
            'AEX':1072 ,# Amsterdamse effectenbeurs 荷兰证券交易所 (.AEX)
            'SIX':1073 ,# SWX Swiss Exchange 瑞士证券交易所 (.SIX)
            'DYSGE':1074 ,# （通联DataYes渠道）上海期货交易所 (.DYSGE)
            'DYINE':1075 ,# （通联DataYes渠道）上海国际能源交易中心 (.DYINE)
            'DYDCE':1076 ,# （通联DataYes渠道）大连商品期货交易所 (.DYDCE)
            'DYZCE':1077 ,# （通联DataYes渠道）郑州商品期货交易所 (.DYZCE)
            'DYGFE':1078 ,# （通联DataYes渠道）广州期货交易所 (.DYGFE)
            'SCBRT':1079,#渣打银行 实时（.SCBRT）
            'REFFX':1080,#路孚特 FIX ALL实时（.REFFX）
            'FINRA':1081,#美国金融业监管局 （.FINRA）
        }

        return EnumeratedMapping.table_handle(exchange_list, exchange_num)

    @staticmethod
    def exchange_suffix_map(exchange_list):

        exchange_suffix_map = {
            'XSHG': 'SH',
            'XSHE': 'SZ',
            'CSI': 'CSI',
            'CNI': 'CNI',
            'XBSE': 'BJ',
            'HKSC': 'HKSC',
            'CCFX': 'CF',
            'XSGE': 'SHF',
            'XDCE': 'DCE',
            'XZCE': 'ZCE',
            'HTIS': 'HT',
            'SGEX': 'SGE',

            'XHKG': 'HK',
            'NASDAQ': 'UW',
            'ICE': 'ICE',
            'CME': 'CME',
            'CBOT': 'CBT',
            'COMEX': 'CMX',
            'NYMEX': 'NYM',
            'LME': 'LME',
            'SGX': 'SG',
            'LSE': 'LI',
            'BBG': 'BBG',
        }

        return EnumeratedMapping.table_handle(exchange_list, exchange_suffix_map)

    @staticmethod
    def security_sub_type_map():

        return {'01001': '交易所指数', '01002': '亚洲指数', '01003': '国际指数', '01004': '系统分类指数',
                '01005': '用户分类指数', '01006': '期货指数', '01007': '指数现货', '01101': '申万一级行业指数',
                '01102': '申万二级行业指数', '01103': '申万三级行业指数', '01201': '自定义指数 - 概念股指数',
                '01202': '自定义指数 - 行业指数', '01203': '自定义指数 - 策略指数', '02001': 'A股（主板）',
                '02002': '中小板股', '02003': '创业板股', '02004': 'B股', '02005': '国际板',
                '02006': '战略新兴板', '02007': '新三板', '02008': '港股主板', '02009': '港股创业板',
                '02010': '香港上市NASD股票', '02011': '香港扩展板块股票', '02012': '美股',
                '02013': '美国存托凭证ADR', '02014': '英股', '02015': 'CDR（暂只包括CDR）',
                '02016': '两网公司及退市公司A股（股转系统）', '02017': '两网公司及退市公司B股（股转系统）', '02018': '股转系统挂牌公司股票',
                '02019': 'B转H股/H股全流通', '02020': '主板、中小板存托凭证', '02021': '创业板存托凭证', '02022': '北交所（精选层）',
                '02023': '股转系统基础层', '02024': '股转系统创新层', '02025': '股转系统特殊交易业务', '02100': '优先股',
                '02200': '科创板', '03001': '基金（封闭式）', '03002': '未上市开放基金（仅申赎）', '03003': '上市开放基金LOF',
                '03004': '交易型开放式指数基金ETF', '03005': '分级子基金', '03006': '扩展板块基金（港）',
                '03007': '仅申赎基金', '03008': '基础设施基金', '03009': '沪深基金通业务', '04001': '政府债券（国债）',
                '04002': '企业债券', '04003': '金融债券', '04004': '公司债', '04005': '可转债券', '04006': '私募债', '04007': '可交换私募债',
                '04008': '证券公司次级债', '04009': '证券公司短期债', '04010': '可交换公司债', '04011': '债券预发行',
                '04012': '固收平台特定债券', '04013': '定向可转债', '04020': '资产支持证券', '05001': '质押式国债回购',
                '05002': '质押式企债回购', '05003': '买断式债券回购', '05004': '报价回购', '05005': '质押式协议回购', '05006': '三方回购',
                '06001': '企业发行权证', '06002': '备兑权证', '06003': '牛证（moo-cow）',
                '06004': '熊证（bear）', '07001': '个股期权', '07002': 'ETF期权', '08001': '指数期货',
                '08002': '商品期货', '08003': '股票期货', '08004': '债券期货', '08005': '同业拆借利率期货',
                '08006': 'Exchange Fund Note Futures外汇基金票据期货', '08007': 'Exchange For Physicals期货转现货',
                '08009': 'Exchange of Futures For Swaps', '08010': '指数期货连线CX',
                '08011': '指数期货连线CC', '08012': '商品期货连线CX', '08013': '商品期货连线CC',
                '08014': '股票期货连线CX', '08015': '股票期货连线CC', '08016': '期现差价线', '08017': '跨期差价线',
                '08018': '外汇期货', '08019': '贵金属期货', '08100': '上海国际能源交易中心（INE）', '09000': '汇率',
                '10000': '利率', '11000': '贵金属', '12001': '国债（银行间市场TB）', '12002': '政策性金融债（银行间市场PFB）',
                '12003': '央行票据（银行间市场CBB）', '12004': '政府支持机构债券（银行间市场GBAB）', '12005': '短期融资券（银行间市场CP）',
                '12006': '中期票据（银行间市场MTN）', '12007': '企业债（银行间市场CORP）', '12008': '同业存单（银行间市场CD）',
                '12009': '超短期融资券（银行间市场SCP）', '12010': '资产支持证券（银行间市场ABS）',
                '12999': '其它（银行间市场Other）', '13002': '商品现货', '13018': '外汇现货', '13019': '贵金属期货',
                '99001': 'A股新股申购', '99002': 'A股增发', '99003': '新债申购', '99004': '新基金申购',
                '99005': '配股', '99006': '配债', '99010': '集合资产管理计划', '99020': '资产支持证券', '99030': '资金前端控制'}

    @staticmethod
    def trading_phase_code_map():

        return {'0': '开盘前，启动', '1': '开盘集合竞价', '2': '开盘集合竞价阶段结束到连续竞价阶段开始之前', '3': '连续竞价',
                '4': '中午休市', '5': '收盘集合竞价', '6': '已闭市', '7': '盘后交易', '8': '临时停牌', '9': '波动性中断',
                '10': '竞价交易收盘至盘后固定价格交易之前', '11': '盘后固定价格交易', '101': 'Halt in effect (Cross all U.S. equity exchanges)',
                '102': 'Paused across all U.S. equity markets / SROs (Nasdaq-listed securities only)',
                '103': 'Quote only period in effect (Cross all U.S. equity changes)',
                '104': 'Trading on Nasdaq marktet', '200': 'Undefined', '201': 'Normal', '202': 'Halted',
                '203': 'Suspended', '204': 'Opening Delay', '206': 'Closing Delay'}
