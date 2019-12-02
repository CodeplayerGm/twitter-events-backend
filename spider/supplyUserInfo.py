from Config_2019 import getDBByName, getLocalDbByName
import time,os
from pyquery import PyQuery
from got2019.TweetManager import getHtmlWithURL

userAvatarSavePath = './userHeads/'

# 爬取用户信息
def spiderUserInfo(dbName):
    # 先查询已爬取的推文，获得已有的用户screen_name集
    db = getDBByName(dbName)
    dataset = db['dataset']
    dataList = dataset.find()
    screenNameDict = dict()
    dataSetCount = 0
    for dataItem in dataList:
        dataSetCount += 1
        tweet = dataItem['tweet']
        userScreenName = tweet['user']['screen_name']
        userAvatarSrc = tweet['user']['avatar_src']
        if userScreenName not in screenNameDict.keys():
            screenNameDict[userScreenName] = {'avatar_src': userAvatarSrc}
    print('当前共有推文：' + str(dataSetCount) + '条。 待补充信息的用户：' + str(len(screenNameDict)))
    # 根据screenName生成查询用户信息url，获取各screenName对应的用户信息
    print('开始爬取用户信息')
    urlPrefix = 'https://twitter.com/'
    userInfoDict = dict()
    alreadyExistList = os.listdir(userAvatarSavePath)
    time_start = time.time()
    count = 1
    for sname in screenNameDict.keys():
        # 爬取用户发文量、关注者、描述、地点信息
        url = urlPrefix + sname
        userHtml = getHtmlWithURL(url).text
        userDoc = PyQuery(userHtml)
        userTweetsNum = userDoc('li.ProfileNav-item--tweets a span.ProfileNav-value').attr('data-count')
        userFollowersNum = userDoc('li.ProfileNav-item--followers a span.ProfileNav-value').attr('data-count')
        userDesc = userDoc('div.ProfileHeaderCard p.ProfileHeaderCard-bio').text().replace('\n', ' ').replace('# ',
                                                                                                              '#').replace(
            '@ ', '@')
        userLocation = userDoc('div.ProfileHeaderCard-location span.ProfileHeaderCard-locationText').text()
        userInfoDict[sname] = {'tweetsNum': userTweetsNum, 'followersNum': userFollowersNum, 'desc': userDesc,
                               'location': userLocation}
        # 爬取用户头像数据
        userAvatarSrc = screenNameDict[sname]['avatar_src']
        fileName = sname + '.jpg'
        if fileName not in alreadyExistList:
            userAvatarHtml = getHtmlWithURL(userAvatarSrc)
            if userAvatarHtml.status_code == 200:
                with open(userAvatarSavePath + '/' + fileName, "wb") as f:
                    f.write(userAvatarHtml.content)
            elif userAvatarHtml.status_code == 404:
                print('爬取用户：' + sname + '的头像失败，url:' + userAvatarSrc)
        print('成功爬取到第 ' + str(count) + ' 个用户信息 ' + sname)
        count += 1
    time_end = time.time()
    print('用户信息爬取耗时：', time_end - time_start)
    # 重新写入完整的推文
    # print('开始写入完整推文 ')
    # dataCol = db['dataSetFull']
    # 重新执行查询，刷新cursor
    # dataList = dataset.find()
    # time_start = time.time()
    # count = 1
    # for item in dataList:
    #     tweet = item['tweet']
    #     userScreenName = tweet['user']['screen_name']
    #     fullTweet = dict()
    #     fullTweet['id'] = tweet['id']
    #     fullTweet['conversation_id'] = tweet['conversation_id']
    #     fullTweet['is_reply'] = tweet['is_reply']
    #     fullTweet['created_at'] = tweet['created_at']
    #     fullTweet['hashtags'] = tweet['hashtags']
    #     fullTweet['urls'] = tweet['urls']
    #     fullTweet['mentions'] = tweet['mentions']
    #     fullTweet['lang'] = tweet['lang']
    #     fullTweet['raw_text'] = tweet['raw_text']
    #     fullTweet['standard_text'] = tweet['standard_text']
    #     fullTweet['user'] = {
    #         'screen_name': tweet['user']['screen_name'],
    #         'data_name': tweet['user']['data_name'],
    #         'user_id': tweet['user']['user_id'],
    #         'avatar_src': tweet['user']['avatar_src'],
    #         'userbadges': tweet['user']['userbadges'],
    #         'tweetsNum': userInfoDict[userScreenName]['tweetsNum'],
    #         'followersNum': userInfoDict[userScreenName]['followersNum'],
    #         'desc': userInfoDict[userScreenName]['desc'],
    #         'location': userInfoDict[userScreenName]['location']
    #     }
    #     fullTweet['media'] = tweet['media']
    #     fullTweet['action'] = tweet['action']
    #     print(fullTweet)
    #     dataCol.insert_one({'tweet': fullTweet, 'id': item['id'], 'q': item['q']})
    #     print(str(count) + '个推文信息已写入！')
    #     count += 1
    # time_end = time.time()
    # print('写入新信息耗时：', time_end - time_start)

if __name__ == '__main__':
    spiderUserInfo('2019HongKong_protest')
