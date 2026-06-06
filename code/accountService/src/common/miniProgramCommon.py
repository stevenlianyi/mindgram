#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Filename: miniProgramCommon.py  
#Author: Steven Lian
#E-mail: steven.lian@gmail.com  
#Date: 2019-09-03
#Description:   微信小程序(miniProgram) 和web 端扫码登录interface 

_VERSION="20230814"

import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
if sys.getdefaultencoding() != 'utf-8':
    pass
    #reload(sys)
    #sys.setdefaultencoding('utf-8')

import traceback

import time
import hashlib
import hmac

import requests

from lxml import etree

#import numpy as np

#global defintion/common var etc.
#from common import globalDefinition as comGD

#code/decode functions
#from common import codingDecoding as comCD

#common functions(log,time,string, json etc)
from common import miscCommon as misc

from config import accountMiniProgramSettings as settings

_DEBUG = settings._DEBUG
#_DEBUG = False

if _DEBUG:
    logfilepath = os.path.join(parentdir,r"..\log")
    #_LOG = misc.setLogNew("MINI", "miniprogramlog",logfilepath)
    _LOG = misc.setLogNew("MINI", "miniprogramlog")
    systemVersion = str(sys.version_info.major) + "." + str(sys.version_info.minor ) + "." + str(sys.version_info.micro )
    _LOG.info("python version:{0}, code version:{1}, _DEBUG:{2}".format(systemVersion, _VERSION, _DEBUG))
    
#小程序登录  
miniAppID = settings.miniAppID
miniAppSecret = settings.miniAppSecret

miniGrantType = settings.miniGrantType
miniServerURL = settings.miniServerURL
miniMchID = settings.miniMch_id
miniAppKey= settings.miniAppKey
miniFeeType = settings.miniFeeType
miniBodyText = settings.miniBodyText
miniDetails = settings.miniDetails

#小程序支付
miniLocapIP = settings.miniLocapIP
miniNotifyUrl = settings.miniNotifyUrl
miniTradeType = settings.miniTradeType
miniUnifiedOrderURL = settings.miniUnifiedOrderURL

miniAppIDChief = settings.miniAppIDChief
miniAppSecretChief = settings.miniAppSecretChief

miniServerRootCAFilePath = settings.miniServerRootCAFilePath
miniAPIClientCertFilePath = settings.miniAPIClientCertFilePath
miniAPIClientKeyFilePath = settings.miniAPIClientKeyFilePath

miniRefundURL = settings.miniRefundURL

#web扫码登录等
webAppID = settings.webAppID
webAppSecret = settings.webAppSecret
webServerURL = settings.webServerURL
webRefreshURL = settings.webRefreshURL
webVerifyURL = settings.webVerifyURL
webUserInfoURL = settings.webUserInfoURL
webGrantType = settings.webGrantType


_DEF_USER_SEX_FEMALE = "F" #性别 女
_DEF_USER_SEX_MALE = "M" #性别 男

#获取openID
def getOpenID(code, appType=""):
    result = {}
    payload = {}
    if appType == "chief":
        payload["appid"] = miniAppIDChief
        payload["secret"] = miniAppSecretChief
    else:
        payload["appid"] = miniAppID
        payload["secret"] = miniAppSecret

    if _DEBUG:
        _LOG.info("DEBUG: appType:[{}],code:[{}],appid:[{}] secret:[{}]".format(appType, code,  payload["appid"], payload["secret"])) 
        
    payload["js_code"] = code
    payload["grant_type"] = miniGrantType

    try:
    
        r = requests.get(miniServerURL, params = payload)
        if r.status_code == 200:
            rtnData = misc.jsonLoads(r.text)
            result["openID"] = rtnData.get("openid", "")        
            result["unionID"] = rtnData.get("unionid", "")        
            result["sessionKey"] = rtnData.get("session_key", "") 
            if _DEBUG:
                _LOG.info("DEBUG: %s %s" % (misc.jsonDumps(rtnData), misc.jsonDumps(result))) 
        
    except Exception as e:
        pass
        errMsg = ""
        _LOG.error("{}, {}, {}".format(errMsg, traceback.format_exc(), str(e)))      
    
    return result


#如果有unionID就使用unionID, 否则使用openID
def getWechatUniqueID(openID,unionID):
    if unionID:
        result = unionID
    else:
        result = openID
    return result


