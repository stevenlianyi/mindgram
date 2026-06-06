#! /usr/bin/env python
#encoding: utf-8

#Filename: settings.py  
#Author: Steven Lian
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


#redis数据库信息  begin
_REDIS_DB_PORT_ORIGINAL = 6379
_REDIS_DB_PORT_DEFAULT = 16379
_REDIS_DB_NO_DEFAULT = 3

#主库，写记录
REDIS_WRITE_HOST = {
    #"local":"127.0.0.1",
    "local":"127.0.0.1",
    "iotDevice":"127.0.0.1", 
    "localHost":"127.0.0.1", 
    "iotdemo":"127.0.0.1", 
    "iotHome":"192.168.100.58", 
    }[_SYS]

REDIS_WRITE_PORT = {
    "local":_REDIS_DB_PORT_ORIGINAL,
    "iotDevice":_REDIS_DB_PORT_DEFAULT, 
    "localHost":_REDIS_DB_PORT_DEFAULT, 
    "iotdemo":_REDIS_DB_PORT_DEFAULT, 
    "iotHome":_REDIS_DB_PORT_DEFAULT, 
    }[_SYS]

REDIS_WRITE_DB = {
    "local":_REDIS_DB_NO_DEFAULT,
    "iotDevice":_REDIS_DB_NO_DEFAULT, 
    "localHost":_REDIS_DB_NO_DEFAULT, 
    "iotdemo":_REDIS_DB_NO_DEFAULT, 
    "iotHome":_REDIS_DB_NO_DEFAULT, 
   }[_SYS]

#从库，读记录
REDIS_READ_HOST = {
    #"local":"127.0.0.1",
    "local":"127.0.0.1",
    "iotDevice":"127.0.0.1", 
    "localHost":"127.0.0.1", 
    "iotdemo":"127.0.0.1", 
    "iotHome":"192.168.100.58", 
    }[_SYS]
    
REDIS_READ_PORT = {
    "local":_REDIS_DB_PORT_ORIGINAL,
    "iotDevice":_REDIS_DB_PORT_DEFAULT, 
    "localHost":_REDIS_DB_PORT_DEFAULT, 
    "iotdemo":_REDIS_DB_PORT_DEFAULT, 
    "iotHome":_REDIS_DB_PORT_DEFAULT, 
    }[_SYS]
    
REDIS_READ_DB = {
    "local":_REDIS_DB_NO_DEFAULT,
    "iotDevice":_REDIS_DB_NO_DEFAULT, 
    "localHost":_REDIS_DB_NO_DEFAULT, 
    "iotdemo":_REDIS_DB_NO_DEFAULT, 
    "iotHome":_REDIS_DB_NO_DEFAULT, 
    }[_SYS]
        
REDIS_PASSWD = {
    "local":"",
    "iotDevice":"", 
    "localHost":"", 
    "iotdemo":"", 
    "iotHome":"", 
    }[_SYS]


if REDIS_PASSWD == "":
    #主库，写记录
    dbMainW = redisHandle.getRedisDB(host=REDIS_WRITE_HOST,port=REDIS_WRITE_PORT,db=REDIS_WRITE_DB)
    #从库，读记录
    dbMainR = redisHandle.getRedisDB(host=REDIS_READ_HOST,port=REDIS_READ_PORT,db=REDIS_READ_DB)
else:
    #主库，写记录
    dbMainW = redisHandle.getRedisDB(host=REDIS_WRITE_HOST,port=REDIS_WRITE_PORT,db=REDIS_WRITE_DB, passwd=REDIS_PASSWD)
    #从库，读记录
    dbMainR = redisHandle.getRedisDB(host=REDIS_READ_HOST,port=REDIS_READ_PORT,db=REDIS_READ_DB, passwd=REDIS_PASSWD)
    
redisMainDB = redisHandle.RedisHandle(dbW=dbMainW,dbR=dbMainR)
pipeMainHandle = redisHandle.PipeHandle(redisMainDB)

#redis数据库信息  end



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
    "localHost":"digistkey", 
    "iotdemo":"digistkey", 
    "iotHome":"digistkey", 
}[_SYS]


#file server url dataSet, 注意这个是一个字典
FILE_SERVER_URL ={
"local":"http://127.0.0.1/hfile",
"iotDevice":"http://127.0.0.1/hfile", 
"localHost":"http://www.localHost.online/hfile", 
"iotdemo":"http://127.0.0.1/hfile", 
"iotHome":"http://192.168.100.58/hfile", 
}


