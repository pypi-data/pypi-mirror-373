#! /usr/scripts/env python3
# -*- coding: UTF-8 -*-
##############################################
# Home	: http://netkiller.github.io
# Author: Neo <netkiller@msn.com>
# Data: 2025-08-29
##############################################
try:
    import re
    import json
    from netkiller import Data
except ImportError as err:
    print("Error: %s" % (err))
    exit()


class Markdown:
    def __init__(self, markdown: str = None):
        self.markdown = markdown
        pass

    def mindmap(self):
        """
        解析Markdown列表为嵌套字典结构，确保同级节点正确识别
        修复AlmaLinux的层级问题
        """
        # 按行分割文本，保留原始缩进信息（不strip()）
        lines = [line for line in self.markdown.split('\n') if line.strip()]

        # 提取根标题（以#开头的行）
        title = ""
        if lines and lines[0].startswith('#'):
            title = lines[0].lstrip('#').strip()
            lines = lines[1:]  # 移除根标题行

        # 解析每一行的缩进级别和内容
        parsed_lines = []
        for line in lines:
            # 匹配列表项（-/*/+ 开头），精确捕获缩进
            match = re.match(r'^(\s*)([-*+])\s+(.*)$', line)
            if match:
                indent = len(match.group(1))  # 原始缩进空格数
                content = match.group(3).strip()

                # 计算缩进级别（2个空格为一级）
                level = max(0, indent // 2)
                parsed_lines.append((level, content))

        # 递归构建嵌套结构
        def build_hierarchy(lines, start_idx, parent_level):
            nodes = []
            i = start_idx

            while i < len(lines):
                current_level, current_content = lines[i]

                # 如果当前级别小于等于父级别，说明不属于当前父节点的子节点
                if current_level <= parent_level:
                    return i, nodes  # 返回当前索引和已构建的节点列表

                # 创建当前节点
                node = {"text": current_content, "children": []}

                # 递归处理子节点（下一行开始，父级别为当前级别）
                next_i, children = build_hierarchy(lines, i + 1, current_level)
                node["children"] = children
                nodes.append(node)

                # 移动到下一个待处理节点
                i = next_i

            return i, nodes

        # 从第0行开始构建，根节点的父级别为-1
        _, children = build_hierarchy(parsed_lines, 0, -1)

        # 构建根节点
        root = children.pop()
        # print(title)
        root["title"] = title

        return root

    def table2csv(self):
        """从 Markdown 文本中提取第一个表格并转为 DataFrame"""
        # 按行分割文本
        lines = [line.strip() for line in self.markdown.split('\n') if line.strip()]

        # 查找表格的起始和结束位置（寻找包含 | 的行）
        table = []
        is_table = False
        for line in lines:
            if '|' in line and '|-' not in line and '| :-' not in line:
                table.append(line.replace('|', ',').strip(','))  # 替换 | 为逗号

        if not table:
            return None  # 未找到表格

        csv_text = '\n'.join(table)
        # print(table)
        return csv_text

    def table2list(self):
        """从 Markdown 文本中提取第一个表格并转为 DataFrame"""
        # 按行分割文本
        lines = [line.strip() for line in self.markdown.split('\n') if line.strip()]

        # 查找表格的起始和结束位置（寻找包含 | 的行）
        table = []
        is_table = False
        for line in lines:
            # if '|' in line:
            #     is_table = True
            # if '|-' in line:
            #     is_table = True
            #     continue
            if '|' in line and '|-' not in line and '| :-' not in line:
                table.append(line.strip('|').split('|'))  # 替换 | 为逗号
            # elif in_table:
            #     break  # 表格结束

        if not table:
            return None  # 未找到表格
        return table

    def table2dict(self):
        """从 Markdown 文本中提取第一个表格并转为 DataFrame"""
        # 按行分割文本
        lines = [line.strip() for line in self.markdown.split('\n') if line.strip()]

        # 查找表格的起始和结束位置（寻找包含 | 的行）
        table = []
        header = []
        for line in lines:
            if '|' in line and not header:
                header = line.strip('|').split('|')
                header = [item.strip() for item in header]
                continue
            # if '|-' in line:
            #     continue
            if '|' in line and '|-' not in line and '| :-' not in line:
                body = line.strip('|').split('|')
                body = [item.strip() for item in body]
                table.append(dict(zip(header, body)))  # 替换 | 为逗号

        if not table:
            return None  # 未找到表格
        return table

    def title(self):
        lines = [line.strip() for line in self.markdown.split('\n') if line.strip()]
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return None

        # def dumps(self):

    #
    def gantt(self):
        items = self.table2dict()

        tmp = Data()
        no = 1
        for item in items:
            # print(item)
            try:
                tmp.add(int(item["id"]), item["name"], item["start"], item["finish"], item["resource"],
                        int(item["progress"]),
                        int(item["predecessor"]), tmp.str2bool(item["milestone"]), int(item["parent"]))
            except KeyError as err:
                print(
                    "Error: The key %s does not exist. The full details are as follows: | id | name | start | finish | resource | progress | predecessor | milestone | parent | " % (
                        err))
                exit()
            no += 1
        data = tmp.data

        # json_output = json.dumps(data, ensure_ascii=False, indent=2)
        # print(json_output)
        return data

    def fishbone(self):

        # 解析Markdown文本
        lines = [line.rstrip() for line in self.markdown.rstrip().split('\n') if line.rstrip()]
        # print(lines)

        parent = None
        jsonData = {}

        for line in lines:
            # 匹配一级目标（无缩进）
            if line.startswith('- ') and not line.startswith('  - '):
                # print(line)
                parent = line[2:].strip()
                jsonData[parent] = []
            # 匹配二级目标（有缩进）
            elif line.startswith('  - '):
                value = line[4:].strip()
                jsonData[parent].append(value)
        # print(jsonData)
        return jsonData

    def debug(self):
        markdown = """
        # 石川鱼骨图
        - 产品目标
          - 竞品分析
        - 开发目标
          - 编码开发
          - 代码测试
        - 运营目标
          - 区域投放
            """
        self.markdown = markdown
        jsonString = self.fishbone()
        # 打印结果
        print(json.dumps(jsonString, ensure_ascii=False, indent=2))
        pass

    def main(self):
        # 示例 Markdown 文本
        #         self.markdown = """# 测试标题
        # - 一级标题
        #   - 内容段落1
        #   - 内容段落2
        #   - 列表项1
        #   - 列表项2
        #     - 子列表项1
        #       - 孙列表项1
        #   - 三级标题
        #     - 更多内容 1
        #     - AAA
        #     - AAA
        #     - 更多内容 1
        #   - 另一个二级标题
        #     - 列表A
        #     - 子列表A1
        #     - 列表B
        #       - 子列表B1
        #         - 孙列表B1-1
        #       - 子列表B2
        # """

        # 解析并转换为 JSON
        # result = self.parser(markdown_text)
        # json_output = json.dumps(result, ensure_ascii=False, indent=2)
        # self.debug()
        # 打印 JSON 输出

        # df = markdown2csv(md_text)
        # print(df)
        # print('-' * 50)
        # t = self.table2dict()
        # print(t)
        # print(self.dumps())
        self.debug()


if __name__ == "__main__":
    markdown = Markdown()
    markdown.main()