def calSignString(dataSet, weixinKey, model="MD5"):
    result = ""
    keysList = sorted(dataSet.keys())
    aList = []
    for key in keysList:
        val = dataSet.get(key)
        aList.append(key)
        aList.append("=")
        if sys.version_info.major <= 2:
            if isinstance(val, unicode):
                val = val.encode("UTF-8")
        else:
            if isinstance(val, bytes):
                val = val.decode("UTF-8")     
        aList.append(val)
        aList.append("&")
    aList.append("key")
    aList.append("=")
    aList.append(weixinKey)
    tempStr = "".join(aList)
    if sys.version_info.major >= 3:
        if isinstance(tempStr, str):
            tempStr = tempStr.encode("UTF-8")     

    if model == "MD5":
        result = hashlib.md5(tempStr).hexdigest().upper()
    else:
        myhmac  = hmac.new(weixinKey, digestmod=hashlib.sha256)
        myhmac.update(tempStr)
        result = myhmac.hexdigest().upper()
           
    return result


def xmlGenerator(dataSet):
    xmlString = ""
    keysList = sorted(dataSet.keys())
    aList = []
    aList.append("<xml>")
    for key in keysList:
        val = dataSet.get(key)
        if sys.version_info.major >= 3:
            if isinstance(val,  bytes):
                val =  str(val)[2:-1]     
        tempStr = "<{0}>{1}</{0}>".format(key, val)
        aList.append(tempStr)
    aList.append("</xml>")
    xmlString = "\n".join(aList)
    return xmlString
    
    
def xmlDecoder(xmlData):
    result = {}

    if isinstance(xmlData, bytes):
        xmlData = xmlData.decode("UTF-8")        
    root = etree.fromstring(xmlData)
    for child in root.getchildren():
        if child.tag not in result:
            text = ""
            if child.text:
                text = child.text
            result[child.tag] = text
    return result
    

#微信支付, 统一订单接口 
def unifiedOrder(dataSet):
    result = {}
    newSet = {}
    newSet["appid"] = miniAppID
    newSet["mch_id"] = miniMchID
    newSet["openid"] = dataSet.get("openID","web")
    newSet["device_info"] = newSet["openid"]
    currTime = misc.getTime()
    if sys.version_info.major >= 3:
        currTime = currTime.encode()
    newSet["nonce_str"] = hashlib.md5(currTime).hexdigest()[0:32]
    newSet["body"] = miniBodyText
    newSet["detail"] = miniDetails
#    newSet["attach"] = miniDetails
    newSet["out_trade_no"] = dataSet.get("tradeNo")
    newSet["fee_type"] = miniFeeType
    newSet["total_fee"] = dataSet.get("total_fee")
    newSet["spbill_create_ip"] = miniLocapIP
    newSet["time_start"] = misc.getTime()
    newSet["time_expire"] = misc.addTime(newSet["time_start"], 300)
    newSet["notify_url"] = miniNotifyUrl
    newSet["trade_type"] = miniTradeType
