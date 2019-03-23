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
from logging \
    import getLogger, StreamHandler, DEBUG, INFO, ERROR, NullHandler, Formatter
import datetime
import platform

import pyglet

import pathilico.pygletelm.effect as effect
import pathilico.pygletelm.window as window


def configure_log_settings(
        graphic_manager=None, effect_executor=None, backend=None):
    null = NullHandler()
    modes = dict(DEBUG=DEBUG, INFO=INFO, ERROR=ERROR)
    pfcore_log_format = Formatter(
        '[%(asctime)s|%(name)s|%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )

    def set_handler(logger, mode):
        if mode in modes:
            handler = StreamHandler()
            handler.setFormatter(pfcore_log_format)
            logger.setLevel(modes.get(mode))
            logger.addHandler(handler)
        else:
            logger.addHandler(null)
    gm_logger = getLogger("pfcore.GraphicManager")
    set_handler(gm_logger, graphic_manager)
    backend_logger = getLogger("pfcore.Backend")
    set_handler(backend_logger, backend)
    effect_logger = getLogger("pfcore.EffectExecutor")
    set_handler(effect_logger, effect_executor)


class FunctionRegistry(object):

    def __init__(self, funcs=None, logger=None):
        self.logger = logger or getLogger("pfcore.Backend")
        self.funcs = funcs or list()

    def register(self, f):
        self.logger.debug("Registered, function `{}`".format(f))
        self.funcs.append(f)

    def clear(self):
        self.funcs = list()

    def __iter__(self):
        return self.funcs.__iter__()


class StateProxyForBeginnerBackend(object):

    def __init__(self, state, logger=None):
        self.logger = logger or getLogger("pfcore.Backend")
        self.state = state
        self.view_handlers = FunctionRegistry()

    @property
    def model(self):
        return self.state.model

    @model.setter
    def model(self, new_model, initial=False):
        self.logger.debug(
            "StateProxy's setter {} -> {}".format(self.state.model, new_model)
        )
        self.state.model = new_model
        self.exec_view(new_model)

    def exec_view(self, model):
        views = self.state.view(model)
        for f in self.view_handlers:
            f(views)

    def initial_view(self):
        self.exec_view(self.model)

    def push_message(self, message):
        self.logger.debug(
            "StateProxy's push_message is called with {}".format(message)
        )
        new_model = self.state.update(message, self.model)
        self.model = new_model


class StateProxy(object):

    def __init__(self, state, logger=None):
        self.logger = logger or getLogger("pfcore.Backend")
        self.state = state
        self.view_handlers = FunctionRegistry()
        self.cmd_handlers = FunctionRegistry()
        self.sub_handlers = FunctionRegistry()

    @property
    def model(self):
        return self.state.model

    @model.setter
    def model(self, new_model):
        self.logger.debug(
            "StateProxy's setter {} -> {}".format(self.state.model, new_model)
        )
        self.state.model = new_model
        self.exec_view(new_model)
        self.exec_subs(new_model)

    def exec_view(self, model=None):
        model = model or self.state.model
        views = self.state.view(model)
        for f in self.view_handlers:
            f(views)

    def exec_subs(self, model):
        subs = self.state.subscriptions(model)
        for f in self.sub_handlers:
            f(subs)

    def initial_reaction(self, init_cmds=None):
        self.exec_view(self.model)
        self.exec_subs(self.model)
        if init_cmds:
            for f in self.cmd_handlers:
                f(init_cmds)

    def push_message(self, message):
        self.logger.debug(
            "StateProxy's push_message is called with {}".format(message)
        )
        new_model, new_cmds = self.state.update(message, self.model)
        self.model = new_model
        for f in self.cmd_handlers:
            f(new_cmds)


def has_retina_display():
    plt_name = platform.system()
    flag = plt_name == "Darwin"
    return flag


class BeginnerBackend(object):

    def __init__(self, model, view, update, logger=None):
        self.logger = logger or getLogger("pfcore.Backend")
        self.model = model
        self.view = view
        self.update = update
        self.proxy = self.get_proxy()
        self.window_provider = window.Provider(
            proxy=self.proxy, retina_display=has_retina_display()
        )
        self.proxy.initial_view()

    def get_proxy(self):
        return StateProxyForBeginnerBackend(state=self, logger=self.logger)


def beginner_program(model, view, update, logger_config=None):
    logger_config = logger_config or dict()
    configure_log_settings(**logger_config)
    logger = getLogger("pfcore.Backend")
    logger.info("Start beginner program @ {}".format(datetime.datetime.now()))
    backend = BeginnerBackend(
        model, view, update, logger=logger
    )
    pyglet.app.run()


class Backend(object):

    def __init__(
            self, init, view, update, subscriptions, logger=None,
            initial_window_size=(640, 480)
    ):
        self.logger = logger or getLogger("pfcore.Backend")
        self.model, init_cmds = init()
        self.view = view
        self.update = update
        self.subscriptions = subscriptions
        proxy = self.get_proxy()
        self.logger.info("Retina mode: {}".format(has_retina_display()))
        self.window_provider = window.Provider(
            proxy=proxy, initial_window_size=initial_window_size,
            retina_display=has_retina_display()
        )
        self.effect_executor = effect.Executor(proxy=proxy)
        proxy.initial_reaction(init_cmds)

    def set_global_line_width(self, width=3):
        pyglet.gl.glLineWidth(width)

    def get_proxy(self):
        return StateProxy(state=self, logger=self.logger)


def program(init, view, update, subscriptions, logger_config=None,
            initial_window_size=(640, 480)):
    logger_config = logger_config or dict()
    configure_log_settings(**logger_config)
    logger = getLogger("pfcore.Backend")
    logger.info("Start program @ {}".format(datetime.datetime.now()))
    backend = Backend(
        init, view, update, subscriptions, logger=logger,
        initial_window_size=initial_window_size
    )
    backend.set_global_line_width()
    pyglet.app.run()
