#!/usr/bin/python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from .mdc_query_sync_handle_method import *
from .mdc_enumerated_mapping_table import EnumeratedMapping


# K线数据处理
def get_kline_handle(htsc_code, time, frequency, fq):
    query_type = 1002070003

    # 对应关系字典
    map_dict = {"1min": "Period1Min", "5min": "Period5Min", "15min": "Period15Min", "60min": "Period1H",
                "daily": "Period1D", "weekly": "Period1W", "monthly": "Period1Month",  # 频率
                "pre": "ForwardExrights", "post": "BackwardExrights", "none": "NoExrights"}  # 复权

    # 单标的参数转列表
    if isinstance(htsc_code, str):
        htsc_code = [htsc_code]

    start_date = time[0]
    end_date = time[1]

    if frequency:
        try:
            emd_period_type = map_dict[frequency]
        except:
            return 'frequency does not exist'
    else:
        emd_period_type = ''

    if fq:
        try:
            exrights_type = map_dict[fq]
        except:
            return 'fq does not exist'
    else:
        exrights_type = ''

    # 存储数据
    all_result = pd.DataFrame()
    volumns_list = ['htsc_code', 'time', 'exchange', 'security_type', 'security_id', 'frequency', 'open', 'close',
                    'high', 'low', 'num_trades', 'volume', 'value', 'open_interest', 'settle', 'exchange_date',
                    'exchange_time',]

    if frequency in ["1min", "5min", "15min", "60min", "daily"]:

        if frequency == "daily":
            day = 364
            # 日线线以80为单位分组轮播
            hts_group_list = [htsc_code[i:i + 80] for i in range(0, len(htsc_code), 80)]
        else:
            day = 1
            # 分钟线以40为单位分组轮播
            hts_group_list = [htsc_code[i:i + 40] for i in range(0, len(htsc_code), 40)]

        params_list = []
        while True:
            # 多加一天的时间
            start_add_one_day = (start_date + timedelta(days=day))
            if end_date > start_add_one_day:
                params_list.append({"start_date": start_date, "end_date": start_add_one_day})
                start_date = start_add_one_day
            else:
                params_list.append({"start_date": start_date, "end_date": end_date})
                break

        all_result = pd.DataFrame()
        for hts_group in hts_group_list:

            str_hts_group = ",".join(hts_group)

            for date_params in params_list:

                start_time = datetime.strftime(date_params['start_date'], '%Y%m%d%H%M%S')
                end_time = datetime.strftime(date_params['end_date'], '%Y%m%d%H%M%S')

                params = {"HTSC_SECURITY_IDS": str_hts_group, "START_TIME": start_time, "END_TIME": end_time,
                          "EMD_PERIOD_TYPE": emd_period_type, "EXRIGHTS_TYPE": exrights_type}
                result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

                if isinstance(result, list):
                    df_result = query_to_dataframe(result)  # 转dataframe
                    # 合并时间转datetime
                    df_result["time"] = df_result['MDDate'] + df_result['MDTime']
                    df_result["time"] = df_result["time"].apply(lambda x: datetime.strptime(x, '%Y%m%d%H%M%S%f'))
                    df_result['PeriodType'] = frequency
                    kline_result = column_renaming(df_result, 'get_kline')
                    choose_list = [i for i in volumns_list if i in kline_result]
                    kline_result = kline_result[choose_list]
                    all_result = pd.concat([all_result, kline_result], axis=0).reset_index(drop=True)

    if frequency in ["weekly", "monthly"]:

        # 转字符串
        start_date = datetime.strftime(start_date, "%Y%m%d%H%M%S")
        end_date = datetime.strftime(end_date, "%Y%m%d%H%M%S")

        # 日线以100为单位分组轮播
        hts_group_list = [htsc_code[i:i + 100] for i in range(0, len(htsc_code), 100)]

        for hts_group in hts_group_list:

            str_hts_group = ",".join(hts_group)

            params = {"HTSC_SECURITY_IDS": str_hts_group, "START_TIME": start_date, "END_TIME": end_date,
                      "EMD_PERIOD_TYPE": map_dict[frequency], "EXRIGHTS_TYPE": map_dict[fq]}
            # 查询数据
            result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

            if isinstance(result, list):
                df_result = query_to_dataframe(result)  # 转dataframe
                # 合并时间转datetime
                df_result["time"] = df_result['MDDate'] + df_result['MDTime']
                df_result["time"] = df_result["time"].apply(lambda x: datetime.strptime(x, '%Y%m%d%H%M%S%f'))
                df_result['PeriodType'] = frequency
                kline_result = column_renaming(df_result, 'get_kline')
                choose_list = [i for i in volumns_list if i in kline_result]
                kline_result = kline_result[choose_list]

                all_result = pd.concat([all_result, kline_result], axis=0).reset_index(drop=True)

    if not all_result.empty:
        all_result.sort_values(by=['htsc_code', 'time'], ignore_index=True, inplace=True)
        if 'security_type' in all_result:
            security_type_map = EnumeratedMapping.security_type_map([])
            all_result['security_type'] = all_result['security_type'].apply(
                lambda x: security_type_map.get(x) if security_type_map.get(x) else x)

    return all_result


# 股票每日衍生指标数据处理
def get_derived_handle(htsc_code, trading_day, type):
    # 单标的参数转列表
    if isinstance(htsc_code, str):
        htsc_code = [htsc_code]

    start_date = trading_day[0]
    end_date = trading_day[1]

    if type == 'north_bound':

        query_type = 1002090002

        name_map = {'SCHKSBSH.HT': '北向资金（香港-上海）', 'SCHKSBSZ.HT': '北向资金（香港-深圳）',
                    'SCSHNBHK.HT': '南向资金（上海-香港）', 'SCSZNBHK.HT': '南向资金（深圳-香港）'}

        params_list = []
        while True:
            # 多加14天
            start_add_days = (start_date + timedelta(days=13))

            if end_date > start_add_days:
                params_list.append({"start_date": start_date, "end_date": start_add_days})
                start_date = start_add_days + timedelta(days=1)
            else:
                params_list.append({"start_date": start_date, "end_date": end_date})
                break
        all_result = pd.DataFrame()
        for code in htsc_code:

            for date_params in params_list:

                start_time = datetime.strftime(date_params['start_date'], '%Y%m%d')
                end_time = datetime.strftime(date_params['end_date'], '%Y%m%d')

                params = {"HTSC_SECURITY_ID": code, "START_DATE": start_time, "END_DATE": end_time}
                result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
                if isinstance(result, list):
                    df_result = query_to_dataframe(result)  # 转dataframe
                    df_result = column_renaming(df_result, 'get_derived')

                    df_result["time"] = df_result['MDDate'] + df_result['MDTime']
                    df_result["time"] = df_result["time"].apply(lambda x: datetime.strptime(x, '%Y%m%d%H%M%S%f'))

                    df_result['security_type'] = 'index'
                    df_result['name'] = df_result["htsc_code"].apply(lambda x: name_map.get(x))
                    all_result = pd.concat([all_result, df_result], axis=0).reset_index(drop=True)

        if not all_result.empty:
            all_result.sort_values(by=['htsc_code', 'time'], ignore_index=True, inplace=True)
            all_result = all_result[['name', 'htsc_code', 'time', 'exchange', 'security_type', 'value',
                                     'total_buy_value_trade', 'total_sell_value_trade']]

        return all_result

    else:

        query_type = 1002020001

        # 对应关系字典
        map_dict = {"amv": "Amv", "ar_br": "ArBr", "bias": "Bias", "boll": "Boll",
                    "cr": "Cr", "vma_ma": "VmaMa", "vr": "Vr", "wr": "Wr"}
        try:
            type = map_dict[type]
        except:
            return 'type does not exist'

        params_list = []
        while True:
            # 多加一年的日期
            start_add_one_year = (start_date + timedelta(days=364))

            if end_date > start_add_one_year:
                params_list.append({"start_date": start_date, "end_date": start_add_one_year})
                start_date = start_add_one_year + timedelta(days=1)
            else:
                params_list.append({"start_date": start_date, "end_date": end_date})
                break

        all_result = pd.DataFrame()
        hts_group_list = [htsc_code[i:i + 100] for i in range(0, len(htsc_code), 100)]

        for hts_group in hts_group_list:

            str_hts_group = ",".join(hts_group)

            for date_params in params_list:

                start_time = datetime.strftime(date_params['start_date'], '%Y%m%d')
                end_time = datetime.strftime(date_params['end_date'], '%Y%m%d')

                params = {"HTSC_SECURITY_IDS": str_hts_group, "START_DATE": start_time, "END_DATE": end_time}
                result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
                if isinstance(result, list):
                    result = query_to_dataframe(result)  # 转dataframe
                    # 合并时间转datetime
                    result["trading_day"] = result['MDDate'] + result['MDTime']
                    # 筛选非空值数据
                    result["trading_day"] = result["trading_day"].apply(
                        lambda x: datetime.strptime(x, '%Y%m%d%H%M%S%f'))
                    non_empty_result = result[~result[type].isnull()][['HTSCSecurityID', 'trading_day', type]]
                    result_df = pd.DataFrame(non_empty_result[type].to_list())
                    result_df = pd.DataFrame(result_df[0].to_list())
                    finished_df = pd.concat([result[['HTSCSecurityID', 'trading_day']], result_df], axis=1)
                    df_derived_data = change_column_name(finished_df)
                    df_derived_data.columns = df_derived_data.columns.str.lower()  # 转小写列名
                    all_result = pd.concat([all_result, df_derived_data], axis=0).reset_index(drop=True)

        if not all_result.empty:
            all_result.sort_values(by=['htsc_code', 'trading_day'], ignore_index=True, inplace=True)

        return all_result


# 成交分价数据处理
def get_trade_distribution_handle(htsc_code, trading_day):
    query_type = 1002040002

    # 单标的参数转列表
    if isinstance(htsc_code, str):
        htsc_code = [htsc_code]

    start_date = trading_day[0]
    end_date = trading_day[1]

    params_list = []
    while True:
        # 多加一年的日期
        start_add_one_year = (start_date + timedelta(days=364))

        if end_date > start_add_one_year:
            params_list.append({"start_date": start_date, "end_date": start_add_one_year})
            start_date = start_add_one_year + timedelta(days=1)

        else:
            params_list.append({"start_date": start_date, "end_date": end_date})
            break

    all_result = pd.DataFrame()
    hts_group_list = [htsc_code[i:i + 100] for i in range(0, len(htsc_code), 100)]

    for hts_group in hts_group_list:

        str_hts_group = ",".join(hts_group)

        for date_params in params_list:
            start_time = datetime.strftime(date_params['start_date'], '%Y%m%d')
            end_time = datetime.strftime(date_params['end_date'], '%Y%m%d')

            params = {"HTSC_SECURITY_IDS": str_hts_group, "START_DATE": start_time, "END_DATE": end_time}
            result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

            if isinstance(result, list):
                result_list = query_to_dataframe(result, False)
                df_result = pd.json_normalize(result_list, ['Details'],
                                              ['HTSCSecurityID', 'SecurityIDSource', 'Symbol', 'MDDate', 'MDTime'])

                df_result["time"] = df_result['MDDate'] + df_result['MDTime']
                df_result["time"] = df_result["time"].apply(lambda x: datetime.strptime(x, '%Y%m%d%H%M%S%f'))
                df_result.drop(labels=['MDDate', 'MDTime'], axis=1, inplace=True)

                all_result = pd.concat([all_result, df_result], axis=0, ignore_index=True)

    if not all_result.empty:
        all_result = change_column_name(all_result)
        htsc_code = all_result.pop('htsc_code')
        exchange = all_result.pop('exchange')
        name = all_result.pop('name')
        time = all_result.pop('time')
        all_result.insert(0, 'htsc_code', htsc_code)
        all_result.insert(1, 'exchange', exchange)
        all_result.insert(2, 'name', name)
        all_result.insert(3, 'time', time)
        all_result.sort_values(by=['htsc_code', 'time'], ignore_index=True, inplace=True)

    return all_result


# 筹码分布
def get_chip_distribution_handle(htsc_code, trading_day):
    query_type = 1002040004

    exchange_map = {'SH': 'XSHG', 'SZ': 'XSHE'}

    # 单标的参数转列表
    if isinstance(htsc_code, str):
        htsc_code = [htsc_code]

    str_hts_group = ",".join(htsc_code)

    start_date = trading_day[0]
    end_date = trading_day[1]
    start_time = datetime.strftime(start_date, '%Y%m%d')
    end_time = datetime.strftime(end_date, '%Y%m%d')

    params = {"HTSC_SECURITY_IDS": str_hts_group, "START_DATE": start_time, "END_DATE": end_time}
    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

    if isinstance(result, list):
        result_list = query_to_dataframe(result, False)
        handle_result_list = []
        for handle_data in result_list:
            if not handle_data:
                continue
            tradabledetails = handle_data['TradableDetails']
            df_tradabledetails = pd.DataFrame(tradabledetails)

            max_per = df_tradabledetails['NumberOfSharesPercent'].max()
            max_index = df_tradabledetails['NumberOfSharesPercent'].idxmax()
            sec_per = df_tradabledetails['NumberOfSharesPercent'][max_index + 1]

            if max_per > 10:
                multiple_per = max_per / sec_per
                if multiple_per > 10:
                    df_tradabledetails.drop(index=max_index, inplace=True)
                    df_tradabledetails.reset_index(drop=True, inplace=True)

            sum_per = df_tradabledetails['NumberOfSharesPercent'].sum()
            df_tradabledetails['NumberOfSharesPercent'] = df_tradabledetails['NumberOfSharesPercent'].apply(
                lambda x: float(x) / float(sum_per))

            df_tradabledetails['sum'] = df_tradabledetails['NumberOfSharesPercent'].cumsum()

            cost_list = [0.05, 0.15, 0.50, 0.85, 0.95]
            for cost in cost_list:
                df_cost_choose = df_tradabledetails['sum'][df_tradabledetails['sum'] <= cost]
                df_cost_choose = df_tradabledetails.loc[0:len(df_cost_choose)]
                df_cost_choose = df_cost_choose.copy()
                df_cost_choose['NumberOfSharesPercent'].values[-1] = df_cost_choose['NumberOfSharesPercent'].values[
                                                                         -1] - (
                                                                             df_cost_choose['sum'].values[-1] - cost)
                sum_multi = df_cost_choose['Price'].mul(df_cost_choose['NumberOfSharesPercent']).sum()
                avg_sum_multi = sum_multi / cost
                handle_data[f"cost_{str(int(cost * 100))}pct"] = avg_sum_multi

            handle_result_list.append(handle_data)

        df_all_data = pd.DataFrame(handle_result_list)
        df_all_data = change_column_name(df_all_data)

        df_all_data["time"] = df_all_data['MDDate'] + df_all_data['MDTime']
        df_all_data["time"] = df_all_data["time"].apply(lambda x: datetime.strptime(x, '%Y%m%d%H%M%S%f'))
        df_all_data["exchange"] = df_all_data["htsc_code"].apply(lambda x: exchange_map.get(str(x).split('.')[-1]))

        column_list = ["last", "prev_close", "avg_cost", "max_cost", "min_cost", "winner_rate",
                       "diversity", "pre_winner_rate", "restricted_avg_cost", "restricted_max_cost",
                       "restricted_min_cost",
                       "large_shareholders_avg_cost", "large_shareholders_total_share_pct"]

        for column_name in column_list:
            if column_name in df_all_data:
                df_all_data[column_name] = df_all_data[column_name].apply(lambda x: float(x) / 10000 if x else 0)

        choose_list = ['htsc_code', 'time', 'exchange', 'last', 'prev_close', 'total_share', 'a_total_share',
                       'a_listed_share', 'listed_share', 'restricted_share', 'cost_5pct', 'cost_15pct', 'cost_50pct',
                       'cost_85pct', 'cost_95pct', 'avg_cost', 'max_cost', 'min_cost', 'winner_rate', 'diversity',
                       'pre_winner_rate', 'restricted_avg_cost', 'restricted_max_cost', 'restricted_min_cost',
                       'large_shareholders_avg_cost', 'large_shareholders_total_share',
                       'large_shareholders_total_share_pct']

        all_result = df_all_data.filter(items=choose_list, axis=1)

        return all_result

    return pd.DataFrame()


# 资金流向数据处理
def get_money_flow_handle(htsc_code, trading_day):
    query_type = 1002040003

    # 单标的参数转列表
    if isinstance(htsc_code, str):
        htsc_code = [htsc_code]

    start_date = trading_day[0]
    end_date = trading_day[1]

    params_list = []
    while True:
        # 多加一年的日期
        start_add_one_year = (start_date + timedelta(days=364))

        if end_date > start_add_one_year:
            params_list.append({"start_date": start_date, "end_date": start_add_one_year})
            start_date = start_add_one_year + timedelta(days=1)

        else:
            params_list.append({"start_date": start_date, "end_date": end_date})
            break

    all_result = pd.DataFrame()
    hts_group_list = [htsc_code[i:i + 100] for i in range(0, len(htsc_code), 100)]

    for hts_group in hts_group_list:

        str_hts_group = ",".join(hts_group)

        for date_params in params_list:
            start_time = datetime.strftime(date_params['start_date'], '%Y%m%d')
            end_time = datetime.strftime(date_params['end_date'], '%Y%m%d')

            params = {"HTSC_SECURITY_IDS": str_hts_group, "START_DATE": start_time, "END_DATE": end_time}
            result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

            if isinstance(result, list):
                df_result = query_to_dataframe(result)
                df_result["time"] = df_result['MDDate'] + df_result['MDTime']
                df_result["time"] = df_result["time"].apply(lambda x: datetime.strptime(x, '%Y%m%d%H%M%S%f'))
                df_result = change_column_name(df_result)

                choose_list = ["htsc_code", "exchange", "name", "time", "super_large_outflow_value",
                               "super_large_outflow_qty", "super_large_inflow_value", "super_large_inflow_qty",
                               "large_outflow_value", "large_outflow_qty", "large_inflow_value", "large_inflow_qty",
                               "medium_outflow_value", "medium_outflow_qty", "medium_inflow_value", "medium_inflow_qty",
                               "small_outflow_value", "small_outflow_qty", "small_inflow_value", "small_inflow_qty",
                               "main_outflow_value", "main_outflow_qty", "main_inflow_value", "main_inflow_qty"]

                df_result = df_result[choose_list]
                all_result = pd.concat([all_result, df_result], axis=0, ignore_index=True)

    if not all_result.empty:
        all_result.sort_values(by=['htsc_code', 'time'], ignore_index=True, inplace=True)

    return all_result


# 涨跌分析数据处理
def get_change_summary_handle(market, trading_day):
    query_type = 1002040001

    # 单标的参数转列表
    if isinstance(market, str):
        market = [market]

    start_date = trading_day[0]
    end_date = trading_day[1]

    market_map_dict = {"sh_a_share": "MDI1001.HT", "sz_a_share": "MDI1002.HT", "a_share": "MDI1003.HT",
                       "b_share": "MDI1004.HT", "gem": "MDI1005.HT", "sme": "MDI1006.HT", "star": "MDI1013.HT"}

    market = list(map(lambda x: market_map_dict[x], market))

    params_list = []
    while True:
        # 多加一年的日期
        start_add_one_year = (start_date + timedelta(days=364))

        if end_date > start_add_one_year:
            params_list.append({"start_date": start_date, "end_date": start_add_one_year})
            start_date = start_add_one_year + timedelta(days=1)

        else:
            params_list.append({"start_date": start_date, "end_date": end_date})
            break

    all_result = pd.DataFrame()
    market_code_str = ",".join(market)
    for date_params in params_list:
        start_time = datetime.strftime(date_params['start_date'], '%Y%m%d')
        end_time = datetime.strftime(date_params['end_date'], '%Y%m%d')

        params = {"HTSC_SECURITY_IDS": market_code_str, "START_DATE": start_time, "END_DATE": end_time}
        result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

        if isinstance(result, list):
            df_result = query_to_dataframe(result)
            df_result["time"] = df_result['MDDate'] + df_result['MDTime']
            df_result["time"] = df_result["time"].apply(lambda x: datetime.strptime(x, '%Y%m%d%H%M%S%f'))

            df_result = change_column_name(df_result)
            inverse_market_map_dict = dict(zip(market_map_dict.values(), market_map_dict.keys()))
            df_result['market_code'] = df_result["htsc_code"].apply(lambda x: inverse_market_map_dict[x])

            for idx, row_data in df_result.iterrows():

                df_row_data = row_data.to_frame().T

                change_percent_list = row_data["UpsDownsPartitionDetail"]

                for change_percent in change_percent_list:

                    PartitionChangePercent = change_percent["PartitionChangePercent"]
                    if PartitionChangePercent < 0:
                        pcp = str(PartitionChangePercent).replace("-", "minus_")
                    else:
                        pcp = str(PartitionChangePercent)

                    df_row_data["change_percent_" + pcp] = change_percent["Numbers"]

                all_result = pd.concat([all_result, df_row_data], axis=0, ignore_index=True)

    if not all_result.empty:
        choose_list = ['market_code', 'name', 'time', 'change_percent_minus_10', 'change_percent_minus_9',
                       'change_percent_minus_8', 'change_percent_minus_7', 'change_percent_minus_6',
                       'change_percent_minus_5', 'change_percent_minus_4', 'change_percent_minus_3',
                       'change_percent_minus_2', 'change_percent_minus_1', 'change_percent_0', 'change_percent_1',
                       'change_percent_2', 'change_percent_3', 'change_percent_4', 'change_percent_5',
                       'change_percent_6', 'change_percent_7', 'change_percent_8', 'change_percent_9',
                       'change_percent_10', 'ups_downs_count_ups', 'ups_downs_count_downs', 'ups_downs_count_equals',
                       'ups_downs_count_pre_ups', 'ups_downs_count_pre_downs', 'ups_downs_count_pre_equals',
                       'ups_downs_count_ups_percent', 'ups_downs_count_pre_ups_percent',
                       'ups_downs_limit_count_no_reached_limit_px', 'ups_downs_limit_count_up_limits',
                       'ups_downs_limit_count_down_limits', 'ups_downs_limit_count_pre_no_reached_limit_px',
                       'ups_downs_limit_count_pre_up_limits', 'ups_downs_limit_count_pre_down_limits',
                       'ups_downs_limit_count_pre_up_limits_average_change_percent',
                       'ups_downs_limit_count_up_limits_percent']

        all_result = all_result[choose_list]
        all_result.sort_values(by=['market_code', 'time'], ignore_index=True, inplace=True)

    return all_result


