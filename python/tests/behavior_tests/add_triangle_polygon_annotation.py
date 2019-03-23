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
import os

import sympy

from profilehooks import profile

from pathilico.misc.behavior_tools import *


SAMPLE_FILE_PATH = os.path.expanduser(
    "~/DataForML/svs/aiba.svs"
)
LOGGING_CONFIG = dict(
    graphic_manager="INFO",
    effect_executor="INFO",
    backend="INFO"
)
WINDOW_SIZE = (1600, 900)


def get_heart_y(x):
    """

    (x^2 +y^2 - 1)^3 = x^2 * y^3

    :param x:
    :return int:
    """
    x = sympy.Symbol('x')
    y = sympy.Symbol('y', real=True)
    ep = ""


def triangle_coordinate(bottom=0, left=0):
    top2left = list()
    for i in range(5):
        x = 125 - 25 * i
        y = 250 - 50 * i
        top2left.append((x, y))
    left2right = list()
    for i in range(8):
        x = 0 + 25 * i
        y = 0
        left2right.append((x, y))
    right2top = list()
    for i in range(6):
        x = 200 - 25 * i
        y = 0 + 50 * i
        right2top.append((x, y))
    result = [
        (left + x, bottom + y) for x, y in top2left + left2right + right2top
    ]
    return result


def get_schedule():
    move_schedule = (
        (("once", 0.3), Msg.WindowResized, dict(
            width=WINDOW_SIZE[0], height=WINDOW_SIZE[1])),
        (("once", 0.7), Msg.FileSelected, dict(path=SAMPLE_FILE_PATH)),
        (("once", 1), Msg.Move, dict(dx=-6000, dy=-8000)),
    )
    cs = triangle_coordinate(200, 200)
    xs = [r[0] for r in cs]
    ys = [r[1] for r in cs]
    start_time = 2
    start_drawing = (
        (("once", start_time), Msg.DrawLineDragStartAt,
         dict(x=xs[0], y=ys[0])),
    )
    drawing_dicts = list()
    for i in range(1, len(xs)-1):
        x = xs[i]
        y = ys[i]
        dx = (xs[i+1] - x) // 2
        dy = (ys[i+1] - y) // 2
        drawing_dicts.append(dict(x=x, y=y, dx=dx, dy=dy))
    drawings = tuple([
        (("once", start_time+0.1 + 0.1*i), Msg.DrawLineDragAt, d)
        for i, d in enumerate(drawing_dicts)
    ])
    end_drawing = (
        (("once", start_time+len(cs)*0.1), Msg.DrawLineDragEndAt,
         dict(x=xs[-1], y=ys[-1])),
    )
    drawing_schedule = start_drawing + drawings + end_drawing
    halt_schedule = ((("once", 8), Msg.Shrink, dict(abcx=250)), )
    schedule = move_schedule + drawing_schedule+ halt_schedule
    behavior = ScheduledBehavior.from_schedules(schedule)
    return behavior


SCHEDULE = get_schedule()


@wrap_subscriptions_with_message_dispatcher(SCHEDULE)
def scheduled_subscriptions(model):
    return subscriptions(model)


def app():
    load_dependencies()
    configure_app_logging_settings()
    program(
        init=init_model,
        view=view,
        update=profile(update),
        subscriptions=scheduled_subscriptions,
        logger_config=LOGGING_CONFIG,
        initial_window_size=WINDOW_SIZE
    )


if __name__ == "__main__":
    app()