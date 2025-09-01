#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
##############################################
# Home	: https://www.netkiller.cn
# Author: Neo <netkiller@msn.com>
# Data: 2025-08-18
##############################################
from . import attribute


class Marker:
    def __init__(self, id: str, **kwargs):
        # super().__init__()
        self.id = id
        self.attrs = attribute(kwargs)
        self.elements = []

    def append(self, element):
        self.elements.append(element.__str__())
        return self

    def __str__(self):
        return f'<marker id="{self.id}" {self.attrs}>{" ".join(self.elements)}</marker>'


class Mask:
    def __init__(self, id: str, **kwargs):
        # super().__init__()
        self.id = id
        self.attrs = attribute(kwargs)
        self.elements = []

    def append(self, element):
        self.elements.append(element.__str__())
        return self

    def __str__(self):
        return f'<mask id="{self.id}" {self.attrs}>{" ".join(self.elements)}</mask>'
