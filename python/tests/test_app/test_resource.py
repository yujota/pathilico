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


class TestAddReservation(unittest.TestCase):
    def getTargetFunc(self):
        from pathilico.app.resource import add_reservation as f
        return f

    def createResourceModel(self):
        from pathilico.app.resource import ResourceModel
        m = ResourceModel()
        return m

    def testAddReservation(self):
        model = self.createResourceModel()
        func = self.getTargetFunc()
        mock_id = 1234
        mock_query = "read some"
        model = func(model, mock_id, mock_query)
        self.assertEqual({mock_id: mock_query}, model.queries)


class TestUpdateReservation(unittest.TestCase):
    def getTargetFunc(self):
        from pathilico.app.resource import update_reservation as f
        return f

    def createResourceModel(self):
        from pathilico.app.resource import ResourceModel
        m = ResourceModel()
        return m

    def testUpdateReservationCheckIfDeleteOldRequest(self):
        model = self.createResourceModel()
        func = self.getTargetFunc()
        mock_id = 1234
        mock_old_query = "read some"
        mock_new_query = "read other"
        model.queries[mock_id] = mock_old_query
        model.requesting.add(mock_id)
        model = func(model, mock_id, mock_new_query)
        self.assertEqual({mock_id: mock_new_query}, model.queries)
        self.assertEqual(set(), model.requesting)

    def testUpdateReservationCheckIfDoNothingForSameQuery(self):
        model = self.createResourceModel()
        func = self.getTargetFunc()
        mock_id = 1234
        mock_query = "read some"
        model.queries[mock_id] = mock_query
        model.requesting.add(mock_id)
        model = func(model, mock_id, mock_query)
        self.assertEqual({mock_id: mock_query}, model.queries)
        self.assertEqual({mock_id}, model.requesting)

    def testUpdateReservationCheckIfDeleteOldImage(self):
        model = self.createResourceModel()
        func = self.getTargetFunc()
        mock_id = 1234
        mock_old_query = "read some"
        mock_old_image = b"\x03"
        mock_new_query = "read other"
        model.queries[mock_id] = mock_old_query
        model.images[mock_id] = mock_old_image
        model = func(model, mock_id, mock_new_query)
        self.assertEqual({mock_id: mock_new_query}, model.queries)
        self.assertFalse(mock_id in model.images)


class TestCombinedResourceOperations(unittest.TestCase):
    def getAddReservationFunc(self):
        from pathilico.app.resource import add_reservation as f
        return f

    def getAddImageFunc(self):
        from pathilico.app.resource import add_image as f
        return f

    def getRequestQueries(self):
        from pathilico.app.resource import request_queries as f
        return f

    def createResourceModel(self):
        from pathilico.app.resource import ResourceModel
        m = ResourceModel()
        return m

    def testAddReserveAndRequestThenAddImage(self):
        add_reserve = self.getAddReservationFunc()
        add_image = self.getAddImageFunc()
        get_request = self.getRequestQueries()
        model = self.createResourceModel()
        mock_id = 1234
        mock_image = b"\x03"
        mock_query = "read some"
        model = add_reserve(model, mock_id, mock_query)
        model, r_ids, r_queries = get_request(model, [mock_id])
        self.assertEqual([mock_id], r_ids)
        self.assertEqual([mock_query], r_queries)
        self.assertEqual({mock_id}, model.requesting)
        model = add_image(model, mock_id, mock_query, mock_image)
        self.assertEqual(set(), model.requesting)
        self.assertTrue(mock_id in model.images)












