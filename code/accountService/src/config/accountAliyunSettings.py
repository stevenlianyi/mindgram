#! /usr/bin/env python
#encoding: utf-8

#Filename: AliyunSettings.py  
#Author: Steven Lian
#E-mail:  / /steven.lian@gmail.com  
#Date: 2019-11-30
#Description:   阿里云通用的配置管理,

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

_DEBUG = True  #预设trace开关，禁止修改

#SMS Service 
ALIYUN_SMS_SERVICE = {
"local":{
    "AccessKeyId":"ACCESS_KEY", 
    "AccessKeySecret":"ACCESS_SECRET", 
    "Domain":"cn-zhangjiakou", 
    "RegionId":"cn-zhangjiakou", 
    "code":"code",
    "SignName":"用户", 
    "TemplateCode":"SMS_ID", 
    "infoCode":"phone", 
    "infoSignName":"用户通知", 
    "infoTemplateCode":"SMS_ID2", 
    "roleChangeProjectName":"projectName", 
    "roleChangeRoleName":"roleName", 
    "roleChangeSignName":"用户通知", 
    "roleChangeTemplateCode":"SMS_254130635", 
    }, 
"iotdemo":{
    "AccessKeyId":"ACCESS_KEY", 
    "AccessKeySecret":"ACCESS_SECRET", 
    "Domain":"cn-zhangjiakou", 
    "RegionId":"cn-zhangjiakou", 
    "code":"code",
    "SignName":"用户", 
    "TemplateCode":"SMS_ID", 
    "infoCode":"phone", 
    "infoSignName":"用户通知", 
    "infoTemplateCode":"SMS_ID2", 
    "roleChangeProjectName":"projectName", 
    "roleChangeRoleName":"roleName", 
    "roleChangeSignName":"用户通知", 
    "roleChangeTemplateCode":"SMS_254130635", 
    }, 
"xjy_cd_1":{
    "AccessKeyId":"ACCESS_KEY", 
    "AccessKeySecret":"ACCESS_SECRET", 
    "Domain":"cn-zhangjiakou", 
    "RegionId":"cn-zhangjiakou", 
    "code":"code",
    "SignName":"用户", 
    "TemplateCode":"SMS_ID", 
    "infoCode":"phone", 
    "infoSignName":"用户通知", 
    "infoTemplateCode":"SMS_ID2", 
    "roleChangeProjectName":"projectName", 
    "roleChangeRoleName":"roleName", 
    "roleChangeSignName":"用户通知", 
    "roleChangeTemplateCode":"SMS_254130635", 
    }, 
"zyj_bj":{
    "AccessKeyId":"ACCESS_KEY", 
    "AccessKeySecret":"ACCESS_SECRET", 
    "Domain":"cn-zhangjiakou", 
    "RegionId":"cn-zhangjiakou", 
    "code":"code",
    "SignName":"用户", 
    "TemplateCode":"SMS_ID", 
    "infoCode":"phone", 
    "infoSignName":"用户通知", 
    "infoTemplateCode":"SMS_ID2", 
    "roleChangeProjectName":"projectName", 
    "roleChangeRoleName":"roleName", 
    "roleChangeSignName":"用户通知", 
    "roleChangeTemplateCode":"SMS_254130635", 
    }, 
}[_SYS]


