import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line:
    def __init__(self, start_point, end_point):
        self.start_point = start_point
        self.end_point = end_point


def is_on_line(line: Line, R: Point) -> bool:
    P, Q = line.start_point, line.end_point
    if (R.x <= max(P.x, Q.x)) and (R.x >= min(P.x, Q.x)) and (R.y <= max(P.y, Q.y)) and (R.y >= min(P.y, Q.y)):
        return True
    return False


def compute_orientation(A: Point, B: Point, C: Point) -> int:
    det = (B.x - A.x) * (C.y - B.y) - (B.y - A.y) * (C.x - B.x)
    if det < 0.0:
        # negative orientation
        return -1
    elif det > 0.0:
        # positive orientation
        return 1
    else:
        # collinear orientation
        return 0


def check_intersection(line1: Line, line2: Line) -> bool:
    P1, Q1 = line1.start_point, line1.end_point
    P2, Q2 = line2.start_point, line2.end_point

    orientation_line1_P2 = compute_orientation(P1, Q1, P2)
    orientation_line1_Q2 = compute_orientation(P1, Q1, Q2)
    orientation_line2_P1 = compute_orientation(P2, Q2, P1)
    orientation_line2_Q1 = compute_orientation(P2, Q2, P1)

    if orientation_line1_P2 != orientation_line1_Q2 and orientation_line2_P1 != orientation_line2_Q1:
        return True

    if orientation_line1_P2 and is_on_line(line1, P2):
        return True
    if orientation_line1_Q2 and is_on_line(line1, Q2):
        return True
    if orientation_line2_P1 and is_on_line(line2, P1):
        return True
    if orientation_line2_Q1 and is_on_line(line2, Q1):
        return True

    else:
        return False


def test_intersection_function(line1: Line, line2: Line) -> None:
    print('Lines do intersect: {}'.format(check_intersection(line1, line2)))
    P1, Q1 = line1.start_point, line1.end_point
    P2, Q2 = line2.start_point, line2.end_point
    plt.plot([P1.x, Q1.x], [P1.y, Q1.y], label='Line 1')
    plt.plot([P2.x, Q2.x], [P2.y, Q2.y], label='Line 2')
    plt.legend()
    plt.show()
    return None


P1 = Point(1, 1)
Q1 = Point(10, 1)
P2 = Point(1, 2)
Q2 = Point(10, 2)
line1 = Line(P1, Q1)
line2 = Line(P2, Q2)
test_intersection_function(line1, line2)