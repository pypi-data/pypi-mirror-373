# -*- coding: utf-8 -*-
from datetime import datetime
from .. import data_handle
from ..interface.mdc_enumerated_mapping_table import EnumeratedMapping


# 回放接口 (注意：securitylist 和 securityIdList取并集!!!)
# 回放限制
# 对于回放而言，时间限制由股票只数和天数的乘积决定，要求 回放只数 × 回放天数 × 证券权重 ≤ 450，交易时间段内回放功能 乘积<=200。
# Tick/Transaction/Order回放时间范围限制是30天，每支证券权重为1，即可以回放15只股票30天以内的数据或450支股票1天内数据。
# 日K数据回放时间范围限制是365天，每支证券权重为0.005。
# 分钟K线数据回放时间范围限制是90天，每支证券权重0.05。
# 数据最早可以回放到 2017年1月2日

def playback_tick(htsc_code=None, replay_time=None, fq='pre'):
    '''
    :param htsc_code: 华泰证券ID，入参为list或者string
    :param replay_time: 回放范围，默认为一天，list类型 [datetime，datetime]
    :param fq: 复权，默认前复权”pre”，后复权为”post”，不复权“none”
    '''

    if not fq:
        fq = 'pre'
    fq_map = {"none": 1, "pre": 2, "post": 3}
    exchange_suffix_list = list(EnumeratedMapping.exchange_suffix_map(
        ['XSHG', 'XSHE', 'CSI', 'CNI', 'XBSE', 'HKSC', 'XSGE', 'XDCE', 'XZCE', 'CCFX', 'HTIS', 'XHKG', 'NASDAQ', 'ICE',
         'CME', 'CBOT', 'COMEX', 'NYMEX', 'LME', 'SGX', 'LSE', 'BBG', 'SGEX']).values())

    if not htsc_code:
        print('htsc_code can not be empty')
        return False

    if isinstance(htsc_code, str):
        htsc_code = [htsc_code]

    if isinstance(htsc_code, list) and isinstance(fq, str):
        htscsecurityID_and_types = []
        for code in htsc_code:
            try:
                suffix = code.split(".")[-1]
                if suffix in exchange_suffix_list:
                    htscsecurityID_and_type = {}
                    htscsecurityID_and_type['HTSCSecurityID'] = code
                    htscsecurityID_and_type['EMarketDataType'] = 104
                    htscsecurityID_and_types.append(htscsecurityID_and_type)
                else:
                    print('htsc_code {} does not support'.format(code))
                    return False
            except:
                print('htsc_code {} format error'.format(code))
                return False

        fq = fq_map.get(fq)
        if not fq:
            print('fq does not exist')
            return False

        if replay_time:
            if isinstance(replay_time, list):
                if len(replay_time) > 2:
                    print("replay_time format is not [start_date, end_date]")
                    return False
                if len(replay_time) == 1:
                    replay_time = [replay_time[0], replay_time[0]]
                if not isinstance(replay_time[0], datetime) or not isinstance(replay_time[1], datetime):
                    print("start_date,end_date format is not datetime")
                    return False
            else:
                print("replay_time format is not list")
                return False
            start_time = datetime.strftime(replay_time[0], '%Y%m%d%H%M%S')
            stop_time = datetime.strftime(replay_time[1], '%Y%m%d%H%M%S')
        else:
            date_str = datetime.now().strftime('%Y%m%d')
            start_time = f"{date_str}000000"
            stop_time = f"{date_str}235959"

        data_handle.get_interface().playCallback(htscsecurityID_and_types, fq, start_time, stop_time)


