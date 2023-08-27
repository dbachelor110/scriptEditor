from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
import pandas as pd
import time
import sys
import os.path as osPath
from os import listdir,makedirs
"""產報告測試"""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
"""產報告測試"""
from io import BytesIO
from PIL import Image as PIL_Image
import importlib
from queue import Queue
import traceback
import toolBox
# import FunctionSP

# log暫存器
logList = toolBox.LogAdmin.logList
# gui接口
log_area = toolBox.LogAdmin.log_area
log_queue = toolBox.LogAdmin.log_queue

# # 當error發生，需要終止迴圈時，errorFlag設為1。
# errorFlag=0


def logText(text,save=1):
    '''logText 是紀錄 log 的 function, save 設為非 1 時，只會顯示不會儲存進log.txt
    '''
    return toolBox.logText(text,save=1)

# 讀取參數path指定的位置，取得該路徑下的所有excel檔案名稱-->回傳所有excel檔案名稱組成的list ExcelList
def getExcelList(path):
    """取得所有 .xlsx 檔並 return excelList """
    return toolBox.ScriptListAdmin.getScriptList(path)

# 在路徑下放一個txt檔案，可以指定需要執行的excelList
def getExcelListInTxt(path):
    return toolBox.ScriptListAdmin.getScriptListInTxt(path)

def excelWriter(path:str,writerConfig):
    if osPath.exists(path):
        with pd.ExcelWriter(path, mode="a", engine='openpyxl', if_sheet_exists='replace')as writer:
            writerConfig(writer)
    else:
        with pd.ExcelWriter(path, mode="w", engine='openpyxl')as writer:
            writerConfig(writer)

#取得專案資料夾path
def mainFolderPath():
    mainFolderPath = toolBox.mainFolderPath()
    return mainFolderPath

#取得專案path
def locoalFolderPath():
    return toolBox.locoalFolderPath

# 設定環境變數
def getParameter():
    return toolBox.parameterFunction.get()

# 根據字典參數中的headless與auto_update_driver製作Browser
def makeBrowser(loginData):
    return toolBox.parameterFunction.makeBrowser(loginData)

def Parameter_save(loginData):
    return toolBox.parameterFunction.save(loginData)

# 螢幕截圖程式
def makeScreenLongShot(inputName:str,driver:webdriver.Chrome=None,url:str=None, path:str=osPath.dirname(osPath.abspath(__file__)),maxWindow=1,avoidImgTooBig=1):
    """將完整的網頁內容以圖片形式保存"""
    return toolBox.ScreenShot.makeLong(inputName,driver,url,path,maxWindow,avoidImgTooBig)

class testInformation():
    def __init__(self,fileName='',parameterData ={}):
        self.fileName = fileName
        self.parameterData = parameterData
        if self.parameterData == {}:
            self.parameterData=makeBrowser(getParameter())
        #取得Parameter_settings
        self.browser:webdriver.Chrome = self.parameterData["browser"]
        self.input_path=self.parameterData["input_path"]
        self.error_path=self.parameterData["error_path"]
        #取得linkSrc
        self.domain = self.parameterData["domain"]
        self.url = self.parameterData["url"]
        self.username = self.parameterData["username"]
        self.password = self.parameterData["password"]
        self.username_locator = self.parameterData['username_locator']
        self.password_locator = self.parameterData['password_locator']
        self.submit_locator = self.parameterData['submit_locator']

        #將fileName的附檔名去除
        self.fileName=self.fileName.split(".")[0]
        # 定義資料文件來源與輸出，路徑請在config.txt中設定
        self.input_file_path = f"{self.input_path}/{self.fileName}.xlsx"
        self.error_file_path = f"{self.error_path}/errorlog.xlsx"

        # 定義照相功能儲存的路徑與名稱
        self.save_directory = f"{self.input_path}/{self.fileName}"
        self.screenshot_name = self.fileName
        self.count = 1
        self.saveSpace={}

        # 檢查error文件是否已存在
        self.output_dir = osPath.dirname(self.error_file_path)
        if not osPath.exists(self.output_dir):
            makedirs(self.output_dir)

        # 讀取Excel文件，當遇到欄位值為文字"NA"時視為有效字符
        self.df = pd.read_excel(self.input_file_path, sheet_name='marco', header=None)

        # 定義儲存比對錯誤訊息的list
        self.error_list = []

        # 定義迴圈結束註記
        self.end_flag  = False

        # 創建一個 PDF 文件
        self.report_path = f'{self.input_path}/{self.fileName}'
        if not osPath.exists(self.report_path):
            makedirs(self.report_path)
        self.report_path = f'{self.report_path}/{self.fileName}.pdf'
        self.doc = SimpleDocTemplate(self.report_path, pagesize=letter)
        self.page_width, self.page_height = letter

        # 註冊支持中文的字體
        # pdfmetrics.registerFont(TTFont('STHeiti Light.ttc', 'STHeiti Light.ttc', subfontIndex=1))

        # 定義一個樣式
        self.styles = getSampleStyleSheet()
        self.style_normal = self.styles['Normal']
        # style_normal.fontName = 'STHeiti Light.ttc'

        # 創建一個空的 Story（內容）列表
        self.story = []

        # 先建一個標題
        # 添加文字段落
        self.paragraph = Paragraph(f"{self.fileName}測試報告", self.style_normal)
        self.story.append(self.paragraph)

        # 添加間隔
        self.story.append(Spacer(1, 12))
