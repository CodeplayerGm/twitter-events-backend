from flask import Flask, jsonify,request
from flask_cors import CORS
from programs.programAction import getAllProgramsAction, addProgramAction, deleteProgramAction, startProgramAction

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
    response = startProgramAction(pname)
    # print(programForm)
    return jsonify(response)

if __name__ == '__main__':
    app.run()
