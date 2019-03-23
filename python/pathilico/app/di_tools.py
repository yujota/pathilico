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
"""This tool is used to make interface and store dependency injection"""
INJECTED_METHODS = dict()
DECLARED_METHODS = set()


def is_interface(name, bases, attrs):
    if len(name) >= 9:
        if name[:9] == "Interface":
            return True
    else:
        return False


def lazy_load(name):
    fs = [None]

    def func(*args, **kwargs):
        f = fs[0]
        if f is None:
            f = INJECTED_METHODS.get(name, None)
            if f is None:
                raise NotImplementedError(name)
            else:
                fs[0] = f
                return f(*args, **kwargs)
        else:
            return f(*args, **kwargs)
    return func


class NotDeclaredError(Exception):
    pass


class RegisterDeclaredMethod(type):

    def __new__(meta, name, bases, attrs):
        if is_interface(name, bases, attrs):
            pass
        else:
            for k in DECLARED_METHODS:
                attrs[k] = lazy_load(k)
        cls = super().__new__(meta, name, bases, attrs)
        return cls


class InterfaceBase(object, metaclass=RegisterDeclaredMethod):

    @staticmethod
    def register(func):
        f_name = func.__name__
        if callable(func) and f_name in DECLARED_METHODS:
            INJECTED_METHODS[f_name] = func
        else:
            msg = "{} is not declared in interface".format(f_name)
            raise NotDeclaredError(msg)

    @staticmethod
    def register_as(func, name):
        if callable(func) and name in DECLARED_METHODS:
            INJECTED_METHODS[name] = func
        else:
            msg = "{} is not declared in interface".format(name)
            raise NotDeclaredError(msg)


def declare_method(func):
    """Used as decorator"""
    DECLARED_METHODS.add(func.__name__)
    return func
