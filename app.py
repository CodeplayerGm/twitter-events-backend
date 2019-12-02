from flask import Flask, jsonify,request
from flask_cors import CORS
from programs.programAction import getAllProgramsAction, addProgramAction, deleteProgramAction, startProgramAction
from eventVisible.eventVisibleAction import getEventAnalysisConfigDataAction, changeEventAnalysisAction, getEventAnalysisFullDataAction, \
    queryVisibleDataByPname, storeVisibleData

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/')
def hello_world():
    return 'Hello World!'

# 查询全部方案
@app.route('/api/getAllPrograms')
def getAllPrograms():
    response = getAllProgramsAction()
    return jsonify(response)

# 添加方案
@app.route('/api/addProgram', methods=["POST"])
def addProgram():
    programForm = request.get_json(silent=True)
    response = addProgramAction(programForm['data'])
    # print(programForm)
    return jsonify(response)

# 删除方案
@app.route('/api/deleteProgram', methods=["POST"])
def deleteProgram():
    params = request.get_json(silent=True)
    pname = params['data']
    response = deleteProgramAction(pname)
    # print(programForm)
    return jsonify(response)

# 启动方案
@app.route('/api/startProgram', methods=["POST"])
def startProgram():
    params = request.get_json(silent=True)
    pname = params['data']
    num = params['num']
    response = startProgramAction(pname, num)
    # print(programForm)
    return jsonify(response)

# 获取事件分析图表加载项数据
@app.route('/api/getEventAnalysisConfigData', methods=["GET"])
def getEventAnalysisConfigData():
    # params = request.get_json(silent=True)
    # pname = params['data']
    response = getEventAnalysisConfigDataAction()
    # print(programForm)
    return jsonify(response)

# 修改事件分析图表加载项
@app.route('/api/changeEventAnalysis', methods=["POST"])
def changeEventAnalysis():
    params = request.get_json(silent=True)
    config = params['data']
    response = changeEventAnalysisAction(config)
    # print(programForm)
    return jsonify(response)

# 获取指定方案的事件分析数据
@app.route('/api/getEventAnalysisFullData', methods=["POST"])
def getEventAnalysisFullData():
    params = request.get_json(silent=True)
    pname = params['data']
    # 先查看是否有预存的图表数据，如果有，直接返回，否则重新生成数据，并预存
    queryResponse = queryVisibleDataByPname(pname)
    # 有预存数据，根据当前图表加载项设置，组织数据返回
    if queryResponse['resCode'] == 1:
        getConfigResponse = getEventAnalysisConfigDataAction()
        # 查询当前系统的图表加载项配置
        if getConfigResponse['resCode'] == 1:
            fullData = queryResponse['resObject']
            config = getConfigResponse['resObject']
            currentData = dict()
            currentData['eventSummary'] = fullData['eventSummary']
            currentData['config'] = config
            if config['wordCloud']:
                currentData['wordCloudData'] = fullData['wordCloudData']
            if config['mapHot']:
                currentData['mapAddressData'] = fullData['mapAddressData']
                currentData['mapCountryData'] = fullData['mapCountryData']
                currentData['mapCountryYAxisData'] = fullData['mapCountryYAxisData']
            if config['discussionTrend']:
                currentData['discussionTrendXAxisData'] = fullData['discussionTrendXAxisData']
                currentData['discussionTrendYAxisData'] = fullData['discussionTrendYAxisData']
            if config['levelPie']:
                currentData['levelPieLegendData'] = fullData['levelPieLegendData']
                currentData['levelPieData'] = fullData['levelPieData']
            if config['popularTweeter']:
                currentData['popularTweeterData'] = fullData['popularTweeterData']
            if config['timeTrack']:
                currentData['timeTrackData'] = fullData['timeTrackData']
            backResult = {'resCode': 1,
                         'resStr': '获取预存事件分析结果数据成功',
                         'resObject': currentData,
                         'resList': []}
            return jsonify(backResult)
        else:
            return jsonify(getConfigResponse)
    # 没有预存数据，组织数据
    elif queryResponse['resCode'] == 0:
        dbName = queryResponse['resObject']
        fullDataResponse = getEventAnalysisFullDataAction(pname, dbName)
        # 组织数据成功，预存数据，并返回结果
        if fullDataResponse['resCode'] == 1:
            fullData = fullDataResponse['resObject']
            currentData = dict()
            # 查询图表加载项配置信息
            response = getEventAnalysisConfigDataAction()
            if response['resCode'] == 1:
                config = response['resObject']
                currentData['config'] = config
                currentData['eventSummary'] = fullData['eventSummary']
                if config['wordCloud']:
                    currentData['wordCloudData'] = fullData['wordCloudData']
                if config['mapHot']:
                    currentData['mapAddressData'] = fullData['mapAddressData']
                    currentData['mapCountryData'] = fullData['mapCountryData']
                    currentData['mapCountryYAxisData'] = fullData['mapCountryYAxisData']
                if config['discussionTrend']:
                    currentData['discussionTrendXAxisData'] = fullData['discussionTrendXAxisData']
                    currentData['discussionTrendYAxisData'] = fullData['discussionTrendYAxisData']
                if config['levelPie']:
                    currentData['levelPieLegendData'] = fullData['levelPieLegendData']
                    currentData['levelPieData'] = fullData['levelPieData']
                if config['popularTweeter']:
                    currentData['popularTweeterData'] = fullData['popularTweeterData']
                if config['timeTrack']:
                    currentData['timeTrackData'] = fullData['timeTrackData']
                storeResponse = storeVisibleData(pname, fullData)
                # 预存成功，直接返回结果
                if storeResponse['resCode'] == 1:
                    backResult = {'resCode': 1,
                                  'resStr': '获取事件分析结果数据成功',
                                  'resObject': currentData,
                                  'resList': []}
                    return jsonify(backResult)
                # 预存出错，返回报错信息
                else:
                    return jsonify(storeResponse)
            else:
                return jsonify(response)
        # 组织数据出错，返回报错信息
        else:
            return jsonify(fullDataResponse)


if __name__ == '__main__':
    app.run()
