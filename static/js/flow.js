/*
* 页面铺满屏幕
*/
function setFullScreen() {
    var screenHeight = document.documentElement.clientHeight;
    var contentHeight = screenHeight - 60 - 60;
    document.getElementById("content").style.height = contentHeight + "px";
}


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

        },
        error: function () {
            alert('Error: selectDevice')
        }
    })
}


// function test() {
//     $.ajax({
//         url: "/flow/burst/",
//         type: "GET",
//         success: function (data) {
//             let data_obj = JSON.parse(data);
//             {#$("#result1").text(data_obj["upload"])# }
//             {#$("#result2").text(data_obj["download"])# }
//             {#$("#result3").text(data_obj["upload_now"])# }
//             {#$("#result4").text(data_obj["download_now"])# }
//             {#$("#result5").text(data_obj["upload_history"])# }
//             {#$("#result6").text(data_obj["download_history"])# }
//         },
//         error: function () {
//             alert('Error.')
//         }
//     })
// }


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

        },
        error: function () {
            alert('Error: getFlowData')
        }
    })
}


/*
* 绘制实时流量数据折线图
*/
function plotRealTimeTrafficChart() {
    var base = +new Date();
    var interval = 1 * 1000;

    var time = [];
    var download = [];
    var upload = [];

    var now = new Date(base);

    // 添加折线图数据
    function addData(shift) {
        now = new Date();
        now = [now.getHours(), now.getMinutes(), now.getSeconds()];
        for (var i = 0; i < 3; i++) {
            if (now[i] < 10) {
                now[i] = "0" + now[i];
            }
        }
        now = now.join(":")

        time.push(now);
        download.push((Math.random()) * 10);
        upload.push((Math.random()) * 10);

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
        addData(time.length > 100);

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