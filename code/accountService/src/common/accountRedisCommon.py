#! /usr/bin/env python
#encoding: utf-8


#Filename: redisCommon.py  
#Author: Steven Lian
#E-mail:  steven.lian@gmail.com  
#Date: 2019-08-03
#Description:   redis 处理代码

_VERSION="20260602"

import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

import time
import hashlib
import copy

#global defintion/common var etc.
from common import accountDefinition as comGD

#code/decode functions
#from common import codingDecoding as comCD

#common functions(log,time,string, json etc)
from common import miscCommon as misc

#setting files
from config import accountRedisSettings as settings

if "redisMainDB" not in dir() or not redisMainDB:
    dbMainW = settings.dbMainW
    dbMainR = settings.dbMainR
    redisMainDB = settings.redisMainDB
    redisPipe = settings.pipeMainHandle


#generate the redis db key
def genDBKey(level1, level2, level3 = "", level4 = "",  level5 = ""):
    result = ""
    if level3 == "":
        result = "%s.%s" % (str(level1), str(level2))
    elif level4 == "":
        result = "%s.%s.%s" % (str(level1), str(level2), str(level3))
    elif level5 == "":
        result="%s.%s.%s.%s" % (str(level1), str(level2), str(level3), str(level4))
    else:
        result="%s.%s.%s.%s.%s" % (str(level1), str(level2), str(level3), str(level4), str(level5))
    return result


def scanKeys(dbKey):
    result = []
    cursor = 0
    cursor,  result = redisMainDB.scan(cursor, dbKey)
    while cursor > 0:
        cursor,  keysList = redisMainDB.scan(cursor, dbKey)
        aList = []
        for key in keysList:
            if isinstance(key, bytes):
                key = key.decode()
            aList.append(key)
        result += aList
            
    return result 


#系统初始配置信息 begin
def getSysConfig():
    dbKey=genDBKey(comGD._DEF_REDIS_SYS_LEVEL1, comGD._DEF_REDIS_SYS_CONFIG)
    result = redisMainDB.hgetall(dbKey)
    if result == None:
        result = {}
    return result
    
    
def chkSysConfigExist():
    dbKey=genDBKey(comGD._DEF_REDIS_SYS_LEVEL1, comGD._DEF_REDIS_SYS_CONFIG)
    rtn = redisMainDB.exists(dbKey)
    if rtn == 0:
        result = False
    else:
        result = True
    return result


def setSysConfig(mapping):
    dbKey=genDBKey(comGD._DEF_REDIS_SYS_LEVEL1, comGD._DEF_REDIS_SYS_CONFIG)
    mapping["modifyYMDHMS"] = misc.getTime()
    result = redisMainDB.hmset(dbKey,mapping)
    return result

#系统初始配置信息 end

#设置/时间戳 begin
def getTimeStamp(key = "default"):
    dbKey=genDBKey(comGD._DEF_REDIS_SYS_LEVEL1, comGD._DEF_REDIS_SYS_TIMESTAMP, key)
    result = redisMainDB.get(dbKey)
    if result == None:
        result = ""
    return result
    
    
def setTimeStamp(key = "default", val = ""):
    dbKey=genDBKey(comGD._DEF_REDIS_SYS_LEVEL1, comGD._DEF_REDIS_SYS_TIMESTAMP, key)
    if val == "":
        val = misc.getTime()
    timeStamp = val
    result = redisMainDB.set(dbKey,timeStamp)
    return result

#设置/时间戳 end
    
#系统消息计数 begin
def resetMsgSeqNum():
    dbKey = genDBKey(comGD._DEF_REDIS_SYS_LEVEL1, comGD._DEF_REDIS_SYS_MSG_SEQ_NUM)
    result = redisMainDB.set(dbKey, 0)
    return result


def getMsgSeqNum():
    dbKey = genDBKey(comGD._DEF_REDIS_SYS_LEVEL1, comGD._DEF_REDIS_SYS_MSG_SEQ_NUM)
    result = redisMainDB.get(dbKey)
    return result


def incrMsgSeqNum():
    dbKey = genDBKey(comGD._DEF_REDIS_SYS_LEVEL1, comGD._DEF_REDIS_SYS_MSG_SEQ_NUM)
    result = redisMainDB.incr(dbKey)
    return result


def resetSysHumanTime():
    dbKey = genDBKey(comGD._DEF_REDIS_SYS_LEVEL1, comGD._DEF_REDIS_SYS_KICKOFF_HUMANTIME)
    timeString = misc.getTime()
    result = redisMainDB.set(dbKey, timeString)
    return result


def resetSysMicroSecond():
    dbKey = genDBKey(comGD._DEF_REDIS_SYS_LEVEL1, comGD._DEF_REDIS_SYS_KICKOFF_TIMESTAMP)
    result = int (time.time()*1000)
    redisMainDB.set(dbKey, result)
    return result


