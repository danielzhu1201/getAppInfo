#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2017-02-21 09:59:02
import urllib2
from lxml import etree
import logging
import traceback
import datetime
import re
import os
import time
import json
import multiprocessing
import types
import copy_reg
retry_times = 5

#logging.basicConfig(level=logging.INFO,format='%(message)s')
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


class android():

    def getWeb(self,url,timeout = 3):
        logging.debug(url)
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36)'
        headers = { 'User-Agent' : user_agent ,
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Accept':'application/json, text/javascript, */*; q=0.01',
        "Refer":"http://sj.qq.com/",
        "Host":"android.myapp.com"
        }
        req = urllib2.Request(url=url,headers=headers)
        try:
            return 0,urllib2.urlopen(req,timeout = timeout)
        except Exception as e:
            logging.warning(traceback.format_exc())
            #logging.warning("android crawl error",e)
            return 1,"error"
    
    def formatUrl(self,apkname):
        return "http://android.myapp.com/myapp/detail.htm?apkName=%s"%apkname
    
    
    def analysisHtml(self,response):
        infodict = {}
    
        try:
            lweb = etree.HTML(response.read())
            infodict["trackViewUrl"] = response.url
            packageName = re.findall("(?i)apkName=([^?&]*)",response.url)
            if packageName:infodict["pkgName"] = packageName[0]
        
            appName = lweb.xpath("//div[@class='det-name']/div[@class='det-name-int']/text()")
            if appName:infodict["trackName"] = appName[0]
        
            appType = lweb.xpath("//a[@id='J_DetCate']/text()")
            if appType:infodict["geners"] = appType
        
            companyAndVersion = "\t".join(lweb.xpath("//div[@data-modname='appOthInfo']/div/text()"))
            company = re.findall(u"开发商.\s*(.*)",companyAndVersion)
            if len(company):infodict["sellerName"] = company[0].strip()
            version = re.findall(u"版本号.\t*(\S*)",companyAndVersion)
            if len(version):infodict["version"] = version[0].strip()
        
            downloadTime = lweb.xpath("//div[@class='det-insnum-line']/div[@class='det-ins-num']/text()")
            if downloadTime:infodict["downloadCount"] = downloadTime[0].replace(u"下载","")
        
            filesize = lweb.xpath("//div[@class='det-size']/text()")
            if len(filesize):infodict["fileSize"] = filesize[0]
        
            iconUrl = lweb.xpath("//div[@class='det-icon']/img/@src")
            if len(iconUrl):infodict["iconUrl"] = iconUrl[0]
        
            downloadUrl = lweb.xpath("//a[@class='det-down-btn']/@data-apkurl")
            if len(downloadUrl):infodict["downloadUrl"] = downloadUrl[0]
        
            description =  lweb.xpath("//div[@id='J_DetAppDataInfo']/div[@class='det-app-data-info']/text()")
            if len(description):infodict["description"] = description[0]
        
            publishDate = lweb.xpath("//div[@id='J_ApkPublishTime']")
            if len(publishDate):infodict["publishDate"] = time.strftime("%Y-%m-%d",time.localtime(int(publishDate[0].get("data-apkpublishtime",0))))
        
            screenShot = lweb.xpath("//span[@id='J_PicTurnImgBox']//img/@data-src")
            if len(screenShot):infodict["screenShots"] = screenShot
        
            appRate = lweb.xpath("//div[@class='com-blue-star-num']/text()")
            if len(appRate):infodict["averageUserRating"] = appRate[0]

            try:
                appNameForComment = infodict.get("pkgName",None)
                if appNameForComment:
                    n = 0
                    while 1:
                        n += 1
                        webForComment = self.getWeb("http://android.myapp.com/myapp/app/comment.htm?apkName=%s"%(appNameForComment))
                        if webForComment[0] == 0: 
                            jline = json.loads(webForComment[1].read())
                            obj = jline.get("obj",{})
                            if obj:
                                infodict["userRatingCount"] = int(obj.get("total",0))
                                break
                        if n > retry_times:
                            break
            except  Exception as e:
                logging.warning(traceback.format_exc())
                #logging.info(traceback.format_exc())
        except  Exception as e:
            logging.warning(traceback.format_exc())
            #logging.debug(traceback.format_exc())
        finally:
            if infodict.has_key("publishDate"):
                try:
                    if datetime.datetime.strptime(infodict["publishDate"],"%Y-%m-%d").year < 2000:
                       infodict = {}
                except:
                    traceback.print_exc()
            return infodict
    
    def get(self,apkname):
        url = self.formatUrl(apkname)
        logging.debug("\t".join([apkname,url]))
        if url == False:return None
        web = self.getWeb(url)
        if web[0] == 0:
            return self.analysisHtml(web[1])
        else:
            return None

if __name__ == "__main__":
    #print android().get("com.eg.android.AlipayGphone") 
    print json.dumps(android().get("com.immomo.momo"),indent=4,ensure_ascii=False) 
