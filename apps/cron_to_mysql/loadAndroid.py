import sys
sys.path.insert(0,'../..') #ensure that config is always in parent folder!!
from config import *
import redis
import traceback
import json
import datetime
from sqlalchemy import Table, Text, Column, String, Integer, Date, MetaData, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

mysqlConnectUri = "mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8"%("yminfo","yminfosecret","localhost","3306","yminfo")
print mysqlConnectUri
engine = create_engine(mysqlConnectUri,max_overflow=5)
print engine.execute("show tables;").fetchall()
DBSession = sessionmaker(bind=engine)
session = DBSession()
Base = declarative_base()
"""
metadata = MetaData(bind=engine)
android = Table("android_app",metadata,
    Column("trackViewUrl",String(256)),
    Column("trackName",Text()),
    Column("pkgName",String(128), primary_key=True),
    Column("geners",String(256)),
    Column("sellerName",String(512)),
    Column("version",String(128)),
    Column("downloadCount",String(128)),
    Column("fileSize",String(128)),
    Column("iconUrl",String(128)),
    Column("downloadUrl",String(128)),
    Column("description",Text()),
    Column("publishDate",String(128)),
    Column("screenShots",Text()),
    Column("averageUserRating",String(128)),
    Column("userRatingCount",Integer()),
    Column("crawl_time",String(32)),
    )
metadata.create_all()
"""
"""
"""


class android_app(Base):
    __tablename__ = "android_app"
    mysql_character_set = 'utf8',
    trackViewUrl = Column(String(256))
    trackName = Column(String(128))
    pkgName = Column(String(128),primary_key=True)
    geners = Column(String(256))
    sellerName = Column(String(256))
    version = Column(String(128))
    downloadCount = Column(String(128))
    fileSize = Column(String(128))
    iconUrl = Column(String(128))
    downloadUrl = Column(String(128))
    description = Column(String(128))
    publishDate = Column(String(128))
    screenShots = Column(String(128))
    averageUserRating = Column(String(128))
    userRatingCount = Column(Integer())
    crawl_time = Column(Date())


for platform,db_num in redis_db.iteritems():
    pool=redis.ConnectionPool(host=redis_host,port = redis_port,db=redis_db[platform])
    r = redis.StrictRedis(connection_pool=pool)
    if platform == "android":
        session = DBSession()
        session.query(android_app).delete()
        session.commit()
        for app in r.keys():
            appinfo = r.get(app)
            jappinfo = json.loads(appinfo)
            for k,v in jappinfo.iteritems():
                if isinstance(v,list):
                    jappinfo[k] = str(json.dumps(v,ensure_ascii = True))
                """
                elif isinstance(v,unicode):
                    jappinfo[k] = v.encode("utf8")
                """
            newApp = android_app(**jappinfo)
            try:
                session.add(newApp)
            except:
                session.update(newApp)
            session.commit()
        session.close()



