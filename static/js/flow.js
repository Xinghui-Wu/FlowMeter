/*
* 页面铺满屏幕
*/
$(document).ready(function () {
    var screenHeight = document.documentElement.clientHeight;
    var contentHeight = screenHeight - 60 - 60;
    document.getElementById("content").style.height = contentHeight + "px";
});


// 是否开始监听标记
var start = false;
// 实时下载、上传速度
var downloadNow = 0;
var uploadNow = 0;


/*
* 选择设备
*/
function selectDevice() {
    $.ajax({
        url: "select/",
        type: "GET",
        data: {
            "device_index": $("#device-index").val()
        },
        success: function (data) {
            start = true;
        },
        error: function () {
            alert('Error: selectDevice')
        }
    })
}


/*
* 获取流量数据
*/
function getFlowData() {
    $.ajax({
        url: "get_flow/",
        type: "GET",
        data: {
        },
        success: function (data) {
            var results = JSON.parse(data);

            $("#real-time-download").text(results["download_now"]);
            $("#real-time-upload").text(results["upload_now"]);
            $("#history-download").text(results["download_history"]);
            $("#history-upload").text(results["upload_history"]);

            downloadNow = results["download_now"];
            uploadNow = results["upload_now"];
        },
        error: function () {
            alert('Error: getFlowData')
        }
    })
}


/*
* 地点分析
*/
function analyzeAddresses() {
    $.ajax({
        url: "address/",
        type: "GET",
        data: {
        },
        success: function (data) {
            var results = JSON.parse(data);
            var topDownloadAddresses = sortDict(results["download"]);
            var topUploadAddresses = sortDict(results["upload"]);

            $("#top-download-addresses").text(topDownloadAddresses);
            $("#top-upload-addresses").text(topUploadAddresses);
        },
        error: function () {
            alert('Error: analyzeAddresses')
        }
    })
}


/*
* 域名分析
*/
function analyzeNames() {
    $.ajax({
        url: "name/",
        type: "GET",
        data: {
        },
        success: function (data) {
            var results = JSON.parse(data);
            var topDownloadNames = sortDict(results["download"]);
            var topUploadNames = sortDict(results["upload"]);

            $("#top-download-names").text(topDownloadNames);
            $("#top-upload-names").text(topUploadNames);
        },
        error: function () {
            alert('Error: analyzeNames')
        }
    })
}


/*
* 突发流量分析
*/
function analyzeBurst() {
    $.ajax({
        url: "burst/",
        type: "GET",
        data: {
        },
        success: function (data) {
            alert(data)
            var results = JSON.parse(data);
            var topBurst = sortDict(results["burst"]);

            $("#top-burst").text(topBurst);
        },
        error: function () {
            alert('Error: analyzeBurst')
        }
    })
}


/*
* 根据字典的值对键进行排序
*/
function sortDict(dict) {
    var top = 5;
    if (top > dict.length) {
        top = dic.length;
    }

    var sortedKeys = [];
    
    for (var i = 0; i < top; i++) {
        var maxKey;
        var max = 0;

        for (var key in dict) {
            if (dict[key] > max) {
                maxKey = key;
                max = dict[key];
            }
        }

        sortedKeys.push(maxKey);
        delete dict[maxKey];
    }

    return sortedKeys;
}


/*
* 绘制实时流量数据折线图
*/
function plotRealTimeTrafficChart() {
    var base = +new Date();
    var interval = 2 * 1000;

    var time = [];
    var download = [];
    var upload = [];

    var now = new Date(base);

    // 添加折线图数据
    function addData(shift) {
        // 计算此刻时间
        now = new Date();
        now = [now.getHours(), now.getMinutes(), now.getSeconds()];
        for (var i = 0; i < 3; i++) {
            if (now[i] < 10) {
                now[i] = "0" + now[i];
            }
        }
        now = now.join(":")
        
        // 从后端更新流量数据
        getFlowData();
        // 从后端更新地址分析结果
        analyzeAddresses();
        // 从后端更新域名分析结果
        analyzeNames();
        // 从后端更新突发流量分析结果
        // analyzeBurst();

        // 列表加入新数据
        time.push(now);
        download.push(downloadNow)
        upload.push(uploadNow)

        // 列表平移
        if (shift) {
            time.shift();
            download.shift();
            upload.shift();
        }
    }

    // Echarts设置
    option = {
        title: {
            text: "实时流量"
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: time
        },
        yAxis: {
            boundaryGap: [0, '50%'],
            type: 'value'
        },
        legend: {

        },
        series: [
            {
                name: '下载',
                type: 'line',
                smooth: true,
                symbol: 'none',
                data: download
            },
            {
                name: '上传',
                type: 'line',
                smooth: true,
                symbol: 'none',
                data: upload
            }
        ]
    };

    // 设置更新时间间隔
    setInterval(function () {
        if (start) {
            addData(time.length > 100);
        }

        trafficChart.setOption({
            xAxis: {
                data: time
            },
            series: [
                {
                    name: '下载',
                    data: download
                }, {
                    name: '上传',
                    data: upload
                }
            ]
        });
    }, interval);

    // 基于准备好的DOM，初始化Echarts实例
    var trafficChart = echarts.init(document.getElementById('traffic-chart'));
    trafficChart.setOption(option)
}