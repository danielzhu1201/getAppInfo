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
#iosFile = os.path.abspath(sys.argv[1])
#androidFile = os.path.abspath(sys.argv[2])
#filedict = {
#        "ios":iosFile,
#        "android":androidFile
#    }

logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='./%s.%s.log'%(sys.argv[0],datetime.datetime.now().strftime("%Y-%m-%d")),
                        filemode='a')

red_get_apk = redis.Redis(db=redis_db["crawl_apk"])

apkdict = {}
for key in redis_db.keys():
    if key in crawl_db:
        pass
    else:
        continue
    red = redis.Redis(db=redis_db[key])
    apkdict.setdefault(key,set())
    while 1:
        lineT = red_get_apk.spop(key)
        if lineT == None:break
        line = lineT.split(" ")[0]
        logging.info("\t".join([str(m) for m in [line,key,redis_db[key],line,red.exists(line.strip().lower())]]))
        if red.exists(line.strip().lower()):
            pass
        else:
            apkdict[key].add(line)
        if len(apkdict[key]) >= crawl_threshold:
            break
 
def startthread(url):
    logging.info(url)
    try:
        response = urllib.urlopen(url).read()
    except:
        traceback.print_exc()

    time.sleep(random.random() * delay_time)

urlList = []
for key in apkdict.keys():
    apkset = apkdict[key]
    for apk in apkset:
        urlList.append("https://dm.umlife.com/api/appinfo/v1/getInfo?os=%s&pkg=%s"%(key,apk))
random.shuffle(urlList)

pool = multiprocessing.Pool(2)
for url in urlList:
    pool.apply_async(startthread,(url,))

pool.close()
pool.join()

logging.info("all done")


