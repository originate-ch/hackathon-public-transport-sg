import time
import numpy as np
import pandas as pd
from itertools import pairwise
import matplotlib.pyplot as plt


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __rmul__(self, other):
        return Point(other * self.x, other * self.y)

    def __truediv__(self, other):
        if other == 0.0:
            raise ZeroDivisionError('Cannot divide by 0.')
        return Point(self.x / other, self.y / other)


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


def do_intersect(line1: Line, line2: Line) -> bool:
    P1, Q1 = line1.start_point, line1.end_point
    P2, Q2 = line2.start_point, line2.end_point

    orientation_line1_P2 = compute_orientation(P1, Q1, P2)
    orientation_line1_Q2 = compute_orientation(P1, Q1, Q2)
    orientation_line2_P1 = compute_orientation(P2, Q2, P1)
    orientation_line2_Q1 = compute_orientation(P2, Q2, Q1)

    if orientation_line1_P2 != orientation_line1_Q2 and orientation_line2_P1 != orientation_line2_Q1:
        return True

    if orientation_line1_P2 == 0 and is_on_line(line1, P2):
        return True
    if orientation_line1_Q2 == 0 and is_on_line(line1, Q2):
        return True
    if orientation_line2_P1 == 0 and is_on_line(line2, P1):
        return True
    if orientation_line2_Q1 == 0 and is_on_line(line2, Q1):
        return True

    else:
        return False


def get_middle_index(points_list: list) -> int:
    nb_segments = len(points_list)
    return nb_segments // 2


def compute_label_points(points_list: list) -> (Point, Point):
    idx = get_middle_index(points_list)
    P, Q = points_list[idx], points_list[idx + 1]
    M = (P + Q) / 2.0
    segment_vec = Q - P
    translate_vec = Point(segment_vec.y, -segment_vec.x)
    L1 = M + 0.5 * translate_vec
    L2 = M - 0.5 * translate_vec
    return L1, L2


def compute_bounding_rectangle(points_list: list) -> (float, float, float, float):
    x_min = min([P.x for P in points_list])
    x_max = max([P.x for P in points_list])
    y_min = min([P.y for P in points_list])
    y_max = max([P.y for P in points_list])
    return (x_min, x_max, y_min, y_max)


def is_in_bounding_rectangle(P: Point, corner_points: tuple) -> bool:
    x_min, x_max, y_min, y_max = corner_points
    if P.x < x_min or x_max < P.x or P.y < y_min or y_max < P.y:
        return False
    else:
        return True


def get_nb_passengers(P: Point) -> float:
    pass


def check_intersection_border_traffic_line(border_points: list, traffic_line_points: list) -> list:
    incoming_traffic_points = []
    for A, B in pairwise(traffic_line_points):
        line_traffic = Line(A, B)
        for P, Q in pairwise(border_points):
            line_border = Line(P, Q)
            if do_intersect(line_border, line_traffic):
                incoming_traffic = get_nb_passengers(P)
                incoming_traffic_points.append((P, Q, incoming_traffic))
    return incoming_traffic_points


# -------------------------------------------------------------------------
# test functions
# -------------------------------------------------------------------------

def test_intersection_function() -> None:
    P1 = Point(0, 0)
    Q1 = Point(10, 0)
    P2 = Point(0, -1)
    line1 = Line(P1, Q1)
    list_Q2 = [Point(10, -1), Point(15, 0), Point(10, 0), Point(10, 1), Point(0, 1), Point(0, 0), Point(-5, 0)]
    for Q2 in list_Q2:
        line2 = Line(P2, Q2)
        start = time.time()
        intersect = do_intersect(line1, line2)
        end = time.time()
        print('Lines do intersect: {}'.format(intersect))
        print('Time to compute intersection: {}'.format(end - start))
        P1, Q1 = line1.start_point, line1.end_point
        P2, Q2 = line2.start_point, line2.end_point
        plt.plot([P1.x, Q1.x], [P1.y, Q1.y], label='Line 1')
        plt.plot([P2.x, Q2.x], [P2.y, Q2.y], label='Line 2')
        plt.title('Intersection={}'.format(intersect))
        plt.legend()
        plt.show()
    return None


def test_label_points() -> None:
    points_list = [Point(0.0, 0.0), Point(1.0, 0.0), Point(1.0, 1.0), Point(0.0, 2.0), Point(-1.0, 1.0)]
    x_vals = [P.x for P in points_list]
    y_vals = [P.y for P in points_list]
    L1, L2 = compute_label_points(points_list)

    plt.plot(x_vals, y_vals)
    plt.scatter(L1.x, L1.y, color='red')
    plt.scatter(L2.x, L2.y, color='red')
    plt.xlim(-2, 2)
    plt.ylim(-1, 3)
    plt.grid()
    plt.show()

# test_intersection_function()
# test_label_points()
