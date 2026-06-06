#! /usr/bin/env python3
#encoding: utf-8

#Filename: accountBasicSettings.py  
#Author: Steven Lian's team
#E-mail:  / /steven.lian@gmail.com  
#Date: 2020-03-25
#Description:   通用的配置管理,包括数据库地址,网络地址等

_VERSION="20260606"


import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
if sys.getdefaultencoding() != 'utf-8':
    pass
    #reload(sys)
    #sys.setdefaultencoding('utf-8')

from config import local_settings as local_settings

from common import redisHandle as redisHandle


#生产环境 rss | 测试环境 dss
_SYS = local_settings._SYS
#_SYS = "iotdemo"
#_SYS = "local"

_SYS_SERVER_NAME = local_settings._SYS_SERVER_NAME

#小程序/公众号浏览是否自动保存数据
_MiniProgramLoginSaveFlag = True


_HOME_DIR = {
    "local":r"/data/accountService",
    "iotDevice":r"../../", 
    "localHost":r"/data/accountService", 
    "iotdemo":r"/data/accountService", 
    "iotHome":r"/data/accountService", 
    }[_SYS]

_DEBUG = {
    "local":True,
    "iotDevice":True,
    "localHost":True,
    "iotdemo":True,
    "iotHome":True,
    }[_SYS]

#默认系统自动loginID
SYS_DEFAULT_AUTO_LOGINID ={
    "local":"10010001000", 
    "iotDevice":"10010001000", 
    "localHost":"10010001000", 
    "iotdemo":"10010001000", 
    "iotHome":"10010001000", 
}[_SYS]

#genDigistKey
GEN_DIGIST_KEY ={
    "local":"digistkey", 
    "iotDevice":"digistkey", 
    "iotdemo":"digistkey", 
    "localHost":"digistkey", 
    "iotHome":"digistkey", 
}[_SYS]

#SMS Service
SMS_SERVICE_VENDOR ={
    "local":"tencent", 
    "iotDevice":"aliyun", 
    "iotdemo":"tencent", 
    "localHost":"tencent", 
    "iotHome":"tencent", 
}[_SYS]

#file server url dataSet, 注意这个是一个字典
FILE_SERVER_URL ={
"local":"http://127.0.0.1/hfile",
"iotDevice":"http://127.0.0.1/hfile", 
"iotdemo":"http://127.0.0.1/hfile", 
"localHost":"http://127.0.0.1/hfile", 
"iotHome":"http://192.168.100.58/hfile", 
}

#internal account service url dataSet, 注意这个是一个字典
ACCOUNT_SERVICE_URL ={
"local":"http://127.0.0.1:8160/acis",
"iotDevice":"http://127.0.0.1:8160/acis", 
"iotdemo":"http://127.0.0.1:8160/acis", 
"localHost":"http://127.0.0.1:8160/acis", 
"iotHome":"http://192.168.100.58:8160/acis", 
}[_SYS]

#图片文件最大大小 (宽,高) (width, height)
MAX_PIC_SIZE = {
"local":(1920, 1920),
"iotDevice":(1920, 1920),
"iotdemo":(1920, 1920),
"localHost":(1920, 1920),
"iotHome":(1920, 1920),
}[_SYS]

#thumbnail 缩略图文件大小 (宽,高) (width, height)
THUMBNAIL_SIZE = {
"local":(720, 720),
"iotDevice":(720, 720),
"iotdemo":(720, 720),
"localHost":(720, 720),
"iotHome":(360, 360),
}[_SYS]

#role 角色权限
ROLE_RIGHT_SET ={
    "administrator":0, 
    "manager":10, 
    "operator":20, 
    "chief":30, 
    "customer":60, 
    "visitor":70, 
}

#默认的roleName
accountServiceDefaultRoleName = "visitor"
accountServiceMobilePhoneRoleName = "customer"

#不需要sessionID的命令入口清单
NO_SESSIONID_CMD_LIST = {
    "A0A0", "A4A0", "A6A0","A7A0","A8A0", "A9A0",
    "AIA0", 
    "AKA0", 
    "M2A0", 
    "W1A0", 
    "GAA0", "GUA0"
    }

