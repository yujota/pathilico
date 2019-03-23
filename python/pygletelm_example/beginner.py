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
"""Basic counter app

This program is inspired by Elm (https://elm-lang.org/)
"""
from pathilico.app.views.color import Colors
from pathilico.pygletelm.backend import beginner_program
from pathilico.pygletelm.window \
    import View, LayerList, Layer, button, box_with_text
from pathilico.pygletelm.message import UnionMessage, Message


Model = int


class Msg(UnionMessage):
    Increment = Message()
    Decrement = Message()


# Msg -> Model -> Model
def update(msg, model):
    if msg == Msg.Increment:
        return model + 1
    elif msg == Msg.Decrement:
        return model - 1
    else:
        return model


class Layers(LayerList):
    Bottom = Layer()
    Top = Layer()


# Model -> View Msg
def view(model):
    return View(
        box_with_text(
            x=50, y=350, width=350, height=100, color=Colors.Primary.Cyan,
            layer=Layers.Bottom, text="Count: {}".format(model)
        ),
        button(
            event_msg=Msg.Increment, text="Plus", font_color=Colors.Accent.Pink,
            x=50, y=150, width=150, height=100
        ),
        button(
            event_msg=Msg.Decrement, text="Minus",
            font_color=Colors.Accent.Cyan,
            x=250, y=150, width=150, height=100
        )
    )


if __name__ == "__main__":
    beginner_program(
        model=0,
        view=view,
        update=update
    )
