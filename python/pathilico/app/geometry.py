#   Copyright
#     2019 Department of Dermatology, School of Medicine, Tohoku University
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
from functools import partial
import itertools

from skimage.measure import approximate_polygon, subdivide_polygon
from sympy.geometry import Segment, Point
import numpy as np


def has_intersection_slow(p_a0, p_a1, p_b0, p_b1):
    """Check intersection of two segment(line)s

    :param p_a0 tuple[int, int]|numpy.ndarray:
    :param p_a1 tuple[int, int]|numpy.ndarray:
    :param p_b0 tuple[int, int]|numpy.ndarray:
    :param p_b1 tuple[int, int]|numpy.ndarray:
    :return bool, int, int:
    """
    segment_a = Segment(Point(p_a0), Point(p_a1))
    segment_b = Segment(Point(p_b0), Point(p_b1))
    intersections = segment_a.intersection(segment_b)
    if intersections:
        p = intersections[0]
        return True, int(p.x), int(p.y)
    else:
        return False, 0, 0


def has_intersection(p_a0, p_a1, p_b0, p_b1):
    """Returns tuple[is_parallel: bool, has_intersection: bool, x: int, y]"""
    da_x, da_y = p_a1[0] - p_a0[0], p_a1[1] - p_a0[1]
    db_x, db_y = p_b1[0] - p_b0[0], p_b1[1] - p_b0[1]
    if da_x * db_y == db_x * da_y:  # Check parallelism
        return True, False, 0, 0
    a_x, a_y = p_a0
    b_x, b_y = p_b0
    k = (
        (db_y*(a_x - b_x) - db_x*(a_y - b_y)) / (da_y*db_x - da_x*db_y)
    )
    u = (
        (da_y*(a_x - b_x) - da_x*(a_y - b_y)) / (da_y*db_x - da_x*db_y)
    )
    if 0 <= k <= 1 and 0 <= u <= 1:
        # print(da_x, da_y, db_x, db_y, p_a0, p_a1, p_b0, p_b1, k)
        return False, True, int(a_x + k * da_x), int(a_y + k * da_y)
    else:
        return False, False, 0, 0

def has_intersection_with_k(p_a0, p_a1, p_b0, p_b1):
    """Returns tuple[is_parallel: bool, has_intersection: bool, x: int, y]"""
    da_x, da_y = p_a1[0] - p_a0[0], p_a1[1] - p_a0[1]
    db_x, db_y = p_b1[0] - p_b0[0], p_b1[1] - p_b0[1]
    if da_x * db_y == db_x * da_y:  # Check parallelism
        return True, False, 0, 0, 0
    a_x, a_y = p_a0
    b_x, b_y = p_b0
    k = (
        (db_y*(a_x - b_x) - db_x*(a_y - b_y)) / (da_y*db_x - da_x*db_y)
    )
    u = (
        (da_y*(a_x - b_x) - da_x*(a_y - b_y)) / (da_y*db_x - da_x*db_y)
    )
    if 0 <= k <= 1 and 0 <= u <= 1:
        # print(da_x, da_y, db_x, db_y, p_a0, p_a1, p_b0, p_b1, k)
        return False, True, int(a_x + k * da_x), int(a_y + k * da_y), k
    else:
        return False, False, 0, 0, k


def has_intersection2(p_a0, p_a1, p_b0, p_b1):
    x_a, y_a = p_a0
    x_b, y_b = p_a1
    x_c, y_c = p_b0
    x_d, y_d = p_b1
    l_num = ((y_c - y_a) * (x_b - x_a) - (x_c - x_a) * (y_b - y_c))
    l_den = ((x_d - x_c) * (y_b - y_a) - (x_b - x_a) * (y_d - y_c))
    k_num = ((y_a - y_c) * (x_d - x_c) - (x_a - x_c) * (y_d - y_c))
    k_den = ((x_b - x_a) * (y_d - y_c) - (y_b - y_a) * (x_d - x_c))
    if l_den == 0 or k_den == 0:
        return False, False, 0, 0
    l = l_num / l_den
    k = k_num / k_den
    if 0 < l < 1 and 0 < k < 1:
        return False, True, int(x_a + k*(x_b - x_a)), int(y_a + k*(y_b - y_a))
    else:
        return False, False, 0, 0


# has_intersection = has_intersection2

Clockwise = np.array([-1])
CounterClockwise = np.array([1])
Undefined = np.array([0])


def get_circled_pairs(vertices):
    num_v = len(vertices)
    result = list()
    for i in range(0, num_v-1):
        result.append((vertices[i], vertices[i+1]))
    result.append((vertices[num_v-1], vertices[0]))
    return result


def get_orientation(vertices):
    s = 0
    for (x1, y1), (x2, y2) in get_circled_pairs(vertices):
        s += (x2 - x1) * (y2 + y1)
    if s > 0:
        return CounterClockwise
    elif s < 0:
        return Clockwise
    else:
        return Undefined


def has_point_in_triangle(triangle, points):
    a, b, c = triangle
    s = b - a
    t = c - a
    inv_mat = np.linalg.inv(np.vstack([s, t]).transpose())
    for p in points:
        ps, pt = np.dot(inv_mat, p - a)
        if ps >= 0 and pt >= 0 and ps + pt <= 1:
            return True
    return False


