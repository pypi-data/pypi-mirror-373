class MappingTable:

    @staticmethod
    def get_kline_map():
        return {'HTSCSecurityID': 'htsc_code', 'OpenPx': 'open', 'ClosePx': 'close', 'HighPx': 'high', 'LowPx': 'low',
                'NumTrades': 'num_trades', 'TotalVolumeTrade': 'volume', 'TotalValueTrade': 'value',
                'OpenInterest': 'open_interest', 'SettlePrice': 'settle', 'PeriodType': 'frequency',
                'SecurityID': 'security_id', 'ExchangeDate': 'exchange_date', 'ExchangeTime': 'exchange_time',
                # 订阅
                'securityIDSource': 'exchange', 'securityType': 'security_type',
                # 查询
                'SecurityIDSource': 'exchange', 'SecurityType': 'security_type',


                }

    @staticmethod
    def tick_map():
        return {'HTSCSecurityID': 'htsc_code', 'HighPx': 'high', 'LowPx': 'low', 'MaxPx': 'max', 'MinPx': 'min',
                'LastPx': 'last', 'OpenPx': 'open',
                'ClosePx': 'close', 'PreClosePx': 'prev_close', 'SettlePrice': 'settle', 'PreSettlePrice': 'pre_settle',
                'NumTrades': 'num_trades', 'TotalValueTrade': 'value', 'TotalVolumeTrade': 'volume', 'IOPV': 'iopv',
                'BuyNumOrdersQueue': 'buy_num_orders_queue', 'ChangeSpeed': 'change_speed',
                'AfterHoursTotalValueTrade': 'after_hours_total_value_trade',
                'SellNumOrdersQueue': 'sell_num_orders_queue', 'AfterHoursHighPx': 'after_hours_high_px',
                'ChangeValue': 'change_value', 'SellPriceQueue': 'sell_price_queue',
                'MarketPhaseCode': 'market_phase_code', 'ImpliedBuyPx': 'implied_buy_px',
                'PreMarketTotalVolumeTrade': 'pre_market_total_volume_trade',
                'ShortSellSharesTraded': 'short_sell_shares_traded', 'TradingDate': 'trading_day',
                'TradingPhaseCode': 'trading_phase_code', 'SellOrderQtyQueue': 'sell_order_qty_queue',
                'PreMarketLowPx': 'pre_market_low_px', 'USConsolidateVolume': 'us_consolidate_volume',
                'ImpliedBuyQty': 'implied_buy_qty', 'OtcTotalVolumeTrade': 'otc_total_volume_trade',
                'AfterHoursLowPx': 'after_hours_low_px', 'AfterHoursTotalVolumeTrade': 'after_hours_total_volume_trade',
                'PreMarketHighPx': 'pre_market_high_px', 'ImpliedSellPx': 'implied_sell_px',
                'ChangeRate': 'change_rate', 'AfterHoursLastPx': 'after_hours_last_px', 'ReferencePx': 'reference_px',
                'OpenInterest': 'open_interest', 'PositionTrend': 'position_trend',
                'BuyOrderQtyQueue': 'buy_order_qty_queue', 'PreMarketTotalValueTrade': 'pre_market_total_value_trade',
                'Swing': 'swing', 'TradingHaltReason': 'trading_halt_reason',
                'ShortSellTurnover': 'short_sell_turnover', 'ExchangeDate': 'exchange_date',
                'NorminalPx': 'norminal_px', 'PreOpenInterest': 'pre_open_interest',
                'ImpliedSellQty': 'implied_sell_qty', 'PreMarketLastPx': 'pre_market_last_px',
                'BuyPriceQueue': 'buy_price_queue', 'ExchangeTime': 'exchange_time',
                'TotalBuyValueTrade': 'total_buy_value_trade', 'TotalSellValueTrade': 'total_sell_value_trade',
                'PurchaseNumber': 'purchase_number', 'PurchaseAmount': 'purchase_amount',
                'RedemptionNumber': 'redemption_number', 'RedemptionAmount': 'redemption_amount',
                'InitOpenInterest': 'init_open_interest', 'InterestChg': 'interest_chg', 'LifeHighPx': 'life_high_px',
                'LifeLowPx': 'life_low_px', 'BuyPx': 'buy_px', 'BuyQty': 'buy_qty', 'BuyImplyQty': 'buy_imply_qty',
                'SellPx': 'sell_px', 'SellQty': 'sell_qty', 'SellImplyQty': 'sell_imply_qty',
                'TotalWeightTrade': 'weight', 'AveragePx': 'average'}

    @staticmethod
    def subscribe_trans_map():
        return {'HTSCSecurityID': 'htsc_code', 'TradeIndex': 'trade_index', 'TradeBuyNo': 'trade_buy_no',
                'TradeSellNo': 'trade_sell_no', 'TradeBSFlag': 'trade_bs_flag', 'TradePrice': 'trade_price',
                'TradeQty': 'trade_qty', 'TradeMoney': 'trade_money', 'ApplSeqNum': 'app_seq_num',
                'ChannelNo': 'channel_no', 'TradeType': 'trade_type', 'HKTradeType': 'hk_trade_type',
                'OrderIndex': 'order_index', 'OrderType': 'order_type', 'OrderNO': 'order_no',
                'TradedQty': 'traded_qty', 'OrderBSFlag': 'order_bs_flag', 'OrderPrice': 'order_price',
                'OrderQty': 'order_qty'}

    @staticmethod
    def get_htsc_margin_map():
        return {'HTSCSecurityID': 'htsc_code', 'TradingPhaseCode': 'trading_phase', 'securityIDSource': 'exchange',
                'securityType': 'security_type', 'PreWeightedRate': 'pre_weighted_rate', 'PreHighRate': 'pre_high_rate',
                'PreLowRate': 'pre_low_rate', 'PreHtscVolume': 'pre_htsc_volume',
                'PreMarketVolume': 'pre_market_volume', 'WeightedRate': 'weighted_rate', 'HighRate': 'high_rate',
                'LowRate': 'low_rate', 'HtscVolume': 'htsc_volume', 'MarketVolume': 'market_volume',
                'BestBorrowRate': 'best_borrow_rate', 'BestLendRate': 'best_lend_rate', 'ValidBorrows': 'valid_borrows',
                'ValidALends': 'valid_a_lends', 'ValidBLends': 'valid_b_lends', 'ValidCLends': 'valid_c_lends',
                'ALends': 'a_lends', 'BLends': 'b_lends', 'CLends': 'c_lends',
                'ValidReservationBorrows': 'valid_reservation_borrows',
                'ValidReservationLends': 'valid_reservation_lends', 'ReservationBorrows': 'reservation_borrows',
                'ReservationLends': 'reservation_lends', 'ValidOtcLends': 'valid_otc_lends',
                'BestReservationBorrowRate': 'best_reservationborrow_rate',
                'BestReservationLendRate': 'best_reservation_lend_rate', 'ValidLendAmount': 'valid_lend_amount',
                'ValidALendAmount': 'valid_a_lend_amount', 'ValidBLendAmount': 'valid_b_lend_amount',
                'HtscBorrowAmount': 'htsc_borrow_amount', 'HtscBorrowRate': 'htsc_borrow_rate',
                'BestLoanRate': 'best_loan_rate', 'HtscBorrowTradeVolume': 'htsc_borrow_trade_volume',
                'HtscBorrowWeightedRate': 'htsc_borrow_weighted_rate',
                'PreHtscBorrowTradeVolume': 'pre_htsc_borrow_trade_volume',
                'PreHtscBorrowWeightedRate': 'pre_htsc_borrow_weighted_rate', 'HtscBorrows': 'htsc_borrows',
                'Loans': 'loans', 'ExternalLends': 'external_lends', 'LongTermLends': 'long_term_lends',
                'LastPx': 'last', 'PreClosePx': 'pre_close', 'Borrows': 'borrows',
                'HtscLendTradeVolume': 'htsc_lend_trade_volume', 'MarketTradeVolume': 'market_trade_volume',
                'TradeDate': 'trade_date', 'HtscLendAmount': 'htsc_lend_amount', 'HtscLendTerms': 'htsc_lend_terms',
                'HtscBestLendRate': 'htsc_best_lend_rate', 'HtscBorrowTerms': 'htsc_borrow_terms',
                'TradeVolume': 'trade_volume', 'TradeMoney': 'trade_money', 'PreTradeVolume': 'pre_trade_volume',
                'PreTradeMoney': 'pre_trade_money', 'HtscBorrowTerm': 'htsc_borrow_term', 'LoanAmount': 'loan_amount',
                'MarketBorrows': 'market_borrows', 'ValidLendTerm': 'valid_lend_term',
                'ValidBorrowAmount': 'valid_borrow_amount', 'MarketLends': 'market_lends'}

    @staticmethod
    def get_basic_info_map():
        return {'HTSCSecurityID': 'htsc_code', 'Symbol': 'name', 'SecurityIDSource': 'exchange',
                'SecurityType': 'security_type', 'MDDate': 'time', 'PreClosePx': 'prev_close',
                'SecuritySubType': 'security_sub_type', 'ListDate': 'listing_date',
                'PublicFloatShareQuantity': 'listed_share', 'TradingPhaseCode': 'trading_phase', 'MaxPx': 'max',
                'MinPx': 'min', 'BuyQtyUnit': 'buy_qty_unit', 'SellQtyUnit': 'sell_qty_unit',
                'BuyQtyUpperLimit': 'buy_qty_upper_limit', 'SellQtyUpperLimit': 'sell_qty_upper_limit',
                'BuyQtyLowerLimit': 'buy_qty_lower_limit', 'SellQtyLowerLimit': 'sell_qty_lower_limit',
                'OutstandingShare': 'total_share', 'LotSize': 'lot_size', 'TickSize': 'tick_size',
                'HKSpreadTableCode': 'hk_spread_table_code', 'ShHkConnect': 'sh_hk_connect',
                'SzHkConnect': 'sz_hk_connect', 'VCMFlag': 'is_vcm', 'CASFlag': 'is_cas', 'POSFlag': 'is_pos',
                'ExpireDate': 'expire_date', 'BaseContractID': 'base_contract_id', 'DeliveryYear': 'delivery_year',
                'DeliveryMonth': 'delivery_month', 'InstrumentID': 'instrument_id', 'InstrumentName': 'instrument_name',
                'ExchangeInstID': 'exchange_inst_id', 'ProductID': 'product_id',
                'MaxMarketOrderVolume': 'max_market_order_volume', 'MinMarketOrderVolume': 'min_market_order_volume',
                'MaxLimitOrderVolume': 'max_limit_order_volume', 'MinLimitOrderVolume': 'min_limit_order_volume',
                'VolumeMultiple': 'volume_multiple', 'CreateDate': 'create_date', 'StartDelivDate': 'start_deliv_date',
                'EndDelivDate': 'end_deliv_date', 'PositionType': 'position_type',
                'LongMarginRatio': 'long_margin_ratio', 'ShortMarginRatio': 'short_margin_ratio',
                'MaxMarginSideAlgorithm': 'max_margin_side_algorithm', 'PreOpenInterest': 'pre_open_interest',
                'Currency': 'currency', 'OptionContractID': 'option_contract_id',
                'OptionContractSymbol': 'option_contract_symbol',
                'OptionUnderlyingSecurityID': 'option_underlying_security_id',
                'OptionUnderlyingSymbol': 'option_underlying_symbol', 'OptionUnderlyingType': 'option_underlying_type',
                'OptionOptionType': 'option_option_type', 'OptionCallOrPut': 'option_call_or_put',
                'OptionContractMultiplierUnit': 'option_contract_multiplier_unit',
                'OptionExercisePrice': 'option_exercise_price', 'OptionStartDate': 'option_start_date',
                'OptionEndDate': 'option_end_date', 'OptionExerciseDate': 'option_exercise_date',
                'OptionDeliveryDate': 'option_delivery_date', 'OptionExpireDate': 'option_expire_date',
                'OptionUpdateVersion': 'option_up_date_version',
                'OptionTotalLongPosition': 'option_total_long_position',
                'OptionSecurityClosePx': 'option_security_close', 'OptionSettlPrice': 'option_settl_price',
                'OptionUnderlyingClosePx': 'option_underlying_close', 'OptionPriceLimitType': 'option_price_limit_type',
                'OptionDailyPriceUpLimit': 'option_daily_price_up_limit',
                'OptionDailyPriceDownLimit': 'option_daily_price_down_limit', 'OptionMarginUnit': 'option_margin_unit',
                'OptionMarginRatioParam1': 'option_margin_ratio_param1',
                'OptionMarginRatioParam2': 'option_margin_ratio_param2', 'OptionRoundLot': 'option_round_lot',
                'OptionLmtOrdMinFloor': 'option_lmt_ord_min_floor', 'OptionLmtOrdMaxFloor': 'option_lmt_ord_max_floor',
                'OptionMktOrdMinFloor': 'option_mkt_ord_min_floor', 'OptionMktOrdMaxFloor': 'option_mkt_ord_max_floor',
                'OptionTickSize': 'option_tick_size', 'OptionSecurityStatusFlag': 'option_security_status_flag',
                'OptionListType': 'option_List_type', 'OptionDeliveryType': 'option_delivery_type',
                'OptionContractPosition': 'option_contract_position',
                'OptionBuyQtyUpperLimit': 'option_buy_qty_upper_limit',
                'OptionSellQtyUpperLimit': 'option_Sell_qty_upper_limit',
                'OptionMarketOrderBuyQtyUpperLimit': 'option_market_order_buy_qty_upper_limit',
                'OptionMarketOrderSellQtyUpperLimit': 'option_market_order_sell_qty_upper_limit',
                'OptionQuoteOrderBuyQtyUpperLimit': 'option_quote_order_buy_qty_upper_limit',
                'OptionQuoteOrderSellQtyUpperLimit': 'option_quote_order_sell_qty_upper_limit',
                'OptionBuyQtyUnit': 'option_buy_qty_unit', 'OptionSellQtyUnit': 'option_sell_qty_unit',
                'OptionLastSellMargin': 'option_last_sell_margin', 'OptionSellMargin': 'option_sell_margin',
                'OptionMarketMakerFlag': 'option_market_maker_flag',
                'OptionCombinationStrategy': 'option_combination_strategy', 'FormerSymbol': 'former_symbol',
                'constantParams': 'constant_params', 'PxAccuracy': 'px_accuracy', 'MDChannel': 'md_channel',
                'ConstantSwitchStatus': 'constant_switch_status', 'ExchangeDate': 'exchange_date',
                'StrikePrice': 'strike_price', 'DelistDate': 'delist_date', 'MDTime': 'md_time',
                'ShortSellFlag': 'short_sell_flag', 'EnglishName': 'english_name', 'SecurityID': 'security_id',
                'MDLevel': 'md_level', 'ChiSpelling': 'chi_spelling'}

    @staticmethod
    def get_derived_map():
        return {'HTSCSecurityID': 'htsc_code', 'securityIDSource': 'exchange', 'securityType': 'security_type',
                'TotalValueTrade': 'value', 'TotalBidValueTrade': 'total_buy_value_trade',
                'TotalOfferValueTrade': 'total_sell_value_trade', }

    @staticmethod
    def find_edb_index_map():
        return {'ModifyFrequency': 'modify_frequency', 'IndexId': 'index_id', 'Unit': 'unit',
                'IndexCodeSource': 'index_code_source', 'PathSource': 'path_source', 'IndustryCode': 'industry_code',
                'AccessId': 'access_id', 'IndexName': 'name', 'AccessName': 'access_name',
                'ResourceId': 'resource_id', 'IndexStatus': 'index_status', 'Refenence3': 'refenence3',
                'IS_COMPLIANCE': 'is_compliance'}

    @staticmethod
    def edb_map():
        return {'IndexValue': 'index_value', 'IndexId': 'index_id', 'AccessId': 'access_id', 'PubDate': 'pub_date',
                'AccessName': 'access_name'}

    @staticmethod
    def get_rpt_basicinfo_ht_map():
        return {'UpdateTime': 'update_time', 'AgencyName': 'agency_name', 'AbstractText': 'abstract_text',
                'EntryTime': 'entry_time', 'SubTitle': 'sub_title', 'Abstract': 'abstract', 'Url': 'url',
                'AgencyEngName': 'agency_eng_name', 'IsValid': 'is_valid', 'IssuePlace': 'issue_place',
                'Category': 'category', 'Id': 'id', 'CategoryName': 'category_name', 'Scale': 'scale',
                'ResourceId': 'resource_id', 'UpdateId': 'update_id', 'AgencyCode': 'agency_code',
                'Language': 'language', 'WriteDate': 'time', 'Pages': 'pages', 'GroundTime': 'ground_time',
                'LabelCode': 'label_code', 'LabelValue': 'label_value', 'ReportCode': 'report_code',
                'RecordId': 'record_id', 'IsOrg': 'is_org', 'DeptName': 'dept_name', 'Title': 'title',
                'KeyWords': 'key_words'}

    @staticmethod
    def get_rpt_stk_ht_map():
        return {'SecuCode': 'secu_code', 'InvratingDescLast': 'invrating_desc_last',
                'UpdateTime': 'update_time', 'SecuAbbr': 'name', 'InvratingCodeLast': 'invrating_code_last',
                'PredictPrice': 'predict_price', 'ExchangeName': 'exchange_name', 'EntryTime': 'entry_time',
                'ExchangeCode': 'exchange_code', 'Forecastdate': 'forecast_date', 'IsValid': 'is_valid',
                'IsFirstRating': 'is_first_rating', 'PriceCurrency': 'price_currency', 'Id': 'id',
                'RatingChangeName': 'rating_change_name', 'PreDictpriceLast': 'predict_price_last',
                'InvratingDesc': 'invrating_desc', 'ResourceId': 'resource_id', 'UpdateId': 'update_id',
                'GroundTime': 'ground_time', 'TradingCode': 'trading_code', 'ReportCode': 'report_code',
                'RecordId': 'record_id', 'PriceChange': 'price_change', 'IDSOURCE': 'exchange',
                'InvratingCode': 'invrating_code', 'RatingChange': 'rating_change',
                'HTSCSECURITYID': 'htsc_code'}

    @staticmethod
    def get_rpt_industry_ht_map():
        return {'FInduCode': 'l1_code', 'InvratingDescLast': 'invrating_desc_last', 'UpdateTime': 'update_time',
                'GroundTime': 'ground_time', 'InvratingCodeLast': 'invrating_code_last', 'FInduName': 'l1_name',
                'InduLevel': 'industry_level', 'EntryTime': 'entry_time', 'ForecastDate': 'forecast_date',
                'ReportCode': 'report_code', 'RecordId': 'record_id', 'InduCode': 'industry_code',
                'IsValid': 'is_valid', 'SInduName': 'l2_name', 'IsFirstRating': 'is_first_rating',
                'SInduCode': 'l2_code', 'InduName': 'industry_name', 'InvratingCode': 'invrating_code',
                'RatingChange': 'rating_change', 'Id': 'id', 'RatingChangeName': 'rating_change_name',
                'InvratingDesc': 'invrating_desc', 'ResourceId': 'resource_id', 'UpdateId': 'update_id'}

    @staticmethod
    def get_rpt_author_ht_map():
        return {'AuthorWeight': 'author_weight', 'UpdateTime': 'update_time', 'GroundTime': 'ground_time',
                'CertiCode': 'certi_code', 'Rank': 'rank', 'AuthorCode': 'author_code',
                'CertiTypeCode': 'certi_type_code', 'EntryTime': 'entry_time', 'ReportCode': 'report_code',
                'AuthorName': 'author_name', 'RecordId': 'record_id', 'IsValid': 'is_valid', 'Id': 'id',
                'ResourceId': 'resource_id', 'AuthorType': 'author_type', 'UpdateId': 'update_id'}

    @staticmethod
    def get_rpt_annex_ht_map():
        return {'S3ContentUrl': 's3_content_url', 'S3AnnexUpdateTime': 's3_annex_update_time',
                'UpdateTime': 'update_time', 'AnnexName': 'annex_name', 'GroundTime': 'ground_time',
                'S3AnnexUrl': 's3_annex_url', 'AnnexSize': 'annex_size', 'EntryTime': 'entry_time',
                'ReportCode': 'report_code', 'RecordId': 'record_id', 'IsValid': 'is_valid',
                'S3ContentUpdateTime': 's3_content_update_time', 'AnnexUrl': 'annex_url', 'Id': 'id',
                'ResourceId': 'resource_id', 'AnnexFormat': 'annex_format', 'UpdateId': 'update_id',
                'StoreFileId': 'store_file_id'}

    @staticmethod
    def get_rpt_stkpredict_ht_map():
        return {'SecuCode': 'secu_code', 'UpdateTime': 'update_time', 'GroundTime': 'ground_time',
                'TradingCode': 'trading_code', 'SecuAbbr': 'name', 'EntryTime': 'entry_time',
                'ExchangeCode': 'exchange_code', 'ForecastDate': 'forecast_date', 'ReportCode': 'report_code',
                'RecordId': 'record_id', 'IndexValue': 'index_value', 'IsValid': 'is_valid',
                'PredictYear': 'predict_year', 'IDSOURCE': 'exchange', 'HTSCSECURITYID': 'htsc_code', 'Id': 'id',
                'IndexName': 'index_name', 'ResourceId': 'resource_id', 'UpdateId': 'update_id'}

    @classmethod
    def perform_operation(cls, method_name):
        method = getattr(cls, method_name)
        return method()


if __name__ == '__main__':
    n = MappingTable.perform_operation("get_kline_map")
    print(n)
