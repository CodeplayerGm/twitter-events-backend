from time import strftime,strptime


# 关键词表达式转换成list
def getProgramWordsListFromExp(exp):
    exp = exp[1: len(exp) - 1]
    return exp.split('|')

# 关键词list转换为事件描述字符串
def getEventSummaryWordsStr(wordList):
    wordStr = ''
    for i in range(len(wordList)):
        wordStr += '\"' + wordList[i] + '\"'
        if i != len(wordList) - 1:
            wordStr += '、'
    return wordStr

# 给定clusterTweetDict，查询聚类结果数据库的推文数量
def getAllTweetListLength(clusterTweetDict):
    length = 0
    for key in clusterTweetDict.keys():
        length += len(clusterTweetDict[key])
    return length

# 保留两位小数
def ToDecimal2F(f):
    fs = ('%.2f' % f)
    nf = float(fs)
    return nf

# 把UTC 格式的字符串转换成 精确到天的时间字符串
def timeConvertYMD(src, timeZone):
    time = strftime("%Y-%m-%d", strptime(src, '%a %b %d %H:%M:%S ' + timeZone + ' %Y'))
    return time

def timeConvertYMDHMS(src, timeZone):
    time = strftime("%Y-%m-%d %H:%M:%S", strptime(src, '%a %b %d %H:%M:%S ' + timeZone + ' %Y'))
    return time

# 根据参数，设置热点地区的地图焦点大小，参数：maxPercent最大点占总点数百分比
#                                             maxSize最大点大小
#                                             minPercent最小点占总点数百分比
#                                             minSize最小点大小
#                                             resList最多前100个地点数据
def setHotMapPointSizeValue(maxPercent, maxSize, minPercent, minSize, resList):
    standardResList = resList
    # 先统计各个热度值的点数量
    sum = len(resList)
    maxNum = int(sum * maxPercent)
    minNum = int(sum * minPercent)
    hotNumDict = dict()
    for res in resList:
        hot = res['value'][2]
        if hot in hotNumDict.keys():
            hotNumDict[hot] += 1
        else:
            hotNumDict[hot] = 1
    # 按key排序，从大到小
    sortedList = sorted(hotNumDict.items(), key=lambda x: x[0], reverse=True)
    # 得到最大、最小点阈值
    maxThrehold = sortedList[maxNum - 1][0]
    minThrehold = sortedList[sum - minNum][0]
    # 中间大小的点换算系数
    midRate = (maxSize - minSize) / (maxThrehold - minThrehold)
    # 重新规划各个点的大小
    for res in standardResList:
        hot = res['value'][2]
        if hot >= maxThrehold:
            res['value'][2] = maxSize
        elif hot <= minThrehold:
            res['value'][2] = minSize
        else:
            res['value'][2] = minSize + ToDecimal2F((hot - minThrehold) * midRate)
    # print('max、min num:' + str(maxNum) + ',' + str(minNum))
    # print('maxThrehold、minThrehold:' + str(maxThrehold) + ',' + str(minThrehold))
    return standardResList


if __name__ == '__main__':
    # from dbConfig import getMongoClient
    # myclient = getMongoClient()
    # srcdb = myclient['hongkong_protest']
    # datacol = srcdb['datasetFull']
    # documents = datacol.find()
    #
    # # 每2000条写入一个集合
    # loopCount = 0
    # colIndex = 1
    # tempdbData = dict()
    # loopList = list()
    # for doc in documents:
    #     loopList.append(doc)
    #     loopCount += 1
    #     if loopCount == 2000:
    #         tempdbData[colIndex] = loopList
    #         loopList = []
    #         loopCount = 0
    #         colIndex += 1
    # if loopCount != 0:
    #     tempdbData[colIndex] = loopList
    #
    # # 写入temp db
    # tempdb = myclient['temp']
    # for key in tempdbData.keys():
    #     newcol = tempdb['dataset' + str(key)]
    #     for d in tempdbData[key]:
    #         newcol.insert_one({'tweet': d['tweet'], 'id': d['id'], 'q': d['q']})

    from dbConfig import getMongoClient
    import os

    myclient = getMongoClient()
    mydb = myclient['temp']
    colnames = mydb.collection_names()
    for cname in colnames:
        cmd = 'mongoexport -d temp -c ' + cname + ' -o ' + 'D:/' + cname + '.json'
        os.system(cmd)

