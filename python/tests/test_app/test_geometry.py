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
import unittest
import math
import random


class TestHasIntersectionBasic(unittest.TestCase):
    """簡単なベクトル同士でテストをする"""

    def _getTargetFunc(self):
        from pathilico.app.geometry import has_intersection
        return has_intersection

    def test_basic(self):
        f = self._getTargetFunc()
        v = ((100, 200), (200, 400), (100, 360), (180, 200))
        actual = f(*v)
        desired = (False, True, 140, 280)
        self.assertEqual(actual, desired)

        v = ((100, 150), (200, 200), (100, 120), (200, 100))
        actual = f(*v)
        desired = (False, False, 0, 0)
        self.assertEqual(actual, desired)

        v = ((100, 200), (200, 400), (100, 360), (180, 200))
        actual = f(*v)
        desired = (False, True, 140, 280)
        self.assertEqual(actual, desired)

        v = ((100, 150), (200, 200), (100, 120), (200, 100))
        actual = f(*v)
        desired = (False, False, 0, 0)
        self.assertEqual(actual, desired)


class TestHasIntersection360WithHorizontalLine(unittest.TestCase):

    def _getTestPattern(self, line_length=87, intersection=(100, 100)):
        """Returns List[angle(int), point_a0(tuple[int, int]), point_a1]"""
        results = list()
        for angle in range(0, 360, 10):
            dx = int(line_length * math.cos(math.radians(angle)))
            dy = int(line_length * math.sin(math.radians(angle)))
            p_a0 = (intersection[0]-dx, intersection[1]-dy)
            p_a1 = (intersection[0]+dx, intersection[1]+dy)
            results.append((angle, p_a0, p_a1))
        return results

    def _getTargetFunc(self):
        from pathilico.app.geometry import has_intersection
        return has_intersection

    def _getTargetSympyFunc(self):
        from pathilico.app.geometry import has_intersection_slow
        return has_intersection_slow

    def test_360with_horizontal_line(self):
        f = self._getTargetFunc()
        hor_line_p0 = (50, 100)
        hor_line_p1 = (150, 100)
        patterns = self._getTestPattern()
        for angle, a0, a1 in patterns:
            with self.subTest(angle=angle, a0=a0, a1=a1):
                actual = f(a0, a1, hor_line_p0, hor_line_p1)
                if angle % 180 == 0:
                    desired = (True, False, 0, 0)
                else:
                    desired = (False, True, 100, 100)
                self.assertEqual(actual, desired)

    def test_360with_horizontal_line_by_sympy(self):
        f = self._getTargetFunc()
        sym_f = self._getTargetSympyFunc()
        hor_line_p0 = (50, 100)
        hor_line_p1 = (150, 100)
        patterns = self._getTestPattern()
        for angle, a0, a1 in patterns:
            with self.subTest(angle=angle, a0=a0, a1=a1):
                is_p, has_i, a_x, a_y = f(a0, a1, hor_line_p0, hor_line_p1)
                if has_i:
                    flag, d_x, d_y = sym_f(a0, a1, hor_line_p0, hor_line_p1)
                    self.assertEqual(a_x, d_x)
                    self.assertEqual(a_y, d_y)


class TestHasIntersectionBySympy(unittest.TestCase):
    def _getTargetFunc(self):
        from pathilico.app.geometry import has_intersection_with_k
        return has_intersection_with_k

    def _getTargetSympyFunc(self):
        from pathilico.app.geometry import has_intersection_slow
        return has_intersection_slow

    def test_random_point_positive_control(self):
        sym_f = self._getTargetSympyFunc()
        f = self._getTargetFunc()
        c = 0
        for _ in range(1000):
            ps = list()
            for i in range(4):
                ps.append(random.sample(range(100), 2))
            has_ins, x, y = sym_f(*ps)
            if has_ins:
                a_is_par, a_hasins, a_x, a_y, k = f(*ps)
                if not all([a_hasins, x == a_x, y == a_y]):
                    print(a_is_par, a_hasins, a_x, a_y, x, y, ps, k)
                self.assertTrue(a_hasins)
                self.assertTrue(abs(a_x-x) < 2)
                self.assertTrue(abs(a_y-y) < 2)
            else:
                a_is_par, a_hasins, a_x, a_y, k = f(*ps)
                if a_hasins:
                    print(a_is_par, a_hasins, a_x, a_y, x, y, ps, k)
                self.assertFalse(a_hasins)


class TestGetInscribedPolygon(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