def getSysMicroSecond():
    dbKey = genDBKey(comGD._DEF_REDIS_SYS_LEVEL1, comGD._DEF_REDIS_SYS_KICKOFF_TIMESTAMP)
    try:
        sysMicroseconds = redisMainDB.get(dbKey)
        if sysMicroseconds == None:
            sysMicroseconds = resetSysMicroSecond()
        sysMicroseconds = int(sysMicroseconds)
    except:
        sysMicroseconds = resetSysMicroSecond()
    result = int (time.time()*1000) - sysMicroseconds
    return result    

#系统消息计数 end

    
#IP flood  begin
def chkIPCount(IP):
    result = True
#    dbKey = genDBKey(comGD._DEF_REDIS_DATA_LEVEL1, comGD._DEF_REDIS_DATA_IP_TIME, IP)
#    saveTime = redisMainDB.get(dbKey)
#    if saveTime:
#        saveTime = int(saveTime)
#    else:
#        saveTime = 0
#    currTime = int(time.time())
#    if currTime - saveTime > comGD._DEF_REDIS_DATA_IP_TIME_THRESOLD:
#        dbKey = genDBKey(comGD._DEF_REDIS_DATA_LEVEL1, comGD._DEF_REDIS_DATA_IP_TIME, IP)
#        redisMainDB.set(dbKey, str(currTime))
#        dbKey = genDBKey(comGD._DEF_REDIS_DATA_LEVEL1, comGD._DEF_REDIS_DATA_IP_COUNT, IP)
#        redisMainDB.set(dbKey,"0")
#    else:
#        dbKey = genDBKey(comGD._DEF_REDIS_DATA_LEVEL1, comGD._DEF_REDIS_DATA_IP_COUNT, IP)
#        visits = redisMainDB.incr(dbKey)
#        if visits > comGD._DEF_REDIS_DATA_IP_VISITS:
#            result = False
    return result

#IP flood end


#buffer相关 begin
def chkBufferExist(indexKey):
    result = False
    dbKey=genDBKey(comGD._DEF_REDIS_BUFFER_LEVEL1, comGD._DEF_BUFFER_DATA_NAME, indexKey)
    rtn = redisMainDB.exists(dbKey)
    if rtn == 0:
        result = False
    else:
        result = True
    return result
    
    
def putAllDataBuffer(indexKey, dataList, expireTime = comGD._DEF_BUFFER_DATA_KEEP_TIME):
    result = 0
    dbKey=genDBKey(comGD._DEF_REDIS_BUFFER_LEVEL1, comGD._DEF_BUFFER_DATA_NAME, indexKey)
    rtn = dbMainW.delete(dbKey)
    for data in dataList:
        redisMainDB.rpush(dbKey, misc.jsonDumps(data)) #必须用rpush
        result += 1
    redisMainDB.expire(dbKey, expireTime)
    return result        


def putDataBuffer(indexKey, data, expireTime = comGD._DEF_BUFFER_DATA_KEEP_TIME):
    result = 0
    dbKey=genDBKey(comGD._DEF_REDIS_BUFFER_LEVEL1, comGD._DEF_BUFFER_DATA_NAME, indexKey)
    result = redisMainDB.rpush(dbKey, misc.jsonDumps(data)) #必须用rpush
    redisMainDB.expire(dbKey, expireTime)
    return result        


def getAllDataBuffer(indexKey,  beginNum=0, endNum = -1):
    result = getDataBuffer(indexKey)
    return result
    
    
def getDataBuffer(indexKey,  beginNum=0, endNum = -1):
    result = []
    dbKey=genDBKey(comGD._DEF_REDIS_BUFFER_LEVEL1, comGD._DEF_BUFFER_DATA_NAME, indexKey)
    try:
        dataList =  redisMainDB.lrange(dbKey, beginNum, endNum)
        for data in dataList:
            result.append(misc.jsonLoads(data))
    except:
        pass
    return result  
    
    
def putStepBuffer(indexKey, beginNum=0, endNum = -1, expireTime = comGD._DEF_BUFFER_DATA_KEEP_TIME):
    result = 0
    dbKey=genDBKey(comGD._DEF_REDIS_BUFFER_LEVEL1, comGD._DEF_BUFFER_STEP_NAME, indexKey)
    data = {}
    data["beginNum"] = beginNum
    data["endNum"] = endNum
    data["step"] = endNum - beginNum
    result = redisMainDB.set(dbKey, misc.jsonDumps(data))
    redisMainDB.expire(dbKey, expireTime)
    return result        
    
    
