from dbConfig import getMongoClient
from util.util import getProgramWordsListFromExp, getEventSummaryWordsStr, getAllTweetListLength, ToDecimal2F, setHotMapPointSizeValue

# 获取事件词云数据
def getWordCloudDataAction(clusterDbName):
    try:
        client = getMongoClient()
        db = client[clusterDbName]
        clusterResultCol = db['clusterResult']
        clusters = clusterResultCol.find()
        keyWordsDic = dict()
        geoWordsDic = dict()
        for cluster in clusters:
            keywords = cluster['summary']['keywords']
            geowords = cluster['summary']['geowords']
            for word in keywords:
                if word in keyWordsDic.keys():
                    keyWordsDic[word] += 1
                else:
                    keyWordsDic[word] = 1
            for wordItem in geowords:
                word = wordItem[0]
                freq = wordItem[1]
                if word in geoWordsDic.keys():
                    geoWordsDic[word] += freq
                else:
                    geoWordsDic[word] = freq
        # cNameList = db.collection_names()
        # keyWordsDic = dict()
        # for cName in cNameList:
        #     # 取每个事件簇
        #     collection = db[cName]
        #     # 取全部子事件
        #     subEvents = collection.find()
        #     for subEvent in subEvents:
        #         keyWords = subEvent['summary']['keywords']
        #         for word in keyWords:
        #             if word in keyWordsDic.keys():
        #                 keyWordsDic[word] += 1
        #             else:
        #                 keyWordsDic[word] = 1
    except:
        return {'resCode': 0,
                'resStr': '词云数据库查询失败',
                'resObject': '',
                'resList': []}
    # 按频次排序
    sortedKeyWords = sorted(keyWordsDic.items(), key=lambda x: x[1], reverse=True)
    sortedGeoWords = sorted(geoWordsDic.items(), key=lambda x: x[1], reverse=True)
    # for item in sortedKeyWords:
    #     print(item[0] + ':' + str(item[1]))
    # 显示结果保留最多40个  30个keywords 10个geowords
    result = list()
    if len(sortedKeyWords) > 30:
        tempList = sortedKeyWords[0:30]
    else:
        tempList = sortedKeyWords
    if len(sortedGeoWords) > 10:
        tempList += sortedGeoWords[0:10]
    else:
        tempList += sortedGeoWords
    for item in tempList:
        result.append({'name': item[0], 'value': item[1]})
    client.close()
    return {'resCode': 1,
            'resStr': '获取词云数据成功',
            'resObject': '',
            'resList': result}

# 获取热点地图数据
def getMapHotDataAction(clusterDbName):
    try:
        client = getMongoClient()
        db = client[clusterDbName]
        clusterResultCol = db['clusterResult']
        clusters = clusterResultCol.find()
        addressInfo = dict()
        for cluster in clusters:
            hot = cluster['summary']['hot']
            geo_infer = cluster['geo_infer']
            for geoItem in geo_infer:
                address = geoItem['address']
                lat = geoItem['lat']
                lon = geoItem['lon']
                freq = geoItem['freq']
                country = geoItem['country']
                # print(address + ';' + country + ';' + str(centerLat) + ';' + str(centerLng) + ';' + str(hot))
                if address:
                    if address in addressInfo.keys():
                        addressInfo[address]['hotSum'] += hot * freq
                        addressInfo[address]['hotCount'] += 1
                    else:
                        addressInfo[address] = {'hotSum': hot, 'hotCount': 1, 'geo': {'lat': lat, 'lng': lon}, 'country': country}
        resultInfo = {'addressInfo': {}, 'countryInfo': []}
        countryInfoDic = dict()
        # 计算各个address的热点平均值
        for key in addressInfo.keys():
            hotAve = addressInfo[key]['hotSum'] / addressInfo[key]['hotCount']
            geo = addressInfo[key]['geo']
            country = addressInfo[key]['country']
            resultInfo['addressInfo'][key] = {'hot': hotAve, 'geo': geo}
            if country:
                if country in countryInfoDic.keys():
                    countryInfoDic[country] += hotAve
                else:
                    countryInfoDic[country] = hotAve
        # 国家热度总值最多保留10个
        countryInfoList = sorted(countryInfoDic.items(), key=lambda x: x[1], reverse=True)
        if len(countryInfoList) > 10:
            resultInfo['countryInfo'] = countryInfoList[0:10]
        else:
            resultInfo['countryInfo'] = countryInfoList
        client.close()
        return {'resCode': 1,
                'resStr': '获取热点地图数据成功',
                'resObject': resultInfo,
                'resList': []}
    except:
        return {'resCode': 0,
                'resStr': '热点地图数据库查询失败',
                'resObject': '',
                'resList': []}

