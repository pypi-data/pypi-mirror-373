#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
##############################################
# Home	: https://www.netkiller.cn
# Author: Neo <netkiller@msn.com>
# Data: 2025-08-18
##############################################
# https://developer.mozilla.org/en-US/docs/Web/SVG
class Svg:
    # https://developer.mozilla.org/zh-CN/docs/Web/SVG/Tutorials/SVG_from_scratch/SVG_and_CSS
    def __init__(self, width: int = 0, height: int = 0, **kwargs):
        if width:
            kwargs['width'] = width
        if height:
            kwargs['height'] = height
        self.elements = []
        self.__defs = []
        self.__style = None
        self.__script = None
        self.attribute = []
        for key, value in kwargs.items():
            self.attribute.append(f'{key}="{value}"')

    def __attribute(self, kwargs) -> str:
        attrs = []
        for key, value in kwargs.items():
            if key in ['klass', 'clazz']:
                key = 'class'
            attrs.append(f'{key}="{value}"')
        return " ".join(attrs)

    def link(self, href):
        self.elements.append(f'<link rel="stylesheet" href="{href}" type="text/css" />')

    def title(self, text: str):
        self.elements.append(f"<title>{text}</title>")

    def desc(self, text: str):
        self.elements.append(f"<desc>{text}</desc>")

    def defs(self, *elements):
        for element in elements:
            self.__defs.append(element.__str__())

    def style(self, text):
        self.__style = text

    def script(self, text):
        self.__script = text

    def symbol(self, id: str, element):
        self.elements.append(f'<symbol id="{id}">\n\t{element.__str__()}\n</symbol>')

    def use(self, id: str, **kwargs):
        self.elements.append(f'<use xlink:href="#{id}" {self.__attribute(kwargs)}/>')

    def group(self, element, **kwargs):
        self.elements.append(f'<g {self.__attribute(kwargs)}>{element.__str__()}</g>')

    def comment(self, text: str):
        self.elements.append(f'<!-- {text} -->')

    def append(self, text):
        if type(text) == str:
            self.elements.append(text)
        else:
            self.elements.append(text.__str__())

    def render(self):
        svg = []
        # self.elements.insert(0,
        #                      f'<svg {" ".join(self.attribute)} xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">')
        # if self.__defs:
        #     self.elements.insert(1, f'<defs>\n{"\n".join(self.__defs)}\n</defs>')
        # if self.__style:
        #     self.elements.insert(1, f'<style type="text/css"><![CDATA[\n{self.__style}\n]]></style>')
        # if self.__script:
        #     self.elements.append(f'<script>\n// <![CDATA[\n{self.__script}\n// ]]>\n</script>')
        # self.elements.append("</svg>")
        # return "\n".join(self.elements)

        svg.append(f'<svg {" ".join(self.attribute)} xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">')
        if self.__defs:
            svg.append(f'<defs>\n\t{"\n\t".join(self.__defs)}\n</defs>')
        if self.__style:
            svg.append(f'<style type="text/css"><![CDATA[\n{self.__style}\n]]></style>')
        if self.__script:
            svg.append(f'<script>\n// <![CDATA[\n{self.__script}\n// ]]>\n</script>')
        svg.extend(self.elements)
        svg.append("</svg>")

        return "\n".join(svg)

    def __str__(self):
        return self.render()

    def show(self):
        return self.render()

    def debug(self):
        print(self.render())

    def save(self, filename):
        with open(filename, 'w') as file:
            file.write(self.render())
