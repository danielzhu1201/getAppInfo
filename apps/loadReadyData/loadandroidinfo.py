#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2017-03-08 17:23:06

import json
import redis
import sys

redis_db = {"android":1,"ios":2}
os = "android"
red = redis.Redis(db=redis_db.get(os))
keyword = {"android":"pkgName","ios":"bundleId"}

with open(sys.argv[1]) as fr:
    lines = fr.readlines()
    for line in lines:
        try:
            jline = json.loads(line.strip())
        except:
            print line
            continue
        if jline:
            infodict = {}
            for xk,xv in jline.iteritems():
                infodict[xk] = xv
            red.set(infodict[keyword[os]].strip().lower(),json.dumps(infodict))
