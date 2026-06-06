#! /usr/local/python3/bin/python
#encoding: utf-8

#Filename: accountFuncCommon.py  
#Author: Steven Lian
#E-mail: steven.lian@gmail.com  
#Date: 2019-08-02
#Description:   这个应用的通用函数

#pip3 install password-validator

_VERSION="20241111"

import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
if sys.getdefaultencoding() != 'utf-8':
    pass
    #reload(sys)
    #sys.setdefaultencoding('utf-8')

#import time
import hashlib
import uuid
import random
import math
import re

import requests

#import numpy as np

#global defintion/common var etc.
from common import accountDefinition as comGD

#code/decode functions
#from common import codingDecoding as comCD

#common functions(log,time,string, json etc)
from common import miscCommon as misc

from password_validator import PasswordValidator

from common.id_validator import validator as PIDValidator

#setting files
from config import accountBasicSettings as settings

CONST_ERROR_KEY = "account"

passwdSchema = PasswordValidator()

passwdSchema \
    .min(settings.PASSWORD_RULE["minLength"])\
    .max(settings.PASSWORD_RULE["maxLength"])\

if settings.PASSWORD_RULE["upperCase"]:
    passwdSchema \
        .has().uppercase()\

if settings.PASSWORD_RULE["lowerCase"]:
    passwdSchema \
        .has().lowercase()

if settings.PASSWORD_RULE["number"]:
    passwdSchema \
        .has().digits()

if settings.PASSWORD_RULE["specialChar"]:
    passwdSchema \
        .has().symbols()

if not settings.PASSWORD_RULE["space"]:
    passwdSchema \
        .no().spaces()
    
