import webview
import time

# 從網頁回傳資料的 api
class API:
    def __init__(self):
        self.showCheck = True
        self.XPath = None
        self.closeFlag = False
        self.noWindow = False
        pass

    def output(self,text):
        self.XPath = text
        self.closeFlag = True
    
    def check(self):
        if self.showCheck:
            return "1"
        else:
            return "0"

api = API()
    
# 彈出視窗的 css 字串
innerCSS ='''\'<style>\
dialog#checkXPath{\
  border: none;\
  box-shadow: 0 2px 6px #ccc;\
  border-radius: 10px;\
}\
dialog#checkXPath::backdrop {\
  background-color: rgba(0, 0, 0, 0.1);\
}\
dialog#checkXPath > div > h1 {\
  font-size: 26px;\
  word-wrap:break-word;\
}\
dialog#checkXPath > div > p {\
  font-size: 16px;\
  word-wrap:break-word;\
}\
dialog#checkXPath > div {\
  display: flex;\
  flex-direction: column\
}\
dialog#checkXPath > div > div{\
  display: flex;\
  justify-content: flex-end;\
}\
dialog#checkXPath > div > div >button {\
  background-color: #0d6efd;\
  border: none;\
  border-radius: 6px;\
  color: white;\
  padding: 14px 14px;\
  text-align: center;\
  text-decoration: none;\
  display: inline-block;\
  font-size: 16px;\
  margin: 4px 2px;\
  cursor: pointer;\
}\
#reSelect {\
background-color: #6c757d !important;\
}\
dialog#checkXPath > div > div > button:focus-visible {\
  outline: none;\
}\
</style>\''''
innerdialog='''\'<dialog XPath="" id="checkXPath" check="''' + api.check() + '''">\
<div>\
  <h1>XPath = </h1>\
  <p></p>\
  <hr>\
  <div>\
  <button id="send">確認送出</button>\
  <button id="reSelect">重新選擇</button>\
  </div>\
</div>\
</dialog>\''''

innerFunction='''let checkXPathDialog = document.querySelector('dialog#checkXPath')

        //在 dialog 按鈕上榜定事件
        function closeCheckXPathDialog(){
            //checkXPathDialog.setAttribute('tabindex','-1')
            checkXPathDialog.close();
        }

        function sendXPath(){
            pywebview.api.output(checkXPathDialog.querySelector('p').textContent);
            //checkXPathDialog.setAttribute('tabindex','-1')
            checkXPathDialog.close();
        }

        checkXPathDialog.querySelector('#reSelect').addEventListener('click',closeCheckXPathDialog);
        checkXPathDialog.querySelector('#send').addEventListener('click',sendXPath);
        
        //設定彈出 dialog 的程式
        function launchDialog(Xpath){
            
            if(checkXPathDialog.getAttribute('check') == "1"){
                //利用屬性傳遞 XPath 的值
                //checkXPathDialog.setAttribute('tabindex','1')
                checkXPathDialog.setAttribute('XPath',Xpath)

                //修改 p 的文字
                checkXPathDialog.querySelector('p').textContent = Xpath;
                checkXPathDialog.showModal();
            }else{
                console.log(pywebview.api.Check);
                pywebview.api.output(Xpath);
            }
        }'''
def handleXPath(window:webview.Window):
    window.evaluate_js(
        """
        //在 head 加入 CSS 片段
        let hd = document.querySelector('head');
        hd.innerHTML += """ + innerCSS + """
        
        function handleClick(event) {
            let target = event.target;
            let xpath = getShortXPath(target);
            return xpath;
        }

        function getShortXPath(element) {
        
            let xpath = ''; // 用於構建XPath的變數
            let attributes = []; // 用於存儲元素的特殊屬性和屬性值
            for (; element && element !== document; element = element.parentNode) {
                let tagName = element.tagName.toLowerCase(); // 當前元素的標籤名稱
                let index = 1; // 索引號，用於區分同層級的元素
                let siblings = element.parentNode.children; // 當前元素的同層級子元素
                for (let i = 0; i < siblings.length; i++) {
                    let sibling = siblings[i];
                    if (sibling === element) {
                        let pathIndex = index > 1 ? `[${index}]` : '';
                        xpath = '/' + tagName + pathIndex + xpath;
                        break;
                    }
                    if (sibling.nodeType === 1 && sibling.tagName.toLowerCase() === tagName) {
                        index++;
                    }
                }
                let attrs = element.getAttributeNames().reduce((acc, name) => {
                return {...acc, [name]: element.getAttribute(name)};
                }, {});
                attributes.unshift(attrs);
            }

            let originalXPath = xpath; // 原始的完整XPath
            let finishXPath = '';
            let splitXPath = originalXPath.split('/');
            console.log(`splitXPath : ${splitXPath.length}`);
            console.log(`attributes : ${attributes.length}`);
            for (let i = splitXPath.length-1; i > 0; i--){
                let tag = splitXPath[i].split('[')[0];
                let attribute = attributes[i-1];
                for (let j of Object.keys(attribute)){
                    let tempXPath = `//${tag}[@${j}="${attribute[j]}"]${finishXPath}`;
                    // 從最末端節點開始逐層替換的XPath
                    let result = testXPath(tempXPath);
                    let orign = testXPath(originalXPath);
                    // 測試使用替換後的XPath是否能選擇到相同的元素
                    if (result == orign) {
                        return tempXPath;
                        // 如果測試結果與原始元素相符，則返回該XPath
                    }
                }
                let tempXPath = `//${tag}${finishXPath}`;
                // 從最末端節點開始逐層替換的XPath
                let result = testXPath(tempXPath);
                let orign = testXPath(originalXPath);
                // 測試使用替換後的XPath是否能選擇到相同的元素
                if (result == orign) {
                    return tempXPath;
                    // 如果測試結果與原始元素相符，則返回該XPath
                }
                finishXPath =`/${splitXPath[i]}${finishXPath}`;
            }

            return originalXPath;
            // 如果沒有找到相符的XPath，則返回原始的完整XPath
        }

        function testXPath(XPath) {
            let gogo = document.evaluate(XPath, document, null, XPathResult.ANY_TYPE, null);
            let out = gogo.iterateNext();
            return out;
            // 輸出XPath選擇的元素，供測試和驗證使用
        }


        document.addEventListener('click', function(event) {
            if(event.ctrlKey && event.altKey){
                event.preventDefault();
                let out = handleClick(event);
                pywebview.api.output(out);
            }
            
        });
        """)

def getXPath(url):
    api.closeFlag = False
    selecter = webview.create_window('Run custom JavaScript',url,js_api=api)
    selecter.events.loaded += lambda:handleXPath(selecter)
    while api.closeFlag == False:
        time.sleep(0.05)
    selecter.destroy()
    return api.XPath