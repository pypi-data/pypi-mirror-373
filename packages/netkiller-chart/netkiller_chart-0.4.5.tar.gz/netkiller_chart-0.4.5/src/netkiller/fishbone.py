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
    import os, re, math, json
    # from netkiller.data import Data
    from netkiller.svg.ScalableVectorGraphics import Svg
    from netkiller.svg.elements import Text, Line, Circle, Rectangle, Group, Path, Image, Use
    from netkiller.svg.color import Color
    from netkiller.svg.font import Font
    from netkiller.markdown import Markdown
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
    spineY = 0
    spineHeight = 30
    spineWidth = fishheadWidth + fishtailWidth
    fishboneWidth = 0
    space = 0

    canvasX = 0
    canvasY = 0

    fontFamily = "SourceHanSansSC-Normal"
    # fontFamily = "DejaVuSans"
    fontSize = 20

    causeHeight = 30
    effectWidth = {"up": {}, "down": {}}

    def __init__(self, data: dict = None):
        self.svg = None
        if data:
            self.data = data
        else:
            self.data = {}
        self.__fishbone = {"up": {}, "down": {}}
        self.font = Font(self.fontFamily, self.fontSize)
        self.__title = None
        self.__department = None
        self.__border = 0
        self.__legend = True
        pass

    def clean(self):
        self.svg = None
        self.data = {}
        self.__fishbone = {"up": {}, "down": {}}
        self.effectWidth = {"up": {}, "down": {}}
        # self.fishboneWidth = 0
        self.spineWidth = 0

    def __scan(self):
        countEffect = self.data.__len__();
        countCause = max([len(value) for _, value in self.data.items()])
        if countCause == 0:
            countCause = 1

        bearing = "up"
        for effect, cause in self.data.items():
            self.__fishbone[bearing][effect] = cause

            # self.__fontWidth(effect, cause)
            self.effectWidth[bearing][effect] = {}
            textWidth = self.font.getTextSize(effect)
            self.effectWidth[bearing][effect][effect] = textWidth

            # if textWidth > self.fishboneWidth:
            #     self.fishboneWidth = textWidth

            causeFont = Font(self.fontFamily, 18)
            for item in cause:
                textWidth = causeFont.getTextSize(item)
                self.effectWidth[bearing][effect][item] = textWidth
                # if textWidth > self.fishboneWidth:
                #     self.fishboneWidth = textWidth

            if bearing == "up":
                bearing = "down"
            else:
                bearing = "up"

        if self.__title:
            self.canvasTop = 80

        up = [n.values() for n in self.effectWidth['up'].values()]
        upMaxWidth = sum([max(n) for n in up])

        down = [n.values() for n in self.effectWidth['down'].values()]
        downMaxWidth = sum([max(n) for n in down])

        self.fishboneWidth = max(upMaxWidth, downMaxWidth)
        # print(countEffect, countEffect // 2, countEffect % 2, math.ceil(countEffect / 2))
        # print(self.fishboneWidth)

        if countEffect == 1:
            self.canvasWidth = self.fishtailWidth + self.fishboneWidth + countEffect * (
                    self.gapWidth + self.space) + self.fishheadWidth + self.gapWidth / 2
            self.spineWidth = self.fishtailWidth + self.fishboneWidth + countEffect * (
                    self.gapWidth / 2 + self.space) + self.fishheadWidth
        else:
            self.canvasWidth = self.fishtailWidth + self.fishboneWidth + countEffect // 2 * (
                    self.gapWidth + self.space) + self.gapWidth + self.fishheadWidth + self.gapWidth / 2
            # if countEffect % 2 == 0:
            #     self.spineWidth = self.fishtailWidth + self.fishboneWidth + math.ceil(countEffect / 2) * (
            #             self.gapWidth + self.space) - self.gapWidth / 2 + self.fishheadWidth
            # else:
            self.spineWidth = self.fishtailWidth + self.fishboneWidth + math.ceil(countEffect / 2) * (
                    self.gapWidth + self.space) - self.gapWidth / 2 + self.fishheadWidth
        self.canvasHeight = self.canvasTop + ((countCause + 1) * self.causeHeight) * 2 + self.spineHeight * 2
        self.spineY = self.canvasTop + ((countCause + 1) * self.causeHeight) + self.causeHeight
        self.width = self.canvasWidth + 2
        self.height = self.canvasHeight + 2

        # print(self.effectWidth)
        # reversed_dict = dict(reversed(list(my_dict.items())))

    def render(self):
        if not self.data:
            raise ValueError(f"数据出错")
        color = Color()
        # causeFontSize = 18
        # causeFont = Font(self.fontFamily, causeFontSize)

        self.__scan()

        excludeColor = []

        self.svg = Svg(self.width, self.height)
        if self.__border > 0:
            # 大边框
            self.svg.append(Rectangle(1, 1, self.width - 2, self.height - 2, fill="none", stroke="black", stroke_width=self.__border))
        self.svg.style("""
    text {
      /* 指定使用的系统字体或自定义字体 */
      font-family: "SourceHanSansSC-Normal";
      # 'SourceHanSansSC-Normal' , 'PingFang SC', 'Microsoft YaHei', 'SimHei', 'Arial', sans-serif, ,"FiraSans";

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
            self.svg.append(Text("https://www.netkiller.cn - design by netkiller", self.canvasWidth / 2, self.spineY - 5, text_anchor="middle", fill="grey"))
            self.svg.append(Image(5, 5, 100, 35, href="https://www.netkiller.cn/graphics/by-nc-sa.png"))
        if self.__department:
            self.svg.append(Text(self.__department, self.canvasWidth / 2, self.canvasTop - self.causeHeight + 15, text_anchor="middle", fill="grey", font_size=16))
        # self.svg.append(Rectangle(200, 200, 100, 100, style="stroke:#009900; fill: #00cc00"))

        # self.svg.use(100, 50, "shape1", style="stroke: #00ff00; fill: none;")

        self.canvasX = self.fishtailWidth

        for effect, cause in self.__fishbone['up'].items():

            longestText = max(self.effectWidth['up'][effect].values())

            self.canvasY = self.canvasTop
            # textWidth = self.font.getTextSize(effect)
            effectTextWidth = self.effectWidth['up'][effect][effect]
            effectColor = color.randomAndExclude(excludeColor)
            excludeColor.append(effectColor)

            causeFontSize = 18
            # causeFont = Font(self.fontFamily, causeFontSize)
            group = Group(clazz="effect")
            group.append(Rectangle(self.canvasX + longestText - effectTextWidth - 10, self.canvasY, effectTextWidth + 20, self.causeHeight, stroke="none", fill=effectColor, rx="5", ry="5"))
            self.canvasY += self.causeHeight
            group.append(Text(effect, self.canvasX +
                              longestText - effectTextWidth / 2, self.canvasY - self.causeHeight / 4, text_anchor="middle", fill="white", font_size=self.fontSize))
            self.gapLeft = self.canvasX + longestText
            self.gapRight = self.gapLeft + self.gapWidth
            group.append(Line(self.gapLeft, self.canvasY - self.causeHeight / 2, self.gapRight, self.spineY, stroke=effectColor, stroke_width="2"))

            self.canvasY += self.causeHeight / 2
            excludeCauseColor = [self.spineColor, effectColor]
            for item in cause:
                cx = self.gapWidth * (self.canvasY - self.canvasTop) / (
                        self.spineY - self.causeHeight / 2 - self.canvasTop)
                # textWidth = causeFont.getTextSize(item)
                causeTextWidth = self.effectWidth['up'][effect][item]
                self.canvasY += self.causeHeight
                causeColor = color.randomAndExclude(excludeCauseColor)
                excludeCauseColor.append(causeColor)
                group.append(Circle(cx=self.gapLeft + cx, cy=self.canvasY - 15, r="3", fill=effectColor, stroke="none", stroke_width="1"))
                group.append(Text(item, self.gapLeft + cx - causeTextWidth - 20, self.canvasY - self.causeHeight / 4, fill=causeColor, font_size=causeFontSize))

            self.svg.append(group)
            # self.canvasX += self.effectWidth + self.space
            self.canvasX += longestText + self.gapWidth + self.space
            # if self.canvasX > self.spineWidth:
            #     self.spineWidth = self.canvasX + self.gapWidth / 2 + self.fishheadWidth

        self.canvasX = self.fishtailWidth
        for effect, cause in self.__fishbone['down'].items():

            longestText = max(self.effectWidth['down'][effect].values())
            self.canvasY = self.canvasHeight
            # textWidth = self.font.getTextSize(effect)
            effectTextWidth = self.effectWidth['down'][effect][effect]
            effectColor = color.randomAndExclude(excludeColor)
            excludeColor.append(effectColor)

            group = Group(clazz="effect")
            group.append(Rectangle(self.canvasX + longestText - effectTextWidth - 10, self.canvasY - self.causeHeight, effectTextWidth + 20, self.causeHeight, stroke="none", fill=effectColor, rx="5", ry="5"))
            group.append(Text(effect, self.canvasX + longestText - effectTextWidth / 2, self.canvasY - self.causeHeight / 4, text_anchor="middle", fill="white", font_size=self.fontSize))

            self.gapLeft = self.canvasX + longestText
            self.gapRight = self.gapLeft + self.gapWidth
            group.append(Line(self.gapLeft, self.canvasY - 15, self.gapRight, self.spineY, stroke=effectColor, stroke_width="2"))

            self.canvasY -= self.causeHeight / 2
            excludeCauseColor = [self.spineColor, effectColor]
            for item in cause:
                cx = self.gapWidth * (self.canvasHeight - self.canvasY + 30) / (
                        self.spineY - self.causeHeight / 2 - self.canvasTop)
                # textWidth = causeFont.getTextSize(item)
                causeTextWidth = self.effectWidth['down'][effect][item]
                self.canvasY -= self.causeHeight
                causeColor = color.randomAndExclude(excludeCauseColor)
                excludeCauseColor.append(causeColor)
                group.append(Circle(cx=self.gapLeft + cx, cy=self.canvasY - 15, r="3", fill=effectColor, stroke="none", stroke_width="1"))
                group.append(Text(item, self.gapLeft + cx - causeTextWidth - 20, self.canvasY - self.causeHeight / 4, fill=causeColor, font_size=causeFontSize))

            self.svg.append(group)
            self.canvasX += longestText + self.gapWidth + self.space
            # if self.canvasX > self.spineWidth:
            #     self.spineWidth = self.canvasX + self.gapWidth / 2 + self.fishheadWidth

        group = Group(clazz="effect")
        # self.svg.append(Rectangle(x="10", y=self.spineY, width=self.spineWidth, height=self.spineHeight, rx="5", ry="5", style="stroke: black; fill: none;"))
        group.append(Use(id="fishtail", x=1, y=self.spineY - 75, width=100, height=150))
        group.append(Line(x1="90", y1=self.spineY, x2=self.spineWidth + 2, y2=self.spineY, stroke=self.spineColor, stroke_width="8"))
        group.append(Use(id="fishhead", x=self.spineWidth, y=self.spineY - 50, width=100, height=100))
        group.append(Use(id="fisheye", x=self.spineWidth + 20, y=self.spineY - 25))
        self.svg.append(group)

    def title(self, text):
        self.__title = text

    def department(self, text):
        self.__department = text

    def border(self, width: int = 0):
        self.__border = width

    def legend(self, enable: bool):
        self.__legend = enable

    def save(self, filename):
        self.render()
        self.svg.save(filename)

    def show(self):
        self.render()
        return self.svg.show()

    def debug(self):
        print(f"Canvas {self.canvasWidth}x{self.canvasHeight}")
        print(self.__fishbone)
        pass

    def markdown(self, text):
        if not text:
            raise ValueError("Markdown 出错")
        self.clean()
        markdown = Markdown(text)
        self.data = markdown.fishbone()

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
