// 获取画布canvas对象
var canvas = document.querySelector("canvas");


//手写板对象
var hwPad = new SignaturePad(canvas, {
  backgroundColor: 'rgb(255,255,255)', // 画白色背景，否则默认透明或者黑色，笔也是黑色，出来就是全黑
  minWidth: 3,
  maxWidth: 3
});


//实时响应
hwPad.onEnd = function() {
    send_img();
};


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


//给后端服务器传图片信息
function send_img() {
    imgData = {URL: hwPad.toDataURL().substring(22)}; //JSON

    //用 request 与后端通信, POST
    var request = new XMLHttpRequest();
    // 处理请求返回
    request.onreadystatechange = function () {
          if (request.readyState == 4) {
              if ((request.status >= 200 && request.status < 300) || request.status == 304) {
                  //console.log(request.response)
                  document.querySelector('#pad-result').innerHTML=request.response; //写结果
                  //渲染公式
                  katex.render(request.response, document.getElementById('Latex'), {
                        throwOnError: false
                  });
              };
          }
      };
    request.open("POST", "./predict");
    request.setRequestHeader('content-type', 'application/json');
    request.send(JSON.stringify(imgData));
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

/*
//识别按钮
document.getElementById('pad-predict').addEventListener("click", function (event) {
  if (hwPad.isEmpty()) {
    alert("请书写一个数字");
  } else {
     send_img();
  }
});
*/

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

