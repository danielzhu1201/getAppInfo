#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2017-02-23 16:37:14

#logger_level
import logging
logger_level = logging.DEBUG

#redis的链接信息
redis_host = "127.0.0.1"
redis_port = 6379
#ssdb 的链接信息
ssdb_host = "172.16.1.111"
ssdb_save_port = 8800
ssdb_wait_port = 8801

#获取数据的进程
crawl_thread_num = 5

#爬取数据时每个请求的休眠时间
delay_time = 0.5

#v1版本获取appinfo的配置
crawl_threshold = 50000
 
#数据库中保存数据获取时间的字段
crawl_time_keyword = "crawl_time"
update_time_keyword = "publishDate"
#apkinfo的有效时长,达到最大时长旧重新获取信息
apkinfo_life_days = 30

# 请求代码解释
statusToMessage = {200:"请求成功",
                    101:"参数解析错误",
                    102:"pkg元素个数超出指定范围（最多支持50个）",
                    105:"请求频率过高",}

#各平台app信息储存的数据库id
redis_db = {"android":1,"ios":2,"crawl_apk":3,"crawled":4}

#各平台app信息储存的格式
redis_db_type = {"android":"string","ios":"string","crawl_apk":"set"}

#需要定时更新的平台
crawl_db = ["android","ios"]

#各平台储存apk名的字段
info_apk_key = {"android":"pkgName","ios":"bundleId"}

#平台信息
platform = set(redis_db.keys())

#显示的字段，key为平台名，value是显示的字段，若无设置，默认全部显示（爬取时间除外）
platfrom_display = {
                    "android-se":set(["appStatus","trackViewUrl","trackName","genres","sellerName","version","fileSize","iconUrl","downloadUrl","description","pkgName","releaseDate","price","averageUserRating","userRatingCount","downloadCount","screenShots"]),
                    "android-useless":set(["appStatus","trackViewUrl"]),
                    }
