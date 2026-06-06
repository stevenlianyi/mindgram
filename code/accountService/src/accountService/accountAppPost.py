#!/usr/bin/env python3
#encoding: utf-8

#Filename: accountAppPost.py 
#Author: Steven Lian
#E-mail:  steven.lian@gmail.com  
#Date: 2021-01-29
#Description:   内部account服务器App接口


_VERSION="20260602"


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

import uuid
import random
import copy
import base64
#import requests
#import hashlib


#global defintion/common var etc.
from common import accountDefinition as comGD

#common functions(log,time,string, json etc)
from common import miscCommon as misc

#common functions(database operation)
from common import accountRedisCommon as comDB

from common import accountMysqlCommon as comMysql

#common functions(funct operation)
from common import accountFuncCommon as comFC

#weChat minProgram interface API
from common import miniProgramCommon as comMini

# from common import aliyunSMS as SMS #modify here
# from common import tencentSMS as SMS #modify here

#setting files
from config import accountBasicSettings as settings

if settings.SMS_SERVICE_VENDOR == "aliyun":
    from common import aliyunSMS as SMS
elif settings.SMS_SERVICE_VENDOR == "yihaifenghua":
    from common import yihaifenghuaSMS as SMS
elif settings.SMS_SERVICE_VENDOR == "caict":
    from common import caictSMS as SMS
else:
    from common import tencentSMS as SMS

_processorPID = os.getpid()

HOME_DIR = settings._HOME_DIR

#临时缓存机制对内部服务没有意义, 默认关闭
bufferEnableFlag = False


if __name__ != "__main__":
    _LOG = "" #上级已经有_LOG设置的情况
    
else:
    if "_LOG" not in dir() or not _LOG:
        logDir = os.path.join(HOME_DIR, "log")
        _LOG = misc.setLogNew(comGD._DEF_ACCOUNT_LOG_TITLE, comGD._DEF_ACCOUNT_LOG_NAME, logDir)

    systemVersion = str(sys.version_info.major) + "." + str(sys.version_info.minor ) + "." + str(sys.version_info.micro )
    _LOG.info("python version:[%s], main code version:[%s]" %(systemVersion, _VERSION))
    
_DEBUG = settings._DEBUG

_SYS_SERVER_NAME = settings._SYS_SERVER_NAME

gSN = 0


#function part

# command part begin
# including common func and interface(A0A0~,G0A0~,S0A0~,W0A0~)

  
#openID bundle funcs,
def bundleOpenIDWithLoginID(loginID, openID):
    result = 0
    comDB.addUserOpenIDList(loginID, openID)
    comDB.addLoginIDByOpenID(loginID, openID)
    result = comDB.getUserOpenIDListNum(loginID)
    return result


#openID debundle funcs,
def debundleOpenIDWithLoginID(loginID, openID):
    result = 0    
    comDB.removeUserOpenIDList(loginID, openID)
    comDB.delLoginIDByOpenID(openID)
    result = comDB.getUserOpenIDListNum(loginID)
    return result


#buffer相关, 考虑到部分查询数据较多, 因此查询结果先缓存到redis,然后根据用户要求取出,
def putQueryResult(CMD, loginID, dataList):
    while True:
        indexKey = comFC.genDigest(CMD, loginID, misc.getTime(), str(random.randint(100000, 999999)))
        if comDB.chkBufferExist(indexKey) == False:
            break
    rtn =  comDB.putAllDataBuffer(indexKey, dataList)
    result = indexKey
    return result


def getQueryResult(indexKey, beginNum = 0,  endNum = -1):
    dataExist = comDB.chkBufferExist(indexKey)
    dataList = comDB.getDataBuffer(indexKey,  beginNum,  endNum)
    return dataExist, dataList


#用户数据的keyword检查, protect
def isUserProtectKey(aKey):
    result = True
    try:
        if isinstance(aKey, bytes):
            aKey = aKey.encode()
        aKey = aKey.lower()
        if aKey not in comGD._DEF_REDIS_USER_PROTECT_KEYS_LIST:
            result = False
    except:
        pass
    return result
    
    
#verify passwd
def verifyPasswd(loginID, passwd):
    result = False
    itemsList = ["loginID","passwd"]
    loadSet = comDB.getUserInfo(loginID, itemsList,delFlag=False)
    loadLoginID = loadSet.get("loginID", "")
    loadPasswd = loadSet.get("passwd", "")
    if loadPasswd != "":
        if loadLoginID == loginID and misc.checkPasswd(passwd, loadPasswd):
            result = True
    return result


#获取用户的主号
def getMasterLoginID(loginID):
    result = loginID
    itemsList = ["masterID"]
    loadSet = comDB.getUserInfo(loginID, itemsList,delFlag=False)
    masterID = loadSet.get("masterID", "")
    if masterID != "":
        result = masterID
    return result    


#access and fee verify 
def verifyAccessFee(loginID):
    result = "B0" #借用errcode 定义
    verifyAccessFlag = True
    
    if verifyAccessFlag == False:
        result = "BG"

    verifyFeeFlag = True
    if verifyFeeFlag == False:
        result = "BH"
        
    return result 
    
    
def isHasRight(roleName, dataType):
    result = True
    return result


#获取小程序access token
def getMiniProgramAccessToken():
    result = ""
    #首先尝试redis数据库
    accessToken = comDB.getMiniProgramToken()
    if not accessToken:
        accessTokenData = comMini.getAccessToken()
        if accessTokenData:
            accessToken = accessTokenData["accessToken"]
            comDB.setMiniProgramToken(accessToken,accessTokenData["expireInSeconds"])
    result = accessToken
    return result


#获取小程序openID
def getMiniProgramOpenID(code):
    result = ""


#accountService不负责转移数据, 只保留photoID
def getTempLocation(id):
    return id


#application functions

#cmdA0A0 funcs begin
def funcGetWebOpenID(webCode):
    result = {}
    #微信扫码登录
    if comDB.existWechatWebCode(webCode):
        #已经通过 code 获取了 openID
        wechatDataSet = comDB.getWechatWebCode(webCode)    
    else:
        openID = ""
        unionID = ""
        accessToken = ""
        if comDB.existWechatRefreshCode(webCode):
            refreshCode = comDB.getWechatRefreshCode(webCode)
            #调用refresh接口获取openID
            wechatDataSet = comMini.WebRefreshToken(webCode)
            openID = wechatDataSet.get("openID", "")
            expiresIn = wechatDataSet.get("expiresIn", 7200)
            refreshToken = wechatDataSet.get("refreshToken", "")
            unionID = wechatDataSet.get("unionID", "")
            accessToken = wechatDataSet.get("accessToken", "")
            if openID != "":
                #临时存储 code 关联的数据, 
                comDB.setWechatWebCode(webCode, wechatDataSet,expiresIn)
        else:
            #调用扫码接口获取openID
            wechatDataSet = comMini.getWebOpenID(webCode)

            openID = wechatDataSet.get("openID", "")
            expiresIn = wechatDataSet.get("expiresIn", 7200)
            refreshToken = wechatDataSet.get("refreshToken", "")
            accessToken = wechatDataSet.get("accessToken", "")
            if openID != "":
                #临时存储 code 关联的数据, 
                comDB.setWechatWebCode(webCode, wechatDataSet,expiresIn)
                comDB.setWechatRefreshCode(webCode, wechatDataSet)
        result["openID"]  = openID
        result["unionID"]  = unionID
        result["accessToken"]  = accessToken

        # if _DEBUG:
        #     _LOG.info("DEBUG: funcGetWebOpenID {}".format(misc.jsonDumps(result))) 

    return result

