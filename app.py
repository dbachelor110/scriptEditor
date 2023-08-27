import json
import os
import webbrowser
from functools import wraps
from src.backend import api
from flask import Flask, jsonify, render_template, redirect, request
import webview
import random

admin = {
    'logWindowFlag':False,
    'ver':"?ver={:0>4d}".format(int(random.random()*10000)),
}

def riseLogWindowFlag():
    admin['logWindowFlag'] = True

def cancelLogWindowFlag():
    admin['logWindowFlag'] = False

# 取得父層路徑的方法，輸入 time 可以向上尋找多次
def EXdir(file,time=1):
    temp = file
    for i in range(time):
        temp = os.path.dirname(temp)
    return temp

gui_dir = os.path.join(EXdir(__file__,3), 'gui')   # development path
frontend_dir = os.path.join(EXdir(__file__,2), 'frontend')   # development path

if not os.path.exists(gui_dir):  # frozen executable path
    gui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gui')

server = Flask(__name__, static_folder=gui_dir, template_folder=gui_dir,static_url_path="/")
# server.config['HOST'] = '192.168.17.108'

def verify_token(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        data = json.loads(request.data)
        token = data.get('token')
        if token == webview.token:
            return function(*args, **kwargs)
        else:
            raise Exception('Authentication error')

    return wrapper


@server.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'max-age: 6000'
    return response


@server.route('/')
def landing():
    """
    取得初始設定資訊
    """
    viewText = api.landing()
    
    # ver = "?ver{:0>4d}".format(int(random.random()*10000))
    # 以下是根據資料類型分類，建議將分類直接寫入資料庫，可省許多工。
    setInformation = {'path':{},'userInformation':{},'elementLocator':{},'driverSet':{},'undefined':{}}
    setItem = ''
    setItemName = {
    'input_path':'Input  Path',
    'error_path':'Error  Path',
    'chrome_path':'Chrome Path',
    'chromedriver_path':'Driver Path',
    'auto_update_driver':{'name1':'Driver Updata','name0':'Use Chromium'},
    'headless':{'name1':'Headless','name0':'Head'},
    'domain':'domain',
    'url':'url',
    'username':'username',
    'password':'password',
    'username_locator':'username',
    'password_locator':'password',
    'submit_locator':'submit'
    }
    for i in setItemName.keys():

        def makeSetData(name,value):
            DataDict = {
                'name': name,
                'value': value
            }
            return DataDict


        # 設定變數 setItemtype 傳遞 config type
        setItemtype = -1 # 0 = userInformation, 1 = path, 2 = elementLocator, 3 = driverSet, -1 = undefined

        # 取得 key 對應的 value，若失敗，則value為字串 undefined
        value = 'undefined'
        try:
            value = viewText['getConfig'][i]
        except:
            pass
        
        # 對 key 與 value 字串資料解析，以判斷 setItemtype
        if i.find('path') != -1:
            setInformation['path'][i]=makeSetData(setItemName[i],value)
        elif i.find('locator') != -1:
            setItemtype = 2
            setInformation['elementLocator'][i]=makeSetData(setItemName[i],value)
        elif len(value) == 1:
            setItemtype = 3
            setInformation['driverSet'][i]=makeSetData(setItemName[i],value)
        else:
            setItemtype = 0
            setInformation['userInformation'][i]=makeSetData(setItemName[i],value)
        
    setItem += render_template('pathSet.html',setInformation = setInformation)
    scriptList = api.getScriptList()
    testItem = render_template('fileSelecter.html',scriptList=scriptList)
    ver=admin['ver']
        
    return render_template('setting.html', token=webview.token,viewText=viewText,setItem=setItem, testItem = testItem, ver=ver)

@server.route('/logWindow')
def landingLogWindow():
    return render_template('logWindow.html', token=webview.token)


@server.route('/init', methods=['POST']) #初始化，目前沒有放東西在這裡
@verify_token
def initialize():
    """
    Perform heavy-lifting initialization asynchronously.
    :return:
    """
    can_start = api.initialize()

    if can_start:
        response = {
            'status': 'ok',
        }
    else:
        response = {'status': 'error'}

    return jsonify(response)


@server.route('/choose/path', methods=['POST'])
@verify_token
def choose_path():
    """
    Invoke a folder selection dialog here
    :return:
    """
    dirs = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
    if dirs and len(dirs) > 0:
        directory = dirs[0]
        if isinstance(directory, bytes):
            directory = directory.decode('utf-8')

        response = {'status': 'ok', 'directory': directory}
    else:
        response = {'status': 'cancel'}

    return jsonify(response)


@server.route('/fullscreen', methods=['POST'])
@verify_token
def fullscreen():
    webview.windows[0].toggle_fullscreen()
    return jsonify({})


@server.route('/open-url', methods=['POST'])
@verify_token
def open_url():
    url = request.json['url']
    webbrowser.open_new_tab(url)

    return jsonify({})


@server.route('/do/stuff', methods=['POST'])
@verify_token
def do_stuff():
    result = api.do_stuff()

    if result:
        response = {'status': 'ok', 'result': result}
    else:
        response = {'status': 'error'}

    return jsonify(response)


@server.route('/do/getConfig', methods=['POST'])
@verify_token
def getConfig():
    result = api.getConfig()

    if result:
        response = {'status': 'ok', 'result': result}
    else:
        response = {'status': 'error'}

    return jsonify(response)


@server.route('/do/setConfig', methods=['POST'])
@verify_token
def setConfig():
    '''接受一個 key ，更新 key 對應的 path 並從 result 回傳
    '''
    typeList = ['path', 'elementLocator', 'driverSet', 'userInformation']
    typeCode = typeList.index(request.json['configType'])
    key = request.json['key']
    value = request.json['value']
    if typeCode == 0:
        
        path = api.config.setPath(key)
        if path != None:
            result={
                'key':key,
                'value':path
            }
            response = {'status': 'ok', 'result': result}
        else:
            response = {'status': 'error'}
    elif typeCode == 1:
        locator = api.config.setElementLocator(key)
        if locator != None:
            result={
                'key':key,
                'value':locator
            }
            response = {'status': 'ok', 'result': result}
        else:
            response = {'status': 'error'}

    elif typeCode == 2:
        setDriver = api.config.setDriver(key)
        if setDriver != None:
            result={
                'key':key,
                'value':setDriver
            }
            response = {'status': 'ok', 'result': result}
        else:
            response = {'status': 'error'}
    
    elif typeCode == 3:
        userInformation = api.config.setUserInformation(key,value)
        if userInformation != None:
            result={
                'key':key,
                'value':userInformation
            }
            response = {'status': 'ok', 'result': result}
        else:
            response = {'status': 'error'}
        
    return jsonify(response)

@server.route('/do/upDataScriptList', methods=['POST'])
@verify_token
def upDataScriptList():
    '''回傳根據當前 Config 資料所對應到的 scriptList'''
    try:
        result = api.getScriptList()
        status = 'ok'
        response = {'status': status, 'result': result}

    except:
        response = {'status': 'error'}

    return jsonify(response)

@server.route('/do/test', methods=['POST'])
@verify_token
def testStart():
    '''根據 scriptSelectionList ，開始測試'''
    try:
        scriptList = request.json['scriptSelection']
        if not admin['logWindowFlag']:
            riseLogWindowFlag()
            logWindow = webview.create_window('logView',f'{request.url_root}logWindow',width=600,resizable=False)
            logWindow.events.closed += cancelLogWindowFlag
        api.test(scriptList)
        response = {'status': 'ok'}

    except:
        response = {'status': 'error'}

    return jsonify(response)

@server.route('/do/regression', methods=['POST'])
@verify_token
def regression():
    '''根據 scriptSelectionList 與 timeString ，開始測試'''
    try:
        scriptList = request.json['scriptSelection']
        timeString = request.json['timeString']
        api.setRegression(scriptList,timeString)
        response = {'status': 'ok'}

    except:
        response = {'status': 'error'}

    return jsonify(response)

@server.route('/ask/getTestWindowFlag', methods=['POST'])
@verify_token
def getTestWindowFlag():
    '''取得 getTestWindowFlag '''
    try:
        result = admin['logWindowFlag']
        response = {'status': 'ok', 'result': result}

    except:
        response = {'status': 'error'}

    return jsonify(response)

@server.route('/ask/getTestingFlag', methods=['POST'])
@verify_token
def getTestingFlag():
    '''取得 getTestingFlag '''
    try:
        result = api.getTestingFlag()
        response = {'status': 'ok', 'result': result}

    except:
        response = {'status': 'error'}

    return jsonify(response)

@server.route('/ask/getLogText', methods=['POST'])
@verify_token
def getLogText():
    '''從 log_queue 拿走現有的所有 logText ，回傳到前端'''
    response = {'status': 'error'}
    print('Get ask')
    if not api.core.log_queue.empty():
        logList = []
        while not api.core.log_queue.empty():
            logList.append(api.core.log_queue.get())
        result = logList
        print(result)
        response = {'status': 'ok', 'result': result}

    return jsonify(response)

@server.route('/ask/readScriptByName', methods=['POST'])
@verify_token
def readScriptByName():
    '''根據 Script Name ，以 json 形式回傳對應的 dict
    
    response.result = dict'''
    ScriptName = request.json['ScriptName']
    # print('Get ask')
    try:
        result = api.readScriptByName(ScriptName)
        response = {'status': 'ok', 'result': result}
    except:
        response = {'status': 'error'}

    return jsonify(response)

@server.route('/do/saveScript', methods=['POST'])
@verify_token
def saveScript():
    '''將收到的 script 儲存至資料庫（現以 excel 形式儲存）'''
    ScriptName = request.json['ScriptName']
    ScriptActions = request.json['ScriptActions']
    try:
        if api.saveScript(ScriptName,ScriptActions):
            status = 'ok'
            response = {'status': status}
        else:
            response = {'status': 'error'}

    except:
        response = {'status': 'error'}

    return jsonify(response)


    
if __name__ == '__main__':
    server.run(host='0.0.0.0',processes=1)