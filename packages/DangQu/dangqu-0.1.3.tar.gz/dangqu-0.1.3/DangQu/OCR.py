#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/9/26 11:28
# @Author  : dmj-11740
# @File    : OCR.py
# @Software: PyCharm
# @desc    :
import base64
import json
from io import BytesIO

import requests
from PIL import Image


class OCRConfig:
    api = "http://192.168.125.115:3344"


class OCR:

    @staticmethod
    def ocr_file(file_path):
        """
            ocr识别
        :param file_path: 文件路径
        :return:
        """
        api_url = f"{OCRConfig.api}/ocr/file/json"
        file = open(file_path, "rb").read()
        resp = requests.post(api_url, files={"image": file})
        return resp.json()

    @staticmethod
    def ocr_base64(base64_str):
        """
            ocr识别
        :param base64_str: 图片base64
        :return:
        """
        api_url = f"{OCRConfig.api}/ocr/b64/json"
        resp = requests.post(api_url, data=base64_str)
        return resp.json()

    @staticmethod
    def det_file(file_path):
        """
            目标识别
        :param file_path: 文件路径
        :return:
        """
        api_url = f"{OCRConfig.api}/det/file/json"
        file = open(file_path, "rb").read()
        resp = requests.post(api_url, files={"image": file})
        return resp.json()

    @staticmethod
    def det_base64(base64_str):
        """
            目标识别
        :param base64_str: 图片base64
        :return:
        """
        api_url = f"{OCRConfig.api}/det/b64/json"
        resp = requests.post(api_url, data=base64_str)
        return resp.json()

    @staticmethod
    def slide_file(target_file,
                   bg_file,
                   target_to_size: tuple[int, int] = None,
                   bg_to_size: tuple[int, int] = None,
                   algorithm=1):
        """
            滑块识别
        :param target_file: 目标图片路径
        :param bg_file: 背景图片路径
        :param target_to_size: 目标图片需要大小
        :param bg_to_size: 背景图片需要大小
        :param algorithm: 算法，1为匹配:滑块图和坑位图匹配，2为比较:坑位图和背景图比较
        :return:
        """
        method = "match"
        if algorithm != 1:
            method = "compare"
        target_file = open(target_file, "rb").read()
        target_file_bytes = OCR.content_to_bytes(target_file, target_to_size)
        bg_file = open(bg_file, "rb").read()
        bg_file_bytes = OCR.content_to_bytes(bg_file, bg_to_size)
        api_url = f"{OCRConfig.api}/slide/{method}/file/json"
        resp = requests.post(
            api_url, files={"target_img": target_file_bytes, "bg_img": bg_file_bytes}
        )
        return resp.json()

    @staticmethod
    def slide_base64(target_b64str,
                     bg_b64str,
                     target_to_size: tuple[int, int] = None,
                     bg_to_size: tuple[int, int] = None,
                     algorithm=1):
        """
            滑块识别
        :param target_b64str: 目标图片路径
        :param bg_b64str: 背景图片路径
        :param target_to_size: 目标图片需要大小
        :param bg_to_size: 背景图片需要大小
        :param algorithm: 算法，1为匹配:滑块图和坑位图匹配，2为比较:坑位图和背景图比较
        :return:
        """
        method = "match"
        if algorithm != 1:
            method = "compare"
        target_b64str = OCR.content_to_bytes(target_b64str, target_to_size)
        target_b64str = base64.b64encode(target_b64str).decode()
        bg_b64str = OCR.content_to_bytes(bg_b64str, bg_to_size)
        bg_b64str = base64.b64encode(bg_b64str).decode()
        json_str = json.dumps({"target_img": target_b64str, "bg_img": bg_b64str})
        api_url = f"{OCRConfig.api}/slide/{method}/b64/json"
        resp = requests.post(api_url, data=base64.b64encode(json_str.encode()).decode())
        return resp.json()

    @staticmethod
    def content_to_bytes(image_data, to_size: tuple[int, int] = None):
        if isinstance(image_data, bytes):
            image = Image.open(BytesIO(image_data))
        else:
            if "," in image_data:
                image_data = image_data.split(",")[1]
            image_data = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_data))
        # 8位图片转换为32位图片，否则ddddocr无法处理
        if image.mode == "P":
            image = image.convert("RGBA")
        img_byte_arr = BytesIO()
        if to_size:
            image = image.resize(to_size)
        image.save(img_byte_arr, format="PNG")

        return img_byte_arr.getvalue()