#cmdA0A0 funcs end

 
#用户注册和登录部分
def cmdA0A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}

    lowerCMD = CMD.lower()

    try:
        
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        loginID = dataSet.get("loginID", "")
        passwd = dataSet.get("passwd", "")
        miniCode = dataSet.get("code", "") #微信小程序登录的code
        webCode = dataSet.get("webCode", "") #腾讯扫码登录的code
        position = dataSet.get("position", {"lng":"0","lat":"0"})
        
        verifyCode = dataSet.get("verifyCode", "") #注册验证码
        mobilePhoneNo = dataSet.get("mobilePhoneNo") #注册验证码
        if mobilePhoneNo:
            savedVerifyCode = comDB.getVerifyCode(mobilePhoneNo) #验证码        
        else:
            savedVerifyCode = comDB.getVerifyCode(loginID) #验证码
        
        appType = sessionIDSet.get("appType", "") #app类型
        tempUserID = sessionIDSet.get("loginID", "")
            
        loginIDPasswdValidFlag = comFC.chkLoginIDPasswd(loginID, passwd) #检查用户的loginID 和 passwd是否合规, =="B0"是合规, 但并不是说loginID和passwd是正确的
        
        openID = "" #微信小程序openID
        wechatOpenID = ""
        unionID = "" #微信小程序unionID
        sessionKey = "" #微信小程序session_key
        miniLoginID = "" #给微信小程序openID 对应的 loginID
        loginIDExistFlag = False
        
        if errCode == "B0":
            if miniCode != "" :
                #微信小程序登录
                if comDB.existMiniProgramCode(miniCode):
                    #已经通过 小程序 code 获取了 openID
                    miniProgramSet = comDB.getMiniProgramCode(miniCode)    

                else:
                    #调用接口获取openID
                    miniProgramSet = comMini.getOpenID(miniCode, appType = appType)
                    openID = miniProgramSet.get("openID", "")
                    if openID != "":
                        #临时存储 code 关联的小程序, 
                        comDB.setMiniProgramCode(miniCode, miniProgramSet)
                        
                openID = miniProgramSet.get("openID", "")
                unionID = miniProgramSet.get("unionID", "")
                sessionKey = miniProgramSet.get("sessionKey", "")

                wechatOpenID = openID
                openID = comMini.getWechatUniqueID(openID,unionID)

                if openID == "":
                    if loginID == "" and passwd == "":
                        errCode = "BF" #这个用户的微信小程序code有问题
                    else:
                        #login password
                        if verifyPasswd(loginID, passwd) == False:
                            errCode = "B5" #loginID or passwd 错
                else:
                    #statistics: 
                    comDB.incrUserLoginCount(openID)
                
                    #小程序客户端登录
                    miniLoginID = comDB.getLoginIDByOpenID(openID)
                    if miniLoginID == "":
                        if loginID == "" and passwd =="":
                            #errCode = "BE" #这个用户没有注册,必须输入login/passwd
                            loginID = openID #用户是访客, 可以直接浏览, 不能进行敏感操作.用openID替代loginID.
                            loginID = getMasterLoginID(loginID) #查询主账号
                            loginIDExistFlag = comDB.chkUserExist(loginID,delFlag=False) #判断是登录还是注册                                                 
                        elif loginIDPasswdValidFlag != "B0" and verifyCode == "": #passwd不对, 而且没有验证码
                            errCode = "B5" #loginID or passwd 错
                        else:
                            #判断是注册还是登录
                            loginIDExistFlag = comDB.chkUserExist(loginID,delFlag=False) #判断是登录还是注册
                            #savedVerifyCode = comDB.getVerifyCode(loginID) #验证码
                            if loginIDExistFlag:
                                #登录
                                loginID = getMasterLoginID(loginID) #查询主账号
                                
                                #verify login and passwd
                                if passwd != "" and passwd:
                                    if verifyPasswd(loginID, passwd):
                                        #小程序增加openID 验证, 以后可能改为必须loginID的owner 确认
                                        #new openID bind
                                        rtnData["wechatsUsers"] = str(bundleOpenIDWithLoginID(loginID, openID))
                                    else:
                                        errCode = "B5" #loginID or passwd 错
                                elif verifyCode and verifyCode == savedVerifyCode:
                                    rtnData["wechatsUsers"] = str(bundleOpenIDWithLoginID(loginID, openID))
                                else:
                                    errCode = "B5" #loginID or passwd 错
                                
                                #statistics:
                                #comDB.incrUserLoginCount(openID)
                            else:
                                #注册
                                #savedVerifyCode = comDB.getVerifyCode(loginID) #验证验证码
                                if verifyCode == "" or  savedVerifyCode != verifyCode:
                                    #注册行为但是没有验证码或者是验证码错误
                                    errCode = "BM" 
                                elif appType == "chief":
                                    #警察/管理权限入口,不支持注册
                                    #errCode = "BS"
                                    rtnData["wechatsUsers"] = str(bundleOpenIDWithLoginID(loginID, openID))
                                else:
                                    #new openID bind
                                    rtnData["wechatsUsers"] = str(bundleOpenIDWithLoginID(loginID, openID))
                             
                                    #statistics:
                                    comDB.incrUserRegCount(miniLoginID)

                    else:
                        #statistics:
                        #comDB.incrUserLoginCount(openID)
                        
                        if loginID == "" and passwd == "":
                            loginID = miniLoginID #用户用小程序code登录
                            loginIDExistFlag = True #用户用小程序code登录
                        elif loginIDPasswdValidFlag != "B0" and verifyCode == "": #passwd不对, 而且没有验证码
                            errCode = "B5" #loginID or passwd 错
                        else:
                            if verifyPasswd(loginID, passwd):
                                #old openID debundle
                                debundleOpenIDWithLoginID(miniLoginID, openID)
                                #new openID bind
                                rtnData["wechatsUsers"] = str(bundleOpenIDWithLoginID(loginID, openID))
                            elif  verifyCode != ""  and verifyCode == savedVerifyCode:
                                rtnData["wechatsUsers"] = str(bundleOpenIDWithLoginID(loginID, openID))
                            else:
                                errCode = "B5" #loginID or passwd 错                                
            if webCode != "" and webCode :
                #微信扫码登录
                wechatDataSet = funcGetWebOpenID(webCode)

                openID = wechatDataSet.get("openID", "")
                accessToken = wechatDataSet.get("accessToken", "")
                refreshToken = wechatDataSet.get("refreshToken", "")
                #返回给前端
                rtnData["accessToken"] = accessToken
                                
                if openID == "":

                    if _DEBUG:
                        _LOG.info("DEBUG: webCode step 0 openID:{}, loginID:{},passwd:{}".format(openID, loginID,passwd)) 

                    if loginID == "" and passwd == "":
                        errCode = "BF" #这个用户的扫码code有问题
                    else:
                        #login password
                        if verifyPasswd(loginID, passwd) == False:
                            errCode = "B5" #loginID or passwd 错
                else:
                    #statistics: ????
                    comDB.incrUserLoginCount(openID)
                    #web扫码客户端登录
                    webLoginID = comDB.getLoginIDByOpenID(openID)
                    if _DEBUG:
                        _LOG.info("DEBUG: webCode step 1 openID:{}, webLoginID:{}".format(openID, webLoginID)) 

                    if webLoginID == "":
                        if loginID == "" and passwd =="":
                            #errCode = "BE" #这个用户没有注册,必须输入login/passwd
                            loginID = openID #用户是访客, 可以直接浏览, 不能进行敏感操作.用openID替代loginID.
                            loginID = getMasterLoginID(loginID) #查询主账号
                            loginIDExistFlag = comDB.chkUserExist(loginID,delFlag=False) #判断是登录还是注册

                            if _DEBUG:
                                _LOG.info("DEBUG: webCode step 2 loginID:{}, loginIDExistFlag:{}".format(loginID,loginIDExistFlag)) 
                            
                        elif loginIDPasswdValidFlag != "B0" and verifyCode == "": #passwd不对, 而且没有验证码
                            errCode = "B5" #loginID or passwd 错
                        else:
                            #判断是注册还是登录
                            loginIDExistFlag = comDB.chkUserExist(loginID,delFlag=False) #判断是登录还是注册
                            #savedVerifyCode = comDB.getVerifyCode(loginID) #验证码

                            if _DEBUG:
                                _LOG.info("DEBUG: webCode step 3 loginIDExistFlag:{}".format(loginIDExistFlag)) 

                            if loginIDExistFlag:
                                #登录
                                loginID = getMasterLoginID(loginID) #查询主账号

                                #verify login and passwd
                                if passwd != "" and passwd:
                                    if verifyPasswd(loginID, passwd):
                                        #小程序增加openID 验证, 以后可能改为必须loginID的owner 确认
                                        #new openID bind
                                        rtnData["wechatsUsers"] = str(bundleOpenIDWithLoginID(loginID, openID))
                                    else:
                                        errCode = "B5" #loginID or passwd 错
                                elif verifyCode != ""  and verifyCode == savedVerifyCode:
                                    rtnData["wechatsUsers"] = str(bundleOpenIDWithLoginID(loginID, openID))
                                else:
                                    errCode = "B5" #loginID or passwd 错
                                
                                #statistics:
                                #comDB.incrUserLoginCount(openID)
                            else:
                                #注册
                                #savedVerifyCode = comDB.getVerifyCode(loginID) #验证验证码
                                if verifyCode == ""  or  savedVerifyCode != verifyCode :
                                    #注册行为但是没有验证码或者是验证码错
                                    errCode = "BM" 
                                elif appType == "chief":
                                    #警察/管理权限入口,不支持注册
                                    #errCode = "BS"
                                    rtnData["wechatsUsers"] = str(bundleOpenIDWithLoginID(loginID, openID))
                                else:
                                    #new openID bind
                                    rtnData["wechatsUsers"] = str(bundleOpenIDWithLoginID(loginID, openID))
                                    
                                    #statistics:
                                    comDB.incrUserRegCount(webLoginID)

                        if errCode == "B0":

                            #没有出错
                            userInfo = comMini.webUserInfo(accessToken,openID)

                            if _DEBUG:
                                _LOG.info("DEBUG: webCode step 4 userInfo:{}, loginIDExistFlag:{}".format(misc.jsonDumps(userInfo),loginIDExistFlag)) 

                            #把用户信息插入到输入信息
                            dataSet["nickName"] = userInfo.get("nickName","")
                            dataSet["sex"] = userInfo.get("sex","")
                            dataSet["countryID"] = userInfo.get("countryID","")
                            dataSet["province"] = userInfo.get("province","")
                            dataSet["city"] = userInfo.get("city","")
                            dataSet["avatarID"] = userInfo.get("avatarID","")
                            dataSet["unionID"] = userInfo.get("unionID","")

                    else:
                        #statistics:
                        #comDB.incrUserLoginCount(openID)
                        
                        if loginID == "" and passwd =="":
                            loginID = webLoginID #用户用小程序code登录
                            loginIDExistFlag = True #用户用小程序code登录
                        elif loginIDPasswdValidFlag != "B0" and verifyCode == "": #passwd不对, 而且没有验证码
                            errCode = "B5" #loginID or passwd 错
                        else:
                            if verifyPasswd(loginID, passwd):
                                #old openID debundle
                                debundleOpenIDWithLoginID(webLoginID, openID)
                                #new openID bind
                                rtnData["wechatsUsers"] = str(bundleOpenIDWithLoginID(loginID, openID))
                            elif  verifyCode != ""  and verifyCode == savedVerifyCode:
                                rtnData["wechatsUsers"] = str(bundleOpenIDWithLoginID(loginID, openID))
                            else:
                                errCode = "B5" #loginID or passwd 错                                
            else:
                #web和其他方式登录
                #判断是注册还是登录
                loginIDExistFlag = comDB.chkUserExist(loginID,delFlag=False) #判断是登录还是注册
                if not loginIDExistFlag:
                    #savedVerifyCode = comDB.getVerifyCode(loginID) #验证验证码
                    # if verifyCode == ""  or  savedVerifyCode != verifyCode :
                    if (verifyCode == ""  or  savedVerifyCode != verifyCode) \
                        and not (settings._MiniProgramLoginSaveFlag) :
                        #注册行为但是没有验证码或者是验证码错, 而且默认是浏览用户无需保存数据
                        errCode = "BM" 
                    if appType == "chief":
                        #警察/管理权限入口,不支持注册
                        errCode = "BS"

                    if errCode == "B0":
                        #注册
                        #statistics:
                        comDB.incrUserRegCount(loginID)
                        
                #if loginIDExistFlag:
                else:
                    
                    loginID = getMasterLoginID(loginID) #查询主账号
                    
                    if not settings._MiniProgramLoginSaveFlag:
                        # 浏览用户无需保存数据, 这个时候需要验证
                        if loginIDPasswdValidFlag == "B0":
                            #用户输入了合乎要求的loginID 和 passwd,不是说和存储的一致, 而且默认是
                            #这个可能是web 登录
                            #verify login and passwd
                            if verifyPasswd(loginID, passwd) == False:
                                errCode = "B5" #loginID or passwd 错
                        else:
                            errCode = loginIDPasswdValidFlag #错误的细节
                    else:
                        #检查passwd
                        #verify login and passwd
                        if verifyPasswd(loginID, passwd) == False:
                            errCode = "B5" #loginID or passwd 错
                    
                    if errCode == "B0":
                        #statistics:
                        comDB.incrUserLoginCount(loginID)
                        
            if errCode == "B0": 
                saveSet = {}
                saveSet["loginID"] = loginID
                currYMDHMS = misc.getTime()
                if loginIDExistFlag == False:
                    #registration,注册      
                    saveSet["passwd"] = misc.genHashPasswd(passwd)

                    #saveSet["nickName"] = dataSet.get("nickName", (comGD._DEF_NICKNAME_PREFIX+loginID)[0:comGD._DEF_NICKNAME_LEN])

                    #如果有loginID,就取loginID的部分,否则取日期
                    if loginID:
                        saveSet["nickName"] = dataSet.get("nickName", comGD._DEF_NICKNAME_PREFIX + loginID[-comGD._DEF_NICKNAME_LAST_NUM_LEN:0])
                    else:
                        saveSet["nickName"] = dataSet.get("nickName", comGD._DEF_NICKNAME_PREFIX + "_" + currYMDHMS)

                    saveSet["realName"] = dataSet.get("realName", "")
                    mobilePhoneNo = dataSet.get("mobilePhoneNo", "")
                    saveSet["mobilePhoneNo"] = mobilePhoneNo
                    #如果是有手机号码
                    if mobilePhoneNo:
                        saveSet["roleName"] = settings.accountServiceMobilePhoneRoleName #有手机号码的默认角色
                    else:
                        saveSet["roleName"] = settings.accountServiceMobilePhoneRoleName #没有手机号码的默认角色
                    saveSet["countryID"] = dataSet.get("countryID", "")
                    saveSet["province"] = dataSet.get("province", "")
                    saveSet["city"] = dataSet.get("city", "")
                    saveSet["area"] = dataSet.get("area", "")
                    saveSet["address"] = dataSet.get("address", "")
                    saveSet["email"] = dataSet.get("email", "")
                    saveSet["PID"] = dataSet.get("PID", "")
                    saveSet["sex"] = dataSet.get("sex", "")
                    saveSet["privilege"] = dataSet.get("privilege", "")
                    saveSet["unionID"] = unionID
                    saveSet["wechatOpenID"] = wechatOpenID
                    activeFlag = comGD._CONST_YES
                    saveSet["activeFlag"] = activeFlag #用户活动标记
                    photoIDFront = dataSet.get("photoIDFront", "")
                    if photoIDFront != "":
                        #account service 不保存照片本身, 只保存ID
                        # try:
                        #     saveSet["photoIDFront"] = save2newLocation(photoIDFront, prefix = lowerCMD, privateFlag = True)
                        # except:
                        #     pass
                        saveSet["photoIDFront"] = photoIDFront

                    photoIDBack = dataSet.get("photoIDBack", "")
                    if photoIDBack != "":
                        #account service 不保存照片本身, 只保存ID
                        # try:
                        #     saveSet["photoIDBack"] = save2newLocation(photoIDBack, prefix = lowerCMD, privateFlag = True)
                        # except:
                        #     pass
                        saveSet["photoIDBack"] = photoIDBack

                    photoID = dataSet.get("photoID", "")
                    if photoID != "":
                        #account service 不保存照片本身, 只保存ID
                        # try:
                        #     saveSet["photoID"] = save2newLocation(photoID, prefix = lowerCMD, privateFlag = True)
                        # except:
                        #     pass
                        saveSet["photoID"] = photoID

                    avatarID = dataSet.get("avatarID", "")
                    if avatarID != "":
                        #account service 不保存照片本身, 只保存ID
                        # try:
                        #     saveSet["avatarID"] = save2newLocation(avatarID, prefix = lowerCMD)
                        # except:
                        #     pass
                        saveSet["avatarID"] = avatarID

                    saveSet["regID"] = tempUserID
                    saveSet["regYMDHMS"] = currYMDHMS
                    saveSet["regPosition"] = position #dict/list类型必须转换
                    if openID != "":
                        saveSet["regOpenID"] = openID
                    saveSet["lastLoginYMDHMS"] = currYMDHMS
                else:
                    #login
                    userInfo = comDB.getUserAllInfo(loginID,delFlag=False)
                    activeFlag = userInfo.get("activeFlag")
                    if not activeFlag:
                        activeFlag = comGD._CONST_YES
                    avatarID = dataSet.get("avatarID", "")
                    if userInfo.get("avatarID", "") == "":
                        #account service 不保存照片本身, 只保存ID
                        # saveSet["avatarID"] = save2newLocation(avatarID, prefix = lowerCMD)
                        # delPermanentFile(userInfo.get("avatarID"))
                        saveSet["avatarID"] = avatarID
                        
                    # defaultNickName = dataSet.get("nickName", (comGD._DEF_NICKNAME_PREFIX+loginID)[0:comGD._DEF_NICKNAME_LEN])
                    defaultNickName = dataSet.get("nickName", comGD._DEF_NICKNAME_PREFIX + loginID[-comGD._DEF_NICKNAME_LAST_NUM_LEN:0]) 

                    nickName = userInfo.get("nickName","")
                    if not nickName:
                        nickName = defaultNickName
                        saveSet["nickName"] = defaultNickName                        

                    countryID = dataSet.get("countryID", "")
                    if userInfo.get("countryID", "") == "" and countryID != "":
                        saveSet["countryID"] = countryID

                    province = dataSet.get("province", "")
                    if userInfo.get("province", "") == "" and province != "":
                        saveSet["province"] = province

                    city = dataSet.get("city", "")
                    if userInfo.get("city", "") == "" and city != "":
                        saveSet["city"] = city

                    area = dataSet.get("area", "")
                    if userInfo.get("area", "") == "" and area != "":
                        saveSet["area"] = dataSet.get("area", "")

                    address = dataSet.get("address", "")
                    if userInfo.get("address", "") == "" and address != "":
                        saveSet["address"] = dataSet.get("address", "")

                    sex = dataSet.get("sex", "")
                    if userInfo.get("sex", "") == "" and sex != "":
                        saveSet["sex"] = dataSet.get("sex", "")

                    if userInfo.get("unionID", "") == "" and unionID != "":
                        saveSet["unionID"] = unionID

                    #修改信息
                    saveSet["lastLoginYMDHMS"] = currYMDHMS
                    if openID != "":
                        saveSet["lastOpenID"] = openID

                    saveSet["wechatOpenID"] = wechatOpenID
                    
                #用户定义的非protect key的保存
                if comGD._DEF_REDIS_USER_SAVE_NON_PROTECT_KEYS:
                    for k, v in dataSet.items():
                        if not isUserProtectKey(k): #不是被保护的关键词,才可以保存
                            saveSet[k] = v
                    
                if saveSet:
                    saveSet["modifyID"] = tempUserID
                    saveSet["modifyYMDHMS"] = misc.getTime()

                comDB.setUserInfo(loginID, copy.deepcopy(saveSet))
                #if _DEBUG:
                    #_LOG.info("DEBUG: setUserInfo loginID:{}, saveSet:{}".format(loginID,saveSet)) 
                
                ruleInfo = comDB.getUserRule(loginID)
                roleName = comDB.getUserRoleName(loginID)
                userInfo = comDB.getUserAllInfo(loginID,delFlag=False)
