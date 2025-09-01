#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from ..data_handle import get_interface
from .. import data_handle
from ..interface.mdc_gateway_base_define import GateWayServerConfig, QueryServerConfig


# 登陆
# params1: 用户名
# params2: 密码
# params3:
# params2: 密码
def login(marketservice, Username, Password, login_log=False, IP=GateWayServerConfig.IP, Port=GateWayServerConfig.PORT,
          backupIP=GateWayServerConfig.BACK_LIST):
    # 登陆前 初始化
    result = ""
    if not ((type(Port) == int) and 0 < Port < GateWayServerConfig.MaxPortNum):
        result = "Port has invalid format"
        return result
    Initial(marketservice, login_log)

    abs_path = os.path.abspath(__file__)
    size = len(abs_path)
    abs_path = abs_path[0:size - 17]
    print(f'The current path:{abs_path}')
    ret = get_interface().login(IP, Port, Username, Password, GateWayServerConfig.ISTOKEN,
                                abs_path + GateWayServerConfig.CERTFOLDER, backupIP,
                                QueryServerConfig.QUERY_ADDRESS,
                                abs_path + QueryServerConfig.QUERY_CERT,
                                QueryServerConfig.QUERY_IS_SSL)

    if ret != 0:
        result = f'(login failed!!! reason:{get_interface().get_error_code_value(ret)})'
        return result
    result = "login success"
    return result


# UAT环境
def loginUAT(marketservice, Username, Password, login_log=False, IP=GateWayServerConfig.UAT_IP, Port=GateWayServerConfig.UAT_PORT,
             backupIP=GateWayServerConfig.UAT_BACK_LIST):
    # 登陆前 初始化
    result = ""
    if not ((type(Port) == int) and 0 < Port < GateWayServerConfig.MaxPortNum):
        result = "Port has invalid format"
        return result

    abs_path = os.path.abspath(__file__)
    size = len(abs_path)
    abs_path = abs_path[0:size - 17]

    print(f'The current path:{abs_path}')
    Initial(marketservice, login_log)
    ret = get_interface().login(IP, Port, Username, Password, GateWayServerConfig.ISTOKEN,
                                abs_path + GateWayServerConfig.CERTFOLDER, backupIP,
                                QueryServerConfig.UAT_QUERY_ADDRESS,
                                abs_path + QueryServerConfig.UAT_QUERY_CERT,
                                QueryServerConfig.UAT_QUERY_IS_SSL)

    if ret != 0:
        result = f'(login failed!!! reason:{get_interface().get_error_code_value(ret)})'
        return result
    result = "login success"
    return result


# SIT_Login是测试环境
def loginSIT(marketservice, Username, Password, login_log=False, IP=GateWayServerConfig.SIT_IP, Port=GateWayServerConfig.SIT_PORT,
             backupIP=GateWayServerConfig.SIT_BACK_LIST):
    # 登陆前 初始化
    result = ""
    if not ((type(Port) == int) and 0 < Port < GateWayServerConfig.MaxPortNum):
        result = "Port has invalid format"
        return result

    abs_path = os.path.abspath(__file__)
    size = len(abs_path)
    abs_path = abs_path[0:size - 17]
    Initial(marketservice, login_log)
    ret = get_interface().login(IP, Port, Username, Password, GateWayServerConfig.ISTOKEN,
                                abs_path + GateWayServerConfig.CERTFOLDER, backupIP,
                                QueryServerConfig.SIT_QUERY_ADDRESS,
                                abs_path + QueryServerConfig.SIT_QUERY_CERT,
                                QueryServerConfig.SIT_QUERY_IS_SSL)

    if ret != 0:
        result = f'(login failed!!! reason:{get_interface().get_error_code_value(ret)})'
        return result
    result = "login success"
    return result


# 获取当前版本号
def get_version():
    return get_interface().get_version()


# 释放资源
def release():
    fini()


# 配置
def config(open_trace=True, open_file_log=True, open_cout_log=True):
    if open_file_log:
        get_interface().python_open_file_log()
    else:
        get_interface().python_close_file_log()
    if open_cout_log:
        get_interface().python_open_cout_log()
    else:
        get_interface().python_close_cout_log()
    if open_trace:
        get_interface().python_open_trace()
    else:
        get_interface().python_close_trace()


# 登陆前 初始化 -- 修改ip映射,流量与日志开关设置,回调函数注册,接管系统日志,自我处理日志
def Initial(marketservice, login_flag):
    # 添加ip映射
    # get_interface().add_ip_map("168.63.17.150", "127.0.0.1")
    # 流量与日志开关设置
    # open_trace trace流量日志开关 # params:open_file_log 本地日志文件开关  # params:open_cout_log 控制台日志开关
    open_trace = login_flag
    open_file_log = login_flag
    open_cout_log = login_flag
    get_interface().init(open_trace, open_file_log, open_cout_log)

    # 注册回调和接管日志
    # 1.注册回调接口，不注册无法接收数据、处理数据，不会回调data_handle
    callback = data_handle.OnRecvMarketData(marketservice)
    get_interface().setCallBack(callback)

    # 2.接管日志
    # 若想关闭系统日志,自我处理日志,打开本方法
    # 打开本方法后,日志在insightlog.py的PyLog类的方法log(self,line)中也会体现,其中 line为日志内容）
    # use_init = True 系统日志以 get_interface().init 配置的方式记录
    # use_init = False 系统不再记录或打印任何日志,日志只有自行处理部分处理


# 释放资源
def fini():
    get_interface().fini()