# 排行榜
def get_billboard_handle(type, market):
    query_type = 1002030001
    params = {}

    ranking_type_map_dict = {"inc_list": "1101", "dec_list": "1102", "amp_list": "1103", "quant_list": "1104",
                             "comm_list": "1105", "turnover_rate_list": "1106", "trade_val": "1107",
                             "trade_vol": "1108", "inc_list_5min": "1109", "dec_list_5min": "1110",
                             "trade_val_5min": "1111", "trade_vol_5min": "1112"}

    market_map_dict = {"sh_a_share": "MDI1001.HT", "sz_a_share": "MDI1002.HT", "a_share": "MDI1003.HT",
                       "b_share": "MDI1004.HT", "gem": "MDI1005.HT", "sme": "MDI1006.HT", "star": "MDI1013.HT"}

    type_value_dict = {"1101": "MDIndicators.Ind1101", "1102": "MDIndicators.Ind1101", "1103": "MDIndicators.Ind1102",
                       "1104": "MDIndicators.Ind1103", "1105": "MDIndicators.Ind1104", "1106": "MDIndicators.Ind1105",
                       "1107": "TotalValueTrade", "1108": "TotalVolumeTrade", "1109": "MDIndicators.Ind1106",
                       "1110": "MDIndicators.Ind1106", "1111": "MDIndicators.Ind1107", "1112": "MDIndicators.Ind1108"}

    if type:
        ranking_type = ranking_type_map_dict.get(type)
        if not ranking_type:
            return 'type does not exist'
        params['RANKING_TYPE'] = ranking_type
    else:
        return 'type is null or empty'

    if market:
        if isinstance(market, str):
            market = [market]
        try:
            market = list(map(lambda x: market_map_dict.get(x), market))
            market = list(filter(None, market))
            if not market:
                return "The market does not exist"
            marketstr = ",".join(market)
            params['HTSC_SECURITY_IDS'] = marketstr

        except:
            return "The market does not exist"
    else:
        return 'market is null or empty'

    params['START_DATE'] = datetime.strftime(datetime.today(), '%Y%m%d')
    params['END_DATE'] = datetime.strftime(datetime.today(), '%Y%m%d')

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

    all_result = pd.DataFrame()
    if isinstance(result, list):
        result_list = query_to_dataframe(result, False)
        keys_list = list(market_map_dict.keys())
        values_list = list(market_map_dict.values())

        for market_result in result_list:
            # 通过值反查建
            market_index = values_list.index(market_result["HTSCSecurityID"])
            market_value = keys_list[market_index]

            ranking_result = pd.json_normalize(market_result['RankingList'])

            if ranking_type != "1107":
                ranking_result.drop(['TotalValueTrade'], axis=1, inplace=True)
                ranking_result['value'] = ranking_result[type_value_dict[ranking_type]]

            ranking_result['type'] = type
            ranking_result['market'] = market_value
            ranking_result["trading_day"] = ranking_result['MDDate'] + ranking_result['MDTime']
            ranking_result["trading_day"] = ranking_result["trading_day"].apply(
                lambda x: datetime.strptime(x, '%Y%m%d%H%M%S%f'))
            ranking_result = change_column_name(ranking_result)

            result = ranking_result[["trading_day", "htsc_code", "name", "type", "market", "value"]]
            all_result = pd.concat([all_result, result], axis=0, ignore_index=True)

    return all_result


# 股票基础信息 按照证券ID获取股票基本信息
def get_stock_info_handle(htsc_code, listing_date, listing_state):
    query_type = 1101010001

    params = {}
    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if listing_date:
        listing_date_start_date = datetime.strftime(listing_date[0], '%Y%m%d')
        listing_date_end_date = datetime.strftime(listing_date[1], '%Y%m%d')
        params["START_DATE"] = listing_date_start_date
        params["END_DATE"] = listing_date_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    if listing_state:
        params["LISTING_STATE"] = listing_state

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)

        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)
        c_result = df_result[["htsc_code", "name", "listing_state", "exchange", "listing_date", "delisting_date"]]
        return c_result

    return result


# 股票基础信息 按照市场获取股票基本信息
def get_all_stocks_info_handle(listing_date, exchange, listing_state):
    query_type = 1101010001

    exchange_code_map = {'XSHG': '101', 'XSHE': '105'}

    params = {}
    if exchange:
        try:
            params["EXCHANGE_CODE"] = exchange_code_map[exchange]
        except:
            return 'exchange does not exist'
    else:
        params["EXCHANGE_CODE"] = ''

    if listing_date:
        listing_date_start_date = datetime.strftime(listing_date[0], '%Y%m%d')
        listing_date_end_date = datetime.strftime(listing_date[1], '%Y%m%d')
        params["START_DATE"] = listing_date_start_date
        params["END_DATE"] = listing_date_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    if listing_state:
        params["LISTING_STATE"] = listing_state

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)

        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)
        c_result = df_result[["htsc_code", "name", "exchange", "listing_state", "listing_date", "delisting_date"]]
        return c_result

    return result


# 交易日历
def get_trading_days_handle(exchange, trading_day):
    query_type = 1101080001
    params = {"IS_TRADING_DAY": 1}

    exchange_code_map = {'HKSC': '162', 'XSHG': '101', 'XSHE': '105', 'XBSE': '106', 'XCFE': '113', 'XHKG': '161',
                         'AMEX': '301', 'NASDAQ': '302', 'NYSE': '303'}

    flag = 0
    if exchange:
        try:
            params["EXCHANGE_CODE"] = exchange_code_map[exchange]
        except:
            return 'exchange does not exist'
    else:
        params["EXCHANGE_CODE"] = "101"
        flag = 1

    if trading_day:
        trading_day_start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        trading_day_end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["START_DATE"] = trading_day_start_date
        params["END_DATE"] = trading_day_end_date

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)

        df_result = query_to_dataframe(result)

        if flag == 1:
            result_tuple = ("XSHG", df_result['TradingDay'], "XSHE", df_result['TradingDay'],)
        else:
            result_tuple = (exchange, df_result['TradingDay'])

        return result_tuple

    return result


# 行业分类-按行业查询
def get_industries_handle(classified):
    query_type = 1101110003

    classified_map_dict = {
        "sw_l1": 1, "sw_l2": 2, "sw_l3": 3,
        "zjh_l1": 1, "zjh_l2": 2
    }
    params = {}
    if classified in ["sw_l1", "sw_l2", "sw_l3"]:
        params = {"INDU_STANDARD_CODE": "46"}

    if classified in ["zjh_l1", "zjh_l2"]:
        params = {"INDU_STANDARD_CODE": "36"}

    params['INDU_LEVEL'] = str(classified_map_dict[classified])
    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)
        df_result["classified"] = classified
        r_result = df_result[["classified", "industry_name", "industry_code",
                              "l1_code", "l1_name", "l2_code", "l2_name", "l3_code", "l3_name"]]
        return r_result
    return result


# 行业分类-按标的查询
def get_industry_handle(htsc_code, classified):
    query_type = 1101010003

    if classified == 'sw':
        indu_standard_code = "46"
    else:
        indu_standard_code = "36"

    params = {"HTSC_SECURITY_ID": htsc_code, "INDU_STANDARD_CODE": indu_standard_code}
    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)

        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)
        df_result["classified"] = classified
        r_result = df_result[["htsc_code", "classified", "name", "exchange", "industry_name", "industry_code",
                              "l1_code", "l1_name", "l2_code", "l2_name", "l3_code", "l3_name"]]
        return r_result
    return result


# 行业分类-按行业代码查询
def get_industry_stocks_handle(industry_code, classified):
    query_type = 1101010003

    sw_level_map = {'230000': 1, '240000': 1, '270000': 1, '330000': 1, '340000': 1, '110000': 1, '220000': 1,
                    '370000': 1,
                    '410000': 1, '420000': 1, '430000': 1, '450000': 1, '460000': 1, '480000': 1, '490000': 1,
                    '510000': 1,
                    '610000': 1, '740000': 1, '750000': 1, '760000': 1, '770000': 1, '280000': 1, '620000': 1,
                    '630000': 1,
                    '640000': 1, '650000': 1, '710000': 1, '720000': 1, '730000': 1, '350000': 1, '360000': 1,
                    '220800': 2,
                    '220900': 2, '230300': 2, '230400': 2, '230500': 2, '240200': 2, '240300': 2, '240400': 2,
                    '240500': 2,
                    '240600': 2, '270100': 2, '270200': 2, '270300': 2, '270400': 2, '280400': 2, '280500': 2,
                    '280600': 2,
                    '330100': 2, '330200': 2, '330300': 2, '330400': 2, '330500': 2, '330600': 2, '330700': 2,
                    '340400': 2,
                    '340500': 2, '340600': 2, '340700': 2, '110100': 2, '110200': 2, '110300': 2, '110400': 2,
                    '110500': 2,
                    '110700': 2, '110800': 2, '110900': 2, '220200': 2, '220300': 2, '220400': 2, '220500': 2,
                    '220600': 2,
                    '360300': 2, '360500': 2, '370100': 2, '370200': 2, '370300': 2, '370400': 2, '370500': 2,
                    '370600': 2,
                    '410100': 2, '410300': 2, '420800': 2, '420900': 2, '421000': 2, '421100': 2, '430100': 2,
                    '430300': 2,
                    '450200': 2, '450300': 2, '450400': 2, '450600': 2, '450700': 2, '460600': 2, '460700': 2,
                    '460800': 2,
                    '460900': 2, '461000': 2, '461100': 2, '480200': 2, '480300': 2, '480400': 2, '480500': 2,
                    '480600': 2,
                    '490100': 2, '490200': 2, '490300': 2, '510100': 2, '610100': 2, '610200': 2, '740100': 2,
                    '740200': 2,
                    '750100': 2, '750200': 2, '750300': 2, '760100': 2, '760200': 2, '770100': 2, '770200': 2,
                    '770300': 2,
                    '270500': 2, '270600': 2, '280200': 2, '280300': 2, '610300': 2, '620100': 2, '620200': 2,
                    '620300': 2,
                    '620400': 2, '620600': 2, '630100': 2, '630300': 2, '630500': 2, '630600': 2, '630700': 2,
                    '630800': 2,
                    '640100': 2, '640200': 2, '640500': 2, '640600': 2, '640700': 2, '650100': 2, '650200': 2,
                    '650300': 2,
                    '650400': 2, '650500': 2, '710100': 2, '710300': 2, '710400': 2, '720400': 2, '720500': 2,
                    '720600': 2,
                    '720700': 2, '720800': 2, '720900': 2, '721000': 2, '730100': 2, '730200': 2, '340800': 2,
                    '340900': 2,
                    '350100': 2, '350200': 2, '350300': 2, '360100': 2, '360200': 2, '220602': 3, '220603': 3,
                    '220604': 3,
                    '220801': 3, '220802': 3, '220803': 3, '220804': 3, '220805': 3, '220901': 3, '230301': 3,
                    '230302': 3,
                    '230401': 3, '230402': 3, '230403': 3, '230501': 3, '240201': 3, '240202': 3, '240301': 3,
                    '240302': 3,
                    '240303': 3, '240401': 3, '240402': 3, '240501': 3, '240502': 3, '240504': 3, '240505': 3,
                    '240601': 3,
                    '240602': 3, '240603': 3, '270102': 3, '270103': 3, '270104': 3, '270105': 3, '270106': 3,
                    '270107': 3,
                    '270108': 3, '270202': 3, '270203': 3, '270301': 3, '270302': 3, '270303': 3, '270401': 3,
                    '280401': 3,
                    '280402': 3, '280501': 3, '280502': 3, '280601': 3, '280602': 3, '330102': 3, '330106': 3,
                    '330201': 3,
                    '330202': 3, '330301': 3, '330302': 3, '330303': 3, '330401': 3, '330402': 3, '330501': 3,
                    '330601': 3,
                    '330701': 3, '340401': 3, '340404': 3, '340406': 3, '340407': 3, '340501': 3, '340601': 3,
                    '340602': 3,
                    '340701': 3, '340702': 3, '110101': 3, '110102': 3, '110103': 3, '110104': 3, '110201': 3,
                    '110202': 3,
                    '110301': 3, '110402': 3, '110403': 3, '110404': 3, '110501': 3, '110502': 3, '110504': 3,
                    '110702': 3,
                    '110703': 3, '110704': 3, '110801': 3, '110901': 3, '220201': 3, '220202': 3, '220203': 3,
                    '220204': 3,
                    '220205': 3, '220206': 3, '220305': 3, '220307': 3, '220308': 3, '220309': 3, '220311': 3,
                    '220313': 3,
                    '220315': 3, '220316': 3, '220317': 3, '220401': 3, '220403': 3, '220404': 3, '220405': 3,
                    '220406': 3,
                    '220501': 3, '220503': 3, '220504': 3, '220505': 3, '360306': 3, '360307': 3, '360308': 3,
                    '360309': 3,
                    '360311': 3, '360501': 3, '360502': 3, '370101': 3, '370102': 3, '370201': 3, '370302': 3,
                    '370303': 3,
                    '370304': 3, '370402': 3, '370403': 3, '370404': 3, '370502': 3, '370503': 3, '370504': 3,
                    '370602': 3,
                    '370603': 3, '370604': 3, '370605': 3, '410101': 3, '410102': 3, '410104': 3, '410106': 3,
                    '410107': 3,
                    '410108': 3, '410109': 3, '410110': 3, '410301': 3, '420802': 3, '420803': 3, '420804': 3,
                    '420805': 3,
                    '420806': 3, '420807': 3, '420901': 3, '420902': 3, '420903': 3, '421001': 3, '421002': 3,
                    '421101': 3,
                    '421102': 3, '430101': 3, '430102': 3, '430103': 3, '430301': 3, '430302': 3, '430303': 3,
                    '450201': 3,
                    '450301': 3, '450302': 3, '450303': 3, '450304': 3, '450401': 3, '450601': 3, '450602': 3,
                    '450603': 3,
                    '450701': 3, '460601': 3, '460701': 3, '460801': 3, '460802': 3, '460803': 3, '460804': 3,
                    '460901': 3,
                    '460902': 3, '461001': 3, '461002': 3, '461003': 3, '461004': 3, '461101': 3, '461102': 3,
                    '461103': 3,
                    '480201': 3, '480301': 3, '480401': 3, '480501': 3, '480601': 3, '490101': 3, '490201': 3,
                    '490302': 3,
                    '490303': 3, '490304': 3, '490305': 3, '490306': 3, '490307': 3, '490308': 3, '510101': 3,
                    '610101': 3,
                    '610102': 3, '730205': 3, '730206': 3, '730207': 3, '740101': 3, '740102': 3, '740201': 3,
                    '750101': 3,
                    '750201': 3, '750202': 3, '750301': 3, '750302': 3, '750303': 3, '760101': 3, '760102': 3,
                    '760103': 3,
                    '760104': 3, '760201': 3, '770101': 3, '770102': 3, '770201': 3, '770202': 3, '270503': 3,
                    '270504': 3,
                    '270601': 3, '280202': 3, '280203': 3, '280204': 3, '280205': 3, '280206': 3, '280302': 3,
                    '280303': 3,
                    '610201': 3, '610202': 3, '610301': 3, '610302': 3, '610303': 3, '610304': 3, '610305': 3,
                    '620101': 3,
                    '620201': 3, '620306': 3, '620307': 3, '620401': 3, '620402': 3, '620403': 3, '620404': 3,
                    '620601': 3,
                    '630101': 3, '630301': 3, '630304': 3, '630306': 3, '630501': 3, '630502': 3, '630503': 3,
                    '630504': 3,
                    '630505': 3, '630601': 3, '630602': 3, '630701': 3, '630702': 3, '630703': 3, '630704': 3,
                    '630705': 3,
                    '630801': 3, '630802': 3, '630803': 3, '630804': 3, '630805': 3, '640101': 3, '640103': 3,
                    '640105': 3,
                    '640106': 3, '640107': 3, '640108': 3, '640203': 3, '640204': 3, '640206': 3, '640207': 3,
                    '640208': 3,
                    '640209': 3, '640501': 3, '640601': 3, '640602': 3, '640701': 3, '640702': 3, '640703': 3,
                    '640704': 3,
                    '650101': 3, '650201': 3, '650301': 3, '650401': 3, '650501': 3, '710102': 3, '710103': 3,
                    '710301': 3,
                    '710401': 3, '710402': 3, '720401': 3, '720501': 3, '720502': 3, '720601': 3, '720602': 3,
                    '720701': 3,
                    '720702': 3, '720703': 3, '720704': 3, '720705': 3, '720706': 3, '720801': 3, '720901': 3,
                    '720902': 3,
                    '720903': 3, '721001': 3, '730102': 3, '730103': 3, '730104': 3, '730204': 3, '340801': 3,
                    '340802': 3,
                    '340803': 3, '340901': 3, '350102': 3, '350104': 3, '350105': 3, '350106': 3, '350107': 3,
                    '350205': 3,
                    '350206': 3, '350208': 3, '350209': 3, '350301': 3, '350302': 3, '350303': 3, '360102': 3,
                    '360103': 3,
                    '360202': 3, '360203': 3, '360204': 3, '360205': 3, '360206': 3, '770301': 3, '770302': 3}

    zjh_level_map = {'B': 1, 'C': 1, 'A': 1, 'D': 1, 'E': 1, 'F': 1, 'G': 1, 'H': 1, 'I': 1, 'J': 1, 'K': 1, 'L': 1,
                     'M': 1, 'N': 1, 'O': 1, 'P': 1, 'Q': 1, 'R': 1, 'S': 1, 'A03': 2, 'A04': 2, 'A05': 2, 'B06': 2,
                     'B07': 2, 'B08': 2, 'B09': 2, 'B10': 2, 'B11': 2, 'B12': 2, 'C13': 2, 'C14': 2, 'C15': 2, 'C16': 2,
                     'C17': 2, 'C18': 2, 'C19': 2, 'C20': 2, 'C21': 2, 'C22': 2, 'C23': 2, 'C24': 2, 'C25': 2, 'C26': 2,
                     'C27': 2, 'C28': 2, 'C29': 2, 'C30': 2, 'C31': 2, 'C32': 2, 'C33': 2, 'C34': 2, 'C35': 2, 'C36': 2,
                     'C37': 2, 'C38': 2, 'C39': 2, 'C40': 2, 'C41': 2, 'C42': 2, 'C43': 2, 'D44': 2, 'D45': 2, 'D46': 2,
                     'E47': 2, 'E48': 2, 'E49': 2, 'E50': 2, 'F51': 2, 'F52': 2, 'G53': 2, 'G54': 2, 'G55': 2, 'G56': 2,
                     'G57': 2, 'G58': 2, 'G59': 2, 'G60': 2, 'H61': 2, 'H62': 2, 'I63': 2, 'I64': 2, 'I65': 2, 'J66': 2,
                     'J67': 2, 'J68': 2, 'J69': 2, 'K70': 2, 'L71': 2, 'L72': 2, 'M73': 2, 'M74': 2, 'M75': 2, 'N76': 2,
                     'N77': 2, 'N78': 2, 'O79': 2, 'O80': 2, 'O81': 2, 'P82': 2, 'Q83': 2, 'Q84': 2, 'R85': 2, 'R86': 2,
                     'R87': 2, 'R88': 2, 'R89': 2, 'S90': 2, 'A01': 2, 'A02': 2}

    params = {}

    code_level = None
    if classified == 'sw':
        params["INDU_STANDARD_CODE"] = "46"
        if industry_code:
            try:
                code_level = sw_level_map[industry_code]
            except:
                return 'industry_code dose not exist'

    else:
        params["INDU_STANDARD_CODE"] = "36"
        if industry_code:
            try:
                code_level = zjh_level_map[industry_code]
            except:
                return 'industry_code dose not exist'

    if code_level:
        if code_level == 1:
            params["FINDU_CODE"] = industry_code
        elif code_level == 2:
            params["SINDU_CODE"] = industry_code
        elif code_level == 3:
            params["TINDU_CODE"] = industry_code

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)

        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)
        df_result["classified"] = classified
        r_result = df_result[["htsc_code", "classified", "name", "exchange", "industry_name", "industry_code",
                              "l1_code", "l1_name", "l2_code", "l2_name", "l3_code", "l3_name"]]
        return r_result
    return result


# 新股上市
def get_new_share_handle(htsc_code, book_start_date_online, listing_date):
    query_type = 1101040001

    params = {}

    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if book_start_date_online:
        book_start_date_online_start_date = datetime.strftime(book_start_date_online[0], '%Y%m%d')
        book_start_date_online_end_date = datetime.strftime(book_start_date_online[1], '%Y%m%d')
        params["BOOK_START_DATE_ON_START_DATE"] = book_start_date_online_start_date
        params["BOOK_START_DATE_ON_END_DATE"] = book_start_date_online_end_date
    else:
        params["BOOK_START_DATE_ON_START_DATE"] = ''
        params["BOOK_START_DATE_ON_END_DATE"] = ''

    if listing_date:
        listing_date_start_date = datetime.strftime(listing_date[0], '%Y%m%d')
        listing_date_end_date = datetime.strftime(listing_date[1], '%Y%m%d')
        params["LISTING_DATE_START_DATE"] = listing_date_start_date
        params["LISTING_DATE_END_DATE"] = listing_date_end_date
    else:
        params["LISTING_DATE_START_DATE"] = ''
        params["LISTING_DATE_END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'exchange', 'issue_price', 'par_value', 'raise_net_fund_planned', 'raise_net_fund',
             'raise_fund',
             'issue_share_online_plan', 'issue_share', 'total_share_before_issue',
             'eps_before_issue', 'eps_after_issue', 'bps_before_issue', 'bps_after_issue',
             'pe_before_issue', 'pe_after_issue', 'pb_issue', 'val_pe', 'listing_date',
             'book_start_date_online', 'book_end_date_online',
             'issue_share_online', 'ceiling_apply_share', 'floor_apply_share', 'allot_rate_online']]
        return c_result

    return result


