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


class Message(object):  # Mock class
    def __init__(self, *args):
        self.args = args

    def __call__(self, *args, **kwargs):
        return self


class MetaEq(type):

    def __eq__(cls, other):
        return getattr(cls, "identity", 0) == other


class MessageBase(object, metaclass=MetaEq):
    identity = 0
    __slots__ = tuple()

    def __init__(self, *args, **kwargs):
        d = dict(zip(self.__slots__, args), **kwargs)
        for k in self.__slots__:
            setattr(self, k, d[k])

    def __eq__(self, other):
        return self.identity == other

    def __str__(self):
        msg = "<[ {0} : {1} ]>".format(
            getattr(self, "__class__"),
            str(["{}: {}".format(k, getattr(self, k)) for k in self.__slots__])
        )
        return msg


class MetaMessage(type):  # Meta class
    id_count = 100

    def __new__(meta, name, bases, class_dict):
        new_cls_dict = dict()
        for key, value in class_dict.items():
            if isinstance(value, Message):
                new_cls_dict[key] = type(
                    key, (MessageBase, ),
                    {"__slots__": value.args, "identity": meta.id_count}
                )
                meta.id_count += 1
        cls = type.__new__(meta, name, bases, new_cls_dict)
        return cls


class UnionMessage(object, metaclass=MetaMessage):
    Ok = Message("value")
    Err = Message("error")
    WindowResized = Message("width", "height")
    WindowApiChangeCursorIcon = Message("cursor")


Ok = UnionMessage.Ok
Err = UnionMessage.Err
WindowResized = UnionMessage.WindowResized
WindowApiChangeCursor = UnionMessage.WindowApiChangeCursorIcon