#                ruleInfo = userInfo.get("ruleInfo", {})
#                roleName = userInfo.get("roleName", "visitor")
                mobilePhoneNo = userInfo.get("mobilePhoneNo", "")
                mobileValidation = comGD._CONST_NO
                if mobilePhoneNo and mobilePhoneNo != "":
                    validSet =  comFC.chkDataValidataion(mobilePhoneNo, comGD._DEF_TEL_LABEL, lang)
                    if validSet["rtn"] == True:
                        mobileValidation = comGD._CONST_YES

                PID = userInfo.get("PID", "")
                PIDValidation = comGD._CONST_NO
                if PID and PID != "":
                    validSet =  comFC.chkDataValidataion(PID, comGD._DEF_PID_LABEL, lang)
                    if validSet["rtn"] == True:
                        PIDValidation = comGD._CONST_YES
                        
                if appType == "chief":
                    if (comFC.chkIsChiefOrOpertor(roleName) == False):
                        errCode = "BT"
                        errCode = "BE" #temp solution
                    
                else:
                
                    if (comFC.chkIsChiefOrOpertor(roleName)):
                        pass #临时关闭 tempsolution
#                        roleName = comGD._DEF_LIGHT_USER_DEFAULT_ROLENAME  #非chief接口,只能是 visitor 角色
                
                if errCode == "B0":

                    #sessionID related
                    sessionIDSet = {}
                    sessionIDSet["loginID"] = loginID #用户登录号
                    sessionIDSet["ruleInfo"] = misc.jsonDumps(ruleInfo)  #用户角色,涉及到权限分配
                    sessionIDSet["roleName"] = roleName  #用户角色名称
                    sessionIDSet["mobileValidation"] = mobileValidation  #手机号认证标记
                    sessionIDSet["PIDValidation"] = PIDValidation  #实名认证标记
                    sessionIDSet["activeFlag"] = activeFlag  #用户活动标记
                        
                    if openID != "":
                        sessionIDSet["openID"] = openID #微信小程序,openid
                    if sessionKey != "":
                        sessionIDSet["sessionKey"] = sessionKey #微信小程序,session_key
                    
                    expireTime = comFC.getExpireTime(roleName)
                    
                    sessionID = comDB.genUserSession(sessionIDSet, expireTime)
                    rtnData["loginID"] = loginID
                    rtnData["sessionID"] = sessionID
                    rtnData["openID"] = openID
                    rtnData["wechatOpenID"] = wechatOpenID
                    rtnData["unionID"] = unionID
                    rtnData["mobileValidation"] = mobileValidation
                    rtnData["PIDValidation"] = PIDValidation
                    rtnData["activeFlag"] = activeFlag
                    
                    #传送到mysql 保存队列
#                    comDB.trans2MysqlList(CMD, saveSet)
                    
                    #返回roleName 给 web端
                    rtnData["roleName"] = roleName

        result = rtnData

        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result
    

#删除
def cmdA1A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+"B0"
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()
    
    try:

        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        loginID = dataSet.get("loginID", "")
        passwd = dataSet.get("passwd", "")
        
        sessionID = dataSet.get("sessionID", "")

        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "") #这个是管理员的roleName
        
        tempUserID = comDB.chkUserSession(sessionID) #这个是管理员的ID

        if comDB.chkUserExist(loginID,delFlag=False) == False:
            errCode = "BE"
        elif tempUserID != loginID:
            userInfo = comDB.getUserInfo(loginID,["roleName","loginID"],delFlag=False)
            targetRoleName = userInfo.get("roleName")
            #only manager can delete account
            if comFC.chkIsManager(roleName) and comFC.chkSetRoleRight(roleName,targetRoleName):
                #delete
                comDB.delUserInfo(loginID, openID,action = True)
            else:
                errCode = "B1"

        else:
            #verify passwd
            if verifyPasswd(loginID, passwd):
                #delete
                comDB.delUserInfo(loginID, openID,action = True)
                comDB.delUserSession(sessionID)

                #传送到mysql 保存队列
#                payload = {"loginID":loginID}
#                comDB.trans2MysqlList(CMD, payload)

                result = rtnData
            else:
                errCode = "B5"

        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode
           
    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  

    return result


