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


class TestTheOneDiff(unittest.TestCase):

    @staticmethod
    def _getPayloadTagCls():
        from pathilico.pygletelm.cache import PayloadTag as cls
        return cls

    @staticmethod
    def _getPayloadTypesCls():
        from pathilico.pygletelm.cache import PayloadTypes as cls
        return cls

    @staticmethod
    def _getCachedObjectCls():
        from pathilico.pygletelm.cache import CachedObject as cls
        return cls

    def test_diff(self):
        PTypes = self._getPayloadTypesCls()
        the_one = PTypes.the_one
        CachedObjCls = self._getCachedObjectCls()

        class MockObj(CachedObjCls):
            _payload_attrs = ("message", )

            def __init__(self, message):
                self.message = message
                super().__init__()

        mock_ins1 = MockObj("Hello")
        mock_ins2 = MockObj("World")
        mock_ins3 = MockObj("Foo")
        mock_ins4 = MockObj("Bar")
        mock_ins5 = MockObj("Bar")

        olds = [mock_ins1, mock_ins2]
        news = [mock_ins3]

        new_actual, update_actual, delete_actual = the_one.diff(
            [o.tag for o in olds], [n.tag for n in news]
        )
        self.assertEqual(new_actual, [mock_ins3.tag.id])
        self.assertEqual(delete_actual, [mock_ins1.tag.id, mock_ins2.tag.id])

        olds = [mock_ins1]
        news = [mock_ins1]

        new_actual, update_actual, delete_actual = the_one.diff(
            [o.tag for o in olds], [n.tag for n in news]
        )
        self.assertEqual(new_actual, list())
        self.assertEqual(delete_actual, list())

        olds = [mock_ins4]
        news = [mock_ins5]

        new_actual, update_actual, delete_actual = the_one.diff(
            [o.tag for o in olds], [n.tag for n in news]
        )
        self.assertEqual(new_actual, list())
        self.assertEqual(delete_actual, list())

    def test_id_alloc(self):
        PTypes = self._getPayloadTypesCls()
        the_one = PTypes.the_one
        CachedObjCls = self._getCachedObjectCls()

        class MockObj(CachedObjCls):
            _payload_attrs = ("message", )

            def __init__(self, message):
                self.message = message
                super().__init__()


        mock_ins1 = MockObj("Hello")
        mock_ins2 = MockObj("World")

        self.assertEqual(mock_ins1.tag.id, None)
        self.assertEqual(mock_ins2.tag.id, None)

        self.assertTrue(mock_ins1.tag.p_type is mock_ins2.tag.p_type)
        self.assertFalse(mock_ins1.tag is mock_ins2.tag)

        m1_id = mock_ins1.tag.get_identity()
        self.assertEqual(mock_ins2.tag.id, None)
        m2_id = mock_ins2.tag.get_identity()

        self.assertNotEqual(m1_id, m2_id)

        self.assertNotEqual(mock_ins1.tag.id, None)
        self.assertNotEqual(mock_ins2.tag.id, None)
        self.assertNotEqual(mock_ins1.tag.id, mock_ins2.tag.id)
        self.assertNotIn(m1_id, the_one.unused_ids)

        mock_ins1.done()

        self.assertIn(m1_id, the_one.unused_ids)
        self.assertNotIn(m2_id, the_one.unused_ids)
        mock_ins2.done()


class TestUniqueByClass(unittest.TestCase):

    @staticmethod
    def _getPayloadTypesCls():
        from pathilico.pygletelm.cache import PayloadTypes as cls
        return cls

    @staticmethod
    def _getCachedObjectCls():
        from pathilico.pygletelm.cache import CachedObject as cls
        return cls

    def test_diff(self):
        PTypes = self._getPayloadTypesCls()
        unique_by_class = PTypes.unique_by_class
        CachedObjCls = self._getCachedObjectCls()

        class MockObjOne(CachedObjCls):
            _payload_attrs = ("message", )
            _payload_type = unique_by_class

            def __init__(self, message):
                self.message = message
                super().__init__()

        class MockObjTwo(MockObjOne):
            pass

        mock_ins1 = MockObjOne("Hello")
        mock_ins2 = MockObjOne("World")
        mock_ins3 = MockObjTwo("Foo")

        olds = [mock_ins1]
        news = [mock_ins2]

        new_actual, update_actual, delete_actual = unique_by_class.diff(
            [o.tag for o in olds], [n.tag for n in news]
        )
        self.assertIsInstance(new_actual, list)
        self.assertIsInstance(new_actual[0], int)
        self.assertEqual(new_actual, [mock_ins2.tag.id])
        self.assertEqual(delete_actual, [mock_ins1.tag.id])

        olds = [mock_ins1]
        news = [mock_ins1, mock_ins3]

        new_actual, update_actual, delete_actual = unique_by_class.diff(
            [o.tag for o in olds], [n.tag for n in news]
        )
        self.assertEqual(delete_actual, list())
        self.assertEqual(new_actual, [mock_ins3.tag.id])