# 日行情接口
def get_daily_basic_handle(htsc_code, trading_day):
    query_type = 1101080003

    params = {}

    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if trading_day:
        start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["START_DATE"] = start_date
        params["END_DATE"] = end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    params['ORDER_BY'] = 'TRADINGDAY,TRADINGCODE'

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'exchange', 'trading_day', 'trading_state', 'prev_close', 'open',
             'high', 'low', 'close', 'backward_adjusted_closing_price', 'volume', 'value', 'turnover_deals',
             'day_change', 'turnover_rate', 'amplitude', 'avg_price', 'avg_vol_per_deal', 'avg_value_per_deal',
             'floating_market_val', 'total_market_val']]
        return c_result

    return result


# 市值数据
def get_stock_valuation_handle(htsc_code, trading_day):
    query_type = 1101080004

    params = {}

    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if trading_day:
        start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["START_DATE"] = start_date
        params["END_DATE"] = end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'exchange', 'trading_day', 'close', 'backward_adjusted_closing_price',
             'forward_adjusted_closing_price', 'pe', 'pettm', 'pb', 'pc', 'pcttm', 'ps', 'psttm', 'avg_price',
             'avg_vol_per_deal', 'avg_value_per_deal', 'floating_market_val', 'total_market_val']]
        return c_result

    return result


# 债券基础信息-通过华泰证券代码查询
def get_bond_info_handle(htsc_code, secu_category_code, listing_date, issue_start_date, end_date):
    query_type = 1103010001

    params = {}

    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if secu_category_code:
        params["SECU_CATEGORY_CODE_II"] = secu_category_code
    else:
        params["SECU_CATEGORY_CODE_II"] = ''

    if listing_date:
        listing_date_start_date = datetime.strftime(listing_date[0], '%Y%m%d')
        listing_date_end_date = datetime.strftime(listing_date[1], '%Y%m%d')
        params["LISTING_DATE_START_DATE"] = listing_date_start_date
        params["LISTING_DATE_END_DATE"] = listing_date_end_date
    else:
        params["LISTING_DATE_START_DATE"] = ''
        params["LISTING_DATE_END_DATE"] = ''

    if issue_start_date:
        issue_date_start_date = datetime.strftime(issue_start_date[0], '%Y%m%d')
        issue_date_end_date = datetime.strftime(issue_start_date[1], '%Y%m%d')
        params["ISSUE_START_DATE_START_DATE"] = issue_date_start_date
        params["ISSUE_START_DATE_END_DATE"] = issue_date_end_date
    else:
        params["ISSUE_START_DATE_START_DATE"] = ''
        params["ISSUE_START_DATE_END_DATE"] = ''

    if end_date:
        end_date_start_date = datetime.strftime(end_date[0], '%Y%m%d')
        end_date_end_date = datetime.strftime(end_date[1], '%Y%m%d')
        params["END_DATE_START_DATE"] = end_date_start_date
        params["END_DATE_END_DATE"] = end_date_end_date
    else:
        params["END_DATE_START_DATE"] = ''
        params["END_DATE_END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'secu_category_code', 'exchange', 'category', 'listing_date', 'delisting_date',
             'currency_code', 'bond_maturity', 'issue_start_date', 'accrued_date', 'end_date',
             'issue_size', 'bond_formcode', 'bond_form', 'interest_method', 'payment_method', 'payment_frequency',
             'coupon_rate', 'ref_spread', 'ref_rate', 'redemption_date', 'interest_formula', 'interest_rate_floor',
             'par_value', 'issue_price', 'convert_code', 'bond_rating', 'interest_stop_date', 'bond_type_name',
             'call_date', 'call_price', 'putt_date', 'putt_price', 'mtn', 'delist_date', 'year_payment_date',
             'interest_rate_desc', 'issuer_main', 'compensation_rate', 'fig_interest_method', 'expan_yield',
             'bond_type', 'issue_mode', 'issue_type', 'category_code_i', 'category_name_i', 'category_code_ii',
             'category_name_ii', 'interest_rate', 'interest_method_desc', 'remain_maturity', 'expect_end_date']]
        return c_result

    return result


# 债券基础信息-通过华泰证券市场查询
def get_all_bonds_handle(exchange, secu_category_code, listing_date, issue_start_date, end_date):
    query_type = 1103010001

    params = {}

    exchange_code_map = {'XSHG': '101', 'XSHE': '105', 'XCFE': '113', 'XSHGFI': '116', 'OTC': '701', 'XSHECA': '702',
                         'OTHERS': '999'}

    if exchange:
        try:
            params["EXCHANGE_CODE"] = exchange_code_map[exchange]
        except:
            return 'exchange does not exist'
    else:
        params["EXCHANGE_CODE"] = ''

    if secu_category_code:
        params["SECU_CATEGORY_CODE_II"] = secu_category_code
    else:
        params["SECU_CATEGORY_CODE_II"] = ''

    if listing_date:
        listing_date_start_date = datetime.strftime(listing_date[0], '%Y%m%d')
        listing_date_end_date = datetime.strftime(listing_date[1], '%Y%m%d')
        params["LISTING_DATE_START_DATE"] = listing_date_start_date
        params["LISTING_DATE_END_DATE"] = listing_date_end_date
    else:
        params["LISTING_DATE_START_DATE"] = ''
        params["LISTING_DATE_END_DATE"] = ''

    if issue_start_date:
        issue_date_start_date = datetime.strftime(issue_start_date[0], '%Y%m%d')
        issue_date_end_date = datetime.strftime(issue_start_date[1], '%Y%m%d')
        params["ISSUE_START_DATE_START_DATE"] = issue_date_start_date
        params["ISSUE_START_DATE_END_DATE"] = issue_date_end_date
    else:
        params["ISSUE_START_DATE_START_DATE"] = ''
        params["ISSUE_START_DATE_END_DATE"] = ''

    if end_date:
        end_date_start_date = datetime.strftime(end_date[0], '%Y%m%d')
        end_date_end_date = datetime.strftime(end_date[1], '%Y%m%d')
        params["END_DATE_START_DATE"] = end_date_start_date
        params["END_DATE_END_DATE"] = end_date_end_date
    else:
        params["END_DATE_START_DATE"] = ''
        params["END_DATE_END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'exchange', 'secu_category_code', 'category', 'listing_date', 'delisting_date',
             'currency_code', 'bond_maturity', 'issue_start_date', 'accrued_date', 'end_date',
             'issue_size', 'bond_rating', 'bond_type']]

        return c_result

    return result


# 债券回购行情
def get_repo_price_handle(htsc_code, exchange, trading_day):
    query_type = 1103020001

    exchange_code_map = {'XSHG': '101', 'XSHE': '105', 'XCFE': '113', 'XSHGFI': '116', 'OTC': '701', 'XSHECA': '702',
                         'OTHERS': '999'}

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if exchange:
        try:
            params["EXCHANGE_CODE"] = exchange_code_map[exchange]
        except:
            return 'exchange does not exist'
    else:
        params["EXCHANGE_CODE"] = ''

    if trading_day:
        trading_day_start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        trading_day_end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["TRADING_DAY_START_DATE"] = trading_day_start_date
        params["TRADING_DAY_END_DATE"] = trading_day_end_date
    else:
        params["TRADING_DAY_START_DATE"] = ''
        params["TRADING_DAY_END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[['trading_day', 'htsc_code', 'name', 'exchange', 'last_close_rate', 'open_rate',
                              'close_rate', 'highest_rate', 'lowest_rate', 'volume', 'value',
                              'avg_turnover_vol', 'avg_turnover_val', 'turnover_deals', 'avg_rate', 'day_change',
                              'day_change_rate', 'amplitude', 'last_avg_rate']]
        return c_result
    return result


# 可转债发行列表
def get_new_con_bond_handle(htsc_code, exchange, book_start_date_online, listing_date, issue_date, convert_code):
    query_type = 1103030001
    exchange_code_map = {'XSHG': '101', 'XSHE': '105', 'XCFE': '113', 'XSHGFI': '116', 'OTC': '701', 'XSHECA': '702',
                         'OTHERS': '999'}

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if exchange:
        try:
            params["EXCHANGE_CODE"] = exchange_code_map[exchange]
        except:
            return 'exchange does not exist'
    else:
        params["EXCHANGE_CODE"] = ''

    if book_start_date_online:
        book_start_date_online_start_date = datetime.strftime(book_start_date_online[0], '%Y%m%d')
        book_start_date_online_end_date = datetime.strftime(book_start_date_online[1], '%Y%m%d')
        params["BOOK_START_DATE_ON_START_DATE"] = book_start_date_online_start_date
        params["BOOK_START_DATE_ON_END_DATE"] = book_start_date_online_end_date
    else:
        params["BOOK_START_DATE_ON_START_DATE"] = ''
        params["BOOK_START_DATE_ON_END_DATE"] = ''

    if listing_date:
        listing_date_start_date = datetime.strftime(listing_date[0], '%Y%m%d')
        listing_date_end_date = datetime.strftime(listing_date[1], '%Y%m%d')
        params["LISTING_DATE_START_DATE"] = listing_date_start_date
        params["LISTING_DATE_END_DATE"] = listing_date_end_date
    else:
        params["LISTING_DATE_START_DATE"] = ''
        params["LISTING_DATE_END_DATE"] = ''

    if issue_date:
        issue_date_start_date = datetime.strftime(issue_date[0], '%Y%m%d')
        issue_date_end_date = datetime.strftime(issue_date[1], '%Y%m%d')
        params["ISSUE_START_DATE_START_DATE"] = issue_date_start_date
        params["ISSUE_START_DATE_END_DATE"] = issue_date_end_date
    else:
        params["ISSUE_START_DATE_START_DATE"] = ''
        params["ISSUE_START_DATE_END_DATE"] = ''

    if convert_code:
        params['CONVERT_CODE'] = convert_code

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[['htsc_code', 'name', 'exchange_code', 'exchange', 'bnd_type', 'listing_date',
                              'issue_start_date', 'rating_code', 'book_start_date_online', 'capply_online',
                              'allot_rate_sh', 'apply_price', 'issue_price', 'apply_code', 'convert_code',
                              'convert_abbr', 'conversion_price', 'bond_maturity', 'issue_size', 'issue_val_plan',
                              'preferred_placing_code', 'apply_abbr', 'preferred_placing_abbr',
                              'succ_result_notice_date', 'exchange_code_detail', 'purchase_lower_online']]
        return c_result
    return result


# 债券市场行情
def get_bond_price_handle(htsc_code, exchange, trading_day):
    query_type = 1103020002
    exchange_code_map = {'XSHG': '101', 'XSHE': '105', 'XCFE': '113', 'XSHGFI': '116', 'OTC': '701', 'XSHECA': '702',
                         'OTHERS': '999'}

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if exchange:
        try:
            params["EXCHANGE_CODE"] = exchange_code_map[exchange]
        except:
            return 'exchange does not exist'
    else:
        params["EXCHANGE_CODE"] = ''

    if trading_day:
        trading_day_start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        trading_day_end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["TRADING_DAY_START_DATE"] = trading_day_start_date
        params["TRADING_DAY_END_DATE"] = trading_day_end_date
    else:
        params["TRADING_DAY_START_DATE"] = ''
        params["TRADING_DAY_END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[['htsc_code', 'name', 'category', 'exchange', 'trading_day', 'w_avg_net_price',
                              'w_avg_ai', 'net_prev_closing_price', 'net_prev_avg_closing_price', 'net_opening_price',
                              'net_highest_price', 'net_lowest_price', 'net_closing_price', 'net_avg_closing_price',
                              'net_day_change_rate', 'net_amplitude', 'accrued_interest', 'full_prev_closing_price',
                              'full_prev_avg_closing_price', 'full_opening_price', 'full_highest_price',
                              'full_lowest_price', 'full_closing_price', 'full_avg_closing_price',
                              'full_day_change_rate',
                              'full_amplitude', 'principal_val', 'par_val_vol', 'turnover_deals', 'turnover_rate',
                              'year_to_maturity', 'duration', 'modified_duration', 'convexity', 'yield_to_maturity',
                              'return_of_interest', 'return_of_price', 'total_return', 'opening_yield', 'highest_yield',
                              'lowest_yield', 'avg_closing_yield']]
        return c_result
    return result


# 可转债赎回信息
def get_con_bond_redemption_handle(htsc_code, exchange, register_date):
    query_type = 1103030002

    exchange_code_map = {'XSHG': '101', 'XSHE': '105', 'XCFE': '113', 'XSHGFI': '116', 'OTC': '701', 'XSHECA': '702',
                         'OTHERS': '999', 'XBSE': '106', 'NEEQ': '111'}

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if exchange:
        try:
            params["EXCHANGE_CODE"] = exchange_code_map[exchange]
        except:
            return 'exchange does not exist'
    else:
        params["EXCHANGE_CODE"] = ''

    if register_date:
        register_date_start_date = datetime.strftime(register_date[0], '%Y%m%d')
        register_date_end_date = datetime.strftime(register_date[1], '%Y%m%d')
        params["REGISTER_DATE_START_DATE"] = register_date_start_date
        params["REGISTER_DATE_END_DATE"] = register_date_end_date
    else:
        params["REGISTER_DATE_START_DATE"] = ''
        params["REGISTER_DATE_END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[['htsc_code', 'pub_date', 'exchange', 'type', 'reason', 'redemption_type', 'begin_date',
                              'end_date', 'exer_price', 'is_include_interest', 'curr_qut', 'curr_amt', 'payment_date',
                              'fund_receive_date', 'register_date', 'announcement_date']]
        return c_result
    return result


# 可转债转股价变动
def get_con_bond_2_shares_change_handle(htsc_code, exchange, pub_date, convert_code):
    query_type = 1103030003
    exchange_code_map = {'XSHG': '101', 'XSHE': '105', 'XCFE': '113', 'XSHGFI': '116', 'OTC': '701', 'XSHECA': '702',
                         'OTHERS': '999', 'XBSE': '106', 'NEEQ': '111'}

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if exchange:
        try:
            params["EXCHANGE_CODE"] = exchange_code_map[exchange]
        except:
            return 'exchange does not exist'
    else:
        params["EXCHANGE_CODE"] = ''

    if pub_date:
        pub_date_start_date = datetime.strftime(pub_date[0], '%Y%m%d')
        pub_date_end_date = datetime.strftime(pub_date[1], '%Y%m%d')
        params["DECLARE_DATE_START_DATE"] = pub_date_start_date
        params["DECLARE_DATE_END_DATE"] = pub_date_end_date
    else:
        params["DECLARE_DATE_START_DATE"] = ''
        params["DECLARE_DATE_END_DATE"] = ''

    if convert_code:
        params['STK_CODE'] = convert_code

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[['htsc_code', 'exchange', 'convert_code', 'stk_secu_code', 'stk_exchange_code',
                              'pub_date', 'val_beg_date', 'val_end_date', 'events_type', 'events_type_details',
                              'cvt_ratio', 'cvt_price', 'init_cvt_price', 'bef_cvt_price']]
        return c_result
    return result


# 可转债转股结果
def get_con_bond_2_shares_handle(htsc_code, pub_date, exer_begin_date, exer_end_date, convert_code, exchange):
    query_type = 1103030004
    exchange_code_map = {'XSHG': '101', 'XSHE': '105', 'XCFE': '113', 'XSHGFI': '116', 'OTC': '701', 'XSHECA': '702',
                         'OTHERS': '999', 'XBSE': '106', 'NEEQ': '111'}

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if exchange:
        try:
            params["EXCHANGE_CODE"] = exchange_code_map[exchange]
        except:
            return 'exchange does not exist'
    else:
        params["EXCHANGE_CODE"] = ''

    if pub_date:
        pub_date_start_date = datetime.strftime(pub_date[0], '%Y%m%d')
        pub_date_end_date = datetime.strftime(pub_date[1], '%Y%m%d')
        params["PUB_DATE_START_DATE"] = pub_date_start_date
        params["PUB_DATE_END_DATE"] = pub_date_end_date
    else:
        params["PUB_DATE_START_DATE"] = ''
        params["PUB_DATE_END_DATE"] = ''

    if exer_begin_date:
        exer_begin_date_start_date = datetime.strftime(exer_begin_date[0], '%Y%m%d')
        exer_begin_date_end_date = datetime.strftime(exer_begin_date[1], '%Y%m%d')
        params["EXER_BEG_DATE_START_DATE"] = exer_begin_date_start_date
        params["EXER_BEG_DATE_END_DATE"] = exer_begin_date_end_date
    else:
        params["EXER_BEG_DATE_START_DATE"] = ''
        params["EXER_BEG_DATE_END_DATE"] = ''

    if exer_end_date:
        exer_end_date_start_date = datetime.strftime(exer_end_date[0], '%Y%m%d')
        exer_end_date_end_date = datetime.strftime(exer_end_date[1], '%Y%m%d')
        params["EXER_END_DATE_START_DATE"] = exer_end_date_start_date
        params["EXER_END_DATE_END_DATE"] = exer_end_date_end_date
    else:
        params["EXER_END_DATE_START_DATE"] = ''
        params["EXER_END_DATE_END_DATE"] = ''

    if convert_code:
        params['SK_CODE'] = convert_code

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[['htsc_code', 'pub_date', 'exchange', 'exer_type', 'exer_begin_date', 'exer_end_date',
                              'cvt_ratio', 'cvt_price', 'cvt_vol_cur', 'cvt_acc_stock_vol', 'cvt_acc_amt',
                              'cvt_act_price', 'cvt_acc_vol', 'cvt_tot_ratio', 'outstanding_amt', 'afcvt_cap',
                              'convert_code', 'actual_issue_amt', 'init_cvt_price', 'cvt_amt']]
        return c_result

    return result


# 利润表
def get_income_statement_handle(htsc_code, end_date, period):
    query_type = 1101070002

    period_map = {"Q1": "1", "Q2": "6", "Q3": "9", "Q4": "12"}

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if period:
        try:
            params['REPORT_TYPE'] = period_map[period]
        except:
            return 'period does not exist'
    else:
        params['REPORT_TYPE'] = ''

    if end_date:
        end_date_start_date = datetime.strftime(end_date[0], '%Y%m%d')
        end_date_end_date = datetime.strftime(end_date[1], '%Y%m%d')
        params["START_DATE"] = end_date_start_date
        params["END_DATE"] = end_date_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'pub_date', 'end_date', 'total_oper_revenue', 'oper_revenue', 'interest_income',
             'premium_earned', 'commission_income', 'rem_revenue', 'other_oper_revenue', 'total_oper_cost', 'oper_cost',
             'interest_expense', 'commission_net_income', 'rem_cost', 'cap_develop_cost', 'surrender_premium',
             'net_indemnity_expense', 'net_contact_reserver', 'dive_policy_expense', 'reinsurance_expense',
             'other_oper_cost', 'business_tax_sur_tax', 'sell_expense', 'admin_expense', 'fin_cost',
             'asset_impairment_loss', 'fair_val_gain', 'inv_income', 'ajent_inv_income', 'exchange_gain', 'future_loss',
             'trust_income', 'bonus_income', 'other_oper_profit', 'oper_profit', 'non_oper_revenue', 'non_oper_expense',
             'non_cur_asset_disp_lost', 'total_profit', 'income_tax_expense', 'sgm_invest_loss', 'net_profit',
             'net_profit_coms', 'net_work_profit', 'minority_profit', 'basic_eps', 'diluted_eps', 'other_hole_profit',
             'net_other_profit_coms', 'net_less_profit_coms', 'general_total_income', 'net_general_total_income',
             'net_less_profit_income', 'entry_time', 'update_time', 'ground_time', 'update_id', 'record_id',
             'opinion_code', 'period', 'interest_net_income', 'oper_admin_expense']]
        period_reverse_map = {1: 'Q1', 6: 'Q2', 9: 'Q3', 12: 'Q4'}
        c_result = c_result.copy()
        c_result['period'] = c_result['period'].apply(lambda x: period_reverse_map[x])

        return c_result

    return result


