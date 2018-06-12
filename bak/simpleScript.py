#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2017-02-21 09:49:52


    
import urllib2
import json
import logging
import time
logging.basicConfig(level=logging.INFO,format='%(message)s')
##logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
##logger = logging.getLogger('mylogger')
##fh=logging.FileHandler('record')
##fh.setLevel(logging.DEBUG)
##formatter=logging.Formatter('%(message)s')
##fh.setFormatter(formatter)
##logger.addHandler(fh) 
def get_page(req):
	whiletimes=0
	while True:
		try:
			response=urllib2.urlopen(req)
			return response
		except:
			whiletimes=whiletimes+1
			if whiletimes>5:
				return 0
			time.sleep(3)
			continue
for categoryid in (100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,-10,147,121,144,148,149,153,146,151):
	pageContext=0
	while True:
		apporgame=categoryid>119 and 2 or 1
		url='http://android.myapp.com/myapp/cate/appList.htm?orgame=%s&categoryId=%s&pageSize=20&pageContext=%s'%(apporgame,categoryid,pageContext)
##		logging.debug(url)
		user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36)'
		headers = { 'User-Agent' : user_agent ,
		'Accept-Language':'zh-CN,zh;q=0.8',
		'Cookie':'session_uuid=9bf99aaa-6a35-4102-91c8-9579d74fdae1; JSESSIONID=aaakl_mj0IdU1d0xSff9u; pgv_info=ssid=s2762415773; ts_refer=www.baidu.com/link; pgv_pvid=8567518144; ts_uid=5229388540',
		'Host':'android.myapp.com',
		'Referer':'http://android.myapp.com',
		'Accept':'application/json, text/javascript, */*; q=0.01'
		}
		req = urllib2.Request(url=url,headers=headers)
		response=get_page(req)
		if response!=0 and response.code==200:
			data=response.read()
			jdata=json.loads(data)
			if jdata.get('obj'):
				for i in range(0,len(jdata.get('obj'))):
					mycategory=apporgame=1 and 'app' or 'game'
					description=jdata.get('obj')[i]['description']
					flag=jdata.get('obj')[i]['flag']
					fileSize=jdata.get('obj')[i]['fileSize']
					authorId=jdata.get('obj')[i]['authorId']
					categoryId=jdata.get('obj')[i]['categoryId']
					pkgName=jdata.get('obj')[i]['pkgName']
					apkUrl=jdata.get('obj')[i]['apkUrl']
					appName=jdata.get('obj')[i]['appName']
					appId=jdata.get('obj')[i]['appId']
					versionCode=jdata.get('obj')[i]['versionCode']
					iconUrl=jdata.get('obj')[i]['iconUrl']
					versionName=jdata.get('obj')[i]['versionName']
					appDownCount=jdata.get('obj')[i]['appDownCount']
					averageRating=jdata.get('obj')[i]['averageRating']
					editorIntro=jdata.get('obj')[i]['editorIntro']
					categoryName=jdata.get('obj')[i]['categoryName']
					apkMd5=jdata.get('obj')[i]['apkMd5']
					authorName=jdata.get('obj')[i]['authorName']
					apkPublishTime=jdata.get('obj')[i]['apkPublishTime']
					averageRating=str(jdata.get('obj')[i]['appRatingInfo']['averageRating'])
					ratingCount=str(jdata.get('obj')[i]['appRatingInfo']['ratingCount'])

					logging.info(('%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%sq|w%s'%(mycategory,categoryName,description,flag,fileSize,authorId,categoryId,pkgName,apkUrl,appName,appId,versionCode,iconUrl,versionName,appDownCount,averageRating,editorIntro,apkMd5,authorName,apkPublishTime,averageRating,ratingCount)).encode('utf-8'))
			elif response==0 :
				pass
			else:
				break
		time.sleep(0.5)
		pageContext=pageContext+20
		
##run scripts:python yingyongbao.py  1>record 2>&1