class action():
    def __init__(self,testInformation:testInformation,var0=None,var1=None,var2=None,var3=None,var4=None,var5=None,var6=None):
        self.testInformation = testInformation
        self.var0=var0
        self.var1=var1
        self.var2=var2
        self.var3=var3
        self.var4=var4
        self.var5=var5
        self.var6=var6
        self.errorlist=[]

    def checkVar(self,checkIf,errornumber:int):
        if checkIf:
            error_text = f'Action {self.var0}: {self.var1}  {self.errorlist[errornumber]}'
            logText(error_text)
            self.error_end(error_text)
            return False
        else:
            return True
    
    def find_element(self,定位方式:str=None,定位值:str=None):
        '''預設使用 var2 設定定位方式， var3 設定定位值'''
        # 設定變數
        if 定位方式 == None:定位方式 = str(self.var2).lower()
        if 定位值 == None:定位值 = str(self.var3)
        element:webdriver.WPEWebKit._web_element_cls = None

        # 定位 element
        if 定位方式 == 'xpath':
            # 這裡是讓程式去等待直到指定的元素出來
            element = WebDriverWait(self.testInformation.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, 定位值))
            )
        elif 定位方式 == 'id':
            element = WebDriverWait(self.testInformation.browser, 10).until(
                EC.presence_of_element_located((By.ID, 定位值))
            )
        elif 定位方式 == 'name':
            element = WebDriverWait(self.testInformation.browser, 10).until(
                EC.presence_of_element_located((By.NAME, 定位值))
            )
        elif 定位方式 == 'class':
            element = WebDriverWait(self.testInformation.browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 定位值))
            )
        elif 定位方式 == 'css':
            element = WebDriverWait(self.testInformation.browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 定位值))
            ) 
        else:
            logText('Invalid locator type')
            error_text = f'Action {self.var0}: {self.var1} 定位設定錯誤，請確認！'
            self.error_end(error_text)
        return element
    
    def sleep(self):
        time.sleep(float(self.var4))
    
    # 定義 load_params 函数
    def load_params(self):
        if f"params_{self.var6}" in self.testInformation.saveSpace:
            return self.testInformation.saveSpace.get(f"params_{self.var6}")
        else:
            error_text = f'Action {self.var0}: {self.var1} 指定的參數params_{self.var6}不存在，請確認！'
            self.error_end(error_text)

    # 當資料來源內容錯誤時記錄錯誤並結束
    def error_end(self,error_text):
        errtext = error_text
        logText("腳本參數錯誤!請參照 Excel 最新分頁")
        # 如果error_list中沒有資料(比對錯誤)
        if not self.testInformation.error_list:
            self.testInformation.error_list.append([errtext,None,None,None,None])
            # 定義excel寫入內容
            def writeToExel(exel):
                sheet_name = self.testInformation.fileName + '_error'
                error_df = pd.DataFrame(self.testInformation.error_list, columns=['指令序', '定位方式', '定位內容', '頁面值', '正確值'])
                error_df.to_excel(exel, sheet_name=sheet_name, index=False)

            excelWriter(self.testInformation.error_file_path,writeToExel)
            file_mtime = osPath.getmtime(self.testInformation.error_file_path)
            while (time.time() - file_mtime) < 2:
                time.sleep(1)
            logText("Excel 檔案已儲存完成")
            # 當end_flag＝True時，停止執行Excel上的Action迴圈
            self.testInformation.end_flag = True
        else:
            # 如果已有錯誤資料(比對錯誤)
            self.testInformation.error_list.append([errtext])
            return self.end()

    def end(self):
        if len(self.testInformation.error_list) == 0:
            logText(f'{self.testInformation.fileName} 測試通過！')
            if len(self.testInformation.story) > 0:
                # 將 Story 寫入到 PDF 文件中
                self.testInformation.doc.build(self.testInformation.story)
                print(f"已完成測試報告，儲存路徑：{self.testInformation.input_path}")
                self.testInformation.end_flag = True
        else:
            # 寫入錯誤文件

            def writeToExel(exel):
                sheet_name = self.testInformation.fileName + '_error'
                error_df = pd.DataFrame(self.testInformation.error_list, columns=['指令序', '定位方式', '定位內容', '頁面值', '正確值'])
                error_df.to_excel(exel, sheet_name=sheet_name, index=False)

            excelWriter(self.testInformation.error_file_path,writeToExel)
            file_mtime = osPath.getmtime(self.testInformation.error_file_path)

            with open(f"{locoalFolderPath()}/errorLog.txt","+a")as error:
                for i in self.testInformation.error_list:
                    error.write(f"{self.testInformation.fileName}:{i}\n")
                error.write("\n")
            while (time.time() - file_mtime) < 2:
                time.sleep(1)
            logText(f'{self.testInformation.fileName} 測試不通過，請參考 {self.testInformation.error_file_path} 確認錯誤內容。')
            if self.testInformation.story:
                # 將 Story 寫入到 PDF 文件中
                try:
                    self.testInformation.doc.build(self.testInformation.story)
                except Exception as e:
                    logText(f"An error occurred:{e}")
            self.testInformation.end_flag = True

