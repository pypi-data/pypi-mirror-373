import cv2
import numpy as np
from PIL import Image, ImageDraw


def draw_square(image_np, x, y, color):
    """在指定位置(x, y)绘制3x3大小的正方形"""
    # 确保坐标在图像范围内
    height, width, _ = image_np.shape

    for i in range(3):
        for j in range(3):
            image_np[y + i, x + j] = color


def put_image_number(number, image_np, digits=10, start_pos=None):
    """
    在给定的numpy数组表示的图像上，基于提供的数字绘制二进制表示。
    :param number: 要转换成二进制并显示在图像上的整数。
    :param image_np: numpy数组，原始图像。
    :param x_start: 二进制图案起始的 x 坐标。
    :param y_start: 二进制图案起始的 y 坐标。
    :return: 绘制后的图像，以numpy数组形式返回。
    """
    # 确保 number 在 0~1023 范围内
    h, w, c = image_np.shape
    if start_pos is None:
        x_start = w - digits * 3
        y_start = h - 3
    else:
        x_start, y_start = start_pos

    # 转换为 10 位二进制字符串，高位在左
    binary_str = format(number, '010b')  # 得到形如 '0101010101' 的字符串

    # 遍历 10 个 3x3 的格子
    start_positions = [(x_start + j * 3, y_start) for j in range(digits)]
    for pos, bit in zip(start_positions, binary_str):
        color = (255, 255, 255) if bit == '1' else (0, 0, 0)  # 白色或黑色
        draw_square(image_np, pos[0], pos[1], color)

    return image_np

def read_image_number(image_np, digits=10, start_pos=None, threshold=128):
    """
    从给定的numpy数组表示的图像中读取嵌入的二进制图案，并将其转换回原始整数。
    使用中心像素的亮度值和设定的阈值来进行二值化处理。
    :param image_np: numpy数组，包含绘制的二进制图案的图像。
    :param x_start: 二进制图案起始的 x 坐标。
    :param y_start: 二进制图案起始的 y 坐标。
    :param threshold: 阈值，用于确定哪个亮度值被视为'1'或'0'。
    :return: 转换后的整数。
    """
    h, w, c = image_np.shape
    if start_pos is None:
        x_start = w - digits * 3
        y_start = h - 3
    else:
        x_start, y_start = start_pos
    binary_str = ''
    for j in range(10):
        # 获取每个3x3正方形的中心像素的颜色
        color = image_np[y_start + 1, x_start + j * 3 + 1]
        # 计算亮度值（对于RGB图像，使用平均值）
        brightness = sum(color) // 3
        # 根据亮度值与阈值比较来决定是'1'还是'0'
        bit = '1' if brightness >= threshold else '0'
        binary_str += bit

    return int(binary_str, 2)

# 示例使用
if __name__ == "__main__":
    # 创建一个空白的RGB图像(numpy数组)，例如：高度50，宽度400，颜色通道3（RGB）
    img_np = cv2.imread(r"D:\Code\aigc-event-highlights\live-stream-ai-task-workline\test\football_demo\images\1755589846902.png")

    num = 55  # 例如：42 在 0~1023 之间
    modified_img_np = put_image_number(num, img_np)

    aa = read_image_number(modified_img_np)
    print(aa)

    # 如果想用PIL查看结果，可以将numpy数组转回image对象
    img_result = Image.fromarray(cv2.cvtColor(modified_img_np, cv2.COLOR_BGR2RGB))
    img_result.show()  # 显示修改后的图像