# 热点地图address数据转换为echarts格式
def convertMapAddressData(addressInfo, mapZoom):
    res = list()
    for address in addressInfo.keys():
        hot = ToDecimal2F(addressInfo[address]['hot'])
        lat = addressInfo[address]['geo']['lat']
        lng = addressInfo[address]['geo']['lng']
        # rawValue = ToDecimal2F(hot / 15 * mapZoom)
        # sizeValue = 500 if rawValue > 500 else rawValue
        # sizeValue = 80 if sizeValue < 80 else sizeValue
        res.append({'name': address, 'value': [lng, lat, hot, hot]})
        # print({'name': address, 'value': [lng, lat, sizeValue, ToDecimal2F(hot)]})
    # 当地点数据过多时，取前100个
    res.sort(key=lambda item: item["value"][3], reverse=True)
    res = res[0:100]
    # 设置点大小
    res = setHotMapPointSizeValue(0.1, 500, 0.3, 80, res)
    return res

# 获取事件讨论走势数据
def getDiscussionTrendDataAction(clusterDbName, clusterTweetDict):
    try:
        # client = getMongoClient()
        # db = client[clusterDbName]
        # clusterResultCol = db['clusterResult']
        # clusters = clusterResultCol.find()
        discussionInfo = dict()
        # for cluster in clusters:
        #     mostPossibleTime = cluster['time_infer']['most_possible_time'][0:10]
        #     cluid = cluster['cluid']
        #     tweetsNum = len(clusterTweetDict[cluid])
        #     if mostPossibleTime in discussionInfo.keys():
        #         discussionInfo[mostPossibleTime] += tweetsNum
        #     else:
        #         discussionInfo[mostPossibleTime] = tweetsNum

        for key in clusterTweetDict.keys():
            tweetList = clusterTweetDict[key]
            for tweet in tweetList:
                time = tweet['created_at'][0:10]
                if time in discussionInfo.keys():
                    discussionInfo[time] += 1
                else:
                    discussionInfo[time] = 1
        # client.close()
        return {'resCode': 1,
                'resStr': '获取事件讨论走势数据成功',
                'resObject': discussionInfo,
                'resList': []}
    except:
        return {'resCode': 0,
                'resStr': '事件讨论走势数据库查询失败',
                'resObject': '',
                'resList': []}

# 获取事件等级统计数据
def getEventLevelDataAction(clusterDbName):
    try:
        client = getMongoClient()
        db = client[clusterDbName]
        clusterResultCol = db['clusterResult']
        clusters = clusterResultCol.find()
        levelInfo = dict()
        for cluster in clusters:
            level = cluster['summary']['level']
            if level in levelInfo.keys():
                levelInfo[level] += 1
            else:
                levelInfo[level] = 1
        # for key in levelInfo.keys():
        #     print(key + '：' + str(levelInfo[key]))
        client.close()
        return {'resCode': 1,
                'resStr': '获取事件等级统计数据成功',
                'resObject': levelInfo,
                'resList': []}
    except:
        return {'resCode': 0,
                'resStr': '事件等级统计数据库查询失败',
                'resObject': '',
                'resList': []}

