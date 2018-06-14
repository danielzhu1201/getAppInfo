import sys
sys.path.append("./")
from config.config import *
import traceback
import json
import datetime
nowtime = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d") + " 00:00:00","%Y-%m-%d %H:%M:%S")

from SSDB import SSDB
try:
    pass
    ssdb_save = [SSDB(ssdb_host, ssdb_save_port),ssdb_save_port]
except Exception , e:
    pass
    print e
    sys.exit(0)
hashmap_name = "android"
sep_m = "\t"
start = ""
keyword_list = [u"pkgName",u"trackName",u"sellerName",u"geners",u"iconUrl"]
while 1:
    all_keys = ssdb_save[0].request("hkeys",[hashmap_name,start,"",1000]).data
    if not(all_keys):
        break
    start = all_keys[-1]
    for app in all_keys:
        data = ssdb_save[0].request("hget",[hashmap_name,app]).data
        apkinfo = json.loads(data)
        templist = []
        templist02 = []
        for keyword in keyword_list:
            templist.append(apkinfo.get(keyword,""))
        for index in xrange(len(templist)):
            if keyword_list[index] == "geners":
                if len(templist[index]) > 1:
                    templist02 += templist[index][:2]
                elif len(templist[index]) == 1:
                    templist02.append(templist[index][0])
                    templist02.append("")
                else:
                    templist02.append("")
                    templist02.append("")
            else:
                if isinstance(templist[index],list):
                    templist02.append("&".join(templist[index]))
                if isinstance(templist[index],unicode):
                    templist02.append(templist[index])
                else:
                    templist02.append(templist[index].decode("utf8"))

            templist02[index] = templist02[index].replace("\n",r"\n").replace("\r",r"\r").replace("\t",r"\t")
        #print templist        
        print sep_m.join(templist02).encode("utf8")
