#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
##############################################
# Home	: http://netkiller.github.io
# Author: Neo <netkiller@msn.com>
# Data: 2025-07-25
##############################################
import os
import sys

try:
    module = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # print(module)
    # sys.path.insert(0, ".")
    sys.path.insert(1, module)

    import calendar
    import drawsvg as draw
    from datetime import datetime, date
    from PIL import ImageFont
    import requests
    import platform
    from PIL import ImageFont, ImageDraw, Image
    from optparse import OptionParser, OptionGroup
    import json
    import logging
    import logging.handlers
    from netkiller.data import Data
    from netkiller.markdown import Markdown
except ImportError as err:
    print("Gantt Error: %s" % (err))
    exit()


class Canvas:
    draw = None
    # 画布尺寸
    canvasWidth = 0
    canvasHeight = 0

    canvasTop = 1
    canvasLeft = 1
    # SVG 实际尺寸
    width = 0
    height = 0

    splitLineHeight = 1
    rowHeight = 29

    margin = 0
    padding = 0
    # fontFamily = "Songti"
    fontFamily = "SourceHanSansSC-Normal"
    # fontFamily = "DejaVuSans"
    fontSize = 18
    lineColor = "grey"

    def __init__(self):
        pass

    def getTextSize(self, text):
        #   if platform.system() == "Linux":
        #     font = r"/usr/local/share/netkiller/Songti.ttc"
        # elif platform.system() == "Darwin":
        #     font = r"/System/Library/Fonts/Supplemental/Songti.ttc"
        # else:
        #     font = r"Songti.ttc"

        # 创建一个临时图像用于测量
        img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(img)

        # try:
        # font = ImageFont.truetype(r"Songti.ttc", size=self.fontSize, encoding="utf-8")
        font = ImageFont.truetype(self.fontFamily, size=self.fontSize, encoding="utf-8")
        # except IOError:
        #     raise FileNotFoundError(f"字体文件不存在：{font_path}，请替换为系统中实际存在的字体路径")
        # if self.fontSize > 0:
        #     font = ImageFont.load_default(self.fontSize)
        # else:
        # font = ImageFont.load_default()
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
        # return width, height
        # print(f"文本: {text} 字体: {self.fontFamily} 尺寸: {self.fontSize} 宽度：{width}")
        return width


