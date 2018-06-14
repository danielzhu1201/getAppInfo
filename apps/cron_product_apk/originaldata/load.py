#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2017-03-09 11:45:56

import redis
import os
import sys
sys.path.insert(0,'../..') #ensure that config is always in parent folder!!
from config import *
connect_db = redis_db["crawl_apk"]
red = redis.Redis(db=connect_db)
import sys
filepath = sys.argv[1]
platform = sys.argv[2]
raw_input("please comfirm info: redis_num:%s,platform:%s,file:%s"%(connect_db,platform,filepath))
if os.path.isfile(filepath):
    with open(filepath) as fr:
        while 1:
            lineT = fr.readline()
            if lineT == "":break
            line = lineT.strip()
            red.sadd(platform,line)

