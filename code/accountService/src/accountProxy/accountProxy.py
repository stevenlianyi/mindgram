#! /usr/bin/env python3
#encoding: utf-8

#import flup.server.fcgi as flups
from flask import Flask, request

application = Flask(__name__)

_VERSION="20220305"

import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
if sys.getdefaultencoding() != 'utf-8':
    pass
    #reload(sys)
    #sys.setdefaultencoding('utf-8')

import traceback

#global defintion/common var etc.
from common import accountDefinition as comGD

from common import miscCommon as misc

import accountProxyPost as userApp #modify here
appName = "accountProxy" #modify here
routeAddr = "/accproxy" #modify here
httpMethod = ["POST"] #modify here
appType = ""

# _DEBUG = True #modify here
_DEBUG = False #modify here

if "_LOG" not in dir() or not _LOG:
    _LOG = misc.setLogNew("PROXY", "accoutproxylog")
    
systemVersion = str(sys.version_info.major) + "." + str(sys.version_info.minor ) + "." + str(sys.version_info.micro )
_LOG.info("python version:[%s], start code version:[%s]" %(systemVersion, _VERSION))
    

@application.route(routeAddr, methods = httpMethod ) 
def main():
    rtnSet = {}
    
    try:
        #IP = "0.0.0.0"
        IP =  request.remote_addr
        try:
            x_forward_for = request.headers.get('X-Forwarded-For', '')
            aList = x_forward_for.split(",")
            for a in aList:
#                if  _DEBUG:
#                    _LOG.info("DEBUG:{0},{1},{2}".format(str(aList), len(aList),  str(a)))
                if len(a) > 3:
                    lastIP = a
                    IP = lastIP
#            if  _DEBUG:
#                _LOG.info("DEBUG:{0},{1},{2}".format(request.mimetype, len(lastIP),  str(lastIP)))

        except:
            pass
            
        environSet = {}
        # environSet["REQUEST_METHOD"] = "POST"
        # environSet["CONTENT_LENGTH"] = request.content_length
        # environSet["CONTENT_TYPE"] = request.content_type
        
        dataSet = {}
        if request.mimetype == "multipart/form-data":
            dataSet = request.form.to_dict(flat=False)
            
            if _DEBUG:
                _LOG.info("MR:form-data {0},{1},{2}".format(request.mimetype, misc.jsonDumps(dataSet),  type(dataSet)))
                
            rtnSet = userApp.post(_LOG, dataSet, IP, environSet, appType)

            if _DEBUG:
                _LOG.info("MS:json {0},{1}".format(request.mimetype, misc.jsonDumps(rtnSet)))
            
        elif  request.mimetype == "application/json":
            
            dataSet = request.json
            
            if _DEBUG:
                _LOG.info("MR:json {0},{1}".format(request.mimetype, misc.jsonDumps(dataSet)))

            rtnSet = userApp.post(_LOG, dataSet, IP, environSet, appType)
            
            if _DEBUG:
                _LOG.info("MS:json {0},{1}".format(request.mimetype, misc.jsonDumps(rtnSet)))
                
        else:
            if _DEBUG:
                _LOG.info("MR: {},{}".format(request.mimetype, request.data))

            try:
                dataSet = misc.jsonLoads(request.data)
                rtnSet = userApp.post(_LOG, dataSet, IP, environSet, appType)
                
                if _DEBUG:
                    _LOG.info("MS: {},{}".format(request.mimetype, misc.jsonDumps(rtnSet)))
            except:
                pass
            
        
    except Exception as e:
        f = sys._getframe().f_back
        data = appName
        errMsg = '%s' % (data)
        _LOG.error( '%s,%s,%s' %(errMsg, str(e),traceback.format_exc()))
    
    result = misc.jsonDumps(rtnSet)
    
    if _DEBUG:
        pass
#        MAX_PRINT_LEN = 10000
#        if len(result) > MAX_PRINT_LEN:
#            _LOG.info("S: MAX {0},{1},{2}".format(IP,appType, result[0:MAX_PRINT_LEN]))
#        else:
#            _LOG.info("S: {0},{1},{2}".format(IP,appType, result))
            
    return result
    
    
if __name__ == "__main__":    
    
    from werkzeug.contrib.fixers import ProxyFix
    application.wsgi_app = ProxyFix(application.wsgi_app)
    application.run(host='0.0.0.0')
