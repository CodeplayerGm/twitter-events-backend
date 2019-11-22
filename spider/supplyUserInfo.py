from Config_2019 import getDBByName
import time
from pyquery import PyQuery
from got2019.TweetManager import getHtmlWithURL

if __name__ == '__main__':
    # 先查询已爬取的推文，获得已有的用户screen_name集
    db = getDBByName('2019HongKong_protest')
    dataset = db.dataset
    dataList = dataset.find()
    screenNameList = list()
    dataSetCount = 0
    for dataItem in dataList:
        dataSetCount += 1
        tweet = dataItem['tweet']
        userScreenName = tweet['user']['screen_name']
        if userScreenName not in screenNameList:
            screenNameList.append(userScreenName)
    print('当前共有推文：' + str(dataSetCount) + '条。 待补充信息的用户：' + str(len(screenNameList)))
    # 根据screenName生成查询用户信息url，获取各screenName对应的用户信息
    print('开始爬取用户信息')
    urlPrefix = 'https://twitter.com/'
    userInfoDict = dict()
    time_start = time.time()
    count = 1
    for sname in screenNameList:
        url = urlPrefix + sname
        userHtml = getHtmlWithURL(url)
        userDoc = PyQuery(userHtml)
        userTweetsNum = userDoc('li.ProfileNav-item--tweets a span.ProfileNav-value').attr('data-count')
        userFollowersNum = userDoc('li.ProfileNav-item--followers a span.ProfileNav-value').attr('data-count')
        userDesc = userDoc('div.ProfileHeaderCard p.ProfileHeaderCard-bio').text().replace('\n', ' ').replace('# ', '#').replace( '@ ', '@')
        userLocation = userDoc('div.ProfileHeaderCard-location span.ProfileHeaderCard-locationText').text()
        userInfoDict[sname] = {'tweetsNum': userTweetsNum, 'followersNum': userFollowersNum, 'desc': userDesc, 'location': userLocation}
        print(str(count) + 'th user ' + sname + ' spider finish!')
        count += 1
        if count == 10:
            break
    time_end = time.time()
    print('用户信息爬取耗时：', time_end - time_start)
    # 重新写入完整的推文
    print('开始写入完整推文 ')
    dataCol = db['dataSetFull']
    time_start = time.time()
    count = 1
    for item in dataList:
        tweet = item['tweet']
        userScreenName = tweet['user']['screen_name']
        fullTweet = dict()
        fullTweet['id'] = tweet['id']
        fullTweet['conversation_id'] = tweet['conversation_id']
        fullTweet['is_reply'] = tweet['is_reply']
        fullTweet['created_at'] = tweet['created_at']
        fullTweet['hashtags'] = tweet['hashtags']
        fullTweet['urls'] = tweet['urls']
        fullTweet['mentions'] = tweet['mentions']
        fullTweet['lang'] = tweet['lang']
        fullTweet['raw_text'] = tweet['raw_text']
        fullTweet['standard_text'] = tweet['standard_text']
        fullTweet['user'] = {
            'screen_name': tweet['user']['screen_name'],
            'data_name': tweet['user']['data_name'],
            'user_id': tweet['user']['user_id'],
            'avatar_src': tweet['user']['avatar_src'],
            'userbadges': tweet['user']['userbadges'],
            'tweetsNum': userInfoDict[userScreenName]['tweetsNum'],
            'followersNum': userInfoDict[userScreenName]['followersNum'],
            'desc': userInfoDict[userScreenName]['desc'],
            'location': userInfoDict[userScreenName]['location']
        }
        fullTweet['media'] = tweet['media']
        fullTweet['action'] = tweet['action']
        print(fullTweet)
        dataCol.insert_one({'tweet': fullTweet, 'id': item['id'], 'q': item['q']})
        print(str(count) + '个推文信息已写入！')
        count += 1
    time_end = time.time()
    print('写入新信息耗时：', time_end - time_start)