#    newSet["sign_type"] = "HMAC-SHA256"
    
    sign = calSignString(newSet, miniAppKey)
    newSet["sign"] = sign
    xmlData = xmlGenerator(newSet)
    
    #发起微信支付统一下单API
    try:
        header = {"content-type":"application/xml;charset=utf-8"}
        if sys.version_info.major >= 3:
            payload = xmlData.encode("UTF-8")
        else:
            payload = xmlData
        if _DEBUG:
            _LOG.info("DEBUG S: newSet:{0}, xmlData:{1}".format(str(newSet), payload))
        
        r = requests.post(miniUnifiedOrderURL, data = payload, headers = header)
        if r.status_code == 200:
            r.encoding = "utf-8"
            rtnData = xmlDecoder(r.text)
            return_code = rtnData.get("return_code", "")        
            return_msg = rtnData.get("return_msg", "") 
            if _DEBUG:
                _LOG.info("DEBUG R:r.text:{0}, rtnData:{1}".format(r.text, misc.jsonDumps(rtnData)))

            paySet = {}

            if return_code == "SUCCESS":
                result_code = rtnData.get("result_code", "")
                if result_code == "SUCCESS":
                    #success, 注意下面这些大小写不要动
                    prepay_id = rtnData.get("prepay_id")
                    paySet["appId"] = miniAppID
                    paySet["timeStamp"] = str(int(time.time()))
                    currTime = misc.getTime()
                    if sys.version_info.major >= 3:
                        currTime = currTime.encode()
                    paySet["nonceStr"] = hashlib.md5(currTime).hexdigest()[0:32]
                    paySet["package"] = "prepay_id={0}".format(prepay_id)
                    paySet["signType"] = "MD5"
                    
                    paySign = calSignString(paySet, miniAppKey)
                    
                    paySet.pop("appId")
                    paySet["paySign"] = paySign
                    paySet["rtn"] = return_code
                else:
                    err_code_des = rtnData.get("err_code_des", "")
                    paySet["rtn"] = return_code
                    paySet["result_code"] = result_code
                    paySet["return_msg"] = return_msg
                    paySet["err_code_des"] = err_code_des
                
            else:
                
                paySet["rtn"] = return_code
                paySet["MSG"] = return_msg
                
            result = paySet
            
            if _DEBUG:
                _LOG.info("DEBUG: {} {}".format(misc.jsonDumps(rtnData), misc.jsonDumps(result))) 
        
    except Exception as e:
        pass
        errMsg = ""
        _LOG.error("{}, {}, {}".format(errMsg, traceback.format_exc(), str(e)))      

    return result


#微信支付, 退款接口
def weixinRefund(dataSet):
    result = {}
    newSet = {}
    newSet["appid"] = miniAppID  #小程序ID
    newSet["mch_id"] = miniMchID #商户号
    currTime = misc.getTime()
    if sys.version_info.major >= 3:
        currTime = currTime.encode()
    newSet["nonce_str"] = hashlib.md5(currTime).hexdigest()[0:32]  #随机字符串
    newSet["transaction_id"] = dataSet.get("transactionID","")  #微信支付订单号
    newSet["out_trade_no"] = dataSet.get("tradeNo","")  #商户订单号
    newSet["out_refund_no"] = dataSet.get("refundNo","")  #商户退款单号
    newSet["total_fee"] = dataSet.get("total_fee") #订单金额
    newSet["refund_fee_type"] = miniFeeType #货币种类
    newSet["refund_fee"] = dataSet.get("refund_fee") #退款金额
    newSet["refund_desc"] = dataSet.get("refundReason") #退款原因
    newSet["notify_url"] = miniNotifyUrl #退款结果通知url
    #newSet["signType"] = "MD5"
    
    sign = calSignString(newSet, miniAppKey)
    newSet["sign"] = sign #签名
    xmlData = xmlGenerator(newSet)
    
    #发起微信支付退款API
    try:
        header = {"content-type":"application/xml;charset=utf-8"}
        if sys.version_info.major >= 3:
            payload = xmlData.encode("UTF-8")
        else:
            payload = xmlData
        _LOG.info("DEBUG S: newSet:{0}, xmlData:{1}".format(str(newSet), payload))

        r = requests.post(miniRefundURL, data = payload, headers = header, cert = (miniAPIClientCertFilePath, miniAPIClientKeyFilePath))
        if r.status_code == 200:
            r.encoding = "utf-8"
            rtnData = xmlDecoder(r.text)
            return_code = rtnData.get("return_code", "")        
            return_msg = rtnData.get("return_msg", "") 
            _LOG.info("DEBUG R: r.text:{0}, rtnData:{1}".format(r.text, misc.jsonDumps(rtnData)))

            paySet = {}

            if return_code == "SUCCESS":
                result_code = rtnData.get("result_code", "")
                if result_code == "SUCCESS":
                    #success, 注意下面这些大小写不要动
                    paySet["appId"] = miniAppID
                    paySet["rtn"] = return_code
                else:
                    err_code_des = rtnData.get("err_code_des", "")
                    err_code = rtnData.get("err_code", "")
                    paySet["rtn"] = return_code
                    paySet["result_code"] = result_code
                    paySet["return_msg"] = return_msg
                    paySet["err_code_des"] = err_code_des
                    paySet["err_code"] = err_code
                
            else:
                
                paySet["rtn"] = return_code
                paySet["MSG"] = return_msg
                
            result = paySet
            
            if _DEBUG:
                _LOG.info("DEBUG: {} {}".format(misc.jsonDumps(rtnData), misc.jsonDumps(result))) 
        
    except Exception as e:
        pass
        errMsg = ""
        _LOG.error("{}, {}, {}".format(errMsg, traceback.format_exc(), str(e)))   
    
    return result
    