# 资产负债表
def get_balance_sheet_handle(htsc_code, end_date, period):
    query_type = 1101070001

    period_map = {"Q1": "1", "Q2": "6", "Q3": "9", "Q4": "12"}

    params = {"DATA_FLAG": "102"}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if period:
        try:
            params['REPORT_TYPE'] = period_map[period]
        except:
            return 'period does not exist'
    else:
        params['REPORT_TYPE'] = ''

    if end_date:
        end_date_start_date = datetime.strftime(end_date[0], '%Y%m%d')
        end_date_end_date = datetime.strftime(end_date[1], '%Y%m%d')
        params["START_DATE"] = end_date_start_date
        params["END_DATE"] = end_date_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        # 筛选原始报表
        df_result = change_column_name(df_result)
        c_result = df_result[
            ['htsc_code', 'name', 'pub_date', 'end_date', 'monetary_fund', 'settlement_provision', 'fund_lending',
             'trad_fina_asset', 'deri_fina_asset', 'note_rec', 'account_rec', 'advance_to_supplier', 'premium_rec',
             'reinsurance_rec', 'rcontact_reserverec', 'interest_rec', 'devidend_rec', 'other_rec', 'rexport_refund',
             'rsubsidy', 'rmargin', 'inter_contribution', 'purchased_resell_fina_asset', 'inventory', 'expenses',
             'process_fluxion', 'non_cur_asset_one_year', 'other_curasset', 'total_cur_asset', 'loan_advance',
             'avai_sale_fina_asset', 'held_maturity_inv', 'lt_account_rec', 'lt_equity_inv', 'other_lt_equity_inv',
             'inv_property', 'fixed_assets_before', 'agg_depreciation', 'fixed_nav', 'fixed_wd_prepare',
             'fixed_asset_net', 'construction_progress', 'construction_material', 'liquidation_fixed_asset',
             'production_biology_asset', 'profit_biology_asset', 'oil_gas_asset', 'intangible_asset', 'develop_exp',
             'good_will', 'lt_deferred_asset', 'share_dis_lr', 'deferred_income_tax_asset', 'other_non_cur_asset',
             'total_non_cur_asset', 'total_asset', 'st_borrowing', 'borrowing_from_cbank', 'deposit', 'fund_borrowing',
             'trad_fina_liab', 'deri_fina_liab', 'notes_pay', 'account_pay', 'advance_from_customer',
             'sold_repo_fina_asset', 'commission_pay', 'payroll_pay', 'tax_pay', 'interest_pay', 'dividend_pay',
             'other_should_pay', 'should_pay_margin', 'inner_should_pay', 'other_account_pay', 'accrued_expense',
             'pre_cast_cl', 'reinsurance_pay', 'coi_reserve_fund', 'secu_proxy_money', 'secu_underwriting_money',
             'nation_purchase_balance', 'so_fina_purchase_balance', 'deferred_income', 'pay_short_bond',
             'non_cur_liab_one_year', 'other_cur_liab', 'total_cur_liab', 'lt_borrowing', 'bond_pay', 'lt_account_pay',
             'special_pay', 'long_deferr_tax', 'pre_cast_uncurr_debt', 'deferred_income_tax_liab', 'other_non_cur_liab',
             'total_non_cur_liab', 'total_liab', 'share_capital', 'capital_reserve', 'inventory_share',
             'surplus_reserve', 'general_risk_provision', 'uninvestment_loss', 'retained_earning',
             'allo_cash_dividends', 'diff_conversion_fc', 'sh_equity_parent_com', 'min_shareholder_equity',
             'total_sh_equity', 'total_liab_sh_equity', 'opinion_code', 'total_interest_liabi_ratio',
             'monetary_fund_ratio', 'account_rec_ratio', 'inventory_ratio', 'fixed_asset_net_ratio',
             'other_cur_asset_ratio', 'lt_account_rec_ratio', 'lt_equity_inv_ratio', 'good_will_ratio', 'entry_time',
             'update_time', 'ground_time', 'update_id', 'record_id', 'period', 'cash_deposit_inc_bank',
             'deposit_in_other_bank', 'deposit_from_other_bank', 'other_asset', 'other_liab']]
        period_reverse_map = {1: 'Q1', 6: 'Q2', 9: 'Q3', 12: 'Q4'}
        c_result = c_result.copy()
        c_result['period'] = c_result['period'].apply(lambda x: period_reverse_map[x])
        return c_result

    return result


# 现金流量表
def get_cashflow_statement_handle(htsc_code, end_date, period):
    query_type = 1101070003

    period_map = {"Q1": "1", "Q2": "6", "Q3": "9", "Q4": "12"}

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if period:
        try:
            params['REPORT_TYPE'] = period_map[period]
        except:
            return 'period does not exist'
    else:
        params['REPORT_TYPE'] = ''

    if end_date:
        end_date_start_date = datetime.strftime(end_date[0], '%Y%m%d')
        end_date_end_date = datetime.strftime(end_date[1], '%Y%m%d')
        params["START_DATE"] = end_date_start_date
        params["END_DATE"] = end_date_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)
        c_result = df_result[
            ['htsc_code', 'name', 'pub_date', 'end_date', 'cash_recsale_goods_service', 'net_incr_deposit',
             'net_incr_borrowing_cbank', 'net_incr_borrowing_ibank', 'cash_rec_premium', 'net_cash_rec_reinserance',
             'net_incr_insurer_deposit_inv', 'net_incr_disp_trad_fina_asset', 'cash_rec_commission',
             'net_incr_borrowing', 'net_incr_repo', 'tax_refund', 'cash_rec_other_oper', 'sub_total_cash_in_oper',
             'cash_paid_sale_goods_service', 'net_incr_loan', 'net_incr_deposit_cbib', 'cash_paid_indemnity',
             'cash_paid_inte_commission', 'cash_paid_divi', 'cash_paid_employee', 'tax_paid', 'cash_paid_other_oper',
             'sub_total_cash_out_oper', 'net_cash_flow_operq', 'cash_rec_inv', 'cash_rec_divi_inv',
             'net_cash_rec_disp_fi_asset', 'net_cash_rec_disp_sub_busi', 'cash_rec_other_inv', 'reduce_impawn_cash',
             'sub_total_cash_in_inv', 'cash_paid_fi_asset', 'cash_paid_inv', 'net_incr_pledge_loan',
             'net_cash_paid_acqu_sub_busi', 'cash_paid_other_inv', 'add_impawn_cash', 'sub_total_cash_out_inv',
             'net_cash_flow_inv', 'cash_rec_inv_fina', 'cash_rec_fina_from_mshe_inv', 'cash_rec_loan',
             'cash_rec_issue_bond', 'cash_rec_other_fina', 'sub_total_cash_in_fina', 'debt_repay',
             'cash_paid_divi_profi_nte', 'sub_compay_profit', 'cash_paid_other_fina', 'sub_total_cash_out_fina',
             'net_cash_flow_fina', 'effect_foreign_ex_rate', 'cashequibeginning', 'cashequiending', 'net_profit',
             'min_shareholder_equity', 'stu_inv_loss', 'asset_impairment_prov', 'fixed_asset_depr',
             'amor_intangible_asset', 'amor_lt_expense', 'reduce_prepaid', 'add_accrued', 'loss_disp_fi_asset',
             'loss_fixed_asset', 'fair_val_gain', 'add_deferr_income', 'provision', 'fin_cost', 'inv_loss',
             'deferred_tax_asset_decr', 'deferred_tax_liab_decr', 'inventory_decr', 'oper_rec_decr', 'oper_pay_incr',
             'reduce_not_completed', 'add_settle_not_completed', 'other_item', 'net_cash_flow_oper', 'debt_to_capital',
             'con_bond_one_year', 'fina_leased_fixed_asset', 'cash_ending', 'cash_beginning', 'equi_ending',
             'equi_beginning', 'cash_equi_net_incr', 'entry_time', 'update_time', 'ground_time', 'update_id',
             'record_id', 'opinion_code', 'period']]
        period_reverse_map = {1: 'Q1', 6: 'Q2', 9: 'Q3', 12: 'Q4'}
        c_result = c_result.copy()
        c_result['period'] = c_result['period'].apply(lambda x: period_reverse_map[x])
        return c_result

    return result


# 财务指标
def get_fin_indicator_handle(htsc_code, end_date, period):
    query_type = 1101070013

    period_map = {"Q1": "1", "Q2": "6", "Q3": "9", "Q4": "12"}
    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if period:
        try:
            params['REPORT_TYPE'] = period_map[period]
        except:
            return 'period does not exist'
    else:
        params['REPORT_TYPE'] = ''

    if end_date:
        end_date_start_date = datetime.strftime(end_date[0], '%Y%m%d')
        end_date_end_date = datetime.strftime(end_date[1], '%Y%m%d')
        params["START_DATE"] = end_date_start_date
        params["END_DATE"] = end_date_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[['htsc_code', 'name', 'pub_date', 'start_date', 'end_date', 'currency_code',
                              'ebitda_interest', 'period', 'bad_loans_five', 'bad_loans_one', 'fin_cost',
                              'equity_ratio', 'profit_to_cost_ratio', 'net_cash_flow_fina', 'inventory_turnover',
                              'inventory_turnover_day', 'asset_compose_ratio', 'bad_debt_reserve_rate',
                              'no_recpro_loss_ratio', 'total_liab', 'total_debt', 'share_equity', 'sh_e_to_ta',
                              'sh_equity_turnover', 'fixed_asset', 'fixed_asset_ratio', 'fixed_asset_net_ratio',
                              'fixed_asset_turnover', 'sh_equity_parent_com', 'net_profit_parent_com',
                              'net_profit_cut_parent_com', 'monetary_fund', 'basic_eps', 'basic_eps_yoy',
                              'weight_risk_net_asset', 'weighted_roe', 'net_cash_flow_oper', 'ncfo_to_tl', 'ncfo_to_or',
                              'net_profit_no_shareholder', 'net_profit_in_shareholder', 'net_profit_parent_company',
                              'net_profit_yoy', 'net_profit_gr', 'rate_oe', 'net_asset_yoy', 'cut_basic_eps',
                              'cut_weighted_roe', 'cut_roe', 'total_profit', 'total_profit_yoy', 'intcov_ratio',
                              'current_ratio', 'total_cur_liab', 'total_cur_asset', 'cur_asset_turnover',
                              'cur_asset_turnover_day', 'net_cash_flow_operps', 'net_cash_flow_operps_yoy', 'bvps',
                              'cacl_eps', 'deduct_weight_eps', 'weight_eps', 'deduct_eps', 'eps', 'eps_gr',
                              'retained_earningps', 'cashflow_ps', 'sps', 'captital_reserv_eps', 'remark',
                              'liquidation_ratio', 'ta_to_she', 'roe', 'share_capital', 'is_audit', 'quick_ratio',
                              'owners_equity', 'equity_no_shareholder', 'adjust_bvps', 'net_cash_flow_inv',
                              'inv_income', 'retained_earning', 'ebit', 'ebit_p_margin', 'ebit_gr', 'ebit_da',
                              'diluted_eps', 'cash_asset_ratio', 'cash_equi_net_incr', 'np_margin',
                              'net_porfit_basic_eps', 'oper_cost', 'oper_profit', 'oper_profit_margin',
                              'oper_profit_yoy', 'oper_profit_gr', 'oper_revenue', 'oper_revenue_yoy', 'open_out_price',
                              'account_return_over', 'account_recturn_over_day', 'long_liability', 'ltl_to_wc',
                              'pri_oper_profit_ratio', 'gross_profit_margin', 'pri_oper_revenue_gr', 'pri_oper_profit',
                              'pri_oper_profit_margin', 'capital_fixed_ratio', 'capital_ratio', 'net_asset',
                              'retotal_assets_ratio', 'tl_to_ta', 'total_asset', 'total_share', 'total_assets',
                              'roa_ebit', 'roa', 'total_asset_yoy', 'total_asset_gr', 'total_asset_turnover',
                              'total_asset_turnover_day', 'entry_time', 'update_time', 'ground_time', 'update_id',
                              'record_id', 'opinion_code', 'main_busi_pro_ratio', 'net_profit_cut',
                              'gross_profit_margins', 'profit_margin', 'net_cash_flow_oper_ps_s', 'bvpsii']]
        period_reverse_map = {1: 'Q1', 6: 'Q2', 9: 'Q3', 12: 'Q4'}
        c_result = c_result.copy()
        c_result['period'] = c_result['period'].apply(lambda x: period_reverse_map[x])
        return c_result
    return result


# 个股最新估值
def get_newest_stock_value_handle(htsc_code, exchange):
    query_type = 1101080006

    params = {}

    exchange_map = {'XSHG': '101', 'XSHE': '105'}

    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code

    else:
        params['HTSC_SECURITY_ID'] = ''

    if exchange:
        params['EXCHANGE_CODE'] = exchange_map.get(exchange)
    else:
        params['EXCHANGE_CODE'] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[['htsc_code', 'name', 'exchange', 'trading_day', 'floating_market_val',
                              'total_market_val', 'pe', 'pettm', 'pb', 'pc', 'pcttm', 'ps', 'psttm']]
        return c_result

    return result


# 公司概况
def get_company_info_handle(htsc_code, name):
    query_type = 1101010002

    com_nature_map = {1001: '一般企业', 1101: '证券公司', 1102: '券商理财产品', 1112: '其它证券账户', 1301: '保险公司', 1302: '保险资产管理公司',
                      1303: '保险理财产品', 1401: '社保基金', 1501: '企业年金', 1601: '信托公司', 1603: '信托公司集合信托计划', 1701: '财务公司',
                      1801: '商业银行', 1802: '政策性银行', 1803: '中央银行', 1804: '银行理财', 1805: '外资银行', 1806: '农村合作银行',
                      1807: '城市信用合作社及联社', 1808: '农村信用合作社及联社', 1809: '城市合作银行', 1810: '专项账户', 1811: '村镇银行',
                      1812: '农村资金互助社', 1813: '邮政储蓄银行', 1901: '基金管理公司', 1902: '基金', 1906: '基金专户理财', 1907: '中央政府性基金',
                      1908: '独立基金销售机构', 2101: '会计师事务所', 2201: '律师事务所', 2301: '评估评级公司', 2303: '资产评估机构', 2401: '期货交易所',
                      2501: '期货经纪公司', 2702: '高等院校', 2801: '研究院所机构', 2901: '政府机构', 3301: '创投公司', 3401: '咨询公司',
                      3501: '银行理财公司', 3601: '商业保理公司', 9901: '其他'}
    enterpriseproperties_map = {1001: '国有企业', 1002: '民营企业', 1003: '集体企业', 1004: '国有相对控股企业', 1005: '民营相对控股企业',
                                1006: '中资企业(目前仅适用于基金)', 1007: '地方国企', 2001: '外资企业', 3001: '中外合资企业'}

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if name:
        params['SECU_ABBR'] = name
    else:
        params['SECU_ABBR'] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)

        df_result['ChiName'].fillna(df_result["EngName"], inplace=True)
        df_result['com_nature'] = df_result['ComNatureCode'].apply(lambda x: com_nature_map.get(x))
        df_result['enterprise_properties'] = df_result['EnterpriseProperties'].apply(
            lambda x: enterpriseproperties_map.get(x) if enterpriseproperties_map.get(x) else x)
        df_result = change_column_name(df_result)
        c_result = df_result[
            ['htsc_code', 'name', 'exchange', 'com_name', 'listing_date', 'found_date', 'reg_capital', 'com_nature',
             'legal_repr', 'general_manager', 'country', 'province', 'city', 'reg_address', 'office_address',
             'postal_code', 'tel_code', 'email', 'website', 'business_scope', 'core_business', 'com_profile',
             'ic_reg_no', 'tax_reg_no', 'corp_busil_icense_no', 'l1_name', 'l2_name', 'is_listed', 'is_abroad_listed',
             'employees', 'president', 'local_no', 'enterprise_properties', 'com_code']]

        return c_result
    return result


# 股东人数
def get_shareholder_num_handle(htsc_code, name, end_date):
    query_type = 1101060012

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if name and isinstance(name, str):
        params['SECU_ABBR'] = name
    else:
        params['SECU_ABBR'] = ''

    if end_date:
        end_date_start_date = datetime.strftime(end_date[0], '%Y%m%d')
        end_date_end_date = datetime.strftime(end_date[1], '%Y%m%d')
        params["START_DATE"] = end_date_start_date
        params["END_DATE"] = end_date_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)
        c_result = df_result[
            ['htsc_code', 'name', 'end_date', 'total_sh', 'avg_share', 'pct_of_total_sh', 'pct_of_avg_sh']]
        return c_result
    return result


# 股票增发
def get_additional_share_handle(htsc_code, listing_date):
    query_type = 1101040002

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if listing_date:
        listing_date_start_date = datetime.strftime(listing_date[0], '%Y%m%d')
        listing_date_end_date = datetime.strftime(listing_date[1], '%Y%m%d')
        params["LISTING_DATE_START_DATE"] = listing_date_start_date
        params["LISTING_DATE_END_DATE"] = listing_date_end_date
    else:
        params["LISTING_DATE_START_DATE"] = ''
        params["LISTING_DATE_END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'category', 'exchange', 'listing_notice_date', 'raise_net_fund_planned',
             'raise_net_fund', 'raise_fund',
             'is_pub_issue', 'ini_pub_date', 'right_reg_date', 'issue_start_date', 'issue_end_date', 'par_value',
             'listing_date', 'c_issue_price', 'f_issue_price', 'issue_object', 'issue_price', 'issue_share',
             'total_share_before_issue', 'eps_before_issue', 'eps_after_issue', 'bps_before_issue', 'bps_after_issue',
             'pb_issue', 'issue_cost']]
        return c_result

    return result


# 股票配售
def get_allotment_share_handle(htsc_code, ini_pub_date, is_allot_half_year):
    query_type = 1101040004

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if ini_pub_date:
        ini_pub_date_start_date = datetime.strftime(ini_pub_date[0], '%Y%m%d')
        ini_pub_date_end_date = datetime.strftime(ini_pub_date[1], '%Y%m%d')
        params["INI_PUB_DATE_START_DATE"] = ini_pub_date_start_date
        params["INI_PUB_DATE_END_DATE"] = ini_pub_date_end_date
    else:
        params["INI_PUB_DATE_START_DATE"] = ''
        params["INI_PUB_DATE_END_DATE"] = ''

    if str(is_allot_half_year) == "1":
        params['IS_ALLOT_HALF_Y'] = str(is_allot_half_year)
    elif str(is_allot_half_year) == "0":
        params['IS_ALLOT_HALF_Y'] = str(is_allot_half_year)

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'category', 'exchange', 'currency_code', 'ini_pub_date', 'issue_price', 'issue_share',
             'raise_fund', 'raise_net_fund', 'total_share_before_issue', 'allotment_ratio', 'listing_date', 'par_value',
             'right_reg_date', 'issue_object', 'ex_divi_date', 'is_allot_half_year']]
        return c_result

    return result


# 股本结构
def get_capital_structure_handle(htsc_code, end_date):
    query_type = 1101060001

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if end_date:
        end_date_start_date = datetime.strftime(end_date[0], '%Y%m%d')
        end_date_end_date = datetime.strftime(end_date[1], '%Y%m%d')
        params["START_DATE"] = end_date_start_date
        params["END_DATE"] = end_date_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'exchange', 'pub_date', 'end_date', 'total_share', 'a_total_share', 'a_listed_share',
             'b_total_share', 'b_listed_share', 'h_total_share', 'h_listed_share', 'employee_share', 'promoter_share',
             'state_promoter_share', 'social_promoter_share', 'domestic_crop_share', 'slp_share', 'dlp_share',
             'flp_share', 'other_promoter_share', 'placing_lp_share', 'raise_state_share', 'raise_dlp_share',
             'raise_slp_share', 'raise_sslp_share', 'raise_flp_share', 'strategy_lp_share', 'social_lp_share',
             'a_listed_share_ratio', 'b_listed_share_ratio', 'h_listed_share_ratio', 'a_unlisted_share',
             'b_unlisted_share', 'h_unlisted_share', 'state_res_share', 'state_lp_res_share', 'dlp_res_share',
             'dnp_res_share', 'placing_lp_res_share', 'employee_res_share', 'managing_res_share', 'flp_res_share',
             'fnp_res_share', 'other_res_share', 'total_res_share', 'orga_placing_share', 'limit_strategy_share',
             'total_unlisted_share', 'total_listed_share', 'other_listed_share', 'total_listed_res_share',
             'buy_back_share', 'ex_divi_date']]
        return c_result

    return result


# 股票分红
def get_dividend_handle(htsc_code, right_reg_date, ex_divi_date, divi_pay_date):
    query_type = 1101050001

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if right_reg_date:
        right_reg_date_start_date = datetime.strftime(right_reg_date[0], '%Y%m%d')
        right_reg_date_end_date = datetime.strftime(right_reg_date[1], '%Y%m%d')
        params["RIGHT_REG_DATE_START_DATE"] = right_reg_date_start_date
        params["RIGHT_REG_DATE_END_DATE"] = right_reg_date_end_date
    else:
        params["RIGHT_REG_DATE_START_DATE"] = ''
        params["RIGHT_REG_DATE_END_DATE"] = ''

    if ex_divi_date:
        ex_divi_date_start_date = datetime.strftime(ex_divi_date[0], '%Y%m%d')
        ex_divi_date_end_date = datetime.strftime(ex_divi_date[1], '%Y%m%d')
        params["EX_DIVI_DATE_START_DATE"] = ex_divi_date_start_date
        params["EX_DIVI_DATE_END_DATE"] = ex_divi_date_end_date
    else:
        params["EX_DIVI_DATE_START_DATE"] = ''
        params["EX_DIVI_DATE_END_DATE"] = ''

    if divi_pay_date:
        divi_pay_date_start_date = datetime.strftime(divi_pay_date[0], '%Y%m%d')
        divi_pay_date_end_date = datetime.strftime(divi_pay_date[1], '%Y%m%d')
        params["DIVI_PAY_DATE_START_DATE"] = divi_pay_date_start_date
        params["DIVI_PAY_DATE_END_DATE"] = divi_pay_date_end_date
    else:
        params["DIVI_PAY_DATE_START_DATE"] = ''
        params["DIVI_PAY_DATE_END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'category', 'exchange', 'ini_pub_date', 'right_reg_date', 'imp_notice_date',
             'ex_divi_date', 'splitps', 'divi_pay_date', 'share_listing_date', 'cash_before_tax', 'cash_after_tax',
             'base_share', 'total_share', 'bonus_ratio', 'transfer_ratio', 'bonus_transfer_ratio', 'opt_ratio',
             'total_bonus', 'total_transfer', 'equityBaseDate', 'distri_obj_types', 'last_trading_day']]
        return c_result

    return result


