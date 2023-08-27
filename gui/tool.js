import "./popper.js";
import "./jQuery.min.js";
import "./bootstrap.min.js";
import "./all.min.js";

function textConfig(text = '', length = 16){
    let temp = '';
    if(text.length > length){
        temp = `${text.slice(0,length)}...`;
    }else{
        temp = text;
    }
    return temp;
}
class Ajax {
    constructor(url="", method="GET", responseHandler=(response)=>{}, data={}) {
        console.log(`build Ajax Object : ${url}`);
        // 請求的 URL
        this.url = url;

        // 請求的方法（預設為 GET）
        this.method = method;

        // 回應處理器函式
        this.responseHandler;
        if(responseHandler){
            this.responseHandler = (response)=>{responseHandler(response);}
        }else{
            this.responseHandler = (response)=>{}
        }

        // 要傳遞的資料（預設為空字典）
        this.data = data;
        this.data.token = window.token;
        this.intervalTime = 100;
        this.timeoutTimes = 100;
    }

    // 設定 token 等安全檢核值
    async = true;

    // 避免請求阻塞，設定 flag
    // 為了刪除長時間空轉或 block 的循環請求，設定 count 、 timeoutID

    // 停止循環請求的旗標
    timeoutFlag = false;

    // AJAX 請求中是否正在執行的旗標
    ajaxingFlag = false;

    // 請求失敗或 block 的次數計數器
    count = 0;

    // 停止循環請求的 timeoutID
    timeoutID = 0;

    // 執行 AJAX 請求
    do() {
        if (this.url == "") {
            alert("URL can not be null/blank");
            return false;
        }

        if (this.ajaxingFlag == false) {
            this.ajaxingFlag = true;
            console.log(`Ajax.do : ${this.url}`);
            // 發送 AJAX request
            $.ajax({
                url: this.url,
                method: this.method,
                async: this.async,
                data: JSON.stringify(this.data),
                dataType: "json",
                contentType: "application/json",
                //須接受一個參數，來處理回傳的 json 資料
                success: (response) => {
                    this.count += 1;
                    if (response.status == `error`) {
                        console.log(`Get error`);
                    } else {
                        this.count = 0;
                        this.responseHandler(response);
                    }

                    this.ajaxingFlag = false;
                },
                error: (xhr, status, error) => {
                    this.ajaxingFlag = false;
                    console.log("AJAX request error: " + error);
                }
            });
        } else {
            console.log(`flag = ${this.ajaxingFlag}, Ask block`);
            this.count += 1;
        }

        if (this.count > this.timeoutTimes) {
            this.timeoutFlag = true;
            console.log(`Count = ${this.count}, ClearInterval.`);
        }
    }

    // 停止循環請求
    shoutDown() {
        if (this.timeoutFlag) {
            window.clearInterval(this.timeoutID);
        }
    }

    // 啟動循環請求
    interval() {
        this.timeoutID = window.setInterval(() => {
            this.do();
            this.shoutDown();
        }, this.intervalTime);
    }

    // 不停止的循環請求
    unStopInterval() {
        this.timeoutID = window.setInterval(() => {
            this.do();
        }, this.intervalTime);
    }
}

function doAjax(url="", method="GET", responseHandler, data={}){
    console.log(`get ask to doAjax : ${url}`);
    let temp = new Ajax(url, method, responseHandler, data);
    temp.do();
}

function doAjaxUnStopInterval(url="", method="GET", responseHandler, data={}){
    console.log(`get ask to doAjaxUnStopInterval : ${url}`);
    let temp = new Ajax(url, method, responseHandler, data);
    temp.unStopInterval();
}

class drag{
    static draggingElementItem = document.getElementById(``);
    static list = document.getElementById(`scriptArea`);

    static log = (text = ``)=>{
        console.log(`Drag ${text}`);
    }

    static getItem = (element = new HTMLElement)=>{
        while(element.classList.contains(`item`) != true){
            element = element.parentElement;
        }
        return element;
    }

    static getBehavior = (element = new HTMLElement)=>{
        while(element.classList.contains(`behavior`) != true){
            element = element.parentElement;
        }
        return element;
    }

