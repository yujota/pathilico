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


class TestMove(unittest.TestCase):

    def getTargetFunction(self):
        from pathilico.app.position import move as f
        return f

    def getPositionModel(self):
        from pathilico.app.position import PositionModel as cls
        return cls

    def testMove(self):
        func = self.getTargetFunction()
        PositionModel = self.getPositionModel()
        model = PositionModel()
        dx, dy = 3, 4
        actual = func(model, dx, dy)
        self.assertEqual(-3, actual.x)
        self.assertEqual(-4, actual.y)


class TestShrink(unittest.TestCase):

    def getTargetFunction(self):
        from pathilico.app.position import shrink as f
        return f

    def getPositionModel(self):
        from pathilico.app.position import PositionModel as cls
        return cls

    def testShrinkByOrigin(self):
        func = self.getTargetFunction()
        PositionModel = self.getPositionModel()
        model = PositionModel()
        ds = [1, 4, 16]
        actual = func(model, 0, 0, ds)
        self.assertEqual(0, actual.x)
        self.assertEqual(0, actual.y)
        self.assertEqual(1, actual.level)

    def testShrinkByPointOne(self):
        func = self.getTargetFunction()
        PositionModel = self.getPositionModel()
        model = PositionModel()
        ds = [1, 4, 16]
        model.x = 16
        model.y = 16
        actual = func(model, 0, 0, ds)
        self.assertEqual(4, actual.x)
        self.assertEqual(4, actual.y)
        self.assertEqual(1, actual.level)


class TestEnlarge(unittest.TestCase):

    def getTargetFunction(self):
        from pathilico.app.position import enlarge as f
        return f

    def getPositionModel(self):
        from pathilico.app.position import PositionModel as cls
        return cls

    def testEnlargeByOrigin(self):
        func = self.getTargetFunction()
        PositionModel = self.getPositionModel()
        model = PositionModel()
        model.level = 1
        ds = [1, 4, 16]
        actual = func(model, 0, 0, ds)
        self.assertEqual(0, actual.x)
        self.assertEqual(0, actual.y)
        self.assertEqual(0, actual.level)

    def testEnlargeByPointOne(self):
        func = self.getTargetFunction()
        PositionModel = self.getPositionModel()
        model = PositionModel()
        ds = [1, 4, 16]
        model.x = 4
        model.y = 4
        model.level = 1
        actual = func(model, 0, 0, ds)
        self.assertEqual(16, actual.x)
        self.assertEqual(16, actual.y)
        self.assertEqual(0, actual.level)
