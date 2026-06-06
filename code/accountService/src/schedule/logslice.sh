#log slice and backup  2022-03-05
lastday=`/bin/date -d last-day +%Y%m%d`
logsourcedir=/data/accountService/log
logbackupdir=/data/accountService/log/backup
tarbackupdir=/data/accountService/log/tarbackup

fileName=accintslog
/bin/cp ${logsourcedir}/${fileName}  ${logbackupdir}/${fileName}$lastday 
/bin/echo '' > ${logsourcedir}/${fileName}

fileName=miniprogramlog
/bin/cp ${logsourcedir}/${fileName}  ${logbackupdir}/${fileName}$lastday 
/bin/echo '' > ${logsourcedir}/${fileName}

fileName=accoutproxylog
/bin/cp ${logsourcedir}/${fileName}  ${logbackupdir}/${fileName}$lastday 
/bin/echo '' > ${logsourcedir}/${fileName}


cd ${logbackupdir}
backday=`date -d "-7 days" +%Y%m%d`
#tar and backup
tar -czf backup_$backday.tar.gz *$backday *$backday??
mv backup_$backday.tar.gz ${tarbackupdir}
rm -f *$backday *$backday??

cd ${tarbackupdir}
tarRemoveDay=`date -d "-60 days" +%Y%m%d`
rm -f backup_$tarRemoveDay.tar.gz