#扫码登录 we获取web openID 
def getWebOpenID(code):
    result = {}
    payload = {}
    payload["appid"] = webAppID
    payload["secret"] = webAppSecret

    if _DEBUG:
        _LOG.info("DEBUG: code:[%s],appid:[%s] secret:[%s]" % (code,  payload["appid"], payload["secret"])) 
        
    payload["code"] = code
    payload["grant_type"] = webGrantType

    try:
    
        r = requests.get(webServerURL, params = payload)
        if r.status_code == 200:
            rtnData = misc.jsonLoads(r.text)
            if "openid" in rtnData:
                result["accessToken"] = rtnData.get("access_token", "")        
                result["expiresIn"] = rtnData.get("expires_in", 7200)        
                result["refreshToken"] = rtnData.get("refresh_token", "")    
                result["openID"] = rtnData.get("openid", "") 
                result["scope"] = rtnData.get("scope", "") 
                result["unionID"] = rtnData.get("unionid", "") 
                if _DEBUG:
                    _LOG.info("DEBUG: {}, {}".format(misc.jsonDumps(rtnData), misc.jsonDumps(result))) 
            else:
                _LOG.warning("DEBUG: {}".format(misc.jsonDumps(rtnData))) 


    except Exception as e:
        pass
        if _DEBUG:
            errMsg = ""
            _LOG.error("{}, {}, {}".format(errMsg, traceback.format_exc(), str(e)))  
    
    return result


#扫码登录 web access token 刷新
def webRefreshToken(refreshToken):
    result = {}
    payload = {}
    payload["appid"] = webAppID

    if _DEBUG:
        _LOG.info("DEBUG: code:[{}],appid:[{}] secret:[{}]".format(code,  payload["appid"], payload["secret"])) 
        
    payload["refresh_token"] = refreshToken
    payload["grant_type"] = "refresh_token"

    try:
    
        r = requests.get(webRefreshURL, params = payload)
        if r.status_code == 200:
            rtnData = misc.jsonLoads(r.text)
            if "openid" in rtnData:
                result["accessToken"] = rtnData.get("access_token", "")        
                result["expiresIn"] = rtnData.get("expires_in", 7200)        
                result["refreshToken"] = rtnData.get("refresh_token", "")    
                result["openID"] = rtnData.get("openid", "") 
                result["scope"] = rtnData.get("scope", "") 
                if _DEBUG:
                    _LOG.info("DEBUG: {}, {}".format(misc.jsonDumps(rtnData), misc.jsonDumps(result))) 
            else:
                _LOG.warning("DEBUG: {}".format(misc.jsonDumps(rtnData))) 

    except Exception as e:
        pass
        if _DEBUG:
            errMsg = ""
            _LOG.error("{}, {}, {}".format(errMsg, traceback.format_exc(), str(e)))  
    
    return result


#扫码登录 web access token 验证
def webVerifyToken(accessToken,openID):
    result = {}
    payload = {}
    payload["access_token"] = accessToken
    payload["openid"] = openID

    if _DEBUG:
        _LOG.info("DEBUG: openID:[{}],accessToken:[{}]".format(openID,  accessToken)) 

    try:
    
        r = requests.get(webVerifyURL, params = payload)
        if r.status_code == 200:
            rtnData = misc.jsonLoads(r.text)
            errCode = rtnData.get("errcode")
            result["errCode"] = errCode      
            result["errMsg"] = rtnData.get("errmsg", "")    
            if _DEBUG:
                _LOG.info("DEBUG: {}, {}".format(misc.jsonDumps(rtnData), misc.jsonDumps(result))) 

    except Exception as e:
        pass
        if _DEBUG:
            errMsg = ""
            _LOG.error("{}, {}, {}".format(errMsg, traceback.format_exc(), str(e)))  
        
    return result


