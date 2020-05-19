from flask import Flask, request
import os
from datetime import timedelta

import predict
import CV

app = Flask(__name__)
app.debug = True


# 设置静态文件缓存过期时间
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

# 不这样可能浏览器会缓存，修改的静态文件不会及时更新


# 首页
@app.route('/')
def root():
    return app.send_static_file('index.html')


# 识别
@app.route('/predict', methods=['POST'])
def predictFromImg():
    if request.method == 'POST':
        print("开始识别")
        # json 可以直接以字典 dict 形式读了
        return predict.predict_all(request.get_json()['URL'], 'b64')


# 保存数据页
@app.route('/adddata')
def adddata_index():
    return app.send_static_file('adddata.html')


# 保存
@app.route('/adddata/save', methods=["POST"])
def save_img():
    if request.method == 'POST':
        print("开始保存")
        img = CV.read_by_type(request.get_json()['URL'], "b64")
        label = str(request.get_json()['LABEL'])
        # 先保存到raw里，后续随机抽取出 test , train
        path = r"./DataSet1/raw/" + label
        if not os.path.exists(path): os.makedirs(path)

        return CV.process_save(img, path, label)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2426)