class TestUniqueByClassWithReplaceablePayload(unittest.TestCase):

    @staticmethod
    def _getPayloadTypesCls():
        from pathilico.pygletelm.cache import PayloadTypes as cls
        return cls

    @staticmethod
    def _getCachedObjectCls():
        from pathilico.pygletelm.cache import CachedObject as cls
        return cls

    def test_diff(self):
        PTypes = self._getPayloadTypesCls()
        tag_type = PTypes.unique_by_class_with_replaceable_payload
        CachedObjCls = self._getCachedObjectCls()

        class MockObj(CachedObjCls):
            _payload_attrs = ("message", "value")
            _payload_replaceable_attrs = ("value", )
            _payload_type = tag_type

            def __init__(self, message, value):
                self.message = message
                self.value = value
                super().__init__()

        mock_ins1 = MockObj("Foo", 123)
        mock_ins2 = MockObj("Bar", 234)
        mock_ins3 = MockObj("Foo", 345)

        olds = [mock_ins1]
        news = [mock_ins2]

        new_actual, update_actual, delete_actual = tag_type.diff(
            [o.tag for o in olds], [n.tag for n in news]
        )
        self.assertEqual(new_actual, [mock_ins2.tag.id])
        self.assertEqual(delete_actual, [mock_ins1.tag.id])

        olds = [mock_ins1]
        news = [mock_ins3]

        new_actual, update_actual, delete_actual = tag_type.diff(
            [o.tag for o in olds], [n.tag for n in news]
        )
        ins1_id = mock_ins1.identity
        self.assertEqual(new_actual, list())
        self.assertEqual(delete_actual, list())
        self.assertEqual(update_actual, {ins1_id: {"value": 345}})



class TestUniqueByClassAndPayload(unittest.TestCase):

    @staticmethod
    def _getPayloadTypesCls():
        from pathilico.pygletelm.cache import PayloadTypes as cls
        return cls

    @staticmethod
    def _getCachedObjectCls():
        from pathilico.pygletelm.cache import CachedObject as cls
        return cls

    def test_diff(self):
        PTypes = self._getPayloadTypesCls()
        unique_by_class_and_payload = PTypes.unique_by_class_and_payload
        CachedObjCls = self._getCachedObjectCls()

        class MockObjOne(CachedObjCls):
            _payload_attrs = ("message", )
            _payload_type = unique_by_class_and_payload

            def __init__(self, message):
                self.message = message
                super().__init__()

        mock_ins1 = MockObjOne("Hello")
        mock_ins2 = MockObjOne("World")
        mock_ins3 = MockObjOne("Hello")

        olds = [mock_ins1]
        news = [mock_ins2]

        new_actual, update_actual, delete_actual = \
            unique_by_class_and_payload.diff(
                [o.tag for o in olds], [n.tag for n in news]
            )
        self.assertIsInstance(new_actual, list)
        self.assertIsInstance(new_actual[0], int)
        self.assertEqual(new_actual, [mock_ins2.tag.id])
        self.assertEqual(delete_actual, [mock_ins1.tag.id])

        olds = [mock_ins1]
        news = [mock_ins1, mock_ins2]

        new_actual, update_actual, delete_actual = \
            unique_by_class_and_payload.diff(
                [o.tag for o in olds], [n.tag for n in news]
            )
        self.assertEqual(new_actual, [mock_ins2.tag.id])
        self.assertEqual(delete_actual, list())

        olds = [mock_ins1]
        news = [mock_ins2]

        new_actual, update_actual, delete_actual = \
            unique_by_class_and_payload.diff(
                [o.tag for o in olds], [n.tag for n in news]
            )
        self.assertEqual(new_actual, [mock_ins2.tag.id])
        self.assertEqual(delete_actual, [mock_ins1.tag.id])

        olds = [mock_ins1]
        news = [mock_ins3]

        new_actual, update_actual, delete_actual = \
            unique_by_class_and_payload.diff(
                [o.tag for o in olds], [n.tag for n in news]
            )
        self.assertEqual(new_actual, list())
        self.assertEqual(delete_actual, list())


