#! /usr/bin/env python3
#encoding: utf-8

#Filename: yihaifenghuaSMS.py
#Author: Steven Lian's team
#E-mail:  steven.lian@gmail.com  
#Date: 2023-11-03
#Description:   杭州燚海峰华通信技术有限公司, 短信接口
#请参考 SMS_HTTP_1.5-6d117473.pdf

_VERSION="20231104"

_DEBUG=True

import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
if sys.getdefaultencoding() != 'utf-8':
    pass
    #reload(sys)
    #sys.setdefaultencoding('utf-8')

import requests
import hashlib
# import base64
import traceback

#common functions(log,time,string, json etc)
from common import miscCommon as misc

#setting files
from config import yihaifenghuaSettings as settings

_processorPID = os.getpid()

_DEBUG =  settings._DEBUG
# command part

SMS_ERR_MSG = {
    0:"处理成功",
    1:"帐号名为空",
    2:"帐号名或密码鉴权错误",
    3:"帐号已被锁定",
    4:"此帐号业务未开通",
    5:"帐号余额不足",
    6:"缺少发送号码",
    7:"超过最大发送号码数",
    8:"发送消息内容为空",
    9:"无效的 RCS 模板 ID",
    10:"非法的 IP 地址，提交来源 IP 地址与帐号绑定 IP 不一致",
    11:"24 小时发送时间段限制",
    12:"定时发送时间错误或超过 15 天",
    13:"请求过于频繁，每次获取数据最小间隔为 30 秒",
    14:"错误的用户扩展码",
    16:"时间戳差异过大，与系统时间误差不得超过 5 分钟",
    18:"帐号未进行实名认证",
    19:"帐号未开放回执状态",
    22:"缺少必填参数",
    23:"用户帐号名重复",
    24:"用户无签名限制",
    25:"签名需要包含【】符",
    50:"缺少模板标题",
    51:"缺少模板内容",
    52:"模板内容不全",
    53:"不支持的模板帧类型",
    54:"不支持的文件类型",
    97:"此链接不支持 GET 请求",
    98:"HTTP Content-Type 错误, 请设置 Content-Type: application/json",
    99:"错误的请求 JSON 字符串",
    500:"系统异常",
}

accountUserName = settings.SMS_SERVICE["userName"]
accountPasswd = settings.SMS_SERVICE["password"]
accountPasswdMD5 = hashlib.md5(accountPasswd.encode('utf-8')).hexdigest()

defaultSignName = settings.SMS_SERVICE["signName"]
formatString = settings.SMS_SERVICE["format"]

infoSignName = settings.SMS_SERVICE["infoSignName"]
infoFormatString = settings.SMS_SERVICE["infoFormat"]


#计算sign
#多个指定参数值组合成字符串后计算 MD5 32 位小写结果
#要求：MD5(userName + timestamp + MD5(password))
def calSign(timeStamp):
    strString = accountUserName + str(timeStamp) + accountPasswdMD5
    sign =  hashlib.md5(strString.encode('utf-8')).hexdigest()
    return sign


def sendSMS(phoneNum, content=""):
    result = {}
    try:
        fullSignName = "【" + defaultSignName + "】"  + " " 
        realContent = formatString.format(content)
        fullContent = fullSignName + realContent
        result = sendSMSOne(phoneNum,fullContent)        
    except:
        pass
        
    return result
    

def infoSMS(phoneNum, user,content):
    result = {}
    try:
        fullSignName = "【" + defaultSignName + "】"  + " " 
        realContent = infoFormatString.format(user,content)
        fullContent = fullSignName + realContent
        result = sendSMSOne(phoneNum,fullContent)
    except:
        pass
        
    return result


def customeSMS(phoneNum, content):
    result = {}
    try:
        fullSignName = "【" + defaultSignName + "】"  + " " 
        fullContent = fullSignName + content
        result = sendSMSOne(phoneNum,fullContent)
    except:
        pass
        
    return result
    

#短信一对一发送接口
def sendSMSOne(phone,msg,sendTime=""):
    result = {}

    header = {"content-type":"application/json;charset=utf-8"}
    currTimeStamp = int(misc.time.time() * 1000)

    requestData = {}
    
    requestData["userName"]  = accountUserName
    requestData["timestamp"]  = currTimeStamp
    requestData["sign"]  = calSign(currTimeStamp)

    sendData = {}
    sendData["phone"] = phone
    sendData["content"] = msg
    if sendTime:
        sendData["sendTime"] = sendTime

    requestData["messageList"]  = [sendData]
    
    try:
        payload = misc.jsonDumps(requestData)
        url = settings.sendSMSUrl
        r = requests.post(url, data = payload, headers = header)
        if r.status_code == 200:
            rtnData = misc.jsonLoads(r.text)
            rtnCode = rtnData.get("code") 
            if rtnCode == 0: 
                result["data"] = rtnData.get("data",[]) 
                result["smsCount"] = rtnData.get("smsCount",0) 
                result["Code"] = "OK" #兼容aliyun/tencent
            result["rtn"] = rtnCode
            result["message"] = rtnData.get("message") 

    except Exception as e:
        errMsg = f"PID: {_processorPID},errMsg:{str(e)},{traceback.format_exc()}"
        # _LOG.error(f"{errMsg}, {traceback.format_exc()}")

    return result


