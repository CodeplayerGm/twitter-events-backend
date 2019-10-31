# -*- coding:utf-8 -*-
# got文件、MongoDB数据库和Redis数据库配置文件
import os
import sys
import pymongo
# import redis

def get_noau_config():
    # got文件
    if sys.version_info[0] < 3:
        # print('import got')
        import got
    else:
        # print('import got333333333333333333333333333')
        # import got
        import got3 as got

    # MongoDB数据库
    # client = pymongo.MongoClient(os.environ['MONGOHOST'], 27017, connect=False)
    #client = pymongo.MongoClient('mongodb://3.220.111.222:27017/')
    client=pymongo.MongoClient('3.220.111.222', 27017, connect=False)
    client.admin.authenticate("aircas", "aircas@2018", mechanism='SCRAM-SHA-1')
    # db = client.natural_disaster
    db = client['2019HongKong_protest']
    # db.authenticate(name='aircas',password='aircas@2018')

    # Redis数据库
    # r = redis.StrictRedis(host=os.environ['REDISHOST'], port=6379, db=0)
    # r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

    return got, db

def getMongoClient():
    client = pymongo.MongoClient('3.220.111.222', 27017, connect=False)
    client.admin.authenticate("aircas", "aircas@2018", mechanism='SCRAM-SHA-1')
    return client

def closeMongoClient(client):
    client.close()
    
def getGot():
    # got文件
    if sys.version_info[0] < 3:
        import got
    else:
        import got3 as got
    return got
