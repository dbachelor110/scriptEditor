// 使用 jQuery 撰寫
// https://api.jquery.com/jquery.ajax/
class Ajax {
    constructor(url="", method="GET", responseHandler, data={}) {
        // 請求的 URL
        this.url = url;

        // 請求的方法（預設為 GET）
        this.method = method;

        // 回應處理器函式
        this.responseHandler = responseHandler;

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
            console.log(`Ask AJAX`);
            // 發送 AJAX request
            $.ajax({
                url: this.url,
                method: this.method,
                async: this.async,
                data: JSON.stringify(this.data),
                dataType: "json",
                contentType: "application/json",
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
                // //須接受一個參數，來處理回傳的 json 資料
                // responseHandlerExample(response){
                //    console.log(`Response = ${response}`);
                // }
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