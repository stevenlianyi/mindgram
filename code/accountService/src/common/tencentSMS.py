#! /usr/bin/env python
#encoding: utf-8

#Filename: tencentSMS.py
#Author: Steven Lian
#E-mail:  steven.lian@gmail.com  
#Date: 2020-04-17
# https://cloud.tencent.com/document/product/382/37745
# pip install tencentcloud-sdk-python
#Description:  腾讯云SMS功能

_VERSION="20230802"

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
from config import accountTencentSettings as settings

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
# 导入 SMS 模块的client models
from tencentcloud.sms.v20190711 import sms_client, models

# 导入可选配置类
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile


_DEBUG =  settings._DEBUG
# command part

SMS_ERR_MSG = {
"FailedOperation.ContainSensitiveWord":"短信内容中含有敏感词，请联系 sms helper。",
"FailedOperation.FailResolvePacket":"请求包解析失败，通常情况下是由于没有遵守 API 接口说明规范导致的，请参考 请求包体解析1004错误详解。",
"FailedOperation.InsufficientBalanceInSmsPackage":"套餐包余量不足，请 购买套餐包。",
"FailedOperation.JsonParseFail":"解析请求包体时候失败。",
"FailedOperation.MarketingSendTimeConstraint":"营销短信发送时间限制，为避免骚扰用户，营销短信只允许在8点到22点发送。",
"FailedOperation.MissingSignature":"没有申请签名之前，无法申请模板，请根据 创建签名 申请完成之后再次申请。",
"FailedOperation.MissingSignatureToModify":"此签名 ID 未提交申请或不存在，不能进行修改操作，请检查您的 SignId 是否填写正确。",
"FailedOperation.MissingTemplateToModify":"此模板 ID 未提交申请或不存在，不能进行修改操作，请检查您的 TemplateId是否填写正确。",
"FailedOperation.NotEnterpriseCertification":"非企业认证无法使用签名及模版相关接口，您可以 变更实名认证模式，变更为企业认证用户后，约1小时左右生效。",
"FailedOperation.OtherError":"其他错误，一般是由于参数携带不符合要求导致，请参看API接口说明，如有需要请联系 sms helper。",
"FailedOperation.PhoneNumberInBlacklist":"手机号在黑名单库中，通常是用户退订或者命中运营商黑名单导致的，可联系 sms helper 解决。",
"FailedOperation.PhoneNumberOnBlacklist":"手机号在黑名单库中，通常是用户退订或者命中运营商黑名单导致的，可联系 sms helper 解决",
"FailedOperation.SignatureIncorrectOrUnapproved":"签名格式错误或者签名未审批，签名只能由中英文、数字组成，要求2 - 12个字。如果符合签名格式规范，请核查签名是否已审批。",
"FailedOperation.TemplateAlreadyPassedCheck":"此模板已经通过审核，无法再次进行修改。",
"FailedOperation.TemplateIncorrectOrUnapproved":"模版未审批或请求的内容与审核通过的模版内容不匹配，请参考 1014错误详解。",
"InternalError.OtherError":"其他错误，请联系 sms helper 并提供失败手机号。",
"InternalError.RequestTimeException":"请求发起时间不正常，通常是由于您的服务器时间与腾讯云服务器时间差异超过10分钟导致的，请核对服务器时间及 API 接口中的时间字段是否正常。",
"InternalError.RestApiInterfaceNotExist":"不存在该 RESTAPI 接口，请核查 REST API 接口说明。",
"InternalError.SigFieldMissing":"后端包体中请求包体没有 Sig 字段或 Sig 为空。",
"InternalError.SigVerificationFail":"后端校验 Sig 失败。",
"InternalError.Timeout":"请求下发短信超时，请参考 60008错误详解。",
"InternalError.UnknownError":"未知错误类型。",
"InvalidParameter.AppidAndBizId":"账号与应用id不匹配。",
"InvalidParameter.InvalidParameters":"International 或者 SmsType 参数有误，如有需要请联系 sms helper。",
"InvalidParameterValue.ContentLengthLimit":"请求的短信内容太长，短信长度规则请参考 国内短信内容长度计算规则。",
"InvalidParameterValue.ImageInvalid":"上传的转码图片格式错误，请参照 API 接口说明中对改字段的说明，如有需要请联系 sms helper。",
"InvalidParameterValue.IncorrectPhoneNumber":"手机号格式错误，请参考 1016错误详解",
"InvalidParameterValue.InvalidDocumentType":"DocumentType 字段校验错误，请参照 API 接口说明中对改字段的说明，如有需要请联系 sms helper。",
"InvalidParameterValue.InvalidInternational":"International 字段校验错误，请参照 API 接口说明中对改字段的说明，如有需要请联系 sms helper。",
"InvalidParameterValue.InvalidUsedMethod":"UsedMethod 字段校验错误，请参照 API 接口说明中对改字段的说明，如有需要请联系 sms helper。",
"InvalidParameterValue.MissingSignatureList":"无法识别签名，请确认是否已有签名通过申请，一般是签名未通过申请，可以查看 签名审核 。",
"InvalidParameterValue.ProhibitedUseUrlInTemplateParameter":"禁止在模板变量中使用 URL。",
"InvalidParameterValue.SdkAppidNotExist":"SdkAppid 不存在。",
"InvalidParameterValue.SignAlreadyPassedCheck":"此签名已经通过审核，无法再次进行修改。",
"InvalidParameterValue.TemplateParameterFormatError":"验证码模板参数格式错误，验证码类模版，模版变量只能传入0 - 6位（包括6位）纯数字",
"InvalidParameterValue.TemplateParameterLengthLimit":"单个模板变量字符数超过12个，企业认证用户不限制单个变量值字数，您可以 变更实名认证模式，变更为企业认证用户后，该限制变更约1小时左右生效。",
"LimitExceeded.AppDailyLimit":"业务短信日下发条数超过设定的上限 ，可自行到控制台调整短信频率限制策略。",
"LimitExceeded.DailyLimit":"短信日下发条数超过设定的上限 (国际/港澳台)，如需调整限制，可联系 sms helper。",
"LimitExceeded.DeliveryFrequencyLimit":"下发短信命中了频率限制策略，可自行到控制台调整短信频率限制策略，如有其他需求请联系 sms helper。",
"LimitExceeded.PhoneNumberCountLimit":"调用短信发送 API 接口单次提交的手机号个数超过200个，请遵守 API 接口说明。",
"LimitExceeded.PhoneNumberDailyLimit":"单个手机号日下发短信条数超过设定的上限，可自行到控制台调整短信频率限制策略。",
"LimitExceeded.PhoneNumberOneHourLimit":"单个手机号1小时内下发短信条数超过设定的上限，可自行到控制台调整短信频率限制策略。",
"LimitExceeded.PhoneNumberSameContentDailyLimit":"单个手机号下发相同内容超过设定的上限，可自行到控制台调整短信频率限制策略。",
"LimitExceeded.PhoneNumberThirtySecondLimit":"单个手机号30秒内下发短信条数超过设定的上限，可自行到控制台调整短信频率限制策略。",
"MissingParameter.EmptyPhoneNumberSet":"传入的号码列表为空，请确认您的参数中是否传入号码。",
"UnauthorizedOperation.IndividualUserMarketingSmsPermissionDeny":"个人用户没有发营销短信的权限，请参考 权益区别。",
"UnauthorizedOperation.RequestIpNotInWhitelist":"请求 IP 不在白名单中，您配置了校验请求来源 IP，但是检测到当前请求 IP 不在配置列表中，如有需要请联系 sms helper。",
"UnauthorizedOperation.RequestPermissionDeny":"请求没有权限，请联系 sms helper。",
"UnauthorizedOperation.SdkAppidIsDisabled":"此 sdkappid 禁止提供服务，如有需要请联系 sms helper。",
"UnauthorizedOperation.SerivceSuspendDueToArrears":"欠费被停止服务，可自行登录腾讯云充值来缴清欠款。",
"UnauthorizedOperation.SmsSdkAppidVerifyFail":"SmsSdkAppid 校验失败。",
"UnsupportedOperation.":"不支持该请求。",
"UnsupportedOperation.ContainDomesticAndInternationalPhoneNumber":"群发请求里既有国内手机号也有国际手机号。",
"UnsupportedOperation.UnsuportedRegion":"不支持该地区短信下发。",
}
    

