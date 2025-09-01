#! /usr/scripts/env python3
# -*- coding: UTF-8 -*-
##############################################
# Home	: https://www.netkiller.cn
# Author: Neo <netkiller@msn.com>
# Data: 2025-08-29
##############################################
import random


class Color:
    color = ["#ff7f0e",
             "#2ca02c",
             "#d62728",
             "#9467bd",
             "#1f77b4",
             "#e377c2",
             "#7f7f7f",
             "#bcbd22",
             "#17becf",
             "#8c564b",
             "#ff7f0e",
             "#2ca02c",
             "#d62728",
             "#9467bd",
             "#8c564b",
             "#ff7f0e",
             "#7f7f7f",
             "#17becf",
             "#1f77b4",
             "#ff7f0e",
             "#bcbd22",
             "#d62728",
             "#9467bd",
             "#2ca02c",
             "#e377c2",
             "#1f77b4",
             "#bcbd22",
             "#1f77b4",
             "#ff7f0e",
             "#2ca02c",
             "#d62728",
             "#17becf",
             "#7f7f7f",
             "#8c564b",
             "#7f7f7f",
             "#bcbd22",
             "#1f77b4",
             "#ff7f0e",
             "#17becf",
             "#e377c2",
             "#9467bd",
             "#d62728",
             "#9467bd",
             "#2ca02c",
             "#7f7f7f",
             "#bcbd22",
             "#17becf",
             "#e377c2",
             "#ff7f0e",
             "#2ca02c",
             "#1f77b4",
             "#8c564b",
             "#8c564b",
             "#e377c2",
             "#9467bd",
             "#bcbd22",
             "#17becf",
             "#7f7f7f",
             "#d62728",
             "#2ca02c",
             "#d62728",
             "#9467bd",
             "#ff7f0e",
             "#e377c2",
             "#bcbd22",
             "#17becf",
             "#1f77b4",
             "#7f7f7f",
             "#8c564b",
             "#1f77b4",
             "#2ca02c",
             "#d62728",
             "#ff7f0e",
             "#e377c2",
             "#7f7f7f",
             "#8c564b",
             "#17becf",
             "#bcbd22",
             "#9467bd",
             "#ff7f0e",
             "#d62728",
             "#9467bd",
             "#2ca02c",
             "#1f77b4",
             "#e377c2",
             "#7f7f7f",
             "#17becf",
             "#1f77b4",
             "#bcbd22",
             "#e377c2",
             "#2ca02c",
             "#d62728",
             "#8c564b",
             "#e377c2",
             "#7f7f7f",
             "#9467bd",
             "#ff7f0e",
             "#8c564b",
             "#8c564b",
             "#1f77b4",
             "#ff7f0e",
             "#2ca02c",
             "#17becf",
             "#8c564b",
             "#e377c2",
             "#9467bd",
             "#bcbd22",
             "#7f7f7f",
             "#1f77b4",
             "#ff7f0e",
             "#17becf",
             "#d62728",
             "#2ca02c",
             "#d62728",
             "#bcbd22",
             "#1f77b4", ]

    def __init__(self):
        pass

    def system(self):
        # 红色：red（#FF0000）
        # 绿色：green（#008000）
        # 蓝色：blue（#0000FF）
        # 黄色：yellow（#FFFF00）
        # 黑色：black（#000000）
        # 白色：white（#FFFFFF）
        # 灰色：gray（#808080）
        # 粉色：pink（#FFC0CB）
        # 紫色：purple（#800080）
        # 橙色：orange（#FFA500）
        # 棕色：brown（#A52A2A）
        # 青色：cyan（#00FFFF）
        # 品红：magenta（#FF00FF）
        # 银色：silver（#C0C0C0）
        # 金色：gold（#FFD700）

        color = [
            "red", "green", "blue", "black", "gray", "pink", "purple", "orange", "brown", "cyan", "magenta", "gold",
            "#005588",
        ]
        return random.choice(color)

    def rgb(self):
        """生成随机 RGB 颜色（返回 (r, g, b) 元组）"""
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return f'#{r:02X}{g:02X}{b:02X}'

    def rgba(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        a = round(random.uniform(0, 1), 2)  # 透明度保留2位小数
        return (r, g, b, a)

    def random(self):
        return random.choice(self.color)

    def randomAndExclude(self, excludes: list):
        color = [x for x in self.color if x not in excludes]
        # if excludes:
        #     for exclude in excludes:
        #         if exclude in self.color:
        #             self.color.remove(exclude)
        #     # color = self.color

        # print(color)
        return random.choice(color)