#common function:
#如果执行失败或者异常返回消息定义
CONST_ERROR_wordList = {
    "EN":{
        "OK" :'success',
        "ERR_UPDATE" :'exception. check the updated value.',
        "ERR_FIELD" :'exception. the field %s not found or null.',
        "ERR_TOKEN" :'exception. token or format error.',
        "ERR_SESSION" :'exception. session or format error.',
        
        "ERR_DEVID" :"%s - it's a invalid device ID.",
        "ERR_LOGIN" :"login fail, no user or password wrong",
        "ERR_NO_REG" :"%s - it should be registered firstly.",
        "ERR_REPEAT_REG" :"%s - it has beed registered.",
        "ERR_INVALID":"exception. data in valid", 
        "ERR_WARN":"warning. cells status is not correct, pls check... ", 
        "ERR_GENERAL":"exception. unknow error. %s", 
        "ERR_NOCMD":"data format ERROR, no CMD", 
        "ERR_IPFLOOD":"too many visits", 

        "ERR_PID":"personal ID is invalid, format error", 
        "ERR_TEL":"telephone number is too short, format error", 
        "ERR_NAME":"name is too short, format error", 
        "ERR_HOTELNAME":"hotel name is too short, format error", 
        "ERR_ADDR":"address is too short, format error", 
        "ERR_EMAIL":"email format error", 
        
        "WARN_FACE":"face might not match with ID", 
        
        "B0":"success.",
        "B1":"loginID is invalid.",
        "B2":"loginID is too short.",
        "B3":"passwd is invalid.",
        "B4":"loginID is already exist.",
        "B5":"loginID or passwd is invalid.",
        "B6":"new passwd is invalid.",
        "B7":"new loginID is invalid.",
        "B8":"exception. sessionID or format error.",
        "B9":"alreay exist with same name and address, conflict.",
        "BA":"data is invalid %s.",
        "BE":"user need to be registered.",
        "BF":"mini program code error.",
        "BG":"access denied.",
        "BH":"Due fee, please recharge.",
        "BI":"recID is invalid.",
        "BK":"search option format error.",
        "BL":"file upload error. %s",
        "BM":"verify code is invalid",
        "BN":"verify code send error %s",
        "BO":"key or val error",
        "BP":"superiorID is invalid",
        "BQ":"category is invalid", 
        "BS":"this app don's support resistration",        
        "BT":"you dont' have right to access",       
        "BU":"wechat pay process error",    
        "BV":"face might not match with ID",    
        "BW":"mobile numer is wrong, or could not find",    
        "BX":"no code or wrong code, or no openID is wrong",    
        "BY":"no openID or wrong openID",    
        "BZ":"exception. token or format error.",    
        "CA":"repeat record,pls check",    
        "CB":"no record,pls check",    
        "CC":"expired, re-query",    
        "CD":"only register user could apply",    
        "CE":"invalid visitYMD",    
        "CF":"mobile, name might not match with ID",    
        "CG":"insert record error",    
        "CH":"templateID error",    
        "CI":"backbone service is offline",    
        "CU":"update record error",    
        "CV":"delete record error",    
        "CS":"The message has been sent too many times in a short period, please try again later.",    
    }, 
    "CN":{
        "OK" :'成功',
        "ERR_UPDATE" :'exception. check the updated value.',
        "ERR_FIELD" :'exception. the field %s not found or null.',
        "ERR_TOKEN" :'exception. token or format error.',
        "ERR_SESSION" :'exception. session or format error.',
        
        "ERR_DEVID" :"%s - it's a invalid device ID.",
        "ERR_LOGIN" :"login fail, no user or password wrong",
        "ERR_NO_REG" :"%s - it should be registered firstly.",
        "ERR_REPEAT_REG" :"%s - it has beed registered.",
        "ERR_INVALID":"exception. data in valid", 
        "ERR_WARN":"warning. cells status is not correct, pls check... ", 
        "ERR_GENERAL":"exception. unknow error. %s", 
        "ERR_NOCMD":"权限错误，请联系管理员", 
        "ERR_IPFLOOD":"too many visits", 
        
        "ERR_PID":"身份证号码是无效的", 
        "ERR_TEL":"电话号码太短,少于8位,请查看", 
        "ERR_NAME":"姓名太短,少于2个汉字,请查看", 
        "ERR_HOTELNAME":"酒店名称,少于3个汉字,请查看", 
        "ERR_ADDR":"地址信息太短,少于5个汉字,请查看", 
        "ERR_EMAIL":"email地址不对,请查看", 

        "WARN_FACE":"人脸和身份证可能不匹配,请查验", 

        "B0":"成功",
        "B1":"登录账号不存在",
        "B2":"登录账号太短,不少于6个字符",
        "B3":"密码错",
        "B4":"登录账号重复",
        "B5":"登录账号或者密码错",
        "B6":"新密码错",
        "B7":"新登录账号无效",
        "B8":"sessionID 无效",
        "B9":"已经存在,不能新增",
        "BA":"数据格式有问题, %s.",
        "BE":"用户没有注册,或者限制注册",   
        "BF":"小程序 code error.",
        "BG":"您的权限不足",
        "BH":"您已经欠费,请充值",
        "BI":"recID 无效.",
        "BK":"搜索逻辑格式错误",
        "BL":"文件上传失败. %s",
        "BM":"校验码无效",
        "BN":"验证码发送失败, %s",
        "BO":"key 或者 val 无效",
        "BP":"superiorID 错误",
        "BQ":"category 错误",
        "BR":"你没有登录此小程序的权限",        
        "BS":"不支持注册功能",        
        "BT":"无权访问", 
        "BU":"微信支付出现问题",    
        "BV":"人脸和身份证可能不匹配,请查验",    
        "BW":"手机号码错误, 或者找不到",    
        "BX":"没有小程序code,或者是code错误,导致openID不正确",    
        "BY":"没有小程序openID,或者是生成的openID错误",      
        "BZ":"token错误",    
        "CA":"重复的记录,请检查",    
        "CB":"无此的记录,请检查",    
        "CC":"数据过期,请重新查询",    
        "CD":"只有注册用户可以申请,请先注册",    
        "CF":"手机号,身份证, 姓名不匹配",    
        "CG":"记录添加失败",    
        "CH":"templateID 错误",    
        "CI":"基础服务请求失败",    
        "CU":"记录更新失败",    
        "CV":"记录删除失败",    
        "CS":"短信短时间发送次数太多, 请稍后再发",    
    }
}
    
    
def rtnMSG(CMD,errCode,field = '', lang = "CN"):
    result = {}
    if lang not in CONST_ERROR_wordList:
        lang = "EN"
    wordList = CONST_ERROR_wordList[lang]

    if errCode in wordList:
        word = wordList[errCode]
        if len(word.split('%s')) > 1:
            word = word % (field)
    else:
        word = 'exception. unknow error ID'
    
    result["CMD"] = CMD
    result["MSG"] = {"errCode":str(errCode), "content":word}
    result["KEY"] = CONST_ERROR_KEY
    
    return result
    
    
