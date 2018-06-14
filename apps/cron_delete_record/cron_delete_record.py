#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2017-02

import sys
sys.path.append("./")
from config.config import *
import redis
import os
from config import *
import datetime
import json
import logging

logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s (filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='./%s.%s.log'%(sys.argv[0],datetime.datetime.now().strftime("%Y-%m-%d")),
                        filemode='a')


nowtime = datetime.datetime.now()
red_apk_db = redis.Redis(host=redis_host,port=redis_port,db=redis_db["crawl_apk"])


for platform in crawl_db:
    pool=redis.ConnectionPool(db=redis_db[platform])  
    r = redis.StrictRedis(connection_pool=pool)
    apks = r.keys()
    for apk in apks:
        apkinfo = json.loads(r.get(apk))
        apkinfo.get(crawl_time_keyword,"2017-03-01 00:00:00")
        crawl_time = datetime.datetime.strptime(apkinfo.get(crawl_time_keyword,"2017-03-01 00:00:00"),"%Y-%m-%d %H:%M:%S")
        if [nowtime-crawl_time][0].days > apkinfo_life_days:
            logging.info("\t".join([str(m) for m in [apkinfo.get(crawl_time_keyword,"2017-03-01 00:00:00"),apk,platform,"try to delete apkinfo"]]))
            res.delete(apk) 
        else:
            #print apkinfo.get(crawl_time_keyword,"2017-03-01 00:00:00"),apk,platform,"ignore"
            #raw_input()
            continue
        apk_key = apkinfo.get(info_apk_key[platform],False)
        if apk_key:
            apkreal = apkinfo.get(apk_key,False)
            if apkreal:
                red_apk_db.sadd("\t".join(platform,apkreal))
                continue
        red_apk_db.sadd("\t".join(platform,apk))
    
            
        