    static Count = {
        set:(element = new HTMLElement, attr = ``, value = 0)=>{
            element.setAttribute(attr,`${value}`);
            return value;
        },
        add:(element = new HTMLElement, attr = ``)=>{
            let count = parseInt(element.getAttribute(attr));
            element.setAttribute(attr,`${count+1}`);
            return count+1;
        },
        sub:(element = new HTMLElement, attr = ``)=>{
            let count = parseInt(element.getAttribute(attr));
            element.setAttribute(attr,`${count-1}`);
            return count-1;
        },
    }

    static style = {
        add:(target = new HTMLElement)=>{
            let element = this.getItem(target);
            let count = this.Count.add(element,`enter`);
            if(count === 1){
                element.classList.add(`over`);
                let itemName = element.querySelector(`div.actionName`);
                let name = itemName.textContent;
                this.log(`enter ${name}`);
            }
            return element;
        },
        sub:(target = new HTMLElement)=>{
            let element = this.getItem(target);
            let count = this.Count.sub(element,`enter`);
            if(count === 0){
                element.classList.remove(`over`);
                let itemName = element.querySelector(`div.actionName`);
                let name = itemName.textContent;
                this.log(`leave ${name}`);
            }
            return element;
        },
    }

    static start = (e = new Event)=>{
        this.draggingElementItem = this.getItem(e.target);
        console.log(this.draggingElementItem);
        this.log(`start`);
    }

    static over = (e = new Event)=>{
        e.preventDefault();
        this.log(`over`);
    }

    static drop = (e = new Event)=>{
        e.preventDefault();
        if(this.draggingElementItem.classList.contains(`action`)){
            let element = this.style.sub(e.target);
            // 如果目的地是 behavior
            if(element.classList.contains(`behavior`)){
                element.insertBefore(this.draggingElementItem,element.children[1]);
                let itemArray = Array.from($(`.action`));
                for(let i = 0; i < itemArray.length; i++){
                    let number = this.Count.set(itemArray[i], `dataindex`, i+1);
                    itemArray[i].querySelector(`div.number`).textContent = number;
                }
            }else{
                let itemArray = Array.from($(`.action`));
                let newNumber = itemArray.indexOf(element);
                let oldNumber = itemArray.indexOf(this.draggingElementItem);

                let inserGroup = Array.from(element.parentElement.children);
                let inser = inserGroup.indexOf(element);
                this.log(`drop from ${oldNumber} to ${newNumber}`);

                // 若往下移動 //可以優化，這兩種方法可以整合成一個。
                if(newNumber > oldNumber){
                    
                    // 更改編號
                    // this.draggingElement 編號設為 inser + 1
                    let number = this.Count.set(this.draggingElementItem, `dataindex`, newNumber+1);
                    this.draggingElementItem.querySelector(`div.number`).textContent = number;
                    for(let i = oldNumber + 1; i < newNumber + 1; i++){
                        // 影響範圍編號 -1
                        let number = this.Count.sub(itemArray[i],`dataindex`);
                        itemArray[i].querySelector(`div.number`).textContent = number;
                    }
                    inser += 1;
                }else{ // 若往上移動

                    // 更改編號
                    // this.draggingElement 編號設為 inser + 1
                    let number = this.Count.set(this.draggingElementItem, `dataindex`, newNumber+1);
                    this.draggingElementItem.querySelector(`div.number`).textContent = number;
                    for(let i = newNumber; i < oldNumber; i++){
                        // 影響範圍編號 +1
                        let number = this.Count.add(itemArray[i],`dataindex`);
                        itemArray[i].querySelector(`div.number`).textContent = number;
                    }
                }
                element.parentElement.insertBefore(this.draggingElementItem,inserGroup[inser]);
            }
        }else{
            // 插入 behavior
            let element = this.getBehavior(e.target);
            this.style.sub(element);
            let behaviorArray = Array.from($(`.behavior`));
            let inser = behaviorArray.indexOf(element);
            let from = behaviorArray.indexOf(this.draggingElementItem);
            if(inser>from){
                inser += 1
            }
            element.parentElement.insertBefore(this.draggingElementItem,behaviorArray[inser]);

            // 更新編號
            let itemArray = Array.from($(`.action`));
            for(let i = 0; i < itemArray.length; i++){
                let number = this.Count.set(itemArray[i], `dataindex`, i+1);
                itemArray[i].querySelector(`div.number`).textContent = number;
            }
        }
        
        
    }