def convert_dim1to2(l):
    return [(l[2*i], l[2*i+1]) for i in range(len(l)//2)]


def triangulate(vertices):
    """Return List[int] pyglet.gl.OpenGl like vertices list

    :param vertices List[int]: v2i style
    :return List[int]:
    """
    vertices = np.array(convert_dim1to2(vertices))
    orientation = get_orientation(vertices)
    num_vertex = len(vertices)
    vertex_id_pointer = 0
    remained_point_indices = list(range(num_vertex))
    result = list()
    flag = True
    while len(remained_point_indices) > 2 and flag:
        if vertex_id_pointer not in remained_point_indices:
            vertex_id_pointer += 1
            if vertex_id_pointer > remained_point_indices[-1]:
                # Can't make triangulate
                print("Cant", len(remained_point_indices))
                # return result
                flag = False
                return list()
            else:
                continue
        i = remained_point_indices.index(vertex_id_pointer)
        triangle_ids = \
            (remained_point_indices + remained_point_indices[:2])[i:i+3]
        triangle = (
            vertices[triangle_ids[0]], vertices[triangle_ids[1]],
            vertices[triangle_ids[2]]
        )
        a, b, c = triangle
        c_prod = np.cross(c-b, b-a)
        d_prod = np.dot(orientation, c_prod)
        if d_prod > 0:
            other_points = [
                vertices[i]
                for i in remained_point_indices if i not in triangle_ids
            ]
            if not has_point_in_triangle(triangle, points=other_points):
                result.extend(triangle_ids)
                remained_point_indices.remove(triangle_ids[1])
                vertex_id_pointer = remained_point_indices[0]
                continue
        vertex_id_pointer += 1
    return result


def get_close_curve(x, y, dx, dy, vertices):
    """

    :param int x:
    :param int y:
    :param int dx:
    :param int dy:
    :param List[int] vertices:
    :return bool, List[int]:
    """
    check = partial(has_intersection, (x, y), (x+dx, y+dy))
    result = list()
    for p1, p2 in vertices:
        is_para, has_ins, i_x, i_y = check(p1, p2)
        result.extend(p1)
        if has_ins:
            # return True, [x, y] + result # + [i_x, i_y]
            # return True, result[:-2] + [i_x, i_y]
            return True, result[2:-2] + [i_x, i_y]
    return False, list()


def get_closed_curve_points(x, y, dx, dy, points, dim_points=2):
    if dim_points == 1:
        vs = [
            (points[2*p-2:2*p], points[2*p:2*p+2])
            for p in reversed(range(1, len(points)//2-1))
        ]
    elif dim_points == 2:
        vs = [
            (points[p-1], points[p])
            for p in reversed(range(1, len(points)-1))
        ]
    else:
        raise ValueError
    return get_close_curve(x, y, dx, dy, vs)


def reduce_coordinates(points, dim_points=2):
    if dim_points == 1:
        vs = np.array([
            [points[2*i], points[2*i+1]]
            for i in reversed(range(0, len(points)//2))
        ])
    elif dim_points == 2:
        vs = points
    else:
        raise ValueError
    for _ in range(5):
        if len(vs) < 4:
            return list()
        vs = subdivide_polygon(vs, preserve_ends=True)
    vs = approximate_polygon(vs, tolerance=1.8)
    if dim_points == 1:
        return [int(i) for i in itertools.chain.from_iterable(vs)]
    return vs


def get_circumscribed_rectangle(points, dim_points=2):
    if dim_points == 2:
        xs = [r[0] for r in points]
        ys = [r[1] for r in points]
    elif dim_points == 1:
        xs = [points[i] for i in range(0, len(points), 2)]
        ys = [points[i] for i in range(1, len(points), 2)]
    else:
        raise ValueError
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    return x0, y0, x1-x0, y1-y0


def safe_append(result, i_x, i_y):
    pass


def get_inscribed_polygon_vertices(vertices):
    threshold = 5 * 2
    num_min_points = 10
    num_points = len(vertices) // 2
    if num_points <= num_min_points:
        return list()
    pairs = list()
    for i in reversed(range(num_min_points, num_points)):
        if len(pairs) > 0:
            break
            if len(pairs) > 1:
                break
            elif pairs[0][-1] == i:
                break
        x, y = vertices[2*i: 2*i+2]
        for j in reversed(range(0, i-num_min_points)):
            h, v = vertices[2*j: 2*j+2]
            if (x-h) ** 2 + (y-v) ** 2 < threshold:
                pairs.append((i, j))
                break
    num_pairs = len(pairs)
    if num_pairs == 0:
        return list()
    elif num_pairs == 1:
        end, start = pairs[0]
        return vertices[2*start:2*end+2]
    elif len(pairs) == 2:
        print("Two pair")
        end, p0 = pairs[0]
        start, p1 = pairs[1]
        result = vertices[2*p0:2*p0+2] + vertices[2*start:2*end+2] \
                 + vertices[2*p1:2*p1+2]
        return result
    else:
        return list()