class behavior(action):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)

class elementAction(action):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        self.errorlist.append('定位資訊錯誤！')
        self.element:webdriver.WPEWebKit._web_element_cls = None
        if self.checkVar(pd.isnull(self.var2) or pd.isnull(self.var3),0):
            self.element = self.find_element()
    def preKeyIn(self):
        self.var5=str(self.var5)
        # 解析 var5 判斷是否將 is_date_field 設為 True ，進行 date 輸入流程
        if self.var5.lower()=='y':
            is_date_field = True
        else:
            is_date_field = False
        # 如果 var4 var6 其中一個有值，則繼續測試流程
        if pd.notna(self.var4) or pd.notna(self.var6):
            # 如果 var4 為空，從 load_params(self.var6) 得到 text
            # 由於 var4 var6 其中一個有值，一定可以從其中一個撈到值，不存在皆為空的情況
            if pd.isnull(self.var4):
                if pd.notna(self.var6):
                    self.var4 = self.load_params()

            if pd.notna(self.var2):
                self.element.click()
                if self.element:
                    # 判斷是否為時間欄位(時間欄位執行clear()會無法正常填入值)
                    if is_date_field:
                        self.element.send_keys(Keys.BACKSPACE)
                        self.testInformation.browser.execute_script("arguments[0].style.display = 'block';", self.element)
                    else:
                        self.testInformation.browser.execute_script("arguments[0].style.display = 'block';", self.element)
                        self.element.clear()               
            else:
                self.element = self.testInformation.browser.find_element(by=By.TAG_NAME, value="body")
            return True
        else:
            return False

    def key_in(self):
        if self.preKeyIn():
            self.element.send_keys(self.var4)
        else:
            error_text = f"Action {self.var0}:{self.var1} 未提供填入內容！"
            self.error_end(error_text)
    def mkey_in(self):
        if self.preKeyIn():
            actions = ActionChains(self.testInformation.browser)
            actions.click(self.element).send_keys(self.var4).perform()
        else:
            error_text = f"Action {self.var0}:{self.var1} 未提供填入內容！"
            self.error_end(error_text)

class web_connection(action):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        self.errorlist.append('未提供連線位置！')
        if self.checkVar(pd.isnull(self.var5),0):
            link = f"{self.testInformation.domain}{self.var5}"
            logText(f"Going to:{link}")
            self.testInformation.browser.get(link)

