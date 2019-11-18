# -*- coding:utf-8 -*-
# 爬取推文
# import time
import json
from datetime import datetime

import multiprocessing
from multiprocessing import Pool

from .Config_2019 import get_noau_config, getMongoClient, closeMongoClient

publicGot, publicDb = get_noau_config()

def advance_search_dataset(q, maxNum, actionId):  # 获取推文，放入MongoDB数据库
    print('one search action start !')
    print('q:' + q + '  num:' + str(maxNum))
    # collection = publicDb.event_list
    # print('eventlist num:' + str(len(list(collection.find()))))
    dataset = publicDb.dataset
    tweetCriteria = publicGot.manager.TweetCriteria().setQuerySearch(q).setMaxTweets(maxNum)
    tweets = publicGot.manager.TweetManager.getTweets(tweetCriteria)
    print('tweets num:' + str(len(tweets)))
    tweetsNum = len(tweets)
    insertNum = 0
    for tweet in tweets:
        # tweet = dict(tweet)
        # print('tweet content: ' + str(tweet.id) + '===' + str(tweet.text))
        # print(dataset.find_one({'id': tweet.id}))
        if dataset.find_one({'id': tweet.id}) is None:  # 查看推文是否已存在，若不存在则放入数据库
            # print({'id': tweet.id, 'tweet': tweet, 'actionId': actionId, 'f': f, 'q': q})
            tweet = {'id': tweet.id, 'permalink': tweet.permalink, 'username': tweet.username,
                    'text': tweet.text, 'date': tweet.date, 'formatted_date': tweet.formatted_date,
                    'retweets': tweet.retweets, 'favorites': tweet.favorites, 'mentions': tweet.mentions,
                    'hashtags': tweet.hashtags, 'geo': tweet.geo, 'urls': tweet.urls, 'author_id': tweet.author_id,
                    'actionId': actionId, 'q': q}
            # print(tweet)
            res = dataset.insert_one(tweet)
            insertNum += 1
            print('store result:' + str(res))
    dataset_log = publicDb.dataset_log
    timeNow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dataset_log.insert_one({'actionId': actionId, 'insertTime': timeNow, 'maxNum': maxNum, 'tweetsNum': tweetsNum, 'insertNum': insertNum, 'q': q})
            
def run_dataset_task(actionId, q, maxNum):
    try:
        # if type(f) != list:
        # print('get tweets once ----------------------------------------')
        advance_search_dataset(q, maxNum, actionId)
        # else:
            # 多进程获取推文
            # print('get tweets multi ----------------------------------------')
            # pool = Pool(processes=multiprocessing.cpu_count())
            # python官方建议：废弃apply，使用apply_async（使用apply在这里会出错）
            # [pool.apply_async(advance_search_dataset, (q, fi, num, actionId)) for fi in f]
            # [pool.apply(advance_search_dataset, (q, f, num, event_id)) for f in message_data['f']]
            # pool.close()
            # pool.join()
        return True
    except:
        print('run_dataset_task occurs error !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        return False


if __name__ == '__main__':
    print('2019HongKong_protest craw_worker start!')
    c = getMongoClient()
    db = c['2019HongKong_protest']
    searchInfo = db.searchInfo
    searchInfoResult = searchInfo.find(no_cursor_timeout=True)
    closeMongoClient(c)
    for item in searchInfoResult:
        actionId = item['actionId']
        q = item['q']
        # f = item['f']
        maxNum = item['maxNum']
        print('2019HongKong_protest craw_worker process!')
        run_dataset_task(actionId, q, maxNum)  # 获取推文
        # if craw:
            # 添加查询日志
            # db.dataset_log.insert_one({'actionId': actionId, 'q': q, 'f': f, 'num': num, 'status': 1})
        # else:
            # db.dataset_log.insert_one({'actionId': actionId, 'q': q, 'f': f, 'num': num, 'status': 0})
    print('2019HongKong_protest craw_worker finish!')