# 给定tweetList，根据回复、转发、喜欢数量选出最重要的一条tweet 以及 其回复、转发、喜欢数量
def getBestTweet(tweetsList):
    tweetPointsIndexDict = dict()
    tweetNumsDict = dict()
    tweetIndex = 0
    for tweet in tweetsList:
        # 过滤掉 转发他人的 推文；
        if not tweet['action']['is_retweet']:
            # 取推文的回复、转发、喜欢数量计算重要程度；恐怖袭击类数据缺少回复数量，采用随机数补充
            replyNum = tweet['action']['replies']
            retweetNum = tweet['action']['retweets']
            likeNum = tweet['action']['favorites']
            points = replyNum * 3 + retweetNum * 4 + likeNum * 5
            tweetPointsIndexDict[tweetIndex] = points
            tweetNumsDict[tweetIndex] = {'replyNum': replyNum, 'retweetNum': retweetNum, 'likeNum': likeNum}
        tweetIndex += 1
    # 取重要程度最高的tweet
    tweetPointsIndexOrdered = sorted(tweetPointsIndexDict.items(), key=lambda x: x[1], reverse=True)
    bestIndex = tweetPointsIndexOrdered[0][0]
    bestTweet = tweetsList[bestIndex]
    return bestTweet, tweetNumsDict[bestIndex]

# 获取热门tweeter数据
def getPopularTweeterDataAction(clusterDbName, clusterTweetDict):
    try:
        # 先取热度最高的前 20 个事件实例
        client = getMongoClient()
        db = client[clusterDbName]
        clusterResultCol = db['clusterResult']
        clusters = clusterResultCol.find()
        highHotEvents = list()
        eventHotIndexDict = dict()
        index = 0
        for cluster in clusters:
            hot = cluster['summary']['hot']
            eventHotIndexDict[index] = hot
            index += 1
            highHotEvents.append(cluster)
        # 热度值排序，取前20个
        eventHotIndexOrdered = sorted(eventHotIndexDict.items(), key=lambda x: x[1], reverse=True)[0:20]
        # 从每个事件实例的tweets列表中取出最具代表性的一条推文及作者信息
        resultList = list()
        for eventItem in eventHotIndexOrdered:
            event = highHotEvents[eventItem[0]]
            cluid = event['cluid']
            tweetsList = clusterTweetDict[cluid]
            bestTweet, tweetActionNums = getBestTweet(tweetsList)
            # 获取推文内容以及作者数据
            text = bestTweet['standard_text']
            userName = bestTweet['user']['data_name']
            userHeadSrc = 'none'
            time = bestTweet['created_at']
            resultList.append({'userName': userName, 'userHead': userHeadSrc, 'time': time, 'text': text, 'tweetNums': tweetActionNums})
        # for r in resultList:
        #     print(r)
        client.close()
        return {'resCode': 1,
                'resStr': '获取热门tweeter数据成功',
                'resObject': '',
                'resList': resultList}
    except:
        return {'resCode': 0,
                'resStr': '热门tweeter数据库查询失败',
                'resObject': '',
                'resList': []}

