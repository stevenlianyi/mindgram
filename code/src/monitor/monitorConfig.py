_VERSION = "20260606"

currWorkMode="monitor"

monitorWorkDir = r"/data/mindgram/src/monitor"

monitorFileStatusFileName = "tempMonitorFileName.json"

processData = [
#common part
#{"key":"redis-server","cmd":"sh /data/redis/restore > /dev/null ","param":":16379"}, #redis service
#{"key":"nginx","cmd":"/usr/local/nginx/nginx > /dev/null ","param":""}, #nginx service
#application
    {
        "key":"accountApp:application",
        "cmd":"cd /data/accountService/src/accountService; ./restore_acc.sh ", 
        "param":"",
        "file":"/data/accountService/src/accountService/accountAppPost.py",
        "fileList":["/data/accountService/src/config/accountsettings.py",
                    "/data/accountService/src/config/local_settings.py",
                    "/data/accountService/src/config/accountMysqlSettings.py",
                    "/data/accountService/src/config/accountRedisSettings.py",],
        # "num":3, #不检查数量就不要填, 或者填0
    },
    {
        "key":"ylwzRecvFiles:application",
        "cmd":"cd /data/mindgram/src/stockapi; ./restore_file.sh ", 
        "param":"",
        "file":"/data/mindgram/src/stockapi/ylwzRecvFiles.py",
        "fileList":["/data/mindgram/src/config/basicSettings.py",
                    "/data/mindgram/src/config/local_settings.py",
                    "/data/mindgram/src/common/globalDefinition.py",
                    "/data/mindgram/src/config/redisSettings.py",
                    "/data/mindgram/src/common/funcCommon.py",],
        # "num":3, #不检查数量就不要填, 或者填0
    },
    {
        "key":"transferMysql.py",
        "cmd":"cd /data/mindgram/src/processor; ./restore_trans.sh ", 
        "param":"",
        "file":"/data/mindgram/src/processor/transferStockMysql.py",
        "fileList":["/data/mindgram/src/config/basicSettings.py",
                    "/data/mindgram/src/config/local_settings.py",
                    "/data/mindgram/src/common/globalDefinition.py",
                    "/data/mindgram/src/common/funcCommon.py",
                    "/data/mindgram/src/config/redisSettings.py",
                    "/data/mindgram/src/config/mysqlSettings.py",],
        # "num":3, #不检查数量就不要填, 或者填0
    },
]

existProcessKeys = [
]

serviceMonitorData = [

]
