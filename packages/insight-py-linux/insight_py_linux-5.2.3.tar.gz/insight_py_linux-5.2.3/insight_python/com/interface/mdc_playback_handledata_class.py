import traceback
from datetime import datetime
from .mdc_query_sync_mapping_table import MappingTable
from .mdc_enumerated_mapping_table import EnumeratedMapping


def playback_tick_handle(marketdatajson):

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


def playback_trans_and_order_handle(marketdatajson):

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
                              'order_price': '', 'order_qty': '', 'order_bs_flag': '', 'order_no': '',
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

