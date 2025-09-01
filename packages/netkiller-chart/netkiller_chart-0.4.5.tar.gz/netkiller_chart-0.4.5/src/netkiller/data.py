#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
##############################################
# Home	: https://www.netkiller.cn
# Author: Neo <netkiller@msn.com>
# Data: 2025-09-01
##############################################
import csv
import io


class Data:
    data = {}

    def __init__(self) -> None:
        self.data = {}
        pass

    def str2bool(self, string: str):
        if not string.strip():
            raise ValueError("空字符串无法转换为布尔值")
        lower_s = string.strip().lower()

        if lower_s in ('true', '1', 'yes', 'y'):
            return True
        elif lower_s in ('false', '0', 'no', 'n'):
            return False
        else:
            raise ValueError(f"无法将字符串 '{lower_s}' 转换为布尔值")

    def add(self, id: int, name: str, start: str, finish: str, resource: str, progress: int, predecessor: int,
            milestone: bool,
            parent: int):

        if not resource:
            resource = ""
        if not parent:
            parent = 0
        if not milestone:
            milestone = False
        if not predecessor:
            predecessor = 0
        item = {"id": id, "name": name, "start": start, "finish": finish, "resource": resource, "progress": progress,
                "predecessor": predecessor, "milestone": milestone}

        if parent != "" and int(parent) > 0:
            # print(parent)
            if not "subitem" in self.data[parent]:
                self.data[parent]["subitem"] = {}
            self.data[parent]["subitem"][id] = item

        else:
            self.data[id] = item

    def addFromMySQL(self, row):
        # if row['milestone'] == 'TRUE':
        #     row['milestone'] = True
        # else:
        #     row['milestone'] = False

        id = row["id"]
        parent = row["parent"]
        row["start"] = row["start"].strftime("%Y-%m-%d")
        row["finish"] = row["finish"].strftime("%Y-%m-%d")
        if not row["resource"]:
            row["resource"] = ""
        # print(type(parent))
        if parent and parent > 0:
            if not "subitem" in self.data[parent]:
                self.data[parent]["subitem"] = {}
            self.data[parent]["subitem"][id] = row

        else:
            self.data[id] = row

    def addDict(self, item):
        pass

    def csvfile(self, filepath):
        self.data = {}
        with open(filepath) as csvfile:
            dictReader = csv.DictReader(csvfile)

            items = []
            ids = []
            for item in dictReader:
                items.append(item)
                ids.append(int(item["id"]))
            for item in items:

                if item["milestone"].lower() == "true":
                    item["milestone"] = True
                else:
                    item["milestone"] = False

                if int(item["parent"]) not in ids:
                    item["parent"] = 0

                self.add(int(item["id"]), item["name"], item["start"], item["finish"], item["resource"],
                         int(item['progress']),
                         int(item["predecessor"]), bool(item["milestone"]), int(item["parent"]))
        return self.data

    def csvtext(self, text):
        self.data = {}
        with io.StringIO(text) as buffer:
            dictReader = csv.DictReader(buffer)
            items = []
            ids = []
            for item in dictReader:
                items.append(item)
                ids.append(int(item["id"]))
            # print(ids)
            for item in items:
                # print(item)
                if item["milestone"].lower() == "true":
                    item["milestone"] = True
                else:
                    item["milestone"] = False
                if int(item["parent"]) not in ids:
                    item["parent"] = 0

                self.add(int(item["id"]), item["name"], item["start"], item["finish"], item["resource"],
                         int(item['progress']),
                         int(item["predecessor"]), bool(item["milestone"]), int(item["parent"]))
        return self.data
