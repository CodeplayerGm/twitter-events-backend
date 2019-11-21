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

# 给定mongoClient，查询聚类结果数据库的推文数量
def getAllTweetListLength(client):
    db = client['cluster_demo']
    cNameList = db.collection_names()
    length = 0
    for cName in cNameList:
        # 取每个事件簇
        collection = db[cName]
        # 取全部子事件
        subEvents = collection.find()
        for subEvent in subEvents:
            length += len(subEvent['tweet_list'])
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

if __name__ == '__main__':
    # ToDecimal2F(1253.1)
    from dbConfig import getMongoClient
    myclient = getMongoClient()
    srcdb = myclient['hongkong_protest']
    datasetcol = srcdb['dataset']
    documents = datasetcol.find()

    locData = dict()
    for doc in documents:
        q = doc['q']
        location = q[q.index('(') + 1 : q.index(')')].replace(' ', '')
        if location not in locData.keys():
            locData[location] = [doc]
        else:
            locData[location].append(doc)

    i = 1
    tempdb = myclient['temp']
    for key in locData.keys():
        print(str(i) + ' ---------------------------------------- location:' + key + ' ' + str(len(locData[key])))
        i += 1
        newcol = tempdb[key]
        for d in locData[key]:
            newcol.insert_one({'tweet': d['tweet'], 'id': d['id'], 'q': d['q']})
    # tempdb = myclient['temp']

    from dbConfig import getMongoClient
    import os

    myclient = getMongoClient()
    mydb = myclient['temp']
    colnames = mydb.collection_names()
    for cname in colnames:
        cmd = 'mongoexport -d temp -c ' + cname + ' -o ' + 'D:/' + cname + '.json'
        os.system(cmd)