class login(action):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        self.testInformation.browser.get(self.testInformation.url)
        username_locator=self.testInformation.username_locator
        username_element = WebDriverWait(self.testInformation.browser, 10).until(EC.visibility_of_element_located(username_locator))
        username_element.clear()
        username_element.send_keys(self.testInformation.username)
        password_element = self.testInformation.browser.find_element(*self.testInformation.password_locator)
        password_element.clear()
        password_element.send_keys(self.testInformation.password)

        # 點擊登入按鈕
        submit_element = self.testInformation.browser.find_element(*self.testInformation.submit_locator)
        submit_element.click()

        # 等待跳轉完成，若頁面跳轉判定為登入成功
        try:
            WebDriverWait(self.testInformation.browser, 10).until(EC.url_changes(self.testInformation.url))
            logText('登入成功')
        except TimeoutException:
            logText('登入失敗')
            error_text = f'Action {self.var0}: {self.var1} 登入失敗！'
            self.error_end(error_text)

class wait_jump(action):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        self.errorlist.append('未提供原始網址！')
        if self.checkVar(pd.isnull(self.var5),0):
            try:
                link = f"{self.testInformation.domain}{self.var5}"
                WebDriverWait(self.testInformation.browser, 10).until(EC.url_changes(link))
                logText('跳轉成功')
            except TimeoutException:
                logText('跳轉失敗')
                error_text = f'Action {self.var0}: {self.var1} 跳轉失敗！'
                self.error_end(error_text)

# 定義執行FunctionSP中的自定義功能
class function(action):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        module_name='FunctionSP'
        self.errorlist.append('未填寫需執行的的客製化方法！')
        if self.checkVar(pd.isnull(self.var2),0):
            method = self.var2
            print(f"執行自定義方法：{method}")
            try:
                module = importlib.import_module(module_name)
                method = getattr(module, self.var2)
                return method(self.testInformation.browser, self.var3, self.var4, self.var5, self.var6)
            except ImportError:
                print(f"Error: {module_name} 模組不存在！")
            except AttributeError:
                print(f"Error: 模組 {module_name} 中沒有以下方法： {self.var2}")

class sleep(action):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        self.errorlist.append('未提供等待時間！')
        if self.checkVar(pd.isnull(self.var4),0):
            self.sleep()

class click(elementAction):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        self.element.click()

# 定義滑鼠點擊的定位方式
class mclick(elementAction):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        if pd.isnull(self.var4):
            self.var4 = 0
        actions = ActionChains(self.testInformation.browser)
        actions.click(self.element).perform()
        self.sleep()
        actions.release(self.element).perform()

# 定義滑鼠雙擊的定位方式
class mdbclick(elementAction):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        actions = ActionChains(self.testInformation.browser)
        actions.double_click(self.element).perform()

class key_in(elementAction):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        self.key_in()

class report_text(action):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        self.errorlist.append('未填寫需填入的文字！')
        if self.checkVar(pd.isnull(self.var4),0):
            # 添加文字段落
            paragraph = Paragraph(self.var4, self.testInformation.style_normal)
            self.testInformation.story.append(paragraph)

            # 添加間隔
            self.testInformation.story.append(Spacer(1, 12))

# 定義在表格中欄位輸入
class key_in_table(elementAction):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        # 如果 var4 var6 其中一個有值，則繼續測試流程
        if pd.notna(self.var4) or pd.notna(self.var6):

            # 如果 var4 為空，從 load_params(self.var6) 得到 text
            # 由於 var4 var6 其中一個有值，一定可以從其中一個撈到值，不存在皆為空的情況
            if pd.isnull(self.var4):
                if pd.notna(self.var6):
                    self.var4 = self.load_params()
    
            # 暫存 element xpath
            temp = self.var3
            # 移至 /input[1] xpath
            self.var3 = self.var3 + '/input[1]'
            self.element.clear()

            # 回到 element xpath
            self.var3 = temp
            self.element = self.find_element() 
            self.element.click()

            # 移至 /input[1] xpath
            self.var3 = self.var3 + '/input[1]'
            self.element = self.find_element()
            self.element.send_keys(self.var4)
        else:
            error_text = f"Action {self.var0}:{self.var1} 未提供填入內容！"
            self.error_end(error_text)