def sendSMS(phoneNum,  contentList, templateName = "TemplateID", intPrefix = "+86"):
    result = {}
    templateID = settings.TECENT_SMS_SERVICE[templateName]
    if isinstance(contentList,  list) == False:
        contentList = [contentList]
    try:
        # 必要步骤：
        # 实例化一个认证对象，入参需要传入腾讯云账户密钥对 secretId 和 secretKey
        # 本示例采用从环境变量读取的方式，需要预先在环境变量中设置这两个值
        # 您也可以直接在代码中写入密钥对，但需谨防泄露，不要将代码复制、上传或者分享给他人
        # CAM 密钥查询：https://console.cloud.tencent.com/cam/capi
        
        cred = credential.Credential(settings.TECENT_SMS_SERVICE["SecretId"], settings.TECENT_SMS_SERVICE["SecretKey"])
        # 实例化一个 http 选项，可选，无特殊需求时可以跳过
        httpProfile = HttpProfile()
        httpProfile.reqMethod = "POST"  # POST 请求（默认为 POST 请求）
        httpProfile.reqTimeout = settings.TECENT_SMS_SERVICE["reqTimeout"]    # 请求超时时间，单位为秒（默认60秒）
        httpProfile.endpoint = settings.TECENT_SMS_SERVICE["endpoint"]   # 指定接入地域域名（默认就近接入） "sms.tencentcloudapi.com" 
        
        # 非必要步骤:
        # 实例化一个客户端配置对象，可以指定超时时间等配置
        clientProfile = ClientProfile()
        clientProfile.signMethod = "TC3-HMAC-SHA256"  # 指定签名算法
        clientProfile.language = "en-US"
        clientProfile.httpProfile = httpProfile
        
        # 实例化 SMS 的 client 对象
        # 第二个参数是地域信息，可以直接填写字符串 ap-guangzhou，或者引用预设的常量
        client = sms_client.SmsClient(cred, settings.TECENT_SMS_SERVICE["RegionId"], clientProfile)

        # 实例化一个请求对象，根据调用的接口和实际情况，可以进一步设置请求参数
        # 您可以直接查询 SDK 源码确定 SendSmsRequest 有哪些属性可以设置
        # 属性可能是基本类型，也可能引用了另一个数据结构
        # 推荐使用 IDE 进行开发，可以方便的跳转查阅各个接口和数据结构的文档说明
        req = models.SendSmsRequest()
            
        # 基本类型的设置:
        # SDK 采用的是指针风格指定参数，即使对于基本类型也需要用指针来对参数赋值
        # SDK 提供对基本类型的指针引用封装函数
        # 帮助链接：
        # 短信控制台：https://console.cloud.tencent.com/smsv2
        # sms helper：https://cloud.tencent.com/document/product/382/3773

        # 短信应用 ID: 在 [短信控制台] 添加应用后生成的实际 SDKAppID，例如1400006666
        req.SmsSdkAppid = settings.TECENT_SMS_SERVICE["SmsSdkAppid"]
        # 短信签名内容: 使用 UTF-8 编码，必须填写已审核通过的签名，可登录 [短信控制台] 查看签名信息
        req.Sign = settings.TECENT_SMS_SERVICE["Sign"]
        # 短信码号扩展号: 默认未开通，如需开通请联系 [sms helper]
        req.ExtendCode = ""
        # 用户的 session 内容: 可以携带用户侧 ID 等上下文信息，server 会原样返回
        userSessionContext  = phoneNum +"_"+ misc.getTime() #用电话号码+时间戳
        req.SessionContext = userSessionContext
        # 国际/港澳台短信 senderid: 国内短信填空，默认未开通，如需开通请联系 [sms helper]
        req.SenderId = ""
        # 下发手机号码，采用 e.164 标准，+[国家或地区码][手机号]
        # 例如+8613711112222， 其中前面有一个+号 ，86为国家码，13711112222为手机号，最多不要超过200个手机号
        if phoneNum[0] != "+":
            intPhoneNum = intPrefix+phoneNum
        else:
            intPhoneNum = phoneNum
        req.PhoneNumberSet = [intPhoneNum]
        # 模板 ID: 必须填写已审核通过的模板 ID，可登录 [短信控制台] 查看模板 ID
        req.TemplateID = templateID
        # 模板参数: 若无模板参数，则设置为空
        req.TemplateParamSet = [settings.TECENT_SMS_SERVICE["TemplateParamSet"]]
        req.TemplateParamSet = contentList

        # 通过 client 对象调用 SendSms 方法发起请求。注意请求方法名与请求对象是对应的
        resp = client.SendSms(req)

        # 输出 JSON 格式的字符串回包
        #print(resp.to_json_string(indent=2))
        result =resp.to_json_string(indent=2)
        rtnSet = misc.jsonLoads(result)
        
        SendStatusSet =  rtnSet.get("SendStatusSet")
        
        nLen = len(SendStatusSet)
        
        if nLen == 1:
            if SendStatusSet[0].get("Code") == "Ok":
                rtnSet["Code"] = "OK"
            else:
                rtnSet["Message"] = SendStatusSet[0].get("Message")
            # result = misc.jsonDumps(rtnSet)
            result = rtnSet
            pass

            # 实例化一个请求对象，根据调用的接口和实际情况，可以进一步设置请求参数
            # 您可以直接查询 SDK 源码确定 SendSmsRequest 有哪些属性可以设置
            # 属性可能是基本类型，也可能引用了另一个数据结构
            # 推荐使用 IDE 进行开发，可以方便的跳转查阅各个接口和数据结构的文档说明
            #req = models.PullSmsSendStatusRequest()
            
            # 短信应用 ID: 在 [短信控制台] 添加应用后生成的实际 SDKAppID，例如1400006666
            #req.SmsSdkAppid = settings.TECENT_SMS_SERVICE["SmsSdkAppid"]
            # 拉取最大条数，最多100条
            #req.Limit = 10

            # 通过 client 对象调用 PullSmsSendStatus 方法发起请求。注意请求方法名与请求对象是对应的
            #resp = client.PullSmsSendStatus(req)

            # 输出 JSON 格式的字符串回包
            #print(resp.to_json_string(indent=2))
        
    except TencentCloudSDKException as err:
        print(err)
        
    return result
    

def main():
    print (sendSMS("13801324342", "123345"))
    

if __name__ == "__main__":
    main()



