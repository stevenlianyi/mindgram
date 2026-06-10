#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#Filename: mysqlCommon.py  
#Date: 2020-04-01
#Description:   mysql 处理代码

#mysql数据库信息也存储在这里, 主要是只有部分程序需要处理mysql数据库, 读写已经分离, 目前主要是采用sql语句处理, 已经防止注入攻击. 


_VERSION="20260609"

#add src directory
import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
if sys.getdefaultencoding() != 'utf-8':
    pass
    #reload(sys)
    #sys.setdefaultencoding('utf-8')
    
#import decimal 
#import requests
import traceback
# import copy

#global defintion/common var etc.
from common import globalDefinition as comGD

from common import funcCommon as comFC
#code/decode functions
#from common import codingDecoding as comCD

#common functions(log,time,string, json etc)
from common import miscCommon as misc

#setting files
from config import mysqlSettings as mysqlSettings

from config import basicSettings as settings

HOME_DIR = settings._HOME_DIR

if "_LOG" not in dir() or not _LOG:
    logfilepath = os.path.join(HOME_DIR, comGD._DEF_GENRAL_MYSQL_LOG_NAME)
#    _LOG = misc.setLogNew(comGD._DEF_XJY_MYSQL_TITLE, logfilepath)
    
_DEBUG = settings._DEBUG

auto_increment_default_value = 10000

SYS_DEFAULT_AUTO_LOGINID = settings.SYS_DEFAULT_AUTO_LOGINID

if "mysqlDB" not in dir() or not mysqlDB:
    mysqlDB = mysqlSettings.mysqlDB

database_name = mysqlSettings.MYSQL_READ_DB

#common begin

def dataFormatConvert(dataList):
    result = dataList
    for data in dataList:
        for k, v in data.items():
            if isinstance(v, int):
                data[k] = str(v)
            if isinstance(v, float):
                data[k] = str(v)
            if v == None:
                data[k] = ""
            if k in ["position", "regPosition","fileIDList"]:
                if v:
                    v = v.replace("'", "\"")
                    data[k] = misc.jsonLoads(v)
    result = dataList
    return result


def chkTableExist(tableName):
    result = False
    sqlStr = "SELECT table_name FROM information_schema.TABLES WHERE table_schema = %s and table_name = %s;"
    rtn = mysqlDB.executeRead(sqlStr, (database_name, tableName))
    if rtn > 0:
        result = True
    return result


def dropTableGeneral(tableName):
    result = False
    try:
        sqlStr = "DROP TABLE %s;" % tableName
        rtn = mysqlDB.executeWrite(sqlStr)
        rtn = chkTableExist(tableName)
        if rtn == False:
            result = True
    except:
        pass
    return result    


def insertTableGeneral(tableName, dataSet, selfDefinedPrimaryKey = comGD._CONST_NO):
    result = 0
    try:
        if sys.version_info.major <= 2:
            insertStr = ("INSERT INTO %s (" % tableName).encode("utf-8")
        else:
            insertStr = ("INSERT INTO %s (" % tableName)
            
        fieldNameList = [insertStr]
        placeHolderList = []
        valuesList = []

        for k,  v in dataSet.items():
            fieldNameList.append(k)
            fieldNameList.append(",")
            stringFlag = False
            if isinstance(v,  bytes):
                pass
#            if isinstance(v, int):
#                v = str(v)
#                    v = v.encode("utf-8")
            if sys.version_info.major <= 2:
                if isinstance(v, unicode):
                    v = v.encode("utf-8")
            valuesList.append(v)
            placeHolderList.append("%s")
            placeHolderList.append(",")

        fieldNameList = fieldNameList[0:-1]
        fieldNameList.append(")  VALUES (" ) 
        placeHolderList = placeHolderList[0:-1]
        fieldNameList.extend(placeHolderList)
        fieldNameList.append(")")
        sqlStr = "".join(fieldNameList)
        rtn = mysqlDB.executeWrite(sqlStr, tuple(valuesList))
#        if _DEBUG:
#            if rtn <=0:
#                _LOG.warning("M: %d %s" % (rtn,  sqlStr)) 
        
        if rtn > 0:
            if selfDefinedPrimaryKey == comGD._CONST_NO:
                #result = mysqlDB.lastrowid
                result = mysqlDB.insertID()
            else:
                result = rtn

    except Exception as e:
        errMsg = '%s %s'%("insertTableGeneral", str(e))
#        if _DEBUG:
#            _LOG.error( '%s' %(errMsg))

    return result


def updateTableGeneral(tableName, keySqlstr, keyValues, dataSet):
    result = 0
    try:
        tempStr = "UPDATE %s SET " % tableName
        fieldNameList = [tempStr]
        valuesList = []
        for k,  v in dataSet.items():
            fieldNameList.append("%s = " % (k))
            fieldNameList.append("%s")
            fieldNameList.append(",")
            valuesList.append(v)

        fieldNameList = fieldNameList[0:-1]
        
        fieldNameList.append("  WHERE %s;" % (keySqlstr)) 
        valuesList.extend(keyValues)
            
        sqlStr = "".join(fieldNameList)
        rtn = mysqlDB.executeWrite(sqlStr, tuple(valuesList))
#        if _DEBUG:
#            if rtn <=0:
#                _LOG.warning("M: %d %s" % (rtn,  sqlStr))                         

    except Exception as e:
        errMsg = '%s %s'%("updateTableGeneral", str(e))
#        if _DEBUG:
#            _LOG.error( '%s' %(errMsg))

    return result