def getStepBuffer(indexKey):
    result = {}
    dbKey=genDBKey(comGD._DEF_REDIS_BUFFER_LEVEL1, comGD._DEF_BUFFER_STEP_NAME, indexKey)
    data = redisMainDB.get(dbKey)
    if data != "" and data:
        result = misc.jsonLoads(data)
    else:
        result = {}
    return result        
    
#buffer相关 end


#user info begin
def getUserIDList(userIDPrefix):
    result = []
    key = userIDPrefix + "*"
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_USER_BASIC, key)
    keyPrefix = genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_USER_BASIC)
    keyPrefixLen = len(keyPrefix) + 1
    keyFullList = scanKeys(dbKey)
    for fullKey in keyFullList:
        userID = fullKey[keyPrefixLen:]
        if isinstance(userID,bytes):
            userID = userID.decode()
        result.append(userID)
    return result


def getUserAllInfo(userID,delFlag=True):
    result = {}
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_USER_BASIC, userID)
    if delFlag:
        val = redisMainDB.hget(dbKey,comGD._DEF_REDIS_USER_DB_DELETE_FLAG);
        if isinstance(val,bytes):
           val = val.decode()
        if val == comGD._DEF_REDIS_USER_DB_DELETE_TRUE:
           return result
    dataSet = redisMainDB.hgetall(dbKey)
    for k, v in dataSet.items():
        if isinstance(k, bytes):
            k = k.decode("UTF-8")
        if isinstance(v, bytes):
            v = v.decode("UTF-8")
        if k in ["regPosition", "ruleInfo", "chiefVillageIDList"]:
            if v != "" and v:
                try:
                    v = misc.jsonLoads(v)
                except:
                    pass
        if k in ["roleName"]:
            if v == "" or v == None:
                v = "visitor" #默认是visitor
        result[k] = v
    return result


def scanUserAllInfo(fromPos = 0, key = "*"):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_USER_BASIC, level3=key)
    nextPos,  keysList = redisMainDB.scan(fromPos, dbKey)
    return nextPos, keysList


def getAllUserIDList(maxNum = 2000, key = "*",delFlag=True):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_USER_BASIC, level3=key)
    cursor = 0
    count = 0
    cursor,  allKeysList = redisMainDB.scan(cursor, dbKey)
    count = len(allKeysList)
    if count < maxNum:
        while cursor > 0:
            cursor,  keysList = redisMainDB.scan(cursor, dbKey)
            count += len(keysList)
            allKeysList += keysList
            if count >= maxNum:
                break
    result = []
    nLen = len(comGD._DEF_REDIS_USER_LEVEL1 + comGD._DEF_REDIS_USER_DB_USER_BASIC) + 2
    for data in allKeysList:
        userID = data[nLen:]
        if isinstance(userID, bytes):
            userID = userID.decode()
        result.append(userID)
    return result
        

def getUserInfo(userID, itemsList,delFlag=True):
    result = {}
    dbKey = genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_USER_BASIC, userID)
    if delFlag:
        val = redisMainDB.hget(dbKey,comGD._DEF_REDIS_USER_DB_DELETE_FLAG);
        if isinstance(val,bytes):
           val = val.decode()
        if val == comGD._DEF_REDIS_USER_DB_DELETE_TRUE:
           return result
    aList = redisMainDB.hmget(dbKey, itemsList)
    count = 0
    for data in aList:
        if data == None:
            data = ""
        if isinstance(data, bytes):
            data = data.decode("UTF-8")
        if itemsList[count] in ["regPosition", "ruleInfo", "chiefVillageIDList"]:
            if data !="" and data:
                try:
                    data = misc.jsonLoads(data)
                except:
                    pass
        result[itemsList[count]] = data
        count += 1
    return result


def getUserRule(userID):
    result = {}
    dataSet = getUserInfo(userID, ["ruleInfo"])
    data = dataSet.get("ruleInfo", "")
    if isinstance(data,dict) == False:
        try:
            result = misc.jsonLoads(data)
        except:
            pass
    else:
        result = data
    return result


def getUserRoleName(userID):
    dataSet = getUserInfo(userID, ["roleName"])
    result = dataSet.get("roleName") #默认是visitor
    if result == "" or result == None:
        result = "visitor"
    return result    

    
def chkUserExist(userID,delFlag=True):
    result = False
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_USER_BASIC, userID)
    rtn = redisMainDB.exists(dbKey)
    if rtn == 0:
        result = False
    else:
        result = True
        if delFlag:
            aSet = getUserInfo(userID, [comGD._DEF_REDIS_USER_DB_DELETE_FLAG])
            try:
                if (aSet.get(comGD._DEF_REDIS_USER_DB_DELETE_FLAG)) == comGD._DEF_REDIS_USER_DB_DELETE_TRUE:
                    result = False
            except:
                pass
    return result


