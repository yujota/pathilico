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
import time
import random


class TestUnionMessage(unittest.TestCase):

    @staticmethod
    def _getTargetCls():
        from pathilico.pygletelm.message import UnionMessage as cls
        return cls


    @staticmethod
    def _getMessageCls():
        from pathilico.pygletelm.message import Message as cls
        return cls

    def test_instance_eq(self):
        MsgCls = self._getMessageCls()

        class MockMsg(self._getTargetCls()):
            Hoge = MsgCls()
            Fuga = MsgCls("foo")
            Piyo = MsgCls("foo", "bar")

        hoge_ins1 = MockMsg.Hoge()
        hoge_ins2 = MockMsg.Hoge()
        self.assertTrue(hoge_ins1 == MockMsg.Hoge)
        self.assertTrue(hoge_ins1 == hoge_ins2)
        self.assertFalse(hoge_ins1 == MockMsg.Fuga)
        self.assertFalse(hoge_ins1 == MockMsg.Piyo)

    def test_attr_access(self):
        MsgCls = self._getMessageCls()

        class MockMsg(self._getTargetCls()):
            Piyo = MsgCls("foo", "bar")

        piyo_ins = MockMsg.Piyo(123, 234)
        self.assertTrue(hasattr(piyo_ins, "foo"))
        self.assertTrue(hasattr(piyo_ins, "bar"))
        self.assertEqual(piyo_ins.foo, 123)
        self.assertEqual(piyo_ins.bar, 234)


def create_msg_tuple():
    Hoge = 0
    Fuga = 1
    Piyo = 2
    Msgs = (Hoge, Fuga, Piyo)
    start = time.time()
    r = list()
    mock_value = (103, 23, 434)
    for _ in range(100000):
        m_ind = random.sample(range(3), 1)[0]
        m = Msgs[m_ind], mock_value[:m_ind+1]
        r.append(m)
    return time.time() - start


def create_msg_core():
    MsgCls = TestUnionMessage._getMessageCls()
    class MockMsg(TestUnionMessage._getTargetCls()):
        Hoge = MsgCls()
        Fuga = MsgCls("foo")
        Piyo = MsgCls("foo", "bar")
    Msgs = (MockMsg.Hoge, MockMsg.Fuga, MockMsg.Piyo)
    r = list()
    mock_value = (103, 23, 434)
    start = time.time()
    for _ in range(100000):
        m_ind = random.sample(range(3), 1)[0]
        m = Msgs[m_ind](*mock_value[:m_ind+1])
        r.append(m)
    return time.time() - start


class SpeedTest(unittest.TestCase):

    def test_speed(self):
        tuple_time = create_msg_tuple()
        core_time = create_msg_core()
        print(tuple_time, core_time, core_time - tuple_time)


if __name__ == "__main__":
    unittest.main()
