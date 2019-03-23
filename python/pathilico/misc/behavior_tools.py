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
from logging import getLogger, StreamHandler, DEBUG, INFO, Formatter

import functools
import pathilico.pygletelm.effect as effect
from pathilico.pygletelm.backend import program

from pathilico.app.model import init_model
from pathilico.app.update import update
from pathilico.app.view import view
from pathilico.app.subscriptions import subscriptions
from pathilico.app.message import Msg
from pathilico.app.main import load_dependencies


LOGGING_CONFIG = dict(
    graphic_manager="INFO",
    effect_executor="INFO",
    backend="DEBUG"
)


def configure_app_logging_settings():
    stream_handler = StreamHandler()
    log_format = Formatter(
        '[%(asctime)s|%(name)s|%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    stream_handler.setFormatter(log_format)
    pathology_logger = getLogger("pfapp.Pathology")
    pathology_logger.setLevel(INFO)
    pathology_logger.addHandler(stream_handler)
    annotation_logger = getLogger("pfapp.Annotation")
    annotation_logger.setLevel(INFO)
    annotation_logger.addHandler(stream_handler)
    grouped_annotation_logger = getLogger("pfapp.GroupAnnotation")
    grouped_annotation_logger.setLevel(INFO)
    grouped_annotation_logger.addHandler(stream_handler)
    grouped_annotation_logger = getLogger("pfapp.PickleDatabase")
    grouped_annotation_logger.setLevel(DEBUG)
    grouped_annotation_logger.addHandler(stream_handler)


STR2SUB = {
    "every": effect.notify_every,
    "once": effect.notify_once
}


class ScheduledBehavior(object):

    def __init__(self, subs=None):
        self.subscriptions = subs or effect.Subscriptions()

    def add_schedules(self, *subs):
        self.subscriptions = effect.Subscriptions(self.subscriptions, *subs)

    @classmethod
    def from_schedules(cls, schedules):
        """Make the instance from tuple schedule"""
        subs = list()
        for sub_tuple in schedules:
            spec, msg, msg_kwargs = sub_tuple
            func = STR2SUB.get(spec[0], None)
            if func is None:
                continue
            s = func(msg, msg_kwargs, *spec[1:])
            subs.append(s)
        subs = effect.Subscriptions(*subs)
        return cls(subs)


def wrap_subscriptions_with_message_dispatcher(behaviors):
    def decorator(sub_func):
        @functools.wraps(sub_func)
        def wrapper(model):
            result = effect.Subscriptions(
                sub_func(model), behaviors.subscriptions
            )
            return result
        return wrapper
    return decorator


if __name__ == "__main__":
    from pathilico.pygletelm.message import UnionMessage as Msg
    s = (
        (("every", 5), Msg.Ok, dict(value="fuga")),
    )
    schedule = ScheduledBehavior.from_schedules(s)
    print(schedule.subscriptions.effects)
