# -*- coding:utf-8 -*-
from datetime import datetime
from .got3 import manager as gotter

def doTweetSearchOnce(q, maxNum, db):  # 获取推文，放入MongoDB数据库
    print('one search action start !')
    print('q:' + q + '  num:' + str(maxNum))
    # collection = publicDb.event_list
    # print('eventlist num:' + str(len(list(collection.find()))))
    actionId = hash(q)
    dataset = db.dataset
    insertLog = db.insertLog
    tweetCriteria = gotter.TweetCriteria().setQuerySearch(q).setMaxTweets(maxNum)
    tweets = gotter.TweetManager.getTweets(tweetCriteria)
    print('get tweets num:' + str(len(tweets)))
    tweetsNum = len(tweets)
    insertNum = 0
    for tweet in tweets:
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
    timeNow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    insertLog.insert_one({'actionId': actionId, 'insertTime': timeNow, 'maxNum': maxNum, 'tweetsNum': tweetsNum, 'insertNum': insertNum, 'q': q})
    return {'tweetsNum': tweetsNum, 'insertNum': insertNum}