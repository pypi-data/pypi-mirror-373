# -*- coding: utf-8 -*-


class market_service(object):

    def __init__(self):
        pass

    # ************************************处理数据订阅************************************
    # 处理订阅的股票Tick数据，result格式为dict格式
    def on_subscribe_tick(self, result):
        pass

    # 处理订阅的K线指标模型，result格式为dict格式
    def on_subscribe_kline(self, result):
        pass

    # 处理逐笔数据，result格式为dict格式
    def on_subscribe_trans_and_order(self, result):
        pass

    # 处理衍生数据，result格式为dict格式
    def on_subscribe_derived(self, result):
        pass

    # 处理融券通行情，result格式为dict格式
    def on_subscribe_htsc_margin(self, result):
        pass

    # 处理实时资讯数据，result格式为dict格式
    def on_subscribe_news(self, result):
        pass

    # ************************************处理回放数据************************************
    # 处理回放的Tick数据，result格式为dict格式
    def on_playback_tick(self, result):
        pass

    # 处理回放的逐笔成交逐笔委托数据，result格式为dict格式
    def on_playback_trans_and_order(self, result):
        pass

    # 处理回放的状态，status格式为string格式
    def onPlaybackStatus(self, status):
        pass
        # print(status)

    # 处理回放请求返回结果，response格式为string格式
    def onPlaybackResponse(self, response):
        pass
        # print(response)

    # 处理回放控制请求返回结果，response格式为string格式
    def onPlaybackControlResponse(self, response):
        pass
        # print(response)

    # ************************************处理查询请求返回结果************************************
    # 处理查询今日最新的指定证券的基础信息的返回结果，result格式为dict格式
    def on_query_response(self, result):
        pass


    # 处理查询历史上所有的指定证券的基础信息 query_mdcontant_by_type()的返回结果，queryresponse格式为list[json]
    # 处理查询今日最新的指定证券的基础信息 query_last_mdcontant_by_type()的返回结果，queryresponse格式为list[json]
    # 处理查询历史上所有的指定证券的基础信息 query_mdcontant_by_id()的返回结果，queryresponse格式为list[json]
    # 处理查询今日最新的指定证券的基础信息 query_last_mdcontant_by_id()的返回结果，queryresponse格式为list[json]
    # 处理查询指定证券的ETF的基础信息 query_ETFinfo()的返回结果，queryresponse格式为list[json]
    # 处理查询指定证券的最新一条Tick数据 query_last_mdtick()的返回结果，queryresponse格式为list[json]
    # def onQueryResponse(self, queryresponse):
    #     pass
        # for resonse in iter(queryresponse):
        #     # response格式为json格式
        #     print(resonse)

