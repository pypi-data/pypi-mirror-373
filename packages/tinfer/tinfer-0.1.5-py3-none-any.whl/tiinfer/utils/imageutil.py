import cv2
import numpy

cv2.setNumThreads(5)
import math
from enum import Enum
from typing import Optional, Tuple


# 水平填充方向
class Horizontal(Enum):
    # 左边填充
    LEFT = 1
    # 左边填充
    RIGHT = 2


# 垂直填充方向
class Vertical(Enum):
    # 上边填充
    UPPER = 1
    # 下边填充
    LOWER = 2


# 图片等比扩缩
def scale_image(
    image: numpy.ndarray, min_size: int, max_size: int
) -> Tuple[numpy.ndarray, float]:
    """图片等比扩缩
    保持原图的长宽比例，调整到指定大小范围。整个调整过程分为2步：
    第一次缩放：短边固定为指定大小的较小值，长边等比例缩放。
    第二次缩放：第一次缩放后的图片，如果长边大于指定大小中的较大值，
              则固定长边为指定大小中的较大值，短边等比例缩放。

    :param image: 图片
    :type image: numpy.ndarray
    :param min_size: 图片扩缩小边最小范围值
    :type min_size: int
    :param max_size: 图片扩缩大边最大范围值
    :type max_size: int
    Returns:
    Tuple[numpy.ndarray, float]: 调整后的图片以及缩放比例。缩放比例可以用于推理后box在原图上的位置。
    """
    if not isinstance(image, numpy.ndarray):
        raise TypeError(f"image should be numpy.ndarray. Got {type(image)}")
    if min_size > max_size:
        raise ValueError("min_size should not be larger than max_size")
    h, w = image.shape[:2]
    scale = round(min_size * 1.0 / min(h, w), 3)
    if h < w:
        newh, neww = min_size, scale * w
    else:
        newh, neww = scale * h, min_size
    if max(newh, neww) > max_size:
        scale = round(max_size * 1.0 / max(h, w), 3)
        newh = h * scale
        neww = w * scale
    newh = math.ceil(newh)
    neww = math.ceil(neww)
    new_image = cv2.resize(image, (neww, newh))
    return new_image, scale


# 图片填充
def fill_image(
    image: numpy.ndarray,
    padding_limit: int,
    horizontal: Optional[Horizontal] = None,
    vertical: Optional[Vertical] = None,
    fill_color: Optional[float] = None,
) -> numpy.ndarray:
    """图片填充
    图片填充逻辑，整个调整过程分为3步：
    1：参数检查，最小边如果大于填充上限，直接返回，不需填充。
    2：如果图片的高小于填充下限，垂直方向做填充，填充到padding_limit尺寸。
    3：如果图片的长小于填充下限，水平方向做填充，填充到padding_limit尺寸。

    :param image: 图片
    :type image: numpy.ndarray
    :param padding_limit: 填充时的上限值,小于该值的边需要填充
    :type padding_limit: int
    :param horizontal: 图片水平填充位置
    :type horizontal: Enum LEFT：左边填充；RIGHT：右边填充。默认值：RIGHT
    :param vertical: 图片垂直填充位置
    :type vertical: Enum UPPER：上边填充；LOWER：下边填充。默认值：LOWER
    :param fill_color: 填充颜色
    :type fill_color: Optional[float] ：填充的像素值，为0到255内的数值。默认为0（黑色）
    Returns:
    numpy.ndarray: 填充后的图片。
    """
    if not isinstance(image, numpy.ndarray):
        raise TypeError(f"image should be numpy.ndarray. Got {type(image)}")
    if fill_color is None:
        fill_color = 1  # 默认1表示黑色
    if horizontal is None:
        horizontal = Horizontal.RIGHT  # 水平方向默认右边填充
    if vertical is None:
        vertical = Vertical.LOWER  # 垂直方向默认下边填充

    h, w = image.shape[:2]
    if min(h, w) > padding_limit:
        return image
    if w < padding_limit:
        blank_img = numpy.full([h, padding_limit - w, fill_color, 3], dtype=numpy.uint8)
        if horizontal == Horizontal.RIGHT:
            new_image = numpy.hstack([image, blank_img])
        else:
            new_image = numpy.hstack([blank_img, image])
        h, w = new_image.shape[:2]
    if h < padding_limit:
        blank_img = numpy.full([padding_limit - h, w, 3], fill_color, dtype=numpy.uint8)
        if vertical == Vertical.LOWER:
            new_image = numpy.vstack([image, blank_img])
        else:
            new_image = numpy.vstack([blank_img, image])

    return new_image


# 图片等比扩缩与填充
def scale_fill_image(
    image: numpy.ndarray,
    min_size: int,
    max_size: int,
    padding_limit: int,
    horizontal: Optional[Horizontal] = None,
    vertical: Optional[Vertical] = None,
    fill_color: Optional[float] = None,
) -> Tuple[numpy.ndarray, float]:
    """图片等比扩缩与填充

    :param image: 图片
    :type image: numpy.ndarray
    :param min_size: 图片扩缩小边最小范围值
    :type min_size: int
    :param max_size: 图片扩缩大边最大范围值
    :type max_size: int
    :param padding_limit: 填充时的短边上限。若该参数为空，则默认使用min_size; 若该参数非空，两条边小于padding_limit则填充到padding_limit，该值需小于max_size。
    :type padding_limit: int
    :param horizontal: 图片水平填充位置
    :type horizontal: Enum LEFT：左边填充；RIGHT：右边填充。默认值：RIGHT
    :param vertical: 图片垂直填充位置
    :type vertical: Enum UPPER：上边填充；LOWER：下边填充。默认值：LOWER
    :param fill_color: 填充颜色
    :type fill_color: Optional[float] ：填充的像素值，为0到255内的数值。默认为0（黑色）
    Returns:
    Tuple[numpy.ndarray, float]: 调整后的图片以及缩放比例。缩放比例可以用于推理后box在原图上的位置。
    """
    if not isinstance(image, numpy.ndarray):
        raise TypeError(f"image should be numpy.ndarray. Got {type(image)}")
    if min_size > max_size:
        raise ValueError("min_size should not be larger than max_size")
    if padding_limit > max_size:
        raise ValueError("padding_limit should not be larger than max_size")
    # 做等比扩缩
    sacled_image, scale = scale_image(image, min_size, max_size)

    # 做填充
    filled_image = fill_image(
        sacled_image, padding_limit, horizontal, vertical, fill_color
    )

    return filled_image, scale