#OSS Service 
ALIYUN_OSS_SERVICE = {
"local":{
    "RegionId":"cn-beijing", 
    "roleArn":"acs:ram::1392433711034021:role/aliyunosstokengeneratorrole",
    "AccessKeyId":"ACCESS_KEY_2", 
    "AccessKeySecret":"ACCESS_SECRET_2", 
    "readOnlyAccessKeyId":"ACCESS_KEY_3", 
    "readOnlyAccessKeySecret":"ACCESS_SECRET_3", 
    "stsRegionId":"oss-cn-beijing", 
    "stsAccessKeyId":"ACCESS_KEY_STS", 
    "stsAccessKeySecret":"ACCESS_SECRET_STS", 
    "Endpoint":"https://oss-cn-beijing.aliyuncs.com", 
    "EndpointExternal":"https://oss-cn-beijing.aliyuncs.com", 
    "EndpointInternal":"https://oss-cn-beijing-internal.aliyuncs.com", 
    "BucketName":"PRIVATE", 
    "ConnTimeOut":60, 
    "DispTimeOut":1800, 
    "stsPolicyData":{
        "Version": "1",
        "Statement": 
        [{
            "Effect": "Allow",
            "Action": ["oss:Put*"],
            "Resource": ["acs:oss:*:*:PRIVATE","acs:oss:*:*:PRIVATE/*"],
            "Condition": {}
            }]
        },
    },
"iotdemo":{
    "RegionId":"cn-beijing", 
    "roleArn":"acs:ram::1392433711034021:role/aliyunosstokengeneratorrole",
    "AccessKeyId":"ACCESS_KEY_2", 
    "AccessKeySecret":"ACCESS_SECRET_2", 
    "readOnlyAccessKeyId":"ACCESS_KEY_3", 
    "readOnlyAccessKeySecret":"ACCESS_SECRET_3", 
    "stsRegionId":"oss-cn-beijing", 
    "stsAccessKeyId":"ACCESS_KEY_STS", 
    "stsAccessKeySecret":"ACCESS_SECRET_STS", 
    "Endpoint":"https://oss-cn-beijing.aliyuncs.com", 
    "EndpointExternal":"https://oss-cn-beijing.aliyuncs.com", 
    "EndpointInternal":"https://oss-cn-beijing-internal.aliyuncs.com", 
    "BucketName":"PRIVATE", 
    "ConnTimeOut":60, 
    "DispTimeOut":1800, 
    "stsPolicyData":{
        "Version": "1",
        "Statement": 
        [{
            "Effect": "Allow",
            "Action": ["oss:Put*"],
            "Resource": ["acs:oss:*:*:PRIVATE","acs:oss:*:*:PRIVATE/*"],
            "Condition": {}
            }]
        },
    }, 
"xjy_cd_1":{
    "RegionId":"cn-beijing", 
    "roleArn":"acs:ram::1392433711034021:role/aliyunosstokengeneratorrole",
    "AccessKeyId":"ACCESS_KEY_2", 
    "AccessKeySecret":"ACCESS_SECRET_2", 
    "readOnlyAccessKeyId":"ACCESS_KEY_3", 
    "readOnlyAccessKeySecret":"ACCESS_SECRET_3", 
    "stsRegionId":"oss-cn-beijing", 
    "stsAccessKeyId":"ACCESS_KEY_STS", 
    "stsAccessKeySecret":"ACCESS_SECRET_STS", 
    "Endpoint":"https://oss-cn-beijing.aliyuncs.com", 
    "EndpointExternal":"https://oss-cn-beijing.aliyuncs.com", 
    "EndpointInternal":"https://oss-cn-beijing-internal.aliyuncs.com", 
    "BucketName":"PRIVATE", 
    "ConnTimeOut":60, 
    "DispTimeOut":1800, 
    "stsPolicyData":{
        "Version": "1",
        "Statement": 
        [{
            "Effect": "Allow",
            "Action": ["oss:Put*"],
            "Resource": ["acs:oss:*:*:PRIVATE","acs:oss:*:*:PRIVATE/*"],
            "Condition": {}
            }]
        },
    }, 
"zyj_bj":{
    "RegionId":"cn-beijing", 
    "roleArn":"acs:ram::1392433711034021:role/aliyunosstokengeneratorrole",
    "AccessKeyId":"ACCESS_KEY_2", 
    "AccessKeySecret":"ACCESS_SECRET_2", 
    "readOnlyAccessKeyId":"ACCESS_KEY_3", 
    "readOnlyAccessKeySecret":"ACCESS_SECRET_3", 
    "stsRegionId":"oss-cn-beijing", 
    "stsAccessKeyId":"ACCESS_KEY_STS", 
    "stsAccessKeySecret":"ACCESS_SECRET_STS", 
    "Endpoint":"https://oss-cn-beijing.aliyuncs.com", 
    "EndpointExternal":"https://oss-cn-beijing.aliyuncs.com", 
    "EndpointInternal":"https://oss-cn-beijing-internal.aliyuncs.com", 
    "BucketName":"PRIVATE", 
    "ConnTimeOut":60, 
    "DispTimeOut":1800, 
    "stsPolicyData":{
        "Version": "1",
        "Statement": 
        [{
            "Effect": "Allow",
            "Action": ["oss:Put*"],
            "Resource": ["acs:oss:*:*:PRIVATE","acs:oss:*:*:PRIVATE/*"],
            "Condition": {}
            }]
        },
    }
}[_SYS]


#OSS OCR service 
ALIYUN_OCR_SERVICE = {
"local":{
    "url":"http://dm-51.data.aliyun.com/rest/160601/ocr/ocr_idcard.json", 
    "AppKey":"OCR_KEY", 
    "AppSecret":"OCR_SECRET", 
    "AppCode":"OCR_CODE", 
    }, 
"iotdemo":{
    "url":"http://dm-51.data.aliyun.com/rest/160601/ocr/ocr_idcard.json", 
    "AppKey":"OCR_KEY", 
    "AppSecret":"OCR_SECRET", 
    "AppCode":"OCR_CODE", 
    }, 
"xjy_cd_1":{
    "url":"http://dm-51.data.aliyun.com/rest/160601/ocr/ocr_idcard.json", 
    "AppKey":"OCR_KEY", 
    "AppSecret":"OCR_SECRET", 
    "AppCode":"OCR_CODE", 
    }, 
"zyj_bj":{
    "url":"http://dm-51.data.aliyun.com/rest/160601/ocr/ocr_idcard.json", 
    "AppKey":"OCR_KEY", 
    "AppSecret":"OCR_SECRET", 
    "AppCode":"OCR_CODE", 
    }
}[_SYS]



if __name__ == "__main__":
    pass
    # import pdb
    # pdb.set_trace()
    print ("_SYS",_SYS)
    print ("_SYS_SERVER_NAME",_SYS_SERVER_NAME)
    print ("ALIYUN_OSS_SERVICE",ALIYUN_OSS_SERVICE)
    print ("ALIYUN_OCR_SERVICE",ALIYUN_OCR_SERVICE)