#扫码登录 web access token 验证
def webUserInfo(accessToken,openID):
    result = {}
    payload = {}
    payload["access_token"] = accessToken
    payload["openid"] = openID

    if _DEBUG:
        _LOG.info("DEBUG: webUserInfo openID:[{}],accessToken:[{}]".format(openID,  accessToken)) 

    try:
    
        r = requests.get(webUserInfoURL, params = payload)
        if r.status_code == 200:
            r.encoding = "utf-8"
            if _DEBUG:
                _LOG.info("DEBUG: webUserInfo r.text:[{}]".format(r.text)) 
            rtnData = misc.jsonLoads(r.text)
            if "openid" in rtnData:
                result["openID"] = rtnData.get("openid", "")    
                
                nickName = rtnData.get("nickname", "") 
                result["nickName"] = nickName 

                if rtnData.get("sex") == 1:
                    result["sex"] = _DEF_USER_SEX_MALE 
                else:
                    result["sex"] = _DEF_USER_SEX_FEMALE 

                result["countryID"] = rtnData.get("country", "")    
                result["province"] = rtnData.get("province", "")    
                result["city"] = rtnData.get("city", "")    
                result["avatarID"] = rtnData.get("headimgurl", "")    
                result["privilege"] = rtnData.get("privilege", "")    
                result["unionID"] = rtnData.get("unionid", "")   

                if _DEBUG:
                    _LOG.info("DEBUG: webUserInfo {}, {}".format(misc.jsonDumps(rtnData), result)) 
            else:
                _LOG.warning("DEBUG: webUserInfo {}".format(misc.jsonDumps(rtnData))) 

    except Exception as e:
        pass
        if _DEBUG:
            errMsg = ""
            _LOG.error("{}, {}, {}".format(errMsg, traceback.format_exc(), str(e)))  
    
    return result

#扫码登录 end


#获取access token begin
'''
access_token是公众号的全局唯一接口调用凭据，公众号调用各接口时都需使用access_token。
开发者需要进行妥善保存。access_token的存储至少要保留512个字符空间。
access_token的有效期目前为2个小时，需定时刷新，重复获取将导致上次获取的access_token失效。

https请求方式: 
GET https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
'''
def getAccessToken():
    result = {}
    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}".format(miniAppID, miniAppSecret)

    try:

        r = requests.get(url)
        if r.status_code == 200:
            rtnData = misc.jsonLoads(r.text)
            accessToken = rtnData.get("access_token")
            expireInSeconds = rtnData.get("expires_in")
            if accessToken:
                result = {"accessToken": accessToken, "expireInSeconds": expireInSeconds}
        pass

    except Exception as e:
        pass
        if _DEBUG:
            errMsg = ""
            _LOG.error("{}, {}, {}".format(errMsg, traceback.format_exc(), str(e)))  
    return result
#获取access token end


#获取不限制的小程序码 begin 
'''
该接口用于获取小程序码，适用于需要的码数量极多的业务场景。通过该接口生成的小程序码，永久有效，数量暂无限制
https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/qrcode-link/qr-code/getUnlimitedQRCode.html
'''
def getUnlimitedQRCode(accessToken,scene,page,checkPath=True,envVersion="release",
                       width=430,autoColor=False,lineColor={"r":0,"g":0,"b":0},isHyaline=False):
    result = {}
    try:
        url = "https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}".format(accessToken)
        requestData = {
            "page": page,
            "scene": scene,
            "check_path": checkPath,
            "env_version": envVersion,
            # "width": width,
            # "auto_color": autoColor,
            # "line_color": lineColor,
            # "isHyaline": isHyaline,
        }
        payload = misc.jsonDumps(requestData)
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data = payload, headers = headers)
        if r.status_code == 200:
            #微信写这个接口的是神经病
            try:
                r.encoding = "utf-8"
                rtnData = misc.jsonLoads(r.text)
                if "errcode" in rtnData:
                    errCode = rtnData.get("errcode", "")        
                    errMsg = rtnData.get("errmsg", "") 
                    result["errCode"] = errCode
                    result["errMsg"] = errMsg
                # else:
                #     result["errCode"] = 0
            except:
                dataLen = len(r.content)
                if dataLen > 0:
                    result["errCode"] = 0
                    result["errMsg"] = "ok"
                    result["data"] = r.content

    except Exception as e:
        pass
        if _DEBUG:
            errMsg = ""
            _LOG.error("{}, {}, {}".format(errMsg, traceback.format_exc(), str(e)))  
    return result

#获取不限制的小程序码 end


