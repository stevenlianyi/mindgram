#!/usr/bin/env python3
#encoding: utf-8

#Filename: miniPorgramSettings.py  
#Author: Steven Lian
#E-mail:  / /steven.lian@gmail.com  
#Date: 2019-09-03
#Description:  微信小程序(miniProgram)和web 端扫码登录参数设置

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

#生产环境 rss | 测试环境 dss
_SYS = local_settings._SYS
#_SYS = "bupttest"


miniAppID = {
    "local":"wxappid", 
    "iotDevice":"wxappid", 
    "localHost":"wxappid", 
    "iotdemo":"wxappid", 
    "iotHome":"wxappid", 
}[_SYS]


miniAppSecret = {
    "local":"wxappsecret", 
    "iotDevice":"wxappsecret", 
    "localHost":"wxappsecret", 
    "iotdemo":"wxappsecret", 
    "iotHome":"wxappsecret", 
}[_SYS]


miniMch_id = {
    "local":"wx_mchid", 
    "iotDevice":"wx_mchid", 
    "localHost":"wx_mchid", 
    "iotdemo":"wx_mchid", 
    "iotHome":"wx_mchid", 
}[_SYS]


miniAppKey = {
    "local":"wx_mini_appkey", 
    "iotDevice":"wx_mini_appkey", 
    "localHost":"wx_mini_appkey", 
    "iotdemo":"wx_mini_appkey", 
    "iotHome":"wx_mini_appkey", 
}[_SYS]


miniBodyText = {
    "local":u"应用充值", 
    "iotDevice":u"应用充值", 
    "localHost":u"应用充值", 
    "iotdemo":u"应用充值", 
    "iotHome":u"应用充值", 
}[_SYS]


miniFeeType = {
    "local":"CNY", 
    "iotDevice":"CNY", 
    "localHost":"CNY", 
    "iotdemo":"CNY", 
    "iotHome":"CNY", 
}[_SYS]


miniDetails = {
    "local":u"应用充值", 
    "iotDevice":u"应用充值", 
    "localHost":u"应用充值", 
    "iotdemo":u"应用充值", 
    "iotHome":u"应用充值", 
}[_SYS]


miniAppIDChief = {
    "local":"wxappid", 
    "iotDevice":"wxappid", 
    "localHost":"wxappid", 
    "iotdemo":"wxb53c70620d161e37", 
    "iotHome":"wxappid", 
}[_SYS]


miniAppSecretChief = {
    "local":"wxappsecret", 
    "iotDevice":"wxappsecret", 
    "localHost":"wxappsecret", 
    "iotdemo":"wxappsecret", 
    "iotHome":"wxappsecret", 
}[_SYS]


miniGrantType = "authorization_code" 


miniLocapIP = {
    "local":"39.100.3.91", 
    "iotDevice":"39.100.3.91", 
    "localHost":"127.0.0.1", 
    "iotdemo":"www.iotdemo.tech", 
    "iotHome":"192.168.10.100", 
}[_SYS]


miniServerURL = "https://api.weixin.qq.com/sns/jscode2session"


#异步接收微信支付结果通知的回调地址，通知url必须为外网可访问的url，不能携带参数。
miniNotifyUrl = {
    "local":"https://app.iottest.online/wxnotify", 
    "iotDevice":"https://app.iottest.online/wxnotify", 
    "localHost":"https://app.iottest.online/wxnotify", 
    "iotdemo":"https://app.iotdemo.tech/wxnotify", 
    "iotHome":"https://192.168.10.100/wxnotify", 
}[_SYS]


#小程序取值如下：JSAPI
miniTradeType = {
    "local":"JSAPI", 
    "iotDevice":"JSAPI", 
    "localHost":"JSAPI", 
    "iotdemo":"JSAPI", 
    "iotHome":"JSAPI", 
}[_SYS]


#微信支付统一下单地址
miniUnifiedOrderURL = "https://api.mch.weixin.qq.com/pay/unifiedorder" 

#微信支付退款地址
miniRefundURL = "https://api.mch.weixin.qq.com/secapi/pay/refund"


#微信支付相关证书路径
miniServerRootCAFilePath = {
    "local":r"/etc/pki/tls/certs/ca-bundle.crt", 
    "iotDevice":r"/etc/pki/tls/certs/ca-bundle.crt", 
    "localHost":r"/etc/pki/tls/certs/ca-bundle.crt", 
    "iotdemo":r"/etc/pki/tls/certs/ca-bundle.crt", 
    "iotHome":r"D:\data\cert\cacert.pem", 
}[_SYS]


miniAPIClientCertFilePath = {
    "local":r"/data/cert/apiclient_cert.pem", 
    "iotDevice":r"D:\data\cert\apiclient_cert.pem", 
    "localHost":r"/data/cert/apiclient_cert.pem", 
    "iotdemo":r"/data/cert/apiclient_cert.pem", 
    "iotHome":r"D:\data\cert\apiclient_cert.pem", 
}[_SYS]


miniAPIClientKeyFilePath = {
    "local":r"/data/cert/apiclient_key.pem", 
    "iotDevice":r"/data/cert/apiclient_key.pem", 
    "localHost":r"/data/cert/apiclient_key.pem", 
    "iotdemo":r"/data/cert/apiclient_key.pem", 
    "iotHome":r"D:\data\cert\apiclient_key.pem", 
}[_SYS]


webAppID = {
    "local":"wxappid", 
    "iotDevice":"wxappid", 
    "localHost":"wxappid", 
    "iotdemo":"wxappid", 
    "iotHome":"wxappid", 
}[_SYS]


webAppSecret = {
    "local":"wxappsecret", 
    "iotDevice":"wxappsecret", 
    "localHost":"wxappsecret", 
    "iotdemo":"wxappsecret", 
    "iotHome":"wxappsecret", 
}[_SYS]


webServerURL = "https://api.weixin.qq.com/sns/oauth2/access_token?" 
webRefreshURL = "https://api.weixin.qq.com/sns/oauth2/refresh_token?" 
webVerifyURL = "https://api.weixin.qq.com/sns/auth?" 
webUserInfoURL = "https://api.weixin.qq.com/sns/userinfo?" 
webGrantType = "authorization_code" 


_DEBUG = True  #预设trace开关，禁止修改


if __name__ == "__main__":
    pass
    # import pdb
    # pdb.set_trace()
    print ("_SYS",_SYS)
    print ("miniAppID",miniAppID)
    print ("miniAppSecret",miniAppSecret)
    print ("miniAppIDChief",miniAppIDChief)
    print ("miniAppSecretChief",miniAppSecretChief)
    print ("miniServerRootCAFilePath",miniServerRootCAFilePath)
    print ("miniAPIClientCertFilePath",miniAPIClientCertFilePath)
    print ("webAppID",webAppID)
    print ("webAppSecret",webAppSecret)