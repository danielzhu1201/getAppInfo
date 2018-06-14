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
from SSDB import SSDB


WAIT_TIME = 5 * 60#数据库没有数据之后的间隔访问时间

def init_logger(name, filename):
    logger = logging.getLogger(name)
    try:
        os.mkdir("log")
    except:
        pass
    log_path = os.path.join(os.getcwd(),"log")
    log_file = os.path.join(log_path, filename)
    print log_file
    log_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    return logger

logger = init_logger('mylogger', 'log.txt')
logger.info("start...")

def startthread(url):
    logger.debug(url)
    try:
        response = urllib.urlopen(url).read()
        return response
    except:
        traceback.print_exc()
        return None

def select_platform_and_get_apk():
    try:
        pass
        ssdb_wait = SSDB(ssdb_host, ssdb_wait_port)
        ssdb_save = SSDB(ssdb_host, ssdb_save_port)
        logger.info("connect ssdb sucess !!!")
    except Exception , e:
        pass
        print e
        sys.exit(0)
    while 1:
        try:
            #获取ssdb中有哪些set
            ssdb_set_names = ssdb_wait.request("zlist",["","",-1]).data
            logger.debug("wait crawl list:%s"%(str(ssdb_set_names)))

            #按规则提取需要爬取的set
            #逻辑：
            #判断需要爬取的平台（android，ios），随机抽取
            #抽取目标平台的set集合
            #List名称格式:"平台-n",则取名字最大的set
            choice_keys = set()
            for ssdb_set_name in ssdb_set_names:
                for platform in crawl_db:
                    #假设xxplatform为android，则提取set名字包含android的set
                    if ssdb_set_name.startswith(platform):
                        choice_keys.add(platform)
                        break

            #如果数据库中并无等待爬取队列，则休眠5minute
            if len(choice_keys) == 0:
                logger.debug("set is empty:wait")
                time.sleep(WAIT_TIME)

            #随机抽取平台，并获取该平台待爬取的set列表，取名字字符串最大的
            platform = random.choice(list(choice_keys))
            select_ssdb_set_names = [ssdb_set_name for ssdb_set_name in ssdb_set_names if ssdb_set_name.startswith(platform)]

            logger.debug("choice,platform:%s,simkey:%s"%(platform,select_ssdb_set_names))
            if select_ssdb_set_names:
                target_ssdb_set_name = max(select_ssdb_set_names)
                logger.debug("%s:select_ssdb_set_names:%s,target_ssdb_set_name:%s"%(platform,str(select_ssdb_set_names),target_ssdb_set_name))
                lineT = ssdb_wait.request("zpop_front",[target_ssdb_set_name,1]).data.get("items",{})
                lineT_apks = lineT.keys()
                if len(lineT_apks) == 0:
                    time.sleep(WAIT_TIME)
                    continue
                crawed_key = "crawed-"+platform
                for apk_t in lineT_apks:
                    apk = apk_t.strip()
                    if not(apk.replace(".","").isalnum()):continue
                    if len(apk.split(".")[-1]) > 20:continue
                    info_ismember = ssdb_save.request('hexists', [platform, apk.lower()])
                    #crawed_ismember =  ssdb_wait.request('zexists', [crawed_key, apk.lower()])
                    logger.debug("\t".join([platform,apk,"have_info:%s,%s"%(info_ismember,info_ismember.data),]))
                    if info_ismember.data == 0:
                        logger.info("\t".join([str(m) for m in [apk,platform,target_ssdb_set_name,info_ismember.data]]))
                        url = "https://dm.umlife.com/api/appinfo/v1/getInfo?os=%s&pkg=%s"%(platform,apk)
                        #url = "http://127.0.0.1:8157/api/appinfo/v1/getInfo?os=%s&pkg=%s"%(platform,apk)
                        startthread(url)
                        #ssdb_wait.request("zset",[crawed_key,apk.lower(),1])
                        time.sleep(random.randint(0,10)*1.0/30)
            else:
                continue
        except Exception as e:
            logger.error(str(e), exc_info=True)


"""
select_platform_and_get_apk()
"""
pool = multiprocessing.Pool(crawl_thread_num)
for x_thread_num in range(crawl_thread_num):
    pool.apply_async(select_platform_and_get_apk,())
    #pool.apply_async(select_platform_and_get_apk,())

pool.close()
pool.join()

logger.info("all done")
#os._exit()