#用户修改
def cmdA2A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        loginID = dataSet.get("loginID", "")
        passwd = dataSet.get("passwd", "")
        
        sessionID = dataSet.get("sessionID", "")
        
        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")
             
        if loginID == "" or tempUserID != loginID:
            if loginID == "":
                loginID = openID
            else:
                errCode = "B1"
        # elif len(loginID) <= comGD._DEF_REDIS_USER_ID_LENGTH:
        #     errCode = "B2"
        # elif passwd == "":
        #     errCode = "B3"
        # elif comDB.chkUserExist(loginID) == False:
        #     errCode = "BE"
            
        if comDB.chkUserExist(loginID,delFlag=False) == False:
            errCode = "BE"
        else:
    
            if errCode == "B0":
                userInfo = comDB.getUserAllInfo(loginID,delFlag=False)
                
                saveSet = {}
                
                #用户定义的非protect key的保存
                if comGD._DEF_REDIS_USER_SAVE_NON_PROTECT_KEYS:
                    for k, v in dataSet.items():
                        if not isUserProtectKey(k): #不是被保护的关键词,才可以保存
                            saveSet[k] = v

                saveSet["loginID"] = loginID

                #change passwd
                newPasswd = dataSet.get("newPasswd", "")
                if newPasswd:
                    saveSet["passwd"] = misc.genHashPasswd(newPasswd)
                # else:
                #     errCode = "B6"
                #     rtnCMD = rtnCMD[0:2]+errCode

                realName = dataSet.get("realName")
                if realName:
                    saveSet["realName"] = realName

                nickName = dataSet.get("nickName")
                if nickName:
                    saveSet["nickName"] = nickName

                country = dataSet.get("country")
                if country:
                    saveSet["country"] = country

                countryID = dataSet.get("countryID")
                if countryID:
                    saveSet["countryID"] = countryID

                province = dataSet.get("province")
                if province:
                    saveSet["province"] = province

                city = dataSet.get("city")
                if city:
                    saveSet["city"] = city

                area = dataSet.get("area")
                if area:
                    saveSet["area"] = area

                address = dataSet.get("address")
                if address:
                    saveSet["address"] = address

                emailAddr = dataSet.get("email")
                if emailAddr:
                    saveSet["email"] = emailAddr
                
                #图片的内容
                avatarID = dataSet.get("avatarID")
                if avatarID:
                    #account service 不保存照片本身, 只保存ID
                    # saveSet["avatarID"] = save2newLocation(avatarID, prefix = lowerCMD)
                    # delPermanentFile(userInfo.get("avatarID"))
                    saveSet["avatarID"] = avatarID

                groupQrcode = dataSet.get("groupQrcode")
                if groupQrcode:
                    #account service 不保存照片本身, 只保存ID
                    # saveSet["groupQrcode"] = save2newLocation(groupQrcode, prefix = lowerCMD)
                    # delPermanentFile(userInfo.get("groupQrcode"))
                    saveSet["groupQrcode"] = groupQrcode

                backgroundImg = dataSet.get("backgroundImg")
                if backgroundImg:
                    #account service 不保存照片本身, 只保存ID
                    # saveSet["backgroundImg"] = save2newLocation(backgroundImg, prefix = lowerCMD)
                    # delPermanentFile(userInfo.get("backgroundImg"))
                    saveSet["backgroundImg"] = backgroundImg

                #需要验证码才可以修改的部分
                verifyCode = dataSet.get("verifyCode")
                mobilePhoneNo = dataSet.get("mobilePhoneNo") #注册验证码
                if mobilePhoneNo:
                    savedVerifyCode = comDB.getVerifyCode(mobilePhoneNo) #验证码        
                else:
                    savedVerifyCode = comDB.getVerifyCode(loginID) #验证码
                if  (savedVerifyCode == verifyCode and verifyCode) :
                    # #特殊内容
                    # realName = dataSet.get("realName")
                    # if realName:
                    #     saveSet["realName"] = realName

                    if mobilePhoneNo:
                        saveSet["mobilePhoneNo"] = mobilePhoneNo
                    
                    PID = dataSet.get("PID")
                    if PID:
                        saveSet["PID"] = PID

                    photoIDFront = dataSet.get("photoIDFront")
                    if photoIDFront:
                        #account service 不保存照片本身, 只保存ID
                        # delPermanentFile(userInfo.get("photoIDFront"), privateFlag = True)
                        # photoIDFront = save2newLocation(photoIDFront, prefix = lowerCMD, privateFlag = True)
                        saveSet["photoIDFront"] = photoIDFront

                    photoIDBack = dataSet.get("photoIDBack")
                    if photoIDBack:
                        #account service 不保存照片本身, 只保存ID
                        # delPermanentFile(userInfo.get("photoIDBack"), privateFlag = True)
                        # photoIDBack = save2newLocation(photoIDBack, prefix = lowerCMD, privateFlag = True)
                        saveSet["photoIDBack"] = photoIDBack

                    photoID = dataSet.get("photoID")
                    if photoID:
                        #account service 不保存照片本身, 只保存ID
                        # delPermanentFile(userInfo.get("photoID"), privateFlag = True)
                        # photoID = save2newLocation(photoID, prefix = lowerCMD, privateFlag = True)
                        saveSet["photoID"] = photoID
                            
                #用户定义的非protect key的保存
                if comGD._DEF_REDIS_USER_SAVE_NON_PROTECT_KEYS:
                    for k, v in dataSet.items():
                        if not isUserProtectKey(k): #不是被保护的关键词,才可以保存
                            saveSet[k] = v

                saveSet["modifyID"] = tempUserID
                saveSet["modifyYMDHMS"]  = misc.getTime()
                saveSet["modifyOpenID"]  = openID
                
                comDB.setUserInfo(loginID, copy.deepcopy(saveSet))
                comDB.saveUserSession(loginID, sessionID)

                #传送到mysql 保存队列
#                payload = saveSet
#                comDB.trans2MysqlList(CMD, payload)

                result = rtnData

        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode
           
    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  

    return result


#用户信息获取
def cmdA3A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
        
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")

        appType = sessionIDSet.get("appType", "") #app类型
        
        if tempUserID == "":
            errCode = "B8"
        else:
            
            selfQueryFlag = True
            
            if "loginID" in dataSet: 
                #允许查其他人
                if comFC.chkIsManager(roleName):
                    loginID = dataSet.get("loginID")
                    if tempUserID != loginID:
                        selfQueryFlag = False
            else:
                if tempUserID == "":
                    loginID = openID
                else:
                    loginID = tempUserID
                
            currUserInfo = comDB.getUserAllInfo(loginID,delFlag=False)
            rtnData["nickName"] = currUserInfo.get("nickName", "")
            rtnData["countryID"] = currUserInfo.get("countryID", "")
            rtnData["province"] = currUserInfo.get("province", "")
            rtnData["city"] = currUserInfo.get("city", "")
            rtnData["area"] = currUserInfo.get("area", "")
            rtnData["address"] = currUserInfo.get("address", "")
            rtnData["email"] = currUserInfo.get("email", "")
            rtnData["sex"] = currUserInfo.get("sex", "")
            rtnData["unionID"] = currUserInfo.get("unionID", "")
            
            mobilePhoneNo = currUserInfo.get("mobilePhoneNo", "")
            
            #把非保护的数据给用户
            if comGD._DEF_REDIS_USER_SAVE_NON_PROTECT_KEYS:
                for k, v in currUserInfo.items():
                    if k not in comGD._DEF_REDIS_USER_NOSHOW_KEYS_LIST:
                         rtnData[k] = v
            
            # if comFC.chkIsManager(roleName) or mobilePhoneNo == tempUserID \
            if comFC.chkIsOperator(roleName) or mobilePhoneNo == tempUserID \
                or (roleName not in ["visitor"] and selfQueryFlag):
                #manager, 本人号码和手机号码一致, 或者是本人查询
            #if roleName not in ["visitor"] or mobilePhoneNo == loginID:
                rtnData["realName"] = currUserInfo.get("realName", "")
                rtnData["mobilePhoneNo"] = currUserInfo.get("mobilePhoneNo", "")
                rtnData["PID"] = currUserInfo.get("PID", "")
                
                photoIDFront = currUserInfo.get("photoIDFront", "")
                rtnData["photoIDFront"] =  getTempLocation(photoIDFront)
                # rtnData["photoIDFront"] =  photoIDFront
                
                photoIDBack = currUserInfo.get("photoIDBack", "")
                rtnData["photoIDBack"] =  getTempLocation(photoIDBack)
                # rtnData["photoIDBack"] =  photoIDBack
                
                photoID = currUserInfo.get("photoID", "")
                rtnData["photoID"] =  getTempLocation(photoID)
                # rtnData["photoID"] =  photoID
            
            #图片数据
            groupQrcode = currUserInfo.get("groupQrcode", "")
            rtnData["groupQrcode"] = getTempLocation(groupQrcode)
            # rtnData["groupQrcode"] = groupQrcode

            backgroundImg = currUserInfo.get("backgroundImg", "")
            rtnData["backgroundImg"] = getTempLocation(backgroundImg)
            # rtnData["backgroundImg"] = backgroundImg

            avatarID = currUserInfo.get("avatarID", "")
            rtnData["avatarID"] = getTempLocation(avatarID)
            # rtnData["avatarID"] = avatarID
            
            #用户相关数据
            blockIDList = []
            # blockIDList = getBlockList(tempUserID,  roleName, mode = "short")
            
            # for blockPhoto in blockIDList:
            #     if "blockPhoto" in blockPhoto: 
            #         blockPhoto["blockPhoto"] = getTempLocation(blockPhoto["blockPhoto"])
            #     if "blockThumbnailID" in blockPhoto: 
            #         blockPhoto["blockThumbnailID"] = getTempLocation(blockPhoto["blockThumbnailID"])

            #add search option
            if "searchOption" in dataSet:
                #需要处理搜索问题
                ruleSet = dataSet.get("searchOption")
                allowList = ["blockName"]
                serachResultSet = comFC.handleSearchOption(ruleSet,allowList, blockIDList)
                if serachResultSet["rtn"] == "B0":
                    blockIDList = serachResultSet.get("data", [])
                    
            rtnData["blockIDList"] = blockIDList
            
            result = rtnData

        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result

 
#用户登录
def cmdA4A0(CMD, dataSet, sessionIDSet):
    return cmdA0A0(CMD, dataSet, sessionIDSet)

  
#用户注销/登出
def cmdA5A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")
        
        sessionID = sessionIDSet.get("sessionID")
        
        if tempUserID == "":
            errCode = "B8"
        else:
            comDB.delUserSession(sessionID)

            result = rtnData

        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result
    
    
