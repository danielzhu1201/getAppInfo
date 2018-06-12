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

logging.basicConfig(
    level=logging.DEBUG,
#   format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='./%s.%s.log'%(sys.argv[0],datetime.datetime.now().strftime("%Y%m%d%H%M%S")),
    filemode='a')

wait_time = 5#数据库没有数据之后的间隔访问时间
def startthread(url):
    logging.debug(url)
    try:
        response = urllib.urlopen(url).read()
    except:
        traceback.print_exc()
def select_platform_and_get_apk():
    redis_dict = {
            "android": redis.Redis(db = redis_db["android"]),
            "ios": redis.Redis(db = redis_db["ios"]),
            "crawled": redis.Redis(db = redis_db["crawled"]),
        }
    while 1:
        platforms = redis_db.keys()
        platform = random.choice([xplatform for xplatform in platforms if xplatform in crawl_db])
        redis_get_apk = redis.Redis(db=redis_db["crawl_apk"])
        lineT = redis_get_apk.spop(platform)
        if lineT == None:
            time.sleep(wait_time)
            continue
        apk = lineT.split(" ")[0].strip()
        redis_platform = redis_dict[platform]
        redis_crawled = redis_dict["crawled"]
        exists_status = redis_platform.exists(apk.lower())
        exists_crawled = redis_crawled.sismember(platform,apk)
        logging.info("\t".join([str(m) for m in [apk,platform,redis_db[platform],exists_status,exists_crawled]]))
        if exists_status or exists_crawled:
            continue
        else:
            url = "http://dm.umlife.com/appinfo/api/v1/getInfo?os=%s&pkg=%s"%(platform,apk)
            startthread(url)
            redis_crawled.sadd(platform,apk)
            time.sleep(random.randint(0,10)*1.0/50)


#select_platform_and_get_apk()


pool = multiprocessing.Pool(crawl_thread_num)
for x_thread_num in range(crawl_thread_num):
    pool.apply_async(select_platform_and_get_apk,())
    #pool.apply_async(select_platform_and_get_apk,())

pool.close()
pool.join()



logging.info("all done")
#os._exit()

