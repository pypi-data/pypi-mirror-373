#!/usr/bin/python3
import json

from .interface.mdc_gateway_interface import GatewayInterface
from .interface.mdc_gateway_base_define import EMarketDataType, EPlaybackTaskStatus
from .interface.mdc_subscribe_handledata_class import *
from .interface.mdc_playback_handledata_class import *
from .interface.mdc_query_async_handle_data_class import query_response_handle


global interface
interface = GatewayInterface()


def get_interface():
    return interface


class OnRecvMarketData:
    def __init__(self, marketservice):
        self.marketservice = marketservice

    def OnMarketData(self, marketdatajson):
        # print(marketdatajson)
        try:
            # MD_TICK 快照
            if marketdatajson["marketDataType"] == EMarketDataType.MD_TICK:
                result = subscribe_tick_handle(marketdatajson)
                if result:
                    if result.get("htsc_code") in ['SCHKSBSH.HT', 'SCHKSBSZ.HT', 'SCSHNBHK.HT', 'SCSZNBHK.HT']:
                        self.marketservice.on_subscribe_derived(result)
                    else:
                        self.marketservice.on_subscribe_tick(result)

            # MD_KLINE:实时数据只提供15S和1MIN K线
            elif marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_15S or marketdatajson[
                "marketDataType"] == EMarketDataType.MD_KLINE_1MIN:
                result = subscribe_kline_handle(marketdatajson)
                if result:
                    self.marketservice.on_subscribe_kline(result)

            # MD_TRANSACTION: 逐笔成交 MD_ORDER:逐笔委托
            elif marketdatajson["marketDataType"] == EMarketDataType.MD_TRANSACTION or marketdatajson[
                "marketDataType"] == EMarketDataType.MD_ORDER:
                result = subscribe_trans_and_order_handle(marketdatajson)
                if result:
                    self.marketservice.on_subscribe_trans_and_order(result)

            # MD_SecurityLending
            elif marketdatajson["marketDataType"] == EMarketDataType.MD_SECURITY_LENDING or marketdatajson[
                "marketDataType"] == EMarketDataType.MD_SL_INDICATIVE_QUOTE_VALUE or marketdatajson[
                "marketDataType"] == EMarketDataType.MD_SL_STATISTICS_VALUE or marketdatajson[
                "marketDataType"] == EMarketDataType.MD_SL_ESTIMATION:
                result = subscribe_htsc_margin_handle(marketdatajson)
                if result:
                    self.marketservice.on_subscribe_htsc_margin(result)

            # AD_NEWS 实时资讯
            elif marketdatajson["marketDataType"] == EMarketDataType.AD_NEWS:
                result = subscribe_news_handle(marketdatajson)
                if result:
                    self.marketservice.on_subscribe_news(result)

        except BaseException as e:
            print("onMarketData error happened!" + marketdatajson)
            print(str(e))

    def OnPlaybackMarketData(self, marketdatajson):
        # print(marketdatajson)
        try:
            # .MD_TICK 快照
            if marketdatajson["marketDataType"] == EMarketDataType.MD_TICK:
                result = playback_tick_handle(marketdatajson)
                if result:
                    self.marketservice.on_playback_tick(result)

            # MD_TRANSACTION: 逐笔成交 MD_ORDER:逐笔委托
            elif marketdatajson["marketDataType"] == EMarketDataType.MD_TRANSACTION or marketdatajson[
                "marketDataType"] == EMarketDataType.MD_ORDER:
                result = playback_trans_and_order_handle(marketdatajson)
                if result:
                    self.marketservice.on_playback_trans_and_order(result)

        except BaseException as e:
            print("onMarketData error happened!" + marketdatajson)
            print(e)

    def OnPlaybackPayload(self, playloadstr):
        try:
            interface.set_service_value(4)
            # print(playloadstr)
            playloadjson = json.loads(playloadstr)
            # if "taskId" in playloadjson:
            #     print("Parse Message id:" + playloadjson["taskId"])
            marketDataStream = playloadjson["marketDataStream"]
            # if "isFinished" in marketDataStream:
            #     # print(marketDataStream)
            #     print("OnPlaybackPayload total number=%d, serial=%d, isfinish=%d" % (
            #         marketDataStream["totalNumber"], marketDataStream["serial"], marketDataStream["isFinished"]))
            # else:
            #     print("OnPlaybackPayload total number=%d, serial=%d" % (
            #         marketDataStream["totalNumber"], marketDataStream["serial"]))
            marketDataList = marketDataStream["marketDataList"]
            marketDatas = marketDataList["marketDatas"]
            for data in iter(marketDatas):
                self.OnPlaybackMarketData(data)
        except BaseException as e:
            print(e)

    def OnPlaybackStatus(self, statusstr):
        statusresult = "error happened in OnPlaybackStatus"
        try:
            statusjson = json.loads(statusstr)
            statusresult = f'OnPlaybackStatus playback status={statusjson["taskStatus"]}'
            interface.set_service_value(statusjson["taskStatus"])
            if statusjson["taskStatus"] == EPlaybackTaskStatus.CANCELED or statusjson[
                "taskStatus"] == EPlaybackTaskStatus.COMPLETED or statusjson["taskStatus"] \
                    == EPlaybackTaskStatus.FAILED:
                interface.mutex.acquire()
                if statusjson["taskId"] in interface.task_id_status:
                    del interface.task_id_status[statusjson["taskId"]]
                interface.mutex.release()
        except BaseException as e:
            print(e)
        self.marketservice.onPlaybackStatus(statusresult)

    def OnPlaybackResponse(self, responsestr):
        responseresult = "error happened in OnPlaybackResponse"
        try:
            responsejson = json.loads(responsestr)
            if "isSuccess" in responsejson:
                if responsejson["isSuccess"]:
                    responseresult = f'OnPlaybackResponse Message id: {responsejson["taskId"]}'
                else:
                    responseresult = f'OnPlaybackResponse failed --> {responsejson["errorContext"]["message"]}'
            else:
                responseresult = f'OnPlaybackResponse :{responsestr}'
        except BaseException as e:
            print(e)
        self.marketservice.onPlaybackResponse(responseresult)

    def OnPlaybackControlResponse(self, responsestr):
        responseresult = "error happened in OnPlaybackControlResponse"
        try:
            responsejson = json.loads(responsestr)
            if "isSuccess" in responsejson:
                if responsejson["isSuccess"]:
                    print(responsejson["currentReplayRate"])
                    responseresult = f'OnPlaybackControlResponse Message id:{responsejson["taskId"]}'
                else:
                    responseresult = f'OnPlaybackControlResponse failed!!! reason ->{responsejson["errorContext"]["message"]}'
            else:
                responseresult = f'OnPlaybackControlResponse :{responsestr}'
        except BaseException as e:
            print(e)
        self.marketservice.onPlaybackControlResponse(responseresult)

    def OnServiceMessage(self, marketDataStr):
        try:
            interface.set_service_value(1)
            marketDataJson = json.loads(marketDataStr)
            self.OnMarketData(marketDataJson)
        except BaseException as e:
            print("error happened in OnServiceMessage")
            print(e)

    def OnSubscribeResponse(self, responsestr):
        try:
            responsejson = json.loads(responsestr)
            issucess = responsejson["isSuccess"]
            if issucess:
                print("Subscribe Success!!!")
            else:
                # print(gateway.getErrorCodeValue(response.errorContext.errorCode))
                print("Subscribe failed!!! reason ->" + responsestr)
        except BaseException as e:
            print("error happened in OnServiceMessage")
            print(e)

    def OnFinInfoQueryResponse(self, responsestr):
        try:
            responsejson = json.loads(responsestr)
            print(responsejson)
            if "isSuccess" in responsejson:
                if responsejson["isSuccess"]:
                    print("OnFinInfoQueryResponse sucess")
                else:
                    print("OnFinInfoQueryResponse failed!!! reason -> %s" % (responsejson["errorContext"]["message"]))
                    interface.set_query_exit(True)
            else:
                print("OnFinInfoQueryResponse failed!!! reason -> %s" % (responsejson["errorContext"]["message"]))
                interface.set_query_exit(True)
        except BaseException as e:
            print("error happened in OnFinInfoQueryResponse")
            print(e)

    def OnQueryResponse(self, responsestr):

        try:
            responsejson = json.loads(responsestr)
            if "isSuccess" in responsejson:
                if responsejson["isSuccess"]:
                    marketDataStream = responsejson["marketDataStream"]
                    print(
                        "query response total number=%d, serial=%d" % (
                            marketDataStream["totalNumber"], marketDataStream["serial"]))
                    marketDataList = marketDataStream["marketDataList"]
                    marketDatas = marketDataList["marketDatas"]
                    result = query_response_handle(marketDatas)
                    self.marketservice.on_query_response(result)

                    if "isFinished" in marketDataStream:
                        interface.set_query_exit(marketDataStream["isFinished"] == 1)
                else:
                    print("OnQueryResponse failed!!! reason -> %s" % (responsejson["errorContext"]["message"]))
                    interface.set_query_exit(True)
            else:
                print("OnQueryResponse failed!!! reason -> %s" % (responsejson["errorContext"]["message"]))
                interface.set_query_exit(True)
        except BaseException as e:
            print("error happened in OnQueryResponse")
            print(e)

    def OnGeneralError(self, contextstr):
        try:
            contextjson = json.loads(contextstr)
            # print(gateway.getErrorCodeValue(context.errorCode))
            print("OnGeneralError!!! reason -> %s" % (contextjson["message"]))
        except BaseException as e:
            print("error happened in OnGeneralError")
            print(e)

    def OnLoginSuccess(self):
        interface.login_success = True
        print("OnLoginSuccess!!!")

    def OnLoginFailed(self, error_no, message):
        interface.login_success = False
        try:
            print("OnLoginFailed!!! reason -> %s" % message)
        except BaseException as e:
            print("error happened in OnLoginFailed")
            print(e)

    def OnNoConnections(self):
        print("OnNoConnections!!!")
        interface.set_reconnect(True)
        interface.set_no_connections(True)

    def OnReconnect(self):
        print("OnReconnect!!!")
        interface.set_reconnect(True)
        interface.set_reconnect_count(interface.get_reconnect_count() + 1)
