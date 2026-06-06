#! /usr/bin/env python
#encoding: utf-8

#Filename: aliyunSMS.py
#Author: Steven Lian
#E-mail:  steven.lian@gmail.com  
#Date: 2019-09-28
#Description:   阿里云SMS功能

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

#common functions(log,time,string, json etc)
from common import miscCommon as misc

#setting files
from config import accountAliyunSettings as settings

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
client = AcsClient(settings.ALIYUN_SMS_SERVICE["AccessKeyId"], settings.ALIYUN_SMS_SERVICE["AccessKeySecret"], settings.ALIYUN_SMS_SERVICE["Domain"])

_DEBUG =  settings._DEBUG
# command part

SMS_ERR_MSG = {
}

defaultSignName = settings.ALIYUN_SMS_SERVICE["SignName"]
defaultTemplateCode = settings.ALIYUN_SMS_SERVICE["TemplateCode"]
defaultCode = settings.ALIYUN_SMS_SERVICE["code"]

infoSignName = settings.ALIYUN_SMS_SERVICE["infoSignName"]
infoTemplateCode = settings.ALIYUN_SMS_SERVICE["infoTemplateCode"]
infoCode = settings.ALIYUN_SMS_SERVICE["infoCode"]

roleChangeSignName = settings.ALIYUN_SMS_SERVICE["roleChangeSignName"]
roleChangeTemplateCode = settings.ALIYUN_SMS_SERVICE["roleChangeTemplateCode"]
roleChangeProjectName = settings.ALIYUN_SMS_SERVICE["roleChangeProjectName"]
roleChangeRoleName = settings.ALIYUN_SMS_SERVICE["roleChangeRoleName"]


def sendSMS(phoneNum, content="",signName=defaultSignName,templeateCode=defaultTemplateCode,code=defaultCode,codeSet=None):
    result = {}
    try:
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https') # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('RegionId', settings.ALIYUN_SMS_SERVICE["RegionId"])
        request.add_query_param('PhoneNumbers', phoneNum)
        request.add_query_param('SignName', signName)
        request.add_query_param('TemplateCode', templeateCode)
        if not codeSet:
            codeSet = {code:content}
        codeString = misc.jsonDumps(codeSet)
        request.add_query_param('TemplateParam', codeString)

        response = client.do_action(request)
        if isinstance(response,bytes):
            response = response.decode()
        result = misc.jsonLoads(response)
        # result = response
        
    except:
        pass
        
    return result
    

def infoSMS(phoneNum, content):
    return sendSMS(phoneNum, content,infoSignName,infoTemplateCode,infoCode)

def customeSMS(phoneNum, codeSet):
    return sendSMS(phoneNum,signName=infoSignName,templeateCode=infoTemplateCode,code=infoCode,codeSet=codeSet)

def roleChangeSMS(phoneNum, projectName,roleName):
    codeSet = {}
    codeSet[roleChangeProjectName] = projectName
    codeSet[roleChangeRoleName] = roleName
    return sendSMS(phoneNum,signName =roleChangeSignName,templeateCode=roleChangeTemplateCode,codeSet=codeSet)
    

def main():
    # sendSMS("18519860102", "123345")
    # sendSMS("13910710766", "13910710766",infoSignName,infoTemplateCode,infoCode)
    codeSet = {"alarm":"green","name":"lianyi"}
    customeSMS("13910710766", codeSet)
    codeSet = {"alarm":"红色","name":"张永军"}
    customeSMS("18519860102", codeSet)
    # infoSMS("13910710766", "green")
    # roleChangeSMS("13910710766","5G测试","协调员")
    

if __name__ == "__main__":
    main()



