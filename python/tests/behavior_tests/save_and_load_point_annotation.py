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
MOCK_CATEGORY_ID = (12345000).to_bytes(4, 'little')


def get_schedule():
    move_schedule = (
        (("once", 0.3), Msg.WindowResized, dict(
            width=WINDOW_SIZE[0], height=WINDOW_SIZE[1])),
        (("once", 0.7), Msg.FileSelected, dict(path=SAMPLE_FILE_PATH)),
        (("once", 1), Msg.Move, dict(dx=-6000, dy=-8000)),
        (("once", 2), Msg.ExecLoadFromDatabase, dict()),
        (("once", 5), Msg.ExecSaveToDatabase, dict()),
    )
    add_point_schedule = tuple([
        (("once", 3+0.5*i), Msg.AddPoint,
         dict(x=random.randint(0, 1600), y=random.randint(0, 900),
              category_id=MOCK_CATEGORY_ID))
        for i in range(3)
    ])
    halt_schedule = ((("once", 7), Msg.Shrink, dict(abcx=250)), )
    schedule = move_schedule + add_point_schedule + halt_schedule
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
