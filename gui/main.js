import {Admin, Ajax, doAjax, doAjaxUnStopInterval, drag} from "./admin.js";  

// 網頁認證

// 初始化
doAjax("/init", "POST");

function getMethods(obj) {
    var result = [];
    for (var id in obj) {
        try {
            if (typeof (obj[id]) == "function") {
                result.push(id + ": " + obj[id].toString());
            }
        } catch (err) {
            result.push(id + ": inaccessible");
        }
    }
    return result;
}

function showPath(path = '') {
    // 整理過長的 Path
    let pathList = path.split('/')
    let pathShow = ''
    let pathLength = pathList.length
    if (pathLength > 1) {
        pathShow += `.../${pathList[pathLength - 1]}`;
    }

    else {
        for (let i of pathList) {
            pathShow += `${i}`;
        }
    }
    return pathShow
}

function treeUpDataCeller(response) {
    if (response) {
        let scriptList = response.result;
        console.log(`Get upDataScriptList len = ${scriptList.length}`);
        treeUpData(scriptList);
    }
}

function pathConfigHandler(response) {
    // 取得後端傳來的 path 資料以後，將 path 更新在頁面上。
    if (response) {
        let key = response.result.key;
        let value = response.result.value;
        console.log(`Get pathConfig {${key}:${value}}`)
        let pathShowElement = $(`.item.path[key="${key}"] .show`);
        pathShowElement.text(`${pathShowElement.attr('name')}: ${showPath(value)}`);
        if (key == 'input_path') {
            console.log(`Ask upDataScriptList`);
            doAjax("/do/upDataScriptList", "POST", treeUpDataCeller);
        }
    }
}
function driverConfigHandler(response) {
    // 取得後端傳來的 driverSet 資料以後，發出 console.log 表示接收成功。
    if (response) {
        let key = response.result.key;
        let value = response.result.value;
        console.log(`Get driverConfig {${key}:${value}}`);
        const label = $(`div.item.driverSet[key="${key}"] > label`);
        console.log(`name${value} = ${label.attr(`name${value}`)}`);
        label.text(`${label.attr(`name${value}`)}`);
    }
}

function elementConfigHandler(response) {
    // 取得後端傳來的 element XPath 資料以後，將 XPath 更新在頁面上。
    if (response) {
        let key = response.result.key;
        let value = response.result.value;
        console.log(`Get elementConfig {${key}:${value}}`)
        let show = $(`div.item.elementLocator[key="${key}"] div.item.show > input`)
        show.attr('value', value);
    }
}

function textConfigHandler(response) {
    // 取得後端傳來的 text 資料以後，發出 console.log 表示接收成功。
    if (response) {
        let key = response.result.key;
        let value = response.result.value;
        console.log(`Get textConfig {${key}:${value}}`)
    }
}

function pathConfig(e) {
    let keyValue = e.currentTarget.getAttribute('key');
    let valueValue = 0;
    let request = { configType: 'path', key: keyValue, value: valueValue };
    console.log(`Ask textConfig { 'configType': path, 'key': ${keyValue}}, 'value': ${valueValue}}`);
    doAjax("/do/setConfig", "POST", pathConfigHandler, request);
}
function driverConfig(e) {
    let keyValue = e.currentTarget.getAttribute('key');
    let valueValue = 0;
    let request = { configType: 'driverSet', key: keyValue, value: valueValue };
    console.log(`Ask textConfig { 'configType': driverSet, 'key': ${keyValue}}, 'value': ${valueValue}}`);
    doAjax("/do/setConfig", "POST", driverConfigHandler, request);
}
function elementConfig(e) {
    let keyValue = e.currentTarget.getAttribute('key');
    let valueValue = 0;
    let request = { configType: 'elementLocator', key: keyValue, value: valueValue };
    console.log(`Ask textConfig { 'configType': elementLocator, 'key': ${keyValue}}, 'value': ${valueValue}}`);
    doAjax("/do/setConfig", "POST", elementConfigHandler, request);
}
function textConfig(e) {
    let keyValue = e.currentTarget.getAttribute('key');
    let valueValue = $(`#${keyValue}Input`).val();
    let request = { configType: 'userInformation', key: keyValue, value: valueValue };
    console.log(`Ask textConfig { 'configType': userInformation, 'key': ${keyValue}}, 'value': ${valueValue}}`);
    doAjax("/do/setConfig", "POST", textConfigHandler, request);
}

// 是訂綁定設定業面按鈕的程式
function setConfigFunction(configItems=$(`div.item.config`)){
    for(let item of configItems){
        const functionPoint = $(item).find(`.functionPoint`);
        const type = functionPoint.attr(`configType`);
        if(type == `path`){
            functionPoint.on(`click`,pathConfig);
        }else if(type == `driverSet`){
            functionPoint.on(`click`,driverConfig);
        }else if(type == `userInformation`){
            functionPoint.on(`click`,textConfig);
        }else if(type == `elementLocator`){
            functionPoint.on(`click`,elementConfig);
        }else{
            console.log(`${functionPoint}, type=${type}, error.`);
        }
        
    }
}

// 將 div.temp.text() 的內容以 html 形式寫入對應位置
// tempSet
let tempSet = $(`div.temp.setItem`).text();
Admin.page.Set.html(tempSet);

// tempTest
let tempTest = $(`div.temp.testItem`).text();
Admin.page.View.html(tempTest);

// 將 pathShow 元素初始化
let pathItems = $(`div.item.path div.item.show`)
for (let i of pathItems) {
    i.textContent = `${i.getAttribute('name')}: ${showPath(i.getAttribute('path'))}`;
}

// 幫頁面轉換按鈕綁定事件
$(`#set`).on('click', function () {
    let btn = $(this).parent(`.btn`);
    btn.toggleClass(`btn-primary`);
    btn.toggleClass(`border`);
    btn.toggleClass(`border-dark`);
    Admin.pageSwap.TestAndSet();
});

// 幫關閉編輯室窗按鈕綁定事件
$(`#editFrame>.head .close`).on('click', function () {
    Admin.closeEditer();
});

// 幫設定頁面的按鈕綁定事件

// 實作 treeView class
let tree = new Admin.treeView($(`.list-group`));

function treeUpData(list){
    tree.upDateItem(list);
}

let regressionInput = Admin.page.Test.find(`#regressionInput`);
let regressionSubmit = $('#regressionSubmit');
function askRegression(scriptListValue=[],timeStringValue=``) {
    let request = { scriptSelection: scriptListValue, timeString:timeStringValue };
    doAjax("/do/regression", "POST", false, request);
}
regressionSubmit.on("click",()=>{
    askRegression(tree.getSelection(),regressionInput.val());
});

let bt = $('#start');
bt.on("click",()=>{
    Admin.startTest(tree.getSelection());
});
setConfigFunction();