# 获取事件概述方案描述数据
def getEventSummaryProgramDataAction(pname, clusterTweetDict):
    try:
        client = getMongoClient()
        db = client['programs']
        col = db['programs']
        query = {'pname': pname}
        resProgram = list(col.find(query))
        resLen = len(resProgram)
        if resLen > 1:
            client.close()
            return {'resCode': 2,
                    'resStr': '监控方案名' + pname + '数据库冗余',
                    'resObject': '',
                    'resList': []}
        elif resLen == 0:
            client.close()
            return {'resCode': 2,
                    'resStr': '监控方案' + pname + '不存在',
                    'resObject': '',
                    'resList': []}
        else:
            result = '根据您设置的\"' + pname + '\"事件的检测条件，'
            resProgram = resProgram[0]
            # 组织关键词
            keywords = resProgram['keywords']
            keywordsList = list()
            for group in keywords:
                groupList = getProgramWordsListFromExp(group['exp'])
                for word in groupList:
                    if word not in keywordsList:
                        keywordsList.append(word)
                        if len(keywordsList) >= 5:
                            break
                if len(keywordsList) >= 5:
                    break
            result += '我们围绕着' + getEventSummaryWordsStr(keywordsList) + '等关键词，'
            # 组织过滤词
            ignorewords = resProgram['ignorewords']
            if ignorewords:
                ignorewordsList = list()
                for word in getProgramWordsListFromExp(ignorewords):
                    if word not in ignorewordsList:
                        ignorewordsList.append(word)
                        if len(ignorewordsList) >= 5:
                            break
                result += getEventSummaryWordsStr(ignorewordsList) + '等过滤词，'
            # 组织话题
            topics = resProgram['topics']
            if topics:
                topicsList = list()
                for word in getProgramWordsListFromExp(topics):
                    if word not in topicsList:
                        topicsList.append(word)
                        if len(topicsList) >= 5:
                            break
                result += getEventSummaryWordsStr(topicsList) + '等话题，'
            # 组织其他条件
            maxNum = resProgram['maxNum']
            result += '以每次查询最多' + str(maxNum) + '条推文的方式，'
            stime = resProgram['stime']
            etime = resProgram['etime']
            result += '采集了从' + stime + '到' + etime + '的推文数据，'
            allTweetNum = getAllTweetListLength(clusterTweetDict)
            result += '对其中与事件相关的' + str(allTweetNum) + '条推文进行了统计分析。'
            # print(result)
            client.close()
            return {'resCode': 1,
                    'resStr': '获取事件分析结果概述-方案描述数据成功',
                    'resObject': result,
                    'resList': []}
    except:
        return {'resCode': 0,
                'resStr': '事件分析结果概述-方案描述数据库查询失败',
                'resObject': '',
                'resList': []}

# 获取事件分析图表加载项数据
def getEventAnalysisConfigDataAction():
    try:
        client = getMongoClient()
        db = client['programs']
        config = db['eventAnalysis']
        configObject = dict(list(config.find())[0])
        resultObject = {'wordCloud': configObject['wordCloud'],
                        'mapHot': configObject['mapHot'],
                        'discussionTrend': configObject['discussionTrend'],
                        'levelPie': configObject['levelPie'],
                        'popularTweeter': configObject['popularTweeter'],
                        'timeTrack': configObject['timeTrack']}
        return {'resCode': 1,
                'resStr': '获取事件分析图表加载项数据成功',
                'resObject': resultObject,
                'resList': []}
    except:
        return {'resCode': 0,
                'resStr': '事件分析图表加载项数据库查询失败',
                'resObject': '',
                'resList': []}

# 修改事件分析图表加载项
def changeEventAnalysisAction(data):
    try:
        client = getMongoClient()
        db = client['programs']
        config = db['eventAnalysis']
        query = {}
        newValues = { "$set": data }
        config.update_one(query, newValues)
        return {'resCode': 1,
                'resStr': '修改事件分析图表加载项数据成功',
                'resObject': '',
                'resList': []}
    except:
        return {'resCode': 0,
                'resStr': '修改事件分析图表加载项数据失败',
                'resObject': '',
                'resList': []}

# 根据事件讨论走势数据，获取话题爆发时间节点list
def getEventTimePotList(discussionTrendXAxisData, discussionTrendYAxisData):
    discussionSum = 0
    for item in discussionTrendYAxisData:
        discussionSum += item
    discussionAve = discussionSum * 1.0 / len(discussionTrendYAxisData)
    timePots = list()
    maxPotSize = 8
    for index in range(len(discussionTrendYAxisData)):
        item = discussionTrendYAxisData[index]
        if item > discussionAve:
            timePots.append(discussionTrendXAxisData[index])
            if len(timePots) == maxPotSize:
                break
    return timePots