# 沪深港通持股记录
def get_north_bound_handle(htsc_code, trading_day):
    query_type = 1101130001

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if trading_day:
        trading_day_start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        trading_day_end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["HOLDING_DATE_START_DATE"] = trading_day_start_date
        params["HOLDING_DATE_END_DATE"] = trading_day_end_date
    else:
        params["HOLDING_DATE_START_DATE"] = ''
        params["HOLDING_DATE_END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'trading_day', 'trade_type', 'exchange', 'sh_hkshare_hold', 'pct_total_share']]
        return c_result

    return result


# 融资融券列表
def get_margin_target_handle(htsc_code, exchange):
    query_type = 1101100007

    exchange_code_map = {'XSHG': '101', 'XSHE': '105'}
    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if exchange:
        try:
            params["EXCHANGE_CODE"] = exchange_code_map[exchange]
        except:
            return 'exchange does not exist'
    else:
        params["EXCHANGE_CODE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[['htsc_code', 'name', 'exchange']]
        return c_result

    return result


# 融资融券交易汇总
def get_margin_summary_handle(htsc_code, trading_day):
    query_type = 1101100002

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if trading_day:
        trading_day_start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        trading_day_end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["START_DATE"] = trading_day_start_date
        params["END_DATE"] = trading_day_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'exchange', 'trading_day', 'buy_amount_fina', 'amount_fina', 'pay_amount_fina',
             'sell_vol_stock', 'vol_stock', 'pay_vol_stock', 'amount_stock', 'amount_margin', 'cash_rates']]
        return c_result

    return result


# 融资融券交易明细
def get_margin_detail_handle(exchange, trading_day):
    query_type = 1101100001
    exchange_code_map = {'XSHG': '101', 'XSHE': '105'}

    params = {}
    if exchange:
        try:
            params["EXCHANGE_CODE"] = exchange_code_map[exchange]
        except:
            return 'exchange does not exist'
    else:
        params["EXCHANGE_CODE"] = ''

    if trading_day:
        trading_day_start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        trading_day_end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["START_DATE"] = trading_day_start_date
        params["END_DATE"] = trading_day_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[['trading_day', 'exchange', 'amount_fina', 'buy_amount_fina',
                              'pay_amount_fina', 'amount_stock', 'sell_vol_stock',
                              'pay_vol_stock', 'vol_stock', 'amount_margin']]
        return c_result

    return result


# 十大股东
def get_shareholders_top10_handle(htsc_code, change_date):
    query_type = 1101060010

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if change_date:
        change_date_start_date = datetime.strftime(change_date[0], '%Y%m%d')
        change_date_end_date = datetime.strftime(change_date[1], '%Y%m%d')
        params["START_DATE"] = change_date_start_date
        params["END_DATE"] = change_date_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result.rename(columns={'EndDate': 'change_date'}, inplace=True)
        df_result = change_column_name(df_result)

        c_result = df_result[['htsc_code', 'name', 'change_date', 'sh_name', 'sh_type', 'hold_share', 'pct_total_share',
                              'holdshare_change', 'pct_holdshare_change', 'sh_code']]
        return c_result

    return result


# 十大流通股东
def get_shareholders_floating_top10_handle(htsc_code, change_date):
    query_type = 1101060007

    params = {}
    if htsc_code:
        params['HTSC_SECURITY_ID'] = htsc_code
    else:
        params['HTSC_SECURITY_ID'] = ''

    if change_date:
        change_date_start_date = datetime.strftime(change_date[0], '%Y%m%d')
        change_date_end_date = datetime.strftime(change_date[1], '%Y%m%d')
        params["START_DATE"] = change_date_start_date
        params["END_DATE"] = change_date_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result.rename(columns={'EndDate': 'change_date'}, inplace=True)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'change_date', 'sh_code', 'sh_name', 'hold_share', 'pct_total_share', 'sh_nature',
             'share_nature', 'sh_kind', 'holdshare_change', 'pct_holdshare_change', 'flow_ratio']]
        return c_result

    return result


# tick数据
def get_tick_handle(htsc_code, security_type, trading_day):
    query_type = 1109090009

    exchange_suffix_map = {'SH': '101', 'SZ': '102'}
    zx_exchange_suffix_map = {'SH': '101', 'SZ': '105'}

    security_type_map = {
        'index': '1',
        'stock': '2',
        'fund': '3',
        'bond': '4',
        'option': '7',
    }

    start_date = trading_day[0]
    end_date = trading_day[1]
    zx_exchange_code = zx_exchange_suffix_map.get(htsc_code.split('.')[-1])

    # 判断是否超过30个自然日
    num_day = (datetime.today() - start_date).days
    if num_day > 29:
        print('trading_day limit 30 to today')
        start_date = datetime.today() - timedelta(days=29)

    start_time = datetime.strftime(start_date, '%Y%m%d')
    end_time = datetime.strftime(end_date, '%Y%m%d')
    cal_query_type = 1101080001
    cal_params = {"EXCHANGE_CODE": zx_exchange_code, "START_DATE": start_time, "END_DATE": end_time,
                  "IS_TRADING_DAY": 1}
    cal_result = data_handle.get_interface().queryfininfosynchronous(cal_query_type, cal_params)

    if isinstance(cal_result, list):
        df_cal_result = query_to_dataframe(cal_result)
        trading_day_list = df_cal_result['TradingDay'].to_list()
        trading_day_list = list(map(lambda x: x.split(' ')[0].replace('-', ''), trading_day_list))
    else:
        return pd.DataFrame()

    exchange_code = exchange_suffix_map.get(htsc_code.split('.')[-1])

    all_result = pd.DataFrame()
    for trading_date in trading_day_list:

        params = {'HTSC_SECURITY_ID': htsc_code, 'SECURITY_ID_SOURCE': exchange_code, 'DATE': trading_date,
                  'SECURITY_TYPE': security_type_map.get(security_type), "DATA_LEVEL": "Level2"}

        result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
        if isinstance(result, list):

            content_list_store = []
            column_list = []
            i = 1
            for response in iter(result):
                response_dict = json.loads(response)
                content = response_dict['resultData']['stringContent']
                content = content.replace('"[', '[')
                content = content.replace(']"', ']')

                content_list = content.split(',')

                if i == 1:
                    column_list = content_list
                    i = 0
                    continue

                new_conten_list = []
                v_index = 0
                v_start_index = 0
                flag = 0
                for c_value in content_list:

                    if '[' in c_value:
                        flag = 1
                        v_start_index = v_index

                    elif ']' in c_value:
                        comb_list = content_list[v_start_index: v_index + 1]
                        comb_string = ','.join(comb_list)
                        comb_string = comb_string.strip('[]')
                        new_comb_list = comb_string.split(',')
                        new_conten_list.append(new_comb_list)
                        flag = 0

                    else:
                        if flag == 0:
                            new_conten_list.append(c_value)

                    v_index += 1

                content_list_store.append(new_conten_list)

            df_result = pd.DataFrame(content_list_store, columns=column_list)

            df_result["time"] = df_result['MDDate'] + df_result['MDTime']
            df_result["time"] = df_result["time"].apply(lambda x: datetime.strptime(x, '%Y%m%d%H%M%S%f'))
            df_result['security_type'] = security_type
            df_result = change_column_name(df_result)

            c_result = None
            if security_type == 'stock':  # 股票

                c_result = df_result[['htsc_code', 'time', 'trading_phase_code', 'exchange', 'security_type',
                                      'max', 'min', 'prev_close', 'num_trades', 'volume', 'value', 'last',
                                      'open', 'high', 'low', 'close']]

            elif security_type == "index":  # 指数

                c_result = df_result[['htsc_code', 'time', 'exchange', 'security_type', 'prev_close',
                                      'volume', 'value', 'last', 'open', 'high', 'low', 'close']]

            elif security_type == "fund":  # 基金

                c_result = df_result[['htsc_code', 'time', 'trading_phase_code', 'exchange', 'security_type',
                                      'max', 'min', 'prev_close', 'num_trades', 'volume', 'value', 'last', 'open',
                                      'high', 'low',
                                      'iopv', 'close']]

            elif security_type == "bond":  # 债券

                c_result = df_result[['htsc_code', 'time', 'trading_phase_code', 'exchange', 'security_type',
                                      'max', 'min', 'prev_close', 'num_trades', 'volume', 'value', 'last', 'open',
                                      'high', 'low', 'close']]

            elif security_type == "option":  # 期权

                c_result = df_result[['htsc_code', 'time', 'trading_phase_code', 'exchange', 'security_type',
                                      'max', 'min', 'prev_close', 'num_trades', 'volume', 'value', 'last', 'open',
                                      'high', 'low', 'pre_settle', 'open_interest', 'close', 'settle']]

            divisor_list = ['max', 'min', 'prev_close', 'last', 'open', 'high', 'low', 'close', 'iopv', 'settle',
                            'pre_settle']

            c_result = c_result.copy()
            for divisor_name in divisor_list:
                if divisor_name in c_result:
                    c_result[divisor_name] = c_result[divisor_name].apply(lambda x: float(x) / 10000 if x else 0)

            if security_type != 'index':
                count = 11
                if security_type == 'option':
                    count = 6

                df_result["BuyPriceQueue"] = df_result["BuyPriceQueue"].apply(
                    lambda x: list(map(lambda n: float(n) / 10000, x)))
                df_result["SellPriceQueue"] = df_result["SellPriceQueue"].apply(
                    lambda x: list(map(lambda n: float(n) / 10000, x)))

                df_buy_price_queue = df_result['BuyPriceQueue'].apply(pd.Series,
                                                                      index=['bid' + str(i) for i in range(1, count)])
                df_buy_order_qty_queue = df_result['BuyOrderQtyQueue'].apply(pd.Series,
                                                                             index=['bid_size' + str(i) for i in
                                                                                    range(1, count)])
                df_sell_price_queue = df_result['SellPriceQueue'].apply(pd.Series,
                                                                        index=['ask' + str(i) for i in range(1, count)])
                df_sell_order_qty_queue = df_result['SellOrderQtyQueue'].apply(pd.Series,
                                                                               index=['ask_size' + str(i) for i in
                                                                                      range(1, count)])

                c_result = pd.concat([c_result, df_buy_price_queue, df_buy_order_qty_queue, df_sell_price_queue,
                                      df_sell_order_qty_queue], axis=1)

            all_result = pd.concat([all_result, c_result]).reset_index(drop=True)

    return all_result


# 复权因子
def get_adj_factor_handle(htsc_code, begin_date):
    query_type = 1101080005

    params = {}
    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if begin_date:
        begin_date_start_date = datetime.strftime(begin_date[0], '%Y%m%d')
        begin_date_end_date = datetime.strftime(begin_date[1], '%Y%m%d')
        params["START_DATE"] = begin_date_start_date
        params["END_DATE"] = begin_date_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[['htsc_code', 'name', 'begin_date', 'end_date', 'xdy', 'b_xdy', 'f_xdy']]
        return c_result

    return result


# 限售股解禁
def get_locked_shares_handle(htsc_code, listing_date):
    query_type = 1101060008

    params = {}
    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if listing_date:
        listing_date_start_date = datetime.strftime(listing_date[0], '%Y%m%d')
        listing_date_end_date = datetime.strftime(listing_date[1], '%Y%m%d')
        params["START_DATE"] = listing_date_start_date
        params["END_DATE"] = listing_date_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'pub_date', 'listing_date', 'add_listed', 'percent_addlisted', 'percent_addlisted_f',
             'sstmhd_list_type', 'sstmhd_list_code', 'sstmhd_list_name']]
        return c_result

    return result


# 股权质押
def get_frozen_shares_handle(htsc_code, freezing_start_date):
    query_type = 1101060026

    params = {}
    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if freezing_start_date:
        freezing_start_date_start_date = datetime.strftime(freezing_start_date[0], '%Y%m%d')
        freezing_start_date_end_date = datetime.strftime(freezing_start_date[1], '%Y%m%d')
        params["FREEZING_START_DATE_START_DATE"] = freezing_start_date_start_date
        params["FREEZING_START_DATE_END_DATE"] = freezing_start_date_end_date
    else:
        params["FREEZING_START_DATE_START_DATE"] = ''
        params["FREEZING_START_DATE_END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'pub_date', 'sh_code', 'sh_name', 'hold_share', 'frozen_share', 'freezing_hold_ratio',
             'freezing_total_ratio', 'freezing_start_date', 'freezing_end_date', 'freezing_term-desc', 'freezing_cause',
             'advance_end_date', 'freezing_type', 'freezing_period', 'freezing_period_unit', 'freezing_purpose']]
        return c_result

    return result


# 港股行业分类-标的查询
def get_hk_industry_handle(htsc_code):
    query_type = 1104010003

    params = {}
    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)

        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)
        df_result["classified"] = 'sw'
        r_result = df_result[["htsc_code", "classified", "name", "exchange", "industry_name", "industry_code",
                              "l1_code", "l1_name", "l2_code", "l2_name", "l3_code", "l3_name"]]
        return r_result
    return result


# 港股行业分类-行业代码查询
def get_hk_industry_stocks_handle(industry_code):
    query_type = 1104010003

    sw_level_map = {'230000': 1, '240000': 1, '270000': 1, '330000': 1, '340000': 1, '110000': 1, '220000': 1,
                    '370000': 1,
                    '410000': 1, '420000': 1, '430000': 1, '450000': 1, '460000': 1, '480000': 1, '490000': 1,
                    '510000': 1,
                    '610000': 1, '740000': 1, '750000': 1, '760000': 1, '770000': 1, '280000': 1, '620000': 1,
                    '630000': 1,
                    '640000': 1, '650000': 1, '710000': 1, '720000': 1, '730000': 1, '350000': 1, '360000': 1,
                    '220800': 2,
                    '220900': 2, '230300': 2, '230400': 2, '230500': 2, '240200': 2, '240300': 2, '240400': 2,
                    '240500': 2,
                    '240600': 2, '270100': 2, '270200': 2, '270300': 2, '270400': 2, '280400': 2, '280500': 2,
                    '280600': 2,
                    '330100': 2, '330200': 2, '330300': 2, '330400': 2, '330500': 2, '330600': 2, '330700': 2,
                    '340400': 2,
                    '340500': 2, '340600': 2, '340700': 2, '110100': 2, '110200': 2, '110300': 2, '110400': 2,
                    '110500': 2,
                    '110700': 2, '110800': 2, '110900': 2, '220200': 2, '220300': 2, '220400': 2, '220500': 2,
                    '220600': 2,
                    '360300': 2, '360500': 2, '370100': 2, '370200': 2, '370300': 2, '370400': 2, '370500': 2,
                    '370600': 2,
                    '410100': 2, '410300': 2, '420800': 2, '420900': 2, '421000': 2, '421100': 2, '430100': 2,
                    '430300': 2,
                    '450200': 2, '450300': 2, '450400': 2, '450600': 2, '450700': 2, '460600': 2, '460700': 2,
                    '460800': 2,
                    '460900': 2, '461000': 2, '461100': 2, '480200': 2, '480300': 2, '480400': 2, '480500': 2,
                    '480600': 2,
                    '490100': 2, '490200': 2, '490300': 2, '510100': 2, '610100': 2, '610200': 2, '740100': 2,
                    '740200': 2,
                    '750100': 2, '750200': 2, '750300': 2, '760100': 2, '760200': 2, '770100': 2, '770200': 2,
                    '770300': 2,
                    '270500': 2, '270600': 2, '280200': 2, '280300': 2, '610300': 2, '620100': 2, '620200': 2,
                    '620300': 2,
                    '620400': 2, '620600': 2, '630100': 2, '630300': 2, '630500': 2, '630600': 2, '630700': 2,
                    '630800': 2,
                    '640100': 2, '640200': 2, '640500': 2, '640600': 2, '640700': 2, '650100': 2, '650200': 2,
                    '650300': 2,
                    '650400': 2, '650500': 2, '710100': 2, '710300': 2, '710400': 2, '720400': 2, '720500': 2,
                    '720600': 2,
                    '720700': 2, '720800': 2, '720900': 2, '721000': 2, '730100': 2, '730200': 2, '340800': 2,
                    '340900': 2,
                    '350100': 2, '350200': 2, '350300': 2, '360100': 2, '360200': 2, '220602': 3, '220603': 3,
                    '220604': 3,
                    '220801': 3, '220802': 3, '220803': 3, '220804': 3, '220805': 3, '220901': 3, '230301': 3,
                    '230302': 3,
                    '230401': 3, '230402': 3, '230403': 3, '230501': 3, '240201': 3, '240202': 3, '240301': 3,
                    '240302': 3,
                    '240303': 3, '240401': 3, '240402': 3, '240501': 3, '240502': 3, '240504': 3, '240505': 3,
                    '240601': 3,
                    '240602': 3, '240603': 3, '270102': 3, '270103': 3, '270104': 3, '270105': 3, '270106': 3,
                    '270107': 3,
                    '270108': 3, '270202': 3, '270203': 3, '270301': 3, '270302': 3, '270303': 3, '270401': 3,
                    '280401': 3,
                    '280402': 3, '280501': 3, '280502': 3, '280601': 3, '280602': 3, '330102': 3, '330106': 3,
                    '330201': 3,
                    '330202': 3, '330301': 3, '330302': 3, '330303': 3, '330401': 3, '330402': 3, '330501': 3,
                    '330601': 3,
                    '330701': 3, '340401': 3, '340404': 3, '340406': 3, '340407': 3, '340501': 3, '340601': 3,
                    '340602': 3,
                    '340701': 3, '340702': 3, '110101': 3, '110102': 3, '110103': 3, '110104': 3, '110201': 3,
                    '110202': 3,
                    '110301': 3, '110402': 3, '110403': 3, '110404': 3, '110501': 3, '110502': 3, '110504': 3,
                    '110702': 3,
                    '110703': 3, '110704': 3, '110801': 3, '110901': 3, '220201': 3, '220202': 3, '220203': 3,
                    '220204': 3,
                    '220205': 3, '220206': 3, '220305': 3, '220307': 3, '220308': 3, '220309': 3, '220311': 3,
                    '220313': 3,
                    '220315': 3, '220316': 3, '220317': 3, '220401': 3, '220403': 3, '220404': 3, '220405': 3,
                    '220406': 3,
                    '220501': 3, '220503': 3, '220504': 3, '220505': 3, '360306': 3, '360307': 3, '360308': 3,
                    '360309': 3,
                    '360311': 3, '360501': 3, '360502': 3, '370101': 3, '370102': 3, '370201': 3, '370302': 3,
                    '370303': 3,
                    '370304': 3, '370402': 3, '370403': 3, '370404': 3, '370502': 3, '370503': 3, '370504': 3,
                    '370602': 3,
                    '370603': 3, '370604': 3, '370605': 3, '410101': 3, '410102': 3, '410104': 3, '410106': 3,
                    '410107': 3,
                    '410108': 3, '410109': 3, '410110': 3, '410301': 3, '420802': 3, '420803': 3, '420804': 3,
                    '420805': 3,
                    '420806': 3, '420807': 3, '420901': 3, '420902': 3, '420903': 3, '421001': 3, '421002': 3,
                    '421101': 3,
                    '421102': 3, '430101': 3, '430102': 3, '430103': 3, '430301': 3, '430302': 3, '430303': 3,
                    '450201': 3,
                    '450301': 3, '450302': 3, '450303': 3, '450304': 3, '450401': 3, '450601': 3, '450602': 3,
                    '450603': 3,
                    '450701': 3, '460601': 3, '460701': 3, '460801': 3, '460802': 3, '460803': 3, '460804': 3,
                    '460901': 3,
                    '460902': 3, '461001': 3, '461002': 3, '461003': 3, '461004': 3, '461101': 3, '461102': 3,
                    '461103': 3,
                    '480201': 3, '480301': 3, '480401': 3, '480501': 3, '480601': 3, '490101': 3, '490201': 3,
                    '490302': 3,
                    '490303': 3, '490304': 3, '490305': 3, '490306': 3, '490307': 3, '490308': 3, '510101': 3,
                    '610101': 3,
                    '610102': 3, '730205': 3, '730206': 3, '730207': 3, '740101': 3, '740102': 3, '740201': 3,
                    '750101': 3,
                    '750201': 3, '750202': 3, '750301': 3, '750302': 3, '750303': 3, '760101': 3, '760102': 3,
                    '760103': 3,
                    '760104': 3, '760201': 3, '770101': 3, '770102': 3, '770201': 3, '770202': 3, '270503': 3,
                    '270504': 3,
                    '270601': 3, '280202': 3, '280203': 3, '280204': 3, '280205': 3, '280206': 3, '280302': 3,
                    '280303': 3,
                    '610201': 3, '610202': 3, '610301': 3, '610302': 3, '610303': 3, '610304': 3, '610305': 3,
                    '620101': 3,
                    '620201': 3, '620306': 3, '620307': 3, '620401': 3, '620402': 3, '620403': 3, '620404': 3,
                    '620601': 3,
                    '630101': 3, '630301': 3, '630304': 3, '630306': 3, '630501': 3, '630502': 3, '630503': 3,
                    '630504': 3,
                    '630505': 3, '630601': 3, '630602': 3, '630701': 3, '630702': 3, '630703': 3, '630704': 3,
                    '630705': 3,
                    '630801': 3, '630802': 3, '630803': 3, '630804': 3, '630805': 3, '640101': 3, '640103': 3,
                    '640105': 3,
                    '640106': 3, '640107': 3, '640108': 3, '640203': 3, '640204': 3, '640206': 3, '640207': 3,
                    '640208': 3,
                    '640209': 3, '640501': 3, '640601': 3, '640602': 3, '640701': 3, '640702': 3, '640703': 3,
                    '640704': 3,
                    '650101': 3, '650201': 3, '650301': 3, '650401': 3, '650501': 3, '710102': 3, '710103': 3,
                    '710301': 3,
                    '710401': 3, '710402': 3, '720401': 3, '720501': 3, '720502': 3, '720601': 3, '720602': 3,
                    '720701': 3,
                    '720702': 3, '720703': 3, '720704': 3, '720705': 3, '720706': 3, '720801': 3, '720901': 3,
                    '720902': 3,
                    '720903': 3, '721001': 3, '730102': 3, '730103': 3, '730104': 3, '730204': 3, '340801': 3,
                    '340802': 3,
                    '340803': 3, '340901': 3, '350102': 3, '350104': 3, '350105': 3, '350106': 3, '350107': 3,
                    '350205': 3,
                    '350206': 3, '350208': 3, '350209': 3, '350301': 3, '350302': 3, '350303': 3, '360102': 3,
                    '360103': 3,
                    '360202': 3, '360203': 3, '360204': 3, '360205': 3, '360206': 3, '770301': 3, '770302': 3}

    params = {}
    if industry_code:
        try:
            code_level = sw_level_map[industry_code]
            if code_level == 1:
                params["FINDU_CODE"] = industry_code
            elif code_level == 2:
                params["SINDU_CODE"] = industry_code
            elif code_level == 3:
                params["TINDU_CODE"] = industry_code
        except:
            return 'industry_code dose not exist'

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)
        df_result["classified"] = 'sw'
        r_result = df_result[["htsc_code", "classified", "name", "exchange", "industry_name", "industry_code",
                              "l1_code", "l1_name", "l2_code", "l2_name", "l3_code", "l3_name"]]
        return r_result
    return result


