from dbConfig import getMongoClient
from spider.commonSpider import doTweetSearchOnce
import re
from datetime import datetime
from time import sleep

# 关键词组列表转换为字符串
def getProgramKeyWordsStr(keyWords):
    kwStr = ''
    for group in keyWords:
        kwStr += group['kname'] + ' : ' + group['exp'] + '; '
    return kwStr

# x组关键词排列组合
# 参数：多组关键词列表，起点组（包含），终点组（包含），当前遍历中的一个组合list，最终结果list
def getProgramKeyWordsCombination(keywords, curG, maxG, curList, resultList):
    curGroup = getProgramWordsListFromExp(keywords[curG]['exp'])
    for word in curGroup:
        nextList = curList.copy()
        nextList.append(word)
        if curG == maxG:
            resultList.append(nextList)
        else:
            getProgramKeyWordsCombination(keywords, curG + 1, maxG, nextList, resultList)
    return resultList

# 通过关键词组、时间、过滤词、话题组织查询语句列表
def getProgramSearchSentences(keywords, stime, etime, ignorewords, ignoreStr, topics, topicsStr):
    # 组织查询语句：采取最后一组或几组不参与排列组合，直接全部带入，适当减少查询次数
    groupNum = len(keywords)
    # 排列组合的层数
    combinationNum = groupNum - 1
    lastKeyWordsGroup = keywords[groupNum - 1]
    # 前n-1组关键词进行排列组合
    combinationList = getProgramKeyWordsCombination(keywords, 0, combinationNum - 1, [], [])
    searchList = list()
    for combination in combinationList:
        qsentence = ''
        for word in combination:
            qsentence += '(' + word + ') '
        # 添加完组合关键词，再添加关键词组末尾未参与排列组合的关键词组
        qsentence += re.sub('[|]', ' OR ', lastKeyWordsGroup['exp']) + ' '
        # 如果有过滤词，添加过滤词
        if ignorewords:
            qsentence += ignoreStr
        # 如果有话题：添加话题
        if topics:
            qsentence += topicsStr
        # 添加起始时间
        qsentence += 'since:' + stime + ' until:' + etime
        searchList.append(qsentence)
    return searchList

# 前端话题表达式转换成查询语句
def getProgramTopicsSearchStr(exp):
    words = getProgramWordsListFromExp(exp)
    res = ''
    for i in range(len(words)):
        if i < len(words) - 1:
            res += '#' + words[i] + ' OR '
        else:
            res += '#' + words[i] + ' '
    return res

# 前端过滤词表达式转换成查询语句
def getProgramIgnoreWordsSearchStr(exp):
    words = getProgramWordsListFromExp(exp)
    res = ''
    for i in range(len(words)):
        res += '-' + words[i] + ' '
    return res

# 前端关键词表达式转换成list
def getProgramWordsListFromExp(exp):
    exp = exp[1: len(exp) - 1]
    return exp.split('|')

# mongo方案列表转换成前端展示列表
def getProgramTableList(mongoList):
    resultList = list()
    pid = 1
    for pi in mongoList:
        tableItem = dict()
        tableItem['id'] = pid
        tableItem['pname'] = pi['pname']
        tableItem['desc'] = pi['desc']
        tableItem['stime'] = pi['stime']
        tableItem['etime'] = pi['etime']
        tableItem['keywords'] = getProgramKeyWordsStr(pi['keywords'])
        tableItem['ignorewords'] = pi['ignorewords']
        tableItem['topics'] = pi['topics']
        tableItem['status'] = pi['status']
        resultList.append(tableItem)
        pid += 1
    return resultList

# 查询全部方案列表
def getAllProgramsAction():
    try:
        client = getMongoClient()
        programsDb = client['programs']
        programsCol = programsDb['programs']
        resultList = getProgramTableList(list(programsCol.find()))
        client.close()
        return {
            'resCode': 1,
            'resStr': '查询数据库成功',
            'resObject': '',
            'resList': resultList}
    except:
        return {
            'resCode': 0,
            'resStr': '查询数据库失败',
            'resObject': '',
            'resList': []}