class tap(elementAction):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        if pd.notna(self.var4):
            try:
                exec(f'self.var4 = Keys.{self.var4.upper()}')
            except:
                error_text = f"Action {self.var0}:{self.var1} 特殊鍵名稱錯誤，請重新確認！"
                self.error_end(error_text)
            if pd.notna(self.var5):
                self.var4 = self.var4 + self.var5
            self.key_in()
        else:
            error_text = f"Action {self.var0}:{self.var1} 未提供待輸入的特殊鍵！"
            self.error_end(error_text) 

# 定義下拉式選單
class select(elementAction):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        if pd.notna(self.var4): 
            if self.element:
                select = Select(self.element)
                select.select_by_value(self.var4)
        else:
            error_text = f"Action {self.var0}:{self.var1} 未填寫需使用的值！"
            self.error_end(error_text)
    

# 定義 save_params_to 行為
class save_params_to(elementAction):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        if pd.isnull(self.var6):
            error_text = f"Action {self.var0}:{self.var1} 未提供待用參數之命名！"
            self.error_end(error_text)
        else:  
            if self.element:
                # 欄位值可能有兩種形式：text or attribute，會兩種都抓然後塞有值的那一種
                text_value = self.element.text
                attribute_value = self.element.get_attribute('value')
                actual_value = text_value if text_value else attribute_value
                param_value = actual_value
                # 將 param_name 作為變數名稱存儲 text or attribute
                self.testInformation.saveSpace[f"params_{self.var6}"] = param_value

# 定義 compare 行為
class compare(elementAction):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        if pd.notna(self.var4):
            pass
        elif pd.notna(self.var6):
            self.var4 = self.load_params()
        else:
            self.var4 = None

        if self.element:
            # 欄位值可能有兩種形式：text or attribute，會兩種都抓然後塞有值的那一種
            text_value = self.element.text
            attribute_value = self.element.get_attribute('value')
            actual_value = text_value if text_value else attribute_value
            if not actual_value:
                actual_value = None
            logText(f"頁面值: {actual_value}")
            logText(f"比對值: {self.var4}")
            if actual_value == self.var4:
                logText("比對成功!")
            else:
                logText("比對失敗!")
                self.testInformation.error_list.append([self.var0, self.var2, self.var3, actual_value, self.var4])

# 定義切換到彈出視窗
class switch(action):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        main_window = self.testInformation.browser.current_window_handle
        for window_handle in self.testInformation.browser.window_handles:
            if window_handle != main_window:
                try:
                    self.testInformation.browser.switch_to.window(window_handle)
                    break
                except NoSuchWindowException:
                    logText("彈出視窗不存在")
                    error_text = f'Action {self.var0}: {self.var1} 彈出視窗不存在，請確認！'
                    self.error_end(error_text)

# 定義切換回主畫面
class backto(action):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        if not isinstance(self.var4, str):
            self.var4 = str(self.var4)
        if self.var4.lower() == 'yes':
            self.testInformation.browser.close()
        for window_handle in self.testInformation.browser.window_handles:
            self.testInformation.browser.switch_to.window(window_handle)
            break

# 定義 load_params 函数
class load_params(action):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        self.load_params()

# 定義滾軸移動
class scroll(action):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        # 這裡提供的是滾軸百分比，0代表最左或最上，1代表最右或最下
        scroll_width = float(self.var4)
        scroll_height = float(self.var5)
        if self.var2 == None and self.var3 == None:
            # 無提供元素定位時，滾動整個頁面視窗
            self.testInformation.browser.execute_script(f"window.scrollTo(0, document.body.scrollWidth * {scroll_width});")
            self.testInformation.browser.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {scroll_height});")
        else:
            # 提供元素定位時，滾動指定元素的滾軸
            # arguments 在執行時會帶入 element
            element = self.find_element()
            self.testInformation.browser.execute_script(f"arguments[0].scrollLeft = arguments[0].scrollWidth * {scroll_width};", element)
            self.testInformation.browser.execute_script(f"arguments[0].scrollTop = arguments[0].scrollHeight * {scroll_height};", element)
            print(f"arguments[0].scrollLeft = arguments[0].scrollWidth * {scroll_width};", element)

