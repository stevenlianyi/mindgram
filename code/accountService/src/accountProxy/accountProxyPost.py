#!/usr/bin/env python3
#encoding: utf-8

#Filename: accountAppPost.py 
#Author: Steven Lian
#E-mail:  steven.lian@gmail.com  
#Date: 2022-03-05
#Description:   内部account服务器代理服务


_VERSION="20210305"


import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
if sys.getdefaultencoding() != 'utf-8':
    pass
    #reload(sys)
    #sys.setdefaultencoding('utf-8')

import platform
        
#import json
#import chardet
import traceback

#import uuid
#import random
#import copy
import requests
#import hashlib


#global defintion/common var etc.
from common import accountDefinition as comGD

#common functions(log,time,string, json etc)
from common import miscCommon as misc

#common functions(funct operation)
from common import accountFuncCommon as comFC

#common functions(database operation)

#setting files
from config import accountBasicSettings as settings


HOME_DIR = settings._HOME_DIR
    

if __name__ != "__main__":
    _LOG = "" #上级已经有_LOG设置的情况
    
else:
    if "_LOG" not in dir() or not _LOG:
        logDir = os.path.join(HOME_DIR, "log")
        _LOG = misc.setLogNew("PROXY", "accoutproxylog", logDir)

    systemVersion = str(sys.version_info.major) + "." + str(sys.version_info.minor ) + "." + str(sys.version_info.micro )
    _LOG.info("python version:[%s], main code version:[%s]" %(systemVersion, _VERSION))
    
_DEBUG = settings._DEBUG

_SYS_SERVER_NAME = settings._SYS_SERVER_NAME

gSN = 0

CMDList = settings.ROLE_CMD_LIST["administrator"]


#function part

# command part begin
# including common func and interface(A0A0~,G0A0~,S0A0~,W0A0~)

    
#程序入口, post 调用
def post(theLog, dataSet, IP, environSet, appType):
    result = {}
    global gSN
    global _LOG
    global _VERSION
    
    _LOG = theLog
    
    CMD = "A0A0"
    errCode = "OK"
    rtnField = ""
    
    try:
        gSN += 1
        localSN = gSN

        if _DEBUG:
            _LOG.info("R:{0},{1},{2}".format(_VERSION, IP, misc.jsonDumps(dataSet)))
            
        if True:

            if comGD._DEF_ACCOUNT_CMD_NAME in dataSet:
                localSN = dataSet.get("SN", str(gSN))
                CMD = dataSet[comGD._DEF_ACCOUNT_CMD_NAME]
                if CMD in CMDList:
                    #proxy
                    headers = {'content-type': 'application/json'}

                    url = settings.ACCOUNT_SERVICE_URL
                    payload = misc.jsonDumps(dataSet)
                    r = requests.post(url, data = payload, headers = headers)

                    if r.status_code == 200:
                        rtnData = misc.jsonLoads(r.text)
                            
                else:
                    rtnData = comFC.rtnMSG("ERROR", "ERR_NOCMD", "")
            else:
                rtnData = comFC.rtnMSG("ERROR", "ERR_NOCMD", "")
                
        else:
            rtnData = comFC.rtnMSG("ERROR", "ERR_IPFLOOD", "")

        result = rtnData

        if _DEBUG:
            _LOG.info("S:{},{}".format(_VERSION, misc.jsonDumps(result)))
            
    except Exception as e:
        data = IP+': post() unknow failure'
        f = sys._getframe().f_back
        errMsg = 'R: %s, S: %s'%(msg, data)
        _LOG.error( '%s, %s, %s, %s, %s, %s, %s' %(errMsg, traceback.format_exc(), f.f_code.co_filename, f.f_code.co_name, str(f.f_lineno), str(e), str(type(e))))
        _LOG.error( '%s, %s' %(errMsg, traceback.format_exc()))
        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
#        result = misc.jsonDumps(rtnSet)
        result = rtnSet
   
    return result


if __name__ == "__main__":
    IP = "0.0.0.0"
    appType = "chief"
    appType = ""
    envSet = {"CONTENT_LENGTH":100}
    if len(sys.argv) > 1:
        pass
        if platform.system()=='Linux':
            import pdb
            pdb.set_trace()
            msg = sys.argv[1]
            dataSet = misc.jsonLoads(msg)
            post(_LOG, dataSet, IP, envSet, appType)
            exit(-1)
        
    msg ='{"CMD":"A6A0","sessionID":"testonly","loginID":"13910710766"}'
    
    dataSet = misc.jsonLoads(msg)
    
    print(dataSet)
    
    rtnSet = post(_LOG, dataSet, IP, envSet, appType)
    
    print (rtnSet)