class TestUniqueByClassAndReplaceablePayload(unittest.TestCase):

    @staticmethod
    def _getPayloadTypesCls():
        from pathilico.pygletelm.cache import PayloadTypes as cls
        return cls

    @staticmethod
    def _getCachedObjectCls():
        from pathilico.pygletelm.cache import CachedObject as cls
        return cls

    def test_diff(self):
        PTypes = self._getPayloadTypesCls()
        tag_type = PTypes.unique_by_class_and_replaceable_payload
        CachedObjCls = self._getCachedObjectCls()

        class MockObj(CachedObjCls):
            _payload_attrs = ("message", "value")
            _payload_replaceable_attrs = ("value", )
            _payload_type = tag_type

            def __init__(self, message, value):
                self.message = message
                self.value = value
                super().__init__()

        mock_ins1 = MockObj("Foo", 123)
        mock_ins2 = MockObj("Bar", 234)
        mock_ins3 = MockObj("Foo", 345)

        olds = [mock_ins1]
        news = [mock_ins1, mock_ins2]

        new_actual, update_actual, delete_actual = tag_type.diff(
            [o.tag for o in olds], [n.tag for n in news]
        )
        self.assertEqual(new_actual, [mock_ins2.tag.id])
        self.assertEqual(delete_actual, list())

        olds = [mock_ins1]
        news = [mock_ins3]

        new_actual, update_actual, delete_actual = tag_type.diff(
            [o.tag for o in olds], [n.tag for n in news]
        )
        ins1_id = mock_ins1.identity
        self.assertEqual(new_actual, list())
        self.assertEqual(delete_actual, list())
        self.assertEqual(update_actual, {ins1_id: {"value": 345}})

        olds = [mock_ins1]
        news = [mock_ins1, mock_ins3]

        new_actual, update_actual, delete_actual = tag_type.diff(
            [o.tag for o in olds], [n.tag for n in news]
        )
        self.assertEqual(new_actual, [mock_ins3.tag.id])
        self.assertEqual(delete_actual, list())
        self.assertEqual(update_actual, dict())

    def test_diff_by_update(self):
        PTypes = self._getPayloadTypesCls()
        tag_type = PTypes.unique_by_class_and_replaceable_payload
        CachedObjCls = self._getCachedObjectCls()

        class MockObj(CachedObjCls):
            _payload_attrs = ("message", "value")
            _payload_replaceable_attrs = ("value", )
            _payload_type = tag_type

            def __init__(self, message, value):
                self.message = message
                self.value = value
                super().__init__()

        mock_ins1 = MockObj("Foo", 123)
        mock_ins2 = MockObj("Foo", 234)
        mock_ins3 = MockObj("Foo", 345)
        mock_ins4 = MockObj("Foo", 456)

        olds = []
        news = [mock_ins1]
        new_actual, update_actual, delete_actual = tag_type.diff(
            [o.tag for o in olds], [n.tag for n in news]
        )
        self.assertEqual(new_actual, [mock_ins1.tag.id])
        self.assertEqual(update_actual, dict())
        self.assertEqual(delete_actual, list())

        olds = [mock_ins1]
        news = [mock_ins2]
        mock_ins1_id = mock_ins1.identity
        new_actual, update_actual, delete_actual = tag_type.diff(
            [o.tag for o in olds], [n.tag for n in news]
        )
        self.assertEqual(new_actual, [])
        self.assertEqual(update_actual, {mock_ins1_id: dict(value=234)})
        self.assertEqual(delete_actual, list())

        olds = [mock_ins1]
        news = [mock_ins3]
        new_actual, update_actual, delete_actual = tag_type.diff(
            [o.tag for o in olds], [n.tag for n in news]
        )
        self.assertEqual(new_actual, [])
        self.assertEqual(delete_actual, list())
        self.assertEqual(update_actual, {mock_ins1_id: dict(value=345)})

    def test_diff_by_update_with_several_class(self):
        PTypes = self._getPayloadTypesCls()
        tag_type = PTypes.unique_by_class_and_replaceable_payload
        CachedObjCls = self._getCachedObjectCls()

        class MockObj(CachedObjCls):
            _payload_attrs = ("message", "value")
            _payload_replaceable_attrs = ("value", )
            _payload_type = tag_type

            def __init__(self, message, value):
                self.message = message
                self.value = value
                super().__init__()

        class MockImage(CachedObjCls):
            _payload_attrs = ("message", "image")
            _payload_replaceable_attrs = ("image", )
            _payload_type = tag_type

            def __init__(self, message, image):
                self.message = message
                self.image = image
                super().__init__()

        class MockComplex(CachedObjCls):
            _payload_attrs = ("message", "image", "value")
            _payload_replaceable_attrs = ("image", "value")
            _payload_type = tag_type

            def __init__(self, message, image, value):
                self.message = message
                self.image = image
                self.value = value
                super().__init__()

        mock_ins1 = MockObj("Foo", 123)
        mock_ins2 = MockObj("Foo", 234)
        mock_ins3 = MockImage("Foo", "Sample image")
        mock_ins4 = MockComplex("Foo", "Sample image", 483)

        olds = [mock_ins1, mock_ins3]
        news = [mock_ins2, mock_ins4]
        mock_ins1_id = mock_ins1.identity
        new_actual, update_actual, delete_actual = tag_type.diff(
            [o.tag for o in olds], [n.tag for n in news]
        )
        self.assertEqual(new_actual, [mock_ins4.identity])
        self.assertEqual(update_actual, {mock_ins1_id: dict(value=234)})
        self.assertEqual(delete_actual, [mock_ins3.identity])


if __name__ == "__main__":
    unittest.main()
