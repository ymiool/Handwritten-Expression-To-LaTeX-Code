import tensorflow as tf
from numpy import reshape

import model
import CV


the_model = model.use_model

# 加载模型
model = tf.keras.models.load_model(the_model.name + '/model.h5')
# 加载参数
model.load_weights(the_model.name + '/weights.ckpt')


slash = ['pi', 'times']



class Symbol:

    def __init__(self, label, x, y, xw, yh):
        self.label = label
        self.x = x
        self.y = y
        self.xw = xw
        self.yh = yh
        self.centroid = ( (self.xw + self.x)/2 , (self.y + self.yh) / 2 )

    def width(self):
        return self.xw - self.x

    def height(self):
        return  self.yh - self.y

    def __str__(self):
        return str(self.label)

# 各个遍历 get 函数， 符合条件后也是要记得在原 list 中 pop 出去。
# get 其实就是 抽取（划分子集）。在原 symbol_list 中抽取出符合条件的。所以得pop. 否则就重复了。

def print_symbols(symbol_lists):
    for symbol in symbol_lists:
        print(symbol)


def get_inner_symbols(out, symbol_list):
    inner_list = []
    i = 0
    while i < len(symbol_list):
        symbol = symbol_list[i]
        if out.x < symbol.x and out.xw > symbol.xw and out.y < symbol.y and out.yh > symbol.yh:
            inner_list.append(symbol)
            symbol_list.pop(i)
        else: i += 1
    return inner_list


def get_upper_symbols(center, symbol_list):
    upper_symbols = []
    i = 0
    while i < len(symbol_list):
        symbol = symbol_list[i]
        if center.x < symbol.x and center.xw > symbol.xw and center.y >= (symbol.yh - 10):
            upper_symbols.append(symbol)
            symbol_list.pop(i)
        else: i += 1
    return upper_symbols


def get_under_symbols(center, symbol_list):
    under_symbols = []
    i = 0
    while i < len(symbol_list):
        symbol = symbol_list[i]
        if center.x < symbol.x and center.xw > symbol.xw and center.yh <= (symbol.y + 10):
            under_symbols.append(symbol)
            symbol_list.pop(i)
        else: i += 1
    return under_symbols


def is_sup(this, next):
    print(this.centroid[1] - next.centroid[1])
    return this.centroid[1] - next.centroid[1] >= this.height() * 0.25 and (next.x + 30 - this.xw) >= 0 and next.y <= this.y and this.yh - next.yh > this.height() * 0.25


def get_sup_symbol(pre, this, symbol_list):
    sup = []
    sup.append(this)
    while len(symbol_list) > 0:
        symbol = symbol_list[0]
        if is_sup(pre, symbol):
            sup.append(symbol)
            symbol_list.pop(0)
        else: break
    return sup


def toLatex(symbol_list):
    latex = []
    i = 0
    symbol = None
    while len(symbol_list) > 0:
        pre = symbol
        symbol = symbol_list.pop(i)  #   记得 pop， 以免重复访问

        # 上标
        if (pre is not None) and (pre.label not in ['-', '+', 'times']) and is_sup(pre, symbol):
            print(pre not in ['-'])
            print('有上标 ')
            print(pre.label)
            latex.append('^' + '{' + toLatex(get_sup_symbol(pre, symbol, symbol_list)) + '}')


        # 区分几种 '-' 的情况，仅当后面还有字符时(没有就直接到最后面的常规输出)
        elif symbol.label == '-' and len(symbol_list) > 0:  #
            # 等号
            if symbol_list[i].label == '-' and abs(symbol_list[i].width() - symbol.width()) < symbol.width() * 0.3 and abs(symbol_list[i].x - symbol.x) < symbol.width() * 0.3:
                symbol_list.pop(i)
                latex.append(' = ')

            # 除号
            elif len(symbol_list) > 1 and symbol_list[i].label == 'dot' and symbol_list[i+1].label == 'dot':
                symbol_list.pop(i)
                symbol_list.pop(i) # 注意，pop之后就少了一个了，不需要i+1
                latex.append(' \div ')

            # 分号
            elif len(symbol_list) > 1:
                upper = get_upper_symbols(symbol, symbol_list)
                under = get_under_symbols(symbol, symbol_list)

                print('upper: ')
                print_symbols(upper)
                print('under: ')
                print_symbols(under)

                if len(upper) > 0 or len(under) > 0: # 要求是合法的表达式
                    latex.append(r'\frac' + '{' + toLatex(upper)+ '}' + '{' + toLatex(under) + '}')
                # 漏掉的等号
                elif (len(upper) == 1 or len(under) == 1)  and (upper[0].label == '-' or under[0].label == '-'):
                    latex.append(' = ')
                else:
                    latex.append('-')
            # 不要忘了一般情况
            else:
                latex.append('-')

        # 根号
        elif symbol.label == 'sqrt':
            latex.append(r'\sqrt' + '{' + toLatex(get_inner_symbols(symbol, symbol_list)) + '}')


        # 小数点修改
        elif symbol.label == 'dot':
            latex.append('.')



        # 加斜杠，记住还要再加空格
        elif symbol.label in slash:
            latex.append('\\' + symbol.label + " ")

        # 普通变量字符
        else :
            latex.append(symbol.label)

    return "".join(latex)



def predict(images):
    """
    使用训练好的模型，预测图片所属的类别
    Args: images: 需预测的图片数组(numpy) len * 128 * 128 * 3
    Returns: argmax: 输入的各图片预测得到的对应类别号 数组
    """

    predict = model.predict(images)
    # 找到概率最大的位置
    argmax = tf.argmax(predict, axis=1)
    return argmax.numpy()


def predict_label(img):
    img = reshape(img/255, (1, 128, 128, 1)) #predict可用的小图、格式处理、归一化
    return the_model.dirlist[predict(img)[0]]


def predict_all(img, type):
    """
    预测图片中框出的所有字符(还不是公式)
    img : img 的 path
    type : 指定读取的图片形式是图片文件还是base64编码
    :return: 单字符数组
    """

    img = CV.read_by_type(img, type)  # 分类型读取图片
    img = CV.pre_p(img)  # 预处理
    res = CV.rawBox(img)  # 分割

    result_str = []
    symbol_list = []

    for rec in res:  # 对每一个识别出的矩形框
        # 截取、预处理
        cut = CV.get_resized_cut(img, rec, the_model.img_size)


        # 直接一个个 cut 预测、框出、标记
        r = predict_label(cut)

        result_str.append(r)
        symbol_list.append(Symbol(r, rec[0][0], rec[0][1], rec[1][0], rec[1][1]))


        # 测试用
        CV.draw_box_and_text(img, rec, r)

    CV.write_img("./tmp/test.png", img)


    result_latex = toLatex(symbol_list)  # 翻译 连接更新后的 字符列表 至 latex
    print(result_str)

    return result_latex