# 港股交易日行情
def get_hk_daily_basic_handle(htsc_code, trading_day):
    query_type = 1104060001

    params = {}
    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if trading_day:
        start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["START_DATE"] = start_date
        params["END_DATE"] = end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        column_list = ['htsc_code', 'name', 'exchange', 'trading_day', 'close', 'open', 'prev_close', 'high', 'low',
                       'volume', 'value', 'day_change', 'day_change_rate', 'amplitude']
        choose_list = [i for i in column_list if i in df_result]
        c_result = df_result[choose_list]
        return c_result

    return result


# 港股估值
def get_hk_stock_valuation_handle(htsc_code, trading_day):
    query_type = 1104060004

    params = {}
    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if trading_day:
        start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["START_DATE"] = start_date
        params["END_DATE"] = end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'trading_day', 'name', 'exchange', 'pettm', 'pe', 'pemrq', 'net_profit_cut_ttm',
             'net_profit_cut_lfy', 'net_profit_cut_mrq', 'pb', 'psttm', 'pslfy', 'psmrq', 'pcttm', 'pc', 'pcmrq',
             'turnover_rate', 'dividend_yield_ttm', 'total_market_val', 'floating_market_val', 'corpe_quity_val']]
        return c_result

    return result


# 港股基本信息
def get_hk_stock_basic_info_handle(htsc_code, listing_date, listing_state):
    query_type = 1104010001

    state_map = {"0": '未上市', "1": '上市', "3": '退市'}
    currency_map = {110: "港币", 142: "人民币", 116: "日本元", 132: "新加坡元", 300: "欧元",
                    303: "英镑", 501: "加拿大元", 502: "美元", 999: "未披露"}
    se_type_map = {"1": '港股普通股', "2": '港股优先股', "3": '香港存托凭证 - 普通股', "4": '香港信托基金', "5": '香港存托凭证 - 优先股'}
    ny_map = {"1": 'H股', "2": '红筹股', "9": '非H非R'}

    params = {}
    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code

    if listing_date:
        start_date = datetime.strftime(listing_date[0], '%Y%m%d')
        end_date = datetime.strftime(listing_date[1], '%Y%m%d')
        params["LISTING_DATE_START_DATE"] = start_date
        params["LISTING_DATE_END_DATE"] = end_date

    if listing_state:
        params['LISTING_STATE_CODE'] = dict((v, k) for k, v in state_map.items()).get(listing_state)

    if not all([htsc_code, listing_date, listing_state]):
        params[''] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result['currency'] = df_result['CurrencyCode'].apply(lambda x: currency_map.get(x) if x else None)
        df_result['listing_state'] = df_result['ListingStateCode'].apply(lambda x: state_map.get(str(x)))
        df_result = change_column_name(df_result)

        df_result['ny'] = df_result['ny'].apply(lambda x: ny_map.get(x) if x else None)
        df_result['se_type'] = df_result['se_type'].apply(lambda x: se_type_map.get(x) if x else None)

        c_result = df_result[
            ['htsc_code', 'exchange', 'name', 'currency', 'par_value', 'board_name', 'ny',
             'listing_state', 'listing_date', 'delisting_date', 'se_type', 'ah_code']]
        return c_result

    return result


# 个股主营产品
def get_main_product_info_handle(htsc_code, product_code, product_level):
    query_type = 1114010001

    currency_map = {110: "港币", 142: "人民币"}

    params = {}
    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code

    if product_code:
        params["PRODUCT_CODE"] = product_code

    if product_level:
        params["PRODUCT_LEVEL"] = product_level

    if not all([htsc_code, product_code, product_level]):
        params[''] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result['currency'] = df_result['CurrencyCode'].apply(lambda x: currency_map.get(x) if x else None)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'end_date', 'currency', 'product_code', 'product_name', 'product_eng_name',
             'main_product_income', 'main_product_income_ratio', 'main_product_profit', 'main_product_profit_ratio',
             'product_level']]
        return c_result

    return result


# 华泰融券通
def get_htsc_margin_target_handle():
    query_type = 1003020002

    params = {"": ""}

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

    if isinstance(result, list):
        all_result = []

        for response in iter(result):
            response_dict = json.loads(response)
            htsc_code = response_dict['resultData']['stringContent']
            all_result.append(htsc_code)

        df_result = pd.DataFrame(all_result, columns=["htsc_code"])
        return df_result
    return result


# 处理融券通数据
def process_htsc_margin(json_result, data_type):
    security_type_map = {'StockType': 'stock', 'FundType': 'fund'}

    # 二级目录映射
    lendingentry_map = {'Level': 'level', 'Rate': 'rate', 'Term': 'term', 'Amount': 'amount',
                        'HtscProvided': 'htsc_provided', 'TotalAmount': 'total_amount',
                        'MatchedAmount': 'matched_amount', 'PostponeProbability': 'post_pone_probability'}

    # 二级目录列表
    data_type_lendingentry = {
        "security_lending": ['valid_borrows', 'valid_a_lends', 'valid_b_lends', 'valid_c_lends', 'a_lends', 'b_lends',
                             'c_lends', 'valid_reservation_borrows', 'valid_reservation_lends', 'reservation_borrows',
                             'reservation_lends', 'valid_otc_lends', 'htsc_borrows', 'loans', 'external_lends',
                             'market_borrows', 'market_lends'],
        "security_lending_estimation": ['long_term_lends', 'valid_borrows', 'valid_a_lends', 'valid_b_lends', 'borrows',
                                        'a_lends', 'b_lends'],
    }

    # 一级除数
    divisor_columns = ['trade_money', 'best_loan_rate', 'weighted_rate', 'pre_htsc_borrow_weighted_rate',
                       'htsc_borrow_weighted_rate', 'htsc_borrow_rate', 'pre_low_rate', 'best_borrow_rate',
                       'pre_high_rate', 'htsc_lend_trade_volume', 'pre_weighted_rate',
                       'last', 'low_rate', 'high_rate', 'best_lend_rate', 'market_trade_volume', 'pre_close',
                       'pre_trade_money', 'htsc_best_lend_rate']
    if data_type == 'security_lending_statistics':
        divisor_columns.append('htsc_borrow_trade_volume')

    # json提取映射
    data_type_json_map = {'security_lending': 'mdSecurityLending', 'security_lending_estimation': 'mdSLEstimation',
                          'security_lending_statistics': 'mdSLStatistics',
                          'security_lending_indicative_quote': 'mdSLIndicativeQuote'}

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

    result_list = []
    for response in iter(json_result):
        try:
            response_dict = json.loads(response)
        except:
            continue

        content = response_dict['resultData']['stringContent']
        content = content.replace('"{', '{')
        content = content.replace('}"', '}')
        content = content.replace('false', 'False')
        content = content.replace('true', 'True')

        detail_content = eval(content)[data_type_json_map.get(data_type)]
        result_list.append(detail_content)

    pd_result = pd.DataFrame(result_list)
    new_result = column_renaming(pd_result, 'get_htsc_margin')

    new_result['MDTime'] = new_result['MDTime'].apply(lambda x: str(x).zfill(9) if x else x)
    new_result["time"] = new_result['MDDate'].astype(str) + new_result['MDTime']
    new_result["time"] = new_result["time"].apply(lambda x: datetime.strptime(str(x), '%Y%m%d%H%M%S%f'))

    if 'security_type' in new_result:
        new_result['security_type'] = new_result['security_type'].apply(lambda x: security_type_map.get(x) if x else x)

    divisor = pow(10, int(new_result["DataMultiplePowerOf10"][0]))

    if data_type_lendingentry.get(data_type):

        for lendingentry_column in data_type_lendingentry[data_type]:

            if lendingentry_column in new_result:
                new_result[lendingentry_column] = new_result[lendingentry_column].apply(
                    lambda x: process_lendingentry(x, divisor) if isinstance(x, list) else x)

    existing_divisor_columns = [col for col in divisor_columns if col in new_result.columns]
    if existing_divisor_columns:
        new_result[existing_divisor_columns] = new_result[existing_divisor_columns].apply(lambda x: x / divisor)

    if 'trade_date' in new_result:
        new_result['trade_date'] = new_result['trade_date'].apply(lambda x: datetime.strptime(x, "%Y%m%d") if x else x)

    time_data = new_result.pop('time')
    new_result.insert(1, 'time', time_data)
    new_result.insert(2, 'data_type', data_type)

    new_result.drop(columns=['MDDate', 'MDTime', 'DataMultiplePowerOf10'], inplace=True)
    return new_result


# 融券通行情-ID查询
def get_htsc_margin_by_id_handle(htsc_code, data_type):
    query_type = 1003020003

    data_type_map = {'security_lending': 'MD_SECURITY_LENDING', 'security_lending_estimation': 'MD_SL_ESTIMATION',
                     'security_lending_statistics': 'MD_SL_STATISTICS',
                     'security_lending_indicative_quote': 'MD_SL_INDICATIVE_QUOTE'}

    if isinstance(htsc_code, list):
        htsc_code = ','.join(htsc_code)

    params = {'HTSC_SECURITY_IDS': htsc_code, 'RECORD_TYPE': data_type_map[data_type]}
    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

    if result and isinstance(result, list):
        df_result = process_htsc_margin(result, data_type)

        return df_result
    return pd.DataFrame()


# 融券通行情-类型查询
def get_htsc_margin_by_type_handle(data_type, security_type):
    query_type = 1003020003

    security_type_map = {'stock': 'StockType', 'fund': 'FundType'}
    data_type_map = {'security_lending': 'MD_SECURITY_LENDING', 'security_lending_estimation': 'MD_SL_ESTIMATION',
                     'security_lending_statistics': 'MD_SL_STATISTICS',
                     'security_lending_indicative_quote': 'MD_SL_INDICATIVE_QUOTE'}

    if data_type == 'security_lending':
        if security_type == 'fund':
            exchanges = ['XSHE', 'XSHG']
        else:
            exchanges = ['XSHE', 'XSHG', 'HTSM']
    else:
        exchanges = ['HTSM']

    result_store = []
    for exchange in exchanges:

        params = {'RECORD_TYPE': data_type_map[data_type], 'SECURITY_ID_SOURCE': exchange,
                  'SECURITY_TYPE': security_type_map[security_type]}

        result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
        if result and isinstance(result, list):
            result_store.extend(result)

    if result_store:
        df_result = process_htsc_margin(result_store, data_type)

        return df_result
    return pd.DataFrame()


# 指数基本信息-ID查询
def get_index_info_handle(htsc_code, trading_day):
    query_type = 1106020001

    reverse_exchange_code_map = {806: 'OTHERS', 999: 'OTHERS', 182: 'OTHERS', 101: 'XSHG', 105: 'XSHE', 161: 'XHKG',
                                 181: 'TWSE', 301: 'AMEX',
                                 715: 'CBOE', 132: 'XDCE', 133: 'XZCE', 131: 'XSGE', 901: 'EUREX', 714: 'ICE',
                                 203: 'TSE', 461: 'LME', 134: 'INE', 366: 'ICUS'}

    params = {}
    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if trading_day:
        trading_day_start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        trading_day_end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["TRADING_DAY_START_DATE"] = trading_day_start_date
        params["TRADING_DAY_END_DATE"] = trading_day_end_date
    else:
        params["TRADING_DAY_START_DATE"] = ''
        params["TRADING_DAY_END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)

        try:
            df_result.drop(columns=['IDSOURCE'], inplace=True)
        except:
            pass
        df_result['exchange'] = df_result['EXCHANGECODE'].apply(lambda x: reverse_exchange_code_map.get(x))
        df_result.rename(columns={"PREVCLOSINGPRICE": "prev_close", "TURNOVERVOL": "volume", "TURNOVERVAL": "value",
                                  "DAYCHANGE": "change", "DAYCHANGERATE": "change_rate"}, inplace=True)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'trading_day', 'exchange', 'prev_close', 'open', 'high', 'low', 'close', 'volume',
             'value', 'change', 'change_rate']]
        return c_result

    return result


# 指数基本信息-市场查询
def get_all_index_handle(exchange, trading_day):
    query_type = 1106020001

    exchange_code_map = {'OTHERS': "999", 'XSHG': "101", 'XSHE': "105", 'XHKG': '161', 'TWSE': "181", 'AMEX': "301",
                         'CBOE': "715", 'XDCE': "132", 'XZCE': "133", 'XSGE': "131", 'EUREX': "901", 'ICE': "714",
                         'TSE': "203", 'LME': "461", 'INE': "134", 'ICUS': "366"}

    reverse_exchange_code_map = {806: 'OTHERS', 999: 'OTHERS', 182: 'OTHERS', 101: 'XSHG', 105: 'XSHE', 161: 'XHKG',
                                 181: 'TWSE', 301: 'AMEX',
                                 715: 'CBOE', 132: 'XDCE', 133: 'XZCE', 131: 'XSGE', 901: 'EUREX', 714: 'ICE',
                                 203: 'TSE', 461: 'LME', 134: 'INE', 366: 'ICUS'}

    params = {}
    if exchange:
        try:
            params["EXCHANGE_CODE"] = exchange_code_map[exchange]
        except:
            return 'exchange does not exist'
    else:
        params["EXCHANGE_CODE"] = ''

    if trading_day:
        trading_day_start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        trading_day_end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["TRADING_DAY_START_DATE"] = trading_day_start_date
        params["TRADING_DAY_END_DATE"] = trading_day_end_date
    else:
        params["TRADING_DAY_START_DATE"] = ''
        params["TRADING_DAY_END_DATE"] = ''

    params['ORDER_BY'] = 'TRADINGDAY,TRADINGCODE'

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)

        try:
            df_result.drop(columns=['IDSOURCE'], inplace=True)
        except:
            pass
        df_result['exchange'] = df_result['EXCHANGECODE'].apply(lambda x: reverse_exchange_code_map.get(x))
        df_result.rename(columns={"PREVCLOSINGPRICE": "prev_close", "TURNOVERVOL": "volume", "TURNOVERVAL": "value",
                                  "DAYCHANGE": "change", "DAYCHANGERATE": "change_rate"}, inplace=True)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'trading_day', 'exchange', 'prev_close', 'open', 'high', 'low', 'close', 'volume',
             'value', 'change', 'change_rate']]
        return c_result

    return result


# 指数成分股
def get_index_component_handle(htsc_code, name, stock_code, trading_day):
    query_type = 1106010002

    params = {}
    reverse_exchange_code_map = {101: 'XSHG', 105: 'XSHE', 106: "XBSE", 703: 'CSI', 702: 'CNI', 999: 'OTHERS'}
    indexexchange_code_map = {101: '.SH', 105: '.SZ', 106: ".BJ", 703: '.CSI', 702: '.CNI', 999: '.OTHERS'}

    if htsc_code:
        try:
            htsc_code = htsc_code.split('.')[0]
        except:
            pass
        params["INX_TRADING_CODE"] = htsc_code
    else:
        params["INX_TRADING_CODE"] = ''

    if name:
        params["INX_SECU_ABBR"] = name
    else:
        params["INX_SECU_ABBR"] = ''

    if stock_code:
        params["HTSC_SECURITY_ID"] = stock_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if trading_day:
        trading_day = datetime.strftime(trading_day, '%Y%m%d')
        params["TRADING_DAY"] = trading_day
    else:
        params["TRADING_DAY"] = ''

    params['ORDER_BY'] = 'INXTRADINGCODE,TRADINGDAY,TRADINGCODE'

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result['indexexchange'] = df_result['INDEXEXCHANGECODE'].apply(lambda x: indexexchange_code_map.get(x))
        df_result['htsc_code'] = df_result['INXTRADINGCODE'] + df_result['indexexchange']

        df_result.rename(columns={'INXSECUABBR': 'name', "HTSCSECURITYID": "stock_code", "SECUABBR": "stock_name",
                                  'TRADINGDAY': 'trading_day', 'WEIGHT': 'weight', 'INDATE': 'in_date',
                                  'OUTDATE': 'out_date'}, inplace=True)

        df_result['exchange'] = df_result['INDEXEXCHANGECODE'].apply(lambda x: reverse_exchange_code_map.get(x))
        df_result['stock_exchange'] = df_result['EXCHANGECODE'].apply(lambda x: reverse_exchange_code_map.get(x))

        c_result = df_result[
            ['htsc_code', 'name', 'exchange', 'stock_code', 'stock_name', 'stock_exchange', 'trading_day',
             'weight', 'in_date', 'out_date']]
        return c_result
    return result


# 指数成分股详细数据
def get_index_component_pro_handle(htsc_code, name, stock_code, trading_day):
    query_type = 1106010003

    params = {}
    reverse_exchange_code_map = {101: 'XSHG', 105: 'XSHE', 106: "XBSE", 703: 'CSI', 702: 'CNI', 999: 'OTHERS'}
    indexexchange_code_map = {101: '.SH', 105: '.SZ', 106: ".BJ", 703: '.CSI', 702: '.CNI', 999: '.OTHERS'}

    if htsc_code:
        try:
            htsc_code = htsc_code.split('.')[0]
            params["INX_TRADING_CODE"] = htsc_code
        except:
            return 'htsc_code format error'
    else:
        params["INX_TRADING_CODE"] = ''

    if name:
        params["INDEX_NAME"] = name
    else:
        params["INDEX_NAME"] = ''

    if stock_code:
        try:
            params["CON_TRADING_CODE"] = stock_code.split('.')[0]
        except:
            return 'stock_code format error'
    else:
        params["CON_TRADING_CODE"] = ''

    if trading_day:
        trading_day = datetime.strftime(trading_day, '%Y%m%d')
        params["TRADING_DAY"] = trading_day
    else:
        params["TRADING_DAY"] = ''

    params['ORDER_BY'] = 'INXTRADINGCODE,TRADINGDAY,CONTRADINGCODE'

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result['indexexchange'] = df_result['IEXCHANGECODE'].apply(lambda x: indexexchange_code_map.get(x))
        df_result['htsc_code'] = df_result['INXTRADINGCODE'] + df_result['indexexchange']
        df_result['exchange'] = df_result['IEXCHANGECODE'].apply(lambda x: reverse_exchange_code_map.get(x))

        df_result['stockexchange'] = df_result['EXCHANGECODE'].apply(lambda x: indexexchange_code_map.get(x))
        df_result['stock_code'] = df_result['CONTRADINGCODE'] + df_result['stockexchange']

        df_result.rename(columns={'INDEXNAME': 'name', "CONSECUABBR": "stock_name", 'TRADINGDAY': 'trading_day',
                                  'WEIGHT': 'weight', 'IDSOURCE': 'stock_exchange', 'TCLOSE': 'close',
                                  'TOTALSHARES': 'total_shares', 'SHARESINDEX': 'shares_index',
                                  'CAPFACTOR': 'cap_factor', 'TOTALCAP': 'total_cap', 'CAPINDEX': 'cap_index',
                                  }, inplace=True)
        c_result = df_result[
            ['htsc_code', 'name', 'exchange', 'stock_code', 'stock_name', 'stock_exchange', 'trading_day',
             'weight', 'close', 'total_shares', 'shares_index', 'cap_factor', 'total_cap', 'cap_index']]
        return c_result
    return result


# 量化因子
def get_factors_handle(htsc_code, factor_name, trading_day):
    query_map = {
        # barra因子
        'barra_cne6_beta': 1208010001, 'barra_cne6_booktoprice': 1208010001,
        'barra_cne6_dividendyield': 1208010001, 'barra_cne6_midcap': 1208010001,
        'barra_cne6_earningsquality': 1208010001, 'barra_cne6_earningsvariability': 1208010001,
        'barra_cne6_earningsyield': 1208010001, 'barra_cne6_growth': 1208010001,
        'barra_cne6_investmentquality': 1208010001, 'barra_cne6_leverage': 1208010001,
        'barra_cne6_liquidity': 1208010001, 'barra_cne6_longtermreversal': 1208010001,
        'barra_cne6_momentum': 1208010001, 'barra_cne6_profitability': 1208010001,
        'barra_cne6_residualvolatility': 1208010001, 'barra_cne6_size': 1208010001,
        # alphanet因子
        'alphanet': 1401010003, 'alphanet-5': 1401010004, 'alphanet-15': 1401010005, 'alphanet2-10': 1401010006,
    }

    try:
        query_type = query_map[factor_name]
    except:
        return "factor_name does not exist"

    params = {}
    # 仅barra因子入参
    if query_type == 1208010001:
        params["FACTOR_NAME"] = factor_name
        if htsc_code:
            params["HTSC_SECURITY_ID"] = htsc_code
        else:
            params["HTSC_SECURITY_ID"] = ''
    else:
        # alphanet入参
        if htsc_code:
            params["HTSC_SECURITY_IDS"] = htsc_code
        else:
            params["HTSC_SECURITY_IDS"] = ''

    if trading_day:
        trading_day_start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        trading_day_end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["START_DATE"] = trading_day_start_date
        params["END_DATE"] = trading_day_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        df_result = query_to_dataframe(result)
        df_result.rename(columns={"Value": "value", "Score": "value", "score": "value", "tradedate": "Date"},
                         inplace=True)
        try:
            df_result['trading_day'] = df_result['Date'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        except:
            df_result['trading_day'] = df_result['Date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
        c_result = df_result[['trading_day', 'value']]
        return c_result
    return result


# 基金交易状态
def get_fund_info_handle(htsc_code, trading_day):
    query_type = 1102010003

    params = {}
    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if trading_day:
        trading_day_start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        trading_day_end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["START_DATE"] = trading_day_start_date
        params["END_DATE"] = trading_day_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'exchange', 'delisting_date', 'trading_day', 'trading_state', 'prev_close', 'open',
             'high', 'low', 'close', 'discount_rate', 'backward_adjusted_closing_price', 'volume', 'value',
             'turnover_deals',
             'day_change', 'unit_nav', 'discount', 'discount_ratio', 'day_change_rate', 'turnover_rate', 'amplitude']]
        return c_result

    return result


