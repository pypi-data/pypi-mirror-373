#! /usr/scripts/env python3
# -*- coding: UTF-8 -*-
##############################################
# Home	: https://www.netkiller.cn
# Author: Neo <netkiller@msn.com>
# Data: 2025-08-29
##############################################
# 鱼骨图（Fishbone Diagram） 又称石川图（英语：Ishikawa Diagram），因果图、关键要因图、要因分析图，它常用于产品设计，来显示某个总体效果的可能因子，从而找到 问题的原因。
# 现代管理学先驱日本学者 石川馨 在川崎重工船厂创建品质管制过程时发明石川图，于1956年发表的著作《品质管理入门》创立的因果模型图，现在已经成为品质管理的七种基本工具之一，识别造成问题的所有潜在因素。

try:
    import os, re
    import json
    # from netkiller import Data
    from netkiller.svg.ScalableVectorGraphics import Svg
    from netkiller.svg.elements import Text, Line, Circle, Rectangle, Group, Path, Image
    from netkiller.svg.color import Color
    from netkiller.svg.font import Font
except ImportError as err:
    print("Error: %s" % (err))
    exit()


class Fishbone:
    canvasTop = 1
    canvasLeft = 1
    canvasWidth = 0
    canvasHeight = 0
    # SVG 实际尺寸
    width = 0
    height = 0

    fishheadWidth = 100
    fishtailWidth = 100
    gapWidth = 100
    gapLeft = 0
    gapRight = 0
    spineX = 0
    spineHeight = 30
    space = 0

    canvasX = 0
    canvasY = 0

    causeHeight = 30
    causeWidth = 100

    fontFamily = "SourceHanSansSC-Normal"
    # fontFamily = "DejaVuSans"
    fontSize = 20

    def __init__(self, data: dict = None):
        self.svg = None
        self.data = data
        self.__fishbone = {"up": {}, "down": {}}
        self.font = Font(self.fontFamily, self.fontSize)
        self.__title = None
        self.__border = 0
        self.__legend = True
        pass

    def __scan(self):
        countEffect = self.data.__len__();
        countCause = max([len(value) for _, value in self.data.items()])

        bearing = "up"
        for effect, cause in self.data.items():
            self.__fishbone[bearing][effect] = cause
            if bearing == "up":
                bearing = "down"
            else:
                bearing = "up"

            textWidth = self.font.getTextSize(effect)
            if textWidth > self.causeWidth:
                self.causeWidth = textWidth

            for item in cause:
                textWidth = self.font.getTextSize(item)
                if textWidth > self.causeWidth:
                    self.causeWidth = textWidth

        if self.__title:
            self.canvasTop = 80

        self.canvasWidth = self.fishtailWidth + countEffect // 2 * (
                self.causeWidth + self.gapWidth + self.space) + self.fishheadWidth
        self.canvasHeight = self.canvasTop + ((countCause + 1) * self.causeHeight) * 2 + self.spineHeight * 2
        self.spineX = self.canvasTop + ((countCause + 1) * self.causeHeight) + self.causeHeight
        self.spineWidth = self.fishtailWidth + countEffect // 2 * (
                self.causeWidth + self.gapWidth + self.space)
        self.width = self.canvasWidth + 2
        self.height = self.canvasHeight + 2

        # reversed_dict = dict(reversed(list(my_dict.items())))

    def render(self):
        color = Color()
        self.__scan()

        excludeColor = []

        self.svg = Svg(self.width, self.height)
        if self.__border > 0:
            # 大边框
            self.svg.append(Rectangle(1, 1, self.width - 2, self.height - 2, fill="none", stroke="black", stroke_width=self.__border))
        self.svg.style("""
    text {
      /* 指定使用的系统字体或自定义字体 */
      font-family: 'PingFang SC', 'Microsoft YaHei', 'SimHei', 'Arial', sans-serif, 'SourceHanSansSC-Normal',"FiraSans";

      /* 添加其他样式 */
      # font-size: 16px;
      # font-weight: bold;
      # font-style: italic;
    }        
        """)

        self.svg.desc("https://www.netkiller.cn")
        self.spineColor = color.random()
        excludeColor.append(self.spineColor)
        self.svg.symbol("fisheye", Circle(10, 10, 10, fill="white"))
        self.svg.symbol("fishtail", Path(d="M6.1898889,1.07915896 C8.01375639,1.44374413 39.1438014,24.7349676 99.5800239,70.9528293 C100.504417,72.644382 100.966613,74.3460926 100.966613,76.057961 C100.966613,77.7698295 100.504417,79.29126 99.5800239,80.6222526 C38.8991612,127.536265 7.76911622,150.993271 6.1898889,150.993271 C3.8210479,150.993271 3.08838333,149.893541 2.14697157,148.24665 C1.20555981,146.599759 0.704233203,144.978499 1.10657556,142.100604 C1.3748038,140.182007 14.3473837,119.418972 40.0243154,79.8114992 C40.8248165,78.2084364 41.2250671,76.9572571 41.2250671,76.057961 C41.2250671,75.158665 40.8248165,74.0777826 40.0243154,72.8153137 L1.10657556,10.0609163 C0.866234283,7.21127309 1.03706053,5.27477589 1.61905431,4.25142465 C2.49204497,2.7163978 3.45408765,0.532281203 6.1898889,1.07915896 Z", stroke="none", fill=self.spineColor))
        self.svg.symbol("fishhead", Path(d="M10.0436088,0.880253165 C31.150854,5.15544681 48.6202114,11.2098158 62.4516813,19.0433601 C76.2831511,26.8769044 89.134037,37.4836677 101.004339,50.8636498 C95.0232906,57.0226854 90.4281099,61.6094262 87.2187969,64.6238722 C84.0094839,67.6383182 81.0594073,70.1386926 78.3685671,72.1249953 C66.6292276,73.5598353 60.2503827,74.6755294 59.2320323,75.4720774 C58.2136819,76.2686254 62.1035274,76.9295203 70.9015687,77.4547621 C67.9815896,79.1338578 65.8096144,80.3671348 64.385643,81.1545932 C58.8868729,84.1954216 51.6843033,88.2759492 42.5402494,91.6010438 C36.6505834,93.7427303 25.8183699,96.8358 10.0436088,100.880253 C4.01742896,83.9414693 1.00433901,67.2692682 1.00433901,50.8636498 C1.00433901,34.4580314 4.01742896,17.7968992 10.0436088,0.880253165 Z", stroke="none", fill=self.spineColor))

        if self.__title:
            self.svg.append(Text(self.__title, self.canvasWidth / 2, self.canvasTop / 2, text_anchor="middle", fill="black", font_size="40"))

        if self.__legend:
            self.svg.append(Text("https://www.netkiller.cn - design by netkiller", self.canvasWidth / 2, self.spineX - 5, text_anchor="middle", fill="grey"))
            self.svg.append(Image(5, 5, 100, 35, href="https://www.netkiller.cn/graphics/by-nc-sa.png"))

        # self.svg.append(Rectangle(200, 200, 100, 100, style="stroke:#009900; fill: #00cc00"))

        # self.svg.use(100, 50, "shape1", style="stroke: #00ff00; fill: none;")

        self.canvasX = self.fishtailWidth

        for effect, cause in self.__fishbone['up'].items():
            group = Group(clazz="effect")
            self.canvasY = self.canvasTop
            textWidth = self.font.getTextSize(effect)
            effectColor = color.randomAndExclude(excludeColor)
            excludeColor.append(effectColor)
            group.append(Rectangle(self.canvasX - 10, self.canvasY, textWidth + 20, self.causeHeight, stroke="none", fill=effectColor, rx="5", ry="5"))

            self.canvasY += self.causeHeight
            group.append(Text(effect, self.canvasX + textWidth / 2, self.canvasY - self.causeHeight / 4, text_anchor="middle", fill="white", font_size=self.fontSize))

            self.gapLeft = self.canvasX + textWidth
            self.gapRight = self.gapLeft + self.gapWidth
            group.append(Line(self.gapLeft, self.canvasY - self.causeHeight / 2, self.gapRight, self.spineX, stroke=effectColor, stroke_width="2"))

            self.canvasY += self.causeHeight / 2
            excludeCauseColor = []
            for item in cause:
                cx = self.gapWidth * (self.canvasY - self.canvasTop) / (
                        self.spineX - self.causeHeight / 2 - self.canvasTop)
                textWidth = self.font.getTextSize(item)
                self.canvasY += self.causeHeight
                causeColor = color.randomAndExclude(excludeCauseColor)
                excludeCauseColor.append(causeColor)
                group.append(Circle(cx=self.gapLeft + cx, cy=self.canvasY - 15, r="3", fill=effectColor, stroke="none", stroke_width="1"))
                group.append(Text(item, self.gapLeft + cx - textWidth - 20, self.canvasY - self.causeHeight / 4, fill=causeColor, font_size=self.fontSize))

            self.svg.append(group)
            self.canvasX += self.causeWidth + self.space

        self.canvasX = self.fishtailWidth
        for effect, cause in self.__fishbone['down'].items():
            group = Group(clazz="effect")
            self.canvasY = self.canvasHeight
            textWidth = self.font.getTextSize(effect)
            effectColor = color.randomAndExclude(excludeColor)
            excludeColor.append(effectColor)
            print(excludeColor)
            group.append(Rectangle(self.canvasX - 10, self.canvasY - self.causeHeight, textWidth + 20, self.causeHeight, stroke="none", fill=effectColor, rx="5", ry="5"))
            group.append(Text(effect, self.canvasX + textWidth / 2, self.canvasY - self.causeHeight / 4, text_anchor="middle", fill="white", font_size=self.fontSize))

            self.gapLeft = self.canvasX + textWidth
            self.gapRight = self.gapLeft + self.gapWidth
            group.append(Line(self.gapLeft, self.canvasY - 15, self.gapRight, self.spineX, stroke=effectColor, stroke_width="2"))

            self.canvasY -= self.causeHeight / 2
            excludeCauseColor = []
            for item in cause:
                cx = self.gapWidth * (self.canvasHeight - self.canvasY + 30) / (
                        self.spineX - self.causeHeight / 2 - self.canvasTop)
                textWidth = self.font.getTextSize(item)
                self.canvasY -= self.causeHeight
                causeColor = color.randomAndExclude(excludeCauseColor)
                excludeCauseColor.append(causeColor)
                group.append(Circle(cx=self.gapLeft + cx, cy=self.canvasY - 15, r="3", fill=effectColor, stroke="none", stroke_width="1"))
                group.append(Text(item, self.gapLeft + cx - textWidth - 20, self.canvasY - self.causeHeight / 4, fill=causeColor, font_size=self.fontSize))

            self.svg.append(group)
            self.canvasX += self.causeWidth + self.space
            self.svg.append(group)

        # self.svg.append(Rectangle(x="10", y=self.spineX, width=self.spineWidth, height=self.spineHeight, rx="5", ry="5", style="stroke: black; fill: none;"))
        self.svg.use("fishtail", x=1, y=self.spineX - 75, width=100, height=150)
        self.svg.append(Line(x1="90", y1=self.spineX, x2=self.spineWidth + 2, y2=self.spineX, stroke=self.spineColor, stroke_width="8"))
        self.svg.use("fishhead", x=self.spineWidth, y=self.spineX - 50, width=100, height=100)
        self.svg.use("fisheye", x=self.spineWidth + 20, y=self.spineX - 25)

    def title(self, text):
        self.__title = text

    def border(self, width: int = 0):
        self.__border = width

    def legend(self, enable: bool):
        self.__legend = enable

    def save(self, filename):
        self.render()
        self.svg.save(filename)

    def debug(self):
        print(f"Canvas {self.canvasWidth}x{self.canvasHeight}")
        print(self.__fishbone)
        pass

    def main(self):

        pass


def main():
    try:
        fishbone = Fishbone()
        fishbone.main()
    except KeyboardInterrupt as e:
        print(e)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