    static enter = (e = new DragEvent)=>{
        e.preventDefault();
        let element = e.target;
        console.log(`${element.localName}`);
        this.style.add(element);
    }

    static leave = (e = new Event)=>{
        e.preventDefault();
        let element = e.target;
        console.log(`${element.localName}`);
        this.style.sub(element);
    }
    static addListeners = ()=>{
        const draggables = document.querySelectorAll(`.behavior`);
        console.log(`addListeners ${draggables}`);
        draggables.forEach(draggable => {
            draggable.addEventListener(`dragstart`,this.start)
        });
        const Items = this.list.querySelectorAll(`.droppable`);
        Items.forEach(item =>{
            item.addEventListener(`dragover`,this.over);
            item.addEventListener(`drop`,this.drop);
            item.addEventListener(`dragenter`,this.enter);
            item.addEventListener(`dragleave`,this.leave);
        });
    };
}

let ActionTypeMap = {
    behavior: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            2: { name: `名稱`, type: `string`, required: true },
        },
        directions: `將 action 分群`
    },
    click: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            element: { name: ``, type: `element`, required: true },
            2: { name: `定位方式`, type: `string`, required: true },
            3: { name: `定位字串`, type: `string`, required: true },
        },
        directions: `點擊定位的元素`
    },
    mclick: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            element: { name: ``, type: `element`, required: true },
            2: { name: `定位方式`, type: `string`, required: true },
            3: { name: `定位字串`, type: `string`, required: true },
            4: { name: `等待時間`, type: `float`, required: false }
        },
        directions: `模擬滑鼠點擊行為，輸入等待時間以等待事件完成。`
    },
    mdbclick: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            element: { name: ``, type: `element`, required: true },
            2: { name: `定位方式`, type: `string`, required: true },
            3: { name: `定位字串`, type: `string`, required: true },
        },
        directions: `模擬滑鼠雙擊定位的元素。`
    },

    key_in: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            element: { name: ``, type: `element`, required: true },
            2: { name: `定位方式`, type: `string`, required: true },
            3: { name: `定位字串`, type: `string`, required: true },
            4: { name: `填入字串`, type: `string`, required: false },
            5: { name: `是否為時間`, type: `boolean`, required: false },
            6: { name: `填入變數`, type: `string`, required: false },
            // 4 與 6 是則一填寫的欄位，因此可用邏輯處理成一個欄位，簡化撰寫流程。比如先比較字串是否為變數名，設定強制轉字串字符或按鈕等等。
        },
        directions: `可填入字串值，或者是填入利用 save_params_to 儲存的變數值。另外需要標示是否為時間欄位，避免造成程式執行錯誤。`
    },

    key_in_table: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            element: { name: ``, type: `element`, required: true },
            2: { name: `定位方式`, type: `string`, required: true },
            3: { name: `定位字串`, type: `string`, required: true },
            4: { name: `填入字串`, type: `string`, required: false },
            6: { name: `填入變數`, type: `string`, required: false },
            // 4 與 6 是則一填寫的欄位，因此可用邏輯處理成一個欄位，簡化撰寫流程。比如先比較字串是否為變數名，設定強制轉字串字符或按鈕等等。
        },
        directions: `可在表格中填入字串值，或者是填入利用 save_params_to 儲存的變數值。`
    },

    tap: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            element: { name: ``, type: `element`, required: true },
            2: { name: `定位方式`, type: `string`, required: true },
            3: { name: `定位字串`, type: `string`, required: true },
            4: { name: `特殊鍵名稱`, type: `string`, required: true },
            5: { name: `特殊鍵名稱`, type: `string`, required: false },
            // 可直接合併為一個欄位，用自串解析的方式區分不同特殊鍵。
        },
        directions: `可以模擬輸入特殊鍵，如 tab enter 等等。`
    },

    select: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            element: { name: ``, type: `element`, required: true },
            2: { name: `定位方式`, type: `string`, required: true },
            3: { name: `定位字串`, type: `string`, required: true },
            4: { name: `選擇值`, type: `string`, required: true },
        },
        directions: `選取下拉選單中的選項。`
    },

    save_params_to: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            element: { name: ``, type: `element`, required: true },
            2: { name: `定位方式`, type: `string`, required: true },
            3: { name: `定位字串`, type: `string`, required: true },
            6: { name: `參數名稱`, type: `string`, required: true },
        },
        directions: `將目標元素的 text or attribute 以參數名稱儲存。`
    },

    compare: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            element: { name: ``, type: `element`, required: true },
            2: { name: `定位方式`, type: `string`, required: true },
            3: { name: `定位字串`, type: `string`, required: true },
            4: { name: `比較值`, type: `string`, required: false },
            6: { name: `比較參數`, type: `string`, required: false },
            // 4 與 6 是則一填寫的欄位，因此可用邏輯處理成一個欄位，簡化撰寫流程。比如先比較字串是否為變數名，設定強制轉字串字符或按鈕等等。
        },
        directions: `將目標元素的 text or attribute 與比較值或比較參數進行比較。`
    },

    login: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },},
        directions: `根據設定資料進行登入行為。`
    },
    web_connection: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            5: { name: `連線網址`, type: `string`, required: true }
        },
        directions: `與 admin 合成完整網址。`
    },
    wait_jump: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            5: { name: `原始網址`, type: `string`, required: true }
        },
        directions: `與 admin 合成完整網址。`
    },
    function: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            2: { name: `自定義方法名稱`, type: `string`, required: true },
            3: { name: `變數 1`, type: `string`, required: false },
            4: { name: `變數 2`, type: `string`, required: false },
            5: { name: `變數 3`, type: `string`, required: false },
            6: { name: `變數 4`, type: `string`, required: false }
        },
        directions: `需填自定義方法名稱, 與變數 1 ~ 4 。`
    },
    sleep: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            4: { name: `等待時間`, type: `float`, required: false }
        },
        directions: `單位 : 秒, 預設 1 秒。`
    },
    report_text: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            4: { name: `文字段落`, type: `string`, required: false },
        },
        directions: `可在報表中加入文字段落。`
    },

    switch: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },},
        directions: `透過切換到下一個 window_handle ，將控制目標切換到彈出視窗。`
    },

    backto: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            4: { name: `關閉彈出視窗`, type: `string`, required: false },
            // 建議改成按鈕
        },
        directions: `從彈出視窗返回主頁面，可輸入 yes 來關閉彈出視窗。`
    },

    load_params: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            6: { name: `參數名稱`, type: `string`, required: true },
        },
        directions: `從已儲存的參數取得值。`
    },

    pic: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },},
        directions: `儲存螢幕截圖。`
    },

    scroll: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
            element: { name: `滾動元素`, type: `element`, required: false },
            4: { name: `捲動橫軸`, type: `float`, required: true },
            5: { name: `捲動縱軸`, type: `float`, required: true },
        },
        directions: `捲動指定滾動元素的捲軸，無指定時，滾動整個頁面視窗。輸入捲動比例來捲動卷軸， 0 代表最左或最上， 1 代表最右或最下。`
    },

    end: {
        var: {
            0: { name: `標記`, type: `tag`, required: false },
            1: { name: `type`, type: `tag`, required: false },
        },
            
        directions: `結束測試流程。`
    },
}

