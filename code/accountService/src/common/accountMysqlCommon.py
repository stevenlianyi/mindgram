#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#Filename: mysqlCommon.py  
#Date: 2020-04-01
#Description:   mysql 处理代码

#mysql数据库信息也存储在这里, 主要是只有部分程序需要处理mysql数据库, 读写已经分离, 目前主要是采用sql语句处理, 已经防止注入攻击. 


_VERSION="20250729"

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

#global defintion/common var etc.
from common import accountDefinition as comGD

from common import accountFuncCommon as comFC
#code/decode functions
#from common import codingDecoding as comCD

#common functions(log,time,string, json etc)
from common import miscCommon as misc

#setting files
from config import accountMysqlSettings as mysqlSettings

from config import accountBasicSettings as settings

HOME_DIR = settings._HOME_DIR

if "_LOG" not in dir() or not _LOG:
    logfilepath = os.path.join(HOME_DIR, comGD._DEF_GENRAL_MYSQL_LOG_NAME)
#    _LOG = misc.setLogNew(comGD._DEF_XJY_MYSQL_TITLE, logfilepath)
    
_DEBUG = settings._DEBUG

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
            #以下需要根据项目修改 modify here
            if k in ["position", "regPosition", "fileIDList", 
                "coupon_type_list", "coupon_id_list", "coupon_fee_list", 
                ]: 
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
    
    
def queryTableGeneral(tableName, columns = "*", limitNum = 0):
    result = []
    
    sqlStr =   "SELECT %s FROM %s " % (columns, tableName )
    valuesList = []
        
    if limitNum > 0:
        sqlStr += " LIMIT {0}".format(limitNum)
    
    try:
            
        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        dataList = mysqlDB.fetchAll()
        result = dataList

    except:
        pass
    
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
    
    
#user  family begin
def create_USER_BASIC():
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
    ")  ENGINE=INNODB DEFAULT CHARSET utf8 COLLATE utf8_general_ci;" , 
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


def drop_USER_BASIC():
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
                    whereStr = "AND "
                else:
                    whereStr = "WHERE "
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
                    whereStr = "AND extJobLabel = %s "
                else:
                    whereStr = "WHERE extJobLabel = %s "
                valuesList.append(jobLabel)
                sqlStr += whereStr 

            elif roleName:
                if valuesList:
                    whereStr = "AND roleName = %s "
                else:
                    whereStr = "WHERE roleName = %s "
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
def delete_USER_BASIC(loginID):
    result = 0
    tableName = "USER_BASIC"
    try:
    
        sqlStr = "DELETE FROM %s WHERE loginID = \"%s\";" % (tableName, loginID)
        rtn = mysqlDB.executeWrite(sqlStr)
        result = rtn

    except:
        pass
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
#user  family end