# 定義螢幕截圖
class pic(action):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        # 創建保存目錄，如果不存在
        if not osPath.exists(self.testInformation.save_directory):
            makedirs(self.testInformation.save_directory)

        # 編號截圖
        numbered_screenshot_name = "{}_{:0>2}".format(self.testInformation.screenshot_name,self.testInformation.count)
        numbered_screenshot_name=makeScreenLongShot(numbered_screenshot_name,driver=self.testInformation.browser,path=self.testInformation.save_directory)

        #my code test
            # 檢查截圖的長寬比
        imgdir = f'{self.testInformation.save_directory}/{numbered_screenshot_name}'
        with PIL_Image.open(imgdir) as img:
            original_width, original_height = img.size
            aspect_ratio = original_height / original_width

        # 根據 PDF 頁面寬度縮放圖片，並保持原始縮放比例
        new_width = self.testInformation.page_width - self.testInformation.doc.leftMargin - self.testInformation.doc.rightMargin
        new_height = new_width * aspect_ratio    

        # 添加圖片
        image = Image(imgdir, width=new_width, height=new_height)
        self.testInformation.story.append(image)
        self.testInformation.count+=1

        # 添加間隔
        self.testInformation.story.append(Spacer(1, 12))

class end(action):
    def __init__(self, testInformation: testInformation, var0=None, var1=None, var2=None, var3=None, var4=None, var5=None, var6=None):
        super().__init__(testInformation, var0, var1, var2, var3, var4, var5, var6)
        self.end()

class testClass(testInformation):
    def __init__(self, fileName='', parameterData={}):
        super().__init__(fileName=fileName,parameterData=parameterData)
        step_nmber = 0
        for i in range(1, self.df.shape[0]):
            act = self.df.iloc[i, 1]
            # step_nmber = self.df.iloc[i, 0]
            if self.end_flag == True:
                break

            try:
                # 如果 act 不是 BEHAVIOR ， step_nmber + 1
                if act.upper() != 'BEHAVIOR':
                    step_nmber += 1
                    logText(f"Action {step_nmber}: {act}")
                    a = [step_nmber]+[self.df.iloc[i, j] for j in range(1,7)]
                    exec(f'{self.df.iloc[i, 1]}(self,*a)')

            except Exception as e:
                error_class = e.__class__.__name__ #取得錯誤類型
                try:
                    detail = e.args #取得詳細內容
                except:
                    detail = 'None'
                cl, exc, tb = sys.exc_info() #取得Call Stack
                lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
                fileName = lastCallStack[0] #取得發生的檔案名稱
                lineNum = lastCallStack[1] #取得發生的行號
                funcName = lastCallStack[2] #取得發生的函數名稱
                errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
                logText(f'Action {step_nmber}: {self.df.iloc[i, 1]} 程式錯誤！')
                logText(errMsg)
                logText(f"\n")# 換行
                break

def saveLog():
    # 將logList寫入log.txt
    with open(f"{locoalFolderPath()}/log.txt","+a",encoding="utf-8")as logtxt:
        for txt in logList:
            logtxt.write(f"{txt}\n")

def core(Parameter:dict = getParameter(), excelList = None):
    '''批量測試主程式，透過迭代 excelList 呼叫 test 來完成執行清單中的 excel 測試案例。

    變數
        Parameter | 字典資料，內涵config.txt中的所有變數。
    '''
    logText('get in core')
    if excelList == None or excelList == '':
        excelList = getExcelList(Parameter["input_path"])

    # 嘗試合成 Browser ，若失敗則終止程式
    try:
        testParameter=makeBrowser(Parameter)
    except:
        logText('makeBrowser() Failed')
        logText('core() Exit')
        saveLog()
        return
    
    # 開始測試迴圈
    for excel in excelList:
        print('get in test for')
        logText(f"{excel} : Start")
        print('test for start')
        try:
            testClass(excel,testParameter)
            logText(f"{excel} : Done")
            logText(f"\n")# 換行
        except Exception as e:
            error_class = e.__class__.__name__ #取得錯誤類型
            try:
                detail = e.args[0] #取得詳細內容
            except:
                detail = 'None'
            cl, exc, tb = sys.exc_info() #取得Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
            fileName = lastCallStack[0] #取得發生的檔案名稱
            lineNum = lastCallStack[1] #取得發生的行號
            funcName = lastCallStack[2] #取得發生的函數名稱
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
            logText(errMsg)
            logText(f"\n")# 換行
    try:
        testParameter['browser'].quit()
    except:
        pass
    logText("All Test Already Done")
    saveLog()