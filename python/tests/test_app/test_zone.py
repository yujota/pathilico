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
import random


class TestRegisterId(unittest.TestCase):

    def getRegisterFunc(self):
        from pathilico.app.zone import register_id as f
        return f

    def createZoneModel(self):
        from pathilico.app.zone import ZoneModel
        return ZoneModel()

    def testRegisterPathologyIdOne(self):
        model = self.createZoneModel()
        register_func = self.getRegisterFunc()
        id1_bound1 = (0, 3, 10, 20, 0)
        object_id1 = 1234
        model = register_func(model, object_id1, [id1_bound1])
        actual_bounds = model.bounds
        self.assertEqual({id1_bound1}, actual_bounds[object_id1])
        self.assertEqual(1, len((model.pathology.keys())))

    def testRegisterPathologyIdTwo(self):
        model = self.createZoneModel()
        register_func = self.getRegisterFunc()
        id1_bound1 = (0, 3, 10, 20, 0)
        id1_bound2 = (0, 1, 5, 10, 1)
        object_id1 = 1234
        model = register_func(model, object_id1, [id1_bound1, id1_bound2])
        actual_bounds = model.bounds
        self.assertEqual({id1_bound1, id1_bound2}, actual_bounds[object_id1])
        self.assertEqual(2, len((model.pathology.keys())))


class TestUnregisterId(unittest.TestCase):
    def getUnregisterFunc(self):
        from pathilico.app.zone import unregister_id as f
        return f

    def createZoneModel(self):
        from pathilico.app.zone import ZoneModel
        return ZoneModel()

    def testUnregisterPathologyIdOne(self):
        model = self.createZoneModel()
        unregister_func = self.getUnregisterFunc()
        id1_bound1 = (0, 3, 10, 20, 0)
        object_id1 = 1234
        mock_zone_id = 123
        model.object_id2zone_id[object_id1] = {mock_zone_id}
        model.pathology[mock_zone_id].add(object_id1)
        model.bounds[object_id1] = {id1_bound1}
        model = unregister_func(model, object_id1)
        actual_bounds = model.bounds
        self.assertEqual(set(), actual_bounds[object_id1])
        actual_pathology_ids = model.pathology[mock_zone_id]
        self.assertEqual(set(), actual_pathology_ids)
        actual_zone_ids = model.object_id2zone_id[mock_zone_id]
        self.assertEqual(set(), actual_zone_ids)


class TestGetObjectId(unittest.TestCase):
    def getGetPathologyIdFunc(self):
        from pathilico.app.zone import get_object_ids as f
        return f

    def createZoneModel(self):
        from pathilico.app.zone import ZoneModel
        return ZoneModel()

    def testUnregisterPathologyIdOne(self):
        model = self.createZoneModel()
        get_id_func = self.getGetPathologyIdFunc()
        id1_bound1 = (0, 3, 10, 20, 0)
        object_id1 = 1234
        mock_zone_id = 1 * 100000000 + (0 + 1) * 10000 + 0
        model.object_id2zone_id[object_id1] = {mock_zone_id}
        model.pathology[mock_zone_id].add(object_id1)
        model.bounds[object_id1] = {id1_bound1}
        actual_ids = get_id_func(model, [id1_bound1])
        self.assertEqual({object_id1}, actual_ids)


class TestRegisterPathologyAndGetIds(unittest.TestCase):

    def getRegisterFunc(self):
        from pathilico.app.zone import register_id as f
        return f

    def getGetFunc(self):
        from pathilico.app.zone import get_object_ids as f
        return f

    def createZoneModel(self):
        from pathilico.app.zone import ZoneModel
        return ZoneModel()

    def getRandomBound(self):
        max_int = 10000
        left, bottom = random.randint(0, max_int), random.randint(0, max_int)
        right = left + random.randint(0, max_int)
        top = bottom + random.randint(0, max_int)
        level = random.randint(0, 2)
        bound = (left, bottom, right, top, level)
        return bound

    def testRandomRegisterAndGet(self):
        register_func = self.getRegisterFunc()
        get_func = self.getGetFunc()
        zone_model = self.createZoneModel()
        bound1 = self.getRandomBound()
        bound2 = self.getRandomBound()
        object_id1 = 1234
        zone_model = register_func(
            zone_model, object_id1, [bound1, bound2]
        )
        actual = get_func(zone_model, [bound1])
        self.assertEqual({object_id1}, actual)
        actual = get_func(zone_model, [bound1, bound2])
        self.assertEqual({object_id1}, actual)
        actual = get_func(zone_model, [bound2])
        self.assertEqual({object_id1}, actual)

    def testRegisterAndGetForTwoItems(self):
        register_func = self.getRegisterFunc()
        get_func = self.getGetFunc()
        zone_model = self.createZoneModel()
        id1_bound1 = (0, 3, 10, 20, 0)
        id1_bound2 = (0, 1, 5, 10, 1)
        object_id1 = 1234
        id2_bound1 = (1000, 3000, 1040, 3040, 0)
        id2_bound2 = (250, 750, 260, 760, 1)
        object_id2 = 2345
        zone_model = register_func(
            zone_model, object_id1, [id1_bound1, id1_bound2]
        )
        actual = get_func(zone_model, [id1_bound1])
        self.assertEqual({object_id1}, actual)
        zone_model = register_func(
            zone_model, object_id2, [id2_bound1, id2_bound2]
        )
        actual = get_func(zone_model, [id2_bound2])
        self.assertEqual({object_id2}, actual)

