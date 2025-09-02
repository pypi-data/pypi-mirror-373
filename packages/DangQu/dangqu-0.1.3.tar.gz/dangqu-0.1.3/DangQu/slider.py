#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/14 9:59
# @Author  : dmj-11740
# @File    : slider.py
# @Software: PyCharm
# @desc    : 滑块轨迹生成
import io

import numpy as np
import math
import random
import base64

import ddddocr
from PIL import Image


def __ease_out_expo(sep):
    if sep == 1:
        return 1
    else:
        return 1 - pow(2, -10 * sep)

def get_target(self, img_bytes: bytes = None):
    image = Image.open(io.BytesIO(img_bytes))
    return image.crop([1, 1, 47, 47]), 1, 1


def get_slide_track(distance):
    """
        V1:根据滑动距离生成滑动轨迹
    :param distance: 需要滑动的距离
    :return: 滑动轨迹<type 'list'>: [[x,y,t], ...]
        x: 已滑动的横向距离
        y: 已滑动的纵向距离, 除起点外, 均为0
        t: 滑动过程消耗的时间, 单位: 毫秒
    """

    if not isinstance(distance, int) or distance < 0:
        raise ValueError(
            f"distance类型必须是大于等于0的整数: distance: {distance}, type: {type(distance)}"
        )
    # 初始化轨迹列表
    slide_track = [
        [random.randint(-50, -10), random.randint(-50, -10), 0],
        [0, 0, 0],
    ]
    # 共记录count次滑块位置信息
    count = 30 + int(distance / 2)
    # 初始化滑动时间
    t = random.randint(50, 100)
    # 记录上一次滑动的距离
    _x = 0
    _y = 0
    for i in range(count):
        # 已滑动的横向距离
        x = round(__ease_out_expo(i / count) * distance)
        # 滑动过程消耗的时间
        t += random.randint(10, 20)
        if x == _x:
            continue
        slide_track.append([x, _y, t])
        _x = x
    slide_track.append(slide_track[-1])
    return slide_track


def generate_trajectory(distance, shake: bool = True, shake_space: int = 5) -> list:
    """
        根据滑动距离生成自动化操作所用的动作链
    :param distance: 滑动距离
    :param shake: 滑动距离是否左右抖动
    :param shake_space: 抖动范围
    :return:滑动轨迹<type 'list'>: [[x,y,t], ...]
        x: 本次滑动距离
        y: 本次上下抖动距离
        t: 滑动过程消耗的时间, 单位: 秒
    """
    if shake:
        distance += random.randint(-shake_space, shake_space)
    slide_track = get_slide_track(distance)
    trajectory = []
    last_x = 0
    last_time = 0
    for x, y, time in slide_track:
        this_time = time - last_time
        this_x = x - last_x
        trajectory.append([this_x, y, this_time])
        last_time = time
        last_x = x
    # 将轨迹列表中的时间转换为毫秒
    trajectory = [[x, y, time / 1000] for x, y, time in trajectory if x > 0]
    return trajectory