# 根据事件讨论走势数据，获取话题爆发时间节点结果串
def getEventTimePotStrWithDiscussionData(timePots):
    timePotStr = ''
    for i in range(len(timePots)):
        if i < len(timePots) - 1:
            timePotStr += '\"' + timePots[i] + '\"，'
        else:
            timePotStr += '\"' + timePots[i] + '\"'
    return timePotStr

# 获取事件实例中的时间起点和终点
def getEventTimeSE(clusterDbName):
    try:
        client = getMongoClient()
        db = client[clusterDbName]
        clusterResultCol = db['clusterResult']
        clusters = clusterResultCol.find()
        etime = '0000-00-00'
        stime = '9999-99-99'
        for cluster in clusters:
            mostPossibleTime = cluster['time_infer']['most_possible_time'][0:10]
            if mostPossibleTime < stime:
                stime = mostPossibleTime
            if mostPossibleTime > etime:
                etime = mostPossibleTime
        timeInfo = {'stime': stime, 'etime': etime}
        client.close()
        return {'resCode': 1,
                'resStr': '获取事件始末时间成功',
                'resObject': timeInfo,
                'resList': []}
    except:
        return {'resCode': 0,
                'resStr': '获取事件始末时间失败',
                'resObject': '',
                'resList': []}

# 根据给定的时间节点，找到最重要的一条推文
def getTweetWithTimePots(timePots, clusterDbName, clusterTweetDict):
    try:
        client = getMongoClient()
        db = client[clusterDbName]
        clusterResultCol = db['clusterResult']
        clusters = clusterResultCol.find()
        # 先获取各时间节点的全部tweet
        timeTweetsDict = dict()
        for cluster in clusters:
            mostPossibleTime = cluster['time_infer']['most_possible_time'][0:10]
            cluid = cluster['cluid']
            # 先判断该事件实例的可能时间是否在时间节点中
            if mostPossibleTime in timePots:
                # 取出和mostPossibleTime时间一致的推文
                tweetList = clusterTweetDict[cluid]
                for tweet in tweetList:
                    time = tweet['created_at'][0:10]
                    if time == mostPossibleTime:
                        if time in timeTweetsDict.keys():
                            timeTweetsDict[time].append(tweet)
                        else:
                            timeTweetsDict[time] = [tweet]
        # 针对timeTweetsDict 每个时间的tweetList，选出一条
        timeTweetsData = list()
        timeKeys = list(timeTweetsDict.keys())
        timeKeys.sort()
        for i in range(len(timeKeys)):
            time = timeKeys[i]
            bestTweet, tweetActionNums = getBestTweet(timeTweetsDict[time])
            text = bestTweet['standard_text']
            userName = bestTweet['user']['data_name']
            userHeadSrc = 'none'
            hm = bestTweet['created_at'][11:16]
            timeTweetsData.append({'userName': userName, 'userHead': userHeadSrc, 'text': text, 'tweetNums': tweetActionNums, 'time': {'ymd': time, 'hm': hm}})
        client.close()
        return {'resCode': 1,
                'resStr': '获取指定时间的推文成功',
                'resObject': '',
                'resList': timeTweetsData}
    except:
        return {'resCode': 0,
                'resStr': '获取指定时间的推文失败',
                'resObject': '',
                'resList': []}

