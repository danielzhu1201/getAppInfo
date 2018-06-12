#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2017-02-27 14:28:22

import logging
import urllib2
from lxml import etree
import json
import os
log_path = os.path.join(os.getcwd(),"log")

def init_logger(name, filename):
    logger = logging.getLogger(name)
    log_file = os.path.join(log_path, filename)
    log_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    log_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    return logger

logger = init_logger('mylogger', 'log.txt')

"""
try:
    # 业务代码
except Exception as e:
    logger.error(str(e), exc_info=True)
"""

def ios(apkname,timeout = 3):
    
        url = "https://itunes.apple.com/cn/lookup?bundleId=%s"%apkname
        logging.debug(url)
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36)'
        headers = { 'User-Agent' : user_agent ,
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Accept':'application/json, text/javascript, */*; q=0.01',
            }
        req = urllib2.Request(url=url,headers=headers)
        urllibStatus = False
        response = None
        try:
            response = urllib2.urlopen(req,timeout = timeout)
            urllibStatus = True
        except Exception as e:
            logger.error(str(e), exc_info=True)
            #traceback.print_exc()
        if urllibStatus == False:
            return {}

        infodict = {}

        try:
            jline = json.loads(response.read())
            resultCount = jline.get("resultCount",0)
            if resultCount:
                for xk,xv in jline.get("results",[{}])[0].iteritems():
                    if xk in ["trackId","artistId","userRatingCountForCurrentVersion","userRatingCount"]:
                        infodict[xk] = int(xv)
                    else:
                        infodict[xk] = xv
        except Exception as e:
            #print traceback.format_exc()
            #logging.debug(traceback.format_exc())
            logger.error(str(e), exc_info=True)
        finally:
            #print "\n\n\n\n\n",infodict
            return infodict


if __name__ == "__main__":
    print json.dumps(ios("com.ofo.Bicycle"),indent=4,ensure_ascii=False)
