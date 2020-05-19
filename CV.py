import cv2
import numpy as np
import base64
import os


def read_by_type(img, type):
    """
    按不同类型读取cv图片
    :param img:
    :param type:
    :return:
    """
    if type == 'path':
        img = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    if type == 'b64':
        img = cv2.imdecode(np.frombuffer(base64.b64decode(img), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    return img


def pre_p(img):
    """
    图片预处理，二值，反转
    :param img:
    :return:
    """
    ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    return img


def rawBox(img):
    """
    框出图片中的字符
    :param img: 需要识别的图片
    :return: 框出的矩形坐标信息数组
    """
    # cv2 找轮廓
    # ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)  # 二值化, 黑白翻转， thresh 为处理后
    im2, contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, 2)  # 只选择外轮廓

    # img2 = thresh  # 指定最后绘制框、窗口显示的图片
    res = []  # 框出的矩形坐标数据

    # 依次框出
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)  # 轮廓矩形的左上角坐标、宽、高
        if x is 0: continue  # 除掉整个图片最外框
        if w*h < 15: continue  # 除噪点（按面积）
        # cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 255), 1)  # 画矩形
        res.append([(x, y), (x+w, y+h)])  # 以矩形的两个端点为组保存
    # 显示
    '''
    print(len(res))
    cv2.imshow("1", img2)  # 显示图片
    cv2.waitKey(0)  # 不 wait 窗口打开即关闭，看不到
    cv2.destroyAllWindows()
    '''
    res.sort()  # sort之后就保证是从左到右的顺序了
    return res


def padding_resize(img, re_size):
    """
    缩放、填充至对应的图片分辨率
    :param img:
    :param re_size: 正方形的边长
    :return: 处理后的图片
    """

    # 填充、resize
    size = img.shape
    h, w = size[0], size[1]
    #长边缩放为re_size
    scale = max(w, h) / float(re_size)
    new_w, new_h = int(w/scale), int(h/scale)
    resize_img = cv2.resize(img, (new_w, new_h))
    # 填充至re_size * re_size
    if new_w % 2 != 0 and new_h % 2 == 0:
        top, bottom, left, right = (re_size-new_h)/2, (re_size-new_h)/2, (re_size-new_w)/2 + 1, (re_size-new_w)/2
    elif new_h % 2 != 0 and new_w % 2 == 0:
        top, bottom, left, right = (re_size-new_h)/2 + 1, (re_size-new_h)/2, (re_size-new_w)/2, (re_size-new_w)/2
    elif new_h % 2 == 0 and new_w % 2 == 0:
        top, bottom, left, right = (re_size-new_h)/2, (re_size-new_h)/2, (re_size-new_w)/2, (re_size-new_w)/2
    else:
        top, bottom, left, right = (re_size-new_h)/2 + 1, (re_size-new_h)/2, (re_size-new_w)/2 + 1, (re_size-new_w)/2
    pad_img = cv2.copyMakeBorder(resize_img, int(top), int(bottom), int(left), int(right), cv2.BORDER_CONSTANT, value=[0,0,0]) #从图像边界向上,下,左,右扩的像素数目
    #print pad_img.shape
    return pad_img


def get_resized_cut(img, rec, re_size):
    """
    符合数据集规范的cut图
    :param img:
    :param rec:
    :param re_size:
    :return:
    """
    return padding_resize(img[rec[0][1]:rec[1][1], rec[0][0]:rec[1][0]], re_size)


def draw_box_and_text(img, rec, label):
    """
    在预处理的图片上框出字符、标注预测值
    :param img:
    :param rec:
    :param label:
    :return:
    """
    cv2.rectangle(img, rec[0], rec[1], (255, 255, 255), 1)  # 顺便画出框
    cv2.putText(img, label, rec[0], cv2.FONT_HERSHEY_PLAIN, 3, (100, 200, 200), 2)


def write_img(path, img):
    cv2.imwrite(path, img)


def process_save(img, path, label):
    """
    处理数据集图片，处理至黑底白字，相应分辨率，一张图中可以有多个手写数据，并重命名保存至相应路径
    :param img:
    :param name:
    :return:
    """

    # 预处理
    img = pre_p(img)  # 二值化, 黑白翻转， thresh 为处理后

    # 分割
    res = rawBox(img)

    # 统计目前已有文件数
    dirlist = os.listdir(path)
    i = len(dirlist)
    if '.DS_Store' in dirlist: i = i - 1
    I = i

    for rec in res:
        i = i + 1
        # 截取图片
        cut = get_resized_cut(img, rec, 128)
        cv2.imwrite(path + "/" + label + "_" + str(i) + ".png", cut)  # 保存至本地

    return str(i - I) # 返回保存的图片数


if __name__ == "__main__":
    re_size = 128

    data_set = "DataSet1"

    # 训练集处理
    dirlist = os.listdir(r'./' + data_set + '/train')
    if '.DS_Store' in dirlist:
        dirlist.remove('.DS_Store')
    for dir in dirlist:
        train_datas = os.listdir(r'./' + data_set + '/train/' + dir)
        if '.DS_Store' in train_datas:
            train_datas.remove('.DS_Store')
        i = 1
        for train_data in train_datas:
            img = cv2.imread(r'./' + data_set + '/train/' + dir + '/' + train_data)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            process_save(img, r'./' + data_set + '/train/', dir.split('_', 1)[0])
            i = i + 1

    # 测试集处理
    dirlist = os.listdir(r'./' + data_set + '/test')
    if '.DS_Store' in dirlist:
        dirlist.remove('.DS_Store')
    for dir in dirlist:
        test_datas = os.listdir(r'./' + data_set + '/test/' + dir)
        if '.DS_Store' in test_datas:
            test_datas.remove('.DS_Store')
        i = 1
        for test_data in test_datas:
            img = cv2.imread(r'./' + data_set + '/test/' + dir + '/' + test_data)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            process_save(img, r'./' + data_set + '/test/', dir.split('_', 1)[0])
            i = i + 1