def setUserInfo(userID, mapping):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_USER_BASIC, userID)
    mapping[comGD._DEF_REDIS_USER_DB_DELETE_FLAG] = comGD._DEF_REDIS_USER_DB_DELETE_FALSE
    mapping[comGD._DEF_REDIS_USER_DB_UPDATE_DATE] = misc.getTime()
    if "regPosition" in mapping:
        mapping["regPosition"] = misc.jsonDumps(mapping["regPosition"])
    if "ruleInfo" in mapping:
        mapping["ruleInfo"] = misc.jsonDumps(mapping["ruleInfo"])
    if "chiefVillageIDList" in mapping:
        mapping["chiefVillageIDList"] = misc.jsonDumps(mapping["chiefVillageIDList"])
    result = redisMainDB.hmset(dbKey,mapping)
    return result


def delUserInfo(userID, openID = "", action = False):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_USER_BASIC, userID)
    if redisMainDB.exists(dbKey) == 1:
        mapping = {}
        mapping[comGD._DEF_REDIS_USER_DB_DELETE_FLAG] = comGD._DEF_REDIS_USER_DB_DELETE_TRUE
        mapping[comGD._DEF_REDIS_USER_DB_DELETE_DATE] = misc.getTime()
        if openID != "":
            mapping["delOpenID"] = openID
        result = redisMainDB.hmset(dbKey,mapping) #不要真的删除数据, 只标志删除
    if action:
        result = redisMainDB.delete(dbKey)
    return result
    
    
#session list
def genUserSession(mapping, expireTime = comGD._DEF_USER_SESSION_EXPIRE_TIME):
    userID = mapping.get("loginID", "")
    # key = (userID.encode("UTF-8") + misc.getTime().encode("UTF-8") + comGD._DEF_COMM_HASH_KEY_FOR_ALL.encode("UTF-8"))
    key =  f"{userID}{misc.getTime()}{comGD._DEF_COMM_HASH_KEY_FOR_ALL}".encode("UTF-8")
    # sessionID = hashlib.md5(key).hexdigest()
    # sessionID = hashlib.sha224(key.encode()).hexdigest()
    # sessionID = hashlib.blake2b(key).hexdigest()
    sessionID = hashlib.blake2s(key).hexdigest()
    setSessionInfo(sessionID, mapping,expireTime)
    result = sessionID
    return result


def saveUserSession(userID, sessionID, expireTime = comGD._DEF_USER_SESSION_EXPIRE_TIME):
    saveSet = {}
    saveSet["loginID"] = userID
    setSessionInfo(sessionID, saveSet)
    result = sessionID
    return result
    
    
def setSessionInfo(sessionID, mapping, expireTime = comGD._DEF_USER_SESSION_EXPIRE_TIME):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_SESSIONID_LIST, sessionID)
    result = redisMainDB.hmset(dbKey,mapping)
    redisMainDB.expire(dbKey, expireTime)
    return result
    
    
def getSessionInfo(sessionID, itemsList =[]):
    result = {}
    dbKey = genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_SESSIONID_LIST, sessionID)
    if itemsList == []:
        dataSet = redisMainDB.hgetall(dbKey)
        if dataSet != None:
            for k, v in dataSet.items():
                if isinstance(k, bytes):
                    k = k.decode("UTF-8")
                if isinstance(v, bytes):
                    v = v.decode("UTF-8")
                result[k] = v
    else:
        aList = redisMainDB.hmget(dbKey, itemsList)
        count = 0    
        for data in aList:
            if data == None:
                data = ""
            if isinstance(data, bytes):
                data = data.decode("UTF-8")
            result[itemsList[count]] = data
            count += 1
    return result

    
def chkUserSession(sessionID):
    dataSet = getSessionInfo(sessionID, ["loginID"])
    result = dataSet.get("loginID")
    return result
    
    
def extUserSession(sessionID, expireTime = comGD._DEF_USER_SESSION_EXPIRE_TIME):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_SESSIONID_LIST, sessionID)
    result = redisMainDB.expire(dbKey, expireTime)
    return result


def delUserSession(sessionID):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_SESSIONID_LIST, sessionID)
    result = redisMainDB.delete(dbKey)
    return result    
    
    
#增加用户的访问的openID list 
def addUserOpenIDList(userID, openID):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_WECHAT_OPENID, userID)
    if isinstance(openID, bytes):
        openID = openID.decode("UTF-8")
    result = redisMainDB.sadd(dbKey, openID)
    return result


def scanUserOpenIDList(fromPos = 0, key = "*"):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_WECHAT_OPENID, level3=key)
    nextPos,  keysList = redisMainDB.scan(fromPos, dbKey)
    return nextPos, keysList


