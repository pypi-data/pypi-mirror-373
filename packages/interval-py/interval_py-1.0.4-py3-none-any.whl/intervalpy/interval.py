import math
import numpy as np


class Interval:

    def __init__(self, x):
        self.x = x.copy()

    def __repr__(self):
        """
        Representation of the interval as [a, b]
        :return: rounded ends of the interval
        """
        return "[" + str(round(self.x[0], 3)) + ", " + str(round(self.x[1], 3)) + "]"

    def __round__(self, n=3):
        return Interval([np.round(self.x[0], 3), np.round(self.x[1], 3)])

    def mid(self):
        """
        Calculate middle point of the interval
        :return: middle of the interval, float
        """
        return 0.5 * (self.x[0] + self.x[1])

    def width(self):
        """
        Calculate width of the interval
        :return: width of the interval, float
        """
        return self.x[1] - self.x[0]

    def abs_scale(self, a):
        """
        Enlarge interval with a value
        :param a: float
        :return: enlarged interval
        """
        return Interval([self.x[0] - a, self.x[1] + a])
    def scale(self, factor):
        m = 0.5 * (self.x[0] + self.x[1])
        r = 0.5 * (self.x[1] - self.x[0])
        self.x[0] = m - factor * r
        self.x[1] = m + factor * r

    def isIn(self, other):
        """
        Check if the interval is inside of the another interval
        :param other: second interval
        :return: bool
        """
        return (self.x[0] >= other.x[0]) and (self.x[1] <= other.x[1])

    def isNoIntersec(self, other):
        """
        Check if the interval has no intersection with another interval
        :param other: second interval
        :return: bool
        """
        return (self.x[0] > other.x[1]) or (self.x[1] < other.x[0])

    def intersec(self, other):
        """
        Intersec two intervals
        :param other: second interval
        :return: intersection of the two intervals, interval
        """
        if self.x[1] < other.x[0] or other.x[1] < self.x[0]:
            return None
        #             raise ValueError(other.x[0], other.x[1], "results in wrong bounds:", self.x[0], self.x[1])
        else:
            return Interval([max(self.x[0], other.x[0]), min(self.x[1], other.x[1])])

    def __getitem__(self, item):
        """
        Get the end of the interval
        :param item: left(0) or right(1) end of the interval
        :return: end of the interval, float
        """
        return self.x[item]

    def __setitem__(self, key, value):
        """
        Set the end of the interval
        :param key: left(0) or right(1) end of the interval
        :param value: new value of the end of the interval
        """
        self.x.__setitem__(key, value)

    def __neg__(self):
        """
        Return negative interval
        :return: interval
        """
        ninterval = Interval(self.x)
        ninterval.x[0] = - self.x[1]
        ninterval.x[1] = - self.x[0]
        return ninterval

    def __eq__(self, other):
        if self.x[0] == other.x[0] and self.x[1] == other.x[1]:
            return True
        else:
            return False

    def __add__(self, other):
        """
        Interval addition of two intervals
        :param other: second interval
        :return: interval
        """
        ointerval = valueToInterval(other)
        ninterval = Interval(self.x)
        ninterval.x[0] = self.x[0] + ointerval.x[0]
        ninterval.x[1] = self.x[1] + ointerval.x[1]
        return ninterval

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        """
        Interval subtraction of two intervals
        :param other: second interval
        :return: interval
        """
        ointerval = valueToInterval(other)
        ninterval = Interval(self.x)
        ninterval.x[0] = self.x[0] - ointerval.x[1]
        ninterval.x[1] = self.x[1] - ointerval.x[0]
        return ninterval

    def __rsub__(self, other):
        ointerval = valueToInterval(other)
        return ointerval.__sub__(self)

    def __pow__(self, other):
        """
        Interval power function
        :param other: power value
        :return: interval
        """
        ninterval = Interval(self.x)
        u = self.x[0] ** other
        v = self.x[1] ** other
        if other == 0:
            ninterval.x[0] = 1
            ninterval.x[1] = 1
        elif other % 2 == 0:
            ninterval.x[1] = max(u, v)
            if self.x[0] <= 0 and self.x[1] >= 0:
                ninterval.x[0] = 0
            else:
                ninterval.x[0] = min(u, v)
        else:
            ninterval.x[0] = u
            ninterval.x[1] = v
        return ninterval

    def __mul__(self, other):
        """
        Interval multiplication
        :param other: second interval
        :return: interval
        """
        ointerval = valueToInterval(other)
        v = [self.x[0] * ointerval.x[0], self.x[0] * ointerval.x[1], self.x[1] * ointerval.x[0],
             self.x[1] * ointerval.x[1]]
        b = [min(v), max(v)]
        return Interval(b)

    def __truediv__(self, other):
        """
        Interval division. It includes two variants: if the denominator interval contains zero and doesn't contain
        :param other: second interval
        :return: interval or extended interval
        """
        ointerval = valueToInterval(other)
        if not (valueToInterval(0).isIn(ointerval)):
            v = [self.x[0] / ointerval.x[0], self.x[0] / ointerval.x[1], self.x[1] / ointerval.x[0],
                 self.x[1] / ointerval.x[1]]
            f = [min(v), max(v)]
            return Interval(f)
        else:
            #             print(self)
            #             print(ointerval)
            a1, a2 = self.x[0], self.x[1]
            b1, b2 = ointerval.x[0], ointerval.x[1]
            if b2 == 0 and a2 <= 0:
                c = [a2 / b1, np.inf]
            elif a2 < 0 and b1 < 0 and b2 > 0:
                c = [[-np.inf, a2 / b2], [a2 / b1, np.inf]]
            elif a2 <= 0 and b1 == 0:
                c = [-np.inf, a2 / b2]
            elif a1 >= 0 and b2 == 0:
                c = [-np.inf, a1 / b1]
            elif a1 > 0 and b1 < 0 and b2 > 0:
                c = [[-np.inf, a1 / b1], [a1 / b2, np.inf]]
            elif a1 >= 0 and b1 == 0:
                c = [a1 / b2, np.inf]
            elif a1 <= 0 and a2 >= 0:
                c = [-np.inf, np.inf]
            if len(np.shape(c)) != 2:
                c = Interval(c)
            else:
                ival_c = []
                for el in c:
                    ival_c.append(Interval(el))
                c = ExtendedInterval(ival_c)
            return c

    def __floordiv__(self, other):
        """
        Floor division
        :param other: second interval
        :return: interval
        """
        ointerval = valueToInterval(other)
        v = [self.x[0] // ointerval.x[0], self.x[0] // ointerval.x[1], self.x[1] // ointerval.x[0],
             self.x[1] // ointerval.x[1]]
        b = [min(v), max(v)]
        return Interval(b)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rtruediv__(self, other):
        ointerval = valueToInterval(other)
        return ointerval.__truediv__(self)
    def __abs__(self):
        """
        Absolute interval
        :param x: input interval
        :return: interval
        """
        a, b = self.x[0], self.x[1]
        if b < 0:
            return Interval([-a, -b])
        elif a < 0 and b > 0:
            if -a > b:
                return Interval([b, -a])
            else:
                return Interval([-a, b])
        else:
            return Interval([a, b])
    def sqrt(self):
        #         print("sqrt att", self)
        if isinstance(self, (int, np.integer)):
            return math.sqrt(self)
        elif isinstance(self, (float, np.float64)):
            return math.sqrt(self)
        else:
            return Interval([math.sqrt(self[0]), math.sqrt(self[1])])

    def sin(self):
        """
        Interval sine function
        :param x: input interval
        :return: interval
        """
        if isinstance(self, (int, np.integer)):
            return math.sin(self)
        elif isinstance(self, (float, np.float64)):
            return math.sin(self)
        else:
            y = [math.sin(self[0]), math.sin(self[1])]
            pi2 = 2 * math.pi
            pi05 = math.pi / 2
            if math.ceil((self[0] - pi05) / pi2) <= math.floor((self[1] - pi05) / pi2):
                b = 1
            else:
                b = max(y)
            if math.ceil((self[0] + pi05) / pi2) <= math.floor((self[1] + pi05) / pi2):
                a = -1
            else:
                a = min(y)
            return Interval([a, b])

    def cos(self):
        """
        Interval cosine function
        :param x: input interval
        :return: interval
        """
        if isinstance(self, (int, np.integer)):
            return math.cos(self)
        elif isinstance(self, (float, np.float64)):
            return math.cos(self)
        else:
            y = [math.cos(self[0]), math.cos(self[1])]
            pi2 = 2 * math.pi
            if math.ceil(self[0] / pi2) <= math.floor(self[1] / pi2):
                b = 1
            else:
                b = max(y)
            if math.ceil((self[0] - math.pi) / pi2) <= math.floor((self[1] - math.pi) / pi2):
                a = -1
            else:
                a = min(y)
            return Interval([a, b])

    def exp(self):
        if isinstance(self, (int, np.integer)):
            return math.exp(self)
        elif isinstance(self, (float, np.float64)):
            return math.exp(self)
        else:
            return Interval([math.exp(self[0]), math.exp(self[1])])

    def log(self, base=np.exp):
        """
        Interval Logarithm function
        :param x: input interval
        :param base: base value
        :return: interval
        """
        if base > 1:
            return Interval([math.log(x[0], base), math.log(x[1], base)])
        else:
            return Interval([math.log(x[1], base), math.log(x[0], base)])


class ExtendedInterval(Interval):
    def __init__(self, x):
        self.x = x.copy()

    def __sub__(self, other):
        """
        Interval subtraction of extended interval and classical
        :param other: interval
        :return: extended interval
        """
        ointerval = valueToIntervalExtended(other)
        ninterval = ExtendedInterval([Interval([0, 0]), Interval([0, 0])])
        ninterval[0][0] = -np.inf
        ninterval[1][1] = np.inf
        ninterval[0][1] = self.x[0] - ointerval[1][0]
        ninterval[1][0] = self.x[0] - ointerval[0][1]
        return ninterval

    def name(self):
        return "Extended"

    def __rsub__(self, other):
        ointerval = valueToIntervalExtended(other)
        return ointerval.__sub__(self)

    def isIn(self, other):
        """
        Check if every interval of the extended interval is inside of the another interval
        :param other: second interval
        :return: list of bool
        """
        isIn_list = []
        for interval in self:
            isIn_list.append((interval.x[0] >= other.x[0]) and (interval.x[1] <= other.x[1]))
        return isIn_list

    def isNoIntersec(self, other):
        """
        Check if every interval of the extended interval has no intersection with another interval
        :param other: second interval
        :return: list of bool
        """
        isIntersec_list = []
        for interval in self:
            isIntersec_list.append((interval.x[0] >= other.x[1]) or (interval.x[1] <= other.x[0]))
        return isIntersec_list


def valueToInterval(expr):
    """
    Transformate float and int values into interval type
    :param expr: input float or int
    :return: interval
    """
    if isinstance(expr, int):
        etmp = Interval([expr, expr])
    elif isinstance(expr, float):
        etmp = Interval([expr, expr])
    elif isinstance(expr, np.integer):
        etmp = Interval([expr, expr])
    elif isinstance(expr, np.float64):
        etmp = Interval([expr, expr])
    else:
        etmp = expr
    return etmp


def valueToIntervalExtended(expr):
    """
        Transformate expr into extended interval type
        :param expr: input float or int
        :return: extended interval
        """
    if isinstance(expr, int):
        etmp = ExtendedInterval([expr, expr])
    elif isinstance(expr, float):
        etmp = ExtendedInterval([expr, expr])
    else:
        etmp = expr
    return etmp


def sin(x):
    """
    Interval sine function
    :param x: input interval
    :return: interval
    """
    if isinstance(x, (int, np.integer)):
        return math.sin(x)
    elif isinstance(x, (float, np.float64)):
        return math.sin(x)
    else:
        y = [math.sin(x[0]), math.sin(x[1])]
        pi2 = 2 * math.pi
        pi05 = math.pi / 2
        if math.ceil((x[0] - pi05) / pi2) <= math.floor((x[1] - pi05) / pi2):
            b = 1
        else:
            b = max(y)

        if math.ceil((x[0] + pi05) / pi2) <= math.floor((x[1] + pi05) / pi2):
            a = -1
        else:
            a = min(y)
        return Interval([a, b])


def cos(x):
    """
    Interval cosine function
    :param x: input interval
    :return: interval
    """
    if isinstance(x, (int, np.integer)):
        return math.cos(x)
    elif isinstance(x, (float, np.float64)):
        return math.cos(x)
    else:
        y = [math.cos(x[0]), math.cos(x[1])]
        pi2 = 2 * math.pi
        if math.ceil(x[0] / pi2) <= math.floor(x[1] / pi2):
            b = 1
        else:
            b = max(y)
        if math.ceil((x[0] - math.pi) / pi2) <= math.floor((x[1] - math.pi) / pi2):
            a = -1
        else:
            a = min(y)
        return Interval([a, b])


def exp(x):
    """
    Interval exponent function
    :param x: input interval
    :return: interval
    """
    return Interval([math.exp(x[0]), math.exp(x[1])])


def abs(x):
    """
    Absolute interval
    :param x: input interval
    :return: interval
    """
    if x[1] < 0:
        return Interval([-x[0], -x[1]])
    elif x[0] < 0 and x[1] > 0:
        if -x[0] > x[1]:
            return Interval([x[1], -x[0]])
        else:
            return Interval([-x[0], x[1]])
    else:
        return Interval([x[0], x[1]])


def log(x, base):
    """
    Interval Logarithm function
    :param x: input interval
    :param base: base value
    :return: interval
    """
    if base > 1:
        return Interval([math.log(x[0], base), math.log(x[1], base)])
    else:
        return Interval([math.log(x[1], base), math.log(x[0], base)])

def sqrt(x):
    #     print("sqrt", x)
    if isinstance(x, (int, np.integer)):
        return np.sqrt(x)
    elif isinstance(x, (float, np.float64)):
        return np.sqrt(x)
    else:
        return Interval([np.sqrt(x[0]), np.sqrt(x[1])])