#验证请求
def cmdA6A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
        
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        loginID = dataSet.get("loginID", "")
        miniCode = dataSet.get("code", "") #微信小程序登录的code
        position = dataSet.get("position", {"lng":"0","lat":"0"})

        sessionID = dataSet.get("sessionID", "")
        sessionIDSet = comDB.getSessionInfo(sessionID)
        
        tempUserID = sessionIDSet.get("loginID", "")
        openID = sessionIDSet.get("openID", "")
        
        mobilePhoneNo = ""
        
        if loginID != "":
            mobilePhoneNo = loginID
        else:
            if tempUserID != "":
                loadSet = comDB.getUserAllInfo(tempUserID,delFlag=False)
                mobilePhoneNo = loadSet.get("mobilePhoneNo", tempUserID)
            else:
                errCode = "B1"
        #设置短信验证码发送时间限制
        if not comDB.smsVerifyCodeLimit(mobilePhoneNo):
            errCode = "CS"
        else:        
            if errCode == "B0" and comFC.chkChinaMobileNo(mobilePhoneNo):
                number = random.randint(100000, 999999)
                content = str(number)
                #contentList = [str(number), str(comGD._DEF_DATA_SMS_CODE_KEEP_TIME)]
                #rtnSet = SMS.sendSMS(mobilePhoneNo, contentList, templateName = "verifyWithTime")
                rtnSet = SMS.sendSMS(mobilePhoneNo, content)
                if sys.version_info.major <= 2:
                    if isinstance(rtnSet, unicode):
                        rtnSet = rtnSet.encode("UTF-8")               
                        rtnSet = misc.jsonLoads(rtnSet)
                else:      
                    if isinstance(rtnSet, bytes):
                        rtnSet = rtnSet.decode()
                        rtnSet = misc.jsonLoads(rtnSet)
                rtnCode =  rtnSet.get("Code","")
                if rtnCode.upper() == "OK":
                    if loginID != "":
                        comDB.setVerifyCode(loginID, content)
                    if tempUserID != "" and tempUserID != loginID:
                        comDB.setVerifyCode(tempUserID, content) #给ABA0做准备
                    if openID != "":
                        comDB.setVerifyCode(openID, content) #给ABA0做准备
                    rtnData["loginID"] = loginID
                    rtnData["tempUserID"] = tempUserID
                    rtnData["mobilePhoneNo"] = mobilePhoneNo
                    rtnData["openID"] = openID
                else:
                    errCode = "BN"
                    if lang == "CN":
                        rtnField = SMS.SMS_ERR_MSG.get(rtnCode, "")
                    else:
                        rtnField = rtnSet.get("Message","")
                    
                    if sys.version_info.major <= 2:
                        if isinstance(rtnField, unicode):
                            rtnField = rtnField.encode("UTF-8")               
                    else:      
                        if isinstance(rtnField, bytes):
                            rtnField = rtnField.decode() 
                    
                result = rtnData
                
            else:
                errCode = "BW"
            
        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result


#验证反馈
def cmdA7A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()
    
    try:
        
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        loginID = dataSet.get("loginID", "")
        miniCode = dataSet.get("code", "") #微信小程序登录的code
        position = dataSet.get("position", {"lng":"0","lat":"0"})
        
        verifyCode = dataSet.get("verifyCode", "")
        
        if loginID != "":
            mobilePhoneNo = dataSet.get("mobilePhoneNo") #注册验证码
            if mobilePhoneNo:
                savedVerifyCode = comDB.getVerifyCode(mobilePhoneNo) #验证码        
            else:
                savedVerifyCode = comDB.getVerifyCode(loginID) #验证码
            if verifyCode != "" and savedVerifyCode == verifyCode:
                pass
            else:
                errCode = "BM"
        else:
            errCode = "B1"
            
        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result


#ping
def cmdA8A0(CMD, dataSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()
    
    try:
        
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        result["CMD_STATUS"] = "still under construction!"
        
        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result


#用户,重置passwd
def cmdA9A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()
    
    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        loginID = dataSet.get("loginID", "")
        passwd = dataSet.get("passwd", "")

        appType = sessionIDSet.get("appType", "") #app类型

        miniCode = dataSet.get("code", "") #微信小程序登录的code
        position = dataSet.get("position", {"lng":"0","lat":"0"})
        
        verifyCode = dataSet.get("verifyCode", "")

        if miniCode != "":
            #微信小程序登录
            if comDB.existMiniProgramCode(miniCode):
                #已经通过 小程序 code 获取了 openID
                miniProgramSet = comDB.getMiniProgramCode(miniCode)    
                openID = miniProgramSet.get("openID", "")
            else:
                #调用接口获取openID
                miniProgramSet = comMini.getOpenID(miniCode, appType = appType)
                openID = miniProgramSet.get("openID", "")
                if openID != "":
                    #临时存储 code 关联的小程序, 
                    comDB.setMiniProgramCode(miniCode, miniProgramSet)
        else:
            openID = ""
                                            
        if loginID == "":
            errCode = "B1"
        elif len(loginID) <= comGD._DEF_REDIS_USER_ID_LENGTH:
            errCode = "B2"
        elif passwd == "":
            errCode = "B3"
        elif comDB.chkUserExist(loginID,delFlag=False) == False:
            errCode = "BE"
        else:
            mobilePhoneNo = dataSet.get("mobilePhoneNo") #注册验证码
            if mobilePhoneNo:
                savedVerifyCode = comDB.getVerifyCode(mobilePhoneNo) #验证码        
            else:
                savedVerifyCode = comDB.getVerifyCode(loginID) #验证码
            if verifyCode != "" and savedVerifyCode == verifyCode:

                saveSet = {}
                saveSet["loginID"] = loginID
                saveSet["passwd"] = misc.genHashPasswd(passwd)
                
                if openID != "":
                    saveSet["passwdOpenID"] = openID
                saveSet["passwdYMDHMS"]  = misc.getTime()
                comDB.setUserInfo(loginID, copy.deepcopy(saveSet))

                #传送到mysql 保存队列
                #payload = saveSet
                #comDB.trans2MysqlList(CMD, payload)
            else:
                errCode = "BM"

        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  

    return result


#修改用户角色
def cmdACA0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()
    
    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        loginID = dataSet.get("loginID", "")
        modifyRoleName = dataSet.get("roleName", "")

        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")

        saveFlag = False

        if roleName == "administrator" and modifyRoleName != "administrator":
            saveFlag = True

        if roleName == "manager" and modifyRoleName not in ["administrator","manager"]:
            saveFlag = True

        if roleName == "operator" and modifyRoleName not in ["administrator","manager","operator"]:
            saveFlag = True

        if saveFlag:
            saveSet = {}
            saveSet["loginID"] = loginID
            saveSet["roleName"] = modifyRoleName
            
            saveSet["modifyID"] = tempUserID
            saveSet["modifyYMDHMS"]  = misc.getTime()
            saveSet["modifyLoginID"]  = tempUserID
            comDB.setUserInfo(loginID, copy.deepcopy(saveSet))

            #传送到mysql 保存队列
            #payload = saveSet
            #comDB.trans2MysqlList(CMD, payload)
        else:
            errCode = "BM"

        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  

    return result


#用户资料查询(mysql)
def cmdADA0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)
        
        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")
        
        if tempUserID != "":
            
            loginID = tempUserID

            if comFC.chkIsOperator(roleName) == False:
                errCode = "BG"
                
            if errCode == "B0": 
                searchLoginID = dataSet.get("loginID")
                roleName = dataSet.get("roleName")
                roleNameList = dataSet.get("roleNameList")
                beginYMD = dataSet.get("beginYMD")
                endYMD = dataSet.get("endYMD")
                
                mode = dataSet.get("mode", "normal")
  
                if searchLoginID:
                    userInfoList = comMysql.query_USER_BASIC(loginID = searchLoginID, mode=mode)

                #add search option
                elif "searchOption" in dataSet:
                    ruleSet = dataSet.get("searchOption", {})
                    userInfoList = comMysql.query_USER_BASIC(searchOption = ruleSet, mode=mode)
                    
                elif roleName:
                    userInfoList = comMysql.query_USER_BASIC(roleName = roleName, mode=mode)

                elif roleNameList:
                    userInfoList = comMysql.query_USER_BASIC(roleNameList = roleNameList, mode=mode)
                    
                elif beginYMD or endYMD:
                    if beginYMD == None:
                        beginYMD = misc.getPassday(comGD._DEF_ACCOUNT_USER_DEFAULT_DAYS)
                    if endYMD == None:
                        endYMD = misc.getPassday(1)
                    userInfoList = comMysql.query_USER_BASIC(beginYMD = beginYMD, endYMD = endYMD, mode=mode)
                    
                else:
                    userInfoList = comMysql.query_USER_BASIC(mode=mode)
                    
                dataList = []
                
                for userInfo in userInfoList:
                    if "passwd" in userInfo:
                        userInfo.pop("passwd")
                    if "passwdYMDHMS" in userInfo:
                        userInfo.pop("passwdYMDHMS")
                    if "avatarID" in userInfo:
                        avatarID = userInfo["avatarID"]
                        #需要把照片转移到public domain 
                        avatarID = getTempLocation(avatarID)
                        userInfo["avatarID"] = avatarID
                    if "photoIDFront" in userInfo:
                        photoIDFront = userInfo["photoIDFront"]
                        #需要把照片转移到public domain 
                        photoIDFront = getTempLocation(photoIDFront)
                        userInfo["photoIDFront"] = photoIDFront
                    if "photoIDBack" in userInfo:
                        photoIDBack = userInfo["photoIDBack"]
                        #需要把照片转移到public domain 
                        photoIDBack = getTempLocation(photoIDBack)
                        userInfo["photoIDBack"] = photoIDBack
                    if "photoID" in userInfo:
                        photoID = userInfo["photoID"]
                        #需要把照片转移到public domain 
                        photoID = getTempLocation(photoID)
                        userInfo["photoID"] = photoID

                    dataList.append(userInfo)
                
                #临时缓存机制
                if bufferEnableFlag:
                    beginNum = int(dataSet.get("beginNum", comGD._DEF_BUFFER_DATA_BEGIN_NUM))
                    endNum = int(dataSet.get("endNum", comGD._DEF_BUFFER_DATA_END_NUM))
                    indexKey = putQueryResult(CMD, loginID, dataList) #存放数据到临时缓冲区去
                    rtnData["indexKey"]  = indexKey
                    total = len(dataList)
                    rtnData["total"]  = str(total)
                    rtnData["beginNum"]  = str(beginNum)
                    if endNum >= total:
                        endNum = total-1 #java/c rule, not python rule
                    rtnData["endNum"]  = str(endNum)

                    if total > 0:
                        rtnData["data"]  = dataList[beginNum:endNum+1]
                    else:
                        rtnData["data"]  = []
                else:
                    rtnData["data"]  = dataList
                                                       
                result = rtnData

        else:
            errCode = "B8"
            
        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  

    return result


