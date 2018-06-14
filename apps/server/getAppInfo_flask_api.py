#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2017-02-23 12:00:48

from flask import Flask,request,make_response
import sys
sys.path.append("./")
app = Flask(__name__)
import os 
import logging
#import redis
import json
#from getApkInfo import GetApkInfo
from config.config import *
import traceback
import datetime
import os
reload(sys)
sys.setdefaultencoding('utf8')
import socket

socket.setdefaulttimeout(None)

log_path = os.path.join(os.getcwd(),"log")
print log_path

def init_logger(name, filename):
    logger = logging.getLogger(name)
    print 'logger path = '+ os.path.join(log_path, filename)
    log_file = os.path.join(log_path, filename)
    if not logger.handlers:
        log_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    return logger
  
logger = init_logger('mylogger', 'log.txt')
logger.info("start...")

from SSDB import SSDB
class db():
    def __init__(self):
        self.ssdb = SSDB(ssdb_host, ssdb_save_port)

    def close(self):
        self.ssdb.close()

#redis_connect_dict = {}
#for info,dbint in redis_db.iteritems(): 
#    pool = redis.ConnectionPool(host=redis_host,port=redis_port,db=dbint)
#    redis_t = redis.Redis(connection_pool=pool)
#    redis_connect_dict[info] = redis_t

@app.route(r"/api/appinfo/v1/getInfo")
def get(): 
    #global redis_host
    #global redis_port
    #global redis_db




    #this section of code executes whenever there's a new request with /api/appinfo/v1/getInfo



    returnDict = None
    try:
        apks = [xapk for xapk in request.args.get('pkg',"").replace("[","").replace("]","").split(",") if xapk.strip() != ""] #取出每一个请求的应用名称
        db_des = request.args.get("os",False)
        columns = set([column.strip().lower() for column in request.args.get('columns',"").replace("[","").replace("]","").split(",") if len(column.strip()) != 0])
        if len(apks) == 0 or db_des not in platform:
            returnDict = {"status":101}
            returnDict["message"] = statusToMessage[returnDict["status"]]
        elif len(apks) > 50:
            returnDict = {"status":102}
            returnDict["message"] = statusToMessage[returnDict["status"]]
        #elif  #频率判断
        else:
            #正常情况
            returnDict = {}
            returnDict["status"] = 200
            returnDict["message"] = statusToMessage[returnDict["status"]]
            returnDict["results"] = {}
            print 'db_des = '+str(db_des)
            print 'apks = '+str(apks)
            allApksInfoDict = getAppInfo(db_des,apks)
            display_columns = platfrom_display.get(db_des,[]) #db_des = os type --> android/ios
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
                        if (display_columns == False or xcolumns in display_columns) and (len(columns) == 0 or xcolumns in columns):
                            returnDict["results"][xapk][xcolumns] = xvalues
                        else:
                            pass
    except Exception,e:
        logger.error(str(e), exc_info=True)
        #logging.warning(traceback.format_exc())
    finally:
        try:
            return make_response(json.dumps(returnDict,ensure_ascii=False))
        except:
            logging.warning("error",e)
            return make_response(json.dumps(returnDict))

def getAppInfo(db_des,apks):
    #global redis_connect_dict
    try:
        ssdb_save = db() #ssdb instance declared as a class, see above   #using *** ssdb_save ***
        apksinfo = {}
        for apk in apks:
            #xapkreturninfo = redis_connect_dict.get(db_des).get(apk.lower())
            print "hget:%s,%s"%(db_des, apk.lower())
            logger.debug("hget:%s,%s"%(db_des, apk.lower()))
            xapkreturninfo = ssdb_save.ssdb.request('hget', [db_des, apk.lower()]) #can't find in this database
            print 'xapkreturninfo : '+str(xapkreturninfo)+'  '+str(xapkreturninfo.not_found())
            if xapkreturninfo.not_found() == False:
                logger.debug("return:%s"%str(xapkreturninfo))
                #print dir(xapkreturninfo),xapkreturninfo.not_found
                apksinfo[apk] = json.loads(xapkreturninfo.data)
        
        missApks = set()
        for apk in apks:
            if apk not in apksinfo:
                missApks.add(apk)    #添加miss掉的apks到 **missApks**
        if missApks:
            logging.debug("%s:%s"%("missApk",str(missApks)))
        missApkInfo = None
        if len(missApks):
            missApkInfo = GetApkInfo().getApkInfo(missApks,db_des)

        if missApkInfo:
            print '******* in miss apk info ************'
            print str(missApkInfo.iteritems())
            for k,v in missApkInfo.iteritems():
                print 'in iterator'
                print k
                print v
                if v is None:
                    logging.info("key:%s,value:%s"%(k,str(v)))
                    print ("key:%s,value:%s"%(k,str(v)))
                    continue
                else:
                    try:
                        if len(set(v.keys()).difference(set(["userRatingCount","trackViewUrl","pkgName"]))) == 0: 
                        # if len(set(v.keys())) - len((set(["userRatingCount","trackViewUrl","pkgName"]))) == 0: 
                            '''print 'cond 1'
                            print set(v.keys())
                            print (set(v.keys()).difference(set(["userRatingCount","trackViewUrl","pkgName"])))'''
                            continue
                    except Exception as e:
                        logging.error("v type:%s"%str(type(v)))
                        logger.error(str(e), exc_info=True)

                print 'out of if else'
                if v:
                    print 'in V'
                    v[crawl_time_keyword] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #加入抓取时间
                    #redis_connect_dict.get(db_des).set(k.lower(),json.dumps(v))
                    result = ssdb_save.ssdb.request("hset",[db_des,k.lower(),json.dumps(v)])
                    print result
                    apksinfo[k] = v
        returnDict  = {}
        #print apksinfo
        for k,v in apksinfo.iteritems():
            returnDict.setdefault(k,{})
            for xk,xv in v.iteritems():
                if xk in crawl_time_keyword:
                    continue
                elif isinstance(xv,list):
                    returnDict[k][xk] = [xxv.encode("utf8") for xxv in xv]
                elif  isinstance(xv,int):
                    returnDict[k][xk] = int(xv)
                elif isinstance(xv,str) and xv.strip().startswith("["):
                    returnDict[k][xk] = [xxv.encode("utf8") for xxv in eval(xv)]
                elif isinstance(xv,str) and xv.strip() in ["False","True"]:
                        returnDict[k][xk] = eval(xv)
                else:
                    try:
                        returnDict[k][xk] = xv.encode("utf8")
                    except:
                        returnDict[k][xk] = xv
        return returnDict
    except Exception,e:
        logger.error(str(e), exc_info=True)
        return {}
    finally:
        try:
            ssdb_save.close()
        except Exception as e:
            logger.error(str(e), exc_info=True)

if __name__ == "__main__":
    print "start"
    app.run(host="0.0.0.0",port = 8129, debug=True)
