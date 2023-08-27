"""
Application stub
"""
import webview
import core
import webElementSelect
from qasJenkins import jenkins
from threading import Thread

# 宣告一個字典用來暫存資料，減少與資料庫的溝通次數。
temp = {
    'flag':{
        'testing':False,
        'testWindow':False, 
        },
}

def textSave(text):
    with open(f"{core.locoalFolderPath()}/save.txt","+a")as save:
        save.write(f"{text}\n")

def initialize():
    # perform heavy stuff here
    return True

def landing():
    viewText={
        'setBtn' : '...',
        'title' : '宏燁資訊自動化測試',
        'getConfig' : getConfig(),
    }
    return viewText

def do_stuff():
    # do whatever you need to do
    response = 'This is response from Python backend'
    return response

def getConfig():
    '''從資料庫(目前以 config.txt 代替)  取得 Dict
    '''
    temp['config']=core.getParameter()
    
    return temp['config']

def readConfig():
    '''不經過資料庫，直接回傳 temp['config']
    '''
    return temp['config']
def showPath(path:str):
    pathList = path.split()
    pathShow ='...'
    if len(pathList)>2:
        pathShow += f'/{pathList[-2]}/{pathList[-1]}'
    else:
        for i in pathList:
            pathShow += f'/{i}'
    return pathShow

def upDataConfig(key,value=None)->str:
    '''輸入 key ，用 value 更新對應的 temp['config'] ，並更新資料庫(目前以 config.txt 代替)中的資料
        若 value == None ，則不更新

    return:
        key 對應的 Config 值 --> temp['config'][key]
    '''
    if value != None:
        temp['config'][key] = value
        core.Parameter_save(temp['config'])

    return temp['config'][key]




class config:
    def setPath(key):
        '''輸入 key ，更新對應的 path 並回傳 path 字串

        若更新失敗則回傳 None
        '''
        path = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
        if path and len(path) > 0:
            path = path[0]
            if isinstance(path, bytes):
                path = path.decode('utf-8')
            if path.find('\\')!=-1:
                pathList = path.split('\\')
                path = ''
                for i in pathList:
                    path += f'{i}/'
                path = path[:-1]
        else:
            path = None

        upDataConfig(key,path)
        return path
    
    def setDriver(key):
        '''輸入 key ，更新對應的 driver set 並回傳 0 or 1
        '''
        driverSet = int(getConfig()[key])
        if driverSet == 0:
            driverSet = 1
        elif driverSet == 1:
            driverSet = 0
        else:
            driverSet = None

        upDataConfig(key,driverSet)
        return driverSet
    
    def setUserInformation(key,userInformation):
        '''輸入 key ，更新對應的 userInformation 並回傳 userInformation
        '''
        readConfig()[key] = str(userInformation)
        upDataConfig(key,userInformation)
        return userInformation
    
    def setElementLocator(key):
        '''輸入 key ，更新對應的 elementLocator 並回傳 elementLocator
        '''
        Locator = webElementSelect.getXPath(temp['config']['url'])
        elementLocator = ('xpath', Locator)
        readConfig()[key] = ('xpath', elementLocator)
        upDataConfig(key,elementLocator)
        return str(elementLocator)
        
    

def stringToLine(string:str):
    temp = ''
    string = string.split('\n')
    for i in string:
        temp += i
    string = temp
    return string

def getScriptList():
    '''呼叫 readConfig()["input_path"]，取得 scriptList'''
    scriptList = core.getExcelList(readConfig()["input_path"])
    return scriptList

def setRegression(scriptList:list[str]=None,timeString:str="0 * * * *"):
    return jenkins.createPipeline(scriptList,timeString)

def doTest(scriptList = []):
    try:
        core.core(readConfig(),scriptList)
    except:
        print("doTest() Faile.")
    temp['flag']['testing'] = False
    print('Test Thread Done')

def test(scriptList = []):
    temp['flag']['testing'] = True
    print(f'Get scriptList = {scriptList}')
    testThread = Thread(target = doTest, args=(scriptList,))
    testThread.start()

def getTestingFlag():
    return temp['flag']['testing']

def getTestWindowFlag():
    return temp['flag']['testWindow']

def setTestWindowFlag(value:bool):
    temp['flag']['testWindow'] = value

def getPdByDataName(dataName=''):
    '''根據 dataName 回傳對應的 DataFrame'''

    # 設定讀取範圍 col 0 ~ 6
    columns_to_read = [0, 1, 2, 3, 4, 5, 6]

    # 回傳指定 excel 的內容，因 jasion 不能傳 nan ，所以使用 fillna('nan') 以字串取代 nan
    return core.pd.read_excel(f'{readConfig()["input_path"]}/{dataName}', sheet_name='marco', usecols=columns_to_read, header=None).fillna('nan')

def readScriptByName(Name=''):
    '''根據腳本名稱取得腳本資料，並以 dict 型態回傳'''
    outputDictList = getPdByDataName(Name).to_dict(orient='records')
    return outputDictList[1:]

def saveScript(ScriptName="000",ScriptActions=[]):
    '''根據本名稱儲存腳本內容'''
    def writeToExel(exel):
        sheet_name = "marco"
        Script = core.pd.DataFrame(ScriptActions)
        Script.to_excel(exel, sheet_name=sheet_name, index=False,)
    with core.pd.ExcelWriter(f'{readConfig()["input_path"]}/{ScriptName.split(".")[0]}.xlsx', mode="w", engine='openpyxl')as writer:
        writeToExel(writer)
    return True

if __name__ == '__main__':
    getConfig()
    saveScript()