#wechat code  family begin
def create_UserWechatCode():
    tableName = "USER_weChatCode"
    aList  = ["CREATE TABLE IF NOT EXISTS %s("
    "recID INT AUTO_INCREMENT PRIMARY KEY,", 
    "loginID CHAR(32) NOT NULL,", 
    "openID CHAR(40) NOT NULL,", 
    "YMDHMS CHAR(16) ,", 
    "index (loginID, openID)", 
    ")  ENGINE=INNODB DEFAULT CHARSET utf8 COLLATE utf8_general_ci;" , 
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    return result


def drop_UserWechatCode():
    tableName = "USER_weChatCode"
    result = dropTableGeneral(tableName)
    return result
    

#SELECT * FROM USER_weChatCode WHERE loginID = "13910710766";
def query_UserWechatCode(loginID,  openID = ""):
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
        dataList = mysqlDB.fetchAll()
        dataList = dataFormatConvert(dataList)
        result = list(dataList)        
                
    except:
        pass
    return result
    
    
#DELETE  FROM USER_weChatCode WHERE loginID = "13910710766";
def delete_UserWechatCode(loginID, openID = ""):
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
    
    
def insert_UserWechatCode(loginID, dataSet):
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
    
    
def update_UserWechatCode(loginID, dataSet):
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


#user  wechart pay  record begin
def create_WEIXIN_PAY():
    tableName = "WEIXIN_PAY"
    aList  = ["CREATE TABLE IF NOT EXISTS %s("
    "tradeNo CHAR(32) PRIMARY KEY,",
    "loginID CHAR(32) ,", 
    "fee INT NOT NULL,", 
    "delFlag CHAR(1) ,", 
    "status CHAR(1) ,", 
    "createYMDHMS CHAR(16) ,", 
    "modifyYMDHMS CHAR(16) ,", 
    #weixin data begin
    "appid CHAR(32),", 
    "mch_id CHAR(32),", 
    "device_info CHAR(32),", 
    "nonce_str CHAR(32),", 
    "sign CHAR(32),", 
    "sign_type CHAR(32),", 
    "result_code CHAR(16),", 
    "err_code CHAR(32),", 
    "err_code_des VARCHAR(128),", 
    "openID CHAR(128),", 
    "is_subscribe CHAR(1),", 
    "trade_type CHAR(16),", 
    "bank_type CHAR(32),", 
    "total_fee INT ,", 
    "settlement_total_fee INT ,", 
    "fee_type CHAR(8) ,", 
    "cash_fee_type CHAR(16),", 
    "cash_fee INT,", 
    "coupon_fee INT,", 
    "coupon_count INT,", 
    "coupon_type_list VARCHAR(200),", 
    "coupon_id_list VARCHAR(300),", 
    "coupon_fee_list VARCHAR(300),", 
    "transaction_id CHAR(32),", 
    "attach VARCHAR(128),", 
    "time_end CHAR(16) "
    #weixin data end
    ")  ENGINE=INNODB DEFAULT CHARSET utf8 COLLATE utf8_general_ci;" , 
    ]
    tempStr = "".join(aList)
    sqlStr = tempStr % (tableName)
    rtn = mysqlDB.executeWrite(sqlStr)
    result = chkTableExist(tableName)
    if result:
        pass
        sqlStr = "CREATE INDEX {1} ON {0}({1}) ".format(tableName, "loginID")
        rtn = mysqlDB.executeWrite(sqlStr)

    return result


#删除WEIXIN_PAY表
def drop_WEIXIN_PAY():
    tableName = "WEIXIN_PAY"
    result = dropTableGeneral(tableName)
    return result


#WEIXIN_PAY 删除记录
def delete_WEIXIN_PAY(tradeNo):
    result = 0
    tableName = "WEIXIN_PAY"
    sqlStr = "DELETE FROM %s " % (tableName )
    try:

        sqlStr += " WHERE tradeNo = %s "
        valuesList = [tradeNo] 
        result = mysqlDB.executeWrite(sqlStr,tuple(valuesList))

    except:
        pass

    return result


#WEIXIN_PAY 增加记录
def insert_WEIXIN_PAY(dataSet):
    result = 0
    tableName = "WEIXIN_PAY"
    try:

        saveSet = {}

        saveSet["tradeNo"] = dataSet.get("tradeNo", "") 

        saveSet["loginID"] = dataSet.get("loginID", "") 

        try:
            fee = int(dataSet.get("fee")) 
        except:
            fee = 0 
        saveSet["fee"] = fee

        saveSet["delFlag"] = dataSet.get("delFlag", "0") 

        saveSet["status"] = dataSet.get("status", "") 

        saveSet["createYMDHMS"] = dataSet.get("createYMDHMS", "") 

        saveSet["appid"] = dataSet.get("appid", "") 

        saveSet["mch_id"] = dataSet.get("mch_id", "") 

        saveSet["device_info"] = dataSet.get("device_info", "") 

        saveSet["nonce_str"] = dataSet.get("nonce_str", "") 

        saveSet["sign"] = dataSet.get("sign", "") 

        saveSet["sign_type"] = dataSet.get("sign_type", "") 

        saveSet["result_code"] = dataSet.get("result_code", "") 

        saveSet["err_code"] = dataSet.get("err_code", "") 

        saveSet["err_code_des"] = dataSet.get("err_code_des", "") 

        saveSet["openID"] = dataSet.get("openID", "") 

        saveSet["is_subscribe"] = dataSet.get("is_subscribe", "") 

        saveSet["trade_type"] = dataSet.get("trade_type", "") 

        saveSet["bank_type"] = dataSet.get("bank_type", "") 

        try:
            total_fee = int(dataSet.get("total_fee")) 
        except:
            total_fee = 0 
        saveSet["total_fee"] = total_fee

        try:
            settlement_total_fee = int(dataSet.get("settlement_total_fee")) 
        except:
            settlement_total_fee = 0 
        saveSet["settlement_total_fee"] = settlement_total_fee

        saveSet["fee_type"] = dataSet.get("fee_type", "") 

        saveSet["cash_fee_type"] = dataSet.get("cash_fee_type", "") 

        try:
            cash_fee = int(dataSet.get("cash_fee")) 
        except:
            cash_fee = 0 
        saveSet["cash_fee"] = cash_fee

        try:
            coupon_fee = int(dataSet.get("coupon_fee")) 
        except:
            coupon_fee = 0 
        saveSet["coupon_fee"] = coupon_fee

        try:
            coupon_count = int(dataSet.get("coupon_count")) 
        except:
            coupon_count = 0 
        saveSet["coupon_count"] = coupon_count

        saveSet["coupon_type_list"] = dataSet.get("coupon_type_list", "") 

        saveSet["coupon_id_list"] = dataSet.get("coupon_id_list", "") 

        saveSet["coupon_fee_list"] = dataSet.get("coupon_fee_list", "") 

        saveSet["transaction_id"] = dataSet.get("transaction_id", "") 

        saveSet["attach"] = dataSet.get("attach", "") 

        saveSet["time_end"] = dataSet.get("time_end", "") 


        result = insertTableGeneral(tableName, saveSet)

    except:
        pass

    return result


#WEIXIN_PAY 修改记录
def update_WEIXIN_PAY(tradeNo,dataSet):
    result = 0
    tableName = "WEIXIN_PAY"
    try:
        saveSet = {}

        loginID = dataSet.get("loginID") 
        if loginID:
            saveSet["loginID"] = loginID

        fee = dataSet.get("fee") 
        if fee:
            try:
                fee = int(dataSet.get("fee")) 
                saveSet["fee"] = fee
            except:
                pass

        delFlag = dataSet.get("delFlag") 
        if delFlag:
            saveSet["delFlag"] = delFlag

        status = dataSet.get("status") 
        if status:
            saveSet["status"] = status

#        createYMDHMS = dataSet.get("createYMDHMS") 
#        if createYMDHMS:
#            saveSet["createYMDHMS"] = createYMDHMS

        modifyYMDHMS = dataSet.get("modifyYMDHMS") 
        if modifyYMDHMS:
            saveSet["modifyYMDHMS"] = modifyYMDHMS

        appid = dataSet.get("appid") 
        if appid:
            saveSet["appid"] = appid

        mch_id = dataSet.get("mch_id") 
        if mch_id:
            saveSet["mch_id"] = mch_id

        device_info = dataSet.get("device_info") 
        if device_info:
            saveSet["device_info"] = device_info

        nonce_str = dataSet.get("nonce_str") 
        if nonce_str:
            saveSet["nonce_str"] = nonce_str

        sign = dataSet.get("sign") 
        if sign:
            saveSet["sign"] = sign

        sign_type = dataSet.get("sign_type") 
        if sign_type:
            saveSet["sign_type"] = sign_type

        result_code = dataSet.get("result_code") 
        if result_code:
            saveSet["result_code"] = result_code

        err_code = dataSet.get("err_code") 
        if err_code:
            saveSet["err_code"] = err_code

        err_code_des = dataSet.get("err_code_des") 
        if err_code_des:
            saveSet["err_code_des"] = err_code_des

        openID = dataSet.get("openID") 
        if openID:
            saveSet["openID"] = openID

        is_subscribe = dataSet.get("is_subscribe") 
        if is_subscribe:
            saveSet["is_subscribe"] = is_subscribe

        trade_type = dataSet.get("trade_type") 
        if trade_type:
            saveSet["trade_type"] = trade_type

        bank_type = dataSet.get("bank_type") 
        if bank_type:
            saveSet["bank_type"] = bank_type

        total_fee = dataSet.get("total_fee") 
        if total_fee:
            try:
                total_fee = int(dataSet.get("total_fee")) 
                saveSet["total_fee"] = total_fee
            except:
                pass

        settlement_total_fee = dataSet.get("settlement_total_fee") 
        if settlement_total_fee:
            try:
                settlement_total_fee = int(dataSet.get("settlement_total_fee")) 
                saveSet["settlement_total_fee"] = settlement_total_fee
            except:
                pass

        fee_type = dataSet.get("fee_type") 
        if fee_type:
            saveSet["fee_type"] = fee_type

        cash_fee_type = dataSet.get("cash_fee_type") 
        if cash_fee_type:
            saveSet["cash_fee_type"] = cash_fee_type

        cash_fee = dataSet.get("cash_fee") 
        if cash_fee:
            try:
                cash_fee = int(dataSet.get("cash_fee")) 
                saveSet["cash_fee"] = cash_fee
            except:
                pass

        coupon_fee = dataSet.get("coupon_fee") 
        if coupon_fee:
            try:
                coupon_fee = int(dataSet.get("coupon_fee")) 
                saveSet["coupon_fee"] = coupon_fee
            except:
                pass

        coupon_count = dataSet.get("coupon_count") 
        if coupon_count:
            try:
                coupon_count = int(dataSet.get("coupon_count")) 
                saveSet["coupon_count"] = coupon_count
            except:
                pass

        coupon_type_list = dataSet.get("coupon_type_list") 
        if coupon_type_list:
            saveSet["coupon_type_list"] = coupon_type_list

        coupon_id_list = dataSet.get("coupon_id_list") 
        if coupon_id_list:
            saveSet["coupon_id_list"] = coupon_id_list

        coupon_fee_list = dataSet.get("coupon_fee_list") 
        if coupon_fee_list:
            saveSet["coupon_fee_list"] = coupon_fee_list

        transaction_id = dataSet.get("transaction_id") 
        if transaction_id:
            saveSet["transaction_id"] = transaction_id

        attach = dataSet.get("attach") 
        if attach:
            saveSet["attach"] = attach

        time_end = dataSet.get("time_end") 
        if time_end:
            saveSet["time_end"] = time_end

        keySqlstr = "tradeNo = %s"
        keyValues = [tradeNo]

        result = updateTableGeneral(tableName, keySqlstr,  keyValues, saveSet)

    except:
        pass

    return result


#SELECT * FROM USER_BASIC WHERE loginID = "13910710766";
def query_WEIXIN_PAY(tradeNo = "",loginID = "",delFlag = "0", mode = "full",limitNum = comGD._DEF_MAX_QUERY_LIMIT_NUM):
    result = []
    tableName = "WEIXIN_PAY"
    columns = "*"
    valuesList = []
    sqlStr = "SELECT {0} FROM {1}".format(columns, tableName)

    try:
        if delFlag in ["0","1"]:
            if tradeNo != "":
                sqlStr =  sqlStr + " WHERE  delFlag = %s and tradeNo = %s" 
                valuesList = [delFlag,tradeNo]  
            elif loginID != "":
                sqlStr =  sqlStr + " WHERE  delFlag = %s and loginID = %s" 
                valuesList = [delFlag,loginID]  
        else:
            if tradeNo != "":
                sqlStr =  sqlStr + " WHERE tradeNo = %s" 
                valuesList = [tradeNo]  
            elif loginID != "":
                sqlStr =  sqlStr + " WHERE loginID = %s" 
                valuesList = [loginID]  
            
        if limitNum > 0:
            sqlStr += " LIMIT {0}".format(limitNum)

        rtn = mysqlDB.executeRead(sqlStr, tuple(valuesList))
        dataList = mysqlDB.fetchAll()
        dataList = dataFormatConvert(dataList)
        result = list(dataList)  

    except:
        pass
    return result

#user  wechart pay end


def checkMySqlDataBase():
    #user basic
    YMDHMS = misc.getTime()
    YM = YMDHMS[0:6]
    YMD = YMDHMS[0:8]
    
    tableName = "USER_BASIC"
    if (chkTableExist(tableName) == False):
        rtn = create_USER_BASIC()
        
    tableName = "USER_weChatCode"
    if (chkTableExist(tableName) == False):
        rtn = create_UserWechatCode()
           
    tableName = "WEIXIN_PAY"
    if (chkTableExist(tableName) == False):
        rtn = create_WEIXIN_PAY()  
        

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
            # checkMySqlDataBase()

