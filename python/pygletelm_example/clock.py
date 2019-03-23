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
"""Clock app

This program is inspired by Elm (https://elm-lang.org/)
The original code (for elm 0.18) is listed below
--------------------------------------------
import Html exposing (Html, program)
import Svg exposing (circle, line, svg)
import Svg.Attributes exposing (..)
import Time exposing (Time, second)


main =
  program { init = init, view = view, update = update, subscriptions = subs }


-- MODEL

type alias Model = Time


-- VIEW

view : Model -> Html Msg
view model =
  let
    angle =
      turns (Time.inMinutes model)

    handX =
      toString (50 + 40 * cos angle)

    handY =
      toString (50 + 40 * sin angle)
  in
    svg [ viewBox "0 0 100 100", width "300px" ]
      [ circle [ cx "50", cy "50", r "45", fill "#0B79CE" ] []
      , line [ x1 "50", y1 "50", x2 handX, y2 handY, stroke "#023963" ] []
      ]


-- UPDATE

type Msg
  = Tick Time


update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  case msg of
    Tick newTime ->
      (newTime, Cmd.none)


init : (Model, Cmd Msg)
init =
  (0, Cmd.none)


subs : Model -> Sub Msg
subs model =
  Time.every second Tick
"""
import math

from pathilico.pygletelm.window \
    import View, simple_circle, simple_line, LayerList, Layer
from pathilico.pygletelm.backend import program
from pathilico.app.views.color import Colors
from pathilico.pygletelm.effect import notify_every, Commands, Subscriptions
from pathilico.pygletelm.message import UnionMessage, Message


Model = float


def init_model():
    return Model(), Commands()


def get_angles_from_sec(sec):
    """Helper"""
    degree = (int(sec) % 60) * 6
    radian = math.radians(degree)
    return radian


class Layers(LayerList):
    ClockDisk = Layer()
    ClockHead = Layer()


def view(model):
    center_x, center_y = 200, 200
    length = 100
    rad = get_angles_from_sec(model-90)
    hand_x = center_x + int(length * math.cos(-rad))
    hand_y = center_y + int(length * math.sin(-rad))
    return View(
        simple_circle(
            center_x, center_y, radius=length+10, color=Colors.Primary.Cyan,
            layer=Layers.ClockDisk
        ),
        simple_line(
            center_x, center_y, hand_x, hand_y, color=Colors.Accent.Pink,
            layer=Layers.ClockHead
        )
    )


class Msg(UnionMessage):
    Tick = Message("time")


def subscriptions(model):
    return Subscriptions(notify_every(Msg.Tick, sec=1))


def update(msg, model):
    if msg == Msg.Tick:
        return msg.time, Commands()
    else:
        return model, Commands()


if __name__ == "__main__":
    debug = True
    program(
        init=init_model,
        update=update,
        view=view,
        subscriptions=subscriptions,
    )
