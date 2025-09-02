# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.


class Rectangle(object):
    """rectangle definition 
    """

    def __init__(self, left, top, width, height):
        self._left = left
        self._top = top
        self._width = width
        self._height = height

    def __str__(self):
        return "<Inner Rect (%s, %s, width:%s, height:%s)>" % (self.left,
                                                         self.top,
                                                         self.width,
                                                         self.height)
    __repr__ = __str__

    def __eq__(self, other):
        return self.left == other.left and \
            self.top == other.top and \
            self.width == other.width and \
            self.height == other.height

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, target):
        if isinstance(target, tuple):
            if len(target) == 2:
                x, y = target
                result = x >= self.left and x <= self.right
                result &= y >= self.top and y <= self.bottom
                return result
        else:
            result = target.left >= self.left and target.right <= self.right
            result &= target.top >= self.top and target.bottom <= self.bottom
            return result

    def __mul__(self, other):
        new_rect = type(self)(self.left * other.scale_x,
                              self.top * other.scale_y,
                              self.width * other.scale_x,
                              self.height * other.scale_y)
        return new_rect

    __rmul__ = __mul__

    def __truediv__(self, other):
        new_scale = Scale(1.0 / other.scale_x, 1.0 / other.scale_y)
        return self * new_scale

    __div__ = __truediv__

    def __and__(self, other):
        if self.left >= other.right \
           or other.left >= self.right \
           or self.top >= other.bottom \
           or other.top >= self.bottom:
            return None
        left = max(self.left, other.left)
        width = min(self.right, other.right) - left
        top = max(self.top, other.top)
        height = min(self.bottom, other.bottom) - top
        return Rectangle(left, top, width, height)

    def to_dict(self):
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height
        }

    def scale_to_rect(self, rect):
        scaled_left = rect.width * self.left
        scaled_width = rect.width * self.width
        scaled_top = rect.height * self.top
        scaled_height = rect.height * self.height
        left = round(rect.left + scaled_left, 2)
        top = round(rect.top + scaled_top, 2)
        width = round(scaled_width, 2)
        height = round(scaled_height, 2)
        return Rectangle(left, top, width, height)

    def descale_to_rect(self, rect):
        if rect.width == 0:
            descaled_left = 0
            descaled_width = 0
        else:
            descaled_left = float(self.left - rect.left) / float(rect.width)
            descaled_width = float(self.width) / float(rect.width)
        if rect.height == 0:
            descaled_top = 0
            descaled_height = 0
        else:
            descaled_top = float(self.top - rect.top) / float(rect.height)
            descaled_height = float(self.height) / float(rect.height)
        left = descaled_left
        top = descaled_top
        width = descaled_width
        height = descaled_height
        return Rectangle(left, top, width, height)

    @property
    def left(self):
        return self._left

    @property
    def top(self):
        return self._top

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def bottom(self):
        return self.top + self.height

    @property
    def right(self):
        return self.left + self.width

    @property
    def top_left(self):
        return (self.left, self.top)

    @property
    def center_left(self):
        return (self.left, self.top + self.height / 2.0)

    @property
    def bottom_left(self):
        return (self.left, self.bottom)

    @property
    def center_top(self):
        return (self.left + self.width / 2.0, self.top)

    @property
    def center(self):
        return (self.left + self.width / 2.0, self.top + self.height / 2.0)

    @property
    def center_bottom(self):
        return (self.left + self.width / 2.0, self.bottom)

    @property
    def top_right(self):
        return (self.right, self.top)

    @property
    def center_right(self):
        return (self.right, self.top + self.height / 2.0)

    @property
    def bottom_right(self):
        return (self.right, self.bottom)

class Scale(object):
    def __init__(self, scale_x, scale_y):
        self._scale_x = scale_x
        self._scale_y = scale_y

    @property
    def scale_x(self):
        return self._scale_x

    @property
    def scale_y(self):
        return self._scale_y

    def __str__(self, *args, **kwargs):
        return "<Scale scale_x=%s scale_y=%s>" % (self.scale_x,
                                                  self.scale_y)

    __repr__ = __str__

    def __eq__(self, other):
        return self.scale_x == other.scale_x and \
            self.scale_y == other.scale_y

    def __ne__(self, other):
        return not self.__eq__(other)
