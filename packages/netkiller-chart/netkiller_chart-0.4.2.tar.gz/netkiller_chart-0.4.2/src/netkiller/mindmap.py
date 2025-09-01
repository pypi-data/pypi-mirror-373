#! /usr/scripts/env python3
# -*- coding: UTF-8 -*-
##############################################
# Home	: http://netkiller.github.io
# Author: Neo <netkiller@msn.com>
# Data: 2025-07-19
##############################################

try:
    import os, sys, random

    module = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # print(module)
    sys.path.insert(0, ".")
    sys.path.insert(1, module)
    import svgwrite
    from PIL import ImageFont, ImageDraw, Image
    import argparse
    from netkiller.markdown import Markdown
    import xmind
    # from cairosvg import svg2png
except ImportError as err:
    print("Error: %s" % (err))
    exit()


class Mindmap:
    fontSize = 16
    # fontFamily = "SimHei"
    # fontFamily = "Helvetica"
    # fontFamily = "Times"
    # fontFamily = "PingFang"
    # fontFamily = "SimSun"
    fontFamily = "Songti"
    # fontColor = "black"
    fontColor = "#515151"

    distance = 100
    charHeight = 30
    level = 0

    def __init__(self, jsonObject: dict = None):
        self.coordinate = {}
        self.horizontalPosition = 0
        self.verticalPosition = 0
        self.verticalOffset = 0
        self.width = 0
        self.height = 0
        self.jsonObject = jsonObject
        self.level = {}
        self.about = 'Design by neo<netkiller@msn.com> - https://www.netkiller.cn'
        self.desc = None

    def sytle(self):
        # 定义样式（颜色、字体等）
        styles = """
            .center-node { fill: #4a90e2; stroke: #333; stroke-width: 2; }
            .center-text { font-family: Arial; font-size: 16px; font-weight: bold; fill: white; text-anchor: middle; dominant-baseline: middle; }
            .level1-node { fill: #5cb85c; stroke: #333; stroke-width: 1.5; rx: 5; ry: 5; } /* 带圆角的矩形 */
            .level1-text { font-family: Arial; font-size: 14px; fill: white; text-anchor: middle; dominant-baseline: middle; }
            .level2-node { fill: #f0ad4e; stroke: #333; stroke-width: 1; rx: 3; ry: 3; }
            .level2-text { font-family: Arial; font-size: 12px; fill: #333; text-anchor: middle; dominant-baseline: middle; }
            .connection { stroke: #666; stroke-width: 1.5; fill: none; }
        """
        self.dwg.defs.add(self.dwg.style(styles))

    def font(self, family: str):
        self.fontFamily = family

    def title(self, text):
        title = self.dwg.text(text, insert=(self.width / 2, self.charHeight + self.charHeight // 2),
                              text_anchor='middle',
                              font_size='25', font_family='Arial')
        self.dwg.add(title)

        if self.about:
            author = self.dwg.text(self.about, insert=(self.width / 2, self.charHeight + self.charHeight),
                                   text_anchor='middle',
                                   font_size='10', font_family='Arial')
            self.dwg.add(author)

        if self.desc:
            author = self.dwg.text(self.desc, insert=(self.width / 2, self.height - 2),
                                   text_anchor='middle',
                                   font_size='10', font_family='Arial')
            self.dwg.add(author)

    def author(self, value: str):
        self.about = value

    def description(self, value: str):
        self.desc = value

    def center(self, text: str):
        x = self.horizontalPosition
        y = self.verticalPosition // 2 + self.fontSize * 2
        width = self.fontSize * len(text)
        height = self.fontSize * 2

        self.dwg.add(self.dwg.rect(insert=(0, y), size=(width, height), rx=30, ry=10, fill='lightgreen',
                                   stroke='green',
                                   stroke_width=2))
        self.dwg.add(
            self.dwg.text(text, insert=(width // 2, y + self.fontSize + self.fontSize // 4), text_anchor='middle'))

    def root(self, text: str):
        x = self.horizontalPosition
        y = self.verticalPosition // 2 + self.charHeight + self.charHeight // 2
        width = self.horizontalPosition
        color = self.randomColor()

        self.dwg.add(self.dwg.line(start=(2, y), end=(width, y), stroke=f'{color}', stroke_width=3))

        circle = self.dwg.circle(center=(width, y), r=5, fill="white", stroke=f"{color}", stroke_width="2")
        self.dwg.add(circle)
        self.dwg.add(self.dwg.text(text, insert=(width // 2, y - 5), text_anchor='middle',
                                   font_family=f"{self.fontFamily}",
                                   font_size=f"{self.fontSize}",
                                   fill=f"{self.fontColor}"
                                   ))

    def rectangle(self, text: str):
        rect1 = self.dwg.rect(insert=(50, 70), size=(100, 80), rx=15, ry=15,
                              fill='lightblue', stroke='blue', stroke_width=2)
        self.dwg.add(rect1)
        self.dwg.add(self.dwg.text(text, insert=(100, 120), text_anchor='middle'))
        # self.dwg.add(self.dwg.rect(insert=(0, 0), size=("100%", "100%"), fill='green'))

    def ellipse(self, text: str):
        # 1. 基本椭圆：中心点(150, 100)，水平半径100，垂直半径50
        # 参数说明：
        # center: (cx, cy) 椭圆中心点坐标
        # r: (rx, ry) 水平半径和垂直半径
        basic_ellipse = self.dwg.ellipse(center=(150, 100), r=(100, 50),
                                         fill="lightblue",  # 填充色
                                         stroke="blue",  # 边框色
                                         stroke_width=2)  # 边框宽度
        self.dwg.add(basic_ellipse)
        # self.dwg.add(self.dwg.text("基本椭圆", insert=(150, 100), text_anchor="middle", dominant_baseline="middle"))

    def textNode(self, parentNode: dict, node: dict, color: str, width):

        width = node['x'] + width

        self.dwg.add(self.dwg.text(node['text'], insert=(node["x"] + 4, node["y"] - 4), text_anchor='start',
                                   font_family=f"{self.fontFamily}",
                                   font_size=f"{self.fontSize}",
                                   fill=f"{self.fontColor}"))
        path = self.dwg.path(
            d=f'M {parentNode["x"]},{parentNode["y"]} H {parentNode["x"] + self.distance / 2} V {node["y"]} H {node["x"]}',
            fill='none', stroke='#FF5722', stroke_width=2)
        # self.dwg.add(path)
        line = self.dwg.line(start=(node["x"], node["y"]), end=(width, node["y"]), stroke=f'{color}', stroke_width=2)

        circle = self.dwg.circle(center=(width, node["y"]), r=5, fill="white", stroke=f"{color}", stroke_width="2")

        self.dwg.add(line)
        self.dwg.add(circle)

    def bezierCurveNode(self, parentNode: dict, node: dict, width: int):
        self.dwg.add(self.dwg.text(node['text'], insert=(node["x"], node["y"]), text_anchor='start'))

        path = self.dwg.path(
            d=f'M{parentNode["x"]},{parentNode["y"]} C{parentNode["x"] + self.distance / 2},{parentNode["y"]} {node["x"] - self.distance / 2},{node["y"]} {node["x"]},{node["y"]} L{node["x"] + width},{node["y"]}',
            fill='none', stroke='#FF5722', stroke_width=2)

        self.dwg.add(path)

    def curve(self, parentNode, node, color: str):

        path = self.dwg.path(
            d=f'M{parentNode["x"]},{parentNode["y"]} C{parentNode["x"] + self.distance / 2},{parentNode["y"]} {node["x"] - self.distance / 2},{node["y"]} {node["x"]},{node["y"]}',
            fill='none', stroke=f'{color}', stroke_width=2)

        self.dwg.add(path)

    def scan(self, childNode, horizontalOffset: int = 0, level=1):

        textWidth = 0
        for child in childNode:
            width, height = self.getTextSize(child['text'])
            if width > textWidth:
                textWidth = width

        if textWidth > 0:
            textWidth += 5

        if level not in self.level:
            self.level[level] = True
            self.width += self.distance + horizontalOffset + textWidth

        for child in childNode:

            if 'children' in child and len(child['children']) > 0:
                self.scan(child['children'], textWidth, level + 1)
            else:
                self.skipNode = False
                self.height += self.charHeight;

    def arrange(self, childNode: list, horizontalOffset: int = 0):

        textWidth = 0
        for child in childNode:
            width, height = self.getTextSize(child['text'])
            if width > textWidth:
                textWidth = width

        if textWidth > 0:
            textWidth += 5

        currentVerticalPosition = self.verticalPosition
        currentHorizontalPosition = self.distance + horizontalOffset
        self.horizontalPosition += currentHorizontalPosition

        curve = []

        x = self.horizontalPosition

        for child in childNode:

            if 'children' in child:
                if len(child['children']) > 0:
                    self.arrange(child['children'], textWidth)
                else:
                    pass

            if self.verticalOffset:
                y = self.verticalPosition - self.verticalOffset + self.charHeight // 2
                self.verticalOffset = 0

            else:
                self.verticalPosition += self.charHeight;
                y = self.verticalPosition

            color = self.randomColor()
            text = child["text"]

            # self.textNode({"x": 0, "y": 0}, {"x": x, "y": y, "text": child["text"]}, color, textWidth)
            curve.append((x, y, color, text))

        self.verticalOffset = (self.verticalPosition - currentVerticalPosition) // 2
        self.horizontalPosition -= currentHorizontalPosition

        px = self.horizontalPosition + horizontalOffset
        py = self.verticalPosition - self.verticalOffset + self.charHeight // 2
        for x, y, c, t in curve:
            self.curve({"x": px, "y": py}, {"x": x, "y": y}, c)
            self.textNode({"x": 0, "y": 0}, {"x": x, "y": y, "text": t}, c, textWidth + 5)

    def randomColor(self):
        """生成随机 RGB 颜色（返回 (r, g, b) 元组）"""
        # r = random.randint(0, 255)
        # g = random.randint(0, 255)
        # b = random.randint(0, 255)
        # return f'#{r:02X}{g:02X}{b:02X}'

        # a = round(random.uniform(0, 1), 2)  # 透明度保留2位小数
        # return (r, g, b, a)

        # 红色：red（  # FF0000）
        # 绿色：green（  # 008000）
        # 蓝色：blue（  # 0000FF）
        # 黄色：yellow（  # FFFF00）
        # 黑色：black（  # 000000）
        # 白色：white（  # FFFFFF）
        # 灰色：gray（  # 808080）
        # 粉色：pink（  # FFC0CB）
        # 紫色：purple（  # 800080）
        # 橙色：orange（  # FFA500）
        # 棕色：brown（  # A52A2A）
        # 青色：cyan（  # 00FFFF）
        # 品红：magenta（  # FF00FF）
        # 银色：silver（  # C0C0C0）
        # 金色：gold（  # FFD700）

        # color = [
        #     "red", "green", "blue", "black", "gray", "pink", "purple", "orange", "brown", "cyan", "magenta", "gold",
        #     "#005588",
        # ]

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
        return random.choice(color)

    def getTextSize(self, text, size: float = 16):

        # 创建一个临时图像用于测量
        img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(img)

        # import matplotlib.font_manager as fm
        # font_path = fm.findfont(fm.FontProperties())  # 获取默认字体路径
        # print(f"查看字体文件：{font_path}")

        try:
            font = ImageFont.truetype(self.fontFamily, size=self.fontSize, encoding="utf-8")
        except IOError:
            # raise FileNotFoundError(f"字体文件不存在：{font_path}，请替换为系统中实际存在的字体路径")
            if self.fontSize > 0:
                font = ImageFont.load_default(size)
            else:
                font = ImageFont.load_default()
                # print()

        # 计算文本尺寸
        # 使用 textbbox 获取边界框（参数为文本左上角坐标）
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font,
                                                 # spacing=0,
                                                 align="left")

        # 计算宽度和高度
        width = right - left
        height = bottom - top
        # print(f"文本：{text} 宽度：{width}px，高度：{height}px 字体：{font.getname()} ")
        return width, height

    # def calculate_text_width(self, text, font_family="Arial", font_size=16):
    #     """用cairo计算文本宽度（像素）"""
    #     # 创建虚拟SVG表面用于测量
    #     surface = cairo.SVGSurface(None, 0, 0)
    #     ctx = cairo.Context(surface)
    #     # 设置字体样式
    #     ctx.select_font_face(self.fontFamily)
    #     ctx.set_font_size(self.fontSize)
    #     # 获取文本边界信息
    #     # _, _, width, _, _, _ = ctx.text_extents(text)
    #     x_bearing, y_bearing, width, height, x_advance, y_advance = ctx.text_extents(text)
    #
    #     print(f"文本：{text} 宽度：{width}px，高度：px")
    #     return width

    def data(self, jsonObject: dict):
        self.jsonObject = jsonObject

    def markdown(self, text: str):
        markdown = Markdown(text)
        self.jsonObject = markdown.mindmap()

    def rander(self):

        width, height = self.getTextSize(self.jsonObject['text'])
        self.width = width
        self.height = self.charHeight * 3

        self.scan(self.jsonObject['children'])

        self.dwg = svgwrite.Drawing(self.filepath, size=(self.width, self.height), profile='tiny'
                                    # , viewBox=f"0 -{height // 2} {width} {height // 2}",
                                    # preserveAspectRatio="xMidYMid slice"
                                    )

        # self.background(self.jsonObject['children'], True)

        self.title(self.jsonObject['title'])

        self.horizontalPosition = 0
        self.verticalPosition = self.charHeight * 2

        self.horizontalPosition = width + self.fontSize  # + self.distance

        self.arrange(self.jsonObject['children'])
        self.root(self.jsonObject['text'])

        # self.getTextSize("中国")
        self.dwg.save(pretty=True)

    def save(self, filepath: str = 'example.svg'):
        if not self.jsonObject:
            raise Exception("No data found.")
        self.filepath = filepath
        self.rander()
        # self.dwg.save(pretty=True)

    # def exportPng(self, filepath="example.png"):
    #     self.save(os.path.splitext(filepath)[0])
    #
    #     with open(filepath, "rb") as svg_file:
    #         svg_data = svg_file.read()
    #         # 转换并保存为PNG
    #         svg2png(bytestring=svg_data, write_to=filepath, dpi=300)  # dpi控制清晰度
    #     pass

    def fontList(self):
        import matplotlib.font_manager as fm

        # 获取所有系统字体
        font_list = fm.findSystemFonts()
        print("\n".join(font_list))

    def background(self, childNode: list, bg: bool = False):

        if bg:
            self.dwg.add(self.dwg.rect(insert=(0, 0), size=(self.width, self.height), fill='#EEEEEE'))
            circle = self.dwg.circle(center=(0, 0), r=5, fill="white", stroke="green", stroke_width="2")
            self.dwg.add(circle)

        self.horizontalPosition += self.distance
        x = self.horizontalPosition

        self.dwg.add(self.dwg.line(start=(x, 0), end=(x, self.height),
                                   stroke='grey', stroke_width=1, stroke_dasharray='2,8'
                                   ))

        # textWidth = 0
        # for child in childNode:
        #     width, height = self.getTextSize(child['text'])
        #     if width > textWidth:
        #         textWidth = width
        #
        # x1 = self.horizontalPosition + textWidth
        # self.dwg.add(self.dwg.line(start=(x1, 0), end=(x1, self.height),
        #                            stroke='black', stroke_width=1, stroke_dasharray='10,2'
        #                            ))

        for child in childNode:
            # print(child['text'])
            if 'children' in child and len(child['children']) > 0:
                # self.horizontalPosition += columnWidth
                self.background(child['children'])

            self.verticalPosition += self.charHeight
            y = self.verticalPosition
            self.dwg.add(self.dwg.line(start=(0, y), end=(self.width, y),
                                       stroke='grey', stroke_width=1, stroke_dasharray='2,8'
                                       ))

    def __xmindAddSubTopic(self, node, datas):

        for data in datas:
            sub = node.addSubTopic()
            sub.setTitle(data['text'])
            if 'children' in data:
                self.__xmindAddSubTopic(sub, data['children'])

    def __xmindSheet(self, template, filepath):
        workbook = xmind.load(template)
        sheet = workbook.getPrimarySheet()

        sheet.setTitle(self.jsonObject['title'])
        root = sheet.getRootTopic()
        root.setTitle(self.jsonObject['text'])

        # self.jsonObject['children']
        self.__xmindAddSubTopic(root, self.jsonObject['children']);

        # xmind.save(workbook, path="D:/my_map.xmind")
        xmind.save(workbook, path=filepath)

    def xmind(self, template, filepath):
        self.__xmindSheet(template, filepath)

    def debug(self):

        # rect1 = self.dwg.rect(insert=(50, 70), size=(100, 80), rx=15, ry=15,
        #                       fill='lightblue', stroke='blue', stroke_width=2)
        # self.dwg.add(rect1)
        # self.dwg.add(self.dwg.text(text, insert=(100, 120), text_anchor='middle'))
        # self.debug = True

        self.rander()

        # self.data(mindmapData)
        # self.data(jsonData)
        # self.markdown(data)
        # self.rectangle("咖啡营销会议")
        # self.ellipse("咖啡营销会议")
        # print(mindmapData)

    def main(self):

        self.parser = argparse.ArgumentParser(description='Markdown To Mindmap')
        self.parser.add_argument("-m", '--markdown', type=str, default=None, metavar='/path/to/yout.md',
                                 help='Markfown file')
        self.parser.add_argument("-s", '--stdin', action="store_true", default=False,
                                 help='Standard input from the terminal')

        self.parser.add_argument('-o', '--output', default=None, type=str, metavar='example.svg', help='output picture')
        self.parser.add_argument('-x', '--xmind', default=None, type=str, metavar='example.xmind', help='output xmind')
        self.parser.add_argument('-t', '--template', default="/path/to/your/template.xmind", type=str,
                                 metavar='/path/to/your/template.xmind',
                                 help='xmind template')

        args = self.parser.parse_args()
        # print(args)
        if args.markdown and args.output:
            with open(args.markdown) as file:
                text = file.read()
                self.markdown(text)
                self.save(args.output)
        elif args.stdin and args.output:
            self.markdown(sys.stdin.read())
            self.save(args.output)

        elif args.stdin and args.xmind:
            self.markdown(sys.stdin.read())
            self.xmind(args.template, args.xmind)
        else:
            self.parser.print_help()


def main():
    try:
        mindmap = Mindmap()
        # mindmap.font("DejaVu")
        # mindmap.author("作者：陈景峰")
        # mindmap.description("©️版权所有")
        mindmap.main()
    except KeyboardInterrupt as e:
        print(e)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
