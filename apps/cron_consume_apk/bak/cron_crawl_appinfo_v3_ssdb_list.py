#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2017-03-08 17:48:52

import sys
import os
import json
from config import *
import redis
import multiprocessing
import time
import random
import traceback
import urllib
import logging
import datetime
log_path = os.path.join(os.getcwd(),"log")
print log_path
def init_logger(name, filename):
    logger = logging.getLogger(name)
    log_file = os.path.join(log_path, filename)
    print log_file
    log_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    log_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    return logger

logger = init_logger('mylogger', 'log.txt')
logger.info("start...")
"""
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    #filename='./%s.%s.log'%(sys.argv[0],datetime.datetime.now().strftime("%Y%m%d%H%M%S")),
    filename='./%s.log'%(sys.argv[0]),
    filemode='a')
"""
wait_time = 5#数据库没有数据之后的间隔访问时间
def startthread(url):
    logger.debug(url)
    try:
        logger.debug("request url:%s"%url)
        response = urllib.urlopen(url).read()
        return response
    except Exception as e:
        logger.debug(str(e), exc_info=True)
        return None
from SSDB import SSDB
def select_platform_and_get_apk():
    try:
        pass
        ssdb_wait = SSDB(ssdb_host, ssdb_wait_port)
        ssdb_save = SSDB(ssdb_host, ssdb_save_port)
    except Exception , e:
        pass
        print e
        sys.exit(0)
    logger.info("connect ssdb sucess !!!")
    while 1:
        try:
            logger.debug("start request zlist ~")
            platforms = ssdb_wait.request("qlist",["","",-1]).data
            logger.debug("qlist:%s"%str(platforms))
            if len(platforms) == 0:time.sleep(60)
            choice_keys = set()
            for xplatform in platforms:
                for xxplatform in crawl_db:
                    if xxplatform in xplatform:
                        choice_keys.add(xxplatform)
                        break
            platform = random.choice(list(choice_keys))
            simKey = [xplatform for xplatform in  platforms if xplatform.startswith(platform)]
            logger.debug("crawed platform:%s"%simKey)
            if simKey:
                maxSimKey = max(simKey)
                logger.debug("%s:simkey:%s\t%s"%(platform,str(simKey),maxSimKey))
                apk_t = ssdb_wait.request("qpop_front",[maxSimKey,1]).data
                logger.debug("get pkg:%s"%str(apk_t))
                crawed_key = "crawed-"+platform
                if not(apk_t):
                    time.sleep(wait_time)
                    continue
                else:
                    apk = apk_t.strip()
                    if not(apk.replace(".","").isalnum()):continue
                    if len(apk.split(".")[-1]) > 20:continue
                    info_ismember = ssdb_save.request('hexists', [platform, apk.lower()])
                    #crawed_ismember =  ssdb_wait.request('zexists', [crawed_key, apk.lower()])
                    logger.debug("\t".join([platform,apk,
                                "have_info:%s,%s"%(info_ismember,info_ismember.data),]))
                    if info_ismember.data == 0:
                        logger.info("\t".join([str(m) for m in [apk,platform,maxSimKey,info_ismember.data]]))
                        url = "https://dm.umlife.com/api/appinfo/v1/getInfo?os=%s&pkg=%s"%(platform,apk)
                        #url = "http://127.0.0.1:8157/api/appinfo/v1/getInfo?os=%s&pkg=%s"%(platform,apk)
                        response = startthread(url)
                        logger.debug("response:%s"%repr(response))
                        #logger.debug("response:%s"%repr(startthread("https://dm.umlife.com/api/appinfo/v1/getInfo?os=%s&pkg=%s"%("ios","com.tencent.qq"))))
                        ssdb_wait.request("zset",[crawed_key,apk.lower(),1])
                        time.sleep(random.randint(0,10)*1.0/10)
            else:
                continue
        except Exception as e:
            logger.debug(str(e), exc_info=True)


#select_platform_and_get_apk()

pool = multiprocessing.Pool(crawl_thread_num)
for x_thread_num in range(crawl_thread_num):
    pool.apply_async(select_platform_and_get_apk,())
    #pool.apply_async(select_platform_and_get_apk,())

pool.close()
pool.join()


logging.info("all done")
#os._exit()

