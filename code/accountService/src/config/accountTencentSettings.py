#! /usr/bin/env python
#encoding: utf-8

#Filename: tencentSettings.py  
#Author: Steven Lian
#E-mail:  / /steven.lian@gmail.com  
#Date: 2020-04-16
# https://cloud.tencent.com/document/product/436/12269
# pip install -U cos-python-sdk-v5
#Description:   腾讯云通用的配置管理,

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
#_SYS = "iotdemo"
#_SYS = "local"

_SYS_SERVER_NAME = local_settings._SYS_SERVER_NAME

#预设trace开关，禁止修改
_DEBUG = {
    "local":True,
    "iotDevice":True,
    "localHost":True,
    "iotdemo":True,
    "iotHome":True,
    }[_SYS]

#SMS Service 
TECENT_SMS_SERVICE = {
"local":{
    "SecretId":"SecretId", 
    "SecretKey":"SecretKey", 
    "reqTimeout":30, 
    "endpoint":"sms.tencentcloudapi.com", 
    "RegionId":"ap-beijing", 
    "SmsSdkAppid":"SmsSdkAppid", 
    "Sign":"Sign", 
    "TemplateID":"731411", #注册验证码
    "blockAlarm":"771841", #建筑物业务告警
    "meterAlarm":"772029", #业务告警通知
    "noAlarm":"776009", #无告警通知
    "TemplateParamSet":None, 
    }, 
"iotDevice":{
    "SecretId":"SecretId", 
    "SecretKey":"SecretKey", 
    "reqTimeout":30, 
    "endpoint":"sms.tencentcloudapi.com", 
    "RegionId":"ap-beijing", 
    "SmsSdkAppid":"SmsSdkAppid", 
    "Sign":"Sign", 
    "TemplateID":"731411", #注册验证码
    "blockAlarm":"771841", #建筑物业务告警
    "meterAlarm":"772029", #业务告警通知
    "noAlarm":"776009", #无告警通知
    "TemplateParamSet":None, 
    }, 
"localHost":{
    "SecretId":"SecretId", 
    "SecretKey":"5", 
    "reqTimeout":30, 
    "endpoint":"sms.tencentcloudapi.com", 
    "RegionId":"ap-chengdu", 
    "SmsSdkAppid":"1400352362", 
    "Sign":"Sign", 
    "TemplateID":"731411", #注册验证码
    "blockAlarm":"771841", #建筑物业务告警
    "meterAlarm":"772029", #业务告警通知
    "noAlarm":"776009", #无告警通知
    "TemplateParamSet":None, 
    }, 
"iotdemo":{
    "SecretId":"SecretId", 
    "SecretKey":"SecretKey", 
    "reqTimeout":30, 
    "endpoint":"sms.tencentcloudapi.com", 
    "RegionId":"ap-beijing", 
    "SmsSdkAppid":"SmsSdkAppid", 
    "Sign":"Sign", 
    "TemplateID":"731411", #注册验证码
    "blockAlarm":"771841", #建筑物业务告警
    "meterAlarm":"772029", #业务告警通知
    "noAlarm":"776009", #无告警通知
    "TemplateParamSet":None, 
    }, 
"iotHome":{
    "SecretId":"SecretId", 
    "SecretKey":"SecretKey", 
    "reqTimeout":30, 
    "endpoint":"sms.tencentcloudapi.com", 
    "RegionId":"ap-beijing", 
    "SmsSdkAppid":"SmsSdkAppid", 
    "Sign":"Sign", 
    "TemplateID":"731411", #注册验证码
    "blockAlarm":"771841", #建筑物业务告警
    "meterAlarm":"772029", #业务告警通知
    "noAlarm":"776009", #无告警通知
    "TemplateParamSet":None, 
    }, 
}[_SYS]


#COS Service 
TECENT_COS_SERVICE = {
"local":{
    "secretId":"secretId", 
    "secretKey":"5", 
    "domainBase":"myqcloud.com", 
    "regionId":"ap-chengdu", 
    "bucketName":"xjy-data", 
    "url":"https://xjy-data.cos.ap-chengdu.myqcloud.com", 
    "privateBucketName":"xjy-data", 
    "privateUrl":"https://xjy-data.cos.ap-chengdu.myqcloud.com", 
    "connTimeOut":60, 
    "dispTimeOut":1800, 
    }, 

"iotDevice":{
    "secretId":"secretId", 
    "secretKey":"5", 
    "domainBase":"myqcloud.com", 
    "regionId":"ap-chengdu", 
    "bucketName":"xjy-test-1301615502", 
    "url":"https://xjy-test-1301615502.cos.ap-chengdu.myqcloud.com", 
    "privateBucketName":"xjy-data", 
    "privateUrl":"https://xjy-data.cos.ap-chengdu.myqcloud.com", 
    "connTimeOut":60, 
    "dispTimeOut":1800, 
    }, 
    
"localHost":{
#    "secretId":"secretId", 
#    "secretKey":"5", 
    "secretId":"AKIDpQliPpdtxoOjodRWkty0sfRRFoiLDpjM", 
    "secretKey":"5", 
    "domainBase":"myqcloud.com", 
    "regionId":"ap-chengdu", 
    "bucketName":"xjy-data", 
    "url":"https://xjy-data.cos.ap-chengdu.myqcloud.com", 
    "privateBucketName":"xjy-data", 
    "privateUrl":"https://xjy-data.cos.ap-chengdu.myqcloud.com", 
    "connTimeOut":60, 
    "dispTimeOut":1800, 
    }, 
    
"iotdemo":{
    "secretId":"secretId", 
    "secretKey":"5", 
    "domainBase":"myqcloud.com", 
    "regionId":"ap-chengdu", 
    "bucketName":"xjy-data", 
    "url":"https://xjy-data.cos.ap-chengdu.myqcloud.com", 
    "privateBucketName":"xjy-data", 
    "privateUrl":"https://xjy-data.cos.ap-chengdu.myqcloud.com", 
    "connTimeOut":60, 
    "dispTimeOut":1800, 
    },

"iotHome":{
    "secretId":"secretId", 
    "secretKey":"5", 
    "domainBase":"myqcloud.com", 
    "regionId":"ap-chengdu", 
    "bucketName":"xjy-data", 
    "url":"https://xjy-data.cos.ap-chengdu.myqcloud.com", 
    "privateBucketName":"xjy-data", 
    "privateUrl":"https://xjy-data.cos.ap-chengdu.myqcloud.com", 
    "connTimeOut":60, 
    "dispTimeOut":1800, 
    },    
}[_SYS]


