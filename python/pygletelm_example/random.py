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
"""Random example app

This program is inspired by Elm (https://elm-lang.org/)
"""
from pathilico.pygletelm.window \
    import View, simple_text_label, button
from pathilico.pygletelm.backend import program
from pathilico.app.views.color import Colors
from pathilico.pygletelm.effect import random_sample, Commands, Subscriptions
from pathilico.pygletelm.message import UnionMessage, Message


Model = int


def init_model():
    return Model(1), Commands()


class Msg(UnionMessage):
    Roll = Message()
    NewFace = Message("result")


def view(model):
    return View(
        simple_text_label(200, 200, text="{}".format(model)),
        button(
            event_msg=Msg.Roll, x=150, y=100, width=100, height=50,
            text="Roll!!", font_color=Colors.PrimaryText
        )
    )


def subscriptions(model):
    return Subscriptions()


def update(msg, model):
    if msg == Msg.Roll:
        return model, Commands(
            random_sample(population=(1, 2, 3, 4, 5, 6), k=1, msg=Msg.NewFace)
        )
    elif msg == Msg.NewFace:
        return msg.result[0], Commands()
    else:
        return model, Commands()


if __name__ == "__main__":
    program(
        init=init_model,
        update=update,
        view=view,
        subscriptions=subscriptions
    )