def getErrMsg(errCode, field ="", lang = "CN"):
    result = ""
    if lang not in CONST_ERROR_wordList:
        lang = "EN"
    wordList = CONST_ERROR_wordList[lang]
    if errCode in wordList:
        word = wordList[errCode]
        if len(word.split('%s')) > 1:
            word = word % (field)
    else:
        word = 'exception. unknow error ID'
    result = word

    return result


#其他系统的消息翻译
TRANS_OTHER_MSG = {
    "EN-CN":{
    "the number of sms messages sent from a single mobile number every day exceeds the upper limit":"向对应号码发送的短信数量超过当日最大数量", 
    }, 
    "CN-EN":{
    },  
    }

def transOtherMsg(msg,  lang):
    result = msg
    if lang == "CN":
        transTag = "EN-CN"
    else:
        transTag = "CN-EN"
    newMsg = TRANS_OTHER_MSG[transTag].get(msg)
    if newMsg:
        result = newMsg
    return result

    
def calTableYMD(beginYMDHM, endYMDHM):
    result = []
    if endYMDHM >= beginYMDHM:
        beginY = int(beginYMDHM[0:4])
        beginM = int(beginYMDHM[4:6])
        endY = int(endYMDHM[0:4])
        endM = int(endYMDHM[4:6])

        for Y in range(beginY,  endY+1):
            if beginY == endY:
                endMonth = endM+1
                for M in range(beginM, endMonth):
                    tableYM = "%04d%02d" % (beginY, M) 
                    result.append(tableYM)
            else:
                if Y == endY:
                    beginMonth = 1
                    endMonth = endM+1
                elif Y == beginY:
                    beginMonth = beginM
                    endMonth = 13
                else:
                    beginMonth = 1
                    endMonth = 13
                for M in range(beginMonth, endMonth):
                    tableYM = "%04d%02d" % (Y, M) 
                    result.append(tableYM)
    return result
        
        
#把相近的两个地理位置数据做个简单迁移,避免显示重叠
def shiftPosition(lat1, lng1, lat2, lng2):
    dataType = misc.isStr(lat1)
    vectorScale = 10000
    newLat1 = float(lat1) * vectorScale
    newLng1 = float(lng1) * vectorScale
    newLat2 = float(lat2) * vectorScale
    newLng2 = float(lng2) * vectorScale
    if (int(newLat1) == int(newLat2)) and (int(newLng1) == int(newLng2)):
        shiftPosition = random.randint(0, 10) 
        newLat2 += shiftPosition
        shiftPosition = random.randint(0, 10) 
        newLng2 += shiftPosition
    if dataType:
        result = str(newLat1/vectorScale), str(newLng1/vectorScale), str(newLat2/vectorScale), str(newLng2/vectorScale)
    else:
        result = (newLat1/vectorScale), (newLng1/vectorScale), (newLat2/vectorScale), (newLng2/vectorScale)
    return result
    
    
#把list数据缩减到要求的长度以内,会根据要求的长度和实际长度,挑选一些值,抛弃一些值, 适合比较平滑的数据
def compressList(dataList, requestLen):
    result = []
    actualLen = len(dataList)
    compressRate = int((actualLen + requestLen -1)/requestLen)
    if (compressRate) >= 2:
        #两倍长度以上,直接压缩
        for i in range(0, actualLen, compressRate):
            result.append(dataList[i])
    else:
        result = dataList
    return result