def setUserOpenIDList(userID, openIDList):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_WECHAT_OPENID, userID)
    delUserOpenIDList(userID)
    for openID in openIDList:
        if isinstance(openID, bytes):
            openID = openID.decode("UTF-8")
        result = redisMainDB.sadd(dbKey, openID)
    return result


def getUserOpenIDList(userID):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_WECHAT_OPENID, userID)
    aList = redisMainDB.smembers(dbKey)
    result = []
    for a in aList:
        if isinstance(a, bytes):
            a = a.decode("UTF-8")
        result.append(a)
    return result
    
    
def getUserOpenIDListNum(userID):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_WECHAT_OPENID, userID)
    result = redisMainDB.scard(dbKey)
    return result


def removeUserOpenIDList(userID, openID):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_WECHAT_OPENID, userID)
    if isinstance(openID, bytes):
        openID = openID.decode("UTF-8")
    result = redisMainDB.srem(dbKey, openID)
    return result


def chkUserOpenIDList(userID, openID):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_WECHAT_OPENID, userID)
    if isinstance(openID, bytes):
        openID = openID.decode("UTF-8")
    if redisMainDB.sismember(dbKey, openID) == 1:
        result = True
    else:
        result = False
    return result


def delUserOpenIDList(userID):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_WECHAT_OPENID, userID)
    result = redisMainDB.delete(dbKey)
    return result


#微信小程序openid 对应的 loginID
def getLoginIDByOpenID(openID):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_OPENID_LOGINID, openID)
    data = redisMainDB.get(dbKey)
    if data != None:
        if isinstance(data, bytes):
            data = data.decode("UTF-8")
    else:
        data = ""
    result = data
    return result


def addLoginIDByOpenID(loginID, openID):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_OPENID_LOGINID, openID)
    if isinstance(loginID, bytes):
        loginID = loginID.decode("UTF-8")
    result = redisMainDB.set(dbKey, loginID)
    return result
    
    
def delLoginIDByOpenID(openID):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_OPENID_LOGINID, openID)
    result = redisMainDB.delete(dbKey)
    return result

    
#微信小程序code保存
def setMiniProgramCode(code,  dataSet, expireTime = comGD._DEF_REDIS_USER_WECHAT_CODE_KEEP_TIME):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_WECHAT_CODE, code)
    data = misc.jsonDumps(dataSet)
#    if isinstance(data, bytes):
#        data = data.decode("UTF-8")
    result = redisMainDB.set(dbKey, data)
    redisMainDB.expire(dbKey, expireTime)
    return result


def getMiniProgramCode(code):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_WECHAT_CODE, code)
    dataStr = redisMainDB.get(dbKey)
    try:
        result = misc.jsonLoads(dataStr)
    except:
        result = {}
    return result


def existMiniProgramCode(code):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_REDIS_USER_DB_WECHAT_CODE, code)
    if redisMainDB.exists(dbKey) == 1:
        result = True
    else:
        result = False
    return result

    
#验证码code保存
def setVerifyCode(userID, code,  expireTime = comGD._DEF_DATA_SMS_CODE_KEEP_TIME):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_DATA_SMS_NAME, userID)
    result = redisMainDB.set(dbKey, code)
    redisMainDB.expire(dbKey, expireTime)
    return result


def getVerifyCode(userID):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_DATA_SMS_NAME, userID)
    data = redisMainDB.get(dbKey)
    if data == None:
        result = ""
    else:
        if isinstance(data, bytes):
            data = data.decode()
        result = data
        #删除对应的验证码
        redisMainDB.delete(dbKey)
    return result


def delVerifyCode(userID):
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_DATA_SMS_NAME, userID)
    #删除对应的验证码
    return redisMainDB.delete(dbKey)


def smsVerifyCodeLimit(userID,expireTime = comGD._DEF_DATA_SMS_CODE_KEEP_TIME):
    result = True
    dbKey=genDBKey(comGD._DEF_REDIS_USER_LEVEL1, comGD._DEF_SMS_COUNT_DATA, userID)
    if redisMainDB.exists(dbKey):
        rtn = redisMainDB.incr(dbKey)
    else:
        rtn = redisMainDB.incr(dbKey)
        redisMainDB.expire(dbKey, expireTime)
    if rtn > comGD._DEF_SMS_SEND_LIMIT_PER_MIN:
        result = False
    return result


#当日用户注册计数
def resetUserRegCount():
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_TOTAL, comGD._DEF_ACCOUNT_STAT_REGISTATION)
    result = redisMainDB.delete(dbKey)
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_ID, comGD._DEF_ACCOUNT_STAT_REGISTATION)
    result = redisMainDB.delete(dbKey)
    return result