# 添加新方案
def addProgramAction(programForm):
    # 整理参数
    pname = programForm['pname']
    desc = programForm['desc']
    dbName = programForm['dbName']
    maxNum = programForm['maxNum']
    stime = programForm['timeRange'][0]
    etime = programForm['timeRange'][1]
    keywords = programForm['keywords']
    ignorewords = programForm['ignorewords']
    topics = programForm['topics']
    # 数据库操作
    client = getMongoClient()
    programsDb = client['programs']
    programsCol = programsDb['programs']
    if programsCol.find_one({'pname': pname}) is None:  # 查看记录是否已存在，若不存在则放入数据库
        try:
            programData = {'pname': pname, 'desc': desc, 'dbName': dbName, 'maxNum': maxNum, 'stime': stime, 'etime': etime,
                     'keywords': keywords, 'ignorewords': ignorewords, 'topics': topics, 'status': '无数据'}
            programsCol.insert_one(programData)
            client.close()
            return {
                'resCode': 1,
                'resStr': '添加新方案成功',
                'resObject': '',
                'resList': [] }
        except:
            client.close()
            return {
                'resCode': 0,
                'resStr': '插入记录时发生错误',
                'resObject': '',
                'resList': []}
    else:
        client.close()
        return {
            'resCode': -1,
            'resStr': '记录已存在',
            'resObject': '',
            'resList': [] }

# 按方案名删除方案
def deleteProgramAction(pname):
    client = getMongoClient()
    programsDb = client['programs']
    programsCol = programsDb['programs']
    deleteQuery = {'pname': pname}
    try:
        programsCol.delete_one(deleteQuery)
        client.close()
        return {
            'resCode': 1,
            'resStr': '删除方案：' + pname + '成功！',
            'resObject': '',
            'resList': []}
    except:
        client.close()
        return {
            'resCode': 0,
            'resStr': '删除方案出错!',
            'resObject': '',
            'resList': []}

# 启动方案数据爬取
def startProgramAction(pname):
    client = getMongoClient()
    programsDb = client['programs']
    programsCol = programsDb['programs']
    collectionLog = programsDb['collectionLog']
    # 先根据方案名取出方案具体信息
    query = {'pname': pname}
    program = programsCol.find_one(query)
    dbName = program['dbName']
    stime = program['stime']
    etime = program['etime']
    maxNum = program['maxNum']
    keywords = program['keywords']
    ignorewords = program['ignorewords']
    ignoreStr = getProgramIgnoreWordsSearchStr(ignorewords)
    topics = program['topics']
    topicsStr = getProgramTopicsSearchStr(topics)
    status = program['status']
    # 创建数据库和集合
    db = client[dbName]
    # 得到查询语句
    searchList = getProgramSearchSentences(keywords, stime, etime, ignorewords, ignoreStr, topics, topicsStr)
    # 依次执行爬取操作
    for q in searchList:
        print(q)
        qResult = doTweetSearchOnce(q, maxNum, db)
        timeNow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        collectionLog.insert_one({'pname': pname, 'time': timeNow, 'q': q,
                                  'tweetsNum': qResult['tweetsNum'], 'insertNum': qResult['insertNum']})
    # 更新方案状态
    if status == '无数据':
        newStatus= {"$set": {"status": "已爬取"}}
        programsCol.update_one(query, newStatus)
    elif status == '已爬取':
        newStatus = {"$set": {"status": "已更新"}}
        programsCol.update_one(query, newStatus)
    client.close()
    return {}
    # for i in range(len(keywords) - 1):
    #     exp = keywords[i]['exp']
    # try:
    #     client.close()
    #     return {
    #         'resCode': 1,
    #         'resStr': '删除方案：' + pname + '成功！',
    #         'resObject': '',
    #         'resList': []}
    # except:
    #     client.close()
    #     return {
    #         'resCode': 0,
    #         'resStr': '删除方案出错!',
    #         'resObject': '',
    #         'resList': []}


if __name__ == '__main__':
    # keywords = [
    #     [1, 2, 3],
    #     ['a', 'b', 'c', 'd'],
    #     ['protest', 'protests', 'protesters', 'citizens', 'march', 'marched', 'police', 'government', 'officers', 'lam',
    #      'carrie', 'political', 'force', 'violence', 'riot', 'mainland', 'independent', 'lawmakers', 'revolution'],
    #     ['+', '-', '*', '/']
    # ]
    # res = getProgramKeyWordsCombination(keywords, 0, 2, [], [])
    # for item in res:
    #     print(item)
    print(getProgramTopicsSearchStr('(riot|violence|mainland)'))