#获取限制的小程序码 begin 
'''
该接口用于获取小程序码，适用于需要的码数量较少的业务场景。通过该接口生成的小程序码，永久有效，有数量限制
https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/qrcode-link/qr-code/getQRCode.html
'''
def getlimitedQRCode(accessToken,urlPath,envVersion="release",
                       width=430,autoColor=False,lineColor={"r":0,"g":0,"b":0},isHyaline=False):
    result = {}
    try:
        url = "https://api.weixin.qq.com/wxa/getwxacode?access_token={}".format(accessToken)
        requestData = {
            "path": urlPath,
            "env_version": envVersion,
            # "width": width,
            # "auto_color": autoColor,
            # "line_color": lineColor,
            # "isHyaline": isHyaline,
        }
        payload = misc.jsonDumps(requestData)
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data = payload, headers = headers)
        if r.status_code == 200:
            #微信写这个接口的是神经病
            try:
                r.encoding = "utf-8"
                rtnData = misc.jsonLoads(r.text)
                if "errcode" in rtnData:
                    errCode = rtnData.get("errcode", "")        
                    errMsg = rtnData.get("errmsg", "") 
                    result["errCode"] = errCode
                    result["errMsg"] = errMsg
                # else:
                #     result["errCode"] = 0
            except:
                dataLen = len(r.content)
                if dataLen > 0:
                    result["errCode"] = 0
                    result["errMsg"] = "ok"
                    result["data"] = r.content

    except Exception as e:
        pass
        if _DEBUG:
            errMsg = ""
            _LOG.error("{}, {}, {}".format(errMsg, traceback.format_exc(), str(e)))  
    return result

#获取限制的小程序码 end



def testCalSignString():
#    getOpenID("071zCPzz1SN7N90RIeCz1qoQzz1zCPzF")
#    testSet = {"appid":"wxd930ea5d5a258f4f", "mch_id":"10000100", "device_info":"1000", "body":"test", "nonce_str":"ibuaiVcKdpRxkhJA"}
#    weixinKey = "192006250b4c09247ec02edce69f6a2d"
#    rightRet = "9A0A8659F005D6984697E2CA0A9CF3B7"
#    rtnMsg = calSignString(testSet, weixinKey)

    getOpenID("071zCPzz1SN7N90RIeCz1qoQzz1zCPzF")
    testSet = {"appid":"wxd930ea5d5a258f4f", "mch_id":"10000100", "device_info":"1000", "body":u"中文", "nonce_str":"ibuaiVcKdpRxkhJA"}
    weixinKey = "192006250b4c09247ec02edce69f6a2d"
    rightRet = "9A0A8659F005D6984697E2CA0A9CF3B7"
    rtnMsg = calSignString(testSet, weixinKey)    


def testUnifiedOrder():
    testSet["sign"] = rtnMsg
    xmlData= xmlGenerator(testSet)
    xmlDecoder(xmlData)
    testSet = {'tradeNo': '9e98456728675f96e25ca7fdc8147be0', 'openID': u'ouI-B4okhcfW-7aX16500DXdAw9Y', 'total_fee': u'1'}
    rtnData = unifiedOrder(testSet)


def testRefund():
    testSet = {}
    testSet["transactionID"] = "4200000699202008241142288452"
    testSet["tradeNo"] = "01ed4d5e0110066615e7785acc06684b"
    testSet["refundNo"] = "12345678901234567890"
    testSet["total_fee"] = "2"
    testSet["refund_fee"] = testSet["total_fee"]
    testSet["refundReason"] = "test"
    rtnData = weixinRefund(testSet)


def testGetWebOpenID():
    getWebOpenID("code")


def testWebUserInfo():
    opendID = "oiCR46CTu_Wjm69emz0LLq9gSayU"
    accessToken = "39_U5in9hDde0oDH3hdPs2lYxNJ-x2CzkHtT9crW9_XCe_HuBe7WILUzJ0_GSdMqictjidgfJ9HGJuRedJ61HofiUmOAx-5K8olBwt_MYlkJCc"

    webUserInfo(accessToken,opendID)


def testToken():
    getAccessToken()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pass
        import platform
        if platform.system()=='Linux':
            import pdb
            pdb.set_trace()    
    # testWebUserInfo()
    testToken()
    pass

