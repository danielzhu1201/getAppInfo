#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2017-02

import sys
sys.path.insert(0,'../..') #ensure that config is always in parent folder!!
from config import *
import urllib
import os
import datetime
import json
import logging
import multiprocessing
from SSDB import SSDB

appinfo_life_days = 30
save_retry_times = 2

log_path = os.getcwd()
def init_logger(name, filename):
    logger = logging.getLogger(name)
    log_file = os.path.join(log_path, filename)
    log_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    log_formatter = logging.Formatter(
        '%(asctime)s,[%(levelname)s],%(filename)s,%(funcName)s,%(lineno)s,%(name)s: %(message)s')
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    return logger

logger = init_logger('update apk info', 'log.txt')



nowtime = datetime.datetime.now()


def process_deal(platform):
    #SSDB 链接
    try:
        ssdb_save = [SSDB(ssdb_host, ssdb_save_port),ssdb_save_port]
    except Exception , e:
        logger.error(str(e), exc_info=True)
        sys.exit(0)

    logger.info("try scan hashmap:%s"%(platform))
    start = ""

    #循环便利各平台所有的key（apk）
    while 1:
        try:
            all_keys = ssdb_save[0].request("hkeys",[platform,start,"",2]).data
            logger.debug("query hashmap:%s,start:%s,keys:%s"%(platform,start,str(all_keys[:10])))
        except Exception as e:
            logger.error(str(e), exc_info=True)
            break

        if not(all_keys):
            break

        start = all_keys[-1]

        #遍历获取的所有key值
        for app in all_keys:

            appinfo = None

            try:
                appinfo_string = ssdb_save[0].request("hget",[platform,app]).data
                logger.debug("get,platform:%s,app:%s,data:%s"%(platform,app,appinfo_string))
                appinfo = json.loads(appinfo_string)
            except Exception as e:
                print appinfo_string
                logger.error(str(e), exc_info=True)
                continue

            #提取原始包名，数据库中的key是小写
            apk = appinfo.get(info_apk_key.get(platform,"error"),None)

            #获取不到app原始的包名时忽略更新操作并写入log
            if not(apk):
                logger.info("platform:%s,app:%s,error:get apk error"%(platform,apk))
                continue
            else:
                pass

            #判断数据更新时间是否超时
            crawl_time = datetime.datetime.strptime(appinfo.get(crawl_time_keyword,"2017-03-01 00:00:00"),"%Y-%m-%d %H:%M:%S")
            logger.debug("keyword:%s,app:%s,time:%s"%(crawl_time_keyword,apk,crawl_time))

            if [nowtime-crawl_time][0].days > appinfo_life_days:
                update_code = 0
                
                #先删除数据库中的记录（appinfo有记录），直接请求数据，不存在该记录会触发爬取流程
                try:
                    ssdb_save[0].request("hdel",[platform,app])
                    url = "https://dm.umlife.com/api/appinfo/v1/getInfo?os=%s&pkg=%s"%(platform,apk)
                    #url = "http://localhost:8157/api/appinfo/v1/getInfo?os=%s&pkg=%s"%(platform,apk)
                    logger.debug("update,app:%s,requests url:%s"%(apk,url))
                    jresponse = json.loads(urllib.urlopen(url).read())              
                    logger.debug("update,app:%s,requests response appStatus:%s"%(apk,jresponse.get(u"results",{}).get(apk,{}).get(u"appStatus",None)))
                    if jresponse.get(u"results",{}).get(apk,{}).get(u"appStatus",None) == 0:
                        logger.info("update,app:%s,update sucess"%(apk))
                        update_code = 1
                        pass
                except Exception as e:
                    logger.error(str(e), exc_info=True)
                finally:
                    if update_code == 0:

                        #失败则重复n次保存，若最后也失败，直接记录数据至log中
                        n = 0
                        while n < save_retry_times:
                            n += 1
                            logger.debug("update,app:%s: resave times n:%s"%(apk,n))
                            try:
                                resave_info = ssdb_save[0].request("hset",[platform,app,appinfo_string])
                                logger.debug("update,app:%s,fail and resave:%s"%(apk,resave_info))
                                break
                            except Exception as e:
                                logger.error(str(e), exc_info=True)
                        if n >= save_retry_times:
                            logger.info("update,app:%s,resave fail ... %s"%(apk,appinfo_string))
            else:
                logger.debug("platform:%s,app:%s,do not need update"%(platform,app))
            break
        break
    try:
        ssdb_save[0].close()
    except Exception as e:
        logger.error(str(e), exc_info=True)

pool = multiprocessing.Pool(multiprocessing.cpu_count())

try:
    ssdb_save = [SSDB(ssdb_host, ssdb_save_port),ssdb_save_port]
except Exception , e:
    logger.error(str(e), exc_info=True)
    sys.exit(0)

for platform in ssdb_save[0].request("hlist",["","",-1]).data:
    pool.apply_async(process_deal,(platform,))
#pool.map(process_deal,ssdb_save[0].request("hlist",["","",-1]).data)

try:
    ssdb_save[0].close()
except Exception as e:
    logger.error(str(e), exc_info=True)

pool.close()
pool.join()
