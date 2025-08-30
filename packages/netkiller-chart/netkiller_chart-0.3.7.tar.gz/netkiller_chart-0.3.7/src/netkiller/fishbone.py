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
    import re
    import json
    # from netkiller import Data
    from netkiller.svg.ScalableVectorGraphics import Svg
    from netkiller.svg.elements import Text, Line, Circle, Rectangle, Group
    from netkiller.svg.color import *
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

    fishheadWidth = 200
    fishtailWidth = 200

    # splitLineHeight = 1
    causeHeight = 30
    causeWidth = 300

    spineHeight = 30

    fontFamily = "SourceHanSansSC-Normal"
    # fontFamily = "DejaVuSans"
    fontSize = 18

    def __init__(self, data: dict = None):
        self.svg = None
        self.data = data
        self.__fishbone = {"up": {}, "down": {}}
        self.font = Font(self.fontFamily, self.fontSize)

        pass

    def __scan(self):
        self.canvasWidth = self.fishtailWidth + self.data.__len__() * self.causeWidth + self.fishheadWidth
        countEffect = max([len(value) for _, value in self.data.items()])
        self.canvasHeight = (countEffect + 1) * self.causeHeight * 2 + self.spineHeight
        self.width = self.canvasWidth + 2
        self.height = self.canvasHeight + 2

        bearing = "up"
        for effect, cause in self.data.items():
            self.__fishbone[bearing][effect] = cause
            if bearing == "up":
                bearing = "down"
            else:
                bearing = "up"
        print(self.__fishbone)
        # reversed_dict = dict(reversed(list(my_dict.items())))

    def render(self):
        self.__scan()

        self.svg = Svg(self.width, self.height)
        # 大边框
        self.svg.append(Rectangle(1, 1, self.width - 2, self.height - 2, fill="none", stroke="black"))
        self.svg.style("""
    text {
      /* 指定使用的系统字体或自定义字体 */
      font-family: "FiraSans", sans-serif;

      /* 添加其他样式 */
      font-size: 16px;
      # font-weight: bold;
      # font-style: italic;
    }        
        """)
        # self.svg.title("Test")
        # self.svg.desc("https://www.netkiller.cn")
        # self. svg.append(Title("Hello world"))
        # self.svg.symbol("shape1", Circle(25, 25, 25, "gery"))
        # self.svg.append(Text(100, 200, "Hello world", klass="test"))
        #
        # self.svg.append(Circle(100, 200, 100, "red", fill="none"))

        # self.svg.append(Rectangle(200, 200, 100, 100, style="stroke:#009900; fill: #00cc00"))
        # self.svg.append(Image(300, 300, 100, 100, href="https://www.netkiller.cn/graphics/by-nc-sa.png"))
        # self.svg.use(10, 10, "shape1")
        # self.svg.use(100, 50, "shape1", style="stroke: #00ff00; fill: none;")
        x = self.canvasLeft
        for effect, cause in self.__fishbone['up'].items():
            group = Group(clazz="effect")

            y = self.canvasTop
            textWidth = self.font.getTextSize(effect)
            group.append(Rectangle(x, y, textWidth, self.causeHeight, "blue", fill="green"))
            y += self.causeHeight
            group.append(Line(x + textWidth / 2, y, x + self.causeWidth / 2, self.canvasHeight / 2, stroke="#006600"))
            group.append(Text(effect, x + textWidth / 2, y - self.causeHeight / 4, text_anchor="middle"))

            y += self.causeHeight
            for item in cause:
                x += 30
                y += self.causeHeight

                group.append(Text(item, x, y))
            self.svg.append(group)
            x += self.causeWidth
        # self.svg.append(Path('M100,100 L150,100 L150,150 Z'))
        # self.svg.append(Path().D().M(10, 10).L(10, 15).L(20, 26).H(11).V(30).Z())
        # self.svg.append(Line(100, 200, 300, 300, stroke="#006600"))
        # self.svg.append(Ellipse(30, 30, 30, 15, style="stroke:#006600; fill:#00cc00"))

    def save(self, filename):
        self.render()
        self.svg.save(filename)

    def debug(self):
        print(f"Canvas {self.canvasWidth}x{self.canvasHeight}")
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
