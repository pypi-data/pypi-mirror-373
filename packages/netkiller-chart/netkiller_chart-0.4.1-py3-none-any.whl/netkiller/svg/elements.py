#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
##############################################
# Home	: https://www.netkiller.cn
# Author: Neo <netkiller@msn.com>
# Data: 2025-08-18
##############################################

class Element:
    def __init__(self):
        pass

    def attribute(self, kwargs):
        attrs = []
        for key, value in kwargs.items():
            if key in ['klass', 'clazz']:
                key = 'class'
            elif key == "inn":
                key = 'in'
            elif '_' in key:
                key = key.replace('_', '-')
            attrs.append(f'{key}="{value}"')
        return " ".join(attrs)


class Title(Element):
    def __init__(self, value):
        self.title = value

    def __str__(self):
        return f"<title>{self.title}</title>"


class Text(Element):
    def __init__(self, text: str = None, x: int = 0, y: int = 0, **kwargs):
        super().__init__()
        self.x = x
        self.y = y
        self.text = text
        self.__attrs = super().attribute(kwargs)
        self.elements = []

    def append(self, element):
        self.elements.append(element.__str__())
        return self

    def __str__(self):
        if self.text:
            return f'<text x="{self.x}" y="{self.y}" {self.__attrs}>{self.text}</text>'
        else:
            return f'<text {self.__attrs}>{"\n".join(self.elements)}</text>'


class TextPath(Element):
    def __init__(self, href: str, text: str, **kwargs):
        if href:
            kwargs['href'] = f"#{href}"
        self.text = text
        self.attrs = super().attribute(kwargs)

    def __str__(self):
        return f"<textPath {self.attrs}>{self.text}</textPath>"


class Line(Element):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, stroke: str = None, fill: str = None, **kwargs):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        if stroke:
            kwargs['stroke'] = stroke
        if fill:
            kwargs['fill'] = fill
        self.attrs = super().attribute(kwargs)

    def __str__(self):
        return f'<line x1="{self.x1}" y1="{self.y1}" x2="{self.x2}" y2="{self.y2}" {self.attrs} />'


class Circle(Element):
    def __init__(self, cx: int, cy: int, r: int, stroke: str = None, fill: str = None, **kwargs):
        self.cx = cx
        self.cy = cy
        self.r = r
        if stroke:
            kwargs['stroke'] = stroke
            # self.stroke = stroke
        if fill:
            kwargs['fill'] = fill
            # self.fill = fill
        self.attrs = super().attribute(kwargs)

    def __str__(self):
        return f'<circle cx="{self.cx}" cy="{self.cy}" r="{self.r}" {self.attrs} />'


class Ellipse(Element):
    def __init__(self, cx: int, cy: int, rx: int, ry: int, stroke: str = None, fill: str = None, **kwargs):
        self.cx = cx
        self.cy = cy
        self.rx = rx
        self.ry = ry
        if stroke:
            kwargs['stroke'] = stroke
        if fill:
            kwargs['fill'] = fill
        self.attrs = super().attribute(kwargs)

    def __str__(self):
        return f'<ellipse cx="{self.cx}" cy="{self.cy}" rx="{self.rx}" ry="{self.ry}" {self.attrs} />'


class Polyline(Element):
    def __init__(self, *points, stroke: str = None, fill: str = None, **kwargs):
        # tuple[int, int]
        self.p = []
        if type(points[0]) == str:
            self.points = points[0]
        else:
            for x, y in points:
                self.p.append(f'{x},{y}')
            self.points = " ".join(self.p)
        if stroke:
            kwargs['stroke'] = stroke
        if fill:
            kwargs['fill'] = fill
        self.attrs = super().attribute(kwargs)

    def __str__(self):
        return f'<polyline points="{self.points}" {self.attrs} />'


class Polygon(Element):
    def __init__(self, *points, stroke: str = None, fill: str = None, **kwargs):
        # tuple[int, int]
        self.p = []
        if type(points[0]) == str:
            self.points = points[0]
        else:
            for x, y in points:
                self.p.append(f'{x},{y}')
            self.points = " ".join(self.p)
        if stroke:
            kwargs['stroke'] = stroke
        if fill:
            kwargs['fill'] = fill
        self.attrs = super().attribute(kwargs)

    def __str__(self):
        return f'<polygon points="{self.points}" {self.attrs} />'


