#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2017-03-09 11:45:56

import sys
sys.path.append("./")
from config.config import *
import os
import logging
import datetime


log_path = os.path.join(os.getcwd(),"log")

def init_logger(name, filename):
    logger = logging.getLogger(name)
    date = datetime.datetime.now().strftime("%Y%m%d.")
    log_file = os.path.join(log_path, date+filename)
    log_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    log_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    return logger

logger = init_logger('test', 'log.txt')

"""
try:
    # 业务代码
except Exception as e:
    logger.error(str(e), exc_info=True)
"""

from SSDB import SSDB
try:
        pass
        ssdb_wait = SSDB(ssdb_host, ssdb_wait_port)
        ssdb_save = SSDB(ssdb_host, ssdb_save_port)
except Exception , e:
        pass
        print e
        sys.exit(0)

folderpath = sys.argv[1]
logger.info("folder:%s"%folderpath)
#if os.path.exists(folderpath) == False:os._exit()
if os.path.isfile(folderpath):
    filelist = [folderpath]
else:
    filelist = [os.path.join(folderpath,filename) for filename in os.listdir(folderpath)]
logger.info("filelist:\n%s"%(str(filelist)))
countdict = {}
for filepath in filelist:
    if os.path.isfile(filepath):
        logger.info("read file : %s"%filepath)
        with open(filepath) as fr:
            while 1:
                lineT = fr.readline()
                if lineT == "":break
                line = lineT.strip()
                datas_impurities = line.split("\t")
                if len(datas_impurities) > 1:
                    platform = datas_impurities[0]
                    apk = datas_impurities[1].split(" ")[0]
                    if not(apk.replace(".","").isalnum()):continue
                    if len(apk.split(".")[-1]) > 20:continue
                    info_ismember = ssdb_save.request('hexists', [platform, apk])
                    #crawed_ismember =  ssdb_wait.request('zexists', [platform, apk])
                    logger.debug("\t".join([platform,apk,
                                "have_info:%s,%s"%(info_ismember,info_ismember.data),
                                ]))
                    #if crawed_ismember.data == 0  and info_ismember.data == 0:
                    if info_ismember.data == 0:
                        logger.debug("save:%s,%s"%(platform,apk))
                        status = ssdb_wait.request("qpush_back",[platform + "-1",apk])
                        logger.debug("save info:%s"%str(status))
                        countdict.setdefault(platform,0)
                        countdict[platform] += 1
try:
    ssdb_wait.close()
except Exception as e:
    logger.error(str(e), exc_info=True)
try:
    ssdb_save.close()
except Exception as e:
    logger.error(str(e), exc_info=True)

logger.info("load to ssdb all done !")
logger.info(str(countdict))
