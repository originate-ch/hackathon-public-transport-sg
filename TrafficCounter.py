import json
import time
import pandas as pd
from more_itertools import pairwise
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
        if isinstance(other, int):
            return Point(other * self.x, other * self.y)
        elif isinstance(other, float):
            return Point(other * self.x, other * self.y)
        else:
            raise TypeError('Multiplication is not defined for Point and {}'.format(type(other)))

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
    ab = B - A
    bc = C - B
    det = ab.x * bc.y - ab.y * bc.x
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


"""
# not needed right now

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
"""


def compute_direction_traffic(line_border: Line, line_traffic: Line) -> int:
    dir_border = line_border.end_point - line_border.start_point
    dir_traffic = line_traffic.end_point - line_traffic.start_point
    det = dir_border.x * dir_traffic.y - dir_border.y * dir_traffic.x
    if det < 0:
        return -1
    if det > 0:
        return 1


def geoshape_to_points(border_dict: dict) -> list:
    border_points = []
    pts_list = border_dict['fields']['geoshape']['coordinates']
    for pt in pts_list:
        border_points.append(Point(pt[0], pt[1]))
    return border_points


def compute_intersection_one_border_all_traffic_lines(border_dict: dict, traffic_data: pd.DataFrame) -> dict:
    border_points = geoshape_to_points(border_dict)

    incoming_traffic_flows = {-1: 0.0, 1: 0.0}
    for _, row in traffic_data.iterrows():
        A = Point(row['GeoShape']['coordinates'][0][0], row['GeoShape']['coordinates'][0][1])
        B = Point(row['GeoShape']['coordinates'][1][0], row['GeoShape']['coordinates'][1][1])
        line_traffic = Line(A, B)
        for P, Q in pairwise(border_points):
            line_border = Line(P, Q)
            if do_intersect(line_border, line_traffic):
                direction = compute_direction_traffic(line_border, line_traffic)
                incoming_traffic_flows[direction] += row['besetzung']

    # L1, L2 = compute_label_points(border_points)
    # traffic_flow_info = (L1, L2, incoming_traffic_flows)
    return incoming_traffic_flows


def set_export_path(path_to_border):
    end = path_to_border.rfind('.json')
    path_export = path_to_border[:end] + '_TrafficFlow.json'
    return path_export


def main_traffic_counter(path_to_df: str, path_to_border: str, year=2019, week_slot='Mo - Fr') -> None:
    traffic_data = pd.read_json(path_to_df)
    traffic_data = traffic_data[traffic_data['fp_jahr'] == year]
    traffic_data = traffic_data[traffic_data['zeitraum'] == week_slot]
    with open(path_to_border) as in_file:
        border_collection = json.load(in_file)
    for border_dict in border_collection:
        traffic_flow = compute_intersection_one_border_all_traffic_lines(border_dict, traffic_data)
        border_dict['fields']['in_left'] = traffic_flow[-1]
        border_dict['fields']['in_right'] = traffic_flow[1]
        border_dict['fields']['in_total'] = traffic_flow[1] + traffic_flow[-1]
    export_path = set_export_path(path_to_border)
    with open(export_path, 'w') as out_file:
        json.dump(border_collection, out_file)
    return None


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


def test_main_TrafficCounter() -> None:
    # set traffic data frame
    row_1 = {'GeoShape': {'coordinates': [[0.0, -1.0], [1.0, -1.0]]}, 'besetzung': 100.5}
    row_2 = {'GeoShape': {'coordinates': [[1.0, -1.0], [0.0, 1.0]]}, 'besetzung': 1.1}
    row_3 = {'GeoShape': {'coordinates': [[0.0, 1.0], [1.0, 1.0]]}, 'besetzung': 100.5}
    row_4 = {'GeoShape': {'coordinates': [[3.0, 2.0], [3.0, 1.0]]}, 'besetzung': 1.3}
    row_5 = {'GeoShape': {'coordinates': [[3.0, 1.0], [2.0, 0.0]]}, 'besetzung': 1.5}
    row_6 = {'GeoShape': {'coordinates': [[1.0, 0.5], [2.0, 0.5]]}, 'besetzung': 1.7}
    row_7 = {'GeoShape': {'coordinates': [[3.0, 0.0], [4.0, 2.0]]}, 'besetzung': 100.0}
    df_traffic = pd.DataFrame(columns=['GeoShape', 'besetzung'])
    for row in [row_1, row_2, row_3, row_4, row_5, row_6, row_7]:
        df_traffic = df_traffic.append(row, ignore_index=True)

    # load border from json
    path_to_border = 'example json/border_example.json'
    with open(path_to_border, 'r') as in_file:
        border_collection = json.load(in_file)

    # test function
    for border_dict in border_collection:
        traffic_flow = compute_intersection_one_border_all_traffic_lines(border_dict, df_traffic)
        border_dict['in_right'] = traffic_flow[-1]
        border_dict['in_left'] = traffic_flow[1]
    export_path = set_export_path(path_to_border)
    with open(export_path, 'w') as out_file:
        json.dump(border_collection, out_file)

    # matplotlib visualisation
    border_points = geoshape_to_points(border_dict)
    for row in [row_1, row_2, row_3, row_4, row_5, row_6, row_7]:
        df_traffic = df_traffic.append(row, ignore_index=True)

    plt.plot([P.x for P in border_points], [P.y for P in border_points], lw=4.0, label='border')
    for row in [row_1, row_2, row_3, row_4, row_5, row_6, row_7]:
        x_vals = [p[0] for p in row['GeoShape']['coordinates']]
        y_vals = [p[1] for p in row['GeoShape']['coordinates']]
        plt.plot(x_vals, y_vals, label=row['besetzung'])
    plt.legend()
    plt.show()
    return None


# test_intersection_function()
# test_label_points()
# test_main_TrafficCounter()

# -------------------------------------------------------------------------
# apply main function
# -------------------------------------------------------------------------

main_traffic_counter(path_to_df='ov_route_sections_FULL_df.json',
                     path_to_border='example json/borders_presentation.json')
