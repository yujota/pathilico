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
        (("once", 1.5), Msg.ExecLoadFromDatabase, dict()),
        (("once", 10), Msg.ExecSaveToDatabase, dict()),
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
    area = (200, 100, 1200, 700)
    delete_start = (
        (("once", 7), Msg.DeleteDragStartAt, dict(x=area[0], y=area[1])),
    )
    get_x = lambda i: int((area[2] - area[0]) / 25 * (i+1) + area[0])
    get_y = lambda i: int((area[3] - area[1]) / 25 * (i+1) + area[1])
    delete_at = tuple([
        (("once", 7+0.1*i), Msg.DeleteDragAt, {'x': get_x(i), "y": get_y(i)})
        for i in range(25)
    ])
    delete_end = (
        (("once", 9.5), Msg.DeleteDragEndAt, dict(x=area[2], y=area[3])),
    )
    delete_schedule = delete_start + delete_at + delete_end
    drawing_schedule = start_drawing + drawings + end_drawing
    halt_schedule = ((("once", 11), Msg.Shrink, dict(abcx=250)), )
    schedule = \
        move_schedule + drawing_schedule + delete_schedule + halt_schedule
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