class ScriptElement{
    static UpperClass = ScriptElement;
    static inserPointStr = ``;
    static Count = 0;
    static LastInserPoint = $(``);
    static itemClass = ``;
    static Maps = ActionTypeMap;
    static textConfig(text){return textConfig(text);}
    static UpDataLast(){
        let inserTo = this.getLastInserPoint();
        console.log(`${this.itemClass} LastInserPoint UpData`);
        console.log(`inserPointStr : ${this.inserPointStr}`)
        console.log(`LastInserPoint : ${this.LastInserPoint}`)
        console.log(`inserArea : ${this.UpperClass.LastInserPoint}`)
        this.LastInserPoint = this.UpperClass.LastInserPoint.children(`.${this.itemClass}:last-child`);
        let temp = this.LastInserPoint.find(this.inserPointStr);
        if(temp.length>0){
            this.LastInserPoint = temp;
        }
        console.log(`UpData Done`);
        console.log(`${this.itemClass} last inser point = ${this.LastInserPoint}`);
        return this.LastInserPoint;
    }
    static getLastInserPoint(){
        return this.LastInserPoint;
    }
    static get(inputelement){
        // 將元素轉為 Jquery
        const element = $(inputelement);
        // 找到 varArea
        const varArea = element.children(`.varArea`);
        console.log(`element = ${element}`);
        // 找到 type
        const type = varArea.find(`.type`).attr(`value`);
        console.log(`type = ${type}`)
        const actionMap = this.Maps[`${type}`];
        let output = {};
        for(let i = 0; i < 7; i++){
            let value = ``;
            if(actionMap.var.hasOwnProperty(`${i}`)){
                const varName = actionMap.var[`${i}`].name;
                value = element.find(`.${varName}`).attr(`value`);
                console.log(`${value}`);
            }else{
                value = ``;
            }
            output[`${i}`] = value;
        }
        return output;
    }
}
class ScriptArea extends ScriptElement{
    static LastInserPoint = $(`#scriptArea`);
}
class Behavior extends ScriptElement{
    static itemClass = `behavior`;
    static UpperClass = ScriptArea;
    static inserPointStr = `.${this.itemClass}`;
    static Add = (action={}) => {
        // 插入新的 Behavior
        // 計數器加一
        this.Count += 1;
        let tag = action[`0`];
        let type = action[`1`];
        let Name = action[`2`];
        let showName = ``;
        if (Name != `nan`) {
            showName = this.textConfig(Name);
        } else {
            // 如果沒有給名稱，使用預設名稱
            // 做一個簡單的字串標準化
            if (this.Count < 8) {
                Name = `Behavior 00${this.Count + 1}`;
            } else if (this.Count < 98) {
                Name = `Behavior 0${this.Count + 1}`;
            } else {
                Name = `Behavior ${this.Count + 1}`;
            }
            showName = Name;
        }

        // 插入新的 Behavior
        $(`<div class="behavior item mx-auto mb-2 col-12 border border-black rounded-1 justify-content-center ps-1" draggable="true">
            <div class="row behaviorName varArea droppable py-2 px-1 m-0">
                ${showName}
                <div class="標記" value="${tag}" style="display: none;"></div>
                <div class="type" value="${type}" style="display: none;"></div>
                <div class="名稱" value="${Name}" style="display: none;"></div>
            </div>
        </div>`).appendTo(this.UpperClass.LastInserPoint);
        this.UpDataLast(this);
    }
}
class Action extends ScriptElement{
    static UpperClass = Behavior;
    static itemClass = `action`;
    static inserPointStr = `.showBox`;
    static NanCount = 0;
    static Add = (action={}) => {
        // 插入新的 Action
        if (action != {}) {
            if(action['1'] != `nan`){
                // Count 計數器 +1
                this.Count += 1;
                // 如果尚未建立 Behavior ，新增一個 Behavior
                if (Behavior.Count == 0) {
                    Behavior.Add(action);
                }
                // 實作新 Action
                $(`
                <div class="row action droppable col-12 mb-1 mx-auto pe-1 item" dataindex="${this.Count}" enter="0">
                    <div class="col-2 number ">${this.Count}</div>
                    <div class="col-10 showBox varArea border border-black rounded-1" draggable="true">
                        <div class="row actionName mx-0 my-1 mb-1">${action['1']}</div>
                    </div>
                </div>
                `).appendTo(this.UpperClass.LastInserPoint);
                this.UpDataLast();
                Var.Add.all(action);
            }else{
                this.NanCount += 1;
            }
        }
    }
}