def getUserRegCount():
    result = {}
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_TOTAL, comGD._DEF_ACCOUNT_STAT_REGISTATION)
    v  = redisMainDB.get(dbKey)
    if v:
        if isinstance(v, bytes):
            v = v.decode("UTF-8")
    else:
        v = "0"
    result[comGD._DEF_ACCOUNT_STAT_LEVEL2_TOTAL] = v
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_ID, comGD._DEF_ACCOUNT_STAT_REGISTATION)
    dataSet = redisMainDB.hgetall(dbKey)
    aSet = {}
    if dataSet:
        for k, v in dataSet.items():
            if isinstance(k, bytes):
                k = k.decode("UTF-8")
            if isinstance(v, bytes):
                v = v.decode("UTF-8")
            aSet[k] = v
    result[comGD._DEF_ACCOUNT_STAT_LEVEL2_ID] = aSet
    return result


def incrUserRegCount(userID):
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_TOTAL, comGD._DEF_ACCOUNT_STAT_REGISTATION)
    result = redisMainDB.incr(dbKey)
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_ID, comGD._DEF_ACCOUNT_STAT_REGISTATION)
    result = redisMainDB.hincrby(dbKey, userID, 1)
    return result


#当日用户登录计数
def resetUserLoginCount():
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_TOTAL, comGD._DEF_ACCOUNT_STAT_LOGIN)
    result = redisMainDB.delete(dbKey, 0)
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_ID, comGD._DEF_ACCOUNT_STAT_LOGIN)
    result = redisMainDB.delete(dbKey)
    return result


def getUserLoginCount():
    result = {}
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_TOTAL, comGD._DEF_ACCOUNT_STAT_LOGIN)
    v  = redisMainDB.get(dbKey)
    if v:
        if isinstance(v, bytes):
            v = v.decode("UTF-8")
    else:
        v = "0"
    result[comGD._DEF_ACCOUNT_STAT_LEVEL2_TOTAL] = v
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_ID, comGD._DEF_ACCOUNT_STAT_LOGIN)
    dataSet = redisMainDB.hgetall(dbKey)
    aSet = {}
    if dataSet:
        for k, v in dataSet.items():
            if isinstance(k, bytes):
                k = k.decode("UTF-8")
            if isinstance(v, bytes):
                v = v.decode("UTF-8")
            aSet[k] = v
    result[comGD._DEF_ACCOUNT_STAT_LEVEL2_ID] = aSet
    return result


def incrUserLoginCount(userID):
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_TOTAL, comGD._DEF_ACCOUNT_STAT_LOGIN)
    result = redisMainDB.incr(dbKey)
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_ID, comGD._DEF_ACCOUNT_STAT_LOGIN)
    result = redisMainDB.hincrby(dbKey, userID, 1)
    return result


#当日用户活动计数
def resetUserActiveCount():
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_TOTAL, comGD._DEF_ACCOUNT_STAT_ACTIVE)
    result = redisMainDB.delete(dbKey)
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_ID, comGD._DEF_ACCOUNT_STAT_ACTIVE)
    result = redisMainDB.delete(dbKey)
    return result


def getUserActiveCount(): 
    result = {}
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_TOTAL, comGD._DEF_ACCOUNT_STAT_ACTIVE)
    v  = redisMainDB.get(dbKey)
    if v:
        if isinstance(v, bytes):
            v = v.decode("UTF-8")
    else:
        v = "0"
    result[comGD._DEF_ACCOUNT_STAT_LEVEL2_TOTAL] = v
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_ID, comGD._DEF_ACCOUNT_STAT_ACTIVE)
    dataSet = redisMainDB.hgetall(dbKey)
    aSet = {}
    if dataSet:
        for k, v in dataSet.items():
            if isinstance(k, bytes):
                k = k.decode("UTF-8")
            if isinstance(v, bytes):
                v = v.decode("UTF-8")
            aSet[k] = v
    result[comGD._DEF_ACCOUNT_STAT_LEVEL2_ID] = aSet
    return result


def incrUserActiveCount(userID):
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_TOTAL, comGD._DEF_ACCOUNT_STAT_ACTIVE)
    result = redisMainDB.incr(dbKey)
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_LEVEL2_ID, comGD._DEF_ACCOUNT_STAT_ACTIVE)
    result = redisMainDB.hincrby(dbKey, userID, 1)
    return result


#主要的历史数据
def saveKeyStatData(YMD, dataSet, dataType = comGD._DEF_DEFAULT_STAT_HISTORY_NAME):
    dbKey = genDBKey(comGD._DEF_REDIS_FORM_LEVEL1, comGD._DEF_REDIS_DATA_TYPE_STAT, dataType)
    data = misc.jsonDumps(dataSet)
    result = redisMainDB.hset(dbKey, YMD, data)
    return result


