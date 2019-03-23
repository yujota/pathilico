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


class TestAddPoint(unittest.TestCase):

    def getTargetFunc(self):
        from pathilico.app.annotation import add_point as f
        return f

    def createAnnotationModel(self):
        from pathilico.app.annotation import AnnotationModel as Cls
        return Cls()

    def testAddPoint(self):
        add_point = self.getTargetFunc()
        model = self.createAnnotationModel()
        model, point_id, point_data = add_point(
            model, 100, 100, 1, 100000, "hoge.svs"
        )
        self.assertEqual({point_id}, set(model.points.keys()))
        point_data = model.points[point_id]
        self.assertEqual((100, 100, 1, (100, 100000-100, 1)), point_data)


class TestAddArea(unittest.TestCase):

    def getTargetFunc(self):
        from pathilico.app.annotation import add_area as f
        return f

    def createAnnotationModel(self):
        from pathilico.app.annotation import AnnotationModel as Cls
        return Cls()

    def testAddPoint(self):
        add_area = self.getTargetFunc()
        model = self.createAnnotationModel()

        mock_closed_vs = (
            100, 100, 120, 140, 150, 180, 200, 250, 170, 300, 130, 170
        )
        mock_lv0 = 1000
        mock_category_id = 101
        model, flag, area_id, actual = add_area(
            model, closed_vs=mock_closed_vs, category_id=mock_category_id,
            lv0_height=mock_lv0, display_name="Hoge", reduce_points=False
        )
        self.assertTrue(flag)
        self.assertTrue(100, actual.x)
        self.assertTrue(100, actual.y)
        self.assertTrue(100, actual.width)
        self.assertTrue(200, actual.height)


class TestConvertOpenGLCoordinates(unittest.TestCase):
    def getTargetFunc(self):
        from pathilico.app.annotation \
            import convert_opengl_coordinates2ga_query_coordinates as f
        return f

    def testConvertPointOne(self):
        func = self.getTargetFunc()
        desired = (300, 1024-400)
        actual = func(0, 0, 1, 300, 400, 1024)
        self.assertEqual(desired, actual)

    def testConvertPointTwo(self):
        func = self.getTargetFunc()
        desired = (100, 1024-100)
        actual = func(0, 0, 4, 400, 400, 1024)
        self.assertEqual(desired, actual)


class TestUpdateGroupedAnnotationQuery(unittest.TestCase):
    def getTargetFunc(self):
        from pathilico.app.annotation \
            import update_grouped_annotation_query as f
        return f

    def getGroupedAnnotationRecordCls(self):
        from pathilico.app.annotation \
            import GroupedAnnotationRecord as Cls
        return Cls

    def getGroupedAnnotationImageQuery(self):
        from pathilico.app.annotation \
            import GroupedAnnotationImageQuery as Cls
        return Cls

    def getPointRecordCls(self):
        from pathilico.app.annotation \
            import PointAnnotationRecord as Cls
        return Cls

    def getAreaRecordCls(self):
        from pathilico.app.annotation \
            import AreaAnnotationRecord as Cls
        return Cls

    def testUpdateGAByAddingPoint(self):
        GaCls = self.getGroupedAnnotationRecordCls()
        GaQueryCls = self.getGroupedAnnotationImageQuery()
        PointCls = self.getPointRecordCls()
        func = self.getTargetFunc()
        input_query = GaQueryCls(list(), list(), (1024, 1024))
        mock_point1 = PointCls(
            x=100, y=200, category_id=100, serialized_data=b"\x03"
        )
        mock_point2 = PointCls(
            x=150, y=400, category_id=200, serialized_data=b"\x03"
        )
        mock_point_id1 = b"\x00"
        mock_point_id2 = b"\x01"
        mock_points = {mock_point_id1: mock_point1, mock_point_id2: mock_point2}
        mock_colors = {100: (0, 1, 2, 3), 200: (1, 2, 3, 4)}
        input_gar = GaCls(
            x=0, y=0, level=0, points={mock_point_id1, mock_point_id2},
            areas=set(), query=input_query
        )
        result = func(
            input_gar, points=mock_points, areas=dict(),
            category_id2color=mock_colors,
            level_downsamples=(1, 4, 16)
        )
        actual = result.query
        desired_points = [
            (100, 1024-200, (0,1,2,3)), (150, 1024-400, (1,2,3,4))
        ]
        self.assertEqual(set(desired_points), set(actual.points))

    def testUpdateGAByAddingArea(self):
        GaCls = self.getGroupedAnnotationRecordCls()
        GaQueryCls = self.getGroupedAnnotationImageQuery()
        AreaCls = self.getAreaRecordCls()
        func = self.getTargetFunc()
        input_query = GaQueryCls(list(), list(), (1024, 1024))
        mock_input_contour = (
            0, 0, 100, 100, 200, 150, 150, 300
        )
        mock_desired_contour = (
            0, 1024, 100, 1024-100, 200, 1024-150, 150, 1024-300
        )
        mock_area = AreaCls(
            x=0, y=0, width=200, height=300, triangulate_indices=tuple(),
            category_id=100, serialized_data=tuple(),
            contour=mock_input_contour

        )
        mock_area_id = b"\x00"
        mock_areas = {mock_area_id: mock_area}
        mock_colors = {100: (0, 1, 2, 3), 200: (1, 2, 3, 4)}
        input_gar = GaCls(
            x=0, y=0, level=0, points=set(),
            areas={mock_area_id}, query=input_query
        )
        result = func(
            input_gar, points=dict(), areas=mock_areas,
            category_id2color=mock_colors,
            level_downsamples=(1, 4, 16)
        )
        actual = result.query
        desired_polygon = (mock_desired_contour, mock_colors[100])
        self.assertEqual(desired_polygon, actual.polygons[0])