def playback_trans_and_order(htsc_code=None, replay_time=None, fq='pre'):
    '''
    :param htsc_code: 华泰证券ID，入参为list或者string
    :param replay_time: 回放范围，默认为一天，list类型 [datetime，datetime]
    :param fq: 复权，默认前复权”pre”，后复权为”post”，不复权“none” 0
    '''

    if not fq:
        fq = 'pre'
    fq_map = {"none": 1, "pre": 2, "post": 3}
    exchange_suffix_list = list(EnumeratedMapping.exchange_suffix_map(['XSHG', 'XSHE', 'XHKG']).values())

    if not htsc_code:
        print('htsc_code can not be empty')
        return False

    if isinstance(htsc_code, str):
        htsc_code = [htsc_code]

    if isinstance(htsc_code, list) and isinstance(fq, str):
        htscsecurityID_and_types = []
        for code in htsc_code:
            try:
                suffix = code.split(".")[-1]
                if suffix in exchange_suffix_list:
                    htscsecurityID_and_type = {}
                    htscsecurityID_and_type['HTSCSecurityID'] = code
                    htscsecurityID_and_type['EMarketDataType'] = 107
                    htscsecurityID_and_types.append(htscsecurityID_and_type)
                else:
                    print('htsc_code {} does not support'.format(code))
                    return False
            except:
                print('htsc_code {} format error'.format(code))
                return False

        fq = fq_map.get(fq)
        if not fq:
            print('fq does not exist')
            return False

        if replay_time:
            if isinstance(replay_time, list):
                if len(replay_time) > 2:
                    print("replay_time format is not [start_date, end_date]")
                    return False
                if len(replay_time) == 1:
                    replay_time = [replay_time[0], replay_time[0]]
                if not isinstance(replay_time[0], datetime) or not isinstance(replay_time[1], datetime):
                    print("start_date,end_date format is not datetime")
                    return False
            else:
                print("replay_time format is not list")
                return False
            start_time = datetime.strftime(replay_time[0], '%Y%m%d%H%M%S')
            stop_time = datetime.strftime(replay_time[1], '%Y%m%d%H%M%S')
        else:
            date_str = datetime.now().strftime('%Y%m%d')
            start_time = f"{date_str}000000"
            stop_time = f"{date_str}235959"

        data_handle.get_interface().playCallback(htscsecurityID_and_types, fq, start_time, stop_time)

# def playback_htsc_margin(htsc_code=None, replay_time=None, data_type=None):
#
#     data_type_map = {'security_lending': 59, 'security_lending_record': 82,
#                      'security_lending_statistics_record': 80, 'security_lending_indicative_quote_record': 79}
#     exchange_suffix_list = ['SH', 'SZ', '.HTSM']
#
#
#     if all([htsc_code, data_type]):
#
#         if isinstance(htsc_code, str):
#             htsc_code = [htsc_code]
#
#         if isinstance(htsc_code, list) and isinstance(data_type, str):
#
#             EMarketDataType = data_type_map.get(data_type)
#             if EMarketDataType:
#
#                 htscsecurityID_and_types = []
#                 for code in htsc_code:
#                     try:
#                         suffix = code.split(".")[-1]
#                         if suffix in exchange_suffix_list:
#                             htscsecurityID_and_type = {}
#                             htscsecurityID_and_type['HTSCSecurityID'] = code
#                             htscsecurityID_and_type['EMarketDataType'] = EMarketDataType
#                             htscsecurityID_and_types.append(htscsecurityID_and_type)
#                         else:
#                             print('htsc_code {} does not support'.format(code))
#                             return False
#                     except:
#                         print('htsc_code {} format error'.format(code))
#                         return False
#
#                 if replay_time:
#                     if isinstance(replay_time, list):
#                         if len(replay_time) > 2:
#                             print("replay_time format is not [start_date, end_date]")
#                             return False
#                         if len(replay_time) == 1:
#                             replay_time = [replay_time[0], replay_time[0]]
#                         if not isinstance(replay_time[0], datetime) or not isinstance(replay_time[1], datetime):
#                             print("start_date,end_date format is not datetime")
#                             return False
#                     else:
#                         print("replay_time format is not list")
#                         return False
#                     start_time = datetime.strftime(replay_time[0], '%Y%m%d%H%M%S')
#                     stop_time = datetime.strftime(replay_time[1], '%Y%m%d%H%M%S')
#                 else:
#                     date_str = datetime.now().strftime('%Y%m%d')
#                     start_time = f"{date_str}000000"
#                     stop_time = f"{date_str}235959"
#
#                 data_handle.get_interface().playCallback(htscsecurityID_and_types=htscsecurityID_and_types,
#                                                          exrightsType=1,
#                                                          startTime=start_time,
#                                                          stopTime=stop_time)
#             else:
#                 print('data_type dose not exist')
#     else:
#         print("htsc_code or data_type is null")
