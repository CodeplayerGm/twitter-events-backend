import pymongo
import os
from xml.etree import ElementTree as ET

def getMongoClient():
    # 读取xml文件
    file = ET.parse('./config.xml')
    # file = ET.parse('../config.xml')
    # 获取根节点
    root = file.getroot()
    database = root.findall('database')[0]
    mongo = database.findall('mongo')[0]
    ip = mongo.findall('ip')[0].text
    port = mongo.findall('port')[0].text
    username = mongo.findall('username')[0].text
    password = mongo.findall('password')[0].text
    if username == '#' or password == '#':
        return pymongo.MongoClient('mongodb://localhost:27017/')
    else:
        client = pymongo.MongoClient(ip, port, connect=False)
        client.admin.authenticate(username, password, mechanism='SCRAM-SHA-1')
        return client

if __name__ == '__main__':
    getMongoClient()