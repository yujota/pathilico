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
import time

import pathilico.pygletelm.backend as backend
import pathilico.pygletelm.effect as effect
import pathilico.pygletelm.window as window_api


class MockMsg(object):

    def __init__(self, **kwargs):
        self.keys = list(kwargs.keys())
        for k, v, in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        r = " ".join(
            ["{}: {}".format(k, getattr(self, k)) for k in self.keys]
        )
        return r


def get_mock_backend(
        init_func=None, view_func=None, update_func=None, sub_func=None):
    def mock_init():
        return 0, effect.NO_COMMANDS

    def mock_update(msg, model):
        print(msg)
        return model, effect.NO_COMMANDS
    mock_view = lambda m: window_api.View()
    mock_subscriptions = lambda m: effect.NO_SUBSCRIPTIONS
    init_func = init_func or mock_init
    view_func = view_func or mock_view
    update_func = update_func or mock_update
    sub_func = sub_func or mock_subscriptions
    b = backend.Backend(
        init=init_func, view=view_func, update=update_func,
        subscriptions=sub_func
    )
    return b


def functional_test_notify_every_sec():
    flag = [0]
    s1 = effect.notify_every(MockMsg, dict(text="s1"), 1)
    s2 = effect.notify_every(MockMsg, dict(text="s2"), 2)
    s3 = effect.notify_once(MockMsg, dict(text="Notify once"), 3)
    s4 = effect.notify_every(MockMsg, dict(text="s4"), 1, until=4)
    s5 = effect.notify_every(MockMsg, dict(text="s5"), 1, wait=5, until=9)

    def mock_sub(model):
        if flag[0] is 0:
            return effect.Subscriptions(s1, s3, effect.Subscriptions(s4), s5)
        if flag[0] is 1:
            return effect.Subscriptions(s1, s2, s3, s4, s5)
        if flag[0] is 2:
            return effect.Subscriptions(s2, s3, s4, s5)
    b_end = get_mock_backend(sub_func=mock_sub)
    handler = b_end.effect_executor
    for i in range(50):
        time.sleep(0.1)
        handler.collect_sub_msg(0.5)
    print("=================================")
    flag[0] = 1
    for i in range(60):
        time.sleep(0.1)
        handler.collect_sub_msg(0.5)
    print("=================================")
    flag[0] = 2
    for i in range(50):
        time.sleep(0.1)
        handler.collect_sub_msg(0.5)


if __name__ == "__main__":
    functional_test_notify_every_sec()



