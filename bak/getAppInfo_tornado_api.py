#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2017-02-23 12:00:48

#!/usr/bin/env python 
# coding=utf-8 

import os 
import tornado.web 
import tornado.ioloop
import logging
import redis
import json
from getApkInfo import GetApkInfo
from config import *
import traceback
import sys  
reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.INFO,format='%(message)s')
class ApiHandler(tornado.web.RequestHandler): 
    def get(self): 
        global redis_host
        global redis_port
        global redis_db
        returnDict = None
        apks = self.get_argument('pkg',False).replace("[","").replace("]","").split(",")
        os = self.get_argument("os",False)
        if apks == False or os not in platform:
            returnDict = {"status":102}
            returnDict["message"] = statusToMessage[returnDict["status"]]
        elif len(apks) > 50:
            returnDict = {"status":104}
            returnDict["message"] = statusToMessage[returnDict["status"]]
        #elif  #频率判断
        else:
            returnDict = {}
            returnDict["status"] = 200
            returnDict["message"] = statusToMessage[returnDict["status"]]
            returnDict["results"] = {}
            allApksInfoDict = self.getAppInfo(os,apks)
            display_columns = platfrom_display.get(os,[])
            if len(display_columns) == 0:
                display_columns = False
            returnApknameSet = set(allApksInfoDict.keys())
            for xapk in apks:
                if xapk not in returnApknameSet:
                    returnDict["results"][xapk] = {"appStatus":1,}
                else:
                    returnDict["results"].setdefault(xapk,{})
                    returnDict["results"][xapk]["appStatus"] = 0
                    for xcolumns,xvalues in allApksInfoDict.get(xapk,{}).iteritems():
                        if display_columns == False or xcolumns in display_columns:
                            returnDict["results"][xapk][xcolumns] = xvalues
                        else:
                            pass
        """
        for xk,xv in returnDict.iteritems():
            if isinstance(xv,dict):
                for xxk,xxv in xv.iteritems():
                    if isinstance(xxv,dict):
                        for xxxk,xxxv in xxv.iteritems():
                            print xxxk,type(xxxv)
                    print xxk,type(xxv)
            print xk,type(xv)
        """
        print json.dumps(returnDict,ensure_ascii=False,indent=4)
        return self.finish(json.dumps(returnDict,ensure_ascii=False))

    def getAppInfo(self,os,apks):
        connect_redis_db = redis_db.get(os)
        pool = redis.ConnectionPool(host=redis_host,port=redis_port,db=connect_redis_db)
        red = redis.Redis(connection_pool=pool)

        apksinfo = {}
        for apk in apks:
            xapkreturninfo = red.hgetall(apk.lower())
            if xapkreturninfo:
                apksinfo[apk] = xapkreturninfo
        returnApks = set()
        missApks = set()
        for apk in apks:
            if apk not in apksinfo:
                missApks.add(apk)
        if missApks:print "missApk:",missApks
        missApkInfo = None
        if len(missApks):
            missApkInfo = GetApkInfo().getApkInfo(missApks,os)
        if missApkInfo:
            for k,v in missApkInfo.iteritems():
                if len(set(v.keys()).difference(set(["trackViewUrl","pkgName"]))) == 0:
                    continue
                if v:
                    red.hmset(k.lower(),v)
                    apksinfo[k] = v
        returnDict  = {}
        for k,v in apksinfo.iteritems():
            returnDict.setdefault(k,{})
            for xk,xv in v.iteritems():
                if isinstance(xv,list):
                    returnDict[k][xk] = [xxv.encode("utf8") for xxv in xv]
                elif  isinstance(xv,int) or xv.isdigit():
                    returnDict[k][xk] = int(xv)
                elif isinstance(xv,str) and xv.strip().startswith("["):
                    returnDict[k][xk] = [xxv.encode("utf8") for xxv in eval(xv)]
                elif isinstance(xv,str) and xv.strip().lower() in ["false","true"]:
                        returnDict[k][xk] = eval(xv)
                else:
                    try:
                        returnDict[k][xk] = xv.encode("utf8")
                    except:
                        returnDict[k][xk] = xv
        return returnDict

if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/appinfo/api/v1/getInfo", ApiHandler),
        ])
    application.listen(8157)
    tornado.ioloop.IOLoop.instance().start()
