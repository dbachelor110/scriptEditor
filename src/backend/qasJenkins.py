import requests

# 宣告字串解析工具 function
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

class JenkinsCenter:
    def __init__(self,url:str="http://qascenter.asgard.com.tw:8080/",userName:str="admin",api_token:str="11827602bcb74064717ee971fd3a11a339"):
        self.bassUrl = url
        self.userName = userName
        self.api_token = api_token
        self.auth = (self.userName,self.api_token)
        self.headers = {
            "Content-Type": "application/xml",
            "Jenkins-Crumb": f"{self.api_token}"  # Use API Token as crumb
        }
    def post(self,apiUrl:str="createItem?name=123",data:str=""):
        # 組合 url
        fullUrl = f"{self.bassUrl}{apiUrl}"
        # 送出請求
        response = requests.post(fullUrl, auth=self.auth, headers=self.headers, data=data,timeout=10)
        if response.status_code >= 200 and response.status_code < 400:
            print(f"{response.status_code}:{fullUrl} Successfully.")
            return True
        else:
            print(f"{response.status_code}:{fullUrl} Failed.")
            return False

    def createPipeline(self,pipelineName:str="name",data:str=""):
        return self.post(f"createItem?name={pipelineName}",data)

    def buildPipelineWithParameters(self,pipelineName:str,parametersString:str):
        return self.post(f"job/{pipelineName}/buildWithParameters?{parametersString}")


class AsGardJenkins(JenkinsCenter):
    def __init__(self):
        super().__init__("http://qascenter.asgard.com.tw:8080/", "admin", "11827602bcb74064717ee971fd3a11a339")

    def createPipeline(self, scriptNameList:list[str]=None,timeSetString:str="0 * * * *"):
        if scriptNameList == None: return "沒有選擇欲執行的腳本"
        clearNameList = listCleaner(scriptNameList)
        scriptNameListString = listToString(clearNameList)
        pipelineName = f"回歸測試{clearNameList[0]}len{len(clearNameList)}"

        # 讀 .xml 模板
        pathConfigxml = open("src/backend/model.xml",encoding='utf-8').read()
        stages = makeXmlStringByList(clearNameList)
        # 關鍵，jenkins api 只吃編碼過的字串，因此上一部解析出來的 pathConfigxml 經過處理後需要再使用 encode("utf-8") 編碼後才能傳給 data
        data = pathConfigxml.replace("DefaultScriptNameList",scriptNameListString).replace("timeInserPoint",timeSetString).replace("stageInserPoint",stages).encode("utf-8")

        return super().createPipeline(pipelineName, data)
# 實作一個 AsGardJenkins 物件，命名為 jenkins
jenkins = AsGardJenkins()