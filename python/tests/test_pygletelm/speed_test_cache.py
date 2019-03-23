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
import random
from profilehooks import profile

import pathilico.pygletelm.cache as cache


P_TYPE = cache.PayloadTypes.all[4]


class MockClass(cache.CachedObject):
    _payload_attrs = ("a", "b", "c", "d", "e")
    _payload_replaceable_attrs = ("a", "b", "c")

    def __init__(self):
        self.a, self.b, self.c, self.d, self.e = random.sample(range(100), 5)
        super().__init__()


def get_mocks(p_type=P_TYPE):
    r = list()
    class M(MockClass):
        _payload_type = p_type

    for _ in range(100000):
        r.append(get_tag(M()))
    return r


def main():
    print(P_TYPE)
    mocks = get_mocks()
    measure(mocks)


def get_tag(a):
    return a.tag


@profile
def measure(mocks):
    for i in range(5000):
        m1, m2 = mocks[20*i:20*i+10], mocks[20*i+10:20*i+20]
        cache.diff(m1, m2)


if __name__ == "__main__":
    main()