def genDigest(d1,  d2 = "",  d3 = "",  d4 = "", d5 =""):
    if sys.version_info.major <= 2:
        if isinstance(d1, str) or isinstance(d1, unicode):
            d1 = d1.encode("UTF-8")
        if isinstance(d2, str) or isinstance(d2, unicode):
            d2 = d2.encode("UTF-8")
        if isinstance(d3, str) or isinstance(d3, unicode):
            d3 = d3.encode("UTF-8")
        if isinstance(d4, str) or isinstance(d4, unicode):
            d4 = d4.encode("UTF-8")
        if isinstance(d5, str) or isinstance(d5, unicode):
            d5 = d5.encode("UTF-8")       
    else:
        if isinstance(d1, str) or isinstance(d1, bytes):
            d1 = d1.encode("UTF-8")
        if isinstance(d2, str) or isinstance(d2, bytes):
            d2 = d2.encode("UTF-8")
        if isinstance(d3, str) or isinstance(d3, bytes):
            d3 = d3.encode("UTF-8")
        if isinstance(d4, str) or isinstance(d4, bytes):
            d4 = d4.encode("UTF-8")
        if isinstance(d5, str) or isinstance(d5, bytes):
            d5 = d5.encode("UTF-8")       
  
    tempStr = d1+d2+d3+d4+d5+comGD._DEF_COMM_HASH_KEY_FOR_ALL.encode("UTF-8")
    result = hashlib.md5(tempStr).hexdigest()
    if sys.version_info.major <= 2:
        if isinstance(result, unicode):
            result = result.encode("UTF-8")

    else:
        if isinstance(result, bytes):
            result = result.decode("UTF-8")
    return result 
    
    
#check 身份证信息
def chkPersonalID(data, lang):
    result = {"rtn":True, "msg":"", "data":{}}
    try:
        rtnData = PIDValidator.get_info(data)
        if rtnData == False:
            result["rtn"] = False
            result["msg"] = getErrMsg("ERR_PID", lang = lang)
        else:            
            result["data"]["birthday"] = rtnData.get("birthday_code", "")
            result["data"]["address"] = rtnData.get("address", "")
            result["data"]["length"] = str(rtnData.get("length", 18))
            if rtnData.get("sex") == 1:
                result["data"]["sex"] = "M"
            else:
                result["data"]["sex"] = "F"

    except:
        pass
    return result


#check 姓名
def chkPeronalName(data, lang):
    result = {"rtn":True, "msg":"", "data":{}}
    if len(data) < comGD._DEF_PERSONAL_NAME_MIN_LENGTH:
        result["rtn"] = False
        result["msg"] = getErrMsg("ERR_NAME", lang = lang)        
    return result


#check TEl
def chkTelNo(data, lang):
    result = {"rtn":True, "msg":"", "data":{}}
    if len(data) < comGD._DEF_TEL_NO_MIN_LENGTH:
        result["rtn"] = False
        result["msg"] = getErrMsg("ERR_TEL", lang = lang)        
    return result


#check China mobile phone number
chinaMobilePhoneNoRule = re.compile(r'\(?1\d{2,3}[)-]?\d{7,8}')
def chkChinaMobileNo(data, lang = "EN"):
    result = {"rtn":True, "msg":"", "data":{}}
    m = chinaMobilePhoneNoRule.match(data)
    if m:
        result["rtn"] = True   
    else:
        result["rtn"] = False
        result["msg"] = getErrMsg("ERR_TEL", lang = lang)        
    return result


#check 酒店信息
def chkhotelName(data, lang):
    result = {"rtn":True, "msg":"", "data":{}}
    if len(data) < comGD._DEF_UNIT_NAME_MIN_LENGTH:
        result["rtn"] = False
        result["msg"] = getErrMsg("ERR_HOTELNAME", lang = lang)        
    return result


#check 城市信息
def chkCityName(data, lang):
    result = {"rtn":True, "msg":"", "data":{}}
    return result


#check 区县信息
def chkAreaName(data, lang):
    result = {"rtn":True, "msg":"", "data":{}}
    return result


#check 地址信息
def chkAddrName(data, lang):
    result = {"rtn":True, "msg":"", "data":{}}
    if len(data) < comGD._DEF_ADDR_MIN_LENGTH:
        result["rtn"] = False
        result["msg"] = getErrMsg("ERR_ADDR", lang = lang)        
    return result


