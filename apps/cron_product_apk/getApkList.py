#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2017-03-09 10:32:23



from pyspark import SparkContext
from string import punctuation
from collections import OrderedDict
from operator import add
from collections import Counter
import json
import time
import datetime
import sys
sys.path.append("./")
from config.config import *
import os
import calendar
import traceback

os.environ["TZ"] = "Asia/Shanghai"
time.tzset()

enviroment = "hdfs:///"
newSdkPath = "logarchive.ym/dmptrack/aat=100/dt=%s/"
last5Path = "logarchive.ym/hive/gztables/default_log/dt=%s/sv=3/ac=304"

mode = sys.argv[3] if len(sys.argv) > 3 else "day"

assert(mode in ["day", "week", 'month'])
try:
    Today = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d")
except:
    Today = datetime.date.today()

def generate_dates(begin_date, end_date):
    dates = []
    dt = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    date = begin_date[:]
    while date <= end_date:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y-%m-%d")
    return dates
today_date = datetime.datetime.strftime(Today, "%Y-%m-%d")
week_end = datetime.datetime.strftime(Today + datetime.timedelta(6), "%Y-%m-%d")
next_week = ",".join(generate_dates(today_date,week_end))
month = datetime.datetime.strftime(Today.replace(day=1), "%Y-%m")


if mode == "day":
    input_sdk_data_old = enviroment + last5Path%(today_date)
    input_sdk_data_new = enviroment + newSdkPath%(today_date)
elif mode == "week":
    input_sdk_data_old = enviroment +last5Path%("{%s}"%next_week)
    input_sdk_data_new = enviroment +newSdkPath%("{%s}"%next_week)
elif mode == "month":
    input_sdk_data_old = enviroment + last5Path%("%s*"%month)
    input_sdk_data_new = enviroment + newSdkPath%("%s*"%month)
else:
    print "error: mode must be one of daily, weekly and monthly!"
    exit()

print input_sdk_data_old
print input_sdk_data_new


def IMEI(imei):
    """
    IMEI format: 15 digits, e.g., 123456789012345
    UMID format: 15 digits, e.g., 123456789012345
    """
    try:
        new_imei = str(imei).lower()
        if new_imei.isalnum() and len(new_imei) > 13 and len(new_imei) < 16:
            return new_imei
        else:
            return ""
    except:
        return ""

def IDFA(idfa):
    """
    IDFA format: 36 characters, contains (uppercase) letters or digits. 4 segments
    linked by '-': '-'.join([8,4,4,4,12]), e.g., 1E2DFA89-496A-47FD-9941-DF1FC4E6484A
    UMID format: 32 lowercase characters, e.g., 1e2dfa89496a47fd9941df1fc4e6484a
    """
    try:
        new_idfa = str(idfa).translate(None, punctuation).lower()
        if len(new_idfa) == 32 and new_idfa.isalnum():
            return new_idfa
        else:
            return ""
    except:
        return ""

def MAC(mac):
    """
    MAC format: 17 uppercase characters, 6 segments linked by ':', e.g.,
    3C:CB:4B:59:1C:18
    UMID format: 12 lowercase characters, e.g., 3ccb4b591c18
    """
    try:
        new_mac = str(mac).translate(None, punctuation).lower()
        if new_mac.isalnum() and len(new_mac) == 12:
            if new_mac != "0"*12:
                return new_mac
            else:
                return ""
        else:
            return ""
    except:
        return ""
def getFields_old(line):
    """
    获取相关字段
    """
    returnList = []
    try:
        """
        idsinfolist = line.split("\t")
        if len(idsinfolist) == 2:
            uidT,infos = idsinfolist
            for xinfo in infos.split("&"):
                xinfolist = xinfo.split("^")
                if len(xinfolist) == 7:
                    platform,date,apks,prv,city,carrier,imsi = xinfolist
                    if platform.strip().lower() == "imei":
                        for xapk in apks.split("|"):
                            returnList.append((0,xapk))
                    elif platform.strip().lower() == "idfa":
                        for xapk in apks.split("|"):
                            returnList.append((1,xapk))
        """
        try:
            d = dict((item.split('=', 1) for item in line.strip('\r\n').split('&')))
        except Exception as e:
            raise e
        #device id
        idfa = IDFA(d.get('ifa', ''))
        #imei = IMEI(d.get('ei', ''))
        #mac = MAC(d.get('mac', ''))
        fields = ['pns',]#
        words = tuple([d.get(w, '') for w in fields])
        for word in words:
            for xapk in word.split("|"):
                if xapk:
                    returnList.append((1 if idfa else 0,xapk))
    except:
        traceback.print_exc()
    finally:
        return returnList

def getFields_new(line):
    """
    获取相关字段
    """
    returnList = []
    try:
        """
        jline = json.loads(line)
        imeiT = jline.get("imei",None)
        if imeiT == None:return None
        imei = IMEI(imeiT)
        if not(imei):return None
        apks = jline.get("recentlyapps",[])
        for apk in apks:
            apkname = apk.get("pn",False)
            if apkname:
                returnList.append((0,apkname))
        """
        jline = json.loads(line)
        ver = jline.get("ver",1)
        keyword = {
            1:{
                "install_app":"installapps_third",
                },
            2:{
                "install_app":"d",
                }
        }
        install_keyword = keyword.get(ver,{}).get("install_app",False)
        if install_keyword != False:
            third_install = jline.get(install_keyword,[])
            for x_third_install in third_install.keys():
                returnList.append((0,x_third_install))
    except:
        traceback.print_exc()
    finally:
        return returnList

def main(sc,date,output_path):
    global dayNum
    global output_sdkStatistic

    apks_oldsdk = sc.textFile(input_sdk_data_old).flatMap(getFields_old)
    apks_newsdk = sc.textFile(input_sdk_data_new).flatMap(getFields_new)

    apks_union = apks_oldsdk.union(apks_newsdk)
    
    print apks_union.first()
    print apks_oldsdk.first()
    print apks_newsdk.first()

    apks_android = apks_union.filter(lambda line:line[0] == 0).map(lambda line:line[1]).distinct().map(lambda line:"\t".join(["android",line]))
    apks_ios = apks_oldsdk.filter(lambda line:line[0] == 1).map(lambda line:line[1]).distinct().map(lambda line:"\t".join(["ios",line]))
    
    apks_android.union(apks_ios).coalesce(1).saveAsTextFile(output_path)


if __name__ == '__main__':
    sc = SparkContext()
    date = sys.argv[1]
    output_path = sys.argv[2]

    main(sc,date,output_path)