#OCR service 
TECENT_OCR_SERVICE = {
"local":{
    "url":"http://dm-51.data.aliyun.com/rest/160601/ocr/ocr_idcard.json", 
    "AppKey":"xjy-key", 
    "AppSecret":"5", 
    "AppCode":"5", 
    }, 
"iotDevice":{
    "url":"http://dm-51.data.aliyun.com/rest/160601/ocr/ocr_idcard.json", 
    "AppKey":"xjy-key", 
    "AppSecret":"5", 
    "AppCode":"5", 
    }, 
"localHost":{
    "url":"http://dm-51.data.aliyun.com/rest/160601/ocr/ocr_idcard.json", 
    "AppKey":"xjy-key", 
    "AppSecret":"5", 
    "AppCode":"5", 
    }, 
"iotdemo":{
    "url":"http://dm-51.data.aliyun.com/rest/160601/ocr/ocr_idcard.json", 
    "AppKey":"xjy-key", 
    "AppSecret":"5", 
    "AppCode":"5", 
    },
"iotHome":{
    "url":"http://dm-51.data.aliyun.com/rest/160601/ocr/ocr_idcard.json", 
    "AppKey":"xjy-key", 
    "AppSecret":"5", 
    "AppCode":"5", 
    },
}[_SYS]


#AI 365 服务, 人脸识别, 身份认证
TECENT_AI365_FACE_SERVICE = {
"local":{
    "url":"https://service-q3toequb-1301232119.bj.apigw.tencentcs.com/release/idfaceIdentity", 
    "SecretID":"5", 
    "SecretKey":"5", 
    }, 
"iotDevice":{
    "url":"https://service-q3toequb-1301232119.bj.apigw.tencentcs.com/release/idfaceIdentity", 
    "SecretID":"5", 
    "SecretKey":"5", 
    }, 
"localHost":{
    "url":"https://service-q3toequb-1301232119.bj.apigw.tencentcs.com/release/idfaceIdentity", 
    "SecretID":"5", 
    "SecretKey":"5", 
    }, 
"iotdemo":{
    "url":"https://service-q3toequb-1301232119.bj.apigw.tencentcs.com/release/idfaceIdentity", 
    "SecretID":"5", 
    "SecretKey":"5", 
    },
"iotHome":{
    "url":"https://service-q3toequb-1301232119.bj.apigw.tencentcs.com/release/idfaceIdentity", 
    "SecretID":"5", 
    "SecretKey":"5", 
    },
}[_SYS]


#AI 365  运营商实名认证接口三要素手机验证
TECENT_AI365_OPERATOR_SERVICE = {
"local":{
    "url":"http://service-4epp7bin-1300755093.ap-beijing.apigateway.myqcloud.com/release/efficient/cellphone", 
    "SecretID":"5", 
    "SecretKey":"5 ", 
    }, 
"iotDevice":{
    "url":"http://service-4epp7bin-1300755093.ap-beijing.apigateway.myqcloud.com/release/efficient/cellphone", 
    "SecretID":"5", 
    "SecretKey":"5 ", 
    }, 
"localHost":{
    "url":"http://service-4epp7bin-1300755093.ap-beijing.apigateway.myqcloud.com/release/efficient/cellphone", 
    "SecretID":"5", 
    "SecretKey":"5 ", 
    }, 
"iotdemo":{
    "url":"http://service-4epp7bin-1300755093.ap-beijing.apigateway.myqcloud.com/release/efficient/cellphone", 
    "SecretID":"5", 
    "SecretKey":"5 ", 
    },
"iotHome":{
    "url":"http://service-4epp7bin-1300755093.ap-beijing.apigateway.myqcloud.com/release/efficient/cellphone", 
    "SecretID":"5", 
    "SecretKey":"5 ", 
    },
}[_SYS]


if __name__ == "__main__":
    pass
    # import pdb
    # pdb.set_trace()
    print ("_SYS",_SYS)
    print ("_SYS_SERVER_NAME",_SYS_SERVER_NAME)
    print ("TECENT_SMS_SERVICE",TECENT_SMS_SERVICE)
    print ("TECENT_COS_SERVICE",TECENT_COS_SERVICE)
    print ("TECENT_OCR_SERVICE",TECENT_OCR_SERVICE)
    print ("TECENT_AI365_FACE_SERVICE",TECENT_AI365_FACE_SERVICE)
    print ("TECENT_AI365_OPERATOR_SERVICE",TECENT_AI365_OPERATOR_SERVICE)
