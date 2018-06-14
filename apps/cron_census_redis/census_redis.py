
import redis
from getAppInfo.config import *
import traceback
import json
import datetime
nowtime = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d") + " 00:00:00","%Y-%m-%d %H:%M:%S")
for platform,db_num in redis_db.iteritems():
    try:
        red = redis.Redis(host=redis_host,port = redis_port,db = db_num)
        dbsizeinfo = red.dbsize()
        print "db:%s,int_db:%s,db_key:%s"%(platform,db_num,dbsizeinfo)
        
    except:
        traceback.print_exc() 
        continue
    pool=redis.ConnectionPool(db=redis_db[platform])
    r = redis.StrictRedis(connection_pool=pool)
    keys = r.keys()
    if platform in ["crawl_apk"]:
        for key in keys:
            print "waitting_crawl_count",platform,key,r.scard(key)
    elif platform in ["ios","android"]:
        countYesterday = 0
        todaycount = 0
        for apk in keys:
            apkinfo = json.loads(r.get(apk))
            apkinfo.get(crawl_time_keyword,"2017-03-01 00:00:00")
            crawl_time = datetime.datetime.strptime(apkinfo.get(crawl_time_keyword,"2017-03-01 00:00:00"),"%Y-%m-%d %H:%M:%S")
            if crawl_time > nowtime:
                todaycount += 1
            if [nowtime-crawl_time][0].days == 0:
                countYesterday += 1
        print "yesterday crawl update",countYesterday
        print "today crawl update",todaycount
                 