#role 角色分配的功能清单
ROLE_CMD_LIST =\
{
"administrator":[
    "A0A0", "A1A0", "A2A0", "A3A0", "A4A0", "A5A0", "A6A0", "A7A0", 
    "A8A0", "A9A0", "AAA0", "ABA0", "ACA0", "ADA0", "AEA0", "AFA0", 
    "AGA0", "AHA0",
    "M1A0",
    "G0A0", "G1A0", "G2A0", "G3A0", "G4A0", "G9A0", "GAA0", "GUA0",
    "S0A0", "S1A0", 
    "W0A0", "W1A0",  
    ], 
"manager":
    [
    "A0A0", "A1A0", "A2A0", "A3A0", "A4A0", "A5A0", "A6A0", "A7A0", 
    "A8A0", "A9A0", "AAA0", "ABA0", "ACA0", "ADA0", "AEA0", "AFA0", 
    "AGA0", "AHA0",
    "M1A0",
    "G0A0", "G1A0", "G2A0", "G3A0", "G4A0", "G9A0", "GAA0", "GUA0",
    "S0A0", "S1A0", 
    "W0A0", "W1A0",  
    ], 
"operator":
    [
    "A0A0", "A1A0", "A2A0", "A3A0", "A4A0", "A5A0", "A6A0", "A7A0", 
    "A8A0", "A9A0", "AAA0", "ABA0", "ACA0", "ADA0", "AEA0", "AFA0", 
    "AGA0",
    "M1A0",
    "G0A0", "G1A0", "G2A0", "G3A0", "G4A0", "G9A0", "GAA0", "GUA0",
    "S0A0", "S1A0", 
    "W0A0", "W1A0",  
    ], 
"chief":
    [
    "A0A0", "A1A0", "A2A0", "A3A0", "A4A0", "A5A0", "A6A0", "A7A0",
    "A8A0", "A9A0", "AAA0", "ABA0", "ACA0", "ADA0", "AEA0", "AFA0",
    "G0A0", "G1A0", "G2A0", "G3A0", "G4A0", "G9A0", "GAA0", "GUA0",
    "S0A0", "S1A0", 
    "W0A0", "W1A0",  
    ], 
"customer":
    [
    "A0A0", "A1A0", "A2A0", "A3A0", "A4A0", "A5A0", "A6A0", "A7A0", 
    "A8A0", "A9A0", "AAA0", "ABA0", "ACA0", "ADA0", "AEA0", "AFA0", 
    "G0A0", "G1A0", "G2A0", "G3A0", "G4A0", "G9A0", "GAA0", "GUA0",
    "S0A0", "S1A0", 
    "W0A0", "W1A0",  
    ], 
"visitor":
    [
    "A0A0", "A2A0", "A3A0", "A4A0", "A5A0", "A6A0", "A7A0", "A8A0",
    "A9A0",  "AAA0", "ABA0", "AFA0",
    "G0A0", "G1A0", "G2A0", "G3A0", "G4A0", "G9A0", "GAA0", "GUA0",
    "S0A0", "S1A0", 
    "W0A0", "W1A0",  
    ], 
}

PASSWORD_RULE = {
    "minLength": 6,
    "maxLength": 20,
    "specialChar": True,
    "number": True,
    "letter": True,
    "upperCase": True,
    "lowerCase": True,
    "space": False,
    "chinese": False,
    "repeat": False,
    "sequence": False,
    "history": False,
    "historyCount": 3,
    "historyDays": 90,
}


if __name__ == "__main__":
    pass
    # import pdb
    # pdb.set_trace()
    print ("_SYS",_SYS)
    print ("_DEBUG",_DEBUG)

    print ("THUMBNAIL_SIZE", THUMBNAIL_SIZE)
    print ("ROLE_CMD_LIST", ROLE_CMD_LIST)
    print ("SYS_DEFAULT_AUTO_LOGINID", SYS_DEFAULT_AUTO_LOGINID)