class SliderTrajectory:
    """
        贝赛尔曲线轨迹生成
    """

    def _bztsg(self, dataTrajectory):
        lengthOfdata = len(dataTrajectory)

        def staer(x):
            t = ((x - dataTrajectory[0][0]) / (dataTrajectory[-1][0] - dataTrajectory[0][0]))
            y = np.array([0, 0], dtype=np.float64)
            for s in range(len(dataTrajectory)):
                y += dataTrajectory[s] * ((math.factorial(lengthOfdata - 1) / (
                        math.factorial(s) * math.factorial(lengthOfdata - 1 - s))) * math.pow(t, s) * math.pow(
                    (1 - t), lengthOfdata - 1 - s))
            return y[1]

        return staer

    def _type(self, type, x, numberList):
        numberListre = []
        pin = (x[1] - x[0]) / numberList
        if type == 0:
            for i in range(numberList):
                numberListre.append(i * pin)
            if pin >= 0:
                numberListre = numberListre[::-1]
        elif type == 1:
            for i in range(numberList):
                numberListre.append(1 * ((i * pin) ** 2))
            numberListre = numberListre[::-1]
        elif type == 2:
            for i in range(numberList):
                numberListre.append(1 * ((i * pin - x[1]) ** 2))

        elif type == 3:
            dataTrajectory = [np.array([0, 0]), np.array([(x[1] - x[0]) * 0.8, (x[1] - x[0]) * 0.6]),
                              np.array([x[1] - x[0], 0])]
            fun = self._bztsg(dataTrajectory)
            numberListre = [0]
            for i in range(1, numberList):
                numberListre.append(fun(i * pin) + numberListre[-1])
            if pin >= 0:
                numberListre = numberListre[::-1]
        numberListre = np.abs(np.array(numberListre) - max(numberListre))
        biaoNumberList = ((numberListre - numberListre[numberListre.argmin()]) / (
                numberListre[numberListre.argmax()] - numberListre[numberListre.argmin()])) * (x[1] - x[0]) + x[0]
        biaoNumberList[0] = x[0]
        biaoNumberList[-1] = x[1]
        return biaoNumberList

    def _getFun(self, s):
        '''

        :param s: 传入P点
        :return: 返回公式
        '''
        dataTrajectory = []
        for i in s:
            dataTrajectory.append(np.array(i))
        return self._bztsg(dataTrajectory)

    def _simulation(self, start, end, le=1, deviation=0, bias=0.5):
        '''

        :param start:开始点的坐标 如 start = [0, 0]
        :param end:结束点的坐标 如 end = [100, 100]
        :param le:几阶贝塞尔曲线，越大越复杂 如 le = 4
        :param deviation:轨迹上下波动的范围 如 deviation = 10
        :param bias:波动范围的分布位置 如 bias = 0.5
        :return:返回一个字典equation对应该曲线的方程，P对应贝塞尔曲线的影响点
        '''
        start = np.array(start)
        end = np.array(end)
        cbb = []
        if le != 1:
            e = (1 - bias) / (le - 1)
            cbb = [[bias + e * i, bias + e * (i + 1)] for i in range(le - 1)]

        dataTrajectoryList = [start]

        t = random.choice([-1, 1])
        w = 0
        for i in cbb:
            px1 = start[0] + (end[0] - start[0]) * (random.random() * (i[1] - i[0]) + (i[0]))
            p = np.array([px1, self._bztsg([start, end])(px1) + t * deviation])
            dataTrajectoryList.append(p)
            w += 1
            if w >= 2:
                w = 0
                t = -1 * t

        dataTrajectoryList.append(end)
        # print(dataTrajectoryList)
        return {"equation": self._bztsg(dataTrajectoryList), "P": np.array(dataTrajectoryList)}

    def trackArray(self, start, end, numberList, le=1, deviation=0, bias=0.5, type=0, cbb=0, yhh=10):
        '''

        :param start:开始点的坐标 如 start = [0, 0]
        :param end:结束点的坐标 如 end = [100, 100]
        :param numberList:返回的数组的轨迹点的数量 numberList = 150
        :param le:几阶贝塞尔曲线，越大越复杂 如 le = 4
        :param deviation:轨迹上下波动的范围 如 deviation = 10
        :param bias:波动范围的分布位置 如 bias = 0.5
        :param type:0表示均速滑动，1表示先慢后快，2表示先快后慢，3表示先慢中间快后慢 如 type = 1
        :param cbb:在终点来回摆动的次数
        :param yhh:在终点来回摆动的范围
        :return:返回一个字典trackArray对应轨迹数组，P对应贝塞尔曲线的影响点
        '''
        s = []
        fun = self._simulation(start, end, le, deviation, bias)
        w = fun['P']
        fun = fun["equation"]
        if cbb != 0:
            numberListOfcbb = round(numberList * 0.2 / (cbb + 1))
            numberList -= (numberListOfcbb * (cbb + 1))

            xTrackArray = self._type(type, [start[0], end[0]], numberList)
            for i in xTrackArray:
                s.append([i, fun(i)])
            dq = yhh / cbb
            kg = 0
            ends = np.copy(end)
            for i in range(cbb):
                if kg == 0:
                    d = np.array([end[0] + (yhh - dq * i),
                                  ((end[1] - start[1]) / (end[0] - start[0])) * (end[0] + (yhh - dq * i)) + (
                                          end[1] - ((end[1] - start[1]) / (end[0] - start[0])) * end[0])])
                    kg = 1
                else:
                    d = np.array([end[0] - (yhh - dq * i),
                                  ((end[1] - start[1]) / (end[0] - start[0])) * (end[0] - (yhh - dq * i)) + (
                                          end[1] - ((end[1] - start[1]) / (end[0] - start[0])) * end[0])])
                    kg = 0
                # print(d)
                y = self.trackArray(ends, d, numberListOfcbb, le=2, deviation=0, bias=0.5, type=0, cbb=0, yhh=10)
                s += list(y['trackArray'])
                ends = d
            y = self.trackArray(ends, end, numberListOfcbb, le=2, deviation=0, bias=0.5, type=0, cbb=0, yhh=10)
            s += list(y['trackArray'])

        else:
            xTrackArray = self._type(type, [start[0], end[0]], numberList)
            for i in xTrackArray:
                s.append([i, fun(i)])

        return {"trackArray": np.array(s), "P": w}

    def generate(self, distance, action_count: int = 0, action_time: int = 0):
        """
            根据滑动距离生成滑动轨迹
        :param distance: 需要滑动的距离
        :param action_count: 生成操作数量
        :param action_time: 操作总用时
        :return: 滑动轨迹<type 'list'>: [[x,y,t], ...]
            x: 滑动的横向距离
            y: 滑动的纵向距离
            t: 滑动过程消耗的时间, 单位: 秒
        """
        if action_time == 0:
            action_time = random.randint(700, 2000)
        if action_count == 0:
            action_count = distance // 2 + random.randint(10, 20)
        interval_time = action_time // action_count
        le = random.randint(2, 4)
        action_speed_type = random.randint(0, 3)
        data = self.trackArray([0, 0], np.array([distance, 0]), action_count, le, 20, type=action_speed_type, cbb=2)
        slider_track = [[int(v[0]), int(v[1]), interval_time / 1000] for v in data['trackArray']]
        return slider_track


