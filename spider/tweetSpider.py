# -*- coding:utf-8 -*-
# '2019香港'事件获取
# import pymongo
from Config_2019 import get_noau_config
from datetime import datetime

# client = pymongo.MongoClient('mongodb://3.220.111.222:27017/')
# client.admin.authenticate("aircas", "aircas@2018", mechanism='SCRAM-SHA-1')
# db = client['2019HongKong_protest']

def generateTrigger(triggers):
    res = ''
    for i in range(len(triggers)):
        if i == 0:
            res += '(' + triggers[i]
        else:
            res += ' OR ' + triggers[i]
    res += ')'
    return res

def generateTopic(topics):
    res = ''
    for i in range(len(topics)):
        if i == 0:
            res += topics[i]
        else:
            res += ' OR ' + topics[i]
    return res

# 设置推特查询条件
def set_conditions():
    # 设置起始、终止时间
    stime = '2019-03-01'
    etime = '2019-11-10'

    # 设置香港事件 查询地点名词
    # locations = ['Hong Kong', 'Hong Kong Island', 'Central and Western District', 'Eastern District',
    #              'Southern District', 'Wan Chai District', 'Kowloon', 'Kwun Tong District',
    #              'Sham Shui Po District', 'Wong Tai Sin District', 'Yau Tsim Mong District', 'New Territories', 'Island District',
    #              'North District', 'Sai Kung District', 'Sha Tin District', 'Tai Po District', 'Tsuen Wan District',
    #              'Tuen Mun District', 'Yuen Long District', 'Kowloon Tong',
    #              'Kowloon Bay', 'Pat Sin Leng', 'Sheung Shui', 'Sheung Wan', 'To Kwa Wan',
    #              'Tai Shui Hang', "Tate's Cairn", 'Tai Hang', 'Tai Kok Tsui', 'Sunset Peak', 'Tai Po', 'Lantau Island',
    #              'Tai Po Market', 'Tai Long Wan', 'Tai Wai', 'Tai Mo Shan', 'Tai Wo Hau', 'Tai O',
    #              'Tai Lam Chung', 'Tai Lam Chung Reservoir', 'Siu Sai Wan', 'Siu Lam', 'Central and Western', 'Central', 'Yuen Long',
    #              'Tin Shui Wai', 'Tin Hau', 'Prince Edward', 'Tai Koo', 'Tai Wo', 'Tuen Mun', 'Fo Tan',
    #              'Ngau Tau Kok', 'North Point', 'North', 'Shek Mun', 'Shek Kong', 'Shek Kip Mei',
    #              'Shek Tong Tsui', 'Shek Pik', 'Shek O', 'Siu Hong', 'East Tsim Sha Tsui', 'Tsim Bei Tsui', 'Sai Kung',
    #              'Sai Ying Pun', 'Sai Wan Ho', 'Ho Man Tin', 'Jordan', 'Hang Hau',
    #              'Heng Fa Chuen', 'Sha Tin', 'Sha Tin Wai', 'Sha Tau Kok', 'Stanley', 'Chek Lap Kok',
    #              'Peng Chau', 'Mong Kok', 'Ngong Ping', 'Stonecutters Island',
    #              'Tung Chung', 'Eastern', 'Lam Tsuen', 'Sunny Bay', 'Yau Tsim Mong', 'Yau Ma Tei',
    #              'Yau Tong', 'Admiralty', 'Cheung Sha Wan', 'Cheung Chau', 'Tsing Shan', 'Castle Peak', 'Tsing Yi']
    locations = ['Admiralty']

    # 香港事件 查询关键词
    triggers = ['protest', 'protests', 'protesters', 'citizens', 'march', 'marched', 'police', 'government', 'officers',
                'lam', 'carrie', 'political', 'force', 'violence', 'riot', 'mainland', 'independent', 'lawmakers', 'revolution']

    # 香港事件 查询话题
    topics = ['#HongKong', '#HongKongProtests', '#HongKongProtesters', '#HK', '#HKprotests', '#FreeHK', '#china',
              '#StandWithHongKong', '#FightForFreedomStandWithHongKong', '#香港']

    return stime, etime, locations, triggers, topics

# 生成查询语句
def get_task(event_list):
    print('2019HongKong_protest event_list num:' + str(len(event_list)))
    searchList = list()
    for event in event_list:
        # print(event)
        # print(type(event))
        stime = event['event']['stime']
        etime = event['event']['etime']
        location = event['event']['location']
        triggers = event['event']['triggers']
        topics = event['event']['topics']
        q = '(' + location + ')' + ' ' + triggers + ' ' + topics + ' ' + 'since:' + stime + ' ' + 'until:' + etime
        actionId = event['id']
        message = {'actionId': actionId, 'q': q, 'maxNum': 100}
        # print(message)
        searchList.append(message)
    return searchList

publicGot, publicDb = get_noau_config()
# 执行查询语句，获取推文
def advance_search_dataset(actionId, q, maxNum):  # 获取推文，放入MongoDB数据库
    # try:
    print('one search action start !')
    print('q:' + q + '  num:' + str(maxNum))
    # collection = publicDb.event_list
    # print('eventlist num:' + str(len(list(collection.find()))))
    dataset = publicDb.dataset
    tweetCriteria = publicGot.manager.TweetCriteria().setQuerySearch(q).setMaxTweets(maxNum)
    print('set criteria okkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
    tweets = publicGot.manager.TweetManager.getTweets(tweetCriteria)
    print('get tweets kooooooooooooooooooooooooooooooooooooooo')
    tweetsNum = len(tweets)
    print('tweets num:' + str(tweetsNum))
    # insertNum = 0
    # for tweet in tweets:
    #     # print(tweet)
    #     if dataset.find_one({'id': tweet['id']}) is None:  # 查看推文是否已存在，若不存在则放入数据库
    #         dataItem = {'tweet': tweet, 'id': tweet['id'], 'q': q}
    #         res = dataset.insert_one(dataItem)
    #         insertNum += 1
    #         # print('store result:' + str(res))
    # print('store: ' + str(insertNum))
    # dataset_log = publicDb.dataset_log
    # timeNow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # dataset_log.insert_one({'actionId': actionId, 'insertTime': timeNow, 'maxNum': maxNum, 'tweetsNum': tweetsNum, 'insertNum': insertNum, 'q': q})
    return True
    # except:
    #     print('run_dataset_task occurs error !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    # return False

if __name__ == '__main__':
    stime, etime, locations, triggers, topics = set_conditions()
    # 事件查询条件放入MongoDB数据库 按地点名做事件循环
    requests = list()
    triggersStr = generateTrigger(triggers)
    topicsStr = generateTopic(topics)
    for loc in locations:
        eventId = hash(stime + etime + loc + triggersStr + topicsStr)
        requests.append({'id': eventId,
                         'event': {'stime': stime, 'etime': etime, 'location': loc,
                                   'triggers': triggersStr, 'topics': topicsStr}})

    # 根据条件生成查询语句
    searchList = get_task(requests)
    # 执行查询语句
    for item in searchList:
        actionId = item['actionId']
        q = item['q']
        # f = item['f']
        maxNum = item['maxNum']
        print('2019HongKong_protest craw_worker process!')
        advance_search_dataset(actionId, q, maxNum)  # 获取推文
        # if craw:
            # 添加查询日志
            # db.dataset_log.insert_one({'actionId': actionId, 'q': q, 'f': f, 'num': num, 'status': 1})
        # else:
            # db.dataset_log.insert_one({'actionId': actionId, 'q': q, 'f': f, 'num': num, 'status': 0})
    print('2019HongKong_protest craw_worker finish!')
