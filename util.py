# 测试功能、工具函数（数据集处理等）
import random
import os
from shutil import move
import predict
import CV

def get_dirlist(path) :
    dirlist = os.listdir(path)
    if '.DS_Store' in dirlist:
        dirlist.remove('.DS_Store')
    return dirlist


def rename(dir_name, s):
    root = r"./DataSet1/"
    for char in get_dirlist(root + dir_name + '/'):
        i = 1
        dir_list = get_dirlist(root + dir_name + '/' + char + '/')
        dir_list.sort()
        for img in dir_list:
            os.rename(root + dir_name + '/' + char + '/' + img, root + dir_name + '/' + char + '/' + char + s + str(i) + '.png')
            i = i + 1





def ramdom_images(type, len_image):
    root = r"./DataSet1/"
    for char in get_dirlist(root + "raw/"):
        if not os.path.exists(root + type + '/' + char): os.makedirs(root + type + '/' + char)
        random_img_list = random.sample(get_dirlist(root + "raw/" + char), len_image - len(get_dirlist(root + type + '/' + char)))
        i = 1
        for img in random_img_list:
            move(root + "raw/" + char + "/" + img, root + type + '/'  + char + "/" + char + '_' + str(i) + '.png')
            i = i + 1


def test_acc():
    root = r"./DataSet1/"
    name = 'test'
    dir_list = get_dirlist(root + name + '/')
    dir_list.sort()
    for char in dir_list:
        i = 0
        img_list = get_dirlist(root + name + '/' + char + '/')
        for img in img_list:
            img_path = root + name + '/' + char + '/' + img
            r = predict.predict_label(CV.read_by_type(img_path, 'path'))
            if r == char: i += 1
        acc = i / float(len(img_list))
        print(char + ': ' + str(i))




if __name__ == "__main__" :

    rename('raw', '__')
    rename('raw', '_')
    #rename('train', '___')
    #rename('train', '_')
    #rename('test', '__')
    #rename('test', '_')
    #ramdom_images('test', 10)
    #rename('test', '_')
    # ramdom_images('test', 10)

    test_acc()
    #print(predict.the_model.dirlist)


    '''
    cv2.imshow("1", img)  # 显示图片
    cv2.waitKey(0)  # 不 wait 窗口打开即关闭，看不到
    cv2.destroyAllWindows()
    '''


