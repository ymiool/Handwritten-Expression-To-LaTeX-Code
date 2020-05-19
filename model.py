import tensorflow as tf
from tensorflow.keras import layers, optimizers, datasets, Sequential
import cv2
import numpy as np
import os
import util


class Model:
    """ Model 模型类，   封装模型相关的参数，便于训练使用时调整修改。
    Attributes:
        img_size : int, 输入图像（正方形）的边长（分辨率）
        channel : int, 输入图像的通道数
        epochs_num : int, 训练的 epoch 数
        batch_size : int, 采用MiniBatch方法，每个 batch 所含样本的大小
        classes : int, 分类类别数，对应神经网络输出层个数等
        label_text : string list, 图片的标签（类别名）
        name: string, 模型名称，对应模型训练好后 保存的子文件夹名称
        data_set: string, 数据集名称，对应存放数据集的子文件夹名称
    """
    # 图片格式相关
    img_size = 128
    channel = 1

    # 分类信息相关
    label_text = None

    def __init__(self, name, data_set, epochs_num, batch_size):
        self.name = name
        self.data_set = data_set
        self.dirlist = os.listdir(r'./' + self.data_set + '/train')
        if '.DS_Store' in self.dirlist:
            self.dirlist.remove('.DS_Store')
        self.dirlist.sort()
        self.classes = len(self.dirlist)
        self.epochs_num = epochs_num
        self.batch_size = batch_size
        self.label_text = []


model1 = Model('model1', 'DataSet1', 45, 40)

use_model = model1

def load_data():
    """ 从本地指定文件夹载入数据集，包含 训练集、验证集
    Args: None
    Returns: (x_train, y_train), (x_test, y_test)
              x_train: numpy, (nums of pics, 128, 128, 3) 训练集图片数据
              y_train: numpy, (nums of pics, 1) 训练集图片标签
              x_test: numpy, (nums of pics, 128, 128, 3) 测试集图片数据
              y_test: numpy, (nums of pics, 1) 测试集图片标签
    """
    # 训练集
    trains = []
    y_train = []
    i = 0
    for dir in use_model.dirlist:  # dir 名， 就是 符号名(char)
        #use_model.label_text.append(str(dir))  # 往标签中添加,只添加一次

        train_datas = os.listdir(r'./' + use_model.data_set + '/train/' + dir)
        if '.DS_Store' in train_datas:
            train_datas.remove('.DS_Store')

        for train_data in train_datas:  # dir 文件夹中的每张图
            trains.append(cv2.imread(r'./' + use_model.data_set + '/train/' + dir + '/' + train_data, cv2.IMREAD_GRAYSCALE))
            y_train.append(int(i))  # y 标签

        i = i + 1

    x_train = np.concatenate([train[np.newaxis] for train in trains])
    y_train = np.array(y_train)

    #print(x_train.shape, y_train.shape)


    # 测试集
    tests = []
    y_test = []

    i = 0
    for dir in use_model.dirlist:
        test_datas = os.listdir(r'./' + use_model.data_set + '/test/' + dir)
        if '.DS_Store' in test_datas:
            test_datas.remove('.DS_Store')
        for test_data in test_datas:
            tests.append(cv2.imread(r'./' + use_model.data_set + '/test/' + dir + '/' + test_data, cv2.IMREAD_GRAYSCALE))
            y_test.append(int(i))
        i = i + 1

    x_test = np.concatenate([test[np.newaxis] for test in tests])
    y_test = np.array(y_test)
    # print(y_test)
    # print(type(y_test[2]))
    return (x_train, y_train), (x_test, y_test)


def preprocess(x, y):
    """ 数据集预处理
    Args: x: 某一图片数组
          y: shape(1) 某一图片标签
    Returns: x: 处理后的图片数组（归一化）
             y: shape(classes) 处理后的图片标签（向量化）
    """
    x = tf.cast(x, dtype=tf.float32) / 255  # / 255 就是归一化. 0~255 / 255 : 0 ~ 1.  .cast是类型转换.原来可能是整型。
    x = tf.reshape(x, [use_model.img_size, use_model.img_size, use_model.channel])
    y = tf.cast(y, dtype=tf.int32)
    y = tf.one_hot(y, depth=use_model.classes)
    return x, y


def train():
    # 载入数据集、预处理
    (x_train, y_train), (x_test, y_test) = load_data()
    print('datasets:', x_train.shape, y_train.shape, x_train.min(), x_train.max())

    db = tf.data.Dataset.from_tensor_slices((x_train, y_train))
    db = db.map(preprocess).shuffle(x_train.shape[0]).batch(use_model.batch_size)

    ds_val = tf.data.Dataset.from_tensor_slices((x_test, y_test))
    ds_val = ds_val.map(preprocess).batch(use_model.batch_size)


    # CNN 构建
    conv_layers = [
        # unit 1
                    # filter 个数， size
        layers.Conv2D(16, kernel_size=[2, 2], padding="same", activation=tf.nn.relu),
        layers.MaxPool2D(pool_size=[2, 2], strides=2, padding='same'),
                    # 在 maxpool 里面设置 stride
        # unit 2
        layers.Conv2D(32, kernel_size=[2,2], padding="same", activation=tf.nn.relu),
        layers.MaxPool2D(pool_size=[2, 2], strides=2, padding='same'),

        # unit 3
        layers.Conv2D(64, kernel_size=[2,2], padding="same", activation=tf.nn.relu),
        layers.MaxPool2D(pool_size=[2, 2], strides=2, padding='same'),


        # 展开为向量
        layers.Flatten(),

        # 加几层全连接的神经网络， n是该层输出的神经元数
        layers.Dense(600, activation='relu'),


        # 输出层。 此层分几类，就设几个输出神经元数. 输出层用 softmax 激活函数
        layers.Dense(use_model.classes, activation='softmax'),
    ]

    net = Sequential(conv_layers)  #批量 add.

    net.build(input_shape=(None, use_model.img_size, use_model.img_size, use_model.channel))
    net.summary()

    # evaluate net 的好坏 设置（准确率？）
    net.compile(optimizer=optimizers.Adam(lr=0.001), # lr : 梯度下降时 learning rate
                loss=tf.losses.CategoricalCrossentropy(from_logits=True),
                metrics=['accuracy'])
    # 训练 （feed 数据）
    net.fit(db, epochs=use_model.epochs_num, validation_data=ds_val, validation_freq=2)
    # 评测
    net.evaluate(ds_val)
    # 保存模型
    if not os.path.exists("./" + use_model.name) : os.makedirs("./" + use_model.name)
    net.save(r'./' + use_model.name + '/model.h5')
    # 保存参数
    net.save_weights(r'./' + use_model.name + '/weights.ckpt')

    # 准确率评估


if __name__ == '__main__':
    train()
    util.test_acc()
    print(use_model.classes)
    print(use_model.dirlist)