def getKeyStatAllData(dataType = comGD._DEF_DEFAULT_STAT_HISTORY_NAME):
    result = {}
    dbKey = genDBKey(comGD._DEF_REDIS_FORM_LEVEL1, comGD._DEF_REDIS_DATA_TYPE_STAT, dataType)
    dataSet = redisMainDB.hgetall(dbKey)
    if dataSet != None:
        for k, v in dataSet.items():
            if isinstance(k, bytes):
                k = k.decode("UTF-8")
            if isinstance(v, bytes):
                v = v.decode("UTF-8")
            result[k] = v
    return result


def getKeyStatData(YMD, dataType = comGD._DEF_DEFAULT_STAT_HISTORY_NAME):
    dbKey = genDBKey(comGD._DEF_REDIS_FORM_LEVEL1, comGD._DEF_REDIS_DATA_TYPE_STAT, dataType)
    data = redisMainDB.hget(dbKey, YMD)
    if data :
        result = misc.jsonLoads(data)
    else:
        result = {}
    return result


def delKeyStatData(YMD = "", dataType = comGD._DEF_DEFAULT_STAT_HISTORY_NAME):
    dbKey = genDBKey(comGD._DEF_REDIS_FORM_LEVEL1, comGD._DEF_REDIS_DATA_TYPE_STAT, dataType)
    if YMD != "":
        result = redisMainDB.hdel(dbKey, YMD)
    else:
        result = redisMainDB.delete(dbKey)        
    return result


#file information handler
#给客户端提供的在线存储, G1A0,G2A0, userID = loginID or openID
def getAllSavedData(userID):
    dbKey=genDBKey(comGD._DEF_REDIS_DATA_LEVEL1, comGD._DEF_REDIS_USER_DATA_SAVE_NAME, userID)
    result = {}
    dataSet = redisMainDB.hgetall(dbKey)
    if dataSet != None:
        for k, v in dataSet.items():
            if isinstance(k, bytes):
                k = k.decode("UTF-8")
            if isinstance(v, bytes):
                v = v.decode("UTF-8")
            result[k] = v
    return result


def getSavedData(userID, key):
    result = ""
    dbKey=genDBKey(comGD._DEF_REDIS_DATA_LEVEL1, comGD._DEF_REDIS_USER_DATA_SAVE_NAME, userID)
    data = redisMainDB.hget(dbKey, key)
    if data != None:
        if isinstance(data, bytes):
            data = data.decode("UTF-8")
        result = data
    return result
    
    
def chkSavedDataExist(userID, key):
    result = False
    dbKey=genDBKey(comGD._DEF_REDIS_DATA_LEVEL1, comGD._DEF_REDIS_USER_DATA_SAVE_NAME, userID)
    rtn = redisMainDB.hexists(dbKey, key)
    if rtn == 0:
        result = False
    else:
        result = True
    return result


def setSavedData(userID, key,  val):
    dbKey=genDBKey(comGD._DEF_REDIS_DATA_LEVEL1, comGD._DEF_REDIS_USER_DATA_SAVE_NAME, userID)
    result = redisMainDB.hset(dbKey,key, val)
    return result


def delSavedData(userID, key):
    dbKey=genDBKey(comGD._DEF_REDIS_DATA_LEVEL1, comGD._DEF_REDIS_USER_DATA_SAVE_NAME, userID)
    result = redisMainDB.hdel(dbKey, key)
    return result


#把数据转到相应的列表
def putMsg2Queue(key,  data,  limit = 0):
    dbKey = genDBKey(comGD._DEF_REDIS_DATA_LEVEL1, comGD._DEF_REDIS_DATA_TYPE_QUEUE, level3=key)
    result = redisMainDB.lpush(dbKey, misc.jsonDumps(data))
    if limit > 0:
        redisMainDB.ltrim(dbKey, 0, limit)
    return result


def getMsg2Queue(key):
    dbKey = genDBKey(comGD._DEF_REDIS_DATA_LEVEL1, comGD._DEF_REDIS_DATA_TYPE_QUEUE, level3=key)
    try:
        #result = misc.jsonLoads(redisMainDB.brpop(dbKey, 10)[1].decode("UTF-8"))
        result = misc.jsonLoads(redisMainDB.brpop(dbKey, 10)[1])
    except:
        result = {}
    return result


def getMsgList2Queue(key,  beginNum,  endNum):
    result = []
    dbKey = genDBKey(comGD._DEF_REDIS_DATA_LEVEL1, comGD._DEF_REDIS_DATA_TYPE_QUEUE, level3=key)
    try:
        dataList =  redisMainDB.lrange(dbKey, beginNum, endNum)
        for data in dataList:
            result.append(misc.jsonLoads(data))
    except:
        pass
    return result