class Var{
    static Add = {
        all: (action = {}) => {
            if(Action.Maps.hasOwnProperty(`${action[`1`]}`)){
                let varMap = Action.Maps[`${action[`1`]}`].var;
                for (let i = 0; i < 7; i++) {
                    if (varMap.hasOwnProperty(`${i}`)) {
                        const theVar = varMap[`${i}`];
                        console.log(`add Var ${Behavior.Count}-${Action.Count}-${theVar.name}`)
                        if (theVar.type == `string`) {
                            this.Add.string(theVar.name, action[`${i}`]);
                        } else if (theVar.type == `float`) {
                            this.Add.float(theVar.name, action[`${i}`]);
                        } else if (theVar.type == `boolean`) {
                            this.Add.boolean(theVar.name, action[`${i}`]);
                        }else if (theVar.type == `tag`) {
                            this.Add.tag(theVar.name, action[`${i}`]);
                        }
                    }
                }
            }
        },

        // 以下三種應該要不一樣，待補充設計
        tag: (VarName, VarValue = '') => {
            Action.LastInserPoint.add(`<div class="row m-0 mt-1 align-items-center actionVar" style="display: none;">`+
                `<label for="No${Behavior.Count}-${Action.Count}-${VarName}" class="fs-6 col-4 me-auto col-form-label ps-0 pe-1">${VarName}</label>`+
                `<div class="col-8 ms-auto me-0 pe-0">`+
                    `<input type="text" class="${VarName} form-control fs-6 p-1s me-0" id="No${Behavior.Count}-${Action.Count}-${VarName}" value='${VarValue}'>`+
                `</div>`+
            `</div>`).appendTo(Action.LastInserPoint);
        },
        string: (VarName, VarValue = '') => {
            Action.LastInserPoint.add(`<div class="row m-0 mt-1 align-items-center actionVar">`+
                `<label for="No${Behavior.Count}-${Action.Count}-${VarName}" class="fs-6 col-4 me-auto col-form-label ps-0 pe-1">${VarName}</label>`+
                `<div class="col-8 ms-auto me-0 pe-0">`+
                    `<input type="text" class="${VarName} form-control fs-6 p-1s me-0" id="No${Behavior.Count}-${Action.Count}-${VarName}" value='${VarValue}'>`+
                `</div>`+
            `</div>`).appendTo(Action.LastInserPoint);
        },
        float: (VarName, VarValue = '') => {
            Action.LastInserPoint.add(`<div class="row m-0 mt-1 align-items-center actionVar">`+
                `<label for="No${Behavior.Count}-${Action.Count}-${VarName}" class="fs-6 col-4 me-auto col-form-label ps-0 pe-1">${VarName}</label>`+
                `<div class="col-8 ms-auto me-0 pe-0">`+
                    `<input type="text" class="${VarName} form-control fs-6 p-1s me-0" id="No${Behavior.Count}-${Action.Count}-${VarName}" value='${VarValue}'>`+
                `</div>`+
            `</div>`).appendTo(Action.LastInserPoint);
        },
        boolean: (VarName, VarValue = '') => {
            Action.LastInserPoint.add(`<div class="row m-0 mt-1 align-items-center actionVar">`+
                `<label for="No${Behavior.Count}-${Action.Count}-${VarName}" class="fs-6 col-4 me-auto col-form-label ps-0 pe-1">${VarName}</label>`+
                `<div class="col-8 ms-auto me-0 pe-0">`+
                    `<input type="text" class="${VarName} form-control fs-6 p-1s me-0" id="No${Behavior.Count}-${Action.Count}-${VarName}" value='${VarValue}'>`+
                `</div>`+
            `</div>`).appendTo(Action.LastInserPoint);
        },
    }

}
function logItem(item={}){
    let text = `{ `;
    for(let i = 0; i < 7; i++){
        let value = `no set value`;
        if(item.hasOwnProperty(`${i}`)){
            const temp = item[`${i}`];
            if (temp!=``){
                value = temp;
            }         
        }
        text += `${i}: ${value}, `;
    }
    text += `}`;
    console.log(`${text}`);
}
let scriptItem = {
    Behavior: Behavior,
    Action: Action,
    Var:Var,
    logItem: (item={})=>{return logItem(item);},
}

export { Ajax, doAjax, doAjaxUnStopInterval, drag, scriptItem};