#用户资料查询(redis)
def cmdAEA0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)
        
        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")
        
        if tempUserID != "":
            
            loginID = tempUserID

            if comFC.chkIsOperator(roleName) == False:
                errCode = "BG"
                
            if errCode == "B0": 
                searchLoginID = dataSet.get("loginID")
                roleName = dataSet.get("roleName")
                roleNameList = dataSet.get("roleNameList")
                beginYMD = dataSet.get("beginYMD")
                endYMD = dataSet.get("endYMD")
                loginIDPrefix = dataSet.get("loginIDPrefix")
                
                limitNum = dataSet.get("limitNum")
                if not limitNum:
                    limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM

                mode = dataSet.get("mode", "normal")
  
                if searchLoginID:
                    userInfoList = []
                    userInfo = comDB.getUserAllInfo(searchLoginID,delFlag=False)
                    userInfoList.append(userInfo)
                else:
                    if loginIDPrefix:
                        key = loginIDPrefix + "*"
                        userIDList = comDB.getAllUserIDList(maxNum = limitNum,key=key)
                    else:
                        userIDList = comDB.getAllUserIDList(maxNum = limitNum)
                    userInfoList = []
                    for userID in userIDList:
                        userInfo = comDB.getUserAllInfo(userID,delFlag=False)
                        userInfoList.append(userInfo)

                    #add search option

                    if "searchOption" in dataSet:
                        #需要处理搜索问题
                        ruleSet = dataSet.get("searchOption")
                        allowList = ["loginID","nickName","realName","roleName"]
                        serachResultSet = comFC.handleSearchOption(ruleSet,allowList, userInfoList)
                        if serachResultSet["rtn"] == "B0":
                            userInfoList = serachResultSet.get("data", [])
                    
                dataList = []
                
                for userInfo in userInfoList:
                    if "passwd" in userInfo:
                        userInfo.pop("passwd")
                    if "passwdYMDHMS" in userInfo:
                        userInfo.pop("passwdYMDHMS")
                    if "avatarID" in userInfo:
                        avatarID = userInfo["avatarID"]
                        #需要把照片转移到public domain 
                        avatarID = getTempLocation(avatarID)
                        userInfo["avatarID"] = avatarID
                    if "photoIDFront" in userInfo:
                        photoIDFront = userInfo["photoIDFront"]
                        #需要把照片转移到public domain 
                        photoIDFront = getTempLocation(photoIDFront)
                        userInfo["photoIDFront"] = photoIDFront
                    if "photoIDBack" in userInfo:
                        photoIDBack = userInfo["photoIDBack"]
                        #需要把照片转移到public domain 
                        photoIDBack = getTempLocation(photoIDBack)
                        userInfo["photoIDBack"] = photoIDBack
                    if "photoID" in userInfo:
                        photoID = userInfo["photoID"]
                        #需要把照片转移到public domain 
                        photoID = getTempLocation(photoID)
                        userInfo["photoID"] = photoID

                    dataList.append(userInfo)
                
                #临时缓存机制
                if bufferEnableFlag:
                    beginNum = int(dataSet.get("beginNum", comGD._DEF_BUFFER_DATA_BEGIN_NUM))
                    endNum = int(dataSet.get("endNum", comGD._DEF_BUFFER_DATA_END_NUM))
                    indexKey = putQueryResult(CMD, loginID, dataList) #存放数据到临时缓冲区去
                    rtnData["indexKey"]  = indexKey
                    total = len(dataList)
                    rtnData["total"]  = str(total)
                    rtnData["beginNum"]  = str(beginNum)
                    if endNum >= total:
                        endNum = total-1 #java/c rule, not python rule
                    rtnData["endNum"]  = str(endNum)

                    if total > 0:
                        rtnData["data"]  = dataList[beginNum:endNum+1]
                    else:
                        rtnData["data"]  = []
                else:
                    rtnData["data"]  = dataList
                                                       
                result = rtnData

        else:
            errCode = "B8"
            
        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  

    return result



#用户号码查询(前缀)
def cmdAGA0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)
        
        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")
        
        if tempUserID != "":
            
            loginID = tempUserID

            if comFC.chkIsOperator(roleName) == False:
                errCode = "BG"
                
            if errCode == "B0": 
                loginIDPrefix = dataSet.get("loginIDPrefix")
                
                userIDList = []

                if loginIDPrefix or loginIDPrefix == "":
                    userIDList = comDB.getUserIDList(loginIDPrefix)
                    
                dataList = []
                
                for userID in userIDList:
                    dataList.append(userID)
                
                #临时缓存机制
                if bufferEnableFlag:
                    beginNum = int(dataSet.get("beginNum", comGD._DEF_BUFFER_DATA_BEGIN_NUM))
                    endNum = int(dataSet.get("endNum", comGD._DEF_BUFFER_DATA_END_NUM))
                    indexKey = putQueryResult(CMD, loginID, dataList) #存放数据到临时缓冲区去
                    rtnData["indexKey"]  = indexKey
                    total = len(dataList)
                    rtnData["total"]  = str(total)
                    rtnData["beginNum"]  = str(beginNum)
                    if endNum >= total:
                        endNum = total-1 #java/c rule, not python rule
                    rtnData["endNum"]  = str(endNum)

                    if total > 0:
                        rtnData["data"]  = dataList[beginNum:endNum+1]
                    else:
                        rtnData["data"]  = []
                else:
                    rtnData["data"]  = dataList
                                                       
                result = rtnData

        else:
            errCode = "B8"
            
        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  

    return result


#管理员增加/修改用户信息
def cmdAHA0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        loginID = dataSet.get("loginID", "")
        passwd = dataSet.get("passwd", "")
        
        sessionID = dataSet.get("sessionID", "")
        
        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")
        
        #检查新增用户的roleName是否比操作人员低而且,操作人员role必须是管理员
        # only manager can add new user
        targetRoleName = dataSet.get("roleName")
        if comFC.chkIsManager(roleName) and comFC.chkSetRoleRight(roleName,targetRoleName):
            errCode = "B0"
        else:
            errCode = "BG"
    
        if errCode == "B0":
            userID = dataSet.get("userID")
            
            saveSet = {}
            
            saveSet["loginID"] = userID

            if targetRoleName:
                saveSet["roleName"] = targetRoleName

            activeFlag = dataSet.get("activeFlag")
            if activeFlag:
                saveSet["activeFlag"] = activeFlag

            #passwd
            passwd = dataSet.get("passwd", "")
            if passwd:
                saveSet["passwd"] = misc.genHashPasswd(passwd)

            #change passwd
            newPasswd = dataSet.get("newPasswd", "")

            if newPasswd:
                saveSet["passwd"] = misc.genHashPasswd(newPasswd)

            nickName = dataSet.get("nickName")
            if nickName:
                saveSet["nickName"] = nickName

            country = dataSet.get("country")
            if country:
                saveSet["country"] = country

            countryID = dataSet.get("countryID")
            if countryID:
                saveSet["countryID"] = countryID

            province = dataSet.get("province")
            if province:
                saveSet["province"] = province

            city = dataSet.get("city")
            if city:
                saveSet["city"] = city

            area = dataSet.get("area")
            if area:
                saveSet["area"] = area

            address = dataSet.get("address")
            if address:
                saveSet["address"] = address

            emailAddr = dataSet.get("email")
            if emailAddr:
                saveSet["email"] = emailAddr
            
            #图片的内容
            avatarID = dataSet.get("avatarID")
            if avatarID:
                #account service 不保存照片本身, 只保存ID
                # saveSet["avatarID"] = save2newLocation(avatarID, prefix = lowerCMD)
                # delPermanentFile(userInfo.get("avatarID"))
                saveSet["avatarID"] = avatarID

            groupQrcode = dataSet.get("groupQrcode")
            if groupQrcode:
                #account service 不保存照片本身, 只保存ID
                # saveSet["groupQrcode"] = save2newLocation(groupQrcode, prefix = lowerCMD)
                # delPermanentFile(userInfo.get("groupQrcode"))
                saveSet["groupQrcode"] = groupQrcode

            backgroundImg = dataSet.get("backgroundImg")
            if backgroundImg:
                #account service 不保存照片本身, 只保存ID
                # saveSet["backgroundImg"] = save2newLocation(backgroundImg, prefix = lowerCMD)
                # delPermanentFile(userInfo.get("backgroundImg"))
                saveSet["backgroundImg"] = backgroundImg

            mobilePhoneNo = dataSet.get("mobilePhoneNo")
            if mobilePhoneNo:
                saveSet["mobilePhoneNo"] = mobilePhoneNo

            #特殊内容
            realName = dataSet.get("realName")
            if realName:
                saveSet["realName"] = realName

            PID = dataSet.get("PID")
            if PID:
                saveSet["PID"] = PID

            photoIDFront = dataSet.get("photoIDFront")
            if photoIDFront:
                #account service 不保存照片本身, 只保存ID
                # delPermanentFile(userInfo.get("photoIDFront"), privateFlag = True)
                # photoIDFront = save2newLocation(photoIDFront, prefix = lowerCMD, privateFlag = True)
                saveSet["photoIDFront"] = photoIDFront

            photoIDBack = dataSet.get("photoIDBack")
            if photoIDBack:
                #account service 不保存照片本身, 只保存ID
                # delPermanentFile(userInfo.get("photoIDBack"), privateFlag = True)
                # photoIDBack = save2newLocation(photoIDBack, prefix = lowerCMD, privateFlag = True)
                saveSet["photoIDBack"] = photoIDBack

            photoID = dataSet.get("photoID")
            if photoID:
                #account service 不保存照片本身, 只保存ID
                # delPermanentFile(userInfo.get("photoID"), privateFlag = True)
                # photoID = save2newLocation(photoID, prefix = lowerCMD, privateFlag = True)
                saveSet["photoID"] = photoID

            #用户定义的非protect key的保存
            if comGD._DEF_REDIS_USER_SAVE_NON_PROTECT_KEYS:
                for k, v in dataSet.items():
                    if not isUserProtectKey(k): #不是被保护的关键词,才可以保存
                        saveSet[k] = v

            if comDB.chkUserExist(loginID,delFlag=False):
                saveSet["modifyID"] = tempUserID
                saveSet["modifyYMDHMS"]  = misc.getTime()
                saveSet["modifyOpenID"]  = openID
            else:
                saveSet["regID"] = tempUserID
                saveSet["regYMDHMS"]  = misc.getTime()
            
            comDB.setUserInfo(userID, saveSet)

            result = rtnData

        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode
           
    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  

    return result


#判断用户是否存在
def cmdAIA0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        loginID = dataSet.get("loginID", "")
        passwd = dataSet.get("passwd", "")
        
        sessionID = dataSet.get("sessionID", "")
        
        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")
           
        if errCode == "B0":
            userID = dataSet.get("userID")
            userExistFlag = comGD._CONST_NO
            
            if comDB.chkUserExist(userID,delFlag=False):
                userExistFlag = comGD._CONST_YES

            rtnData["userExistFlag"] = userExistFlag

            result = rtnData

        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode
           
    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  

    return result