class Calendar(Canvas):
    startPosition = 0
    itemLine = 0
    columeWidth = 30
    barHeight = 20
    progressHeight = 14

    nameTextSize = 1
    dateTextSize = 0
    resourceTextSize = 90
    textIndentSize = 40

    beginDate = datetime.now().date()
    endDate = datetime.now().date()
    weekdayPosition = 0
    dayPosition = {}
    linkPosition = {}

    lineNumber = 0
    # 隐藏表格
    isTable = False

    def __init__(self) -> None:
        super().__init__()

    def __table(self, top):
        group = draw.Group(id="table")
        group.append_title("表格")
        # 画布最左边
        # group.append(draw.Line(1, top, 1, self.canvasHeight, stroke='black'))
        left = 5

        group.append(draw.Text("任务", 20, left, top + 20 + self.rowHeight * 2, fill="#555555"))
        left += self.nameTextSize + 5
        group.append(
            draw.Line(left, top + self.rowHeight * 2, left, self.canvasHeight, stroke="grey"))
        group.append(draw.Text("开始日期", 20, left + 5, top + 20 + self.rowHeight * 2, fill="#555555"))
        left += self.dateTextSize + 20
        group.append(
            draw.Line(left, top + self.rowHeight * 2,
                      left, self.canvasHeight,
                      stroke=self.lineColor))
        left += 5
        group.append(
            draw.Text("截止日期", 20, left, top + 20 + self.rowHeight * 2,
                      fill="#555555"))
        left += self.dateTextSize + 15
        group.append(
            draw.Line(left, top + self.rowHeight * 2, left, self.canvasHeight,
                      stroke="grey"))
        left += 5
        group.append(draw.Text("工时", 20, left, top + 20 + self.rowHeight * 2, fill="#555555"))
        left += 45
        group.append(
            draw.Line(left, top + self.rowHeight * 2, left, self.canvasHeight,
                      stroke=self.lineColor))
        left += 5
        group.append(draw.Text("资源", 20, left, top + 20 + self.rowHeight * 2, fill="#555555"))

        return group

    def weekNumberOfMonth(self, currentDate):
        # firstDay = currentDate.replace(            day=1, hour=0, minute=0, second=0, microsecond=0)
        firstDay = currentDate.replace(day=1)
        number = int(currentDate.strftime("%W")) - int(firstDay.strftime("%W")) + 1
        # print(currentDate, number)
        return number

    def __weekdays(self, top, begin, end):
        offsetX = 1
        column = 0

        begin = datetime.strptime(begin, "%Y-%m-%d")
        end = datetime.strptime(end, "%Y-%m-%d")

        beginDay = begin.day
        endDay = end.day
        # print(beginDay, endDay)

        weekNumberOfYear = datetime.strptime(str(begin.year) + "-" + str(begin.month) + "-01", "%Y-%m-%d").strftime(
            "%W")
        # weekNumberOfYear = begin.strftime('%W')
        # weekNumberOfYear = datetime.date(datetime.now().year,month,1).strftime('%W')
        weekGroups = {}
        weekGroups[weekNumberOfYear] = draw.Group(id="week" + str(weekNumberOfYear))

        for day in range(beginDay, endDay + 1):
            # numberOfWeek = self.weekNumberOfMonth(datetime.strptime(str(begin.year)+'-'+str(begin.month)+'-'+str(day), '%Y-%m-%d').date())
            weekday = calendar.weekday(begin.year, begin.month, day)

            currentweekNumberOfYear = datetime.strptime(str(begin.year) + "-" + str(begin.month) + "-" + str(day),
                                                        "%Y-%m-%d").strftime("%W")
            # print(weekNumberOfYear, currentweekNumberOfYear)
            if currentweekNumberOfYear != weekNumberOfYear:
                weekNumberOfYear = currentweekNumberOfYear
                weekGroups[weekNumberOfYear] = draw.Group(id="week" + str(weekNumberOfYear))
            if self.firstsd == True:
                if (int(weekNumberOfYear) % 2) == 0:
                    self.workweeks = 6
                else:
                    self.workweeks = 5
            if weekday >= self.workweeks:
                color = "#dddddd"
            else:
                color = "#cccccc"

            x = self.weekdayPosition + self.columeWidth * (column) + offsetX
            self.dayPosition[date(year=int(begin.year), month=int(begin.month), day=int(day)).strftime("%Y-%m-%d")] = x

            if day == beginDay:
                weekGroups[weekNumberOfYear].append(
                    draw.Text(begin.strftime("%Y年%m月"), 20, x + 4, top + self.rowHeight - 10, fill="#555555"))
            # 右侧封闭
            # if day == endDay:
            #     weekGroups[weekNumberOfYear].append(
            #         draw.Line(x + self.columeWidth, top, x + self.columeWidth, self.canvasHeight, stroke="black"))

            # dayName = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
            dayName = ["一", "二", "三", "四", "五", "六", "日"]

            weekGroups[weekNumberOfYear].append(
                draw.Text(dayName[weekday], 20, x + 4, top + self.columeWidth * 2 - 10, fill="#555555"))
            if day < 10:
                numberOffsetX = 10
            else:
                numberOffsetX = 5

            # 日栏位
            # print(self.weekdayPosition)
            r = draw.Rectangle(x, top + self.rowHeight * 2, self.columeWidth,
                               self.canvasHeight - (top + self.rowHeight * 2), fill=color)
            r.append_title(str(day))
            weekGroups[weekNumberOfYear].append(r)
            # 周分割线
            if weekday == 6:
                weekGroups[weekNumberOfYear].append(
                    draw.Line(x + self.columeWidth, top + self.rowHeight, x + self.columeWidth, self.canvasHeight,
                              stroke="black"))
            # 日期
            weekGroups[weekNumberOfYear].append(
                draw.Text(str(day), 20, x + numberOffsetX, top + self.columeWidth * 3 - 10, fill="#555555"))

            # if column:
            offsetX += self.splitLineHeight
            column += 1

        self.weekdayPosition = x + self.columeWidth

        return weekGroups

    def __month(self, top, months):
        monthGroups = {}
        for begin, end in months:
            month = datetime.strptime(begin, "%Y-%m-%d").month
            monthGroups[month] = draw.Group(id="month" + str(month))
            for key, value in self.__weekdays(top, begin, end).items():
                monthGroups[month].append(value)

        return monthGroups

    def __monthRange(self, begin, end):
        years = {}
        # result = []
        while True:
            if begin.month == 12:
                next = begin.replace(year=begin.year + 1, month=1, day=1)
            else:
                next = begin.replace(month=begin.month + 1, day=1)
            if next > end:
                break

            day = calendar.monthrange(begin.year, begin.month)[1]

            # result.append((begin.strftime("%Y-%m-%d"),
            #                begin.replace(day=day).strftime("%Y-%m-%d")))
            if not begin.year in years:
                years[begin.year] = []
            years[begin.year].append((begin.strftime("%Y-%m-%d"), begin.replace(day=day).strftime("%Y-%m-%d")))
            begin = next
        # result.append((begin.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")))

        if not end.year in years:
            years[end.year] = []
        years[end.year].append((begin.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")))
        # print(years)
        return years

    def calendarYear(self, top):
        self.weekdayPosition = self.startPosition
        yearGroups = {}
        # print(self.beginDate, self.endDate)
        years = self.__monthRange(self.beginDate, self.endDate)

        # print(len(years))
        for year, month in years.items():
            # print(year, month)
            # begin = datetime.strptime(begin, "%Y-%m-%d").date()
            # end = datetime.strptime(end, "%Y-%m-%d").date()
            yearGroups[year] = draw.Group(id="year" + str(year))
            for key, value in self.__month(top, month).items():
                yearGroups[year].append(value)
        return yearGroups

    def setWorkweeks(self, workweeks=5, firstsd=False):
        # 'five-day','six-day'
        self.workweeks = workweeks
        self.firstsd = firstsd

    def calendar(self):
        left = self.startPosition
        top = self.canvasTop

        background = draw.Group(id="calendar")
        if not self.isTable:
            background.append(self.__table(top))

        for key, value in self.calendarYear(top).items():
            background.append(value)
        # for key, value in self.__month(top).items():
        #     background.append(value)
        # 月线
        background.append(draw.Line(left, top + self.rowHeight, self.canvasWidth, top + self.rowHeight, stroke="grey"))

        # top = draw.Line(0, 0, self.canvasWidth, 0, stroke='black')
        # right = draw.Line(self.canvasWidth, 0,
        #                   self.canvasWidth, self.canvasHeight, stroke='black')
        # 周线
        background.append(
            draw.Line(self.canvasLeft, top + self.rowHeight * 2, self.canvasWidth, top + self.rowHeight * 2,
                      stroke="grey"))
        # 日期线
        background.append(
            draw.Line(self.canvasLeft, top + self.rowHeight * 3, self.canvasWidth, top + self.rowHeight * 3,
                      stroke="grey"))
        # 上边封闭
        # background.append(draw.Line(1, top, self.canvasWidth, top, stroke="grey"))
        # 左边封闭
        background.append(draw.Line(left, top, left, self.canvasHeight, stroke="grey"))
        # 底部封闭
        # background.append(draw.Line(1, self.canvasHeight, self.canvasWidth, self.canvasHeight, stroke="black"))

        top = top + self.rowHeight * 3
        # 分割线
        for n in range(0, self.lineNumber):
            top = top + self.rowHeight + self.splitLineHeight
            background.append(
                draw.Lines(self.canvasLeft, top, self.canvasWidth, top,
                           stroke="grey"))

        # 日历边框
        background.append(
            draw.Rectangle(self.canvasLeft, self.canvasTop, self.canvasWidth,
                           self.canvasHeight - self.canvasTop,
                           fill="none",
                           stroke="black"))
        # print(f"calendar: {self.canvasHeight}, top:{top}")
        self.draw.append(background)


class Gantt(Calendar, Canvas):
    textIndent = 0
    isBlank = False

    def __init__(self, data: dict = None) -> None:
        super().__init__()
        # self.canvasWidth = self.width
        # self.canvasHeight = self.height
        self.workweeks = 5
        self.firstsd = None
        self.name = ""
        self.ganttTitle = None
        self.isLegend = True
        self.__department = None
        if data:
            self.data = data
        else:
            self.data = {}
        pass

    def blank(self, status):
        self.isBlank = status

    def author(self, name):
        self.name = name

    def title(self, text):
        self.ganttTitle = text

    def department(self, text):
        self.__department = text

    def __title(self):
        if self.isTable:
            return

        group = draw.Group(id="title", onclick="this.style.stroke = 'green'; ")
        group.append(draw.Text(self.ganttTitle, 30, self.canvasWidth / 2, 25, center=True, text_anchor="middle",
                               font_family=self.fontFamily))
        if self.name:
            group.append(draw.Text(self.name, 16, 5, self.height - self.rowHeight / 2))
        self.draw.append(group)

    def legend(self, enable: bool):
        self.isLegend = enable

    def __legend(self):
        if not self.isLegend:
            return
        if self.isTable:
            return
        top = 10
        self.draw.append(
            draw.Text("https://www.netkiller.cn - design by netkiller", 12, self.canvasWidth - 250,
                      self.height - self.rowHeight / 2,
                      text_anchor="start", fill="grey"))

        # fill='#eeeeee'
        license = "/var/tmp/by-nc-sa.png"
        if not os.path.exists(license):
            # url = 'https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-nc-sa.png'
            url = "https://www.netkiller.cn/graphics/by-nc-sa.png"
            # license = wget.download(url, out=license)
            request = requests.get(url)
            if request.status_code == 200:
                file = open(license, "wb")
                file.write(request.content)
                file.flush()
                file.close()

        self.draw.append(draw.Image(8, 8, 100, 34.99, license, embed=True))

    def table(self, status: bool = False):
        self.isTable = status

    def items(self, line, subitem=False):
        top = self.canvasTop + self.rowHeight * 3 + self.itemLine * self.rowHeight + self.splitLineHeight * self.itemLine

        begin = datetime.strptime(line["start"], "%Y-%m-%d").day
        # end = datetime.strptime(line['end'], '%Y-%m-%d').day
        end = (datetime.strptime(line["finish"], "%Y-%m-%d").date() - datetime.strptime(line["start"],
                                                                                        "%Y-%m-%d").date()).days
        # left += self.columeWidth * (begin - 1) + (1 * begin)
        # # 日宽度 + 竖线宽度
        right = self.columeWidth * (end + 1) + (1 * end)

        left = self.dayPosition[line["start"]]
        # right = self.dayPosition[line['end']]

        self.linkPosition[line["id"]] = {"x": left, "y": top, "width": right}

        lineGroup = draw.Group(id="task")
        if not self.isTable:
            table = draw.Group(id="text")

            table.append(draw.Text(line["name"], self.fontSize, 10 + (self.textIndent * self.textIndentSize), top + 20,
                                   text_anchor="start"))
            # text.append(draw.TSpan(line['begin'], text_anchor='start'))
            # text.append(draw.TSpan(line['end'], text_anchor='start'))

            table.append(draw.Text(line["start"], self.fontSize, self.nameTextSize + 15, top + 20, text_anchor="start"))
            table.append(
                draw.Text(line["finish"], self.fontSize, self.nameTextSize + self.dateTextSize + 35, top + 20,
                          text_anchor="start"))
            # if 'progress' in line:
            #     table.append(draw.Text(
            #         str(line['progress']), 20, self.nameTextSize + 200, top + 20, text_anchor='start'))
            leftOffset = 0
            if end + 1 < 10:
                leftOffset = 10
            elif end + 1 < 100:
                leftOffset = 5
            table.append(
                draw.Text(str(end + 1), self.fontSize, self.nameTextSize + self.dateTextSize * 2 + 60 + leftOffset,
                          top + 20,
                          text_anchor="start"))
            if "resource" in line:
                table.append(
                    draw.Text(str(line["resource"]), self.fontSize, self.nameTextSize + self.dateTextSize * 2 + 105,
                              top + 20,
                              text_anchor="start"))
            lineGroup.append(table)

        group = draw.Group(id="item")
        # fill='none', stroke='black'

        if subitem:
            # print(begin,end)
            # print(left,top,right)
            offsetY = 7
            length = left + right
            group.append(
                draw.Lines(
                    # 坐标
                    left,
                    top + offsetY,
                    # 横线
                    length,
                    top + offsetY,
                    # 竖线
                    length,
                    top + 24,
                    # 斜线
                    length - 10,
                    top + 15,
                    # 横线2
                    left + 10,
                    top + 15,
                    # # 斜线
                    left,
                    top + 24,
                    # # 闭合竖线
                    left,
                    top + offsetY,
                    fill="#333333",
                    stroke="none",
                )
            )
        else:
            if "milestone" in line and line["milestone"]:
                mleft = left + 15
                mtop = top + 4
                p = draw.Path(fill="#333333")
                p.M(mleft, mtop).L(mleft + 11, top + 15).L(mleft, top + 26).L(mleft - 11, top + 15).L(mleft, mtop).Z()
                group.append(p)
                group.append(
                    draw.Text(datetime.strptime(line["start"], "%Y-%m-%d").strftime("%Y年%m月%d日"), 16, left + 30,
                              top + 20, text_anchor="start", fill="#333333"))
            else:
                # 工时
                r = draw.Rectangle(left, top + 5, right, self.barHeight, fill="#00C7C1", stroke="grey")
                r.append_title(line["name"])
                group.append(r)

                # 进度
                if "progress" in line and line["progress"] > 0:
                    progress = 0
                    if line["progress"] > end + 1:
                        progress = end + 1
                    else:
                        progress = line["progress"]

                    progressBar = draw.Rectangle(left + 2, top + 8, 30 * progress - 2, self.progressHeight,
                                                 fill="#B2F2EA")
                    # progressBar.append_title(str(progress))
                    group.append(progressBar)
                    group.append(
                        draw.Text("%d%%" % ((progress / (end + 1)) * 100), 10, left + 5, top + 18, text_anchor="start",
                                  fill="black", font_family=self.fontFamily))

        # 分割线
        # group.append(draw.Lines(1, top + self.rowHeight, self.canvasWidth, top + self.rowHeight, stroke="grey"))

        lineGroup.append(group)
        self.itemLine += 1
        return lineGroup

    def tasks(self, data):
        for id, line in data.items():
            try:
                if "subitem" in line:
                    item = self.items(line, True)
                    self.taskGroup.append(item)
                    self.textIndent += 1
                    self.tasks(line["subitem"])
                    self.textIndent -= 1
                else:
                    item = self.items(line)
                    self.taskGroup.append(item)
            except KeyError as err:
                print("KeyError %s: %s" % (err, line))
                exit()

    def link(self, fromTask, toTask):
        # print(fromTask, toTask)
        linkGroup = draw.Group(id="link")
        x = fromTask["x"] + fromTask["width"] + 1
        y = fromTask["y"] + 15
        arrow = draw.Marker(-0.1, -0.51, 0.9, 0.5, scale=4, orient="auto")
        arrow.append(draw.Lines(-0.1, 0.5, -0.1, -0.5, 0.9, 0, fill="black", close=True))
        path = draw.Path(stroke="black", stroke_width=2, fill="none", marker_end=arrow)
        path.M(x, y).H(toTask["x"] + 15).V(toTask["y"] - 5)
        linkGroup.append(path)
        return linkGroup

    def __predecessor(self, data):
        for id, task in data.items():
            try:
                if "subitem" in task:
                    self.__predecessor(task["subitem"])
                elif "predecessor" in task and task["predecessor"] and int(task["predecessor"]) > 0:
                    # print(self.linkPosition)
                    link = self.link(self.linkPosition[task["predecessor"]], self.linkPosition[task["id"]])
                    self.handover.append(link)
            except KeyError as err:
                print("KeyError: predecessor=%s, %s" % (err, task))

    def __initialize(self, data):
        for id, item in data.items():
            if "subitem" in item:
                self.textIndent += 1
                self.__initialize(item["subitem"])
                self.lineNumber += len(item["subitem"].keys())
                self.textIndent -= 1

            # 计算文字宽度
            length = self.getTextSize(item["name"])
            # print(f"{item["name"]} {length}")

            # 文本表格所占用的宽度
            if self.textIndent > 0:
                if self.nameTextSize < length + self.textIndentSize:
                    self.nameTextSize = length + self.textIndentSize
            else:
                if self.nameTextSize < length:
                    self.nameTextSize = length

            self.dateTextSize = self.getTextSize(" 9999-99-99 ")

            if "resource" in item and item["resource"]:
                length = self.getTextSize(item["resource"])
                if self.resourceTextSize < length:
                    self.resourceTextSize = length

            # begin = datetime.strptime(item['start'], '%Y-%m-%d').date()
            self.minDate.append(item["start"])
            # end = datetime.strptime(item['finish'], '%Y-%m-%d').date()
            self.maxDate.append(item["finish"])

    def rander(self):

        if not self.data:
            raise ValueError("数据出错")

        self.maxDate = []
        self.minDate = []

        self.lineNumber = len(self.data)

        self.__initialize(self.data)

        begin = min(sorted(self.minDate, key=lambda d: datetime.strptime(d, "%Y-%m-%d").timestamp()))
        end = max(sorted(self.maxDate, key=lambda d: datetime.strptime(d, "%Y-%m-%d").timestamp()))
        self.beginDate = datetime.strptime(begin, "%Y-%m-%d").date()
        self.endDate = datetime.strptime(end, "%Y-%m-%d").date()

        # print(self.maxDate, end)
        # print(self.beginDate, self.endDate)

        # 行首加5像素美化
        self.nameTextSize += 5

        if not self.isTable:
            self.startPosition = self.nameTextSize + self.dateTextSize * 2 + self.resourceTextSize + 80

        days = self.endDate - self.beginDate

        if self.ganttTitle:
            self.canvasTop = 50

        self.canvasWidth = self.startPosition + self.columeWidth * days.days + days.days + self.columeWidth
        self.canvasHeight = self.canvasTop + self.rowHeight * 3 + self.rowHeight * self.lineNumber + self.splitLineHeight * (
                self.lineNumber - 1)
        self.width = self.canvasWidth + 2
        self.height = self.canvasHeight + 2 + self.rowHeight

        self.draw = draw.Drawing(self.width, self.height)
        style = """<style><![CDATA[
* {
  font-family: 'PingFang SC', 'Microsoft YaHei', 'SimHei', 'Arial', sans-serif, 'SourceHanSansSC-Normal';
  /* font-size: 16px;*/
}
]]></style>
                """

        self.draw.append(draw.Raw(style))
        # print(f"rander: {self.canvasHeight}")
        self.__title()
        self.calendar()

        if not self.isBlank:
            if self.__department:
                self.draw.append(
                    draw.Text(self.__department, 30, 10, self.canvasTop + self.rowHeight + 10, fill="#555555"))

            self.taskGroup = draw.Group(id="tasks")
            self.tasks(self.data)
            self.draw.append(self.taskGroup)

            self.handover = draw.Group(id="handover")
            self.__predecessor(self.data)
            self.draw.append(self.handover)

        self.__legend()

    def save(self, filename: str):
        self.rander()
        self.draw.save_svg(filename)

    # self.draw.save_png('example.png')
    # self.draw.rasterize()

    def export(self, filename):
        self.rander()
        self.draw.save_png(filename)

    def usage(self):
        self.parser.print_help()
        print("\nHomepage: https://www.netkiller.cn\tAuthor: Neo <netkiller@msn.com>")
        print("Help: https://pypi.org/project/netkiller-gantt/")
        exit()

    def main(self):

        self.parser = OptionParser("usage: %prog [options] ")
        self.parser.add_option("", "--stdin", action="store_true", dest="stdin",
                               help="cat gantt.json | gantt -s file.svg")
        group = OptionGroup(self.parser, "loading data from file")
        group.add_option("-c", "--csv", dest="csv", help="/path/to/workload.csv", default=None,
                         metavar="/path/to/workload.csv")
        group.add_option("-j", "--json", dest="load", help="load data from file.", default=None,
                         metavar="/path/to/gantt.json")
        group.add_option("-m", "--markdown", dest="markdown", help="load data from file.", default=None,
                         metavar="/path/to/gantt.md")
        self.parser.add_option_group(group)
        # group = OptionGroup(self.parser, "loading data from mysql")
        # group.add_option("-H", "--host", dest="host", help="", default=None, metavar="localhost")
        # group.add_option("-u", "--username", dest="username", help="", default=None, metavar="root")
        # group.add_option("-p", "--password", dest="password", help="", default=None, metavar="")
        # group.add_option("-D", "--database", dest="database", help="", default=None, metavar="test")
        # self.parser.add_option_group(group)

        group = OptionGroup(self.parser, "Charts")
        group.add_option("-t", "--title", dest="title", help="甘特图标题", default="甘特图标题", metavar="项目甘特图")
        group.add_option("-n", "--name", dest="name", help="项目名称", default="Netkiller Python 手札",
                         metavar="Netkiller Python 手札")
        group.add_option("-d", "--department", dest="department", help="部门", default="研发部", metavar="研发部")
        group.add_option("-w", "--workweeks", dest="workweeks", help="workweeks default 5", default=5, metavar="5")
        group.add_option("-o", "--odd-even", action="store_true", dest="oddeven", default=False, help="odd-even weeks")
        # group.add_option("-g", "--gantt", action="store_true", dest="gantt", default=True, help="Gantt chart")
        # group.add_option("-w", "--workload", action="store_true", dest="workload", help="Workload chart")
        self.parser.add_option_group(group)
        self.parser.add_option("-s", "--save", dest="save", help="save file", default=None,
                               metavar="/path/to/gantt.svg")
        self.parser.add_option("-e", "--export", dest="save", help="export png file", default=None,
                               metavar="/path/to/gantt.png")
        self.parser.add_option("", "--debug", action="store_true", dest="debug", help="debug mode")

        (options, args) = self.parser.parse_args()
        # exit()

        if options.stdin:
            self.data = json.loads(sys.stdin.read())
        elif options.csv:
            csv = Data()
            self.data = csv.csvfile(options.csv)
        elif options.markdown:
            with open(options.markdown) as file:
                markdown = Markdown(file.read())
                # items = markdown.table2dict()
                # # print(items)
                # tmp = Data()
                # for item in items:
                #     # print(item)
                #     tmp.add(int(item["id"]), item["name"], item["start"], item["finish"], item["resource"],
                #             int(item["predecessor"]), bool(item["milestone"]), int(item["parent"]))
                # data = tmp.data
                self.data = markdown.gantt()
                # print(data)

        # elif options.host:
        #     config = {"host": options.host, "user": options.username, "password": options.password,
        #               "database": options.database, "raise_on_warnings": True}
        #     self.loadFromMySQL(config)
        if options.debug:
            print(options, args)
            print(json.dumps(self.data, ensure_ascii=False))

        if not self.data:
            self.usage()

        if options.save:
            #     file = options.save
            # else:
            #     if options.workload:
            #         file = "workload.svg"

            # if options.workweeks:
            #     workweeks = options.workweeks

            # # elif options.gantt:
            # gantt = Gantt()
            # self.gantt.hideTable()
            self.title(options.title)
            self.author(options.name)
            self.department(options.department)
            self.setWorkweeks(options.workweeks, options.oddeven)
            # self.gantt.ganttChart(options.title)
            self.save(options.save)

        elif options.export:
            self.title(options.title)
            self.author(options.name)
            self.setWorkweeks(options.workweeks, options.oddeven)
            # self.gantt.ganttChart(options.title)
            self.gantt.export(options.export)
            #         file = "gantt.svg"


def main():
    try:
        gantt = Gantt()
        gantt.main()
    except KeyboardInterrupt as e:
        print(e)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
