import requests
import json
import os

class JenkinsPost:
    def __init__(self,url:str="http://jenkinshost:8080/",userName:str="admin",api_token:str="11827602bcb74064717ee971fd3a11a339",data:str=""):
        self.url = url
        self.userName = userName
        self.api_token = api_token
        self.data = data
        self.auth = (self.userName,self.api_token)
        self.headers = {
            "Content-Type": "application/xml",
            "Jenkins-Crumb": f"{self.api_token}"  # Use API Token as crumb
        }
        
        self.send()

    def successfully(self, response):
        print(f"{response.status_code}:{self.url} successfully.")
        print(f"{response}")

    def failed(self,response):
        print(f"{response.status_code}:{self.url} Failed.")

    def send(self):
        response = requests.post(f"{self.url}", auth=self.auth, headers=self.headers, data=self.data,timeout=10)
        if response.status_code >= 200 and response.status_code < 400:
            self.successfully(response)
        else:
            self.failed(response)

class CreateJenkinsPipeline(JenkinsPost):
    def __init__(self, pipelineName:str="name", url: str = "http://jenkinshost:8080/", userName: str = "admin", api_token: str = "11827602bcb74064717ee971fd3a11a339", data: dict = {}):
        self.baseUrl = url
        self.pipelineName = pipelineName
        newUrl = f"{url}createItem?name={pipelineName}"
        super().__init__(newUrl, userName, api_token, data)

    def failed(self, response):
        deletAsk = JenkinsPost(f"{self.baseUrl}job/{self.pipelineName}/disable",self.userName,self.api_token)
        return super().failed(response)
    
def scriptNameCleaner(string:str):
    temp = f"{string.split('.')[0]}"
    return temp

def listCleaner(List:list[str]):
    newList:list[str]=[]
    for i in List:
        newList.append(scriptNameCleaner(i))
    return newList

def listToString(List:list[str]):
    preString="["
    for i in List:
        preString += f"{i},"
    string = preString[:-1]
    string += "]"
    return string

def stageMaker(name:str):
    temp = """stage(&apos;"""+ name +"""&apos;) {
            steps {
                script{
                    if(pythonResult."""+ name +""".failed){
                        error &quot;"""+ name +""" run failed&quot;
                    }else{
                        echo &apos;"""+ name +""" run successfully&apos;
                    }
                }
            }
        }
        """
    return temp

def makeXmlStringByList(List:list[str]):
    xmlString:str = ""
    for i in List:
        xmlString += stageMaker(i)
    return xmlString
    
def createQATestJenkinsPipeline(scriptNameList:list[str]=None,timeSetString:str="0 * * * *"):
    if scriptNameList == None: return "沒有選擇欲執行的腳本"
    clearNameList = listCleaner(scriptNameList)
    scriptNameListString = listToString(clearNameList)
    jenkins_url = "http://qascenter.asgard.com.tw:8080/"
    api_token = "11827602bcb74064717ee971fd3a11a339"
    pipeline_name = f"回歸測試{clearNameList[0]}len{len(clearNameList)}"

    # 讀 .xml 模板
    pathConfigxml = open("src/backend/model.xml",encoding='utf-8').read()
    stages = makeXmlStringByList(clearNameList)
    # 關鍵，jenkins api 只吃編碼過的字串，因此上一部解析出來的 pathConfigxml 經過處理後需要再使用 encode("utf-8") 編碼後才能傳給 data
    data = pathConfigxml.replace("DefaultScriptNameList",scriptNameListString).replace("timeInserPoint",timeSetString).replace("stageInserPoint",stages).encode("utf-8")
    response = CreateJenkinsPipeline(pipeline_name, jenkins_url, "admin",api_token, data)

def stopPipeline(jenkins_url="http://qascenter.asgard.com.tw:8080/",pipelineName="回歸測試01",userName="admin",api_token="11827602bcb74064717ee971fd3a11a339"):
    JenkinsPost(f"{jenkins_url}job/{pipelineName}/disable",userName,api_token)

def buildAsgardPipeline(pipelineName,scriptNameString):
    jenkins_url = "http://qascenter.asgard.com.tw:8080/"
    userName = "admin"
    api_token = "11827602bcb74064717ee971fd3a11a339"
    JenkinsPost(f"{jenkins_url}job/{pipelineName}/buildWithParameters?token=123&&ScriptNameList={scriptNameString}",userName,api_token)

def build回歸測試02(scriptNameList):
    scriptNameString = listToString(scriptNameList)
    buildAsgardPipeline("回歸測試02",scriptNameString)

if __name__ == "__main__":
    testList = ["FEGM0300_20230821","endTest"]
    createQATestJenkinsPipeline(testList)