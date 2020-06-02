// 获取画布canvas对象
var canvas = document.querySelector("canvas");


//手写板对象
var signaturePad = new SignaturePad(canvas, {
  backgroundColor: 'rgb(255,255,255)', // 画白色背景，否则默认透明或者黑色，笔也是黑色，出来就是全黑
  minWidth: 3,
  maxWidth: 3
});


//实时响应
signaturePad.onEnd = function() {
    send_img();

};


//按比例缩放
function resizeCanvas() {
        // When zoomed out to less than 100%, for some very strange reason,
        // some browsers report devicePixelRatio as less than 1
        // and only part of the canvas is cleared then.
        var context = canvas.getContext("2d"); //context.getImageData(0,0,canvas.width,canvas.height)
        var imgData = signaturePad ? signaturePad.toData() : null;
        var ratio =  Math.max(window.devicePixelRatio || 1, 1);
        canvas.width = canvas.offsetWidth * ratio;
        canvas.height = canvas.offsetHeight * ratio;
        context.scale(ratio, ratio);
        // context.putImageData(imgData,0,0);
        imgData && signaturePad.fromData(imgData);
}

window.onresize = resizeCanvas;
resizeCanvas();

//点击复制 LaTeX 代码
function copy_text(){
    var clipboard = new ClipboardJS('#pad-result', {
        target: function() {
            return document.querySelector('#pad-result');
        }
    });
}
document.getElementById('pad-result').onclick = copy_text();


//点击复制渲染图片
function copy_latex_img() {
    if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)){}

    else {
        html2canvas(document.getElementById('Latex')).then(function (canvas) {
            canvas.toBlob(function (blob) {
                const item = new ClipboardItem({"image/png": blob});
                navigator.clipboard.write([item]);
            });
            console.log(canvas.toDataURL('image/png'));
        });
    }
}
document.getElementById('Latex').addEventListener('click', function() {
    copy_latex_img();
});





//给后端服务器传图片信息
function send_img() {
    imgData = {URL: signaturePad.toDataURL().substring(22)}; //JSON

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
/*
                  //转换为canvas
                  html2canvas(document.getElementById('Latex')).then(function(canvas) {
                      $('#Latex').empty();
                        var image = new Image();
                        image.id = "Latex_img";
                        image.src = canvas.toDataURL();
                        document.getElementById('Latex').appendChild(image);
                  });
*/

              }
          }
      };
    request.open("POST", "./predict");
    request.setRequestHeader('content-type', 'application/json');
    request.send(JSON.stringify(imgData));
}




//按钮事件绑定
//清除按钮
document.getElementById('pad-clear').addEventListener("click", function (event) {
  signaturePad.clear();
  document.querySelector('#pad-result').innerHTML="";
  katex.render("", document.getElementById('Latex'), {
      throwOnError: false
    });
});

/*
//识别按钮
document.getElementById('pad-predict').addEventListener("click", function (event) {
  if (signaturePad.isEmpty()) {
    alert("请书写一个数字");
  } else {
     send_img();
  }
});
*/

//橡皮擦按钮
document.getElementById('pad-erase').addEventListener('click', function () {
  //signaturePad.dotSize = 20;
    signaturePad.penColor = "rgb(255,255,255)";
    signaturePad.minWidth = 20;
    signaturePad.maxWidth = 20;
});

//画笔按钮
document.getElementById('pad-draw').addEventListener('click', function () {
    //signaturePad.lineWidth = 10;
    signaturePad.penColor = "rgb(0,0,0)";
    signaturePad.minWidth = 3;
    signaturePad.maxWidth = 3;
});


