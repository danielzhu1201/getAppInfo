import sys
sys.path.append("./")
from config.config import *

import logging
logger = logging.getLogger("census")

import traceback
import json
import datetime
nowtime = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d") + " 00:00:00","%Y-%m-%d %H:%M:%S")
print nowtime
from SSDB import SSDB
try:
    pass
    ssdb_wait = [SSDB(ssdb_host, ssdb_wait_port),ssdb_wait_port]
    ssdb_save = [SSDB(ssdb_host, ssdb_save_port),ssdb_save_port]
except Exception , e:
    pass
    print e
    sys.exit(0)

for ssdb_bind in [ssdb_wait,ssdb_save]:
    list_keys = ssdb_bind[0].request("qlist",["","",-1]).data 
    for list_key in list_keys:
        list_key_size = ssdb_bind[0].request("qsize",[list_key]).data
        logger.info("port:%s,list_key:%s,size:%s"%(ssdb_bind[1],list_key,str(list_key_size)))
    set_keys = ssdb_bind[0].request("zlist",["","",100]).data
    for set_key in set_keys:
        set_key_size = ssdb_bind[0].request("zsize",[set_key]).data
        logger.info("port:%s,set_key:%s,size:%s"%(ssdb_bind[1],set_key,str(set_key_size)))
    hashmap_keys = ssdb_bind[0].request("hlist",["","",100]).data
    for hashmap_key in hashmap_keys:
        hashmap_key_size = ssdb_bind[0].request("hsize",[hashmap_key]).data
        logger.info("port:%s,hashmap_key:%s,size:%s"%(ssdb_bind[1],hashmap_key,str(hashmap_key_size)))
        #yesterday update
        countYesterday = todaycount = 0
        display_count = 0
        display_max = 10
        start = ""
        while 1:
            #break
            all_keys = ssdb_bind[0].request("hkeys",[hashmap_key,start,"",1000]).data
            if not(all_keys):
                break
            start = all_keys[-1]
            for app in all_keys:
                data = ssdb_bind[0].request("hget",[hashmap_key,app]).data
                apkinfo = json.loads(data)
                crawl_time = \
                    datetime.datetime.strptime(apkinfo.get(crawl_time_keyword,"2017-03-01 00:00:00"),"%Y-%m-%d %H:%M:%S")
                update_time = \
                    datetime.datetime.strptime(\
                        apkinfo.get(update_time_keyword,datetime.datetime.now().strftime("%Y-%m-%d"))\
                            ,"%Y-%m-%d")
                if update_time.year < 1971:
                    #print "del",app,apkinfo
                    #ssdb_bind[0].request("hdel",[hashmap_key,app])
                    pass
                if crawl_time > nowtime:
                    todaycount += 1
                if [nowtime-crawl_time][0].days == 0:
                    countYesterday += 1
                #if display_count < display_max:
                #    print app,crawl_time
                #    display_count += 1
        print "yesterday crawl update",countYesterday
        print "today crawl update",todaycount
try:
    ssdb_wait.close()
except:
    pass
try:
    ssdb_save.close()
except:
    pass