#check 完整地址信息
def chkWholeAddr(data, lang):
    result = {"rtn":True, "msg":"", "data":{}}
    return result


#check 邮箱信息
def chkEmailAddr(data, lang):
    result = {"rtn":True, "msg":"", "data":{}}
    #ruleStr=r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
    ruleStr = '[^@]+@[^@]+\.[^@]+'
    if re.match(ruleStr,data):
        result["rtn"] = True
    else:
        result["rtn"] = False
        result["msg"] = getErrMsg("ERR_EMAIL", lang = lang)             
    return result
    

CMDMap = {
    #用户注册
    comGD._DEF_PID_LABEL:chkPersonalID, 
    comGD._DEF_PERSONAL_NAME_LABEL:chkPeronalName, 
    comGD._DEF_TEL_LABEL:chkTelNo, 
    comGD._DEF_CITY_NAME_LABEL:chkCityName, 
    comGD._DEF_AREA_NAME_LABEL:chkAreaName, 
    comGD._DEF_ADDR_NAME_LABEL:chkAddrName, 
    comGD._DEF_WHOLE_ADDR_LABEL:chkWholeAddr, 
    comGD._DEF_EMAIL_LABEL:chkEmailAddr, 
    }


#check 地址,姓名,身份证号等的有消息
def chkDataValidataion(data, dataType, lang = "CN"):
    result = {"rtn":True, "msg":"", "data":{}}
    if dataType in CMDMap:
        result = CMDMap[dataType](data, lang)
    
    return result


def chkPasswd(passwd):
    result = "B0"
    if not passwd:
        result = "B1"
    else:
        chkResult = passwdSchema.validate(passwd)
        if not chkResult:
            result = "B3"
    return result


def chkLoginIDPasswd(loginID, passwd):
    result = "B0"
    if not loginID:
        result = "B1"
    elif len(loginID) <= comGD._DEF_REDIS_USER_ID_LENGTH:
        result = "B2"
    else:
        if not passwd:
            result = "B3"
        else:
            pass
    return result

    
def getProvince(cityName):
    result = ""
    return result

_DEF_DATE_HIST_QRYTYPE_SET = {
"TODAY":1,  #今天的数据
"LAST_DAY":2,  #昨天的数据
"LAST_WEEK":7,  #最近7天
"LAST_MONTH":30, #最近一个月
"GIVEN_DATE":0,  #指定日期的
}


def calQryDays(qryType,  startDate="",  endDate =""):
    result = 1
    givenDate = False
    days = _DEF_DATE_HIST_QRYTYPE_SET.get(qryType, 0)
    if days == 0:
        if len(startDate) >=8 and len(endDate) >=8:
            days = misc.diffDays(startDate, endDate)
            givenDate = True
    if days >= 1:
        result = days
    if givenDate:
        startYMDHMS = startDate
        endYMDHMS = endDate
    else:
        endYMDHMS = misc.getTime()
        minusSeconds = -days *24 * 60 * 60
        startYMDHMS = misc.addTime(endYMDHMS, minusSeconds)
    return result, startYMDHMS, endYMDHMS
    

def calYMD(qryType):
    result = []
    days = _DEF_DATE_HIST_QRYTYPE_SET.get(qryType, 0)
    for i in range(days):
        YMD = misc.getPassday(i)
        result.append(YMD)
    return result


#身份证脱敏处理
def PIDConvertor(personID):
    result = personID
    nLen = len(personID)
    if nLen >=comGD._DEF_PID_ID_MIN_LENGTH and nLen <= comGD._DEF_PID_ID_MAX_LENGTH:
        result = personID[0:12]+"XXXX"+personID[17:]
    return result