# 获取指定方案的事件分析数据 -- 完整
def getEventAnalysisFullDataAction(pname, dbName):
    fullResult = dict()
    clusterDbName = 'cluster_' + dbName
    # 提前查询各cluster对应的tweetList，供后续统计使用
    clusterTweetDict = getClusterTweetListDict(clusterDbName)
    # 获取事件概述-方案描述部分数据  类型：字符串
    response = getEventSummaryProgramDataAction(pname, clusterTweetDict)
    if response['resCode'] == 1:
        eventSummaryProgramStr = response['resObject']
    else:
        return response
    # 获取词云数据  类型：list  [{name: , value}]
    response = getWordCloudDataAction(clusterDbName)
    if response['resCode'] == 1:
        wordCloudData = response['resList']
    else:
        return response
    # 获取热点地图数据  类型：dict  obj['addressInfo'] 字典 key-地区名 value-字典 {hot、geo}  obj['countryInfo'] list [[国家，热度总值]]
    response = getMapHotDataAction(clusterDbName)
    if response['resCode'] == 1:
        addressInfo = response['resObject']['addressInfo']
        countryInfo = response['resObject']['countryInfo']
        # 地区热度数据
        mapAddressData = convertMapAddressData(addressInfo, 4)
        # 国家热度数据
        mapCountryData = list()
        mapCountryYAxisData = list()
        for country in countryInfo:
            mapCountryData.append({'name': country[0], 'value': ToDecimal2F(country[1])})
            mapCountryYAxisData.append(country[0])
        mapCountryData.reverse()
        mapCountryYAxisData.reverse()
    else:
        return response
    # 获取事件讨论走势数据  类型：dict  key-时间  value-推特条数
    response = getDiscussionTrendDataAction(clusterDbName, clusterTweetDict)
    if response['resCode'] == 1:
        discussionTrendDict = response['resObject']
        discussionTrendXAxisData = list()
        discussionTrendYAxisData = list()
        orderedKeys = list(discussionTrendDict.keys())
        orderedKeys.sort()
        for key in orderedKeys:
            discussionTrendXAxisData.append(key)
            discussionTrendYAxisData.append(discussionTrendDict[key])
    else:
        return response
    # 获取事件等级统计数据  类型：dict  key-事件等级  value-事件数
    response = getEventLevelDataAction(clusterDbName)
    if response['resCode'] == 1:
        eventLevelDict = response['resObject']
        levelPieLegendData = list()
        levelPieData = list()
        for key in eventLevelDict.keys():
            levelPieLegendData.append(key)
            levelPieData.append({'name': key, 'value': eventLevelDict[key]})
    else:
        return response
    # 获取热门tweeter数据  类型：list-dict  [{userName, userHead, text, tweetNums}]
    response = getPopularTweeterDataAction(clusterDbName, clusterTweetDict)
    if response['resCode'] == 1:
        popularTweeterData = response['resList']
    else:
        return response
    # 整理事件概述-统计分析部分数据
    eventSummaryAnalysisStr = ''
    # 加入事件爆发时间节点信息
    timePots = getEventTimePotList(discussionTrendXAxisData, discussionTrendYAxisData)
    eventSummaryAnalysisStr += '该事件爆发的时间节点有' + getEventTimePotStrWithDiscussionData(timePots) + '等。'
    # 加入国家热度总值信息
    eventSummaryAnalysisStr += '该事件在\"' + mapCountryYAxisData[len(mapCountryYAxisData) - 1] + '\"国家产生的热度最高，'
    # 加入关键词信息
    eventSummaryAnalysisStr += '人们讨论最多的词汇是\"' + wordCloudData[0]['name'] + '\"。'
    # 加入事件热度爆发终点信息
    eventSummaryAnalysisStr += '在采集时间范围内，事件自' + timePots[len(timePots) - 1] + '后热度逐渐下降。'
    # 获取事件传播途径数据  时间起点、终点 + timePots
    response = getEventTimeSE(clusterDbName)
    if response['resCode'] == 1:
        # 获取事件的爆发节点与起始、终止时间节点
        eventSETime = response['resObject']
        eventStime = eventSETime['stime']
        eventEtime = eventSETime['etime']
        if eventStime not in timePots:
            timePots.append(eventStime)
        if eventEtime not in timePots:
            timePots.append(eventEtime)
        timePots.sort()
        # 根据各个时间节点，找出一条推文
        response = getTweetWithTimePots(timePots, clusterDbName, clusterTweetDict)
        if response['resCode'] == 1:
            timeTrackData = response['resList']
        else:
            return response
    else:
        return response
    # 组织完整数据
    fullResult['eventSummary'] = eventSummaryProgramStr + eventSummaryAnalysisStr
    fullResult['wordCloudData'] = wordCloudData
    fullResult['mapAddressData'] = mapAddressData
    fullResult['mapCountryData'] = mapCountryData
    fullResult['mapCountryYAxisData'] = mapCountryYAxisData
    fullResult['discussionTrendXAxisData'] = discussionTrendXAxisData
    fullResult['discussionTrendYAxisData'] = discussionTrendYAxisData
    fullResult['levelPieLegendData'] = levelPieLegendData
    fullResult['levelPieData'] = levelPieData
    fullResult['popularTweeterData'] = popularTweeterData
    fullResult['timeTrackData'] = timeTrackData
    return {'resCode': 1,
            'resStr': '获取事件分析结果数据成功',
            'resObject': fullResult,
            'resList': []}