# 基金衍生数据
def get_fund_target_handle(htsc_code, exchange, end_date):
    query_type = 1102080005
    exchange_code_map = {'XSHG': '101', 'XSHE': '105', 'OTHERS': '999'}

    params = {}
    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if exchange:
        try:
            params["EXCHANGE_CODE"] = exchange_code_map[exchange]
        except:
            return 'exchange does not exist'
    else:
        params["EXCHANGE_CODE"] = ''

    if end_date:
        end_date_start_date = datetime.strftime(end_date[0], '%Y%m%d')
        end_date_end_date = datetime.strftime(end_date[1], '%Y%m%d')
        params["START_DATE"] = end_date_start_date
        params["END_DATE"] = end_date_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'exchange', 'end_date', 'net_unit', 'total_net_unit', 'post_net_unit', 'd1_navgr',
             'w1_navg', 'w1_navgr', 'w4_navg', 'w4_navgr', 'w13_navg', 'w13_navgr', 'w26_navg', 'w26_navgr', 'w52_navg',
             'w52_navgr', 'ytdn_avg', 'ytdn_avgr', 'y3_navg', 'y5_navg', 'sl_navg', 'navg_vol', 'beta', 'sharper',
             'jensenid', 'treynorid', 'r2']]
        return c_result

    return result


# ETF申赎成份券汇总表
def get_etf_component_handle(htsc_code, pub_date, trading_day):
    query_type = 1102010007

    mexchangecode_map = {101: '.SH', 105: '.SZ', 106:'.BJ',116:'.SH.FI',121:'.CF',131:'.SHF',132:'.DCE',133:'.ZCE',134:'.INE',135:'.GFE',141:'.SGE', 161:'.HK',
                         301: '.A',  303:'.N',
                         461:'.LME',
                         501:'.AX',
                         702:'.SZ.FI',704:'.KS',710: '.O',714:'.ICE',
                         10145:'.EUREX',10148:'.LIFFE',None:''}


    params = {}
    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if pub_date:
        pub_date_start_date = datetime.strftime(pub_date[0], '%Y%m%d')
        pub_date_end_date = datetime.strftime(pub_date[1], '%Y%m%d')
        params["PUB_DATE_START_DATE"] = pub_date_start_date
        params["PUB_DATE_END_DATE"] = pub_date_end_date
    else:
        params["PUB_DATE_START_DATE"] = ''
        params["PUB_DATE_END_DATE"] = ''

    if trading_day:
        trading_day_start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        trading_day_end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["TRADING_DAY_START_DATE"] = trading_day_start_date
        params["TRADING_DAY_END_DATE"] = trading_day_end_date
    else:
        params["TRADING_DAY_START_DATE"] = ''
        params["TRADING_DAY_END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)



    if isinstance(result, list):

        result = paging_data_merge(result, query_type, params)

        df_result = query_to_dataframe(result)
     
        df_result['mexchange'] = df_result['MEXCHANGECODE'].map(mexchangecode_map).fillna('')
  
    
        df_result['stock_code'] = df_result['MTRADINGCODE'] + df_result['mexchange']

        df_result = change_column_name(df_result)
        c_result = df_result[
            ['htsc_code', 'exchange', 'trading_day', 'sub_comp_list', 'pub_date', 'stock_code', 'stock_name', 'c_type',
             'component_num', 'unit', 'is_cash_substitute', 'cash_substitute_rate', 'cash_substitute', 'sub_replace',
             'red_replace']]
        
        return c_result

    return result


# 个股公募持仓
def get_public_fund_portfolio_handle(htsc_code, name, exchange, end_date):
    query_type = 1102050005

    exchange_code_map = {'XSHG': '101', 'XSHE': '105', 'XBSE': '106', 'NEEQ': '111', 'XHKG': '161'}

    params = {}
    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if name:
        params["SECCU_ABBR"] = name
    else:
        params["SECCU_ABBR"] = ''

    if exchange:
        try:
            params["EXCHANGE_CODE"] = exchange_code_map[exchange]
        except:
            return 'exchange does not exist'
    else:
        params["EXCHANGE_CODE"] = ''

    if end_date:
        end_date_start_date = datetime.strftime(end_date[0], '%Y%m%d')
        end_date_end_date = datetime.strftime(end_date[1], '%Y%m%d')
        params["END_DATE_START_DATE"] = end_date_start_date
        params["END_DATE_END_DATE"] = end_date_end_date
    else:
        params["END_DATE_START_DATE"] = ''
        params["END_DATE_END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'name', 'exchange', 'end_date', 'count_fund', 'sum_holding_val', 'sum_holding_vol',
             'num_holding', 'ranks']]
        return c_result

    return result


# ETF申购赎回清单
def get_etf_redemption_handle(htsc_code, exchange, trading_day):
    query_type = 1102010008

    exchange_code_map = {'XSHG': '101', 'XSHE': '105'}

    params = {}
    if htsc_code:
        params["HTSC_SECURITY_ID"] = htsc_code
    else:
        params["HTSC_SECURITY_ID"] = ''

    if exchange:
        try:
            params["EXCHANGE_CODE"] = exchange_code_map[exchange]
        except:
            return 'exchange does not exist'
    else:
        params["EXCHANGE_CODE"] = ''

    if trading_day:
        trading_day_start_date = datetime.strftime(trading_day[0], '%Y%m%d')
        trading_day_end_date = datetime.strftime(trading_day[1], '%Y%m%d')
        params["TRADING_DAY_START_DATE"] = trading_day_start_date
        params["TRADING_DAY_END_DATE"] = trading_day_end_date
    else:
        params["TRADING_DAY_START_DATE"] = ''
        params["TRADING_DAY_END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = change_column_name(df_result)

        c_result = df_result[
            ['htsc_code', 'exchange', 'trading_day', 'cash_dif', 'min_pr_aset', 'esti_cash', 'cash_sub_up_limit',
             'min_pr_units', 'pr_permit', 'con_num', 'purchase_cap', 'redemption_cap', 'price_date', 'net_asset',
             'is_iopv']]
        return c_result

    return result


# 静态信息-按标的查询
def get_basic_info_handle(htsc_code):
    query_type = 1003010005

    if isinstance(htsc_code, list):
        htsc_code = ",".join(htsc_code)

    params = {'HTSC_SECURITY_IDS': htsc_code}

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):

        df_result = query_to_dataframe(result)
        # SecurityType和SecurityIDSource对应数组
        security_type_idsource_np = df_result[['SecurityType', 'SecurityIDSource']].drop_duplicates().values
        df_result = column_renaming(df_result, 'get_basic_info')

        all_result = pd.DataFrame()
        security_type_idsource_dict = {
            'IndexType': {
                'XSHG': ['htsc_code', 'name', 'exchange', 'security_type', 'time', 'prev_close'],
                'XSHE': ['htsc_code', 'name', 'exchange', 'security_type', 'time', 'prev_close'],
                'CSI': ['htsc_code', 'name', 'exchange', 'security_type', 'time', 'prev_close'],
                'CNI': ['htsc_code', 'name', 'exchange', 'security_type', 'time', 'prev_close'],
            },

            'StockType': {
                'XBSE': ['htsc_code', 'name', 'exchange', 'security_type',
                         'security_sub_type', 'listing_date', 'total_share', 'listed_share',
                         'time', 'trading_phase', 'prev_close', 'max', 'min',
                         'lot_size', 'tick_size', 'buy_qty_unit', 'sell_qty_unit'],
                'HKSC': ['htsc_code', 'name', 'exchange', 'security_type',
                         'security_sub_type', 'listing_date', 'time', 'prev_close', 'max',
                         'min', 'lot_size', 'hk_spread_table_code', 'sh_hk_connect',
                         'sz_hk_connect', 'is_vcm', 'is_cas', 'is_pos'],
                'HGHQ': ['htsc_code', 'name', 'exchange', 'security_type',
                         'security_sub_type', 'listed_share', 'time', 'max', 'min',
                         'lot_size', 'tick_size', 'buy_qty_unit', 'sell_qty_unit',
                         'buy_qty_upper_limit', 'sell_qty_upper_limit'],
                'XSHG': ['htsc_code', 'name', 'exchange', 'security_type',
                         'security_sub_type', 'listing_date', 'listed_share', 'time',
                         'trading_phase', 'prev_close', 'max', 'min', 'buy_qty_unit',
                         'sell_qty_unit', 'buy_qty_upper_limit', 'sell_qty_upper_limit',
                         'buy_qty_lower_limit', 'sell_qty_lower_limit'],
                'XSHE': ['htsc_code', 'name', 'exchange', 'security_type',
                         'security_sub_type', 'listing_date', 'total_share', 'listed_share',
                         'time', 'trading_phase', 'prev_close', 'max', 'min',
                         'buy_qty_unit', 'sell_qty_unit', 'buy_qty_upper_limit',
                         'sell_qty_upper_limit'],
            },

            # 基金
            'FundType': {
                'XSHG': ['htsc_code', 'name', 'exchange', 'security_type',
                         'security_sub_type', 'listing_date', 'time', 'trading_phase',
                         'prev_close', 'max', 'min', 'buy_qty_unit', 'sell_qty_unit',
                         'buy_qty_upper_limit', 'sell_qty_upper_limit', 'buy_qty_lower_limit',
                         'sell_qty_lower_limit'],
                'XSHE': ['htsc_code', 'name', 'exchange', 'security_type',
                         'security_sub_type', 'listing_date', 'total_share', 'listed_share',
                         'time', 'trading_phase', 'prev_close', 'max', 'min',
                         'buy_qty_unit', 'sell_qty_unit', 'buy_qty_upper_limit',
                         'sell_qty_upper_limit'],
            },

            # 债券
            'BondType': {
                'XSHG': ['htsc_code', 'name', 'exchange', 'security_type',
                         'security_sub_type', 'listing_date', 'time', 'trading_phase',
                         'prev_close', 'max', 'min', 'buy_qty_unit', 'sell_qty_unit',
                         'buy_qty_upper_limit', 'sell_qty_upper_limit', 'buy_qty_lower_limit',
                         'sell_qty_lower_limit'],
                'XSHE': ['htsc_code', 'name', 'exchange', 'security_type',
                         'security_sub_type', 'listing_date', 'total_share', 'listed_share',
                         'time', 'trading_phase', 'prev_close', 'max', 'min',
                         'tick_size', 'expire_date', 'buy_qty_unit', 'sell_qty_unit',
                         'buy_qty_upper_limit', 'sell_qty_upper_limit', 'buy_qty_lower_limit',
                         'sell_qty_lower_limit'],

                'XBSE': ['htsc_code', 'name', 'exchange', 'security_type',
                         'security_sub_type', 'listing_date', 'total_share', 'listed_share',
                         'time', 'trading_phase', 'prev_close', 'max', 'lot_size',
                         'tick_size', 'buy_qty_unit', 'sell_qty_unit', 'base_contract_id'],

            },

            # 期货
            'FuturesType': {
                'CCFX': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date', 'time',
                         'trading_phase', 'prev_close', 'max', 'min', 'tick_size', 'delivery_year', 'delivery_month',
                         'instrument_id', 'instrument_name', 'exchange_inst_id', 'product_id',
                         'max_market_order_volume', 'min_market_order_volume', 'max_limit_order_volume',
                         'min_limit_order_volume', 'volume_multiple', 'create_date', 'expire_date', 'start_deliv_date',
                         'end_deliv_date', 'position_type', 'long_margin_ratio', 'short_margin_ratio',
                         'max_margin_side_algorithm', 'pre_open_interest', 'base_contract_id'],

                'XSGE': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date', 'time',
                         'trading_phase', 'prev_close', 'max', 'min', 'tick_size', 'delivery_year', 'delivery_month',
                         'instrument_id', 'instrument_name', 'exchange_inst_id', 'product_id',
                         'max_market_order_volume', 'min_market_order_volume', 'max_limit_order_volume',
                         'min_limit_order_volume', 'volume_multiple', 'create_date', 'expire_date', 'start_deliv_date',
                         'end_deliv_date', 'position_type', 'long_margin_ratio', 'short_margin_ratio',
                         'max_margin_side_algorithm', 'pre_open_interest', 'base_contract_id'],

                'XDCE': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date', 'time',
                         'trading_phase', 'prev_close', 'max', 'min', 'tick_size', 'delivery_year', 'delivery_month',
                         'instrument_id', 'instrument_name', 'exchange_inst_id', 'product_id',
                         'max_market_order_volume', 'min_market_order_volume', 'max_limit_order_volume',
                         'min_limit_order_volume', 'volume_multiple', 'create_date', 'expire_date', 'end_deliv_date',
                         'position_type', 'long_margin_ratio', 'short_margin_ratio', 'max_margin_side_algorithm',
                         'pre_open_interest', 'base_contract_id'],

                'XZCE': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date', 'time',
                         'trading_phase', 'prev_close', 'max', 'min', 'tick_size', 'delivery_year', 'delivery_month',
                         'instrument_id', 'instrument_name', 'exchange_inst_id', 'product_id',
                         'max_market_order_volume', 'min_market_order_volume', 'max_limit_order_volume',
                         'min_limit_order_volume', 'volume_multiple', 'create_date', 'expire_date', 'start_deliv_date',
                         'end_deliv_date', 'position_type', 'long_margin_ratio', 'short_margin_ratio',
                         'max_margin_side_algorithm', 'pre_open_interest', 'base_contract_id'],

            },

            # 期权
            'OptionType': {
                'XSHG': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date',
                         'currency', 'time', 'trading_phase', 'prev_close', 'max', 'min', 'tick_size',
                         'option_contract_id', 'option_contract_symbol', 'option_underlying_security_id',
                         'option_underlying_symbol', 'option_underlying_type', 'option_option_type',
                         'option_call_or_put', 'option_contract_multiplier_unit', 'option_exercise_price',
                         'option_start_date', 'option_end_date', 'option_exercise_date', 'option_delivery_date',
                         'option_expire_date', 'option_up_date_version', 'option_total_long_position',
                         'option_security_close', 'option_settl_price', 'option_underlying_close',
                         'option_price_limit_type', 'option_daily_price_up_limit', 'option_daily_price_down_limit',
                         'option_margin_unit', 'option_margin_ratio_param1', 'option_margin_ratio_param2',
                         'option_round_lot', 'option_lmt_ord_min_floor', 'option_lmt_ord_max_floor',
                         'option_mkt_ord_min_floor', 'option_mkt_ord_max_floor', 'option_tick_size',
                         'option_security_status_flag', 'expire_date'],

                'XSHE': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date',
                         'currency', 'time', 'trading_phase', 'prev_close', 'max', 'min', 'tick_size',
                         'option_contract_id', 'option_contract_symbol', 'option_underlying_security_id',
                         'option_option_type', 'option_call_or_put', 'option_contract_multiplier_unit',
                         'option_exercise_price', 'option_start_date', 'option_end_date', 'option_exercise_date',
                         'option_delivery_date', 'option_expire_date', 'option_security_close', 'option_settl_price',
                         'option_daily_price_up_limit', 'option_daily_price_down_limit', 'option_margin_ratio_param1',
                         'option_margin_ratio_param2', 'option_round_lot', 'option_tick_size', 'option_List_type',
                         'option_delivery_type', 'option_contract_position', 'option_buy_qty_upper_limit',
                         'option_Sell_qty_upper_limit', 'option_market_order_buy_qty_upper_limit',
                         'option_market_order_sell_qty_upper_limit', 'option_quote_order_buy_qty_upper_limit',
                         'option_quote_order_sell_qty_upper_limit', 'option_buy_qty_unit', 'option_sell_qty_unit',
                         'option_last_sell_margin', 'option_sell_margin', 'option_market_maker_flag',
                         'option_combination_strategy', 'former_symbol'],

                'CCFX': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date', 'time',
                         'trading_phase', 'prev_close', 'max', 'min', 'option_contract_id', 'option_contract_symbol',
                         'option_underlying_security_id', 'option_underlying_type', 'option_option_type',
                         'option_call_or_put', 'option_contract_multiplier_unit', 'option_exercise_price',
                         'option_start_date', 'option_end_date', 'option_exercise_date', 'option_delivery_date',
                         'option_expire_date', 'option_security_close', 'option_settl_price',
                         'option_lmt_ord_min_floor', 'option_lmt_ord_max_floor', 'option_mkt_ord_min_floor',
                         'option_tick_size', 'delivery_year', 'delivery_month', 'exchange_inst_id', 'product_id',
                         'volume_multiple', 'pre_open_interest'],

                'XSGE': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'time', 'trading_phase',
                         'option_contract_id', 'option_contract_symbol', 'option_underlying_security_id',
                         'option_underlying_type', 'option_option_type', 'option_call_or_put',
                         'option_contract_multiplier_unit', 'option_exercise_price', 'option_start_date',
                         'option_end_date', 'option_exercise_date', 'option_expire_date', 'option_lmt_ord_min_floor',
                         'option_lmt_ord_max_floor', 'option_mkt_ord_min_floor', 'option_mkt_ord_max_floor',
                         'option_tick_size'],

                'XDCE': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date', 'time',
                         'trading_phase', 'prev_close', 'max', 'min', 'option_contract_id', 'option_contract_symbol',
                         'option_underlying_security_id', 'option_underlying_type', 'option_option_type',
                         'option_call_or_put', 'option_contract_multiplier_unit', 'option_exercise_price',
                         'option_start_date', 'option_end_date', 'option_exercise_date', 'option_delivery_date',
                         'option_expire_date', 'option_security_close', 'option_settl_price',
                         'option_lmt_ord_min_floor', 'option_lmt_ord_max_floor', 'option_mkt_ord_min_floor',
                         'option_mkt_ord_max_floor', 'option_tick_size', 'delivery_year', 'delivery_month',
                         'exchange_inst_id', 'product_id', 'volume_multiple'],

                'XZCE': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date', 'time',
                         'trading_phase', 'prev_close', 'max', 'min', 'option_contract_id', 'option_contract_symbol',
                         'option_underlying_security_id', 'option_underlying_type', 'option_option_type',
                         'option_call_or_put', 'option_contract_multiplier_unit', 'option_exercise_price',
                         'option_start_date', 'option_end_date', 'option_exercise_date', 'option_delivery_date',
                         'option_expire_date', 'option_security_close', 'option_settl_price',
                         'option_lmt_ord_min_floor', 'option_lmt_ord_max_floor', 'option_mkt_ord_min_floor',
                         'option_mkt_ord_max_floor', 'option_tick_size', 'delivery_year', 'delivery_month',
                         'exchange_inst_id', 'product_id', 'volume_multiple'],

            },
        }
        # 筛选同类数据合并
        for security_type_idsource_group in security_type_idsource_np:

            group_security_type = security_type_idsource_group[0]
            group_exchange = security_type_idsource_group[1]
            security_group_data = df_result[
                (df_result['exchange'] == group_exchange) & (df_result['security_type'] == group_security_type)]

            c_cloumn_list = None
            security_type_param = security_type_idsource_dict.get(group_security_type)
            if security_type_param:
                c_cloumn_list = security_type_param.get(group_exchange)

            if c_cloumn_list:
                c_cloumn_df = pd.DataFrame(columns=c_cloumn_list)
                c_cloumn_df = pd.concat([c_cloumn_df, security_group_data], axis=0).reset_index(drop=True)
                c_result = c_cloumn_df[c_cloumn_list]
                all_result = pd.concat([all_result, c_result], axis=0).reset_index(drop=True)
            else:
                all_result = pd.concat([all_result, security_group_data], axis=0).reset_index(drop=True)

        if not all_result.empty:

            upper_cols = [col for col in all_result.columns if any(c.isupper() for c in col)]
            all_result = all_result.drop(columns=upper_cols)

            for params_column in ['constant_params', 'constant_switch_status']:
                if params_column in all_result:
                    all_result[params_column] = [
                        [{convert_to_snake_case(k): v for k, v in li.items()} for li in i] if isinstance(i, list) else i
                        for i in all_result[params_column]]

            for time_format in ['time', 'listing_date', 'expire_date', 'create_date', 'start_deliv_date',
                                'end_deliv_date', 'option_start_date', 'option_end_date', 'option_exercise_date',
                                'option_delivery_date', 'option_expire_date', 'exchange_date', 'delist_date']:
                if time_format in all_result:
                    all_result[time_format] = [
                        f'{x[:4]}-{x[4:6]}-{x[6:]}' if isinstance(x, str) and len(x) == 8 else x for x in
                        all_result[time_format]]

            if 'security_type' in all_result:
                security_type_map = EnumeratedMapping.security_type_map([])
                all_result['security_type'] = [security_type_map.get(x) if security_type_map.get(x) else x for x in
                                               all_result['security_type']]

            if "security_sub_type" in all_result:
                security_sub_type_map = EnumeratedMapping.security_sub_type_map()

                all_result['security_sub_type'] = [security_sub_type_map.get(x) if security_sub_type_map.get(x) else x
                                                   for x in
                                                   all_result['security_sub_type']]

            if "trading_phase" in all_result:
                trading_phase_map = EnumeratedMapping.trading_phase_code_map()
                all_result['trading_phase'] = [trading_phase_map.get(x) if trading_phase_map.get(x) else x for x in
                                               all_result['trading_phase']]

        return all_result

    return result