#处理搜索问题, 支持and, or, not 和全局搜索
#"searchOption":{"logic":"AND","optionList":[{"province":"\u5c71\u4e1c\u7701"},{"city":"\u6dc4\u535a\u5e02"},{"area":"\u6dc4\u5ddd\u533a"}]}
def handleSearchOption(ruleSet, allowList, dataList):
    result = {"rtn":"B0", "data":[]}
    hitKeyFlag = False
    try:
        rtnData = []
        logic = (ruleSet.get("logic", "")).upper()
        if logic == comGD._DEF_GE_LOGIC_AND:
            optionList = ruleSet.get("optionList", [])
            ruleNum = len(optionList)
            if ruleNum > 0:
                for data in dataList:
                    ruleCount = 0
                    for rule in optionList:
                        for ruleKey, ruleVal in rule.items():
                            if ruleKey in allowList:
                                hitKeyFlag = True
                                dataVal = data.get(ruleKey)
                                if ruleVal in dataVal:
                                    ruleCount += 1
                    if ruleCount == ruleNum:
                        rtnData.append(data)
                result["data"]  = rtnData
            else:
                result["rtn"] = "BK"
        elif logic == comGD._DEF_GE_LOGIC_OR:
            optionList = ruleSet.get("optionList", [])
            ruleNum = len(optionList)
            if ruleNum > 0:
                for data in dataList:
                    ruleCount = 0
                    for rule in optionList:
                        for ruleKey, ruleVal in rule.items():
                            if ruleKey in allowList:
                                hitKeyFlag = True
                                dataVal = data.get(ruleKey)
                                if ruleVal in dataVal:
                                    ruleCount = ruleNum
                                    break
                        if ruleCount == ruleNum:
                            break
                    if ruleCount == ruleNum:
                        rtnData.append(data)
                result["data"]  = rtnData
            else:
                result["rtn"] = "BK"
        elif logic == comGD._DEF_GE_LOGIC_NOT:
            optionList = ruleSet.get("optionList", [])
            ruleNum = len(optionList)
            if ruleNum > 0:
                for data in dataList:
                    ruleCount = 0
                    for rule in optionList:
                        for ruleKey, ruleVal in rule.items():
                            if ruleKey in allowList:
                                hitKeyFlag = True
                                dataVal = data.get(ruleKey)
                                if ruleVal not in dataVal:
                                    ruleCount += 1
                    if ruleCount == ruleNum:
                        rtnData.append(data)
                result["data"]  = rtnData
            else:
                result["rtn"] = "BK"
        elif logic == comGD._DEF_GE_LOGIC_ALL:
            option = ruleSet.get("option", "")
            for data in dataList:
                if option != "":
                    for dataKey,  dataVal in data.items():
                        if dataKey in allowList:
                            hitKeyFlag = True
                            if option in dataVal:
                                rtnData.append(data)
                                break
                else:
                    rtnData.append(data)
                    #result["rtn"] = "BK"
            result["data"]  = rtnData
            
        if hitKeyFlag == False:
            #条件不在allowList
            result["data"]  = dataList
    except:
        result["rtn"] = "BK"
    return result
    
    
#通过地址获取经纬度的接口
baiduMapKey = "mDMczR9BuvbPOOYE9z3i5iNfQVQLcOd6"
def getLocation(city,  address):
    url = "https://api.map.baidu.com/geocoder"
    dataSet = {}
    dataSet["address"] = address
    dataSet["output"] = "json"
    dataSet["key"] = baiduMapKey
    dataSet["city"] = city    
    r = requests.get(url, params = dataSet)
    if r.status_code == 200:
        try:
            rtnSet = r.json()
        except:
            rtnSet = {}
    result = rtnSet.get("result")
    try:
        result["location"]["lng"] = str(result["location"]["lng"])
        result["location"]["lat"] = str(result["location"]["lat"])
        result["map"] = "baidu"
    except:
        result = {}
    return result


#省市区分割
provinceLevelData = [
u"北京市", 
u"天津市", 
u"上海市", 
u"重庆市", 
u"黑龙江省", 
u"吉林省",
u"辽宁省", 
u"河北省", 
u"河南省", 
u"山东省", 
u"江苏省", 
u"安徽省", 
u"江西省", 
u"浙江省", 
u"福建省", 
u"广东省", 
u"广西省", 
u"海南省", 
u"湖北省", 
u"湖南省", 
u"山西省", 
u"陕西省", 
u"四川省", 
u"贵州省", 
u"云南省", 
u"甘肃省", 
u"青海省", 
u"内蒙古", 
u"宁夏", 
u"新疆", 
u"西藏", 
u"香港", 
u"澳门", 
u"台湾省", 
]

