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
    etime = '2019-10-20'

    # 设置香港事件 查询地点名词
    # locations = 'Hong Kong OR ' + 'Hong Kong Island OR Central and Western District OR Eastern District OR Southern District OR Wan Chai District OR ' + 'Kowloon OR Kowloon City District OR Kwun Tong District OR Sham Shui Po District OR Wong Tai Sin District OR Yau Tsim Mong District OR ' + 'New Territories OR Island District OR Kwai Tsing District OR North District OR Sai Kung District OR Sha Tin District OR Tai Po District OR Tsuen Wan District OR Tuen Mun District OR Yuen Long District OR ' + "Kowloon Reservoir OR Kowloon City OR Kowloon Tong OR Kowloon Bay OR Pat Sin Leng OR Sheung Shui OR Sheung Wan OR To Kwa Wan OR Tai Shui Hang OR Tate's Cairn OR Tai Hang OR Tai Mei Tuk OR Tai Kok Tsui OR Tai Tung Shan OR Sunset Peak OR Tai Po Industrial Estate OR Tai Po OR Tai Po Kau OR Tai Po Market OR " + "Tai Long Wan OR Tai Wai OR Tai Mo Shan OR Tai Wo Hau OR Tai Mong Tsai OR Tai Tam Reservoirs OR Tai Tam Bay OR Tai O OR Lantau Island OR Tai Pang Wan OR Mirs Bay OR Tai Lam Chung OR Tai Lam Chung Reservoir OR Siu Sai Wan OR Siu Lam OR Central and Western OR Central OR Tseng Lan Shue OR Yuen Long OR Fan Lau OR " + "Tin Shui Wai OR Tin Hau OR Prince Edward OR Tai Koo OR Tai Wo OR Tuen Mun OR Fo Tan OR Ngau Chi Wan OR Ngau Mei Hoi OR Port Shelter OR Ngau Tau Kok OR North Point OR North OR Pak Tam Chung OR Ta Kwu Ling OR Ting Kau OR Shek Mun OR Shek Kong OR Shek Kip Mei OR Shek Tong Tsui OR Shek Pik OR Shek Pik Reservoir OR " + "Shek O OR Kei Ling Ha Hoi OR Three Fathoms Cove OR Siu Hong OR Crooked Island OR Tolo Harbour OR Tsim Sha Tsui OR East Tsim Sha Tsui OR Tsim Bei Tsui OR Sai Kung Hoi OR Inner Port Shelter OR Sai Kung OR Sai Ying Pun OR Sai Wan Ho OR Ho Man Tin OR Jordan OR Hang Hau OR Heng Fa Chuen OR Sha Tin Hoi OR Sha Tin OR " + "Sha Tin Wai OR Sha Tau Kok OR Pui O OR Tolo Channel OR Stanley OR Chek Lap Kok OR King's Park OR Wo Hop Shek OR Peng Chau OR Mong Kok OR Ngong Ping OR Ngong Suen Chau OR Stonecutters Island OR Tung Ping Chau OR Tung Chung OR Eastern OR Tung Lung Chau OR Kwo Chau Kwan To OR Lam Tsuen OR Sunny Bay OR Ho Pui Reservoir OR " + "Yau Tsim Mong OR Yau Ma Tei OR Yau Tong OR Admiralty OR Cheung Sha Wan OR Cheung Chau OR Tsing Shan OR Castle Peak OR Tsing Yi OR Tsing Lung Tau"
    locations = ['Hong Kong', 'Hong Kong Island', 'Central and Western District', 'Eastern District',
                 'Southern District', 'Wan Chai District', 'Kowloon', 'Kowloon City District', 'Kwun Tong District',
                 'Sham Shui Po District',
                 'Wong Tai Sin District', 'Yau Tsim Mong District', 'New Territories', 'Island District',
                 'Kwai Tsing District', 'North District', 'Sai Kung District', 'Sha Tin District', 'Tai Po District',
                 'Tsuen Wan District',
                 'Tuen Mun District', 'Yuen Long District', 'Kowloon Reservoir', 'Kowloon City', 'Kowloon Tong',
                 'Kowloon Bay', 'Pat Sin Leng', 'Sheung Shui', 'Sheung Wan', 'To Kwa Wan',
                 'Tai Shui Hang', "Tate's Cairn", 'Tai Hang', 'Tai Mei Tuk', 'Tai Kok Tsui', 'Tai Tung Shan',
                 'Sunset Peak', 'Tai Po Industrial Estate', 'Tai Po', 'Lantau Island',
                 'Tai Po Kau', 'Tai Po Market', 'Tai Long Wan', 'Tai Wai', 'Tai Mo Shan', 'Tai Wo Hau', 'Tai Mong Tsai',
                 'Tai Tam Reservoirs', 'Tai Tam Bay', 'Tai O',
                 'Tai Pang Wan', 'Mirs Bay', 'Tai Lam Chung', 'Tai Lam Chung Reservoir', 'Siu Sai Wan', 'Siu Lam',
                 'Central and Western', 'Central', 'Tseng Lan Shue', 'Yuen Long',
                 'Fan Lau', 'Tin Shui Wai', 'Tin Hau', 'Prince Edward', 'Tai Koo', 'Tai Wo', 'Tuen Mun', 'Fo Tan',
                 'Ngau Chi Wan', 'Ngau Mei Hoi',
                 'Port Shelter', 'Ngau Tau Kok', 'North Point', 'North', 'Pak Tam Chung', 'Ta Kwu Ling', 'Ting Kau',
                 'Shek Mun', 'Shek Kong', 'Shek Kip Mei',
                 'Shek Tong Tsui', 'Shek Pik', 'Shek Pik Reservoir', 'Shek O', 'Kei Ling Ha Hoi', 'Three Fathoms Cove',
                 'Siu Hong', 'Crooked Island', 'Tolo Harbour', 'Tsim Sha Tsui',
                 'East Tsim Sha Tsui', 'Tsim Bei Tsui', 'Sai Kung Hoi', 'Inner Port Shelter', 'Sai Kung',
                 'Sai Ying Pun', 'Sai Wan Ho', 'Ho Man Tin', 'Jordan', 'Hang Hau',
                 'Heng Fa Chuen', 'Sha Tin Hoi', 'Sha Tin', 'Sha Tin Wai', 'Sha Tau Kok', 'Pui O', 'Tolo Channel',
                 'Stanley', 'Chek Lap Kok', "King's Park",
                 'Wo Hop Shek', 'Peng Chau', 'Mong Kok', 'Ngong Ping', 'Ngong Suen Chau', 'Stonecutters Island',
                 'Tung Ping Chau', 'Tung Chung', 'Eastern', 'Tung Lung Chau',
                 'Kwo Chau Kwan To', 'Lam Tsuen', 'Sunny Bay', 'Ho Pui Reservoir', 'Yau Tsim Mong', 'Yau Ma Tei',
                 'Yau Tong', 'Admiralty', 'Cheung Sha Wan', 'Cheung Chau',
                 'Tsing Shan', 'Castle Peak', 'Tsing Yi', 'Tsing Lung Tau']

    # 香港事件 查询关键词
    triggers = ['protest', 'protests', 'protesters', 'citizens', 'march', 'marched', 'police', 'government', 'officers',
                'lam',
                'carrie', 'political', 'force', 'violence', 'riot', 'mainland', 'independent', 'lawmakers',
                'revolution']

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
    print('tweets num:' + str(len(tweets)))
    tweetsNum = len(tweets)
    insertNum = 0
    for tweet in tweets:
        print(tweet)
        if dataset.find_one({'id': tweet['id']}) is None:  # 查看推文是否已存在，若不存在则放入数据库
            dataItem = {'tweet': tweet, 'id': tweet['id'], 'q': q}
            res = dataset.insert_one(dataItem)
            insertNum += 1
            print('store result:' + str(res))
    dataset_log = publicDb.dataset_log
    timeNow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dataset_log.insert_one({'actionId': actionId, 'insertTime': timeNow, 'maxNum': maxNum, 'tweetsNum': tweetsNum, 'insertNum': insertNum, 'q': q})
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
