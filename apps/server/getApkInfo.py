#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2017-02-27 11:29:40
import sys
sys.path.append("./")
import logging
import traceback
import time
import json
import multiprocessing
import types
import copy_reg
import lib
import os
from config.config import *
log_path = '/home/ymserver/dmvhost/getAppInfo/log'

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


def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)
copy_reg.pickle(types.MethodType, _pickle_method)

#logging.basicConfig(level=logging.INFO,format='%(message)s')

class GetApkInfo():
    def __init__(self):
        self.os = None
        self.saveDict = None

    def getApkInfoSingle(self,apkname):
        try:
            logging.debug("use sigle thread for %s"%(str(apkname)))
            exec("from lib.%s import %s as analysisFunction"%(self.os, self.os))
            #print type(eval("analysisFunction")())
            #function = vars().get("analysisFunction",None) 
            function = analysisFunction
            logging.debug("function name:%s, type:%s"%(self.os,str(type(function))))
            if isinstance(function,(types.TypeType, types.ClassType)):
                return function().get(apkname)
            elif callable(function) or function is types.FunctionType:
                return function(apkname)
            else:
                #print type(function)
                logging.warning("can not found function or class object")
                return {}
        except Exception as e:
            logger.error(str(e), exc_info=True)
            #logging.INFO(traceback.format_exc())
    def getApkInfoMulti_connect(self,apkname):
        try:
            self.saveDict[apkname] = self.getApkInfoSingle(apkname)
        except Exception as e:
            logger.error(str(e), exc_info=True)
            #logging.INFO(traceback.format_exc())

    def getApkInfoMulti(self,apks):
        try:
            logging.debug("use multiprocessing for %s"%(str(apks)))
            self.saveDict = multiprocessing.Manager().dict()
            pool = multiprocessing.Pool(crawl_thread_num)
            #pool.map(self.getApkInfoMulti_connect,apks)
            for apk in apks:
                pool.apply_async(self.getApkInfoMulti_connect,(apk,))
            pool.close()
            pool.join()
            returnDict = {}
            for k in self.saveDict.keys():
                returnDict[k] = self.saveDict.get(k,{})
            return returnDict
        except Exception,e:
            logger.error(str(e), exc_info=True)
            #logging.error("multiprocessing error",e)
            return {}

    def getApkInfo(self,apks,os):
        self.os = os
        exec("from lib.%s import %s as analysisFunction"%(self.os, self.os))
        #print type(eval("analysisFunction")())
        #logging.info("os:%s,apks:%s"%(os,str(apks)))
        if isinstance(apks,str):
            return {apks:self.getApkInfoSingle(apks)}
        elif isinstance(apks,list) or isinstance(apks,set):
            if len(apks) > 1:
                return self.getApkInfoMulti(apks)
            else:
                apk = list(apks)[0]
                return {apk:self.getApkInfoSingle(apk)}