# 静态信息-按证券类型和市场查询
def get_all_basic_info_handle(security_type, exchange, today):
    if today:
        query_type = 1003010003
    else:
        query_type = 1003010011

    if isinstance(exchange, str):
        exchange = [exchange]

    original_security_type_map = EnumeratedMapping.security_type_map(
        ['IndexType', 'StockType', 'FundType', 'BondType', 'OptionType', 'FuturesType', 'SPFuturesType',
         'WarrantType', 'RateType', 'SpotType'])
    security_type_map = {v: k for k, v in original_security_type_map.items()}
    security_type_param = security_type_map.get(security_type)

    security_type_idsource_dict = {
        'IndexType': {
            'XSHG': ['htsc_code', 'name', 'exchange', 'security_type', 'time', 'prev_close'],
            'XSHE': ['htsc_code', 'name', 'exchange', 'security_type', 'time', 'prev_close'],
            'CSI': ['htsc_code', 'name', 'exchange', 'security_type', 'time', 'prev_close'],
            'CNI': ['htsc_code', 'name', 'exchange', 'security_type', 'time', 'prev_close'],
        },

        'StockType': {
            'XBSE': ['htsc_code', 'name', 'exchange', 'security_type',
                     'security_sub_type', 'listing_date', 'total_share', 'listed_share',
                     'time', 'trading_phase', 'prev_close', 'max', 'min',
                     'lot_size', 'tick_size', 'buy_qty_unit', 'sell_qty_unit'],
            'HKSC': ['htsc_code', 'name', 'exchange', 'security_type',
                     'security_sub_type', 'listing_date', 'time', 'prev_close', 'max',
                     'min', 'lot_size', 'hk_spread_table_code', 'sh_hk_connect',
                     'sz_hk_connect', 'is_vcm', 'is_cas', 'is_pos'],
            'HGHQ': ['htsc_code', 'name', 'exchange', 'security_type',
                     'security_sub_type', 'listed_share', 'time', 'max', 'min',
                     'lot_size', 'tick_size', 'buy_qty_unit', 'sell_qty_unit',
                     'buy_qty_upper_limit', 'sell_qty_upper_limit'],
            'XSHG': ['htsc_code', 'name', 'exchange', 'security_type',
                     'security_sub_type', 'listing_date', 'listed_share', 'time',
                     'trading_phase', 'prev_close', 'max', 'min', 'buy_qty_unit',
                     'sell_qty_unit', 'buy_qty_upper_limit', 'sell_qty_upper_limit',
                     'buy_qty_lower_limit', 'sell_qty_lower_limit'],
            'XSHE': ['htsc_code', 'name', 'exchange', 'security_type',
                     'security_sub_type', 'listing_date', 'total_share', 'listed_share',
                     'time', 'trading_phase', 'prev_close', 'max', 'min',
                     'buy_qty_unit', 'sell_qty_unit', 'buy_qty_upper_limit',
                     'sell_qty_upper_limit'],
        },

        # 基金
        'FundType': {
            'XSHG': ['htsc_code', 'name', 'exchange', 'security_type',
                     'security_sub_type', 'listing_date', 'time', 'trading_phase',
                     'prev_close', 'max', 'min', 'buy_qty_unit', 'sell_qty_unit',
                     'buy_qty_upper_limit', 'sell_qty_upper_limit', 'buy_qty_lower_limit',
                     'sell_qty_lower_limit'],
            'XSHE': ['htsc_code', 'name', 'exchange', 'security_type',
                     'security_sub_type', 'listing_date', 'total_share', 'listed_share',
                     'time', 'trading_phase', 'prev_close', 'max', 'min',
                     'buy_qty_unit', 'sell_qty_unit', 'buy_qty_upper_limit',
                     'sell_qty_upper_limit'],
        },

        # 债券
        'BondType': {
            'XSHG': ['htsc_code', 'name', 'exchange', 'security_type',
                     'security_sub_type', 'listing_date', 'time', 'trading_phase',
                     'prev_close', 'max', 'min', 'buy_qty_unit', 'sell_qty_unit',
                     'buy_qty_upper_limit', 'sell_qty_upper_limit', 'buy_qty_lower_limit',
                     'sell_qty_lower_limit'],
            'XSHE': ['htsc_code', 'name', 'exchange', 'security_type',
                     'security_sub_type', 'listing_date', 'total_share', 'listed_share',
                     'time', 'trading_phase', 'prev_close', 'max', 'min',
                     'tick_size', 'expire_date', 'buy_qty_unit', 'sell_qty_unit',
                     'buy_qty_upper_limit', 'sell_qty_upper_limit', 'buy_qty_lower_limit',
                     'sell_qty_lower_limit'],

            'XBSE': ['htsc_code', 'name', 'exchange', 'security_type',
                     'security_sub_type', 'listing_date', 'total_share', 'listed_share',
                     'time', 'trading_phase', 'prev_close', 'max', 'lot_size',
                     'tick_size', 'buy_qty_unit', 'sell_qty_unit', 'base_contract_id'],

        },

        # 期货
        'FuturesType': {
            'CCFX': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date', 'time',
                     'trading_phase', 'prev_close', 'max', 'min', 'tick_size', 'delivery_year', 'delivery_month',
                     'instrument_id', 'instrument_name', 'exchange_inst_id', 'product_id',
                     'max_market_order_volume', 'min_market_order_volume', 'max_limit_order_volume',
                     'min_limit_order_volume', 'volume_multiple', 'create_date', 'expire_date', 'start_deliv_date',
                     'end_deliv_date', 'position_type', 'long_margin_ratio', 'short_margin_ratio',
                     'max_margin_side_algorithm', 'pre_open_interest', 'base_contract_id'],

            'XSGE': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date', 'time',
                     'trading_phase', 'prev_close', 'max', 'min', 'tick_size', 'delivery_year', 'delivery_month',
                     'instrument_id', 'instrument_name', 'exchange_inst_id', 'product_id',
                     'max_market_order_volume', 'min_market_order_volume', 'max_limit_order_volume',
                     'min_limit_order_volume', 'volume_multiple', 'create_date', 'expire_date', 'start_deliv_date',
                     'end_deliv_date', 'position_type', 'long_margin_ratio', 'short_margin_ratio',
                     'max_margin_side_algorithm', 'pre_open_interest', 'base_contract_id'],

            'XDCE': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date', 'time',
                     'trading_phase', 'prev_close', 'max', 'min', 'tick_size', 'delivery_year', 'delivery_month',
                     'instrument_id', 'instrument_name', 'exchange_inst_id', 'product_id',
                     'max_market_order_volume', 'min_market_order_volume', 'max_limit_order_volume',
                     'min_limit_order_volume', 'volume_multiple', 'create_date', 'expire_date', 'end_deliv_date',
                     'position_type', 'long_margin_ratio', 'short_margin_ratio', 'max_margin_side_algorithm',
                     'pre_open_interest', 'base_contract_id'],

            'XZCE': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date', 'time',
                     'trading_phase', 'prev_close', 'max', 'min', 'tick_size', 'delivery_year', 'delivery_month',
                     'instrument_id', 'instrument_name', 'exchange_inst_id', 'product_id',
                     'max_market_order_volume', 'min_market_order_volume', 'max_limit_order_volume',
                     'min_limit_order_volume', 'volume_multiple', 'create_date', 'expire_date', 'start_deliv_date',
                     'end_deliv_date', 'position_type', 'long_margin_ratio', 'short_margin_ratio',
                     'max_margin_side_algorithm', 'pre_open_interest', 'base_contract_id'],

        },

        # 期权
        'OptionType': {
            'XSHG': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date',
                     'currency', 'time', 'trading_phase', 'prev_close', 'max', 'min', 'tick_size',
                     'option_contract_id', 'option_contract_symbol', 'option_underlying_security_id',
                     'option_underlying_symbol', 'option_underlying_type', 'option_option_type',
                     'option_call_or_put', 'option_contract_multiplier_unit', 'option_exercise_price',
                     'option_start_date', 'option_end_date', 'option_exercise_date', 'option_delivery_date',
                     'option_expire_date', 'option_up_date_version', 'option_total_long_position',
                     'option_security_close', 'option_settl_price', 'option_underlying_close',
                     'option_price_limit_type', 'option_daily_price_up_limit', 'option_daily_price_down_limit',
                     'option_margin_unit', 'option_margin_ratio_param1', 'option_margin_ratio_param2',
                     'option_round_lot', 'option_lmt_ord_min_floor', 'option_lmt_ord_max_floor',
                     'option_mkt_ord_min_floor', 'option_mkt_ord_max_floor', 'option_tick_size',
                     'option_security_status_flag', 'expire_date'],

            'XSHE': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date',
                     'currency', 'time', 'trading_phase', 'prev_close', 'max', 'min', 'tick_size',
                     'option_contract_id', 'option_contract_symbol', 'option_underlying_security_id',
                     'option_option_type', 'option_call_or_put', 'option_contract_multiplier_unit',
                     'option_exercise_price', 'option_start_date', 'option_end_date', 'option_exercise_date',
                     'option_delivery_date', 'option_expire_date', 'option_security_close', 'option_settl_price',
                     'option_daily_price_up_limit', 'option_daily_price_down_limit', 'option_margin_ratio_param1',
                     'option_margin_ratio_param2', 'option_round_lot', 'option_tick_size', 'option_List_type',
                     'option_delivery_type', 'option_contract_position', 'option_buy_qty_upper_limit',
                     'option_Sell_qty_upper_limit', 'option_market_order_buy_qty_upper_limit',
                     'option_market_order_sell_qty_upper_limit', 'option_quote_order_buy_qty_upper_limit',
                     'option_quote_order_sell_qty_upper_limit', 'option_buy_qty_unit', 'option_sell_qty_unit',
                     'option_last_sell_margin', 'option_sell_margin', 'option_market_maker_flag',
                     'option_combination_strategy', 'former_symbol'],

            'CCFX': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date', 'time',
                     'trading_phase', 'prev_close', 'max', 'min', 'option_contract_id', 'option_contract_symbol',
                     'option_underlying_security_id', 'option_underlying_type', 'option_option_type',
                     'option_call_or_put', 'option_contract_multiplier_unit', 'option_exercise_price',
                     'option_start_date', 'option_end_date', 'option_exercise_date', 'option_delivery_date',
                     'option_expire_date', 'option_security_close', 'option_settl_price',
                     'option_lmt_ord_min_floor', 'option_lmt_ord_max_floor', 'option_mkt_ord_min_floor',
                     'option_tick_size', 'delivery_year', 'delivery_month', 'exchange_inst_id', 'product_id',
                     'volume_multiple', 'pre_open_interest'],

            'XSGE': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'time', 'trading_phase',
                     'option_contract_id', 'option_contract_symbol', 'option_underlying_security_id',
                     'option_underlying_type', 'option_option_type', 'option_call_or_put',
                     'option_contract_multiplier_unit', 'option_exercise_price', 'option_start_date',
                     'option_end_date', 'option_exercise_date', 'option_expire_date', 'option_lmt_ord_min_floor',
                     'option_lmt_ord_max_floor', 'option_mkt_ord_min_floor', 'option_mkt_ord_max_floor',
                     'option_tick_size'],

            'XDCE': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date', 'time',
                     'trading_phase', 'prev_close', 'max', 'min', 'option_contract_id', 'option_contract_symbol',
                     'option_underlying_security_id', 'option_underlying_type', 'option_option_type',
                     'option_call_or_put', 'option_contract_multiplier_unit', 'option_exercise_price',
                     'option_start_date', 'option_end_date', 'option_exercise_date', 'option_delivery_date',
                     'option_expire_date', 'option_security_close', 'option_settl_price',
                     'option_lmt_ord_min_floor', 'option_lmt_ord_max_floor', 'option_mkt_ord_min_floor',
                     'option_mkt_ord_max_floor', 'option_tick_size', 'delivery_year', 'delivery_month',
                     'exchange_inst_id', 'product_id', 'volume_multiple'],

            'XZCE': ['htsc_code', 'name', 'exchange', 'security_type', 'security_sub_type', 'listing_date', 'time',
                     'trading_phase', 'prev_close', 'max', 'min', 'option_contract_id', 'option_contract_symbol',
                     'option_underlying_security_id', 'option_underlying_type', 'option_option_type',
                     'option_call_or_put', 'option_contract_multiplier_unit', 'option_exercise_price',
                     'option_start_date', 'option_end_date', 'option_exercise_date', 'option_delivery_date',
                     'option_expire_date', 'option_security_close', 'option_settl_price',
                     'option_lmt_ord_min_floor', 'option_lmt_ord_max_floor', 'option_mkt_ord_min_floor',
                     'option_mkt_ord_max_floor', 'option_tick_size', 'delivery_year', 'delivery_month',
                     'exchange_inst_id', 'product_id', 'volume_multiple'],

        },

    }

    all_result = pd.DataFrame()
    for query_exchange in exchange:

        params = {"SECURITY_ID_SOURCE": query_exchange, "SECURITY_TYPE": security_type_param}

        if today:
            params['IS_NEED_ALL_HISTORY'] = 'false'

        result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
        if isinstance(result, list):
            df_result = query_to_dataframe(result)
            df_result = column_renaming(df_result, 'get_basic_info')

            c_cloumn_list = None
            security_type_template = security_type_idsource_dict.get(security_type_param)
            if security_type_template:
                c_cloumn_list = security_type_template.get(query_exchange)

            if c_cloumn_list:
                c_cloumn_df = pd.DataFrame(columns=c_cloumn_list)
                c_cloumn_df = pd.concat([c_cloumn_df, df_result], axis=0).reset_index(drop=True)
                c_result = c_cloumn_df[c_cloumn_list]
                all_result = pd.concat([all_result, c_result], axis=0).reset_index(drop=True)
            else:
                all_result = pd.concat([all_result, df_result], axis=0).reset_index(drop=True)

        else:
            print('time out:', query_exchange)

    if not all_result.empty:

        if 'security_type' in all_result:
            all_result['security_type'] = all_result['security_type'].apply(lambda x: original_security_type_map.get(x))

        for params_column in ['constant_params', 'constant_switch_status']:
            if params_column in all_result:
                all_result[params_column] = [
                    [{convert_to_snake_case(k): v for k, v in li.items()} for li in i] if isinstance(i, list) else i
                    for i in all_result[params_column]]

        for time_format in ['time', 'listing_date', 'expire_date', 'create_date', 'start_deliv_date',
                            'end_deliv_date', 'option_start_date', 'option_end_date', 'option_exercise_date',
                            'option_delivery_date', 'option_expire_date', 'exchange_date', 'delist_date']:
            if time_format in all_result:
                all_result[time_format] = [
                    f'{x[:4]}-{x[4:6]}-{x[6:]}' if isinstance(x, str) and len(x) == 8 else x for x in
                    all_result[time_format]]

        if "security_sub_type" in all_result:
            security_sub_type_map = EnumeratedMapping.security_sub_type_map()

            all_result['security_sub_type'] = [security_sub_type_map.get(x) if security_sub_type_map.get(x) else x
                                               for x in
                                               all_result['security_sub_type']]

        if "trading_phase" in all_result:
            trading_phase_map = EnumeratedMapping.trading_phase_code_map()
            all_result['trading_phase'] = [trading_phase_map.get(x) if trading_phase_map.get(x) else x for x in
                                           all_result['trading_phase']]

        return all_result

    return pd.DataFrame()


# 资讯数据查询
def get_news_handle(htsc_code, event_ids, pub_date):
    query_type = 1120010001

    search_type_map = {'0': '新闻', '1': '公告', '2': '舆情'}
    is_valid_map = {0: '已删除的消息', 1: '有效的消息'}

    params = {}

    if htsc_code:
        if isinstance(htsc_code, str):
            htsc_code = [htsc_code]
        params['HTSC_SECURITY_IDS'] = ",".join(htsc_code)
    else:
        params['HTSC_SECURITY_IDS'] = ''

    if event_ids:
        if isinstance(event_ids, str):
            event_ids = [event_ids]
        params['EVENT_IDS'] = ",".join(event_ids)

    if pub_date:
        pub_date_start_date = datetime.strftime(pub_date[0], '%Y-%m-%d')
        pub_date_end_date = datetime.strftime(pub_date[1], '%Y-%m-%d')
        params["PUB_DATE_START_DATE"] = pub_date_start_date
        params["PUB_DATE_END_DATE"] = pub_date_end_date
    else:
        params["PUB_DATE_START_DATE"] = ''
        params["PUB_DATE_END_DATE"] = ''

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):

        result = paging_news_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)

        if 'htsc_codes' in df_result and 'htsc_code' in df_result:
            df_result['htsc_code'].fillna(df_result["htsc_codes"], inplace=True)

        elif 'htsc_codes' in df_result and 'htsc_code' not in df_result:
            df_result.rename(columns={'htsc_codes': 'htsc_code'}, inplace=True)

        if 'htsc_codes' in df_result:
            df_result.drop(columns=['htsc_codes'], inplace=True)
        df_result.drop(columns=['TotalCount'], inplace=True)

        df_result['htsc_code'] = df_result['htsc_code'].apply(lambda x: x.strip(',') if isinstance(x, str) else x)
        df_result['is_valid'] = df_result['is_valid'].apply(lambda x: is_valid_map.get(x) if is_valid_map.get(x) else x)
        df_result['search_type'] = df_result['search_type'].apply(
            lambda x: search_type_map.get(x) if search_type_map.get(x) else x)

        return df_result

    return result


# EDB基本信息
def find_edb_index_handle(name):
    query_type = 1110010001

    if name:
        params = {"INDEX_NAME": name}
    else:
        params = {"": ""}

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)

    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = column_renaming(df_result, 'find_edb_index')
        del df_result['TotalCount']
        return df_result

    return result


# EDB数据
def edb_handle(indexes=None, pub_date=None):
    query_type = 1110010002

    params = {}
    if pub_date:
        pub_date_start_date = datetime.strftime(pub_date[0], '%Y%m%d')
        pub_date_end_date = datetime.strftime(pub_date[1], '%Y%m%d')
        params["START_DATE"] = pub_date_start_date
        params["END_DATE"] = pub_date_end_date
    else:
        params["START_DATE"] = ''
        params["END_DATE"] = ''

    if indexes:
        all_result = []
        for index_id in indexes:
            params['INDEX_ID'] = index_id
            result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
            if isinstance(result, list):
                params_copy = params.copy()
                result = paging_data_merge(result, query_type, params_copy)
                all_result.extend(result)
    else:
        all_result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
        if isinstance(all_result, list):
            all_result = paging_data_merge(all_result, query_type, params)

    if all_result and isinstance(all_result, list):
        df_result = query_to_dataframe(all_result)
        df_result = column_renaming(df_result, 'edb')
        del df_result['TotalCount']
        return df_result

    return pd.DataFrame()


# 华泰研报基本信息表
def get_rpt_basicinfo_ht_handle(id, report_code, time, title, language, is_valid):
    query_type = 1120020001

    params = {}
    if not any([id, report_code, time, title, language, is_valid]):
        params[''] = ''
    else:
        if id:
            params['ID'] = id
        if report_code:
            params['REPORT_CODE'] = report_code
        if time:
            params["START_DATE"] = datetime.strftime(time[0], '%Y%m%d')
            params["END_DATE"] = datetime.strftime(time[1], '%Y%m%d')
        if language:
            params['LANGUAGE'] = language
        if title:
            params['TITLE'] = title
        if is_valid:
            params['IS_VALID'] = is_valid

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = column_renaming(df_result, 'get_rpt_basicinfo_ht')
        del df_result['TotalCount']
        return df_result

    return result


# 研报股票表
def get_rpt_stk_ht_handle(report_code):
    query_type = 1120020002

    if not report_code:
        report_code = ''
    params = {'REPORT_CODE': report_code}

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = column_renaming(df_result, 'get_rpt_stk_ht')
        del df_result['TotalCount']
        return df_result

    return result


# 研报行业表
def get_rpt_industry_ht_handle(report_code):
    query_type = 1120020003

    if not report_code:
        report_code = ''
    params = {'REPORT_CODE': report_code}

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = column_renaming(df_result, 'get_rpt_industry_ht')
        del df_result['TotalCount']
        return df_result

    return result


# 研报作者表
def get_rpt_author_ht_handle(report_code):
    query_type = 1120020004

    if not report_code:
        report_code = ''
    params = {'REPORT_CODE': report_code}

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = column_renaming(df_result, 'get_rpt_author_ht')
        del df_result['TotalCount']
        return df_result

    return result


# 研报附件表
def get_rpt_annex_ht_handle(report_code):
    query_type = 1120020005

    if not report_code:
        report_code = ''
    params = {'REPORT_CODE': report_code}

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = column_renaming(df_result, 'get_rpt_annex_ht')
        del df_result['TotalCount']
        return df_result

    return result


# 研报盈利预测表
def get_rpt_stkpredict_ht_handle(report_code):
    query_type = 1120020006

    if not report_code:
        report_code = ''
    params = {'REPORT_CODE': report_code}

    result = data_handle.get_interface().queryfininfosynchronous(query_type, params)
    if isinstance(result, list):
        result = paging_data_merge(result, query_type, params)
        df_result = query_to_dataframe(result)
        df_result = column_renaming(df_result, 'get_rpt_stkpredict_ht')
        del df_result['TotalCount']
        return df_result

    return result