areaSuffixData = [u"区", u"市", u"盟", u"县", u"州"]
specificProvinceList = [u"北京市", u"天津市", "上海市", u"重庆市", u"香港", u"澳门", u"台湾省", u"海南省"]
def PCASplit(pca):
    foundFlag = False
#    if isinstance(pca, unicode):
#        pca = pca.encode("UTF-8")
    for provinceName in provinceLevelData:
        pos = pca.find(provinceName)
        if pos == 0:
            newStart = pos + len(provinceName)
            for areaSuffix in areaSuffixData:
                newPos = pca[newStart:].find(areaSuffix)
                areaName = pca[newStart:newPos+1]
                cityName = pca[newPos+1:]
#                if provinceName not in specificProvinceList:
#                    areaName = pca[newStart:newPos+1]
#                    cityName = pca[newPos+1:]
#                else:
#                    areaName = pca[newPos+1:]
#                    cityName = ""
                foundFlag = True
                break
            if foundFlag:
                break
    result = {}
    result["provinceName"] = provinceName
    result["areaName"] = areaName
    result["cityName"] = cityName
    return result
        
        
provinceCityData = {
"normal":{
    "北京市":{"北京市":"北京城区"},
    "天津市":{"天津市":"天津城区"}, 
    "上海市":{"上海市":"上海城区"}, 
    "重庆市":{"重庆市":"市辖区"}, 
}, 

"reverse":{
    "北京市":{"北京城区":"北京市"},
    "天津市":{"天津城区":"天津市"}, 
    "上海市":{"上海城区":"上海市"}, 
    "重庆市":{"市辖区":"重庆市"}, 
    }, 
}


def miniProvinceConvert(province, city,  model = "normal"):
    newCity = city
    if sys.version_info.major <= 2:
        if isinstance(province, unicode):
            province = province.encode("UTF-8")
        if isinstance(city, unicode):
            city = city.encode("UTF-8")
    else:
        if isinstance(province, bytes):
            pass
            province = province.decode("UTF-8")
        if isinstance(city, bytes):
            pass
            city = city.decode("UTF-8")
        
    if model == "normal":
        convertDataSet = provinceCityData["normal"]
    else:
        convertDataSet = provinceCityData["reverse"]
    if province in convertDataSet:
        if city in convertDataSet[province]:
            newCity = convertDataSet[province][city]
        
    return  newCity
  
  
#比较权限大小, 如果roleName权限比targetRoleName权限小, 返回 False, 否则返回True
def chkSetRoleRight(roleName, targetRoleName):
    result = False
    roleValueSet = settings.ROLE_RIGHT_SET
    roleVal = roleValueSet.get(roleName, 1000)
    targetRoleVal = roleValueSet.get(targetRoleName,1000)
    if targetRoleVal:
        if roleName in settings.ROLE_RIGHT_SET:
            if roleVal <= targetRoleVal:
                result = True
            if targetRoleName == "administrator":
                result = False
        else:
            if targetRoleName not in settings.ROLE_RIGHT_SET:
                if roleVal <= targetRoleVal:
                    result = True            
    return result
    
    
def chkIsRegisterUser(roleName):
    result = False
    if roleName in ["customer","householder","chief","operator", "manager", "administrator"]:
        result = True
    return result
    
    
def chkIsOperator(roleName):
    result = False
    if roleName in ["administrator", "manager", "operator"]:
        result = True
    return result


def chkIsManager(roleName):
    result = False
    if roleName in ["administrator", "manager"]:
        result = True
    return result
    
    
def chkIsChiefOrOpertor(roleName):
    result = False
    if roleName in ["administrator", "manager", "operator", "chief"]:
        result = True
    return result
    

def getExpireTime(roleName):
    result = comGD._DEF_OPERATOR_SESSION_EXPIRE_TIME
    if roleName in ["owner"]:
        result = comGD._DEF_USER_SESSION_EXPIRE_TIME
    return result
        