class TestConvertBytes(unittest.TestCase):

    def getBinarizerFunc(self):
        from pathilico.app.annotation \
            import convert_int_seq2bytes as f
        return f

    def getDeBinarizerFunc(self):
        from pathilico.app.annotation \
            import convert_bytes as f
        return f

    def testConvert(self):
        i2b = self.getBinarizerFunc()
        b2i = self.getDeBinarizerFunc()
        desired = (1, 2, 3, 4)
        flag, actual = b2i(i2b(desired))
        self.assertTrue(flag)
        self.assertEqual(desired, actual)


class TestAreaAnnotationSerialization(unittest.TestCase):

    def getSerializeFunc(self):
        from pathilico.app.annotation \
            import create_area_annotation_serialized_data as f
        return f

    def getDeserializeFunc(self):
        from pathilico.app.annotation \
            import create_area_annotation_record_from_serialized_data as f
        return f

    def getDeBinarizeFunc(self):
        from pathilico.app.annotation \
            import convert_bytes as f
        return f

    def getSerializedDataCls(self):
        from pathilico.app.annotation \
            import AreaAnnotationSerializedData as Cls
        return Cls

    def testSerialize(self):
        serializer = self.getSerializeFunc()
        SerializedCls = self.getSerializedDataCls()
        debinarize = self.getDeBinarizeFunc()
        x = 100
        y = 200
        width = 50
        height = 100
        counter = (0, 0, 30, 70, 50, 100)
        desired_contour = (0, 100, 30, 30, 50, 0)
        lv0_height = 1000
        category_id = 3
        triangulate_indices = (0, 1, 2)
        actual = serializer(
            x, y, width, height, counter, triangulate_indices, category_id,
            lv0_height
        )
        self.assertIsInstance(actual, SerializedCls)
        self.assertEqual(x, actual.x)
        self.assertEqual(lv0_height-y-height, actual.y)
        self.assertEqual(width, actual.width)
        self.assertEqual(height, actual.height)
        self.assertEqual(category_id, actual.category_id)
        self.assertEqual(
            triangulate_indices, debinarize(actual.triangulate_indices)[1]
        )
        self.assertEqual(
            desired_contour, debinarize(actual.contour)[1]
        )

    def testDeserialize(self):
        serializer = self.getSerializeFunc()
        deserializer = self.getDeserializeFunc()
        x = 100
        y = 200
        width = 50
        height = 100
        contour = (0, 0, 30, 70, 50, 100)
        lv0_height = 1000
        category_id = 3
        triangulate_indices = (0, 1, 2)
        serialized = serializer(
            x, y, width, height, contour, triangulate_indices, category_id,
            lv0_height
        )
        flag, actual = deserializer(serialized, lv0_height)
        self.assertTrue(flag)
        self.assertEqual(x, actual.x)
        self.assertEqual(y, actual.y)
        self.assertEqual(width, actual.width)
        self.assertEqual(height, actual.height)
        self.assertEqual(category_id, actual.category_id)
        self.assertEqual(
            triangulate_indices, actual.triangulate_indices
        )
        self.assertEqual(contour, actual.contour)


class TestGetBoundsForPoint(unittest.TestCase):

    def getTargetFunc(self):
        from pathilico.app.annotation import get_bounds_for_point as f
        return f

    def testGetBoundsForOrigin(self):
        func = self.getTargetFunc()
        offset = 4
        actual = func(0, 0, (1, 4, 16), offset=4)
        desired = [(-4, -4, 4, 4, 0), (-4, -4, 4, 4, 1), (-4, -4, 4, 4, 2)]
        self.assertEqual(desired, actual)

    def testGetBoundsForPointOne(self):
        func = self.getTargetFunc()
        ofs = 4  # offset
        actual = func(1600, 1600, (1, 4, 16), offset=ofs)
        desired = [
            (1600-ofs, 1600-ofs, 1600+ofs, 1600+ofs, 0),
            (400-ofs, 400-ofs, 400+ofs, 400+ofs, 1),
            (100-ofs, 100-ofs, 100+ofs, 100+ofs, 2)
        ]
        self.assertEqual(desired, actual)


class TestGetBoundsForArea(unittest.TestCase):

    def getTargetFunc(self):
        from pathilico.app.annotation import get_bounds_for_area as f
        return f

    def testGetBoundsForOrigin(self):
        func = self.getTargetFunc()
        w, h = 256, 1024
        actual = func(0, 0, w, h, (1, 4, 16))
        desired = [
            (0, 0, w, h, 0),
            (0, 0, w//4, h//4, 1),
            (0, 0, w//16, h//16, 2)
        ]
        self.assertEqual(desired, actual)

    def testGetBoundsForArea(self):
        func = self.getTargetFunc()
        x, y = 1600, 1600
        w, h = 256, 1024
        actual = func(x, y, w, h, (1, 4, 16))
        desired = [
            (1600, 1600, x+w, y+h, 0),
            (400, 400, 400+w//4, 400+h//4, 1),
            (100, 100, 100+w//16, 100+h/16, 2),
        ]
        self.assertEqual(desired, actual)
