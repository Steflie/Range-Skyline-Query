#!/usr/bin/python

import itertools

class Rectangle():

    def __init__(self, bottom_left, top_right):
        """
        The constructor of the class
        """
        self.bottom_left = bottom_left
        self.top_right = top_right
        self.x1 = bottom_left[0]
        self.y1 = bottom_left[1]
        self.x2 = top_right[0]
        self.y2 = top_right[1]


    def intersection(self, other):
        """
        The implementation of the rectangles intersection
        """
        a, b = self, other
        x1 = max(min(a.x1, a.x2), min(b.x1, b.x2))
        y1 = max(min(a.y1, a.y2), min(b.y1, b.y2))
        x2 = min(max(a.x1, a.x2), max(b.x1, b.x2))
        y2 = min(max(a.y1, a.y2), max(b.y1, b.y2))
        if x1 < x2 and y1 < y2:
            return type(self)([x1, y1], [x2, y2])
    __and__ = intersection


    def difference(self, other):
        """
        The implementation of the rectangles difference
        """
        inter = self & other
        if not inter:
            yield self
            return
        xs = {self.x1, self.x2}
        ys = {self.y1, self.y2}
        if self.x1 < other.x1 < self.x2: xs.add(other.x1)
        if self.x1 < other.x2 < self.x2: xs.add(other.x2)
        if self.y1 < other.y1 < self.y2: ys.add(other.y1)
        if self.y1 < other.y2 < self.y2: ys.add(other.y2)
        for (x1, x2), (y1, y2) in itertools.product(
            pairwise(sorted(xs)), pairwise(sorted(ys))
        ):
            rect = type(self)([x1, y1], [x2, y2])
            if rect != inter:
                yield rect
    __sub__ = difference


    def __iter__(self):
        """
        Overwrite ther __iter__ function
        """
        yield self.x1
        yield self.y1
        yield self.x2
        yield self.y2


    def __eq__(self, other):
        """
        Overwrite ther __eq__ function
        """
        return isinstance(other, Rectangle) and tuple(self) == tuple(other)


    def __ne__(self, other):
        """
        Overwrite ther __ne__ function
        """
        return not (self == other)


    def __repr__(self):
        """
        Overwrite the __repr__ function
        """
        return type(self).__name__ + repr(tuple(self))


    


def pairwise(iterable):
    # //docs.python.org/dev/library/itertools.html#recipes
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

    