def cleanMsg2Queue(key = "*"):
    dbKey = genDBKey(comGD._DEF_REDIS_DATA_LEVEL1, comGD._DEF_REDIS_DATA_TYPE_QUEUE, level3=key)
    result = 0
    cursor = 0
    cursor,  keysList = redisMainDB.scan(cursor, dbKey)
    result += len(keysList)
    for keys in keysList:
        redisMainDB.delete(keys)
    while cursor > 0:
        cursor,  keysList = redisMainDB.scan(cursor, dbKey)
        result += len(keysList)
        for keys in keysList:
            redisMainDB.delete(keys)
    return result


def trans2MysqlList(dataType, dataSet):
    transSet = {}
    transSet["dataType"]  = dataType
    transSet["payload"] = dataSet
    putMsg2Queue(comGD._DEF_ACCOUNT_MQSQL_LIST, transSet)


def getMysqlList():
    transSet = getMsg2Queue(comGD._DEF_ACCOUNT_MQSQL_LIST)
    result = transSet
    return result
    
    
def trans2FileList(dataType, dataSet):
    transSet = {}
    transSet["dataType"]  = dataType
    transSet["payload"] = dataSet
    putMsg2Queue(comGD._DEF_ACCOUNT_FILE_LIST, transSet)


def getFileList():
    transSet = getMsg2Queue(comGD._DEF_ACCOUNT_FILE_LIST)
    result = transSet
    return result
    

def statSaveDataGeneral(dataType,  dataSet):
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1,comGD._DEF_ACCOUNT_STAT_BEFORE_NAME,  dataType)
    data = misc.jsonDumps(dataSet)
    redisMainDB.set(dbKey, data)
    return True


def statGetDataGeneral(dataType):
    result = {}
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1,comGD._DEF_ACCOUNT_STAT_BEFORE_NAME,  dataType)
    data = redisMainDB.get(dbKey)
    if data:
        result = misc.jsonLoads(data)
    return result


#把数据存到列表
def statSaveListGeneral(dataType,  data,  limit = 0):
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_BEFORE_NAME, level3=dataType)
    result = redisMainDB.lpush(dbKey, misc.jsonDumps(data))
    if limit > 0:
        redisMainDB.ltrim(dbKey, 0, limit)
    return result


def statGetListGeneral(dataType,  beginNum,  endNum):
    result = []
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_BEFORE_NAME, level3=dataType)
    try:
        dataList =  redisMainDB.lrange(dbKey, beginNum, endNum)
        for data in dataList:
            result.append(misc.jsonLoads(data))
    except:
        pass
    return result
    

def statDelListGeneral(dataType):
    result = 0
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_BEFORE_NAME, level3=dataType)
    try:
        result =  redisMainDB.delete(dbKey)
    except:
        pass
    return result
    
    
#把数据存到hash
def statSaveHashGeneral(key,  filed,  data):
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_BEFORE_NAME, level3=key)
    result = redisMainDB.hset(dbKey, filed,  misc.jsonDumps(data))
    return result
    
    
def statGetHashGeneral(key,  filed):
    result = None
    dbKey = genDBKey(comGD._DEF_REDIS_STAT_LEVEL1, comGD._DEF_ACCOUNT_STAT_BEFORE_NAME, level3=key)
    try:
        data =  redisMainDB.hget(dbKey, filed)
        result = misc.jsonLoads(data)
    except:
        pass
    return result
    
#channel operation part begin
def publish2Channel(channelType, CMD , dataSet):
    dbKey=genDBKey(comGD._DEF_REDIS_CHANNEL_LEVEL1,channelType, CMD)
    try:
        msg = misc.jsonDumps(dataSet)
    except:
        msg = str(dataSet)
        
    result = redisMainDB.publish(dbKey, msg)
    
    return result

#channel operation part end


#mini program begin

def setMiniProgramToken(token,expireTime=7200):
    dbKey=genDBKey(comGD._DEF_REDIS_SYS_LEVEL1, comGD._DEF_REDIS_SYS_MINI_ACCESS_TOKEN)
    result = redisMainDB.set(dbKey, token)
    redisMainDB.expire(dbKey, expireTime)
    return result


def getMiniProgramToken():
    dbKey=genDBKey(comGD._DEF_REDIS_SYS_LEVEL1, comGD._DEF_REDIS_SYS_MINI_ACCESS_TOKEN)
    data = redisMainDB.get(dbKey)
    if data == None:
        result = ""
    else:
        if isinstance(data, bytes):
            data = data.decode()
        result = data
    return result

#mini program end

if __name__ == "__main__":
    # import pdb
    # pdb.set_trace()
    print ("_SYS",settings._SYS)