#查询余额
def getBalance():
    result = {}

    header = {"content-type":"application/json;charset=utf-8"}
    currTimeStamp = int(misc.time.time() * 1000)

    requestData = {}
    
    requestData["userName"]  = accountUserName
    requestData["timestamp"]  = currTimeStamp
    requestData["sign"]  = calSign(currTimeStamp)
    
    try:
        payload = misc.jsonDumps(requestData)
        url = settings.balanceUrl
        r = requests.post(url, data = payload, headers = header)
        if r.status_code == 200:
            rtnData = misc.jsonLoads(r.text)
            rtnCode = rtnData.get("code") 
            if rtnCode == 0: 
                result["balance"] = rtnData.get("balance",0) 
            result["rtn"] = rtnCode
            result["message"] = rtnData.get("message") 

    except Exception as e:
        errMsg = f"PID: {_processorPID},errMsg:{str(e)},{traceback.format_exc()}"
        # _LOG.error(f"{errMsg}, {traceback.format_exc()}")

    return result


#报备签名接口
def addSignature(signName):
    result = {}

    header = {"content-type":"application/json;charset=utf-8"}
    currTimeStamp = int(misc.time.time() * 1000)

    requestData = {}
    
    requestData["userName"]  = accountUserName
    requestData["timestamp"]  = currTimeStamp
    requestData["sign"]  = calSign(currTimeStamp)

    fullSignName = "【" + signName + "】"
    requestData["signatureList"]  = [fullSignName]

    try:
        payload = misc.jsonDumps(requestData)
        url = settings.querySignatureUrl
        r = requests.post(url, data = payload, headers = header)
        if r.status_code == 200:
            rtnData = misc.jsonLoads(r.text)
            rtnCode = rtnData.get("code") 
            if rtnCode == 0 or rtnCode == 24: 
                pass
            result["rtn"] = rtnCode
            result["message"] = rtnData.get("message") 

    except Exception as e:
        errMsg = f"PID: {_processorPID},errMsg:{str(e)},{traceback.format_exc()}"
        # _LOG.error(f"{errMsg}, {traceback.format_exc()}")

    return result


#查询签名接口
def querySignature():
    result = {}

    header = {"content-type":"application/json;charset=utf-8"}
    currTimeStamp = int(misc.time.time() * 1000)

    requestData = {}
    
    requestData["userName"]  = accountUserName
    requestData["timestamp"]  = currTimeStamp
    requestData["sign"]  = calSign(currTimeStamp)
    
    try:
        payload = misc.jsonDumps(requestData)
        url = settings.querySignatureUrl
        r = requests.post(url, data = payload, headers = header)
        if r.status_code == 200:
            rtnData = misc.jsonLoads(r.text)
            rtnCode = rtnData.get("code") 
            if rtnCode == 0 or rtnCode == 24: 
                result["data"] = rtnData.get("data",[]) 
            result["rtn"] = rtnCode
            result["message"] = rtnData.get("message") 

    except Exception as e:
        errMsg = f"PID: {_processorPID},errMsg:{str(e)},{traceback.format_exc()}"
        # _LOG.error(f"{errMsg}, {traceback.format_exc()}")

    return result


def testSign():
    timeStamp = "1596254400000"
    accountUserName = "test"
    accountPasswd = "123"
    passwdMD5 = hashlib.md5(accountPasswd.encode('utf-8')).hexdigest()
    strString = accountUserName + timeStamp + passwdMD5
    sign =  hashlib.md5(strString.encode('utf-8')).hexdigest()
    print(sign)


def test():
    # testSign()

    # getBalance()
    signName = "移动与远程医疗器械揭榜挂帅"
    addSignature(signName)

    querySignature()


def main():
    # test()
    # sendSMS("13910710766", "123345")
    # sendSMS("13911518328", "123345")
    sendSMS("18910026100", "123345")
    
    customeSMS("13910710766", "当前链路告警级别是[红色]")
    customeSMS("13910710766", "当前用户13910710766角色改为[管理员]")
    

if __name__ == "__main__":
    main()