#判断passwd是否合规
def cmdAKA0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        loginID = dataSet.get("loginID", "")
        passwd = dataSet.get("passwd", "")
        
        sessionID = dataSet.get("sessionID", "")
        
        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")
           
        if errCode == "B0":
            errCode = comFC.chkPasswd(passwd)
            result = rtnData

        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode
           
    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  

    return result


#管理员获取微信accessToken
def cmdM1A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        loginID = dataSet.get("loginID", "")
        passwd = dataSet.get("passwd", "")
        
        sessionID = dataSet.get("sessionID", "")
        
        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")
        
        if not comFC.chkIsOperator(roleName):
            errCode = "BG"
    
        if errCode == "B0":
            rtnData["accessToken"] = getMiniProgramAccessToken()

            result = rtnData

        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode
           
    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  

    return result


#系统获取获取不限制的小程序码
def cmdM2A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        loginID = dataSet.get("loginID", "")
        passwd = dataSet.get("passwd", "")
        
        sessionID = dataSet.get("sessionID", "")
        
        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")
            
        # if tempUserID or openID:
        scene = dataSet.get("scene","")
        page = dataSet.get("page","")
        if scene and page:
            errCode = "B0"
            accessToken = getMiniProgramAccessToken()
            if not accessToken:
                errCode = "BR"
        else:
            errCode = "BA" 
            rtnField = "scene or page is not exist"

        if errCode == "B0":
            checkPath = dataSet.get("checkPath")
            envVersion = dataSet.get("envVersion")
            width = dataSet.get("width")
            autoColor = dataSet.get("autoColor")
            lineColor = dataSet.get("lineColor")
            isHyaline = dataSet.get("isHyaline")

            if checkPath != None and envVersion != None:
                rtnData = comMini.getUnlimitedQRCode(accessToken,scene,page,checkPath=checkPath,envVersion=envVersion)
            elif checkPath != None and envVersion == None:
                rtnData = comMini.getUnlimitedQRCode(accessToken,scene,page,checkPath=checkPath)
            elif not checkPath == None and envVersion != None:
                rtnData = comMini.getUnlimitedQRCode(accessToken,scene,page,envVersion=envVersion)
            else:
                rtnData = comMini.getUnlimitedQRCode(accessToken,scene,page)
            rtnErrCode = rtnData.get("errCode")
            if rtnErrCode == 0:
                #二进制数据, 需要转换为 base64
                b64data = base64.b64encode(rtnData["data"])
                if isinstance(b64data, bytes):
                    b64data = b64data.decode()
                result["data"] = b64data
            else:
                errCode = "BA"
                rtnField = str(rtnErrCode) + "," + rtnData.get("errMsg")

        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode
           
    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  

    return result


#获取查询结果
def cmdG0A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()
    
    try:

        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)
    
        result["CMD_STATUS"] = "still under construction!"
        
        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result


#存储数据 --  G1A0
def cmdG1A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()
    
    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)
        
        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")
        
        userKey = dataSet.get("key", "")
        userVal = dataSet.get("val", "")

        if tempUserID != "":
            if openID != "":
                userID = openID
            else:
                userID = tempUserID
            if userKey != "" and userVal != "":
                comDB.setSavedData(userID, userKey, userVal)
            else:
                errCode = "BO"
        else:
            errCode = "B8"
            
        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result


#获取存储数据 --  G2A0
def cmdG2A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()
    
    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)
        
        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")
        
        userKey = dataSet.get("key", "")

        if tempUserID != "":
            if openID != "":
                userID = openID
            else:
                userID = tempUserID
            if userKey != "":
                userVal = comDB.getSavedData(userID, userKey)
                rtnData["val"] = userVal
                        
                result = rtnData
            else:
                errCode = "BO"
        else:
            errCode = "B8"
            
        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result


#获取下一批数据 --  G3A0
def cmdG3A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()
    
    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)
        
        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")
        
        indexKey = dataSet.get("indexKey", "")
        beginNum = int(dataSet.get("beginNum", comGD._DEF_BUFFER_DATA_BEGIN_NUM))
        endNum = int(dataSet.get("endNum", comGD._DEF_BUFFER_DATA_END_NUM))

        if tempUserID != "":
            if indexKey != "":
                dataExist,  dataList = getQueryResult(indexKey, beginNum, endNum)
                if dataExist:
                    dataLen = len(dataList)
                    endNum = (beginNum + dataLen)
                    rtnData["indexKey"] = indexKey
                    rtnData["beginNum"] = str(beginNum)
                    rtnData["endNum"] = str(endNum)
                    rtnData["data"] = dataList
                    rtnData["dataLen"] = str(dataLen)
                        
                    result = rtnData
                else:
                    errCode = "CC"
            else:
                errCode = "BO"
        else:
            errCode = "B8"
            
        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result


#超级用户,重置passwd
def cmdG9A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()
    
    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        loginID = dataSet.get("loginID", "")
        passwd = dataSet.get("passwd", "")
        
        if loginID == "":
            errCode = "B1"
        elif len(loginID) <= comGD._DEF_REDIS_USER_ID_LENGTH:
            errCode = "B2"
        elif passwd == "":
            errCode = "B3"
        elif comDB.chkUserExist(loginID,delFlag=False) == False:
            errCode = "BE"
        else:
            saveSet = {}
            saveSet["loginID"] = loginID
            saveSet["passwd"] = misc.genHashPasswd(passwd)

            if rtnCMD[2:4] == "B0":
                saveSet["modifyYMDHMS"]  = misc.getTime()
                saveSet["superG9YMDHMS"] = misc.getTime()
                comDB.setUserInfo(loginID, copy.deepcopy(saveSet))

                #传送到mysql 保存队列
                #payload = saveSet
                #comDB.trans2MysqlList(CMD, payload)

                result = rtnData

        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  

    return result


#获取 calUserCMDMapKeyList 服务
def cmdGAA0(CMD, dataSet, sessionIDSet={}):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        try:
            CMDList = []
            sessionIDSet = {}
            userErrCode = "B0"

            keyList = dataSet.get("CMDMapKeyList",[])
            sessionID = dataSet.get("sessionID","")

            sessionIDSet = comDB.getSessionInfo(sessionID)
            if sessionIDSet != {}:
                roleName = sessionIDSet.get("roleName", "")
                sessionIDSet["sessionID"] = sessionID
                aList = settings.ROLE_CMD_LIST.get(roleName, [])
                CMDList =list(set(aList).intersection(set(keyList)))
            else:
                userErrCode = "B8"

            rtnData["userCMDMapKeyList"] = CMDList
            rtnData["sessionIDSet"] = sessionIDSet
            rtnData["errCode"] = userErrCode

        except:
            pass

        result["data"] = rtnData
        
        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result


#获取UUID服务
def cmdGUA0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)
        
        try:
            defaultNum = int(dataSet.get("num", "4"))
        except:
            defaultNum = 4
            
        dataList = []
        
        for i in range(0, defaultNum):
            while True:
                data = str(uuid.uuid4())
                if comDB.chkFileExist(data) == False:
                    dataList.append(data)
                    break
                    
        result["dataList"] = dataList
        result["data"] = dataList[0]
        
        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result


#服务器信息通知
def cmdS0A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
    
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)

        result["CMD_STATUS"] = "still under construction!"
        
        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result

   
#服务器更新消息
def cmdS1A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:

        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)
    
        result["CMD_STATUS"] = "still under construction!"
        
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result


#微信支付,JSAPI接口
def cmdW0A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
        
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)
        
        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")

        appType = sessionIDSet.get("appType", "") #app类型

        miniCode = dataSet.get("code", "") #微信小程序登录的code
        if miniCode != "":
            #微信小程序登录
            if comDB.existMiniProgramCode(miniCode):
                #已经通过 小程序 code 获取了 openID
                miniProgramSet = comDB.getMiniProgramCode(miniCode)    
                openID = miniProgramSet.get("openID", "")
            else:
                #调用接口获取openID
                miniProgramSet = comMini.getOpenID(miniCode, appType = appType)
                openID = miniProgramSet.get("openID", "")
                if openID != "":
                    #临时存储 code 关联的小程序, 
                    comDB.setMiniProgramCode(miniCode, miniProgramSet)
        
        if tempUserID != "":
            if openID != "" and openID:
                fee = dataSet.get("fee", "0")
                
                tradeNo = dataSet.get("tradeNo")
                
                if tradeNo:
                    tradeNo = str(tradeNo)[0:32]
                else:
                    tradeNo = comFC.genDigest(tempUserID, misc.getTime())[0:32]
                
                requestSet = {}
                requestSet["openID"] = openID
                requestSet["total_fee"] = fee
                requestSet["tradeNo"] = tradeNo
                
                rtnSet = comMini.unifiedOrder(requestSet)
                paySign = rtnSet.get("paySign")
                if paySign:
                    rtnData = rtnSet
                    saveSet = {}
                    saveSet["loginID"] = tempUserID
                    saveSet["tradeNo"] = tradeNo
                    saveSet["fee_type"] = comMini.miniFeeType
                    saveSet["fee"] = fee
                    saveSet["openID"] = openID
                    saveSet["status"] = comGD._DEF_WECHAT_PAY_STATYS_CREATE
                    saveSet["createYMDHMS"] = misc.getTime()
                    recID = comMysql.insert_WEIXIN_PAY(saveSet)
                    rtnData["tradeNo"] = tradeNo
                    rtnData["recID"] = str(recID)
                    if recID <= 0:
                        errCode = "CG"
                else:
                    errCode = "BU"
                        
        else:
            errCode = "B8"
        result = rtnData

        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode

    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result