#获取当前数据库表名称和记录数
def getCurrTableNames():
    result = []
    databaseName = mysqlSettings.MYSQL_READ_DB

    valuesList = []
    sqlStr =  f"SELECT TABLE_NAME,TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='{databaseName}';" 

    try:
        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            for data in dataList:
                aSet = {}
                aSet["tableName"] = data["TABLE_NAME"]
                aSet["tableRows"] = data["TABLE_ROWS"]
                result.append(aSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"

    return result


def genOrList(IDList, keyName = ""):
    aList = []
    count = 0
    aList.append("( ")
    for ID in IDList:
        if count == 0:
            aList.append(f" {keyName} = %s ")
        else:
            aList.append(f" OR {keyName} = %s ")
        count += 1
    aList.append(") ")
    result = "".join(aList)
    return result

#common end
    
    
#user family begin
def createUserBasic():
    tableName = "USER_BASIC"
    aList  = ["CREATE TABLE IF NOT EXISTS %s("
    "loginID VARCHAR(32) PRIMARY KEY COMMENT '用户登录号',",
    "passwd VARCHAR(80) COMMENT '用户密码',",
    "openID VARCHAR(40) COMMENT '微信openID',",
    "roleName VARCHAR(16) COMMENT '角色名称',",
    "nickName VARCHAR(40) COMMENT '昵称',",
    "realName VARCHAR(40) COMMENT '用户真实姓名' ,",
    "gender CHAR(1) COMMENT '性别',",
    "avatarID VARCHAR(200) COMMENT '头像ID',",
    "mobilePhoneNo VARCHAR(32) COMMENT '手机号',",
    "masterID VARCHAR(32) COMMENT '用户主号',",
    "province VARCHAR(32) COMMENT '省',",
    "city VARCHAR(32) COMMENT '市',",
    "area VARCHAR(32) COMMENT '地区',",
    "address VARCHAR(200) COMMENT '地址',",
    "email VARCHAR(100) COMMENT '用户邮箱',",
    "PID VARCHAR(20) COMMENT '用户身份证号',",
    "photoIDFront VARCHAR(128) COMMENT '用户身份证头像侧',",
    "photoIDBack VARCHAR(128) COMMENT '用户身份证背面',",
    "photoID VARCHAR(128) COMMENT '用户照片',",
    "delFlag CHAR(1) COMMENT '删除标记',",
    "activeFlag CHAR(1) COMMENT '活动标记',",
    "regPosition VARCHAR(80) COMMENT '注册位置',",
    "regID VARCHAR(32) COMMENT '注册ID',",
    "regYMDHMS VARCHAR(16) COMMENT '注册年月日',",
    "updateYMDHMS VARCHAR(16) COMMENT '数据更新日期',",
    "lastOpenID VARCHAR(40) COMMENT '用户最后一次登录openID',",
    "lastLoginYMDHMS VARCHAR(16) COMMENT '用户最后一次登录年月日',",
    "modifyID VARCHAR(32) COMMENT '修改用户ID',",
    "modifyYMDHMS VARCHAR(16) COMMENT '修改年月日',",
    "passwdYMDHMS VARCHAR(16) COMMENT '密码修改年月日',",
    "extSessionID VARCHAR(48) COMMENT '扩展用户sessionID',",
    "extCapital float COMMENT '扩展用户资金',",
    "extStartYMDHMS VARCHAR(16) COMMENT '扩展开始年月日',",
    "extLeaveYMDHMS VARCHAR(16) COMMENT '扩展停止年月日',",
    "extJobPosition VARCHAR(100) COMMENT '扩展职位',",
    "extDepartment VARCHAR(100) COMMENT '扩展部门',",
    "extOrgName VARCHAR(300) COMMENT '扩展组织名称',",
    "extOrgID INT COMMENT '扩展组织ID',",
    "extInService VARCHAR(1) COMMENT '扩展是否在职',",
    "extJobLabel VARCHAR(16) COMMENT '扩展职位身份标签_注册用户_区域用户_后台用户',",
    "extJobDetail VARCHAR(64) COMMENT '扩展职位细节_例如是工信厅卫生局等',",
    "extBrief VARCHAR(1000) COMMENT '扩展人员简介_专家简介_区域管理员类别',",
    "extManualTagList VARCHAR(500) COMMENT '扩展标签列表',",
    "extManagementAreaList VARCHAR(500) COMMENT '扩展管理区域',",
    "extMemo VARCHAR(100) COMMENT '扩展备注'"
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;" , 
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        sqlStr = "CREATE INDEX {1} ON {0}({1})".format(tableName, "roleName")
        rtn = mysqlDB.executeWrite(sqlStr)
        sqlStr = "CREATE INDEX {1} ON {0}({1})".format(tableName, "extJobLabel")
        rtn = mysqlDB.executeWrite(sqlStr)

    return result


def dropUserBasic():
    tableName = "USER_BASIC"
    result = dropTableGeneral(tableName)
    return result


#以后这个是标准写法,利用fetchMany来处理数据
#SELECT * FROM USER_BASIC WHERE loginID = "13910710766";
def queryUserBasic(loginID = "" , name = "", mobile = "", manualTag = "",jobLabel="",
                   searchOption = {},  roleName = "", roleNameList = [],  keyword="",
                   mode = "normal", beginYMD = "",endYMD = "", 
                   order="create", limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    tableName = "USER_BASIC"

    if mode =="short":
        columns = "loginID,nickName,realName,roleName, avatarID"
    elif mode =="normal":
        columns = "loginID,nickName,realName,roleName,avatarID,openID,masterID,mobilePhoneNo,province,city,area, address, email, regYMDHMS, updateYMDHMS"
    else:
        columns = "*"
    valuesList = [] 
    sqlStr =   "SELECT %s FROM %s " % (columns, tableName )

    try:
        if loginID:
            sqlStr += " WHERE loginID = %s"
            valuesList = [loginID]
        else:
            valuesList = []
            #以下 searchOption,roleName,roleNameList是并列关系,只能选一个
            if searchOption:
                if valuesList:
                    whereStr = " AND "
                else:
                    whereStr = " WHERE "
                logic = searchOption.get("logic", "AND")
                optionList = searchOption.get("optionList", [])
                count = 0
                for optionSet in optionList:
                    if count > 0:
                        whereStr += " " + logic + " "
                    if "realName" in optionSet:
                        whereStr += " realName = %s" 
                        valuesList.append(optionSet["realName"])
                    if "nickName" in optionSet:
                        whereStr += " nickName = %s" 
                        valuesList.append(optionSet["nickName"])
                    if "loginID" in optionSet:
                        whereStr += " loginID = %s" 
                        valuesList.append(optionSet["loginID"])
                    if "roleName" in optionSet:
                        whereStr += " roleName = %s" 
                        valuesList.append(optionSet["roleName"])
                    if "province" in optionSet:
                        whereStr += " province = %s" 
                        valuesList.append(optionSet["province"])
                    count += 1
                sqlStr += whereStr 
                
            elif jobLabel:
                if valuesList:
                    whereStr = " AND extJobLabel = %s "
                else:
                    whereStr = " WHERE extJobLabel = %s "
                valuesList.append(jobLabel)
                sqlStr += whereStr 

            elif roleName:
                if valuesList:
                    whereStr = " AND roleName = %s "
                else:
                    whereStr = " WHERE roleName = %s "
                valuesList.append(roleName)
                sqlStr += whereStr 

            elif roleNameList:
                if valuesList:
                    whereStr = " AND " + genOrList(roleNameList, "roleName")
                else:
                    whereStr = " WHERE " + genOrList(roleNameList, "roleName")
                valuesList += roleNameList
                sqlStr += whereStr 
            
            if keyword:
                if valuesList:
                    sqlStr =  sqlStr + " AND (locate(%s,realName) OR locate(%s,nickName) OR locate(%s,extJobPosition) OR locate(%s,extJobDetail) OR locate(%s,extOrgName) OR locate(%s,loginID) )" 
                else:
                    sqlStr =  sqlStr + " WHERE (locate(%s,realName) OR locate(%s,nickName) OR locate(%s,extJobPosition) OR locate(%s,extJobDetail) OR locate(%s,extOrgName) OR locate(%s,loginID) )" 
                valuesList.append(keyword)
                valuesList.append(keyword)
                valuesList.append(keyword)
                valuesList.append(keyword)
                valuesList.append(keyword)
                valuesList.append(keyword)

            # beginYMD 和 endYMD可以和上面混用
            if beginYMD  and endYMD :
                beginYMDHMS = beginYMD + "000000"
                endYMDHMS = endYMD + "240000"
                if valuesList:
                    whereStr = " AND regYMDHMS >= %s and regYMDHMS <= %s "
                else:
                    whereStr = " WHERE regYMDHMS >= %s and regYMDHMS <= %s "
                sqlStr = sqlStr + " WHERE regYMDHMS >= %s and regYMDHMS <= %s " 
                valuesList += [beginYMDHMS, endYMDHMS] 
                                
        if order == "create":
            sqlStr += " ORDER BY regYMDHMS DESC"
        
        #其他过滤数据的在这里
        if name or mobile or manualTag:
            #分批次获取数据并挑选数据
            rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
            if rtn:
                batchNum = 1000
                total = 0
                while True:
                    dataList = mysqlDB.fetchMany(batchNum)
                    dataList = dataFormatConvert(dataList)
                
                    for data in dataList:
                        matchFlag = False

                        if mobile:
                            keyword = mobile
                            keyList = ["mobilePhoneNo","loginID"]
                            for key in keyList:
                                currVal = data.get(key)
                                if currVal:
                                    if currVal.find(keyword) >= 0:
                                        matchFlag = True
                                        break
                        if name:
                            keyword = name
                            keyList = ["roleName","nickName","realName"]
                            for key in keyList:
                                currVal = data.get(key)
                                if currVal:
                                    if currVal.find(keyword) >= 0:
                                        matchFlag = True
                                        break

                        if matchFlag:
                            result.append(data)

                    #final
                    #如果取不到更多数据就退出
                    currDataLen = len(dataList)
                    if currDataLen < batchNum:
                        break
                    
                    #如果取到的数据满足要求也退出,limitNUm = 0 是提取全部满足条件数据
                    if limitNum > 0:
                        total = len(result)
                        if total >= limitNum:
                            result = result[0:limitNum]
                            break
        else:
            if limitNum > 0:
                sqlStr += " LIMIT {0}".format(limitNum)

            rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
            if rtn > 0:
                dataList = mysqlDB.fetchAll()
                dataList = dataFormatConvert(dataList)

                result = dataList

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
#        if _DEBUG:
#            _LOG.error(f"{errMsg}")

    return result

    
#SELECT * FROM USER_BASIC WHERE loginID = "13910710766";
def deleteUserBasic(loginID):
    result = 0
    tableName = "USER_BASIC"
    try:
    
        sqlStr = "DELETE FROM %s WHERE loginID = \"%s\";" % (tableName, loginID)
        rtn = mysqlDB.executeWrite(sqlStr)
        result = rtn

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
#        if _DEBUG:
#            _LOG.error(f"{errMsg}")

    return result
    
    
def insertUserBasic(loginID, dataSet):
    result = 0
    tableName = "USER_BASIC"
    try:
        saveSet = {}
        saveSet["loginID"]  = loginID

        saveSet["passwd"] = dataSet.get("passwd", "") 

        saveSet["openID"] = dataSet.get("openID", "") 

        saveSet["roleName"] = dataSet.get("roleName", "") 

        saveSet["nickName"] = dataSet.get("nickName", "") 

        saveSet["realName"] = dataSet.get("realName", "") 

        saveSet["gender"] = dataSet.get("gender", "") 

        saveSet["avatarID"] = dataSet.get("avatarID", "") 

        saveSet["mobilePhoneNo"] = dataSet.get("mobilePhoneNo", "") 

        saveSet["masterID"] = dataSet.get("masterID", "") 

        saveSet["province"] = dataSet.get("province", "") 

        saveSet["city"] = dataSet.get("city", "") 

        saveSet["area"] = dataSet.get("area", "") 

        saveSet["address"] = dataSet.get("address", "") 

        saveSet["email"] = dataSet.get("email", "") 

        saveSet["PID"] = dataSet.get("PID", "") 

        saveSet["photoIDFront"] = dataSet.get("photoIDFront", "") 

        saveSet["photoIDBack"] = dataSet.get("photoIDBack", "") 

        saveSet["photoID"] = dataSet.get("photoID", "") 

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        saveSet["activeFlag"] = dataSet.get("activeFlag", comGD._CONST_YES) 

        regPosition = dataSet.get("regPosition", {})
        if (regPosition != {}):
            #双引号的特殊处理
            saveSet["regPosition"]  = misc.jsonDumps(regPosition).replace("\"", "'")
        else:
            saveSet["regPosition"] = misc.jsonDumps({})

        saveSet["regID"] = dataSet.get("regID", "") 

        saveSet["regYMDHMS"] = dataSet.get("regYMDHMS", "") 

        saveSet["updateYMDHMS"] = dataSet.get("updateYMDHMS", "") 

        saveSet["lastOpenID"] = dataSet.get("lastOpenID", "") 

        saveSet["lastLoginYMDHMS"] = dataSet.get("lastLoginYMDHMS", "") 

        saveSet["passwdYMDHMS"] = dataSet.get("passwdYMDHMS", "") 

        # extend items begin, per project
        
        saveSet["extSessionID"] = dataSet.get("extSessionID", "") 

        try:
            extCapital = float(dataSet.get("extCapital")) 
        except:
            extCapital = 0.0 
        saveSet["extCapital"] = extCapital

        saveSet["extStartYMDHMS"] = dataSet.get("extStartYMDHMS", "") 

        saveSet["extStartYMDHMS"] = dataSet.get("extStartYMDHMS", "") 

        saveSet["extLeaveYMDHMS"] = dataSet.get("extLeaveYMDHMS", "") 

        saveSet["extJobPosition"] = dataSet.get("extJobPosition", "") 

        saveSet["extDepartment"] = dataSet.get("extDepartment", "") 

        saveSet["extOrgName"] = dataSet.get("extOrgName", "") 

        try:
            extOrgID = int(dataSet.get("extOrgID")) 
        except:
            extOrgID = 0 
        saveSet["extOrgID"] = extOrgID

        saveSet["extInService"] = dataSet.get("extInService", "") 

        saveSet["extJobLabel"] = dataSet.get("extJobLabel", "") 

        saveSet["extJobDetail"] = dataSet.get("extJobDetail", "") 

        saveSet["extBrief"] = dataSet.get("extBrief", "") 

        saveSet["extManualTagList"] = dataSet.get("extManualTagList", "") 

        saveSet["extManagementAreaList"] = dataSet.get("extManagementAreaList", "") 

        saveSet["extMemo"] = dataSet.get("extMemo", "") 
        # extend items end, per project

        result = insertTableGeneral(tableName, saveSet, selfDefinedPrimaryKey = comGD._CONST_YES)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
#        if _DEBUG:
#            _LOG.error(f"{errMsg}")

    return result
    
    
def updateUserBasic(loginID, dataSet):
    result = 0
    tableName = "USER_BASIC"
    try:
        saveSet = {}
        
        passwd = dataSet.get("passwd")
        if passwd != "" and passwd:
            saveSet["passwd"] = passwd
            
        openID = dataSet.get("openID", "")
        if openID != "":
            saveSet["openID"] = openID

        roleName = dataSet.get("roleName", "")
        if roleName != "":
            saveSet["roleName"] = roleName

        nickName = dataSet.get("nickName", "")
        if nickName != "":
            saveSet["nickName"] = nickName

        realName = dataSet.get("realName", "")
        if realName != "":
            saveSet["realName"] = realName

        gender = dataSet.get("gender", "")
        if gender != "":
            saveSet["gender"] = gender

        avatarID = dataSet.get("avatarID", "")
        if avatarID != "":
            saveSet["avatarID"] = avatarID

        mobilePhoneNo = dataSet.get("mobilePhoneNo", "")
        if mobilePhoneNo != "":
            saveSet["mobilePhoneNo"] = mobilePhoneNo

        province = dataSet.get("province", "")
        if province != "":
            saveSet["province"] = province
            
        masterID = dataSet.get("masterID", "")
        if masterID != "":
            saveSet["masterID"] = masterID
            
        city = dataSet.get("city", "")
        if city != "":
            saveSet["city"] = city
            
        area = dataSet.get("area", "")
        if area != "":
            saveSet["area"] = area
            
        address = dataSet.get("address", "")
        if address != "":
            saveSet["address"] = address
            
        email = dataSet.get("email", "")
        if email != "":
            saveSet["email"] = email
            
        PID = dataSet.get("PID", "")
        if PID != "":
            saveSet["PID"] = PID
            
        photoIDFront = dataSet.get("photoIDFront", "")
        if photoIDFront != "":
            saveSet["photoIDFront"] = photoIDFront
            
        photoIDBack = dataSet.get("photoIDBack", "")
        if photoIDBack != "":
            saveSet["photoIDBack"] = photoIDBack
            
        photoIDBack = dataSet.get("photoIDBack", "")
        if photoIDBack != "":
            saveSet["photoIDBack"] = photoIDBack
            
        photoID = dataSet.get("photoID", "")
        if photoID != "":
            saveSet["photoID"] = photoID

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            if delFlag != "1":
                delFlag = "0"
            saveSet["delFlag"] = delFlag

        activeFlag = dataSet.get("activeFlag")
        if activeFlag:
            saveSet["activeFlag"] = activeFlag

        regPosition = dataSet.get("regPosition", {})
        if (regPosition != {}):
            #双引号的特殊处理
            saveSet["regPosition"] = misc.jsonDumps(regPosition).replace("\"", "'")

        updateYMDHMS = dataSet.get("updateYMDHMS", "")
        if updateYMDHMS != "":
            saveSet["updateYMDHMS"] = updateYMDHMS
        lastOpenID = dataSet.get("lastOpenID", "")

        if lastOpenID != "":
            saveSet["lastOpenID"] = lastOpenID

        lastLoginYMDHMS = dataSet.get("lastLoginYMDHMS", "")
        if lastLoginYMDHMS != "":
            saveSet["lastLoginYMDHMS"] = lastLoginYMDHMS

        modifyID = dataSet.get("modifyID")
        if modifyID != "":
            saveSet["modifyID"] = modifyID

        modifyYMDHMS = dataSet.get("modifyYMDHMS", "")
        if modifyYMDHMS != "":
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        passwdYMDHMS = dataSet.get("passwdYMDHMS", "")
        if passwdYMDHMS != "":
            saveSet["passwdYMDHMS"] = passwdYMDHMS
    
        # extend items begin, per project

        extSessionID = dataSet.get("extSessionID") 
        if extSessionID:
            saveSet["extSessionID"] = extSessionID
            
        try:
            extCapital = float(dataSet.get("extCapital")) 
        except:
            extCapital = 0.0 
        saveSet["extCapital"] = extCapital

        extStartYMDHMS = dataSet.get("extStartYMDHMS") 
        if extStartYMDHMS:
            saveSet["extStartYMDHMS"] = extStartYMDHMS

        extLeaveYMDHMS = dataSet.get("extLeaveYMDHMS") 
        if extLeaveYMDHMS:
            saveSet["extLeaveYMDHMS"] = extLeaveYMDHMS

        extJobPosition = dataSet.get("extJobPosition") 
        if extJobPosition:
            saveSet["extJobPosition"] = extJobPosition

        extDepartment = dataSet.get("extDepartment") 
        if extDepartment:
            saveSet["extDepartment"] = extDepartment

        extOrgName = dataSet.get("extOrgName") 
        if extOrgName:
            saveSet["extOrgName"] = extOrgName

        extOrgID = dataSet.get("extOrgID") 
        if extOrgID:
            try:
                extOrgID = int(dataSet.get("extOrgID")) 
                saveSet["extOrgID"] = extOrgID
            except:
                pass

        extInService = dataSet.get("extInService") 
        if extInService:
            saveSet["extInService"] = extInService

        extJobLabel = dataSet.get("extJobLabel") 
        if extJobLabel:
            saveSet["extJobLabel"] = extJobLabel

        extJobDetail = dataSet.get("extJobDetail") 
        if extJobDetail:
            saveSet["extJobDetail"] = extJobDetail

        extBrief = dataSet.get("extBrief") 
        if extBrief:
            saveSet["extBrief"] = extBrief

        extManualTagList = dataSet.get("extManualTagList") 
        if extManualTagList:
            saveSet["extManualTagList"] = extManualTagList

        extManagementAreaList = dataSet.get("extManagementAreaList") 
        if extManagementAreaList:
            saveSet["extManagementAreaList"] = extManagementAreaList

        extMemo = dataSet.get("extMemo") 
        if extMemo:
            saveSet["extMemo"] = extMemo

        # extend items end, per project

        keySqlstr = "loginID = %s" 
        keyValues = [loginID]
        
        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)
        
    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
#        if _DEBUG:
#            _LOG.error(f"{errMsg}")

    return result


#获取本地用户信息mysql
def getUserInfoMysql(loginID):
    result = {}
    try:
        mode = "full"
        currDataList = queryUserBasic(loginID,mode = mode)

        if currDataList:
            currDataSet = currDataList[0]

            aSet = {}

            aSet["loginID"] = currDataSet.get("loginID","")
            # aSet["openID"] = currDataSet.get("openID","")
            aSet["roleName"] = currDataSet.get("roleName","")
            aSet["nickName"] = currDataSet.get("nickName","")
            aSet["realName"] = currDataSet.get("realName","")
            aSet["gender"] = currDataSet.get("gender","")

            aSet["avatarID"] = currDataSet.get("avatarID","")

            aSet["mobilePhoneNo"] = currDataSet.get("mobilePhoneNo","")
            aSet["masterID"] = currDataSet.get("masterID","")
            aSet["province"] = currDataSet.get("province","")
            aSet["city"] = currDataSet.get("city","")
            aSet["area"] = currDataSet.get("area","")
            aSet["address"] = currDataSet.get("address","")
            aSet["email"] = currDataSet.get("email","")
            aSet["PID"] = currDataSet.get("PID","")
            aSet["activeFlag"] = currDataSet.get("activeFlag","")

            # photoIDFront = currDataSet.get("photoIDFront","")
            # if photoIDFront:
            #     photoIDFront = getTempLocation(photoIDFront, privateFlag = True)
            # aSet["photoIDFront"] = photoIDFront

            # photoIDBack = currDataSet.get("photoIDBack","")
            # if photoIDBack:
            #     photoIDBack = getTempLocation(photoIDBack, privateFlag = True)
            # aSet["photoIDBack"] = photoIDBack

            # photoID = currDataSet.get("photoID","")
            # if photoID:
            #     photoID = getTempLocation(photoID, privateFlag = True)
            # aSet["photoID"] = photoID

            # aSet["delFlag"] = currDataSet.get("delFlag","")
            aSet["regPosition"] = currDataSet.get("regPosition","")
            aSet["regID"] = currDataSet.get("regID","")
            aSet["regYMDHMS"] = currDataSet.get("regYMDHMS","")
            aSet["updateYMDHMS"] = currDataSet.get("updateYMDHMS","")
            # aSet["lastOpenID"] = currDataSet.get("lastOpenID","")
            aSet["lastLoginYMDHMS"] = currDataSet.get("lastLoginYMDHMS","")
            aSet["modifyID"] = currDataSet.get("modifyID","")
            aSet["modifyYMDHMS"] = currDataSet.get("modifyYMDHMS","")
            # aSet["passwdYMDHMS"] = currDataSet.get("passwdYMDHMS","")

            # extend items begin, per project
            aSet["extSessionID"] = currDataSet.get("extSessionID","")
            
            try:
                extCapital = float(currDataSet.get("extCapital")) 
            except:
                extCapital = 0.0 
            aSet["extCapital"] = extCapital
            
            aSet["extStartYMDHMS"] = currDataSet.get("extStartYMDHMS","")
            aSet["extLeaveYMDHMS"] = currDataSet.get("extLeaveYMDHMS","")
            aSet["extJobPosition"] = currDataSet.get("extJobPosition","")
            aSet["extDepartment"] = currDataSet.get("extDepartment","")
            aSet["extOrgName"] = currDataSet.get("extOrgName","")
            aSet["extOrgID"] = currDataSet.get("extOrgID","")

            aSet["extInService"] = currDataSet.get("extInService","")
            # aSet["extInService"] = chkIsInService(aSet["extInService"],aSet["activeFlag"])

            aSet["extJobLabel"] = currDataSet.get("extJobLabel","")
            aSet["extJobDetail"] = currDataSet.get("extJobDetail","")
            aSet["extBrief"] = currDataSet.get("extBrief","")

            #list/dict处理
            extManualTagList = currDataSet.get("extManualTagList")
            try:
                extManualTagList = misc.jsonLoads(extManualTagList)
            except:
                extManualTagList = []
            aSet["extManualTagList"] = extManualTagList

            #list/dict处理
            extManagementAreaList = currDataSet.get("extManagementAreaList")
            try:
                extManagementAreaList = misc.jsonLoads(extManagementAreaList)
            except:
                extManagementAreaList = []
            aSet["extManagementAreaList"] = extManagementAreaList
            aSet["extMemo"] = currDataSet.get("extMemo","")
            # extend items end, per project

            result = aSet
    except:
        pass
    return result


#champion only 
def statUserBasic(statBy = "roleName", beginYMD = "",endYMD = ""):
    result = []
    tableName = "USER_BASIC"

    valuesList = []

    try:
        if statBy == "roleName":
            sqlStr = f"SELECT count(loginID) as total, roleName FROM {tableName} "

            if beginYMD:
                beginYMDHMS = beginYMD + "000000"
                if valuesList:
                    sqlStr += " AND regYMDHMS >= % " 
                else:
                    sqlStr += " WHERE regYMDHMS >= % " 
                valuesList.append(beginYMDHMS)

            if endYMD:
                endYMDHMS = endYMD + "240000"
                if valuesList:
                    sqlStr += " AND regYMDHMS <= % " 
                else:
                    sqlStr += " WHERE regYMDHMS <= % " 
                valuesList.append(endYMDHMS)
            
            sqlStr += " GROUP BY roleName"
        else:
            sqlStr = f"SELECT count(loginID) as total FROM {tableName}"

            if beginYMD:
                beginYMDHMS = beginYMD + "000000"
                if valuesList:
                    sqlStr += " AND regYMDHMS >= % " 
                else:
                    sqlStr += " WHERE regYMDHMS >= % " 
                valuesList.append(beginYMDHMS)

            if endYMD:
                endYMDHMS = endYMD + "240000"
                if valuesList:
                    sqlStr += " AND regYMDHMS <= % " 
                else:
                    sqlStr += " WHERE regYMDHMS <= % " 
                valuesList.append(endYMDHMS)
            
        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            result = dataList

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
#        if _DEBUG:
#            _LOG.error(f"{errMsg}")

    return result

#user family end


#wechat code  family begin
def createUserWechatCode():
    tableName = "USER_weChatCode"
    aList  = ["CREATE TABLE IF NOT EXISTS %s("
    "id INT AUTO_INCREMENT PRIMARY KEY,", 
    "loginID VARCHAR(32) NOT NULL,", 
    "openID VARCHAR(40) NOT NULL,", 
    "YMDHMS VARCHAR(16) ,", 
    "index (loginID, openID)", 
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;" , 
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    return result


def dropUserWechatCode():
    tableName = "USER_weChatCode"
    result = dropTableGeneral(tableName)
    return result
    

#SELECT * FROM USER_weChatCode WHERE loginID = "13910710766";
def queryUserWechatCode(loginID,  openID = ""):
    result = []
    tableName = "USER_weChatCode"
    try:

        if loginID == "" and openID != "":
            sqlStr = "SELECT * FROM %s WHERE openID = \"%s\";" % (tableName, openID)              
        elif loginID != "" and openID != "":
            sqlStr = "SELECT * FROM %s WHERE loginID = \"%s\" and openID = \"%s\";" % (tableName, loginID, openID) 
        else:
            sqlStr = "SELECT * FROM %s WHERE loginID = \"%s\";" % (tableName, loginID)
            
        rtn = mysqlDB.executeRead(sqlStr)
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            result = list(dataList)        
                
    except:
        pass
    return result
    
    
#DELETE  FROM USER_weChatCode WHERE loginID = "13910710766";
def deleteUserWechatCode(loginID, openID = ""):
    result = 0
    tableName = "USER_weChatCode"
    try:

        if openID == "":
            sqlStr = "DELETE FROM %s WHERE loginID = \"%s\";" % (tableName, loginID)
        else:
            sqlStr = "DELETE FROM %s WHERE loginID = \"%s\" and openID = \"%s\";" % (tableName, loginID, openID)                
        rtn = mysqlDB.executeWrite(sqlStr)
        result = rtn

    except:
        pass
    return result
    
    
def insertUserWechatCode(loginID, dataSet):
    result = 0
    tableName = "USER_weChatCode"
    try:
        saveSet = {}
        saveSet["loginID"]  = loginID

        openID = dataSet.get("openID", "")
        saveSet["openID"]  = openID

        YMDHMS = dataSet.get("YMDHMS", "")
        if (YMDHMS != ""):
            saveSet["YMDHMS"]  = YMDHMS

        result = insertTableGeneral(tableName, saveSet)
    except:
        pass
    return result
    
    
def updateUserWechatCode(loginID, dataSet):
    result = 0
    tableName = "USER_weChatCode"
    try:
        saveSet = {}
        
        openID = dataSet.get("openID", "")

        YMDHMS = dataSet.get("YMDHMS","")
        if YMDHMS != "":
            saveSet["YMDHMS"] = YMDHMS
            
        keyOption = ("loginID = \"%s\" and openID = \"%s\"" %(loginID, openID))
            
        result = updateTableGeneral(tableName, keyOption , saveSet)
    except:
        pass
    return result
#wechat code  family end


#application begin


#hwinfo_report_record begin 

def tablename_convertor_hwinfo_report_record(dataSource=""):
    if dataSource:
        tableName = "hwinfo_report_record" + "_" + dataSource
    else:
        tableName = "hwinfo_report_record"
    tableName = tableName.lower()
    return tableName


def decode_tablename_hwinfo_report_record(tableName):
    result = {}
    aList = tableName.split("_")
    
    return result


#创建hwinfo_report_record表
def create_hwinfo_report_record(tableName):
    aList = ["CREATE TABLE IF NOT EXISTS %s("
    "recID INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录号',",
    "hostName VARCHAR(64) COMMENT '主机名称',",
    "description VARCHAR(64) COMMENT '主机描述',",
    "IP VARCHAR(16) COMMENT 'IP地址',",
    "IPs VARCHAR(1000) COMMENT 'IP地址集合',",
    "os VARCHAR(32) COMMENT '操作系统',",
    "osVersion VARCHAR(64) COMMENT '操作系统版本',",
    "mac VARCHAR(20) COMMENT 'mac地址',",
    "cpuCount INT COMMENT 'CPU核心数',",
    "cpuLoad INT COMMENT 'CPU占用百分比',",
    "RAMTotal VARCHAR(8) COMMENT 'RAM total',",
    "RAMUsed VARCHAR(8) COMMENT 'RAM used',",
    "RAMFree VARCHAR(8) COMMENT 'RAM free',",
    "RAMPercent INT COMMENT 'RAM占用百分比',",
    "disk VARCHAR(1000) COMMENT 'disk描述',",
    "diskTotal VARCHAR(8) COMMENT '硬盘总容量',",
    "diskUsed VARCHAR(8) COMMENT '硬盘使用量',",
    "diskPercent INT COMMENT '硬盘使用百分比',",
    "processorInfo VARCHAR(1000) COMMENT '进程描述',",
    "addtionalInfo VARCHAR(5000) COMMENT '额外信息',",
    "YMDHMS VARCHAR(16) COMMENT '数据年月日',",
    "label1 VARCHAR(32) NULL,",
    "label2 VARCHAR(32) NULL,",
    "label3 VARCHAR(32) NULL,",
    "memo VARCHAR(200) NULL,",
    "regID VARCHAR(32) NOT NULL COMMENT '注册ID',",
    "regYMDHMS VARCHAR(16) NOT NULL COMMENT '注册年月日',",
    "modifyID VARCHAR(32) COMMENT '修改ID',",
    "modifyYMDHMS VARCHAR(16) COMMENT '数据修改年月日',",
    "dispFlag VARCHAR(1) COMMENT '是否显示标记',",
    "delFlag VARCHAR(1) COMMENT '是否删除标记'"
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        #sqlStr = "CREATE INDEX {1} ON {0}({1}) ".format(tableName, "indexKey")
        #rtn = mysqlDB.executeWrite(sqlStr)
        #sqlStr = "ALTER TABLE {0} auto_increment = {1} ".format(tableName,auto_increment_default_value)
        #rtn = mysqlDB.executeWrite(sqlStr)

    return result


#删除hwinfo_report_record表
def drop_hwinfo_report_record(tableName):
    result = dropTableGeneral(tableName)
    return result


#hwinfo_report_record 删除记录
def delete_hwinfo_report_record(tableName,recID):
    result = 0
    sqlStr = f"DELETE FROM {tableName}"
    try:

        sqlStr += " WHERE recID = %s"
        valuesList = [recID] 
        result = mysqlDB.executeWrite(sqlStr,tuple(valuesList))

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#hwinfo_report_record 增加记录
def insert_hwinfo_report_record(tableName,dataSet):
    result = 0
    try:

        saveSet = {}

        saveSet["hostName"] = dataSet.get("hostName", "") 

        saveSet["description"] = dataSet.get("description", "") 

        saveSet["IP"] = dataSet.get("IP", "") 

        saveSet["IPs"] = dataSet.get("IPs", "") 

        saveSet["os"] = dataSet.get("os", "") 

        saveSet["osVersion"] = dataSet.get("osVersion", "") 

        saveSet["mac"] = dataSet.get("mac", "") 

        try:
            cpuCount = int(dataSet.get("cpuCount")) 
        except:
            cpuCount = 0 
        saveSet["cpuCount"] = cpuCount

        try:
            cpuLoad = int(dataSet.get("cpuLoad")) 
        except:
            cpuLoad = 0 
        saveSet["cpuLoad"] = cpuLoad

        saveSet["RAMTotal"] = dataSet.get("RAMTotal", "") 

        saveSet["RAMUsed"] = dataSet.get("RAMUsed", "") 

        saveSet["RAMFree"] = dataSet.get("RAMFree", "") 

        try:
            RAMPercent = int(dataSet.get("RAMPercent")) 
        except:
            RAMPercent = 0 
        saveSet["RAMPercent"] = RAMPercent

        saveSet["disk"] = dataSet.get("disk", "") 

        saveSet["diskTotal"] = dataSet.get("diskTotal", "") 

        saveSet["diskUsed"] = dataSet.get("diskUsed", "") 

        try:
            diskPercent = int(dataSet.get("diskPercent")) 
        except:
            diskPercent = 0 
        saveSet["diskPercent"] = diskPercent

        saveSet["processorInfo"] = dataSet.get("processorInfo", "") 

        saveSet["addtionalInfo"] = dataSet.get("addtionalInfo", "") 

        saveSet["YMDHMS"] = dataSet.get("YMDHMS", "") 

        saveSet["label1"] = dataSet.get("label1", "") 

        saveSet["label2"] = dataSet.get("label2", "") 

        saveSet["label3"] = dataSet.get("label3", "") 

        saveSet["memo"] = dataSet.get("memo", "") 

        saveSet["regID"] = dataSet.get("regID", "") 

        saveSet["regYMDHMS"] = dataSet.get("regYMDHMS", "") 

        saveSet["dispFlag"] = dataSet.get("dispFlag", "") 

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        result = insertTableGeneral(tableName, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#hwinfo_report_record 修改记录
def update_hwinfo_report_record(tableName,recID,dataSet):
    result = -2
    try:
        saveSet = {}

        hostName = dataSet.get("hostName") 
        if hostName:
            saveSet["hostName"] = hostName

        description = dataSet.get("description") 
        if description:
            saveSet["description"] = description

        IP = dataSet.get("IP") 
        if IP:
            saveSet["IP"] = IP

        IPs = dataSet.get("IPs") 
        if IPs:
            saveSet["IPs"] = IPs

        os = dataSet.get("os") 
        if os:
            saveSet["os"] = os

        osVersion = dataSet.get("osVersion") 
        if osVersion:
            saveSet["osVersion"] = osVersion

        mac = dataSet.get("mac") 
        if mac:
            saveSet["mac"] = mac

        try:
            cpuCount = int(dataSet.get("cpuCount")) 
            saveSet["cpuCount"] = cpuCount
        except:
            pass

        try:
            cpuLoad = int(dataSet.get("cpuLoad")) 
            saveSet["cpuLoad"] = cpuLoad
        except:
            pass

        RAMTotal = dataSet.get("RAMTotal") 
        if RAMTotal:
            saveSet["RAMTotal"] = RAMTotal

        RAMUsed = dataSet.get("RAMUsed") 
        if RAMUsed:
            saveSet["RAMUsed"] = RAMUsed

        RAMFree = dataSet.get("RAMFree") 
        if RAMFree:
            saveSet["RAMFree"] = RAMFree

        try:
            RAMPercent = int(dataSet.get("RAMPercent")) 
            saveSet["RAMPercent"] = RAMPercent
        except:
            pass

        disk = dataSet.get("disk") 
        if disk:
            saveSet["disk"] = disk

        diskTotal = dataSet.get("diskTotal") 
        if diskTotal:
            saveSet["diskTotal"] = diskTotal

        diskUsed = dataSet.get("diskUsed") 
        if diskUsed:
            saveSet["diskUsed"] = diskUsed

        try:
            diskPercent = int(dataSet.get("diskPercent")) 
            saveSet["diskPercent"] = diskPercent
        except:
            pass

        processorInfo = dataSet.get("processorInfo") 
        if processorInfo:
            saveSet["processorInfo"] = processorInfo

        addtionalInfo = dataSet.get("addtionalInfo") 
        if addtionalInfo:
            saveSet["addtionalInfo"] = addtionalInfo

        YMDHMS = dataSet.get("YMDHMS") 
        if YMDHMS:
            saveSet["YMDHMS"] = YMDHMS

        label1 = dataSet.get("label1") 
        if label1:
            saveSet["label1"] = label1

        label2 = dataSet.get("label2") 
        if label2:
            saveSet["label2"] = label2

        label3 = dataSet.get("label3") 
        if label3:
            saveSet["label3"] = label3

        memo = dataSet.get("memo") 
        if memo:
            saveSet["memo"] = memo

        modifyID = dataSet.get("modifyID") 
        if modifyID:
            saveSet["modifyID"] = modifyID

        modifyYMDHMS = dataSet.get("modifyYMDHMS") 
        if modifyYMDHMS:
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        dispFlag = dataSet.get("dispFlag") 
        if dispFlag:
            saveSet["dispFlag"] = dispFlag

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            saveSet["delFlag"] = delFlag

        keySqlstr = "recID = %s"
        keyValues = [recID]

        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#hwinfo_report_record 查询记录
def query_hwinfo_report_record(tableName,recID = "0", hostName = "", YMDHMS="", beginYMDHMS="", endYMDHMS="", sortFlag = "DESC",
                               delFlag = "0", mode = "full",limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    columns = "*"
    valuesList = []
    sqlStr = f"SELECT {columns} FROM {tableName}"

    try:

        try:
            recID = int(recID)
        except:
            recID = 0

        if recID > 0:
            sqlStr =  sqlStr + " WHERE recID = %s" 
            valuesList = [recID]  
        else:
            if hostName:
                if valuesList:
                    sqlStr =  sqlStr + " AND hostName = %s" 
                else:
                    sqlStr =  sqlStr + " WHERE hostName = %s" 
                valuesList.append(hostName)
            if YMDHMS:
                if valuesList:
                    sqlStr =  sqlStr + " AND YMDHMS <= %s"
                else:
                    sqlStr =  sqlStr + " WHERE YMDHMS <= %s"
                valuesList.append(YMDHMS)            
            if beginYMDHMS:
                if valuesList:
                    sqlStr =  sqlStr + " AND YMDHMS >= %s"
                else:
                    sqlStr =  sqlStr + " WHERE YMDHMS >= %s"
                valuesList.append(beginYMDHMS)            
            if endYMDHMS:
                if valuesList:
                    sqlStr =  sqlStr + " AND YMDHMS < %s"
                else:
                    sqlStr =  sqlStr + " WHERE YMDHMS < %s"
                valuesList.append(endYMDHMS)            

            if sortFlag == "DESC":
                sqlStr = sqlStr + " ORDER BY recID DESC"

            if limitNum > 0:
                sqlStr += " LIMIT {0}".format(limitNum)

        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            if dataList:
                dataList = dataFormatConvert(dataList)
                result = list(dataList)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#hwinfo_report_record end 



#application end


#mindgram begin


#mgAnnualFilm begin
def tablename_convertor_mgAnnualFilm():
    tableName = "mgAnnualFilm"
    tableName = tableName.lower()
    return tableName


def create_mgAnnualFilm(tableName):
    aList = ["CREATE TABLE IF NOT EXISTS %s("
    "filmID BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '年度电影ID',",
    "userID VARCHAR(32) NOT NULL COMMENT '用户ID',",
    "filmYear CHAR(4) COMMENT '年度 YYYY',",
    "videoUrl VARCHAR(500) COMMENT '视频文件URL',",
    "duration SMALLINT COMMENT '视频时长 秒',",
    "scenesData TEXT COMMENT '场景数据 JSON 包含四章场景',",
    "resilienceScore TINYINT COMMENT '韧性评分 0-100',",
    "headlineStats TEXT COMMENT '六项核心数据 JSON',",
    "narrationScript TEXT COMMENT '旁白脚本 TEXT',",
    "exportUrl VARCHAR(500) COMMENT '导出分享URL',",
    "chapterData TEXT COMMENT '章节跳转数据 JSON',",
    "createdYMDHMS VARCHAR(16) COMMENT '生成时间',",
    "regID VARCHAR(32) COMMENT '注册ID',",
    "regYMDHMS VARCHAR(16) COMMENT '注册年月日',",
    "modifyID VARCHAR(32) COMMENT '修改用户ID',",
    "modifyYMDHMS VARCHAR(16) COMMENT '修改年月日',",
    "delFlag CHAR(1) COMMENT '删除标记'"
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        #sqlStr = "CREATE INDEX {1} ON {0}({1}) ".format(tableName, "indexKey")
        #rtn = mysqlDB.executeWrite(sqlStr)
        #sqlStr = "ALTER TABLE {0} auto_increment = {1} ".format(tableName,auto_increment_default_value)
        #rtn = mysqlDB.executeWrite(sqlStr)

    return result


#删除mgAnnualFilm表
def drop_mgAnnualFilm(tableName):
    result = dropTableGeneral(tableName)
    return result


#mgAnnualFilm 删除记录
def delete_mgAnnualFilm(tableName,filmID):
    result = 0
    sqlStr = f"DELETE FROM {tableName}"
    try:

        sqlStr += " WHERE filmID = %s"
        valuesList = [filmID] 
        result = mysqlDB.executeWrite(sqlStr,tuple(valuesList))

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgAnnualFilm 增加记录
def insert_mgAnnualFilm(tableName,dataSet):
    result = 0
    try:

        saveSet = {}

        saveSet["userID"] = dataSet.get("userID", "") 

        saveSet["filmYear"] = dataSet.get("filmYear", "") 

        saveSet["videoUrl"] = dataSet.get("videoUrl", "") 

        try:
            duration = int(dataSet.get("duration")) 
        except:
            duration = 0 
        saveSet["duration"] = duration

        saveSet["scenesData"] = dataSet.get("scenesData", "") 

        try:
            resilienceScore = int(dataSet.get("resilienceScore")) 
        except:
            resilienceScore = 0 
        saveSet["resilienceScore"] = resilienceScore

        saveSet["headlineStats"] = dataSet.get("headlineStats", "") 

        saveSet["narrationScript"] = dataSet.get("narrationScript", "") 

        saveSet["exportUrl"] = dataSet.get("exportUrl", "") 

        saveSet["chapterData"] = dataSet.get("chapterData", "") 

        saveSet["createdYMDHMS"] = dataSet.get("createdYMDHMS", "") 

        saveSet["regID"] = dataSet.get("regID", "") 

        saveSet["regYMDHMS"] = dataSet.get("regYMDHMS", "") 

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        result = insertTableGeneral(tableName, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgAnnualFilm 修改记录
def update_mgAnnualFilm(tableName,filmID,dataSet):
    result = -2
    try:
        saveSet = {}

        userID = dataSet.get("userID") 
        if userID:
            saveSet["userID"] = userID

        filmYear = dataSet.get("filmYear") 
        if filmYear:
            saveSet["filmYear"] = filmYear

        videoUrl = dataSet.get("videoUrl") 
        if videoUrl:
            saveSet["videoUrl"] = videoUrl

        try:
            duration = int(dataSet.get("duration")) 
            saveSet["duration"] = duration
        except:
            pass

        scenesData = dataSet.get("scenesData") 
        if scenesData:
            saveSet["scenesData"] = scenesData

        try:
            resilienceScore = int(dataSet.get("resilienceScore")) 
            saveSet["resilienceScore"] = resilienceScore
        except:
            pass

        headlineStats = dataSet.get("headlineStats") 
        if headlineStats:
            saveSet["headlineStats"] = headlineStats

        narrationScript = dataSet.get("narrationScript") 
        if narrationScript:
            saveSet["narrationScript"] = narrationScript

        exportUrl = dataSet.get("exportUrl") 
        if exportUrl:
            saveSet["exportUrl"] = exportUrl

        chapterData = dataSet.get("chapterData") 
        if chapterData:
            saveSet["chapterData"] = chapterData

        createdYMDHMS = dataSet.get("createdYMDHMS") 
        if createdYMDHMS:
            saveSet["createdYMDHMS"] = createdYMDHMS

        modifyID = dataSet.get("modifyID") 
        if modifyID:
            saveSet["modifyID"] = modifyID

        modifyYMDHMS = dataSet.get("modifyYMDHMS") 
        if modifyYMDHMS:
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            saveSet["delFlag"] = delFlag

        keySqlstr = "filmID = %s"
        keyValues = [filmID]

        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgAnnualFilm 查询记录
def query_mgAnnualFilm(tableName,filmID = "0", delFlag = "0", mode = "full",limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    columns = "*"
    valuesList = []
    sqlStr = f"SELECT {columns} FROM {tableName}"

    try:

        try:
            filmID = int(filmID)
        except:
            filmID = 0

        if filmID > 0:
            sqlStr =  sqlStr + " WHERE filmID = %s" 
            valuesList = [filmID]  

        #if limitNum > 0:
            #sqlStr += " LIMIT {0}".format(limitNum)

        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            result = list(dataList)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgAnnualFilm end 


#mgBadgeDef begin
def tablename_convertor_mgBadgeDef():
    tableName = "mgBadgeDef"
    tableName = tableName.lower()
    return tableName


def create_mgBadgeDef(tableName):
    aList = ["CREATE TABLE IF NOT EXISTS %s("
    "badgeID VARCHAR(16) PRIMARY KEY COMMENT '徽章ID',",
    "badgeName VARCHAR(40) COMMENT '徽章名称',",
    "badgeIcon VARCHAR(200) COMMENT '徽章图标URL',",
    "`description` VARCHAR(200) COMMENT '获得条件描述',",
    "conditionType VARCHAR(32) COMMENT '条件类型 STREAK/GUESS/POST/SPECIAL',",
    "conditionValue SMALLINT COMMENT '条件数值',",
    "sortOrder SMALLINT COMMENT '排序',",
    "regID VARCHAR(32) COMMENT '注册ID',",
    "regYMDHMS VARCHAR(16) COMMENT '注册年月日',",
    "modifyID VARCHAR(32) COMMENT '修改用户ID',",
    "modifyYMDHMS VARCHAR(16) COMMENT '修改年月日',",
    "delFlag CHAR(1) COMMENT '删除标记'"
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        #sqlStr = "CREATE INDEX {1} ON {0}({1}) ".format(tableName, "indexKey")
        #rtn = mysqlDB.executeWrite(sqlStr)

    return result


#删除mgBadgeDef表
def drop_mgBadgeDef(tableName):
    result = dropTableGeneral(tableName)
    return result


#mgBadgeDef 删除记录
def delete_mgBadgeDef(tableName,badgeID):
    result = 0
    sqlStr = f"DELETE FROM {tableName}"
    try:

        sqlStr += " WHERE badgeID = %s"
        valuesList = [badgeID] 
        result = mysqlDB.executeWrite(sqlStr,tuple(valuesList))

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgBadgeDef 增加记录
def insert_mgBadgeDef(tableName,badgeID,dataSet):
    result = 0
    try:

        saveSet = {}

        saveSet["badgeID"] = dataSet.get("badgeID", "") 

        saveSet["badgeName"] = dataSet.get("badgeName", "") 

        saveSet["badgeIcon"] = dataSet.get("badgeIcon", "") 

        saveSet["description"] = dataSet.get("description", "") 

        saveSet["conditionType"] = dataSet.get("conditionType", "") 

        try:
            conditionValue = int(dataSet.get("conditionValue")) 
        except:
            conditionValue = 0 
        saveSet["conditionValue"] = conditionValue

        try:
            sortOrder = int(dataSet.get("sortOrder")) 
        except:
            sortOrder = 0 
        saveSet["sortOrder"] = sortOrder

        saveSet["regID"] = dataSet.get("regID", "") 

        saveSet["regYMDHMS"] = dataSet.get("regYMDHMS", "") 

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        result = insertTableGeneral(tableName, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgBadgeDef 修改记录
def update_mgBadgeDef(tableName,badgeID,dataSet):
    result = -2
    try:
        saveSet = {}

        badgeName = dataSet.get("badgeName") 
        if badgeName:
            saveSet["badgeName"] = badgeName

        badgeIcon = dataSet.get("badgeIcon") 
        if badgeIcon:
            saveSet["badgeIcon"] = badgeIcon

        description = dataSet.get("description") 
        if description:
            saveSet["description"] = description

        conditionType = dataSet.get("conditionType") 
        if conditionType:
            saveSet["conditionType"] = conditionType

        try:
            conditionValue = int(dataSet.get("conditionValue")) 
            saveSet["conditionValue"] = conditionValue
        except:
            pass

        try:
            sortOrder = int(dataSet.get("sortOrder")) 
            saveSet["sortOrder"] = sortOrder
        except:
            pass

        modifyID = dataSet.get("modifyID") 
        if modifyID:
            saveSet["modifyID"] = modifyID

        modifyYMDHMS = dataSet.get("modifyYMDHMS") 
        if modifyYMDHMS:
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            saveSet["delFlag"] = delFlag

        keySqlstr = "badgeID = %s"
        keyValues = [badgeID]

        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgBadgeDef 查询记录
def query_mgBadgeDef(tableName,badgeID = "", delFlag = "0", mode = "full",limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    columns = "*"
    valuesList = []
    sqlStr = f"SELECT {columns} FROM {tableName}"

    try:

        #recID = int(recID)

        #if recID > 0:
            #sqlStr =  sqlStr + " WHERE recID = %s" 
            #valuesList = [recID]  

        #if limitNum > 0:
            #sqlStr += " LIMIT {0}".format(limitNum)

        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            result = list(dataList)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgBadgeDef end 


#mgFriend begin
def tablename_convertor_mgFriend():
    tableName = "mgFriend"
    tableName = tableName.lower()
    return tableName


def create_mgFriend(tableName):
    aList = ["CREATE TABLE IF NOT EXISTS %s("
    "relationID BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '好友关系ID',",
    "userID VARCHAR(32) NOT NULL COMMENT '用户ID',",
    "friendID VARCHAR(32) NOT NULL COMMENT '好友用户ID',",
    "`status` CHAR(1) COMMENT '关系状态 0=请求中 1=已接受 2=已拒绝 3=已拉黑',",
    "requestMsg VARCHAR(100) COMMENT '添加好友附言',",
    "createYMDHMS VARCHAR(16) COMMENT '建立关系时间',",
    "regID VARCHAR(32) COMMENT '注册ID',",
    "regYMDHMS VARCHAR(16) COMMENT '注册年月日',",
    "modifyID VARCHAR(32) COMMENT '修改用户ID',",
    "modifyYMDHMS VARCHAR(16) COMMENT '修改年月日',",
    "delFlag CHAR(1) COMMENT '删除标记'"
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        #sqlStr = "CREATE INDEX {1} ON {0}({1}) ".format(tableName, "indexKey")
        #rtn = mysqlDB.executeWrite(sqlStr)
        #sqlStr = "ALTER TABLE {0} auto_increment = {1} ".format(tableName,auto_increment_default_value)
        #rtn = mysqlDB.executeWrite(sqlStr)

    return result


#删除mgFriend表
def drop_mgFriend(tableName):
    result = dropTableGeneral(tableName)
    return result


#mgFriend 删除记录
def delete_mgFriend(tableName,relationID):
    result = 0
    sqlStr = f"DELETE FROM {tableName}"
    try:

        sqlStr += " WHERE relationID = %s"
        valuesList = [relationID] 
        result = mysqlDB.executeWrite(sqlStr,tuple(valuesList))

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgFriend 增加记录
def insert_mgFriend(tableName,dataSet):
    result = 0
    try:

        saveSet = {}

        saveSet["userID"] = dataSet.get("userID", "") 

        saveSet["friendID"] = dataSet.get("friendID", "") 

        saveSet["status"] = dataSet.get("status", "") 

        saveSet["requestMsg"] = dataSet.get("requestMsg", "") 

        saveSet["createYMDHMS"] = dataSet.get("createYMDHMS", "") 

        saveSet["regID"] = dataSet.get("regID", "") 

        saveSet["regYMDHMS"] = dataSet.get("regYMDHMS", "") 

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        result = insertTableGeneral(tableName, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgFriend 修改记录
def update_mgFriend(tableName,relationID,dataSet):
    result = -2
    try:
        saveSet = {}

        userID = dataSet.get("userID") 
        if userID:
            saveSet["userID"] = userID

        friendID = dataSet.get("friendID") 
        if friendID:
            saveSet["friendID"] = friendID

        status = dataSet.get("status") 
        if status:
            saveSet["status"] = status

        requestMsg = dataSet.get("requestMsg") 
        if requestMsg:
            saveSet["requestMsg"] = requestMsg

        createYMDHMS = dataSet.get("createYMDHMS") 
        if createYMDHMS:
            saveSet["createYMDHMS"] = createYMDHMS

        modifyID = dataSet.get("modifyID") 
        if modifyID:
            saveSet["modifyID"] = modifyID

        modifyYMDHMS = dataSet.get("modifyYMDHMS") 
        if modifyYMDHMS:
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            saveSet["delFlag"] = delFlag

        keySqlstr = "relationID = %s"
        keyValues = [relationID]

        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgFriend 查询记录
def query_mgFriend(tableName,relationID = "0", delFlag = "0", mode = "full",limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    columns = "*"
    valuesList = []
    sqlStr = f"SELECT {columns} FROM {tableName}"

    try:

        try:
            relationID = int(relationID)
        except:
            relationID = 0

        if relationID > 0:
            sqlStr =  sqlStr + " WHERE relationID = %s" 
            valuesList = [relationID]  

        #if limitNum > 0:
            #sqlStr += " LIMIT {0}".format(limitNum)

        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            result = list(dataList)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgFriend end 


#mgInviteLink begin
def tablename_convertor_mgInviteLink():
    tableName = "mgInviteLink"
    tableName = tableName.lower()
    return tableName


def create_mgInviteLink(tableName):
    aList = ["CREATE TABLE IF NOT EXISTS %s("
    "inviteID BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '邀请ID',",
    "userID VARCHAR(32) NOT NULL COMMENT '邀请人用户ID',",
    "inviteCode VARCHAR(32) COMMENT '唯一邀请码',",
    "usageCount SMALLINT COMMENT '已使用次数',",
    "maxUsage SMALLINT COMMENT '最大使用次数',",
    "expireDate CHAR(8) COMMENT '过期日期 YYYYMMDD',",
    "`status` CHAR(1) COMMENT '状态 0=有效 1=已用完 2=已过期',",
    "createdYMDHMS VARCHAR(16) COMMENT '创建时间',",
    "regID VARCHAR(32) COMMENT '注册ID',",
    "regYMDHMS VARCHAR(16) COMMENT '注册年月日',",
    "modifyID VARCHAR(32) COMMENT '修改用户ID',",
    "modifyYMDHMS VARCHAR(16) COMMENT '修改年月日',",
    "delFlag CHAR(1) COMMENT '删除标记'"
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        #sqlStr = "CREATE INDEX {1} ON {0}({1}) ".format(tableName, "indexKey")
        #rtn = mysqlDB.executeWrite(sqlStr)
        #sqlStr = "ALTER TABLE {0} auto_increment = {1} ".format(tableName,auto_increment_default_value)
        #rtn = mysqlDB.executeWrite(sqlStr)

    return result


#删除mgInviteLink表
def drop_mgInviteLink(tableName):
    result = dropTableGeneral(tableName)
    return result


#mgInviteLink 删除记录
def delete_mgInviteLink(tableName,inviteID):
    result = 0
    sqlStr = f"DELETE FROM {tableName}"
    try:

        sqlStr += " WHERE inviteID = %s"
        valuesList = [inviteID] 
        result = mysqlDB.executeWrite(sqlStr,tuple(valuesList))

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgInviteLink 增加记录
def insert_mgInviteLink(tableName,dataSet):
    result = 0
    try:

        saveSet = {}

        saveSet["userID"] = dataSet.get("userID", "") 

        saveSet["inviteCode"] = dataSet.get("inviteCode", "") 

        try:
            usageCount = int(dataSet.get("usageCount")) 
        except:
            usageCount = 0 
        saveSet["usageCount"] = usageCount

        try:
            maxUsage = int(dataSet.get("maxUsage")) 
        except:
            maxUsage = 0 
        saveSet["maxUsage"] = maxUsage

        saveSet["expireDate"] = dataSet.get("expireDate", "") 

        saveSet["status"] = dataSet.get("status", "") 

        saveSet["createdYMDHMS"] = dataSet.get("createdYMDHMS", "") 

        saveSet["regID"] = dataSet.get("regID", "") 

        saveSet["regYMDHMS"] = dataSet.get("regYMDHMS", "") 

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        result = insertTableGeneral(tableName, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgInviteLink 修改记录
def update_mgInviteLink(tableName,inviteID,dataSet):
    result = -2
    try:
        saveSet = {}

        userID = dataSet.get("userID") 
        if userID:
            saveSet["userID"] = userID

        inviteCode = dataSet.get("inviteCode") 
        if inviteCode:
            saveSet["inviteCode"] = inviteCode

        try:
            usageCount = int(dataSet.get("usageCount")) 
            saveSet["usageCount"] = usageCount
        except:
            pass

        try:
            maxUsage = int(dataSet.get("maxUsage")) 
            saveSet["maxUsage"] = maxUsage
        except:
            pass

        expireDate = dataSet.get("expireDate") 
        if expireDate:
            saveSet["expireDate"] = expireDate

        status = dataSet.get("status") 
        if status:
            saveSet["status"] = status

        createdYMDHMS = dataSet.get("createdYMDHMS") 
        if createdYMDHMS:
            saveSet["createdYMDHMS"] = createdYMDHMS

        modifyID = dataSet.get("modifyID") 
        if modifyID:
            saveSet["modifyID"] = modifyID

        modifyYMDHMS = dataSet.get("modifyYMDHMS") 
        if modifyYMDHMS:
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            saveSet["delFlag"] = delFlag

        keySqlstr = "inviteID = %s"
        keyValues = [inviteID]

        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgInviteLink 查询记录
def query_mgInviteLink(tableName,inviteID = "0", delFlag = "0", mode = "full",limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    columns = "*"
    valuesList = []
    sqlStr = f"SELECT {columns} FROM {tableName}"

    try:

        try:
            inviteID = int(inviteID)
        except:
            inviteID = 0

        if inviteID > 0:
            sqlStr =  sqlStr + " WHERE inviteID = %s" 
            valuesList = [inviteID]  

        #if limitNum > 0:
            #sqlStr += " LIMIT {0}".format(limitNum)

        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            result = list(dataList)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgInviteLink end 


#mgMoodGuess begin
def tablename_convertor_mgMoodGuess():
    tableName = "mgMoodGuess"
    tableName = tableName.lower()
    return tableName


def create_mgMoodGuess(tableName):
    aList = ["CREATE TABLE IF NOT EXISTS %s("
    "guessID BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '猜测记录ID',",
    "postID BIGINT NOT NULL COMMENT '被猜打卡贴ID',",
    "guesserID VARCHAR(32) NOT NULL COMMENT '猜测者用户ID',",
    "guessedEmoji VARCHAR(8) COMMENT '猜测的表情',",
    "isCorrect CHAR(1) COMMENT '是否猜对 0=否 1=是',",
    "pointsEarned SMALLINT COMMENT '获得积分',",
    "guessYMDHMS VARCHAR(16) COMMENT '猜测时间',",
    "regID VARCHAR(32) COMMENT '注册ID',",
    "regYMDHMS VARCHAR(16) COMMENT '注册年月日',",
    "modifyID VARCHAR(32) COMMENT '修改用户ID',",
    "modifyYMDHMS VARCHAR(16) COMMENT '修改年月日',",
    "delFlag CHAR(1) COMMENT '删除标记'"
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        #sqlStr = "CREATE INDEX {1} ON {0}({1}) ".format(tableName, "indexKey")
        #rtn = mysqlDB.executeWrite(sqlStr)
        #sqlStr = "ALTER TABLE {0} auto_increment = {1} ".format(tableName,auto_increment_default_value)
        #rtn = mysqlDB.executeWrite(sqlStr)

    return result


#删除mgMoodGuess表
def drop_mgMoodGuess(tableName):
    result = dropTableGeneral(tableName)
    return result


#mgMoodGuess 删除记录
def delete_mgMoodGuess(tableName,guessID):
    result = 0
    sqlStr = f"DELETE FROM {tableName}"
    try:

        sqlStr += " WHERE guessID = %s"
        valuesList = [guessID] 
        result = mysqlDB.executeWrite(sqlStr,tuple(valuesList))

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgMoodGuess 增加记录
def insert_mgMoodGuess(tableName,dataSet):
    result = 0
    try:

        saveSet = {}

        try:
            postID = int(dataSet.get("postID")) 
        except:
            postID = 0 
        saveSet["postID"] = postID

        saveSet["guesserID"] = dataSet.get("guesserID", "") 

        saveSet["guessedEmoji"] = dataSet.get("guessedEmoji", "") 

        saveSet["isCorrect"] = dataSet.get("isCorrect", "") 

        try:
            pointsEarned = int(dataSet.get("pointsEarned")) 
        except:
            pointsEarned = 0 
        saveSet["pointsEarned"] = pointsEarned

        saveSet["guessYMDHMS"] = dataSet.get("guessYMDHMS", "") 

        saveSet["regID"] = dataSet.get("regID", "") 

        saveSet["regYMDHMS"] = dataSet.get("regYMDHMS", "") 

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        result = insertTableGeneral(tableName, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgMoodGuess 修改记录
def update_mgMoodGuess(tableName,guessID,dataSet):
    result = -2
    try:
        saveSet = {}

        try:
            postID = int(dataSet.get("postID")) 
            saveSet["postID"] = postID
        except:
            pass

        guesserID = dataSet.get("guesserID") 
        if guesserID:
            saveSet["guesserID"] = guesserID

        guessedEmoji = dataSet.get("guessedEmoji") 
        if guessedEmoji:
            saveSet["guessedEmoji"] = guessedEmoji

        isCorrect = dataSet.get("isCorrect") 
        if isCorrect:
            saveSet["isCorrect"] = isCorrect

        try:
            pointsEarned = int(dataSet.get("pointsEarned")) 
            saveSet["pointsEarned"] = pointsEarned
        except:
            pass

        guessYMDHMS = dataSet.get("guessYMDHMS") 
        if guessYMDHMS:
            saveSet["guessYMDHMS"] = guessYMDHMS

        modifyID = dataSet.get("modifyID") 
        if modifyID:
            saveSet["modifyID"] = modifyID

        modifyYMDHMS = dataSet.get("modifyYMDHMS") 
        if modifyYMDHMS:
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            saveSet["delFlag"] = delFlag

        keySqlstr = "guessID = %s"
        keyValues = [guessID]

        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgMoodGuess 查询记录
def query_mgMoodGuess(tableName,guessID = "0", delFlag = "0", mode = "full",limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    columns = "*"
    valuesList = []
    sqlStr = f"SELECT {columns} FROM {tableName}"

    try:

        try:
            guessID = int(guessID)
        except:
            guessID = 0

        if guessID > 0:
            sqlStr =  sqlStr + " WHERE guessID = %s" 
            valuesList = [guessID]  

        #if limitNum > 0:
            #sqlStr += " LIMIT {0}".format(limitNum)

        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            result = list(dataList)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgMoodGuess end 


#mgMoodPost begin
def tablename_convertor_mgMoodPost():
    tableName = "mgMoodPost"
    tableName = tableName.lower()
    return tableName


def create_mgMoodPost(tableName):
    aList = ["CREATE TABLE IF NOT EXISTS %s("
    "postID BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '打卡贴ID',",
    "userID VARCHAR(32) NOT NULL COMMENT '用户ID',",
    "moodEmoji VARCHAR(8) NOT NULL COMMENT '情绪表情Emoji',",
    "intensity TINYINT NOT NULL COMMENT '情绪强度 1-10',",
    "hintNote VARCHAR(200) COMMENT '谜语式提示语',",
    "isAnonymous CHAR(1) COMMENT '是否匿名 0=否 1=是',",
    "photoUrl VARCHAR(500) COMMENT '自拍照片URL',",
    "thumbnailUrl VARCHAR(500) COMMENT '缩略图URL',",
    "postDate CHAR(8) COMMENT '打卡日期 YYYYMMDD',",
    "postYMDHMS CHAR(16) COMMENT '打卡时间 YYYYMMDDHHMMSS',",
    "regID VARCHAR(32) COMMENT '注册ID',",
    "regYMDHMS VARCHAR(16) COMMENT '注册年月日',",
    "modifyID VARCHAR(32) COMMENT '修改用户ID',",
    "modifyYMDHMS VARCHAR(16) COMMENT '修改年月日',",
    "delFlag CHAR(1) COMMENT '删除标记'"
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        #sqlStr = "CREATE INDEX {1} ON {0}({1}) ".format(tableName, "indexKey")
        #rtn = mysqlDB.executeWrite(sqlStr)
        #sqlStr = "ALTER TABLE {0} auto_increment = {1} ".format(tableName,auto_increment_default_value)
        #rtn = mysqlDB.executeWrite(sqlStr)

    return result


#删除mgMoodPost表
def drop_mgMoodPost(tableName):
    result = dropTableGeneral(tableName)
    return result


#mgMoodPost 删除记录
def delete_mgMoodPost(tableName,postID):
    result = 0
    sqlStr = f"DELETE FROM {tableName}"
    try:

        sqlStr += " WHERE postID = %s"
        valuesList = [postID] 
        result = mysqlDB.executeWrite(sqlStr,tuple(valuesList))

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgMoodPost 增加记录
def insert_mgMoodPost(tableName,dataSet):
    result = 0
    try:

        saveSet = {}

        saveSet["userID"] = dataSet.get("userID", "") 

        saveSet["moodEmoji"] = dataSet.get("moodEmoji", "") 

        try:
            intensity = int(dataSet.get("intensity")) 
        except:
            intensity = 0 
        saveSet["intensity"] = intensity

        saveSet["hintNote"] = dataSet.get("hintNote", "") 

        saveSet["isAnonymous"] = dataSet.get("isAnonymous", "") 

        saveSet["photoUrl"] = dataSet.get("photoUrl", "") 

        saveSet["thumbnailUrl"] = dataSet.get("thumbnailUrl", "") 

        saveSet["postDate"] = dataSet.get("postDate", "") 

        saveSet["postYMDHMS"] = dataSet.get("postYMDHMS", "") 

        saveSet["regID"] = dataSet.get("regID", "") 

        saveSet["regYMDHMS"] = dataSet.get("regYMDHMS", "") 

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        result = insertTableGeneral(tableName, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgMoodPost 修改记录
def update_mgMoodPost(tableName,postID,dataSet):
    result = -2
    try:
        saveSet = {}

        userID = dataSet.get("userID") 
        if userID:
            saveSet["userID"] = userID

        moodEmoji = dataSet.get("moodEmoji") 
        if moodEmoji:
            saveSet["moodEmoji"] = moodEmoji

        try:
            intensity = int(dataSet.get("intensity")) 
            saveSet["intensity"] = intensity
        except:
            pass

        hintNote = dataSet.get("hintNote") 
        if hintNote:
            saveSet["hintNote"] = hintNote

        isAnonymous = dataSet.get("isAnonymous") 
        if isAnonymous:
            saveSet["isAnonymous"] = isAnonymous

        photoUrl = dataSet.get("photoUrl") 
        if photoUrl:
            saveSet["photoUrl"] = photoUrl

        thumbnailUrl = dataSet.get("thumbnailUrl") 
        if thumbnailUrl:
            saveSet["thumbnailUrl"] = thumbnailUrl

        postDate = dataSet.get("postDate") 
        if postDate:
            saveSet["postDate"] = postDate

        postYMDHMS = dataSet.get("postYMDHMS") 
        if postYMDHMS:
            saveSet["postYMDHMS"] = postYMDHMS

        modifyID = dataSet.get("modifyID") 
        if modifyID:
            saveSet["modifyID"] = modifyID

        modifyYMDHMS = dataSet.get("modifyYMDHMS") 
        if modifyYMDHMS:
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            saveSet["delFlag"] = delFlag

        keySqlstr = "postID = %s"
        keyValues = [postID]

        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgMoodPost 查询记录
def query_mgMoodPost(tableName,postID = "0", delFlag = "0", mode = "full",limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    columns = "*"
    valuesList = []
    sqlStr = f"SELECT {columns} FROM {tableName}"

    try:

        try:
            postID = int(postID)
        except:
            postID = 0

        if postID > 0:
            sqlStr =  sqlStr + " WHERE postID = %s" 
            valuesList = [postID]  

        #if limitNum > 0:
            #sqlStr += " LIMIT {0}".format(limitNum)

        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            result = list(dataList)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgMoodPost end 


#mgMoodReaction begin
def tablename_convertor_mgMoodReaction():
    tableName = "mgMoodReaction"
    tableName = tableName.lower()
    return tableName


def create_mgMoodReaction(tableName):
    aList = ["CREATE TABLE IF NOT EXISTS %s("
    "reactionID BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '回应记录ID',",
    "postID BIGINT NOT NULL COMMENT '打卡贴ID',",
    "userID VARCHAR(32) NOT NULL COMMENT '回应用户ID',",
    "reactionType VARCHAR(8) COMMENT '回应类型 heart/tears/laugh/hug',",
    "reactionYMDHMS VARCHAR(16) COMMENT '回应时间',",
    "regID VARCHAR(32) COMMENT '注册ID',",
    "regYMDHMS VARCHAR(16) COMMENT '注册年月日',",
    "modifyID VARCHAR(32) COMMENT '修改用户ID',",
    "modifyYMDHMS VARCHAR(16) COMMENT '修改年月日',",
    "delFlag CHAR(1) COMMENT '删除标记'"
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        #sqlStr = "CREATE INDEX {1} ON {0}({1}) ".format(tableName, "indexKey")
        #rtn = mysqlDB.executeWrite(sqlStr)
        #sqlStr = "ALTER TABLE {0} auto_increment = {1} ".format(tableName,auto_increment_default_value)
        #rtn = mysqlDB.executeWrite(sqlStr)

    return result


#删除mgMoodReaction表
def drop_mgMoodReaction(tableName):
    result = dropTableGeneral(tableName)
    return result


#mgMoodReaction 删除记录
def delete_mgMoodReaction(tableName,reactionID):
    result = 0
    sqlStr = f"DELETE FROM {tableName}"
    try:

        sqlStr += " WHERE reactionID = %s"
        valuesList = [reactionID] 
        result = mysqlDB.executeWrite(sqlStr,tuple(valuesList))

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgMoodReaction 增加记录
def insert_mgMoodReaction(tableName,dataSet):
    result = 0
    try:

        saveSet = {}

        try:
            postID = int(dataSet.get("postID")) 
        except:
            postID = 0 
        saveSet["postID"] = postID

        saveSet["userID"] = dataSet.get("userID", "") 

        saveSet["reactionType"] = dataSet.get("reactionType", "") 

        saveSet["reactionYMDHMS"] = dataSet.get("reactionYMDHMS", "") 

        saveSet["regID"] = dataSet.get("regID", "") 

        saveSet["regYMDHMS"] = dataSet.get("regYMDHMS", "") 

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        result = insertTableGeneral(tableName, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgMoodReaction 修改记录
def update_mgMoodReaction(tableName,reactionID,dataSet):
    result = -2
    try:
        saveSet = {}

        try:
            postID = int(dataSet.get("postID")) 
            saveSet["postID"] = postID
        except:
            pass

        userID = dataSet.get("userID") 
        if userID:
            saveSet["userID"] = userID

        reactionType = dataSet.get("reactionType") 
        if reactionType:
            saveSet["reactionType"] = reactionType

        reactionYMDHMS = dataSet.get("reactionYMDHMS") 
        if reactionYMDHMS:
            saveSet["reactionYMDHMS"] = reactionYMDHMS

        modifyID = dataSet.get("modifyID") 
        if modifyID:
            saveSet["modifyID"] = modifyID

        modifyYMDHMS = dataSet.get("modifyYMDHMS") 
        if modifyYMDHMS:
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            saveSet["delFlag"] = delFlag

        keySqlstr = "reactionID = %s"
        keyValues = [reactionID]

        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgMoodReaction 查询记录
def query_mgMoodReaction(tableName,reactionID = "0", delFlag = "0", mode = "full",limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    columns = "*"
    valuesList = []
    sqlStr = f"SELECT {columns} FROM {tableName}"

    try:

        try:
            reactionID = int(reactionID)
        except:
            reactionID = 0

        if reactionID > 0:
            sqlStr =  sqlStr + " WHERE reactionID = %s" 
            valuesList = [reactionID]  

        #if limitNum > 0:
            #sqlStr += " LIMIT {0}".format(limitNum)

        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            result = list(dataList)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgMoodReaction end 


#mgQuarterlyReport begin
def tablename_convertor_mgQuarterlyReport():
    tableName = "mgQuarterlyReport"
    tableName = tableName.lower()
    return tableName


def create_mgQuarterlyReport(tableName):
    aList = ["CREATE TABLE IF NOT EXISTS %s("
    "reportID BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '季度报告ID',",
    "userID VARCHAR(32) NOT NULL COMMENT '用户ID',",
    "quarterStart CHAR(8) COMMENT '季度开始日期 YYYYMMDD',",
    "quarterEnd CHAR(8) COMMENT '季度结束日期 YYYYMMDD',",
    "avgMoodScore DECIMAL(3,1) COMMENT '平均情绪得分',",
    "positiveDaysPct DECIMAL(3,1) COMMENT '积极情绪天数占比',",
    "maxStreak SMALLINT COMMENT '季度最长连续打卡',",
    "loggingRate DECIMAL(3,1) COMMENT '打卡覆盖率',",
    "emojiBreakdown TEXT COMMENT '表情分布数据 JSON',",
    "monthlyTrend TEXT COMMENT '月度趋势数据 JSON',",
    "diagnosisFindings TEXT COMMENT '诊断五项发现 JSON',",
    "actionCards TEXT COMMENT '六张行动建议卡片 JSON',",
    "aiModelVersion VARCHAR(16) COMMENT 'AI模型版本',",
    "createdYMDHMS VARCHAR(16) COMMENT '生成时间',",
    "regID VARCHAR(32) COMMENT '注册ID',",
    "regYMDHMS VARCHAR(16) COMMENT '注册年月日',",
    "modifyID VARCHAR(32) COMMENT '修改用户ID',",
    "modifyYMDHMS VARCHAR(16) COMMENT '修改年月日',",
    "delFlag CHAR(1) COMMENT '删除标记'"
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        #sqlStr = "CREATE INDEX {1} ON {0}({1}) ".format(tableName, "indexKey")
        #rtn = mysqlDB.executeWrite(sqlStr)
        #sqlStr = "ALTER TABLE {0} auto_increment = {1} ".format(tableName,auto_increment_default_value)
        #rtn = mysqlDB.executeWrite(sqlStr)

    return result


#删除mgQuarterlyReport表
def drop_mgQuarterlyReport(tableName):
    result = dropTableGeneral(tableName)
    return result


#mgQuarterlyReport 删除记录
def delete_mgQuarterlyReport(tableName,reportID):
    result = 0
    sqlStr = f"DELETE FROM {tableName}"
    try:

        sqlStr += " WHERE reportID = %s"
        valuesList = [reportID] 
        result = mysqlDB.executeWrite(sqlStr,tuple(valuesList))

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgQuarterlyReport 增加记录
def insert_mgQuarterlyReport(tableName,dataSet):
    result = 0
    try:

        saveSet = {}

        saveSet["userID"] = dataSet.get("userID", "") 

        saveSet["quarterStart"] = dataSet.get("quarterStart", "") 

        saveSet["quarterEnd"] = dataSet.get("quarterEnd", "") 

        try:
            avgMoodScore = float(dataSet.get("avgMoodScore")) 
        except:
            avgMoodScore = 0 
        saveSet["avgMoodScore"] = avgMoodScore

        try:
            positiveDaysPct = float(dataSet.get("positiveDaysPct")) 
        except:
            positiveDaysPct = 0 
        saveSet["positiveDaysPct"] = positiveDaysPct

        try:
            maxStreak = int(dataSet.get("maxStreak")) 
        except:
            maxStreak = 0 
        saveSet["maxStreak"] = maxStreak

        try:
            loggingRate = float(dataSet.get("loggingRate")) 
        except:
            loggingRate = 0 
        saveSet["loggingRate"] = loggingRate

        saveSet["emojiBreakdown"] = dataSet.get("emojiBreakdown", "") 

        saveSet["monthlyTrend"] = dataSet.get("monthlyTrend", "") 

        saveSet["diagnosisFindings"] = dataSet.get("diagnosisFindings", "") 

        saveSet["actionCards"] = dataSet.get("actionCards", "") 

        saveSet["aiModelVersion"] = dataSet.get("aiModelVersion", "") 

        saveSet["createdYMDHMS"] = dataSet.get("createdYMDHMS", "") 

        saveSet["regID"] = dataSet.get("regID", "") 

        saveSet["regYMDHMS"] = dataSet.get("regYMDHMS", "") 

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        result = insertTableGeneral(tableName, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgQuarterlyReport 修改记录
def update_mgQuarterlyReport(tableName,reportID,dataSet):
    result = -2
    try:
        saveSet = {}

        userID = dataSet.get("userID") 
        if userID:
            saveSet["userID"] = userID

        quarterStart = dataSet.get("quarterStart") 
        if quarterStart:
            saveSet["quarterStart"] = quarterStart

        quarterEnd = dataSet.get("quarterEnd") 
        if quarterEnd:
            saveSet["quarterEnd"] = quarterEnd

        try:
            avgMoodScore = float(dataSet.get("avgMoodScore")) 
            saveSet["avgMoodScore"] = avgMoodScore
        except:
            pass

        try:
            positiveDaysPct = float(dataSet.get("positiveDaysPct")) 
            saveSet["positiveDaysPct"] = positiveDaysPct
        except:
            pass

        try:
            maxStreak = int(dataSet.get("maxStreak")) 
            saveSet["maxStreak"] = maxStreak
        except:
            pass

        try:
            loggingRate = float(dataSet.get("loggingRate")) 
            saveSet["loggingRate"] = loggingRate
        except:
            pass

        emojiBreakdown = dataSet.get("emojiBreakdown") 
        if emojiBreakdown:
            saveSet["emojiBreakdown"] = emojiBreakdown

        monthlyTrend = dataSet.get("monthlyTrend") 
        if monthlyTrend:
            saveSet["monthlyTrend"] = monthlyTrend

        diagnosisFindings = dataSet.get("diagnosisFindings") 
        if diagnosisFindings:
            saveSet["diagnosisFindings"] = diagnosisFindings

        actionCards = dataSet.get("actionCards") 
        if actionCards:
            saveSet["actionCards"] = actionCards

        aiModelVersion = dataSet.get("aiModelVersion") 
        if aiModelVersion:
            saveSet["aiModelVersion"] = aiModelVersion

        createdYMDHMS = dataSet.get("createdYMDHMS") 
        if createdYMDHMS:
            saveSet["createdYMDHMS"] = createdYMDHMS

        modifyID = dataSet.get("modifyID") 
        if modifyID:
            saveSet["modifyID"] = modifyID

        modifyYMDHMS = dataSet.get("modifyYMDHMS") 
        if modifyYMDHMS:
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            saveSet["delFlag"] = delFlag

        keySqlstr = "reportID = %s"
        keyValues = [reportID]

        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgQuarterlyReport 查询记录
def query_mgQuarterlyReport(tableName,reportID = "0", delFlag = "0", mode = "full",limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    columns = "*"
    valuesList = []
    sqlStr = f"SELECT {columns} FROM {tableName}"

    try:

        try:
            reportID = int(reportID)
        except:
            reportID = 0

        if reportID > 0:
            sqlStr =  sqlStr + " WHERE reportID = %s" 
            valuesList = [reportID]  

        #if limitNum > 0:
            #sqlStr += " LIMIT {0}".format(limitNum)

        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            result = list(dataList)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgQuarterlyReport end 


#mgSystemConfig begin
def tablename_convertor_mgSystemConfig():
    tableName = "mgSystemConfig"
    tableName = tableName.lower()
    return tableName


def create_mgSystemConfig(tableName):
    aList = ["CREATE TABLE IF NOT EXISTS %s("
    "configID VARCHAR(32) PRIMARY KEY COMMENT '配置项ID',",
    "configValue VARCHAR(500) COMMENT '配置值',",
    "configType VARCHAR(16) COMMENT '配置类型 STRING/INT/FLOAT/JSON',",
    "`description` VARCHAR(200) COMMENT '配置说明',",
    "regID VARCHAR(32) COMMENT '注册ID',",
    "regYMDHMS VARCHAR(16) COMMENT '注册年月日',",
    "modifyID VARCHAR(32) COMMENT '修改用户ID',",
    "modifyYMDHMS VARCHAR(16) COMMENT '修改年月日',",
    "delFlag CHAR(1) COMMENT '删除标记'"
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        #sqlStr = "CREATE INDEX {1} ON {0}({1}) ".format(tableName, "indexKey")
        #rtn = mysqlDB.executeWrite(sqlStr)

    return result


#删除mgSystemConfig表
def drop_mgSystemConfig(tableName):
    result = dropTableGeneral(tableName)
    return result


#mgSystemConfig 删除记录
def delete_mgSystemConfig(tableName,configID):
    result = 0
    sqlStr = f"DELETE FROM {tableName}"
    try:

        sqlStr += " WHERE configID = %s"
        valuesList = [configID] 
        result = mysqlDB.executeWrite(sqlStr,tuple(valuesList))

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgSystemConfig 增加记录
def insert_mgSystemConfig(tableName,configID,dataSet):
    result = 0
    try:

        saveSet = {}

        saveSet["configID"] = dataSet.get("configID", "") 

        saveSet["configValue"] = dataSet.get("configValue", "") 

        saveSet["configType"] = dataSet.get("configType", "") 

        saveSet["description"] = dataSet.get("description", "") 

        saveSet["regID"] = dataSet.get("regID", "") 

        saveSet["regYMDHMS"] = dataSet.get("regYMDHMS", "") 

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        result = insertTableGeneral(tableName, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgSystemConfig 修改记录
def update_mgSystemConfig(tableName,configID,dataSet):
    result = -2
    try:
        saveSet = {}

        configValue = dataSet.get("configValue") 
        if configValue:
            saveSet["configValue"] = configValue

        configType = dataSet.get("configType") 
        if configType:
            saveSet["configType"] = configType

        description = dataSet.get("description") 
        if description:
            saveSet["description"] = description

        modifyID = dataSet.get("modifyID") 
        if modifyID:
            saveSet["modifyID"] = modifyID

        modifyYMDHMS = dataSet.get("modifyYMDHMS") 
        if modifyYMDHMS:
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            saveSet["delFlag"] = delFlag

        keySqlstr = "configID = %s"
        keyValues = [configID]

        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgSystemConfig 查询记录
def query_mgSystemConfig(tableName,configID = "", delFlag = "0", mode = "full",limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    columns = "*"
    valuesList = []
    sqlStr = f"SELECT {columns} FROM {tableName}"

    try:

        #recID = int(recID)

        #if recID > 0:
            #sqlStr =  sqlStr + " WHERE recID = %s" 
            #valuesList = [recID]  

        #if limitNum > 0:
            #sqlStr += " LIMIT {0}".format(limitNum)

        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            result = list(dataList)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgSystemConfig end 


#mgTcmDiagnosis begin
def tablename_convertor_mgTcmDiagnosis():
    tableName = "mgTcmDiagnosis"
    tableName = tableName.lower()
    return tableName


def create_mgTcmDiagnosis(tableName):
    aList = ["CREATE TABLE IF NOT EXISTS %s("
    "tcmID BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '中医诊断ID',",
    "userID VARCHAR(32) NOT NULL COMMENT '用户ID',",
    "quarterStart CHAR(8) COMMENT '关联季度开始',",
    "quarterEnd CHAR(8) COMMENT '关联季度结束',",
    "primaryPattern VARCHAR(60) COMMENT '主证型 如:肝气郁结',",
    "secondaryPattern TEXT COMMENT '次证型 JSON',",
    "radarChartData TEXT COMMENT '五行雷达图数据 JSON',",
    "dietPlan TEXT COMMENT '饮食方案 JSON 含时辰/食材',",
    "sleepPlan TEXT COMMENT '睡眠方案 JSON 含就寝时间/流程/穴位',",
    "bodyClockData TEXT COMMENT '子午流注时钟数据 JSON',",
    "weeklyPlan TEXT COMMENT '周养生计划 JSON',",
    "aiModelVersion VARCHAR(16) COMMENT 'AI模型版本',",
    "createdYMDHMS VARCHAR(16) COMMENT '生成时间',",
    "regID VARCHAR(32) COMMENT '注册ID',",
    "regYMDHMS VARCHAR(16) COMMENT '注册年月日',",
    "modifyID VARCHAR(32) COMMENT '修改用户ID',",
    "modifyYMDHMS VARCHAR(16) COMMENT '修改年月日',",
    "delFlag CHAR(1) COMMENT '删除标记'"
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        #sqlStr = "CREATE INDEX {1} ON {0}({1}) ".format(tableName, "indexKey")
        #rtn = mysqlDB.executeWrite(sqlStr)
        #sqlStr = "ALTER TABLE {0} auto_increment = {1} ".format(tableName,auto_increment_default_value)
        #rtn = mysqlDB.executeWrite(sqlStr)

    return result


#删除mgTcmDiagnosis表
def drop_mgTcmDiagnosis(tableName):
    result = dropTableGeneral(tableName)
    return result


#mgTcmDiagnosis 删除记录
def delete_mgTcmDiagnosis(tableName,tcmID):
    result = 0
    sqlStr = f"DELETE FROM {tableName}"
    try:

        sqlStr += " WHERE tcmID = %s"
        valuesList = [tcmID] 
        result = mysqlDB.executeWrite(sqlStr,tuple(valuesList))

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgTcmDiagnosis 增加记录
def insert_mgTcmDiagnosis(tableName,dataSet):
    result = 0
    try:

        saveSet = {}

        saveSet["userID"] = dataSet.get("userID", "") 

        saveSet["quarterStart"] = dataSet.get("quarterStart", "") 

        saveSet["quarterEnd"] = dataSet.get("quarterEnd", "") 

        saveSet["primaryPattern"] = dataSet.get("primaryPattern", "") 

        saveSet["secondaryPattern"] = dataSet.get("secondaryPattern", "") 

        saveSet["radarChartData"] = dataSet.get("radarChartData", "") 

        saveSet["dietPlan"] = dataSet.get("dietPlan", "") 

        saveSet["sleepPlan"] = dataSet.get("sleepPlan", "") 

        saveSet["bodyClockData"] = dataSet.get("bodyClockData", "") 

        saveSet["weeklyPlan"] = dataSet.get("weeklyPlan", "") 

        saveSet["aiModelVersion"] = dataSet.get("aiModelVersion", "") 

        saveSet["createdYMDHMS"] = dataSet.get("createdYMDHMS", "") 

        saveSet["regID"] = dataSet.get("regID", "") 

        saveSet["regYMDHMS"] = dataSet.get("regYMDHMS", "") 

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        result = insertTableGeneral(tableName, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgTcmDiagnosis 修改记录
def update_mgTcmDiagnosis(tableName,tcmID,dataSet):
    result = -2
    try:
        saveSet = {}

        userID = dataSet.get("userID") 
        if userID:
            saveSet["userID"] = userID

        quarterStart = dataSet.get("quarterStart") 
        if quarterStart:
            saveSet["quarterStart"] = quarterStart

        quarterEnd = dataSet.get("quarterEnd") 
        if quarterEnd:
            saveSet["quarterEnd"] = quarterEnd

        primaryPattern = dataSet.get("primaryPattern") 
        if primaryPattern:
            saveSet["primaryPattern"] = primaryPattern

        secondaryPattern = dataSet.get("secondaryPattern") 
        if secondaryPattern:
            saveSet["secondaryPattern"] = secondaryPattern

        radarChartData = dataSet.get("radarChartData") 
        if radarChartData:
            saveSet["radarChartData"] = radarChartData

        dietPlan = dataSet.get("dietPlan") 
        if dietPlan:
            saveSet["dietPlan"] = dietPlan

        sleepPlan = dataSet.get("sleepPlan") 
        if sleepPlan:
            saveSet["sleepPlan"] = sleepPlan

        bodyClockData = dataSet.get("bodyClockData") 
        if bodyClockData:
            saveSet["bodyClockData"] = bodyClockData

        weeklyPlan = dataSet.get("weeklyPlan") 
        if weeklyPlan:
            saveSet["weeklyPlan"] = weeklyPlan

        aiModelVersion = dataSet.get("aiModelVersion") 
        if aiModelVersion:
            saveSet["aiModelVersion"] = aiModelVersion

        createdYMDHMS = dataSet.get("createdYMDHMS") 
        if createdYMDHMS:
            saveSet["createdYMDHMS"] = createdYMDHMS

        modifyID = dataSet.get("modifyID") 
        if modifyID:
            saveSet["modifyID"] = modifyID

        modifyYMDHMS = dataSet.get("modifyYMDHMS") 
        if modifyYMDHMS:
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            saveSet["delFlag"] = delFlag

        keySqlstr = "tcmID = %s"
        keyValues = [tcmID]

        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgTcmDiagnosis 查询记录
def query_mgTcmDiagnosis(tableName,tcmID = "0", delFlag = "0", mode = "full",limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    columns = "*"
    valuesList = []
    sqlStr = f"SELECT {columns} FROM {tableName}"

    try:

        try:
            tcmID = int(tcmID)
        except:
            tcmID = 0

        if tcmID > 0:
            sqlStr =  sqlStr + " WHERE tcmID = %s" 
            valuesList = [tcmID]  

        #if limitNum > 0:
            #sqlStr += " LIMIT {0}".format(limitNum)

        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            result = list(dataList)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgTcmDiagnosis end 


#mgUserBadge begin
def tablename_convertor_mgUserBadge():
    tableName = "mgUserBadge"
    tableName = tableName.lower()
    return tableName


def create_mgUserBadge(tableName):
    aList = ["CREATE TABLE IF NOT EXISTS %s("
    "recordID BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',",
    "userID VARCHAR(32) NOT NULL COMMENT '用户ID',",
    "badgeID VARCHAR(16) NOT NULL COMMENT '徽章ID',",
    "earnYMDHMS VARCHAR(16) COMMENT '获得时间',",
    "isWearing CHAR(1) COMMENT '是否佩戴中 0=否 1=是',",
    "regID VARCHAR(32) COMMENT '注册ID',",
    "regYMDHMS VARCHAR(16) COMMENT '注册年月日',",
    "modifyID VARCHAR(32) COMMENT '修改用户ID',",
    "modifyYMDHMS VARCHAR(16) COMMENT '修改年月日',",
    "delFlag CHAR(1) COMMENT '删除标记'"
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        #sqlStr = "CREATE INDEX {1} ON {0}({1}) ".format(tableName, "indexKey")
        #rtn = mysqlDB.executeWrite(sqlStr)
        #sqlStr = "ALTER TABLE {0} auto_increment = {1} ".format(tableName,auto_increment_default_value)
        #rtn = mysqlDB.executeWrite(sqlStr)

    return result


#删除mgUserBadge表
def drop_mgUserBadge(tableName):
    result = dropTableGeneral(tableName)
    return result


#mgUserBadge 删除记录
def delete_mgUserBadge(tableName,recordID):
    result = 0
    sqlStr = f"DELETE FROM {tableName}"
    try:

        sqlStr += " WHERE recordID = %s"
        valuesList = [recordID] 
        result = mysqlDB.executeWrite(sqlStr,tuple(valuesList))

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgUserBadge 增加记录
def insert_mgUserBadge(tableName,dataSet):
    result = 0
    try:

        saveSet = {}

        saveSet["userID"] = dataSet.get("userID", "") 

        saveSet["badgeID"] = dataSet.get("badgeID", "") 

        saveSet["earnYMDHMS"] = dataSet.get("earnYMDHMS", "") 

        saveSet["isWearing"] = dataSet.get("isWearing", "") 

        saveSet["regID"] = dataSet.get("regID", "") 

        saveSet["regYMDHMS"] = dataSet.get("regYMDHMS", "") 

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        result = insertTableGeneral(tableName, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgUserBadge 修改记录
def update_mgUserBadge(tableName,recordID,dataSet):
    result = -2
    try:
        saveSet = {}

        userID = dataSet.get("userID") 
        if userID:
            saveSet["userID"] = userID

        badgeID = dataSet.get("badgeID") 
        if badgeID:
            saveSet["badgeID"] = badgeID

        earnYMDHMS = dataSet.get("earnYMDHMS") 
        if earnYMDHMS:
            saveSet["earnYMDHMS"] = earnYMDHMS

        isWearing = dataSet.get("isWearing") 
        if isWearing:
            saveSet["isWearing"] = isWearing

        modifyID = dataSet.get("modifyID") 
        if modifyID:
            saveSet["modifyID"] = modifyID

        modifyYMDHMS = dataSet.get("modifyYMDHMS") 
        if modifyYMDHMS:
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            saveSet["delFlag"] = delFlag

        keySqlstr = "recordID = %s"
        keyValues = [recordID]

        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgUserBadge 查询记录
def query_mgUserBadge(tableName,recordID = "0", delFlag = "0", mode = "full",limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    columns = "*"
    valuesList = []
    sqlStr = f"SELECT {columns} FROM {tableName}"

    try:

        try:
            recordID = int(recordID)
        except:
            recordID = 0

        if recordID > 0:
            sqlStr =  sqlStr + " WHERE recordID = %s" 
            valuesList = [recordID]  

        #if limitNum > 0:
            #sqlStr += " LIMIT {0}".format(limitNum)

        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            result = list(dataList)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgUserBadge end 

#mgUserStats begin 

def tablename_convertor_mgUserStats():
    tableName = "mgUserStats"
    tableName = tableName.lower()
    return tableName


def decode_tablename_mgUserStats(tableName):
    result = {}
    aList = tableName.split("_")
    
    return result


#����mgUserStats��
def create_mgUserStats(tableName):
    aList = ["CREATE TABLE IF NOT EXISTS %s("
    "userID VARCHAR(32) PRIMARY KEY COMMENT '�û�ID',",
    "totalScore INT COMMENT '�ۼ��ܻ���',",
    "weeklyScore INT COMMENT '���ܻ���',",
    "streakDays SMALLINT COMMENT '��ǰ����������',",
    "longestStreak SMALLINT COMMENT '��ʷ���������',",
    "totalPosts INT COMMENT '�ۼƷ�����',",
    "totalCorrectGuesses INT COMMENT '�ۼ���ȷ�²���',",
    "totalGuesses INT COMMENT '�ۼ��ܲ²���',",
    "weeklyRank SMALLINT COMMENT '��������',",
    "lastPostDate CHAR(8) COMMENT '��������',",
    "allowShowMoodToFriends SMALLINT COMMENT '�Ƿ�����չʾ���������İ����',",
    "regID VARCHAR(32) COMMENT 'ע��ID',",
    "regYMDHMS VARCHAR(16) COMMENT 'ע��������',",
    "modifyID VARCHAR(32) COMMENT '�޸��û�ID',",
    "modifyYMDHMS VARCHAR(16) COMMENT '�޸�������',",
    "delFlag CHAR(1) COMMENT 'ɾ�����'"
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        #sqlStr = "CREATE INDEX {1} ON {0}({1}) ".format(tableName, "indexKey")
        #rtn = mysqlDB.executeWrite(sqlStr)

    return result


#ɾ��mgUserStats��
def drop_mgUserStats(tableName):
    result = dropTableGeneral(tableName)
    return result


#mgUserStats ɾ����¼
def delete_mgUserStats(tableName,userID):
    result = 0
    sqlStr = f"DELETE FROM {tableName}"
    try:

        sqlStr += " WHERE userID = %s"
        valuesList = [userID] 
        result = mysqlDB.executeWrite(sqlStr,tuple(valuesList))

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgUserStats ���Ӽ�¼
def insert_mgUserStats(tableName,userID,dataSet):
    result = 0
    try:

        saveSet = {}

        saveSet["userID"] = dataSet.get("userID", "") 

        try:
            totalScore = int(dataSet.get("totalScore")) 
        except:
            totalScore = 0 
        saveSet["totalScore"] = totalScore

        try:
            weeklyScore = int(dataSet.get("weeklyScore")) 
        except:
            weeklyScore = 0 
        saveSet["weeklyScore"] = weeklyScore

        try:
            streakDays = int(dataSet.get("streakDays")) 
        except:
            streakDays = 0 
        saveSet["streakDays"] = streakDays

        try:
            longestStreak = int(dataSet.get("longestStreak")) 
        except:
            longestStreak = 0 
        saveSet["longestStreak"] = longestStreak

        try:
            totalPosts = int(dataSet.get("totalPosts")) 
        except:
            totalPosts = 0 
        saveSet["totalPosts"] = totalPosts

        try:
            totalCorrectGuesses = int(dataSet.get("totalCorrectGuesses")) 
        except:
            totalCorrectGuesses = 0 
        saveSet["totalCorrectGuesses"] = totalCorrectGuesses

        try:
            totalGuesses = int(dataSet.get("totalGuesses")) 
        except:
            totalGuesses = 0 
        saveSet["totalGuesses"] = totalGuesses

        try:
            weeklyRank = int(dataSet.get("weeklyRank")) 
        except:
            weeklyRank = 0 
        saveSet["weeklyRank"] = weeklyRank

        saveSet["lastPostDate"] = dataSet.get("lastPostDate", "") 

        try:
            allowShowMoodToFriends = int(dataSet.get("allowShowMoodToFriends")) 
        except:
            allowShowMoodToFriends = 0 
        saveSet["allowShowMoodToFriends"] = allowShowMoodToFriends

        saveSet["regID"] = dataSet.get("regID", "") 

        saveSet["regYMDHMS"] = dataSet.get("regYMDHMS", "") 

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        result = insertTableGeneral(tableName, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgUserStats �޸ļ�¼
def update_mgUserStats(tableName,userID,dataSet):
    result = -2
    try:
        saveSet = {}

        try:
            totalScore = int(dataSet.get("totalScore")) 
            saveSet["totalScore"] = totalScore
        except:
            pass

        try:
            weeklyScore = int(dataSet.get("weeklyScore")) 
            saveSet["weeklyScore"] = weeklyScore
        except:
            pass

        try:
            streakDays = int(dataSet.get("streakDays")) 
            saveSet["streakDays"] = streakDays
        except:
            pass

        try:
            longestStreak = int(dataSet.get("longestStreak")) 
            saveSet["longestStreak"] = longestStreak
        except:
            pass

        try:
            totalPosts = int(dataSet.get("totalPosts")) 
            saveSet["totalPosts"] = totalPosts
        except:
            pass

        try:
            totalCorrectGuesses = int(dataSet.get("totalCorrectGuesses")) 
            saveSet["totalCorrectGuesses"] = totalCorrectGuesses
        except:
            pass

        try:
            totalGuesses = int(dataSet.get("totalGuesses")) 
            saveSet["totalGuesses"] = totalGuesses
        except:
            pass

        try:
            weeklyRank = int(dataSet.get("weeklyRank")) 
            saveSet["weeklyRank"] = weeklyRank
        except:
            pass

        lastPostDate = dataSet.get("lastPostDate") 
        if lastPostDate:
            saveSet["lastPostDate"] = lastPostDate

        try:
            allowShowMoodToFriends = int(dataSet.get("allowShowMoodToFriends")) 
            saveSet["allowShowMoodToFriends"] = allowShowMoodToFriends
        except:
            pass

        modifyID = dataSet.get("modifyID") 
        if modifyID:
            saveSet["modifyID"] = modifyID

        modifyYMDHMS = dataSet.get("modifyYMDHMS") 
        if modifyYMDHMS:
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            saveSet["delFlag"] = delFlag

        keySqlstr = "userID = %s"
        keyValues = [userID]

        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgUserStats ��ѯ��¼
def query_mgUserStats(tableName,userID = "", delFlag = "0", mode = "full",limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    columns = "*"
    valuesList = []
    sqlStr = f"SELECT {columns} FROM {tableName}"

    try:

        #recID = int(recID)

        #if recID > 0:
            #sqlStr =  sqlStr + " WHERE recID = %s" 
            #valuesList = [recID]  

        #if limitNum > 0:
            #sqlStr += " LIMIT {0}".format(limitNum)

        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            result = list(dataList)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgUserStats end 


#mgWeeklyReel begin
def tablename_convertor_mgWeeklyReel():
    tableName = "mgWeeklyReel"
    tableName = tableName.lower()
    return tableName


def create_mgWeeklyReel(tableName):
    aList = ["CREATE TABLE IF NOT EXISTS %s("
    "reelID BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '周回顾ID',",
    "userID VARCHAR(32) NOT NULL COMMENT '用户ID',",
    "weekStart CHAR(8) COMMENT '周开始日期 YYYYMMDD',",
    "weekEnd CHAR(8) COMMENT '周结束日期 YYYYMMDD',",
    "videoUrl VARCHAR(500) COMMENT '视频文件URL',",
    "gifUrl VARCHAR(500) COMMENT 'GIF文件URL',",
    "daysTracked TINYINT COMMENT '本周打卡天数',",
    "topMood VARCHAR(8) COMMENT '本周主导情绪Emoji',",
    "avgIntensity DECIMAL(3,1) COMMENT '平均情绪强度',",
    "shareUrl VARCHAR(200) COMMENT '分享链接',",
    "createdYMDHMS VARCHAR(16) COMMENT '生成时间',",
    "regID VARCHAR(32) COMMENT '注册ID',",
    "regYMDHMS VARCHAR(16) COMMENT '注册年月日',",
    "modifyID VARCHAR(32) COMMENT '修改用户ID',",
    "modifyYMDHMS VARCHAR(16) COMMENT '修改年月日',",
    "delFlag CHAR(1) COMMENT '删除标记'"
    ")  ENGINE=INNODB DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        #sqlStr = "CREATE INDEX {1} ON {0}({1}) ".format(tableName, "indexKey")
        #rtn = mysqlDB.executeWrite(sqlStr)
        #sqlStr = "ALTER TABLE {0} auto_increment = {1} ".format(tableName,auto_increment_default_value)
        #rtn = mysqlDB.executeWrite(sqlStr)

    return result


#删除mgWeeklyReel表
def drop_mgWeeklyReel(tableName):
    result = dropTableGeneral(tableName)
    return result


#mgWeeklyReel 删除记录
def delete_mgWeeklyReel(tableName,reelID):
    result = 0
    sqlStr = f"DELETE FROM {tableName}"
    try:

        sqlStr += " WHERE reelID = %s"
        valuesList = [reelID] 
        result = mysqlDB.executeWrite(sqlStr,tuple(valuesList))

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgWeeklyReel 增加记录
def insert_mgWeeklyReel(tableName,dataSet):
    result = 0
    try:

        saveSet = {}

        saveSet["userID"] = dataSet.get("userID", "") 

        saveSet["weekStart"] = dataSet.get("weekStart", "") 

        saveSet["weekEnd"] = dataSet.get("weekEnd", "") 

        saveSet["videoUrl"] = dataSet.get("videoUrl", "") 

        saveSet["gifUrl"] = dataSet.get("gifUrl", "") 

        try:
            daysTracked = int(dataSet.get("daysTracked")) 
        except:
            daysTracked = 0 
        saveSet["daysTracked"] = daysTracked

        saveSet["topMood"] = dataSet.get("topMood", "") 

        try:
            avgIntensity = float(dataSet.get("avgIntensity")) 
        except:
            avgIntensity = 0 
        saveSet["avgIntensity"] = avgIntensity

        saveSet["shareUrl"] = dataSet.get("shareUrl", "") 

        saveSet["createdYMDHMS"] = dataSet.get("createdYMDHMS", "") 

        saveSet["regID"] = dataSet.get("regID", "") 

        saveSet["regYMDHMS"] = dataSet.get("regYMDHMS", "") 

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        result = insertTableGeneral(tableName, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgWeeklyReel 修改记录
def update_mgWeeklyReel(tableName,reelID,dataSet):
    result = -2
    try:
        saveSet = {}

        userID = dataSet.get("userID") 
        if userID:
            saveSet["userID"] = userID

        weekStart = dataSet.get("weekStart") 
        if weekStart:
            saveSet["weekStart"] = weekStart

        weekEnd = dataSet.get("weekEnd") 
        if weekEnd:
            saveSet["weekEnd"] = weekEnd

        videoUrl = dataSet.get("videoUrl") 
        if videoUrl:
            saveSet["videoUrl"] = videoUrl

        gifUrl = dataSet.get("gifUrl") 
        if gifUrl:
            saveSet["gifUrl"] = gifUrl

        try:
            daysTracked = int(dataSet.get("daysTracked")) 
            saveSet["daysTracked"] = daysTracked
        except:
            pass

        topMood = dataSet.get("topMood") 
        if topMood:
            saveSet["topMood"] = topMood

        try:
            avgIntensity = float(dataSet.get("avgIntensity")) 
            saveSet["avgIntensity"] = avgIntensity
        except:
            pass

        shareUrl = dataSet.get("shareUrl") 
        if shareUrl:
            saveSet["shareUrl"] = shareUrl

        createdYMDHMS = dataSet.get("createdYMDHMS") 
        if createdYMDHMS:
            saveSet["createdYMDHMS"] = createdYMDHMS

        modifyID = dataSet.get("modifyID") 
        if modifyID:
            saveSet["modifyID"] = modifyID

        modifyYMDHMS = dataSet.get("modifyYMDHMS") 
        if modifyYMDHMS:
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            saveSet["delFlag"] = delFlag

        keySqlstr = "reelID = %s"
        keyValues = [reelID]

        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgWeeklyReel 查询记录
def query_mgWeeklyReel(tableName,reelID = "0", delFlag = "0", mode = "full",limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    columns = "*"
    valuesList = []
    sqlStr = f"SELECT {columns} FROM {tableName}"

    try:

        try:
            reelID = int(reelID)
        except:
            reelID = 0

        if reelID > 0:
            sqlStr =  sqlStr + " WHERE reelID = %s" 
            valuesList = [reelID]  

        #if limitNum > 0:
            #sqlStr += " LIMIT {0}".format(limitNum)

        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        if rtn > 0:
            dataList = mysqlDB.fetchAll()
            dataList = dataFormatConvert(dataList)
            result = list(dataList)

    except Exception as e:
        traceMsg = traceback.format_exc().strip("")
        errMsg = f"{e},{traceMsg}"
        # if _DEBUG:
            # _LOG.error(f"{errMsg}")

    return result


#mgWeeklyReel end 


#mgWeeklyReel end

#mindgram end



def checkMySqlDataBase():
    YMDHMS = misc.getTime()
    currYear = YMDHMS[0:4]
    YM = YMDHMS[0:6]
    YMD = YMDHMS[0:8]
    
    #user basic
    tableName = "USER_BASIC"
    if chkTableExist(tableName) == False:
        rtn = createUserBasic()

    tableName = "USER_weChatCode"
    if chkTableExist(tableName) == False:
        createUserWechatCode()

    tableName = tablename_convertor_hwinfo_report_record()
    if chkTableExist(tableName) == False:
        rtn = create_hwinfo_report_record(tableName)

    #mindgram tables
    tableName = tablename_convertor_mgAnnualFilm()
    if chkTableExist(tableName) == False:
        rtn = create_mgAnnualFilm(tableName)
    tableName = tablename_convertor_mgBadgeDef()
    if chkTableExist(tableName) == False:
        rtn = create_mgBadgeDef(tableName)
    tableName = tablename_convertor_mgFriend()
    if chkTableExist(tableName) == False:
        rtn = create_mgFriend(tableName)
    tableName = tablename_convertor_mgInviteLink()
    if chkTableExist(tableName) == False:
        rtn = create_mgInviteLink(tableName)
    tableName = tablename_convertor_mgMoodGuess()
    if chkTableExist(tableName) == False:
        rtn = create_mgMoodGuess(tableName)
    tableName = tablename_convertor_mgMoodPost()
    if chkTableExist(tableName) == False:
        rtn = create_mgMoodPost(tableName)
    tableName = tablename_convertor_mgMoodReaction()
    if chkTableExist(tableName) == False:
        rtn = create_mgMoodReaction(tableName)
    tableName = tablename_convertor_mgQuarterlyReport()
    if chkTableExist(tableName) == False:
        rtn = create_mgQuarterlyReport(tableName)
    tableName = tablename_convertor_mgSystemConfig()
    if chkTableExist(tableName) == False:
        rtn = create_mgSystemConfig(tableName)
    tableName = tablename_convertor_mgTcmDiagnosis()
    if chkTableExist(tableName) == False:
        rtn = create_mgTcmDiagnosis(tableName)
    tableName = tablename_convertor_mgUserBadge()
    if chkTableExist(tableName) == False:
        rtn = create_mgUserBadge(tableName)
    tableName = tablename_convertor_mgUserStats()
    if chkTableExist(tableName) == False:
        rtn = create_mgUserStats(tableName)
    tableName = tablename_convertor_mgWeeklyReel()
    if chkTableExist(tableName) == False:
        rtn = create_mgWeeklyReel(tableName)


def dropMySqlDataBase():
    YMDHMS = misc.getTime()
    currYear = YMDHMS[0:4]
    YM = YMDHMS[0:6]
    YMD = YMDHMS[0:8]
    
    #user basic
    tableName = "USER_BASIC"
    if chkTableExist(tableName):
        rtn = dropUserBasic()

    tableName = "USER_weChatCode"
    if chkTableExist(tableName):
        rtn = dropUserWechatCode()

    tableName = tablename_convertor_hwinfo_report_record()
    if chkTableExist(tableName):
        rtn = drop_hwinfo_report_record(tableName)

    #mindgram tables
    tableName = tablename_convertor_mgAnnualFilm()
    if chkTableExist(tableName):
        rtn = drop_mgAnnualFilm(tableName)
    tableName = tablename_convertor_mgBadgeDef()
    if chkTableExist(tableName):
        rtn = drop_mgBadgeDef(tableName)
    tableName = tablename_convertor_mgFriend()
    if chkTableExist(tableName):
        rtn = drop_mgFriend(tableName)
    tableName = tablename_convertor_mgInviteLink()
    if chkTableExist(tableName):
        rtn = drop_mgInviteLink(tableName)
    tableName = tablename_convertor_mgMoodGuess()
    if chkTableExist(tableName):
        rtn = drop_mgMoodGuess(tableName)
    tableName = tablename_convertor_mgMoodPost()
    if chkTableExist(tableName):
        rtn = drop_mgMoodPost(tableName)
    tableName = tablename_convertor_mgMoodReaction()
    if chkTableExist(tableName):
        rtn = drop_mgMoodReaction(tableName)
    tableName = tablename_convertor_mgQuarterlyReport()
    if chkTableExist(tableName):
        rtn = drop_mgQuarterlyReport(tableName)
    tableName = tablename_convertor_mgSystemConfig()
    if chkTableExist(tableName):
        rtn = drop_mgSystemConfig(tableName)
    tableName = tablename_convertor_mgTcmDiagnosis()
    if chkTableExist(tableName):
        rtn = drop_mgTcmDiagnosis(tableName)
    tableName = tablename_convertor_mgUserBadge()
    if chkTableExist(tableName):
        rtn = drop_mgUserBadge(tableName)
    tableName = tablename_convertor_mgUserStats()
    if chkTableExist(tableName):
        rtn = drop_mgUserStats(tableName)
    tableName = tablename_convertor_mgWeeklyReel()
    if chkTableExist(tableName):
        rtn = drop_mgWeeklyReel(tableName)


checkMySqlDataBase()
#check mysql database end

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pass
        import platform
        if platform.system()=='Linux':
            import pdb
            pdb.set_trace()
            msg = sys.argv[1]
            checkMySqlDataBase()

