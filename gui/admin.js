import {Ajax, doAjax, doAjaxUnStopInterval, drag, scriptItem} from "./tool.js";
class treeView {
    constructor(treeElement = $('')){

        // 將 listGroup 物件存成 treeElement 屬性
        this.treeElement = treeElement;

        // 暫存上一個選擇的選項 index ，預設為 0
        this.lastSelect = 0;
        
        // 在 list-group-item 加上 js event
        this.addEvent();
        

    }
    clearSelection(){
        this.treeElement.children().removeClass("active");
    }
    getSelection(){
        let output=[];            
        // 取得 treeElement 中被選取的 element.text()
        let selections = this.treeElement.children(".active");
        $.each(selections,function(){
            output.push($(this).text());
        });
        console.log(output);
        return output;
    }
    listItemClicked(e){
        e.preventDefault();            
        let selectElement = $(e.target);
        let all = selectElement.parent().children();
        if(e.shiftKey){
            // 範圍選取
            // 清除舊有選擇
            all.removeClass("active");
            let shiftSelect = selectElement.index();
            let start = 0;
            let end = 0;
            if(shiftSelect > this.lastSelect){
                start = this.lastSelect;
                end = shiftSelect+1;
            }else{
                start = shiftSelect;
                end = this.lastSelect+1;
            }
            let adds = all.slice(start,end);
            adds.addClass("active");

        }else if(e.altKey){
            // 全選
            // 更新最後選擇
            this.lastSelect = selectElement.index();
            // 全部選取
            all.addClass("active");
        }else if(e.ctrlKey){
            // 複數選取
            // 更新最後選擇
            this.lastSelect = selectElement.index();
            // 動態變更選取狀況
            selectElement.toggleClass("active");
        }else{
            // 更新最後選擇
            this.lastSelect = selectElement.index();
            selectElement.addClass("active").siblings().removeClass("active");    
        }   
    }
    listItemDbclicked(e){
        // 雙擊開啟編輯畫面
        // 阻止預設行為
        e.preventDefault();

        // 取得點擊的 Script Name
        let selectElement = $(e.target);
        let scriptName = selectElement.text();
        let request = {ScriptName: scriptName};

        // 呼叫管理員開啟編輯器
        Admin.openEditer(scriptName);
        
        
        // 要求ajax
        doAjax("/ask/readScriptByName", "POST",function(response){
            if (response) {
                let DataFrame = response.result;
                console.log(`Get DataFrame, len = ${DataFrame.length}`);
                console.log(`${DataFrame}`);

                for(let row of DataFrame){
                    // 如果Action Name == Behavior ，插入新的 Behavior 
                    if( row['1'].toUpperCase() == 'BEHAVIOR' ){
                        Admin.newBehavior(row);
                    }else if(row['1'].toUpperCase() == 'nan'){
                        // NanCount + 1
                        Admin.script.Action.NanCount += 1;
                    }else{
                        // 新增 Action
                        Admin.newAction(row);
                    }

                    // 如果 NanCount > 10 ，終止迴圈
                    if(Admin.script.Action.NanCount > 10){
                        break;
                    }
                }
                
                drag.addListeners();
                
            }
        },request);
    }
    addEvent(){
        this.treeElement.on("click",this.listItemClicked.bind(this));
        this.treeElement.on("dblclick",this.listItemDbclicked.bind(this));
    }
    upDateItem(list=[]){
        this.treeElement.children().remove();
        if(list.length == 0){
            this.treeElement.append( `<a href="#" class="list-group-item list-group-item-action list-ss">No Excel be Finded.</a>`);
        }else{
            for(let i of list){
                this.treeElement.append( `<a href="#" class="list-group-item list-group-item-action list-ss">${i}</a>`);
            }
        }
    }
}
class Admin {
    static treeView = treeView;
    // 此類別紀錄物件的狀態
    // TestAndSet : true 代表顯示 Test page， false 代表顯示 Set page
    static page = {
        Swap: {
            TestAndSet: true, //true 代表顯示 Test page， false 代表顯示 Set page
            ViewAndEdit: true
        },
        flag: {
            Test: false,
            WebWindow: false
        },
        Test: $(`#testItem`),
        Set: $(`#setItem`),
        View: $(`#viewItem`),
        Edit: $(`#editItem`)
    }
    static script = {
        Area: $(`#scriptArea`),
        Name:{
            Element: $(`#scriptName`),
            FullText:``,
        },
        UpDataName: (scriptName = ``) => {
            this.script.Name.FullText = scriptName;
            this.script.Name.Element.text(this.textConfig(scriptName));
        },
        getAllActionData:()=>{
            let behaviors = $(`.behavior`);
            let output = [];
            let temp = undefined;
            for(let behavior of behaviors){
                temp = this.script.Behavior.get(behavior);
                console.log(`Behavior.get`);
                scriptItem.logItem(temp);
                output.push(temp);
                let actions = $(behavior).find(`.action`);
                for(let action of actions){
                    temp = this.script.Action.get(action);
                    console.log(`Action.get`);
                    scriptItem.logItem(temp);
                    output.push(temp);
                }
            }
            return output;
        },

        save:()=>{
            // 取得所有 action 的資料
            let actionList = this.script.getAllActionData();
            console.log(`${actionList}`)

            // 宣告一個計數器來編號
            const data = {
                ScriptName:this.script.Name.FullText,
                ScriptActions:actionList,
            };
            doAjax("/do/saveScript", "POST",(response)=>{if(response.status ==`ok`){console.log(`saveScript success`)}},data);
        },
        Behavior: scriptItem.Behavior,
        Action: scriptItem.Action,
        Var: scriptItem.Var,
    }
    