class Rectangle(Element):
    def __init__(self, x: int, y: int, width: int, height: int, stroke: str = None, fill: str = None, **kwargs):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        if stroke:
            kwargs['stroke'] = stroke
        if fill:
            kwargs['fill'] = fill
        self.attrs = super().attribute(kwargs)

    def __str__(self):
        # return f'<circle cx="{self.cx}" cy="{self.cy}" r="{self.r}" stroke="{self.stroke}" fill="{self.fill}" {self.attrs} />'
        return f'<rect x="{self.x}" y="{self.y}" width="{self.width}" height="{self.height}" {self.attrs} />'


class Image(Element):
    def __init__(self, x: int, y: int, width: int, height: int, href: str, **kwargs):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.href = href
        self.attrs = super().attribute(kwargs)

    def __str__(self):
        return f'<image x="{self.x}" y="{self.y}" width="{self.width}" height="{self.height}" xlink:href="{self.href}" {self.attrs} />'


class Path(Element):
    def __init__(self, d: str = None, stroke: str = None, fill: str = None, **kwargs):
        self.d = d
        if stroke:
            kwargs['stroke'] = stroke
        if fill:
            kwargs['fill'] = fill
        self.attrs = super().attribute(kwargs)
        self.drawn = []

    def D(self):
        # https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/d
        self.d = None
        return self

    def M(self, x, y):
        self.drawn.append(f'M {x},{y}')
        return self

    def m(self, dx, dy):
        self.drawn.append(f'M {dx},{dy}')
        return self

    def L(self, x, y):
        self.drawn.append(f'L {x},{y}')
        return self

    def l(self, dx, dy):
        self.drawn.append(f'l {dx},{dy}')
        return self

    def H(self, x: int):
        self.drawn.append(f'H {x}')
        return self

    def H(self, dx: int):
        self.drawn.append(f'H {dx}')
        return self

    def V(self, y: int):
        self.drawn.append(f'H {y}')
        return self

    def v(self, dy: int):
        self.drawn.append(f'H {dy}')
        return self

    def C(self, x1, y1, x2, y2, x, y):
        self.drawn.append(f'C {x1},{y1},{x2},{y2},{x},{y}')
        return self

    def c(self, dx1, dy1, dx2, dy2, dx, dy):
        self.drawn.append(f'c {dx1},{dy1},{dx2},{dy2},{dx},{dy}')
        return self

    def S(self, x2, y2, x, y):
        self.drawn.append(f'S {x2},{y2},{x},{y}')
        return self

    def s(self, dx2, dy2, dx, dy):
        self.drawn.append(f's {dx2},{dy2},{dx},{dy}')
        return self

    def Q(self, x1, y1, x, y):
        self.drawn.append(f'Q {x1},{y1},{x},{y}')
        return self

    def q(self, dx1, dy1, dx, dy):
        self.drawn.append(f'q {dx1},{dy1},{dx},{dy}')
        return self

    def T(self, x, y):
        self.drawn.append(f'T {x},{y}')
        return self

    def t(self, dx, dy):
        self.drawn.append(f't {dx},{dy}')
        return self

    def A(self, rx, ry, angle, large_arc_flag, sweep_flag, x, y):
        self.drawn.append(f'A {rx}, {ry}, {angle}, {large_arc_flag}, {sweep_flag}, {x}, {y}')
        return self

    def a(self, rx, ry, angle, large_arc_flag, sweep_flag, dx, dy):
        self.drawn.append(f'A {rx}, {ry}, {angle}, {large_arc_flag}, {sweep_flag}, {dx}, {dy}')
        return self

    def Z(self):
        self.drawn.append(f'Z')
        return self

    def z(self):
        self.drawn.append(f'z')
        return self

    def __str__(self):
        if not self.d:
            self.d = " ".join(self.drawn)
        return f'<path d="{self.d}" {self.attrs} />'


class Group(Element):
    def __init__(self, **kwargs):
        self.__attrs = super().attribute(kwargs)
        self.elements = []

    def append(self, element):
        self.elements.append(element.__str__())
        return self

    def __str__(self):
        return f'<g {self.__attrs}>\n\t{"\n\t".join(self.elements)}\n</g>'


class Switch(Element):
    def __init__(self, element=None):
        self.elements = []
        if element:
            self.elements.append(element.__str__())

    def append(self, element):
        self.elements.append(element.__str__())
        return self

    def __str__(self):
        return f'<switch>\n{"\n".join(self.elements)}\n</switch>'


class Use(Element):
    def __init__(self, id: str, **kwargs):
        self.id = id
        self.__attrs = super().attribute(kwargs)

    def __str__(self):
        return f'<use xlink:href="#{self.id}" {self.__attrs} />'
