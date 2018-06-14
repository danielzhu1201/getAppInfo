#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2017-03-08 17:48:52

import sys
sys.path.append("./")
from config.config import *
import os
import json
import multiprocessing
import time
import random
import traceback
import urllib
import logging
import datetime
from SSDB import SSDB
import ssl


WAIT_TIME = 2#数据库没有数据之后的间隔访问时间

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
    logger.setLevel(logger_level)
    return logger

logger = init_logger('test', 'log.txt')
logger.info("start...")

def startthread(url):
    logger.debug(url)
    try:
        #what if we bypass ssl verification?
        cont = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        response = urllib.urlopen(url,context=cont).read()
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
            #获取ssdb中有哪些list
            ssdb_list_names = ssdb_wait.request("qlist",["","",-1]).data
            logger.debug("wait crawl list:%s"%(str(ssdb_list_names)))
            
            #print ("ssdb_list_names = wait crawl list:%s"%(str(ssdb_list_names)))
            if ssdb_list_names == None:
                time.sleep(WAIT_TIME)
                continue

            #按规则提取需要爬取的list
            #逻辑：
            #判断需要爬取的平台（android，ios），随机抽取
            #抽取目标平台的list
            #List名称格式:"平台-n",则取名字最大的list
            choice_keys = set()
            for ssdb_list_name in ssdb_list_names:
                #print ("ssdb_list_name = %s"%(str(ssdb_list_name)))
                for platform in crawl_db:
                    #print ("platform = %s"%(str(platform)))
                    #假设platform为android，则提取loggerloggerlist名字包含android的list
                    if ssdb_list_name.startswith(platform):
                        choice_keys.add(platform)
                        break
            #print ("chioce keys = %s"%(str(choice_keys)))
            #如果数据库中并无等待爬取队列，则休眠5minute
            if len(choice_keys) == 0:
                logger.info("ssdb wait list is empty:wait")
                time.sleep(WAIT_TIME)
                continue

            #随机抽取平台，并获取该平台待爬取的set列表，取名字字符串最大的
            platform = random.choice(list(choice_keys))
            select_ssdb_list_names = [ssdb_list_name for ssdb_list_name in ssdb_list_names if ssdb_list_name.startswith(platform)]
            #print ("select_ssdb_list_names = %s"%(str(select_ssdb_list_names)))
            logger.debug("choice,platform:%s,simkey:%s"%(platform,select_ssdb_list_names))
            if select_ssdb_list_names:
                target_ssdb_list_name = max(select_ssdb_list_names)
                #print '********    获取ssdb_list_name中    ********'
                #print select_ssdb_list_names
                #print target_ssdb_list_name
                #输出获取apk的来源信息，平台，keys，key
                logger.debug("platform:%s,list_names:%s,list_name:%s"%(platform,str(select_ssdb_list_names),target_ssdb_list_name))
                #取出队列
                apk_t = ssdb_wait.request("qpop_front",[target_ssdb_list_name,1]).data #pop an app's info from our database
                logger.debug("qpop_front list:%s,data:%s"%(target_ssdb_list_name,apk_t))
                ##testing
                #print '****** printing 被取出的队列 apk_t *******'
                #print apk_t
                if apk_t:
                    apk = apk_t.strip()
                    print '****** printing apk *******'
                    print apk
                    if not(apk.replace(".","").isalnum()):continue #check if they are all alph or num
                    if len(apk.split(".")[-1]) > 20:continue
                    info_ismember = ssdb_save.request('hexists', [platform, apk.lower()]) #check if apk.lower() is in HashTable whose name = platform 
                    #print "**** platform vs target_ssdb_list_name ****"
                    #print platform
                    #print target_ssdb_list_name
                    #print apk.lower()
                    print info_ismember.data
                    logger.debug(",".join(["platform:%s, apk:%s"%(platform,apk),"ssdb_have_info:%s,%s"%(info_ismember,info_ismember.data),]))
                    if info_ismember.data == 0:
                        logger.debug("\t".join([str(m) for m in [apk,platform,target_ssdb_list_name,info_ismember.data]]))
                        url = "https://dm.umlife.com/api/appinfo/v1/getInfo?os=%s&pkg=%s"%(platform,apk)
                        #url = "http://127.0.0.1:8157/api/appinfo/v1/getInfo?os=%s&pkg=%s"%(platform,apk)
                        startthread(url) #这里没有问题 可以正常access
                        time.sleep(random.randint(0,10)*1.0/30)
            else:
                continue
        except Exception as e:
            logger.error(str(e), exc_info=True)
    try:
        ssdb_wait.close()
    except:
        pass
    try:
        ssdb_save.close()
    except:
        pass



select_platform_and_get_apk()



pool = multiprocessing.Pool(crawl_thread_num)
for x_thread_num in range(crawl_thread_num):
    pool.apply_async(select_platform_and_get_apk,())
    #pool.apply_async(select_platform_and_get_apk,())

pool.close()
pool.join()

logger.info("all done")
#os._exit()