    static openEditer(scriptName) {
        console.log(`Do Open:{ View: ${this.page.View}, Edit:${this.page.Edit}}`)
        this.page.View.hide();
        this.page.Edit.show();
        this.script.UpDataName(scriptName);
    }
    static closeEditer() {
        console.log(`Do Close:{ View: ${this.page.View}, Edit:${this.page.Edit}}`)
        this.page.Edit.hide();
        this.page.View.show();
        this.script.save();
        this.script.Area.html(``);
        this.script.Behavior.Count = 0;
        this.script.Action.Count = 0;
        this.script.Action.NanCount = 0;
    }
    static newBehavior(action={}) {
        // 插入新的 Behavior
        this.script.Behavior.Add(action);
    }
    static newAction(action = {}) {
        // 如果名稱不為 nan ，插入新 Action
        this.script.Action.Add(action);
    }

    // 切換測試頁面與設定頁面
    static pageSwap = {
        TestAndSet:()=>{
            if (this.page.Swap.TestAndSet) {
                this.page.Test.hide();
                this.page.Set.show();
                this.page.Swap.TestAndSet = false;
            } else {
                this.page.Test.show();
                this.page.Set.hide();
                this.page.Swap.TestAndSet = true;
            }
        },
    }

    // 避免字串過長影響排版
    static textConfig(text = '', length = 16){
        let temp = '';
        if(text.length > length){
            temp = `${text.slice(0,length)}...`;
        }else{
            temp = text;
        }
        return temp;
    }

    static logText = {
        timeoutID:0,
        // 如果 ajax 返回 done，
        ifDone:(response)=>{
            if (response) {
                let testing = response.result;
                console.log(`Get testing = ${testing}`);
                if(testing == false){
                    this.page.flag.Test = false;
                    window.clearInterval(this.logText.timeoutID);
                }
            }
        },
        DoneOrNot:()=>{
            this.logText.timeoutID = window.setInterval(() => {
                if(this.page.flag.Test){
                    doAjax("/ask/getTestingFlag", "POST",this.logText.ifDone);
                }
            }, 100);
        },
    }
    // 開始測試
    static startTest(scriptList=['']){
        if(this.page.flag.Test == false){
            this.page.flag.Test = true;
            let request = {scriptSelection: scriptList};
            console.log(`Ask test { 'scriptSelection': ${scriptList}}`)
            doAjax("/do/test", "POST",false,request);
            this.logText.DoneOrNot();
        }
    }
}

export {Admin, Ajax , doAjax, doAjaxUnStopInterval, drag};