var label;
// 获取画布canvas对象
var canvas = document.querySelector("canvas");

//手写板
var hwPad = new SignaturePad(canvas, {
  backgroundColor: 'rgb(255,255,255)', // 画白色背景，否则默认透明或者黑色，笔也是黑色，出来就是全黑
  minWidth: 3,
  maxWidth: 3
});

//按比例缩放，改变窗口大小时会清除
function resizeCanvas() {
  var ratio =  Math.max(window.devicePixelRatio || 1, 1);
  canvas.width = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;
  //canvas.getContext("2d").scale(ratio, ratio);
  hwPad.clear();
}

window.onresize = resizeCanvas;
resizeCanvas();


function get_raw_dataset() {

        //用 request 请求 与后端通信, POST
    var request = new XMLHttpRequest();

    // 处理请求返回
    console.log("开始获取文件信息");

    request.onreadystatechange = function () {
          if (request.readyState == 4) {
              if ((request.status >= 200 && request.status < 300) || request.status == 304) {
                 //console.log(request.response)
                    var label_list = JSON.parse(request.response).label_list;
                    show_li(label_list);
              }
          }
      };

    request.open("POST", "/adddata/get_raw_dataset"); //具体的POST
    request.setRequestHeader('content-type', 'application/json');
    request.send();
}

/*
function update() {
    var request = new XMLHttpRequest();

    // 处理请求返回
    console.log("开始获取文件信息");

    request.onreadystatechange = function () {
          if (request.readyState == 4) {
              if ((request.status >= 200 && request.status < 300) || request.status == 304) {
                 //console.log(request.response)
                    var label_list = JSON.parse(request.response).label_list;

                        var li_wrap = document.getElementById('select_label');
                        var lis = li_wrap.childNodes;
                        for(var i in lis){
                            lis[i].innerHTML = label_list[i].label.toString() + '<span class = "color_text" >'  +'(' + label_list[i].len.toString() +')'  + '</span>';
                        }

              }
          }
      };

    request.open("POST", "/adddata/get_raw_dataset"); //具体的POST
    request.setRequestHeader('content-type', 'application/json');
    request.send();


}*/

//保存图片数据。图片+标签
function save_img(label) {
    imgData = {URL: hwPad.toDataURL().substring(22), LABEL:label}; //获取手写板的图片信息、去掉b64头部、JSON化, 便于与后端通信

    //用 request 请求 与后端通信, POST
    var request = new XMLHttpRequest();
    // 处理请求返回
    request.onreadystatechange = function () {
          if (request.readyState == 4) {
              if ((request.status >= 200 && request.status < 300) || request.status == 304) {
                  //console.log(request.response)
                  alert("成功保存" + request.response + "张" + label);
                    hwPad.clear();
                    //update();
              }
          }
      };

    request.open("POST", "/adddata/save"); //具体的POST
    request.setRequestHeader('content-type', 'application/json');
    request.send(JSON.stringify(imgData));
    //console.log(JSON.stringify(imgData))

}



//按钮事件绑定
//清除按钮
document.getElementById('pad-clear').addEventListener("click", function (event) {
  hwPad.clear();
  document.querySelector('#pad-result').innerHTML="";
  katex.render("", document.getElementById('Latex'), {
      throwOnError: false
    });
});



//橡皮擦按钮
document.getElementById('pad-erase').addEventListener('click', function () {
  //hwPad.dotSize = 20;
  hwPad.penColor = "rgb(255,255,255)";
    hwPad.minWidth = 20;
    hwPad.maxWidth = 20;
});

//画笔按钮
document.getElementById('pad-draw').addEventListener('click', function () {
    //hwPad.lineWidth = 10;
  hwPad.penColor = "rgb(0,0,0)";
    hwPad.minWidth = 3;
    hwPad.maxWidth = 3;
});


//保存按钮
document.getElementById('pad-save').addEventListener('click', function() {
  if (hwPad.isEmpty()) {
    alert("请书写一个数字");
  } else {
     save_img(label.toString());
  }
});



function show_li(label_list){
    console.log(label_list);

    var li_wrap = document.getElementById('select_label');

    for(var i in label_list){
        var item = document.createElement("li");
        item.innerHTML = label_list[i].label.toString() + '<span class = "color_text" >'  +'(' + label_list[i].len.toString() +')'  + '</span>';
        item.setAttribute('value', i);
        item.addEventListener('click', function () {
            label = label_list[this.getAttribute('value')].label.toString();
            //alert(label.toString());
            $(this).addClass("selected").siblings().removeClass("selected");
        });
        li_wrap.appendChild(item);
    }

}

window.onload = function() {
    get_raw_dataset();
};



