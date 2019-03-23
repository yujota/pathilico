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


class TestLayerControl(unittest.TestCase):

    @staticmethod
    def _getLayerListCls():
        from pathilico.pygletelm.window import LayerList as cls
        return cls

    @staticmethod
    def _getLayerCls():
        from pathilico.pygletelm.window import Layer as cls
        return cls

    def test_layer_order(self):
        LayerList = self._getLayerListCls()
        LayerCls = self._getLayerCls()

        class MockLayer(LayerList):
            Zero = LayerCls()
            First = LayerCls()
            Second = LayerCls()

        self.assertIsInstance(MockLayer.Zero, int)
        self.assertEqual(MockLayer.Zero, 0)
        self.assertEqual(MockLayer.First, 1)
        self.assertEqual(MockLayer.Second, 2)


class TestActualClass(unittest.TestCase):

    @staticmethod
    def _getPrimitiveTextLabelCls():
        from pathilico.pygletelm.window import PrimitiveTextLabel as cls
        return cls

    @staticmethod
    def _getPrimitiveImageCls():
        from pathilico.pygletelm.window import PrimitiveImage as cls
        return cls

    def test_class_eq(self):
        Text = self._getPrimitiveTextLabelCls()
        Image = self._getPrimitiveImageCls()
        mock_text = Text(x=100, y=100, text="hoge")
        mock_img = Image(x=100, y=100, image="Hoge")
        self.assertNotEqual(mock_img.__class__, mock_text.__class__)


class TestNestedView(unittest.TestCase):

    @staticmethod
    def _getViewCls():
        from pathilico.pygletelm.window import View as cls
        return cls

    @staticmethod
    def _getWindowObject():
        from pathilico.pygletelm.window import WindowObject as cls
        return cls

    def test_merge_nested_view(self):
        View = self._getViewCls()
        WinObj = self._getWindowObject()
        v1 = View(WinObj(events=[123]))
        v2 = View(WinObj(events=[234]))
        v3 = View(v1, v2)
        self.assertEqual(v3.events, [123, 234])


if __name__ == "__main__":
    unittest.main()
