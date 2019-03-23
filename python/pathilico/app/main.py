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
from logging import getLogger, INFO, Formatter, NullHandler

from pathilico.pygletelm.backend import program
from pathilico.app.model import init_model
from pathilico.app.view import view
from pathilico.app.update import update
from pathilico.app.subscriptions import subscriptions


LOGGING_CONFIG = dict(
    graphic_manager="INFO",
    effect_executor="INFO",
    backend="INFO"
)
WINDOW_SIZE = (16 * 80, 9 * 80)


def configure_app_logging_settings():
    # stream_handler = StreamHandler()
    stream_handler = NullHandler()
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


def load_dependencies():
    import pathilico.app.pathology as _
    import pathilico.app.position as _
    import pathilico.app.zone as _
    import pathilico.app.resource as _
    import pathilico.app.ux as _
    import pathilico.app.user as _
    import pathilico.app.annotation as _
    import pathilico.app.data as _
    import pathilico.app.menu as _


def main():
    configure_app_logging_settings()
    load_dependencies()
    program(
        init=init_model,
        view=view,
        update=update,
        subscriptions=subscriptions,
        logger_config=LOGGING_CONFIG,
        initial_window_size=WINDOW_SIZE
    )


if __name__ == "__main__":
    main()

