#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/7/11 10:20
@Author  : dmj-11740
@File    : tess.py
@Software: PyCharm
@desc    : 
"""
import base64
import os
import random
import time
from copy import deepcopy
from io import BytesIO

import ddddocr
import cv2
from PIL import Image
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from numpy.linalg import norm
from scipy.optimize import linear_sum_assignment


class SliderCS:

    def __init__(self, hint_tailor_x=0, bg_to_size=None):
        self.hint_tailor_x = hint_tailor_x
        self.bg_to_size = bg_to_size
        self.det = ddddocr.DdddOcr(det=True)
        self.ocr = ddddocr.DdddOcr()

    def expand_rect(self, rect, expand_pixel=10):
        """
        扩大矩形坐标框

        参数:
        rect (list): 原始矩形坐标 [x1, y1, x2, y2]
        expand_pixel (int): 向四周扩大的像素值（默认10像素）

        返回:
        list: 扩大后的矩形坐标 [new_x1, new_y1, new_x2, new_y2]
        """
        x1, y1, x2, y2 = rect
        # 计算扩大后的坐标
        new_x1 = x1 - expand_pixel
        new_y1 = y1 - expand_pixel
        new_x2 = x2 + expand_pixel
        new_y2 = y2 + expand_pixel
        # 确保坐标不为负数（可选，根据实际场景）
        new_x1 = max(0, new_x1)
        new_y1 = max(0, new_y1)
        return [new_x1, new_y1, new_x2, new_y2]

    def crop_image_by_coordinates(self, image, coords):
        """
        根据坐标列表切割图片
        coords (list): 坐标列表，格式为[x1, y1, x2, y2]
        """
        try:
            coords = self.expand_rect(coords, 3)
            x1, y1, x2, y2 = coords
            if image is None:
                print(f"错误：无法读取图片 {image}")
                return False
            height, width = image.shape[:2]
            x2 = min(width, x2)
            y2 = min(height, y2)
            x1 = max(0, x1)
            y1 = max(0, y1)
            if x1 >= x2 or y1 >= y2:
                print(
                    f"错误：无效的坐标范围。图片尺寸: {width}x{height}，给定坐标: ({x1},{y1}) 到 ({x2},{y2})"
                )
                return False
            cropped_image = image[y1:y2, x1:x2]

            # print(f"成功切割图片并保存到 {output_path}")
            retval, buffer = cv2.imencode(".png", cropped_image)
            # 将缓冲区转换为二进制数据
            binary_data = buffer.tobytes()

            return binary_data

        except Exception as e:
            print(f"切割图片时发生错误: {str(e)}")
            return False

    def convert_background(self, image_data, ts=False):
        if isinstance(image_data, bytes):
            image = Image.open(BytesIO(image_data))
        else:
            if image_data.startswith("data:image/"):
                image_data = image_data.split(",")[1]
            image_data = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_data))
        with open(f"tt-{'hint' if ts else 'bg'}.png", "wb") as f:
            f.write(image_data)
        cv_rgb_image = np.array(image)
        image = cv2.cvtColor(cv_rgb_image, cv2.COLOR_RGB2BGR)
        height, width = image.shape[:2]
        if ts:
            image = image[0:height, self.hint_tailor_x:width]
        else:
            resize_data = self.bg_to_size or [width, height]
            image = cv2.resize(image, resize_data, interpolation=cv2.INTER_AREA)

        retval, buffer = cv2.imencode(".jpg", image)

        # 将缓冲区转换为二进制数据
        binary_data = buffer.tobytes()

        bboxes = self.det.detection(binary_data)
        bboxes = sorted(bboxes, key=lambda x: x[0])

        print(bboxes)
        A = []
        img = Image.open(BytesIO(binary_data))
        for idx, bbox in enumerate(bboxes):
            result = self.crop_image_by_coordinates(image, bbox)
            result = self.ocr.classification(result)
            if not result:
                for angle in range(-20, 20, 5):
                    result = self.img_rotate_discern(img, angle)
                    if result:
                        break
            if not result:
                result = "人"
            A.append(result[0])
        return bboxes, A

    def char_to_vector(self, ch, size=32, font_path="C:/Windows/Fonts/simhei.ttf"):
        img = Image.new("L", (size, size), color=255)  # 白底
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font_path, size=size - 4)

        bbox = draw.textbbox((0, 0), ch, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size - w) / 2, (size - h) / 2), ch, fill=0, font=font)

        vec = np.array(img).astype(float).flatten()
        vec = (vec - vec.mean()) / (vec.std() + 1e-5)
        return vec

    def cosine_similarity(self, vec1, vec2):
        return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))

    def match_indices_unique(
            self, list1, list2, font_path="C:/Windows/Fonts/simhei.ttf"
    ):
        # 向量化
        vec1s = [self.char_to_vector(ch, font_path=font_path) for ch in list1]
        vec2s = [self.char_to_vector(ch, font_path=font_path) for ch in list2]

        # 相似度矩阵 (list1 行, list2 列)
        sim_matrix = np.zeros((len(list1), len(list2)))
        for i, v1 in enumerate(vec1s):
            for j, v2 in enumerate(vec2s):
                sim_matrix[i, j] = self.cosine_similarity(v1, v2)

        # 匈牙利算法：因为 linear_sum_assignment 是最小化代价，所以取 -sim
        row_ind, col_ind = linear_sum_assignment(-sim_matrix)

        # 输出结果
        result = {}
        for i, j in zip(row_ind, col_ind):
            # result[list1[i]] = (j, sim_matrix[i, j])  # (索引, 相似度)
            result[list1[i]] = j  # 索引
        return result

    def img_rotate_discern(self, image, angle):
        rotated_img = image.rotate(
            angle, expand=True, resample=Image.Resampling.BICUBIC
        )
        result = self.ocr.classification(rotated_img)
        # rotated_img.show()
        return result

    def get_center_coordinate(self, rect):
        """
        计算矩形区域的中间坐标（中心点）

        参数:
        rect (list): 矩形坐标，格式为 [x1, y1, x2, y2]

        返回:
        tuple: 中心点坐标 (center_x, center_y)
        """
        x1, y1, x2, y2 = rect
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return (center_x, center_y)


def get_select_coord(hint, background, hint_tailor_x: int = 0, bg_to_size: tuple[int, int] = None):
    """
        点选验证坐标识别
    :param hint:
    :param background:
    :param hint_tailor_x: 提示词 裁剪X
    :param bg_to_size: 背景图尺寸裁剪
    :return:
    """
    scs = SliderCS(hint_tailor_x, bg_to_size)
    if os.path.exists(hint):
        with open(hint, "rb") as f:
            hint = f.read()
    if os.path.exists(background):
        with open(background, "rb") as f:
            background = f.read()
        background_ = Image.open(BytesIO(background))
    else:
        if background.startswith("data:image/"):
            background = background.split(",")[1]
        image_data = base64.b64decode(background)
        background_ = Image.open(BytesIO(image_data))
    bboxes1, list1 = scs.convert_background(hint, True)
    bboxes2, list2 = scs.convert_background(background, False)
    list1_b = deepcopy(list1)
    bboxes2_b = deepcopy(bboxes2)
    for word1 in list1:
        if word1 in list2:
            list1_b.remove(word1)
            idx = list2.index(word1)
            bboxes2_b.remove(bboxes2[idx])
    cv_rgb_image = np.array(background_)
    image = cv2.cvtColor(cv_rgb_image, cv2.COLOR_RGB2BGR)
    for boxe in bboxes2_b:
        if not list1_b:
            break
        binary_data = scs.crop_image_by_coordinates(image, boxe)
        img = Image.open(BytesIO(binary_data))
        for angle in range(-20, 20, 5):
            result = scs.img_rotate_discern(img, angle)
            if result in list1_b:
                idx = bboxes2.index(boxe)
                list2[idx] = result
                list1_b.remove(result)
                break
    print("最后优化识别词：", list1)
    print("最后优化识别选：", list2)
    coors = scs.match_indices_unique(
        list1, list2, font_path="C:/Windows/Fonts/simhei.ttf"
    )
    print({coor: list2[idx] for coor, idx in coors.items()})
    result = [(scs.get_center_coordinate(bboxes2[coor])) for coor in coors.values()]
    # print(result)
    return result