#图片文件最大大小 (宽,高) (width, height)
MAX_PIC_SIZE = {
"local":(1920, 1920),
"iotDevice":(1920, 1920),
"localHost":(1920, 1920),
"iotdemo":(1920, 1920),
"iotHome":(1920, 1920),
}[_SYS]

#thumbnail 缩略图文件大小 (宽,高) (width, height)
THUMBNAIL_SIZE = {
"local":(720, 720),
"iotDevice":(720, 720),
"localHost":(720, 720),
"iotdemo":(720, 720),
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

#村庄单位级别
POLICE_CATEGORY_SET ={
    "stateLevel":0, 
    "provinceLevel":10, 
    "areaLevel":20, 
    "countryLevel":30, 
    "villageLevel":50, 
}


#不需要sessionID的命令入口清单
NO_SESSIONID_CMD_LIST = {"A0A0", "A4A0", "A6A0","A7A0","A8A0", "A9A0", "W1A0", "GAA0", "GUA0"}

#role 角色分配的功能清单
ROLE_CMD_LIST =\
{
"administrator":[
    "A0A0", "A1A0", "A2A0", "A3A0", "A4A0", "A5A0", "A6A0", "A7A0", "A8A0", "A9A0",  "AAA0", "ABA0", "ACA0", "ADA0", "AEA0", "AFA0",
    "G0A0", "G1A0", "G2A0", "G3A0", "G4A0", "G9A0", 
    "S0A0", "S1A0", 
    "W0A0", "W1A0",  
    ], 
"manager":
    [
    "A0A0", "A1A0", "A2A0", "A3A0", "A4A0", "A5A0", "A6A0", "A7A0", "A8A0", "A9A0",  "AAA0", "ABA0", "ACA0", "ADA0", "AEA0", "AFA0",
    "G0A0", "G1A0", "G2A0", "G3A0", "G4A0", "G9A0", 
    "S0A0", "S1A0", 
    "W0A0", "W1A0",  
    ], 
"operator":
    [
    "A0A0", "A1A0", "A2A0", "A3A0", "A4A0", "A5A0", "A6A0", "A7A0", "A8A0", "A9A0",  "AAA0", "ABA0", "ACA0", "ADA0", "AEA0", "AFA0",
    "G0A0", "G1A0", "G2A0", "G3A0", "G4A0", "G9A0", 
    "S0A0", "S1A0", 
    "W0A0", "W1A0",  
    ], 
"chief":
    [
    "A0A0", "A1A0", "A2A0", "A3A0", "A4A0", "A5A0", "A6A0", "A7A0", "A8A0", "A9A0",  "AAA0", "ABA0", "ACA0", "ADA0", "AEA0", "AFA0",
    "G0A0", "G1A0", "G2A0", "G3A0", "G4A0", "G9A0", 
    "S0A0", "S1A0", 
    "W0A0", "W1A0",  
    ], 
"customer":
    [
    "A0A0", "A1A0", "A2A0", "A3A0", "A4A0", "A5A0", "A6A0", "A7A0", "A8A0", "A9A0",  "AAA0", "ABA0", "ACA0", "ADA0", "AEA0", "AFA0", 
    "G0A0", "G1A0", "G2A0", "G3A0", "G4A0", "G9A0", 
    "S0A0", "S1A0", 
    "W0A0", "W1A0",  
    ], 
"visitor":
    [
    "A0A0", "A2A0", "A3A0", "A4A0", "A5A0", "A6A0", "A7A0", "A8A0", "A9A0",  "AAA0", "ABA0", "AFA0",
    "G0A0", "G1A0", "G2A0", "G3A0", "G4A0", "G9A0",  
    "S0A0", "S1A0", 
    "W0A0", "W1A0",  
    ], 
}



if __name__ == "__main__":
    pass
    # import pdb
    # pdb.set_trace()
    print ("_SYS",_SYS)
    print ("REDIS_WRITE_HOST",REDIS_WRITE_HOST)
    print ("REDIS_WRITE_PORT",REDIS_WRITE_PORT)
    print ("REDIS_WRITE_DB",REDIS_WRITE_DB)
    print ("REDIS_READ_HOST",REDIS_READ_HOST)
    print ("REDIS_READ_PORT",REDIS_READ_PORT)
    print ("REDIS_READ_DB",REDIS_READ_DB)
    print ("dbW",dbMainW)
    print ("dbR",dbMainR)
    print ("redisDB",redisMainDB)

    print ("THUMBNAIL_SIZE", THUMBNAIL_SIZE)
    print ("ROLE_CMD_LIST", ROLE_CMD_LIST)
    print ("SYS_DEFAULT_AUTO_LOGINID", SYS_DEFAULT_AUTO_LOGINID)
