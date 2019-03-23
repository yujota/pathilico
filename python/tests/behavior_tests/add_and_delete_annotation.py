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
import random

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
MOCK_ORANGE_ID = (12345000).to_bytes(4, 'little')


def get_schedule():
    area = (200, 300, 1200, 700)
    move_schedule = (
        (("once", 0.3), Msg.WindowResized, dict(
            width=WINDOW_SIZE[0], height=WINDOW_SIZE[1])),
        (("once", 0.7), Msg.FileSelected, dict(path=SAMPLE_FILE_PATH)),
        (("once", 1), Msg.Move, dict(dx=-6000, dy=-8000)),
    )
    add_point_schedule = tuple([
        (("once", 1.5+0.5*i), Msg.AddPoint,
         dict(x=random.randint(area[0], area[2]),
              y=random.randint(area[1], area[3]),
              category_id=MOCK_ORANGE_ID))
        for i in range(5)
    ])
    delete_start = (
        (("once", 6), Msg.DeleteDragStartAt, dict(x=area[0], y=area[1])),
    )
    get_x = lambda i: int((area[2] - area[0]) / 25 * (i+1) + area[0])
    get_y = lambda i: int((area[3] - area[1]) / 25 * (i+1) + area[1])
    delete_at = tuple([
        (("once", 6+0.2*i), Msg.DeleteDragAt, {'x': get_x(i), "y": get_y(i)})
        for i in range(25)
    ])
    delete_end = (
        (("once", 12), Msg.DeleteDragEndAt, dict(x=area[2], y=area[3])),
    )
    delete_schedule = delete_start + delete_at + delete_end
    halt_schedule = ((("once", 20), Msg.Shrink, dict(abcx=250)), )
    schedule = (
            move_schedule
            + add_point_schedule
            + delete_schedule
            + halt_schedule
    )
    behavior = ScheduledBehavior.from_schedules(schedule)
    return behavior


SCHEDULE = get_schedule()


@wrap_subscriptions_with_message_dispatcher(SCHEDULE)
def scheduled_subscriptions(model):
    return subscriptions(model)


@profile
def profiled_update(msg, model):
    return update(msg, model)


@profile
def profiled_program(*args, **kwargs):
    return program(*args, **kwargs)


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