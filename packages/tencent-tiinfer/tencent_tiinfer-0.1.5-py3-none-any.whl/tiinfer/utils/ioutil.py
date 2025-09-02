import base64
import os
import urllib.request
from io import BytesIO

import cv2
import numpy as np
from PIL import Image


def base64bytes_to_nparray(s: str, dtype=np.uint8) -> np.ndarray:
    return np.array(Image.open(BytesIO(base64.b64decode(s))))


def base64bytes_to_pil_image(s: str) -> Image.Image:
    return Image.open(BytesIO(base64.b64decode(s)))


# image_to_cv2_mat能够正确处理本地图片、图片url及base64编码的图片内容，将之转换为opencv2中的矩阵
def image_to_cv2_mat(img_data: str) -> cv2.Mat:
    if os.path.isfile(img_data):
        # 输入为本地图片，则直接读取
        img_mat = cv2.imread(img_data)
    elif img_data.startswith("http"):
        # 输入为图片url
        url_response = urllib.request.urlopen(img_data)
        image_data = url_response.read()
        image_nparr = np.array(bytearray(image_data), dtype=np.uint8)
        img_mat = cv2.imdecode(image_nparr, cv2.IMREAD_COLOR)
    else:
        # 图片base64解码
        image_data = base64.b64decode(img_data)
        image_nparr = np.frombuffer(image_data, np.uint8)
        img_mat = cv2.imdecode(image_nparr, cv2.IMREAD_COLOR)
    return img_mat


# image_to_pil_image能够正确处理本地图片、图片url及base64编码的图片内容，将之转换为PIL中的image
def image_to_pil_image(img_data: str) -> Image.Image:
    if os.path.isfile(img_data):
        # 输入为本地图片，则直接读取
        img_data = Image.open(img_data)
    elif img_data.startswith("http"):
        # 输入为图片url
        url_response = urllib.request.urlopen(img_data)
        image_data = url_response.read()
        img_data = Image.open(BytesIO(image_data))
    else:
        # 图片base64解码
        image_data = base64.b64decode(img_data)
        img_data = Image.open(BytesIO(image_data))
    return img_data
