#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
##############################################
# Home	: https://www.netkiller.cn
# Author: Neo <netkiller@msn.com>
# Data: 2025-08-18
##############################################
from . import attribute


class linearGradient:
    def __init__(self, id: str, **kwargs):
        self.id = id
        self.__attrs = attribute(kwargs)
        self.elements = []

    def append(self, element):
        self.elements.append(element.__str__())
        return self

    def __str__(self):
        return f'<linearGradient id="{self.id}" {self.__attrs}>{" ".join(self.elements)}</linearGradient>'


class radialGradient:
    def __init__(self, id: str, **kwargs):
        self.id = id
        self.__attrs = attribute(kwargs)
        self.elements = []

    def append(self, element):
        self.elements.append(element.__str__())
        return self

    def __str__(self):
        return f'<radialGradient id="{self.id}" {self.__attrs}>{" ".join(self.elements)}</radialGradient>'


class stop:
    def __init__(self, offset: str, stop_color: str = None, stop_opacity: str = None, **kwargs):
        kwargs['offset'] = offset
        if stop_color:
            kwargs['stop-color'] = stop_color
        if stop_opacity:
            kwargs['stop-opacity'] = stop_opacity
        self.attrs = attribute(kwargs)
        # self.elements = []

    # def append(self, element):
    #     self.elements.append(element.__str__())

    def __str__(self):
        return f'<stop {self.attrs} />'
