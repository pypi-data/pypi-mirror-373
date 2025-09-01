#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
##############################################
# Home	: http://netkiller.github.io
# Author: Neo <netkiller@msn.com>
# Data: 2025-08-06
##############################################


import csv
import json
import os
import sys
from datetime import datetime
from optparse import OptionParser

module = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(module)
sys.path.insert(0, ".")
sys.path.insert(1, module)

import drawsvg as draw

from netkiller.data import Data
from netkiller.gantt import Gantt, Calendar


class Workload(Calendar):
    def __init__(self, data: dict = None) -> None:
        super().__init__()
        self.data = {}
        self.minDate = []
        self.maxDate = []
        self.resourceTextSize = 0
        self.workweeks = 5
        self.firstsd = None
        self.canvasTop = 0
        self.splitLine = 1
        self.fontSize = 16
        self.__department = None
        if data:
            self.data = data

    def gantt2workload(self, data):
        # self.data = dict()
        for key, item in data.items():
            if "subitem" in item:
                self.__gantt2workload(item["subitem"])

            if not "resource" in item:
                continue
            elif not item["resource"]:
                item["resource"] = "null"

            start = datetime.strptime(item["start"], "%Y-%m-%d").date()
            finish = datetime.strptime(item["finish"], "%Y-%m-%d").date()

            self.minDate.append(start)
            self.maxDate.append(finish)

            length = self.getTextSize(item["resource"])
            # print(self.resourceTextSize,length)
            if self.resourceTextSize < length:
                self.resourceTextSize = length

            if item["resource"] in self.data.keys():
                # if data.has_key(item['resource']):

                # if not 'start' in self.data[item['resource']]:
                # self.data[item['resource']]['start']=''
                # if datetime.strptime(self.data[item['resource']]['start'], '%Y-%m-%d').date() > start:
                #     self.data[item['resource']]['start'] = item['start']
                # if datetime.strptime(self.data[item['resource']]['finish'], '%Y-%m-%d').date() < finish:
                #     self.data[item['resource']]['finish'] = item['finish']

                # print(self.data)

                if self.data[item["resource"]]["start"] > start:
                    self.data[item["resource"]]["start"] = start
                if self.data[item["resource"]]["finish"] < finish:
                    self.data[item["resource"]]["finish"] = finish
            else:
                self.data[item["resource"]] = {"resource": item["resource"], "start": start, "finish": finish}
        return self.data

    def csv2workload(self, file):
        dictReader = csv.DictReader(file)
        for item in dictReader:

            if not item["resource"]:
                # item["resource"] = "未知员工"
                continue
            # print(item["start"])
            start = datetime.strptime(item["start"], "%Y-%m-%d").date()
            finish = datetime.strptime(item["finish"], "%Y-%m-%d").date()

            self.minDate.append(start)
            self.maxDate.append(finish)

            length = self.getTextSize(item["resource"]) + 20
            # print(self.resourceTextSize,length)
            if self.resourceTextSize < length:
                self.resourceTextSize = length

            if item["resource"] in self.data.keys():
                if self.data[item["resource"]]["start"] > start:
                    self.data[item["resource"]]["start"] = start
                if self.data[item["resource"]]["finish"] < finish:
                    self.data[item["resource"]]["finish"] = finish
                self.data[item["resource"]]["task"].append((start, finish, item["name"]))
            else:
                self.data[item["resource"]] = {"resource": item["resource"], "start": start, "finish": finish,
                                               "task": [(start, finish, item["name"])]}

        return self.data

    def workload(self):

        if not self.data:
            raise ValueError("数据出错")

        self.startPosition = self.resourceTextSize + 300
        left = self.startPosition

        self.beginDate = min(self.minDate)
        self.endDate = max(self.maxDate)

        lineNumber = len(self.data)

        if self.__title:
            self.canvasTop = 50

        days = self.endDate - self.beginDate
        self.canvasWidth = self.startPosition + self.columeWidth * days.days + days.days + self.columeWidth + 2
        self.canvasHeight = self.canvasTop + self.rowHeight * 3 + self.rowHeight * lineNumber + (
                lineNumber - 1) * self.splitLine
        self.width = self.canvasWidth + 1
        self.height = self.canvasHeight + 1
        # print(self.canvasTop, self.canvasHeight)

        self.draw = draw.Drawing(self.width, self.height)

        style = """<style><![CDATA[
        /* 全局默认字体设置 */
        * {
          font-family: 'PingFang SC', 'Microsoft YaHei', 'SimHei', 'Arial', sans-serif, 'SourceHanSansSC-Normal';
          /* font-size: 16px;*/
        }
        ]]></style>
                        """

        self.draw.append(draw.Raw(style))

        if self.__title:
            self.draw.append(draw.Text(self.__title, 30, self.canvasWidth / 2, 25, center=True, text_anchor="middle",
                                       font_family=self.fontFamily))

        if self.__department:
            self.draw.append(
                draw.Text(self.__department, 30, 10, self.canvasTop + self.rowHeight + 10, fill="#555555"))

        top = self.canvasTop + self.rowHeight * 2
        chart = draw.Group(id="workload")

        table = draw.Group(id="table")
        table.append_title("表格")
        # 封顶
        table.append(draw.Line(1, self.canvasTop, self.canvasWidth, self.canvasTop, stroke="black"))
        table.append(draw.Text("资源", 20, 10, top + 20, fill="#555555"))
        table.append(draw.Line(self.resourceTextSize, top, self.resourceTextSize, self.canvasHeight, stroke="grey"))
        table.append(draw.Text("开始日期", 20, self.resourceTextSize + 10, top + 20, fill="#555555"))
        table.append(
            draw.Line(self.resourceTextSize + 115, top, self.resourceTextSize + 115, self.canvasHeight, stroke="grey"))
        table.append(draw.Text("截止日期", 20, self.resourceTextSize + 120 + 5, top + 20, fill="#555555"))
        table.append(
            draw.Line(self.resourceTextSize + 225, top, self.resourceTextSize + 225, self.canvasHeight, stroke="grey"))
        table.append(draw.Text("工时", 20, self.resourceTextSize + 235, top + 20, fill="#555555"))
        # table.append(draw.Line(self.resourceTextSize + 400, top,                               self.resourceTextSize + 400, self.canvasHeight, stroke='grey'))

        chart.append(table)

        # for key, value in self.__month(top).items():
        #     chart.append(value)
        for key, value in super().calendarYear(self.canvasTop).items():
            chart.append(value)

        # print(self.dayPosition)

        # for key, value in self.__weekday(top).items():
        #     background.append(value)
        # 月线
        chart.append(draw.Line(self.startPosition, self.canvasTop + self.rowHeight, self.canvasWidth,
                               self.canvasTop + self.rowHeight, stroke="grey"))
        # 周线
        chart.append(
            draw.Line(1, self.canvasTop + self.rowHeight * 2, self.canvasWidth, self.canvasTop + self.rowHeight * 2,
                      stroke="grey"))

        chart.append(
            draw.Line(1, self.canvasTop + self.rowHeight * 3, self.canvasWidth, self.canvasTop + self.rowHeight * 3,
                      stroke="grey"))
        # 竖线
        chart.append(draw.Line(left, self.canvasTop, left, self.canvasHeight, stroke="grey"))

        # begin = datetime.strptime(line['begin'], '%Y-%m-%d').day
        # # end = datetime.strptime(line['end'], '%Y-%m-%d').day
        #

        # left += self.columeWidth * (begin - 1) + (1 * begin)
        # # 日宽度 + 竖线宽度
        self.canvasTop += self.rowHeight * 3
        for resource, row in self.data.items():
            # # 工时
            top = self.canvasTop + self.itemLine * self.rowHeight + self.splitLine * self.itemLine
            # print(resource, row, top)
            # end = (datetime.strptime(row['finish'], '%Y-%m-%d').date() -
            #        datetime.strptime(row['start'], '%Y-%m-%d').date()).days
            end = (row["finish"] - row["start"]).days
            # end = (row['finish'] - row['start']).days
            right = self.columeWidth * (end + 1) + (1 * end)

            group = draw.Group(id=resource)

            group.append(draw.Text(resource, self.fontSize, 10, top + 20, text_anchor="start"))
            group.append(
                draw.Text(row["start"].strftime("%Y-%m-%d"), self.fontSize, self.resourceTextSize + 10, top + 20,
                          text_anchor="start"))
            group.append(
                draw.Text(row["finish"].strftime("%Y-%m-%d"), self.fontSize, self.resourceTextSize + 125, top + 20,
                          text_anchor="start"))

            group.append(
                draw.Text(str(end + 1), self.fontSize, self.resourceTextSize + 235, top + 20, text_anchor="start"))

            # left = self.dayPosition[row["start"].strftime("%Y-%m-%d")]
            # r = draw.Rectangle(left, top + 4, right, self.barHeight, fill="blue")
            # r.append_title(resource)
            # chart.append(r)

            for start, finish, name in row['task']:
                left = self.dayPosition[start.strftime("%Y-%m-%d")]
                end = (finish - start).days
                # end = (row['finish'] - row['start']).days
                right = self.columeWidth * (end + 1) + (1 * end)

                r = draw.Rectangle(left, top + 4, right, self.barHeight, fill="blue")
                r.append_title(name)
                group.append(r)
            chart.append(group)
            chart.append(draw.Line(1, top + self.rowHeight, self.canvasWidth, top + self.rowHeight, stroke="grey"))

            self.itemLine += 1

        self.draw.append(chart)
        self.draw.append(draw.Rectangle(1, 1, self.canvasWidth,
                                        self.canvasHeight, fill='none', stroke='black'))

        # self.legend()

    def title(self, title):
        self.__title = title

    def department(self, text):
        self.__department = text

    def save(self, filename: str):
        self.workload()
        self.draw.save_svg(filename)

    def main(self):

        self.parser = OptionParser("usage: %prog [options] ")

        self.parser.add_option("", "--stdin", action="store_true", dest="stdin",
                               help="cat gantt.json | gantt -s file.svg")
        self.parser.add_option("-c", "--csv", dest="csv", help="/path/to/workload.csv", default=None,
                               metavar="/path/to/workload.csv")
        self.parser.add_option("-j", "--json", dest="json", help="load data from file.", default=None,
                               metavar="/path/to/gantt.json")

        # group = OptionGroup(self.parser, "loading data from mysql")
        # group.add_option("-H", "--host", dest="host", help="", default=None, metavar="localhost")
        # group.add_option("-u", "--username", dest="username", help="", default=None, metavar="root")
        # group.add_option("-p", "--password", dest="password", help="", default=None, metavar="")
        # group.add_option("-D", "--database", dest="database", help="", default=None, metavar="test")
        # self.parser.add_option_group(group)

        # group = OptionGroup(self.parser, "Workload")
        self.parser.add_option("-t", "--title", dest="title", help="标题", default="Netkiller Python 手札",
                               metavar="项目标题")
        self.parser.add_option("-d", "--department", dest="department", help="项目名称", default="技术部",
                               metavar="技术部")
        self.parser.add_option("-W", "--workweeks", dest="workweeks", help="workweeks default 5", default=5,
                               metavar="5")
        self.parser.add_option("-o", "--odd-even", action="store_true", dest="oddeven", default=False,
                               help="odd-even weeks")
        # group.add_option("-g", "--gantt", action="store_true", dest="gantt", default=True, help="Gantt chart")
        # group.add_option("-w", "--workload", action="store_true", dest="workload", help="Workload chart")
        self.parser.add_option("-s", "--save", dest="save", help="save file", default=None,
                               metavar="/path/to/workload.svg")
        # self.parser.add_option_group(group)
        self.parser.add_option("--debug", action="store_true", dest="debug", help="debug mode")

        (options, args) = self.parser.parse_args()
        # self.parser.print_usage()

        if options.debug:
            print(options, args)
            print(json.dumps(self.data, ensure_ascii=False))

        if not options.save:
            self.parser.print_help()
            exit()

        if options.stdin:
            json.loads(sys.stdin.read())
            # self.gantt2workload(data)
        elif options.csv:
            with open(options.csv) as file:
                tmp = self.csv2workload(file)
                # print(workload.minDate)
        elif options.json:
            with open(options.json) as file:
                data = json.dumps(file.read(), ensure_ascii=False)
                self.gantt2workload(data)
        else:
            self.parser.print_help()
            exit()
        # elif options.host:
        #     config = {"host": options.host, "user": options.username, "password": options.password,
        #               "database": options.database, "raise_on_warnings": True}
        #     self.loadFromMySQL(config)

        # if options.workweeks:
        #     workweeks = options.workweeks

        # print(data)
        # workload.setWorkweeks(options.workweeks, False)
        self.title(options.title)
        self.department(options.department)
        self.save(options.save)


def main():
    try:
        workload = Workload()
        workload.main()
    except KeyboardInterrupt as e:
        print(e)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