#文件系统请求方式        
def fileServerRequest(serverName, dataSet):
    result = {}
    url = settings.FILE_SERVER_URL.get(serverName)
    header = {"content-type":"application/json"}
    payload = misc.jsonDumps(dataSet)
    r = requests.post(url, data=payload, headers = header) 
    if r.status_code == requests.codes.ok:
        result =misc.jsonLoads(r.text)
        
    return result
    

def getRandomList(listNum,  maxNum):
    result = []
    selectList = []
    count = 0
    num = 0 
    if maxNum > 1:
        while True:
            nT1 = random.randint(0, maxNum-1)
            if nT1 not in selectList:
                selectList.append(nT1) #随机内容
                num += 1
            count += 1
            if (num >= listNum) or (count > (listNum *10)):
                break
    elif maxNum == 1:
        selectList = [0]
    result = selectList
    return result
    

def convertRandomList(dataList):
    result = []
    nLen = len(dataList)
    selectList = getRandomList(nLen, nLen)
    for i in selectList:
        result.append(dataList[i])
    return result 
    
    
def getRaddomDrop(molecules ,  denominators):
    result = True
    nT1 = random.randint(0, denominators)
    if nT1 <= molecules: #随机抛弃1/4内容
        result = True
    else:
        result = False
    return result
    
    
#把一个经纬度中心和范围(公里)转换为一个矩形经纬度区域, 简单换算, 
GPS_BJ_CENTER_LNG = 116.398
GPS_BJ_CENTER_LAT = 39.910
GPS_DEFAULT_DISTANCE = 300
GPS_KM_LNG_LAT= 111 #在经线上，纬度每差1度,实地距离大约为111千米抄；在纬线上，经度每差1度,实际距离为111×cosθ千米
def calcPositionRange(dataSet):
    result = {}
    lng = float(dataSet.get("lng", GPS_BJ_CENTER_LNG))
    lat = float(dataSet.get("lat", GPS_BJ_CENTER_LAT))
    distance = float(dataSet.get("distance", GPS_DEFAULT_DISTANCE))
    KMPerLAT =  GPS_KM_LNG_LAT
    KMPerLNG = GPS_KM_LNG_LAT * math.cos(math.radians(lat))
    distLat = abs(distance/KMPerLAT)
    distLng = abs(distance/KMPerLNG)
    result["leftTopLat"] = lat + distLat
    result["leftTopLng"] = lng - distLng
    result["rightBottomLat"] = lat - distLat
    result["rightBottomLng"] = lng + distLng
    return result
  

#生成临时文件名
def genTempFileName(extName = ""):
    result = ""
    tempDir = os.path.join("/data/webserver/temp",  "output")
    while True:
        uuidName = str(uuid.uuid4()).replace("-","") + extName
        tempFileName = os.path.join(tempDir, uuidName)
        if os.path.exists(tempFileName) == False:
            result = tempFileName
            break
    return result
    
    
def downloadFile(url,  fileName):
    result = 0
    r = requests.get(url)
    if r.status_code == 200:
        try:
            with open(fileName, "wb") as hFile:
                hFile.write(r.content)
            result = os.path.getsize(fileName)
        except:
            pass
    return result
    
    
def sendFile(filePath, description = "file"):
    result = {}
    
    url = settings.FILE_UPLOAD_URL
    try:
        #fileName = os.path.basename(filePath)

        multipart_form_data = {
            'file': (filePath, open(filePath, 'rb')),
            'description': ('', str(description)),
        }
        
        r = requests.post(url, files=multipart_form_data)
        if r.status_code == requests.codes.ok:
            rtnData = misc.jsonLoads(r.text)
        
            result = rtnData
        
    except Exception as e:
        pass

    return result


def currencyConvert(currency):
    result = {}
    if currency not in comGD._DEF_CURRENCY_UNITS:
        currency = comGD._DEF_CURRENCY_DEFAULT
    result["unit"] = comGD._DEF_CURRENCY_UNITS[currency]["unit"]
    result["rate"] = comGD._DEF_CURRENCY_UNITS[currency]["rate"]
    return result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pass
        import platform
        if platform.system()=='Linux':
            import pdb
            pdb.set_trace()
    rtnSet = currencyConvert("CNY")
    tempFileName = genTempFileName(".txt")
    

