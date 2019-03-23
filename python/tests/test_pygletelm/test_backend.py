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


class TestFunctionRegistry(unittest.TestCase):

    @staticmethod
    def _getTargetCls():
        from pathilico.pygletelm.backend import FunctionRegistry as cls
        return cls

    def test_iter(self):
        FunctionRegistry = self._getTargetCls()

        obj = FunctionRegistry()

        def sample(*args): return None

        obj.register(sample)

        for f in obj:
            self.assertIs(f, sample)


class TestProxyBeginnerBackend(unittest.TestCase):

    @staticmethod
    def _getTargetCls():
        from pathilico.pygletelm.backend import StateProxyForBeginnerBackend as cls
        return cls

    def _getMockStateCls(self):

        class MockState(object):
            def __init__(self, model, view, update):
                self.model, self.view, self.update = model, view, update
        return MockState

    def test_property(self):
        MS = self._getMockStateCls()

        def mock_update(msg, model):
            print("Mock update", msg, model)
            return model + 1

        def mock_view(model):
            print("Mock view", model)

        mock_state = MS(0, mock_view, mock_update)
        proxy = self._getTargetCls()(mock_state)
        self.assertEqual(proxy.model, 0)
        proxy.model = 3
        self.assertEqual(proxy.model, 3)
        proxy.push_message("Increment")
        self.assertEqual(proxy.model, 4)




if __name__ == "__main__":
    unittest.main()