#微信支付,JSAPI接口, 支持非登录用户
def cmdW1A0(CMD, dataSet, sessionIDSet):
    result = {}
    errCode = "B0"
    rtnCMD = CMD[0:2]+errCode
    rtnField = ""
    rtnData = {}
    lowerCMD = CMD.lower()

    try:
        
        lang = dataSet.get("lang", comGD._DEF_DEFAULT_LANGUAGE)
        
        openID = sessionIDSet.get("openID", "")
        roleName = sessionIDSet.get("roleName", "")
        tempUserID = sessionIDSet.get("loginID", "")

        appType = sessionIDSet.get("appType", "") #app类型

        userToken = dataSet.get("token")
        YMDHMS = dataSet.get("YMDHMS")
        miniCode = dataSet.get("code", "") #微信小程序登录的code
        genToken = comFC.genDigest(settings.GEN_DIGIST_KEY, CMD, miniCode, YMDHMS)   
        currYMDHMS = misc.getTime()

        diffInSeconds =  misc.diffTime(YMDHMS, currYMDHMS)

        if genToken == userToken and diffInSeconds < (600): #权限判断, 时间差在10分钟内
            if miniCode != "":
                #微信小程序登录
                if comDB.existMiniProgramCode(miniCode):
                    #已经通过 小程序 code 获取了 openID
                    miniProgramSet = comDB.getMiniProgramCode(miniCode)    
                    openID = miniProgramSet.get("openID", "")
                else:
                    #调用接口获取openID
                    miniProgramSet = comMini.getOpenID(miniCode, appType = appType)
                    openID = miniProgramSet.get("openID", "")
                    if openID != "":
                        #临时存储 code 关联的小程序, 
                        comDB.setMiniProgramCode(miniCode, miniProgramSet)
            else:
                errCode = "BX"
                
            if openID != "" and openID and errCode == "B0":
                fee = dataSet.get("fee", "0")
                
                tradeNo = comFC.genDigest(tempUserID, misc.getTime())[0:32]
                
                requestSet = {}
                requestSet["openID"] = openID
                requestSet["total_fee"] = fee
                requestSet["tradeNo"] = tradeNo
                
                rtnSet = comMini.unifiedOrder(requestSet)
                paySign = rtnSet.get("paySign")
                if paySign:
                    rtnData = rtnSet
                    saveSet = {}
                    saveSet["tradeNo"] = tradeNo
                    saveSet["loginID"] = tempUserID
                    saveSet["fee_type"] = comMini.miniFeeType
                    saveSet["fee"] = fee
                    saveSet["openID"] = openID
                    saveSet["status"] = comGD._DEF_WECHAT_PAY_STATYS_CREATE
                    saveSet["createYMDHMS"] = misc.getTime()
                    recID = comMysql.insert_WEIXIN_PAY(saveSet)
                    rtnData["tradeNo"] = tradeNo
                    rtnData["recID"] = str(recID)
                    if recID <= 0:
                        errCode = "CG"
                else:
                    errCode = "BU"
                    
            else:
                errCode = "BY"
        else:
            errCode = "BZ"
        
        result = rtnData

        rtnCMD = CMD[0:2]+errCode
        rtnSet = comFC.rtnMSG(rtnCMD, errCode, rtnField, lang)
        result["CMD"] = rtnSet["CMD"]
        result["MSG"] = rtnSet["MSG"]
        result["errCode"] = errCode
        
    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
       
    return result

# command part end


#===== main entrace ======
CMDMap = {
    #用户注册
    "A0A0":cmdA0A0, 
    #用户删除
    "A1A0":cmdA1A0, 
    #用户修改
    "A2A0":cmdA2A0, 
    #用户信息获取
    "A3A0":cmdA3A0, 
    #用户登录
    "A4A0":cmdA4A0, 
    #用户注销/登出
    "A5A0":cmdA5A0, 
    #验证请求
    "A6A0":cmdA6A0, 
    #验证反馈
    "A7A0":cmdA7A0, 
    #ping
    "A8A0":cmdA8A0, 
    #用户,重置passwd
    "A9A0":cmdA9A0, 
    #修改用户角色
    "ACA0":cmdACA0, 
    #用户资料查询(mysql)
    "ADA0":cmdADA0, 
    #用户资料查询(reis)
    "AEA0":cmdAEA0, 
    #用户号码查询(前缀)
    "AGA0":cmdAGA0, 
    #管理员增加/修改用户信息
    "AHA0":cmdAHA0, 
    #判断用户是否存在
    "AIA0":cmdAIA0, 
    #判断passwd是否合规
    "AKA0":cmdAKA0, 

    #管理员获取微信accessToken
    "M1A0":cmdM1A0, 
    #系统获取获取不限制的小程序码
    "M2A0":cmdM2A0, 

    #获取查询结果
    "G0A0":cmdG0A0, 
    #存储数据 --  G1A0
    "G1A0":cmdG1A0, 
    #获取存储数据 --  G2A0
    "G2A0":cmdG2A0, 
    #获取下一批数据 --  G3A0
    "G3A0":cmdG3A0, 
    #超级用户,重置passwd
#    "G9A0":cmdG9A0, 
    #获取 calUserCMDMapKeyList 服务
    "GAA0":cmdGAA0, 
    #获取UUID服务
    "GUA0":cmdGUA0, 
    
    #服务器信息通知
    "S0A0":cmdS0A0, 
    #服务器更新消息
    "S1A0":cmdS1A0, 

    #微信支付,JSAPI接口
    "W0A0":cmdW0A0,   
    #微信支付,JSAPI接口,支持非登录用户
    "W1A0":cmdW1A0,  

}


CMDMapKeyList = []


for k, v in CMDMap.items():
    CMDMapKeyList.append(k)


def dataFormatConvertor(dataType,  dataSet):
    result = dataSet
    if dataType == "FORM":
        formData = dataSet.get("formData", {})
        for k, v in formData.items():
            result[k] = v
        result.pop("formData")
    return result
    
    
def calUserCMDMapKeyList(dataSet,CMDMapKeyList):
    CMDList = []
    sessionIDSet = {}
    errCode = "B0"
    CMD = dataSet.get("CMD")

    sessionID = dataSet.get("sessionID", "")

    if CMD in settings.NO_SESSIONID_CMD_LIST:
        #登录或者是注册等不需要sessionID的命令
        CMDList =list(set(settings.NO_SESSIONID_CMD_LIST).intersection(set(CMDMapKeyList)))
    else:
        sessionID = dataSet.get("sessionID", "")
        sessionIDSet = comDB.getSessionInfo(sessionID)
        if sessionIDSet != {}:
            roleName = sessionIDSet.get("roleName", "")
            sessionIDSet["sessionID"] = sessionID
            aList = settings.ROLE_CMD_LIST.get(roleName, [])
            CMDList =list(set(aList).intersection(set(CMDMapKeyList)))
        else:
            errCode = "B8"

    return CMDList, sessionIDSet, errCode
    
    
#程序入口, post 调用
def post(theLog, dataSet, IP, environSet, appType):
    global gSN
    global _LOG
    global _VERSION
    
    _LOG = theLog
    
    CMD = "CMD"
    errCode = "OK"
    rtnField = ""
    
    try:
        gSN += 1
        localSN = gSN
        #transfer data receive
#        REQUEST_METHOD = environSet.get("REQUEST_METHOD", "")
#        CONTENT_LENGTH = environSet.get("CONTENT_LENGTH", "")
#        CONTENT_TYPE = environSet.get("CONTENT_TYPE", "")
#        if _DEBUG:
#            _LOG.info("H: %s %s" % ("REQUEST_METHOD",  REQUEST_METHOD)) 
#            _LOG.info("H: %s %s" % ("CONTENT_LENGTH",  CONTENT_LENGTH)) 
#            _LOG.info("H: %s %s" % ("CONTENT_TYPE",  CONTENT_TYPE)) 

        if _DEBUG:
            _LOG.info("R:{0},{1},{2}".format(_VERSION, IP, misc.jsonDumps(dataSet)))
            
        if comDB.chkIPCount(IP):

            if comGD._DEF_ACCOUNT_CMD_NAME in dataSet:
                localSN = dataSet.get("SN", str(gSN))
                CMD = dataSet[comGD._DEF_ACCOUNT_CMD_NAME]
                dataType = dataSet.get("dataType", "")
                if dataType != "":
                    dataSet = dataFormatConvertor(dataType, dataSet)
                userCMDMapKeyList, sessionIDSet, errCode = calUserCMDMapKeyList(dataSet,CMDMapKeyList)
                openID = sessionIDSet.get("openID", "")
                loginID = sessionIDSet.get("loginID", "")
                if errCode == "B0":
                    sessionIDSet["appType"] = appType
                    
                    if CMD in userCMDMapKeyList:
                        dataSet["_IP"] = IP
                        dataSet = CMDMap[CMD](CMD, dataSet, sessionIDSet)
                        
                        #statistics:
                        if loginID == "":
                            loginID = openID
                        if loginID != "":
                            comDB.incrUserActiveCount(loginID)
                            
                    else:
                        dataSet = comFC.rtnMSG("ERROR", "ERR_NOCMD", "")
                else:
                    rtnCMD = CMD[0:2]+errCode
                    dataSet = comFC.rtnMSG(rtnCMD, errCode, "")
            else:
                dataSet = comFC.rtnMSG("ERROR", "ERR_NOCMD", "")
                
        else:
            dataSet = comFC.rtnMSG("ERROR", "ERR_IPFLOOD", "")

        dataSet["SN"] = localSN
        dataSet["YMDHMS"]  = misc.getTime()
        result = dataSet
#        result = misc.jsonDumps(dataSet)

        if _DEBUG:
            _LOG.info("S:{0},{1},{2}".format(_VERSION, IP, misc.jsonDumps(dataSet)))
            
    except Exception as e:
        errMsg = f"PID: {_processorPID},CMD:{CMD},errMsg:{str(e)}"
        _LOG.error(f"{errMsg}, {traceback.format_exc()}")

        rtnSet = comFC.rtnMSG("ERROR", "ERR_GENERAL", "")
        result = rtnSet  
   
    return result


if __name__ == "__main__":
    IP = "0.0.0.0"
    appType = "chief"
    appType = ""
    envSet = {"CONTENT_LENGTH":100}
    comMysql.checkMySqlDataBase()
    if len(sys.argv) > 1:
        pass
        if platform.system()=='Linux':
            import pdb
            pdb.set_trace()
            msg = sys.argv[1]
            dataSet = misc.jsonLoads(msg)
            post(_LOG, dataSet, IP, envSet, appType)
            exit(-1)
            
#        msg = '{"CMD":"A0A0","clientType":"web","SN":"1586755460463","loginID":"13910710766","passwd":"0eae66f9a3339addc0c209fd70a9b954","verifyCode":"808145","lang":"CN"}'
#        msg = '{"CMD":"A0A0","clientType":"miniProgram","SN":"9697761088","nickName":"\u5218\u7545","lang":"CN","YMDHMS":"","code":"021gmWfh2KRyuD0oFGdh2O02gh2gmWfk"}'
        
#        msg ='{"CMD":"A2A0","sessionID":"testonly","nickName":"test","loginID":"13910710766","email":"1@1"}'
#        msg = '{"CMD":"A2A0","clientType":"miniProgram","SN":"0134393713","sessionID":"2270e45d34b09cd29298036bf9655187","nickName":"\u6c34\u79c0","avatarID":"https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJdnShCNJ2OjfqVhCknfmGmyyr90xibMeSV1J5l0YO9cQplY3Tic0gH9PGuVX3ZqxAHuuIplicUeiaJIQ/132","mobilePhoneNo":"","realName":"\u5218","lang":"CN"}'

#        msg ='{"CMD":"A3A0","sessionID":"testonly"}'
#        msg ='{"CMD":"A3A0","sessionID":"20a6f3cd863c129e3d21858ceb118aef"}'
        
        msg ='{"CMD":"A6A0","sessionID":"testonly","loginID":"13910710766"}'

        
        msg = misc.jsonShiftReturn(msg)
        
        dataSet = misc.jsonLoads(msg)
        
        print(dataSet)
        
        rtnSet = post(_LOG, dataSet, IP, envSet, appType)
        
        print (rtnSet)
        
