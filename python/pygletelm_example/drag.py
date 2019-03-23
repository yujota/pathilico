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
"""Drag example app

This program is inspired by Elm (https://elm-lang.org/)
"""
from pathilico.app.views.color import Colors
from pathilico.pygletelm.backend import beginner_program
from pathilico.pygletelm.window import View, box_with_text, mouse_drag_area
from pathilico.pygletelm.message import Message, UnionMessage


class Model(object):
    def __init__(self):
        self.x = 100
        self.y = 100
        self.dragging = False

    def __str__(self):
        return "x: {}, y: {}".format(self.x, self.y)

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        else:
            return False


class Msg(UnionMessage):
    Move = Message("dx", "dy")
    DragStart = Message("x", "y")
    DragEnd = Message("x", "y")


# Msg -> Model -> ( Model, Cmd Msg
def update(msg, model):
    if msg == Msg.Move:
        model.x, model.y = model.x + msg.dx, model.y + msg.dy
        return model
    elif msg == Msg.DragStart:
        model.dragging = True
        return model
    elif msg == Msg.DragEnd:
        model.dragging = False
        return model
    else:
        return model


def view(model):
    return View(
        box_with_text(
            x=model.x, y=model.y, width=100, height=100, text="Drag Me",
            color=Colors.Primary.Cyan, font_color=Colors.WhiteText
        ),
        mouse_drag_area(
            x=model.x, y=model.y, width=100, height=100, message=Msg.Move,
            drag_start_msg=Msg.DragStart, drag_end_msg=Msg.DragEnd
        ),
        box_with_text(
            x=0, y=0, width=640, height=50,
            text="Now dragging" if model.dragging else "Waiting",
            color=Colors.Primary.Pink, font_color=Colors.WhiteText
        ),
    )


if __name__ == "__main__":
    beginner_program(
        model=Model(),
        view=view,
        update=update
    )