class Slider:
    def __init__(self, resize_data: list):
        """
            拼图滑块识别
        :param resize_data: 图片在网页中实际大小[(小图x,小图y),(大图x,大图y)]
        """
        self.tailor_y = None
        self.resize_data = resize_data

    def content_to_bytes(self, image_data, image_type):
        first_row_with_pixel, end_row_with_pixel = None, None
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        else:
            if image_data.startswith("data:image/"):
                image_data = image_data.split(",")[1]
            image_data = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_data))
        # 8位图片转换为32位图片，否则ddddocr无法处理
        if image.mode == "P":
            image = image.convert("RGBA")
        if image.mode == "GBA":
            image = image.convert("RGBA")
        # 前端显示的大小非图片大小
        if image_type == "background":
            image = image.resize(self.resize_data[0])
            if self.tailor_y:
                box = (0, self.tailor_y[0], 290, self.tailor_y[1])
                image = image.crop(box)

        elif image_type == "slider":
            image = image.resize(self.resize_data[1])
            pixel = image.load()
            for y in range(image.size[1]):
                row_not_pixel = True
                for x in range(image.size[0]):
                    r, g, b, a = pixel[x, y]
                    if a != 0 and not first_row_with_pixel:
                        first_row_with_pixel = y
                    if a != 0:
                        row_not_pixel = False
                if first_row_with_pixel and row_not_pixel:
                    end_row_with_pixel = y
                if first_row_with_pixel and end_row_with_pixel:
                    break
            first_row_with_pixel = first_row_with_pixel - 10
            end_row_with_pixel = end_row_with_pixel + 10
            self.tailor_y = (first_row_with_pixel, end_row_with_pixel)
            image = image.crop((0, first_row_with_pixel, 60, end_row_with_pixel))

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")

        return img_byte_arr.getvalue()

    def slider_discern(self, slider, background):
        """
            拼图滑块识别
        :param slider: 小图base64
        :param background: 大图base64
        :return: 滑动距离
        """
        try:
            ddddocr.DdddOcr.get_target = get_target
            slide = ddddocr.DdddOcr(det=False, ocr=False)
            slider = self.content_to_bytes(slider, "slider")
            background = self.content_to_bytes(background, "background")
            res = slide.slide_match(slider, background)
            print(f"滑块识别结果[可能需要修正边框距离]：{res}")
            return res["target"][0]
        except Exception as e:
            print(f"滑块识别失败:{e}")
            return 100


