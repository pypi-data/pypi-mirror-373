import unittest
import numpy as np
from intervalpy import Interval, ExtendedInterval


class TestStringMethods(unittest.TestCase):
    def test_addition(self):
        a = Interval([1, 2])
        b = Interval([3, 4])
        c = Interval([4, 6])
        self.assertEqual(a + b, c)

    def test_subtraction(self):
        a = Interval([1, 2])
        b = Interval([3, 4])
        c = Interval([-3, -1])
        self.assertEqual(a - b, c)

    def test_multiplication(self):
        a = Interval([1, 2])
        b = Interval([3, 4])
        c = Interval([3, 8])
        self.assertEqual(a * b, c)

    def test_division(self):
        a = Interval([1, 2])
        b = Interval([3, 4])
        c = Interval([1/4, 2/3])
        self.assertEqual(a / b, c)

    def test_zero_division(self):
        # print("b2 == 0 and a2 <= 0")
        a = Interval([-2, -1])
        b = Interval([-1, 0])
        c = Interval([1, np.inf])
        self.assertEqual(a / b, c)
        # elif a2 < 0 and b1 < 0 and b2 > 0:
        #     c = [[-np.inf, a2 / b2], [a2 / b1, np.inf]]
        # print("a2 < 0 and b1 < 0 and b2 > 0")
        a = Interval([-2, -1])
        b = Interval([-1, 1])
        c = ExtendedInterval([Interval([-np.inf, -1]), Interval([1, np.inf])])
        self.assertEqual(a / b, c)
        # print("a2 <= 0 and b1 = 0")
        a = Interval([-2, -1])
        b = Interval([0, 1])
        c = Interval([-np.inf, -1])
        self.assertEqual(a / b, c)
        # print("a1 >= 0 and a2 == 0")
        a = Interval([1, 2])
        b = Interval([-1, 0])
        c = Interval([-np.inf, -1])
        self.assertEqual(a / b, c)
        # print("a1 > 0 and b1 < 0 and b2 > 0")
        a = Interval([1, 2])
        b = Interval([-1, 1])
        c = ExtendedInterval([Interval([-np.inf, -1]), Interval([1, np.inf])])
        self.assertEqual(a / b, c)
        # print("a1 >= 0 and b1 = 0")
        a = Interval([1, 2])
        b = Interval([0, 1])
        c = Interval([1, np.inf])
        self.assertEqual(a / b, c)
        # print("a1 <= 0 and a2 >= 0")
        a = Interval([-1, 1])
        b = Interval([-1, 1])
        c = Interval([-np.inf, np.inf])
        self.assertEqual(a / b, c)

    def test_extended_interval_methods(self):
        a = 1
        b = ExtendedInterval([Interval([-np.inf, -1]), Interval([0, np.inf])])
        c = ExtendedInterval([Interval([-np.inf, 1]), Interval([2, np.inf])])
        self.assertEqual(a - b, c)
        a = Interval([-1, 1])
        b = ExtendedInterval([Interval([-1, 1]), Interval([-2, 2])])
        c = [True, False]
        self.assertEqual(b.isIn(a), c)
        a = Interval([-1, 1])
        b = ExtendedInterval([Interval([-3, -2]), Interval([-2, 2])])
        c = [True, False]
        self.assertEqual(b.isNoIntersec(a), c)

if __name__ == '__main__':
    unittest.main()
