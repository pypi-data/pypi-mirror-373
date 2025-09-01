#!/usr/bin/python3+

import sys
import json

from ..interface.mdc_gateway_base_define import ErrorInfo, SortType, Play_Back_Type, QueryType, QueryServerConfig, \
    GateWayServerConfig

from ..interface import mdc_recvdata_interface as recvdata

# from log_handle import PyLog
import time
from multiprocessing import Lock
from ..interface.mdc_gateway_head import mdc_gateway_client

sys.path.insert(1, "./interface")
sys.path.insert(2, "./libs")

global notifys  # ȫ�ֱ�������������ʱ��������Ҫȫ��ʹ��,ע����������
notifys = recvdata.PyNotify()
notifys.thisown = 0


class GatewayInterface:
    ineffective_size = 9999999999
    min_synchronous_data_len = 10
    ineffective_ret_size = 9999999998
    error_code_len = 8
    error_msg_data_len = 8
    ret_size = 4
    service_value = 0
    query_exit = False
    reconnect = False
    login_success = False
    no_connections = False
    reconnect_count = 0
    mutex = Lock()
    task_id_status = {}

    def __init__(self):
        self.service_value = 0
        self.query_exit = False
        self.reconnect = False
        self.login_success = False
        self.no_connections = False
        self.reconnect_count = 0
        self.open_file_log = False
        self.open_cout_log = False
        self.open_trace = True

    def get_service_value(self):
        return self.service_value

    def set_service_value(self, i):
        self.service_value = i

    def get_query_exit(self):
        return self.query_exit

    def set_query_exit(self, value):
        self.query_exit = value

    def get_reconnect(self):
        return self.reconnect

    def set_reconnect(self, value):
        self.reconnect = value

    def get_login_flag(self):
        return self.login_success

    def get_no_connections(self):
        return self.no_connections

    def set_no_connections(self, value):
        self.no_connections = value

    def get_reconnect_count(self):
        return self.reconnect_count

    def set_reconnect_count(self, value):
        self.reconnect_count = value

    def get_version(self):
        # ver = str(mdc_gateway_client.python_get_version())
        ver = 'insight_python_5.2.2_2025/09/01'
        return ver

    def get_error_code_value(self, code):
        value = ErrorInfo.get_error_code_value(code)
        return value

    def add_ip_map(self, original_ip, map_ip):
        mdc_gateway_client.python_add_ip_map(original_ip.encode(encoding="utf-8"), map_ip.encode(encoding="utf-8"))

    def delete_ip_map(self, original_ip):
        mdc_gateway_client.python_delete_ip_map(original_ip.encode(encoding="utf-8"))

    def add_ip_port(self, original_port, map_port):
        mdc_gateway_client.python_add_port_map(original_port, map_port)

    def delete_ip_map(self, original_port):
        mdc_gateway_client.python_delete_port_map(original_port)

    def is_trace(self):
        return mdc_gateway_client.python_is_trace()

    def is_compress(self):
        return mdc_gateway_client.python_is_compress()

    def is_responseCallback(self):
        return mdc_gateway_client.python_is_response_callback()

    def init(self, open_trace, open_file_log, open_cout_log):
        mdc_gateway_client.python_init_env()
        mdc_gateway_client.python_open_response_callback()
        self.open_trace = open_trace
        self.open_file_log = open_file_log
        self.open_cout_log = open_cout_log

    def python_open_file_log(self):
        self.open_file_log = True
        mdc_gateway_client.python_open_file_log()

    def python_close_file_log(self):
        self.open_file_log = False
        mdc_gateway_client.python_close_file_log()

    def python_open_cout_log(self):
        self.open_cout_log = True
        mdc_gateway_client.python_open_cout_log()

    def python_close_cout_log(self):
        self.open_cout_log = False
        mdc_gateway_client.python_close_cout_log()

    def python_open_trace(self):
        self.open_trace = True
        mdc_gateway_client.python_open_trace()

    def python_close_trace(self):
        self.open_trace = False
        mdc_gateway_client.python_close_trace()

    def __init_log__(self):
        print(f'open_file_log:{self.open_file_log} open_cout_log:{self.open_cout_log} open_trace:{self.open_trace}')
        if self.open_file_log:
            mdc_gateway_client.python_open_file_log()
        else:
            mdc_gateway_client.python_close_file_log()
        if self.open_cout_log:
            mdc_gateway_client.python_open_cout_log()
        else:
            mdc_gateway_client.python_close_cout_log()
        if self.open_trace:
            mdc_gateway_client.python_open_trace()
        else:
            mdc_gateway_client.python_close_trace()

    def open_compress(self, torf):
        if torf:
            mdc_gateway_client.python_open_compress()
        else:
            mdc_gateway_client.python_close_compress()

    def fini(self):
        mdc_gateway_client.python_logout()
        mdc_gateway_client.python_fini_env()

    # ����-ȫ���� param:marketDataTypeList Ϊ EMarketDataType ö��ֵ����
    def subscribebytype(self, datatype, marketdatatypes):

        if self.get_login_flag():
            GateWayServerConfig.IsRealTimeData = True
            subscribejson = {"DataType": datatype}
            subscribejson["MarketdataTypes"] = marketdatatypes
            subscribestr = json.dumps(subscribejson)
            # print(subscribestr)
            ret = mdc_gateway_client.python_subscribe(subscribestr, len(subscribestr))
            if ret < 0:
                print("subscribeAll failed!!! reason:%s" % (self.get_error_code_value(ret)))
                exit(-1)
        else:
            print("Unsuccessful login")

    def subscribebyid(self, datatype, htscSecurityids):

        if self.get_login_flag():
            GateWayServerConfig.IsRealTimeData = True
            subscribejson = {"DataType": datatype}
            subscribejson["HTSCSecurityIDs"] = htscSecurityids
            subscribestr = json.dumps(subscribejson)
            # print(subscribestr)
            ret = mdc_gateway_client.python_subscribe(subscribestr, len(subscribestr))
            if ret < 0:
                print("subscribeAll failed!!! reason:%s" % (self.get_error_code_value(ret)))
                exit(-1)
        else:
            print("Unsuccessful login")

    # �ط�  params:securityIdList Ϊ��� strֵ����;marketDataType Ϊ EMarketDataType ö��ֵ����;exrightsType ΪEPlaybackExrightsTypeö��ֵ,startTime str����;stopTime str����
    def playCallback(self, htscsecurityID_and_types, exrightsType, startTime, stopTime, isMdtime=True):
        if self.get_login_flag():
            for htscsecurityID_and_type in htscsecurityID_and_types:
                playbackjson = {}
                playbackjson["TaskID"] = mdc_gateway_client.python_get_task_id()
                self.mutex.acquire()
                self.task_id_status[playbackjson["TaskID"]] = 0
                self.mutex.release()

                htscSecurityIDs = []

                htscSecurityID = {}
                htscSecurityID["HTSCSecurityID"] = htscsecurityID_and_type["HTSCSecurityID"]
                htscSecurityID["EMarketDataType"] = htscsecurityID_and_type["EMarketDataType"]
                htscSecurityIDs.append(htscSecurityID)

                playbackjson["HTSCSecurityIDs"] = htscSecurityIDs
                playbackjson["ExrightsType"] = exrightsType
                playbackjson["StartTime"] = startTime
                playbackjson["EndTime"] = stopTime

                if isMdtime:
                    playbackjson["Sort"] = SortType.Sort_MDTime
                else:
                    playbackjson["Sort"] = SortType.Sort_RecivedTime

                playbackjson["DataType"] = Play_Back_Type.Play_Back

                playback_info = json.dumps(playbackjson)
                while self.task_id_status.__len__() >= 5:
                    time.sleep(1)

                ret = mdc_gateway_client.python_request_playback(playback_info, len(playback_info))
                if ret < 0:
                    print(self.get_error_code_value(ret))
                    print("playCallback failed!!!")
                    exit(-1)
                time.sleep(1)

            while self.task_id_status.__len__() > 0:
                time.sleep(1)
        else:
            print("Unsuccessful login")

    # �ط�  params:securityIdList Ϊ��� strֵ����;marketDataType Ϊ EMarketDataType ö��ֵ����;exrightsType ΪEPlaybackExrightsTypeö��ֵ,startTime str����;stopTime str����
    def playSortCallback(self, marketDataTypes, startTime, stopTime, exrightsType, sort):
        if self.get_login_flag():
            for marketDataType in marketDataTypes:
                playbackjson = {}
                playbackjson["TaskID"] = mdc_gateway_client.python_get_task_id()
                self.mutex.acquire()
                self.task_id_status[playbackjson["TaskID"]] = 0
                self.mutex.release()

                htscSecurityIDs = []

                htscSecurityID = {}
                htscSecurityID["HTSCSecurityID"] = marketDataType["HTSCSecurityID"]
                htscSecurityID["EMarketDataType"] = marketDataType["EMarketDataType"]
                htscSecurityIDs.append(htscSecurityID)

                playbackjson["HTSCSecurityIDs"] = htscSecurityIDs
                playbackjson["ExrightsType"] = exrightsType
                playbackjson["StartTime"] = startTime
                playbackjson["EndTime"] = stopTime

                playbackjson["Sort"] = sort
                playbackjson["DataType"] = Play_Back_Type.Play_Back

                playback_info = json.dumps(playbackjson)
                while self.task_id_status.__len__() >= 5:
                    time.sleep(1)

                ret = mdc_gateway_client.python_request_playback(playback_info, len(playback_info))
                if ret < 0:
                    print(self.get_error_code_value(ret))
                    print("playCallback failed!!!")
                    exit(-1)
                self.set_service_value(0)
            while 1:
                value = self.get_service_value()
                if value == 16 or value == 17 or value == 18:
                    break
                else:
                    time.sleep(1)
        else:
            print("Unsuccessful login")

    def queryfininfo(self, querytype, params, synchronousflag=False, securityIDSourceAndTypes=[], securityIdList=[]):

        if synchronousflag:  # ͬ��
            self.queryfininfosynchronous(querytype, params, securityIDSourceAndTypes, securityIdList)
        else:  # �첽
            self.queryfininfoasynchronous(querytype, params, securityIDSourceAndTypes, securityIdList)

    def queryfininfosynchronous(self, querytype, params, securityIDSourceAndTypes=[], securityIdList=[]):
        if self.get_login_flag():
            request = {"DataType": querytype}
            request["Params"] = params
            securitySourceTypes = []
            securityIds = []

            for securityIDSourceAndType in iter(securityIDSourceAndTypes):
                securitySourceTypes.append(securityIDSourceAndType)
            if len(securitySourceTypes) > 0:
                request["MarketdataTypes"] = securitySourceTypes
            for id in securityIdList:
                securityIds.append(id)
            if len(securityIds) > 0:
                request["HTSCSecurityIDs"] = securityIds
            # print(request)
            request_info = json.dumps(request)

            rettempdata = mdc_gateway_client.python_request_fin_info_query_sync(request_info, len(request_info))
            retdatalenstr = mdc_gateway_client.cdata(rettempdata, self.min_synchronous_data_len)
            try:
                retdatalen = int(retdatalenstr)
            except:
                print("invalid data")
                return None

            if retdatalen == self.ineffective_size:
                print("invalid request")
                return None

            elif retdatalen == self.ineffective_ret_size:

                retdatastr = mdc_gateway_client.cdata(rettempdata,
                                                      self.min_synchronous_data_len + self.error_code_len + self.error_msg_data_len)
                # errorcode = retdatastr[self.min_synchronous_data_len:self.min_synchronous_data_len + self.error_code_len]
                errormsglenstr = retdatastr[
                                 self.min_synchronous_data_len + self.error_code_len:self.min_synchronous_data_len + self.error_code_len + self.error_msg_data_len]

                try:
                    errormsglen = int(errormsglenstr)
                except:
                    errormsglen = 0

                if errormsglen > 0:
                    errortoatlsize = self.min_synchronous_data_len + self.error_code_len + self.error_msg_data_len + errormsglen
                    errormsgstr = mdc_gateway_client.cdata(rettempdata, errortoatlsize)
                    errormsg = errormsgstr[
                               self.min_synchronous_data_len + self.error_code_len + self.error_msg_data_len:errortoatlsize]
                    # print("queryfininfo failed!!! reason:%s" % (self.get_error_code_value(errorcode)))
                    if querytype in [1002070003, 1002020001, 1002040002, 1002040003, 1002040001, 1002030001, 1002040004,
                                     1101080001, 1109090009, 1003020003, 1002090002, 1110010002]:
                        # if querytype in [1002070003, 1002020001, 1002040002, 1002040003, 1002040001, 1002030001, 1002040004, 1101080001, 1109090009, 1003010011]:
                        # if errormsg == 'No KLine Found' or errormsg == 'No Data found' or errormsg == 'No data found':
                        return None
                    print("queryfininfo failed!!! reason:%s" % (errormsg))
                    return None
                else:
                    print("invalid error msg")
                    return None

            else:
                if self.min_synchronous_data_len < retdatalen < QueryServerConfig.MAX_QUERY_SIZE:

                    retdatastr = mdc_gateway_client.cdata(rettempdata, retdatalen)
                    retlenstr = retdatastr[self.min_synchronous_data_len:self.ret_size]
                    if len(retlenstr) > 0:
                        ret = int(retlenstr)
                        print(ret)
                        if ret < 0:
                            print("queryfininfo failed!!! reason:%s" % (self.get_error_code_value(ret)))
                    result = json.loads(retdatastr[self.min_synchronous_data_len:retdatalen])
                    return result
                else:
                    print("invalid data")
                    return None
        else:
            print("Unsuccessful login")

    def queryfininfoasynchronous(self, querytype, params, securityIDSourceAndTypes=[], securityIdList=[]):

        request = {"DataType": querytype}
        request["Params"] = params
        securitySourceTypes = []
        securityIds = []

        for securityIDSourceAndType in iter(securityIDSourceAndTypes):
            securitySourceTypes.append(securityIDSourceAndType)
        if len(securitySourceTypes) > 0:
            request["MarketdataTypes"] = securitySourceTypes
        for id in securityIdList:
            securityIds.append(id)
        if len(securityIds) > 0:
            request["HTSCSecurityIDs"] = securityIds
        # print(request)
        request_info = json.dumps(request)

        ret = mdc_gateway_client.python_request_fin_info_query_async(request_info, len(request_info))
        if ret < 0:
            print("queryfininfo failed!!! reason:%s" % (self.get_error_code_value(ret)))
            exit(-1)

    def queryMdContantCallback(self, securityIDSourceAndTypes, securityIdList, synchronousflag=False):
        self.queryCallback(QueryType.QUERY_CONSTANT, securityIDSourceAndTypes, securityIdList, synchronousflag)

    def queryLastMdContantCallback(self, securityIDSourceAndTypes, securityIdList, synchronousflag=False):
        self.queryCallback(QueryType.QUERY_CONSTANT_TODAY, securityIDSourceAndTypes, securityIdList, synchronousflag)

    def queryETFInfoCallback(self, securityIDSourceAndTypes, securityIdList, synchronousflag=False):
        self.queryCallback(QueryType.QUERY_ETFBASICINFO, securityIDSourceAndTypes, securityIdList, synchronousflag)

    def queryLastMdTickCallback(self, securityIDSourceAndTypes, securityIdList, synchronousflag=False):
        self.queryCallback(QueryType.QUERY_TICK, securityIDSourceAndTypes, securityIdList, synchronousflag)

    # ��ѯ  params:queryType Ϊintֵ;securityIdSource Ϊ�г�ESecurityIDSource ö��ֵ;securityType Ϊ ESecurityIDSourceö��ֵ����
    def queryCallback(self, queryType, securityIDSourceAndTypes, securityIdList, synchronousflag=False):
        if self.get_login_flag():
            request = {"DataType": queryType}
            securitySourceTypes = []
            securityIds = []

            for securityIDSourceAndType in iter(securityIDSourceAndTypes):
                securitySourceTypes.append(securityIDSourceAndType)
            request["MarketdataTypes"] = securitySourceTypes
            for id in securityIdList:
                securityIds.append(id)
            request["HTSCSecurityIDs"] = securityIds
            # print(request)
            request_info = json.dumps(request)
            ret = mdc_gateway_client.python_request_mdquery(request_info, len(request_info))
            if ret < 0:
                print("queryCallback failed!!! reason:%s" % (self.get_error_code_value(ret)))
                exit(-1)
            self.set_query_exit(False)
            while True:
                exit = self.get_query_exit()
                if exit:
                    break
                else:
                    time.sleep(1)
        else:
            print("Unsuccessful login")

    def login(self, ip, port, username, pwd, istoken, certlog, backuplist,
              queryaddress=QueryServerConfig.QUERY_ADDRESS,
              querycert=QueryServerConfig.QUERY_CERT,
              isSSL=QueryServerConfig.QUERY_IS_SSL,
              thread_count=1):
        self.__init_log__()
        # ������ڵĻص�ע�ᣬ�������ڣ��򲻻�����ص�
        mdc_gateway_client.Notify_Regist(notifys)
        loginjson = {}
        loginjson["UserName"] = username
        loginjson["Password"] = pwd
        loginjson["IsToken"] = istoken
        loginjson["MainServerIP"] = ip
        loginjson["MainServerPort"] = port
        loginjson["BackServer"] = backuplist
        loginjson["QueryAddress"] = queryaddress
        loginjson["QueryCert"] = querycert
        loginjson["QuerySSL"] = isSSL
        loginjson["QueryMaxQuerySize"] = QueryServerConfig.MAX_QUERY_SIZE
        loginjson["Thread_Count"] = GateWayServerConfig.THREAD_COUNT
        loginjson["CertPath"] = certlog

        loginstr = json.dumps(loginjson)

        ret = mdc_gateway_client.python_login(loginstr, len(loginstr))
        return ret

    def setCallBack(self, callback):
        recvdata.PyNotify_Regist(callback)

    # def own_deal_log(self,use_init,open_trace = True):
    #     if not use_init:
    #         self.open_trace = open_trace
    #         self.open_file_log = False
    #         self.open_cout_log = False
    #     log = PyLog()
    #     recvdata.PyLog_Regist(log)


class Element:
    def __init__(self, source, type, list):
        self.source = source
        self.type = type
        self.list = list


class SecurityIDSourceAndType:
    def __init__(self, source, type):
        self.source = source
        self.type = type


class SubscribeByIdElement:
    def __init__(self, id, typeList):
        self.id = id
        self.securityIDSourceAndTypeList = typeList


class QueryElement:
    def __init__(self, idList, type):
        self.idList = idList
        self.securityIDSourceAndType = type


class BackupList:
    def __init__(self):
        self.list = mdc_gateway_client.StrIntMap()

    def Add(self, key, value):
        self.list[key.encode(encoding="utf-8")] = value


class StrList:
    def __init__(self):
        self.list = mdc_gateway_client.StrList()

    def Add(self, value):
        self.list.push_back(value.encode(encoding="utf-8"))