# 根据方案名查询图表预存数据库
def queryVisibleDataByPname(pname):
    try:
        client = getMongoClient()
        db = client['programs']
        collection = db['visibleData']
        documents = collection.find()
        for document in documents:
            if document['pname'] == pname:
                client.close()
                return {'resCode': 1,
                        'resStr': '方案' + pname + '预存图表数据存在！',
                        'resObject': document['chartData'],
                        'resList': []}
        # 没有预存数据，需要根据 数据库名查询生成图表数据
        program = db['programs']
        query = {'pname': pname}
        dbName = list(program.find(query))[0]['dbName']
        client.close()
        return {'resCode': 0,
                'resStr': '方案' + pname + '预存图表数据不存在！',
                'resObject': dbName,
                'resList': []}
    except:
        return {'resCode': -1,
                'resStr': '查询方案预存数据时出错！',
                'resObject': '',
                'resList': []}

# 预存指定方案的图表数据
def storeVisibleData(pname, chartData):
    try:
        client = getMongoClient()
        db = client['programs']
        collection = db['visibleData']
        data = {'pname': pname, 'chartData': chartData}
        collection.insert_one(data)
        return {'resCode': 1,
                'resStr': '预存方案' + pname + '图表数据成功！',
                'resObject': '',
                'resList': []}
    except:
        return {'resCode': 0,
                'resStr': '预存方案' + pname + '图表数据失败！',
                'resObject': '',
                'resList': []}

# 查询每个cluster对应的tweetList，组装成dict
def getClusterTweetListDict(clusterDbName):
    client = getMongoClient()
    db = client[clusterDbName]
    clusterResultCol = db['clusterResult']
    clusterTweetCol = db['clusterTweet']
    clusters = clusterResultCol.find()
    clusterTweetDict = dict()
    for cluster in clusters:
        cluid = cluster['cluid']
        query = {'cluid': cluid}
        tweetObjList = clusterTweetCol.find(query)
        clusterTweetDict[cluid] = list()
        for tweetObj in tweetObjList:
            clusterTweetDict[cluid].append(tweetObj['tweet'])
    return clusterTweetDict

if __name__ == '__main__':
    # getTweetWithTimePots(['2016-02-26'], 'cluster_natural_disaster')
    client = getMongoClient()
    db = client['cluster_2019HKProtest']
    clusterTweetCol = db['clusterTweet']
    tweetObjList = clusterTweetCol.find()
    tweetTimeDict = dict()
    for tweetObj in tweetObjList:
        tweet = tweetObj['tweet']
        time = tweet['created_at'][0:10]
        if time in tweetTimeDict.keys():
            tweetTimeDict[time] += 1
        else:
            tweetTimeDict[time] = 1
    sortedList = sorted(tweetTimeDict.items(), key=lambda x: x[1], reverse=True)
    for item in sortedList:
        print(item[0] + ':' + str(item[1]))