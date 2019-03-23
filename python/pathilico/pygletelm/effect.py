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
"""This module provides base classes which handles job with side effect
such as file IO"""
import os
import time
import random
import threading
import queue
from logging import getLogger

import pyglet
from PIL import Image

import pathilico.pygletelm.cache as cache


# User APIs
class Subscriptions(object):

    def __init__(self, *subs):
        """Contain result of subscription function

        :param Iter[EffectObject] subs:
        """
        self.effects = [
            x for s_result in subs for x in s_result.effects
        ]
        self.events = [
            x for s_result in subs for x in s_result.events
        ]


NO_SUBSCRIPTIONS = Subscriptions()


class Commands(object):

    def __init__(self, *cmds):
        """Contain result of subscription function

        :param Iter[EffectObject] subs:
        """
        self.effects = [
            x for s_result in cmds for x in s_result.effects
        ]
        self.instants = [
            x for s_result in cmds for x in s_result.instants
        ]


NO_COMMANDS = Commands()


class EffectObject(object):

    def __init__(self, effects=None, events=None, instants=None):
        self.effects = effects or list()
        self.events = events or list()  # TODO: deprecate
        self.instants = instants or list()


# Subscription APIs
def notify_every(msg, msg_kwargs=None, sec=1, wait=0, until=0, sub_id=0):
    """Create subscription order, msg must take arg `time` (float)"""
    sub = NotifyEverySecondSubscription(
        msg, msg_kwargs=msg_kwargs, interval=sec, wait=wait, until=until,
        sub_id=sub_id
    )
    return EffectObject(effects=[sub])


def notify_once(msg, msg_kwargs=None, sec=1, sub_id=0):
    """Create subscription order, msg must take arg `time` (float)"""
    sub = NotifyOnceSubscription(
        msg, msg_kwargs=msg_kwargs, second=sec, sub_id=sub_id
    )
    return EffectObject(effects=[sub])


# Command APIs
def random_sample(population, k, msg, msg_kwargs=None):
    cmd = RandomSample(population, k, msg=msg, msg_kwargs=msg_kwargs)
    return EffectObject(instants=[cmd])


def read_image(image_path, msg, msg_kwargs=None):
    cmd = ReadImageCommand(
        image_path=image_path, msg=msg, msg_kwargs=msg_kwargs
    )
    return EffectObject(effects=[cmd])


# Core api
class SubscriptionBase(cache.CachedObject):

    def start(self):
        pass

    def update(self, update_kwargs):
        pass

    def done(self):
        pass


class Executor(object):
    # TODO: 受け取るコマンドを実体のないものにして, addやdeleteの機能は使わない
    # get_messageでコマンドを消去させるようにする
    # スレッド自体はasyncのファイルのdictかなんかにプールするようにする

    def __init__(self, proxy, logger=None):
        """Execute effect

        :param pathfinder.pygletelm.backend.StateProxy proxy:
        """
        self.logger = logger or getLogger("pfcore.EffectExecutor")
        self.proxy = proxy
        pyglet.clock.schedule(self.collect_sub_msg)
        pyglet.clock.schedule(self.collect_cmd_msg)
        self.subscriptions = dict()
        self.commands = list()
        self.proxy.sub_handlers.register(self.handle_subs)
        self.proxy.cmd_handlers.register(self.handle_cmds)

    def handle_subs(self, new_sub):
        """This func is passed to proxy.sub_handlers.register

        :param Subscriptions new_sub:
        """
        effects = new_sub.effects
        self.logger.debug("Handling new subs {}".format(effects))
        self.update_subscription_effects(effects)

    def handle_cmds(self, new_cmds):
        """This func is passed to proxy.sub_handlers.register

        :param Subscriptions new_sub:
        """
        insts = new_cmds.instants
        effects = new_cmds.effects
        self.logger.debug("Handling new instant cmds {}".format(insts))
        self.logger.debug("Handling new effect cmds {}".format(effects))
        self.add_command_effects(effects)
        for ins in insts:
            flag, msg = ins.get_message()
            if flag:
                self.proxy.push_message(msg)

    def update_subscription_effects(self, effects):
        new, update, delete = cache.diff(
            self.get_tags(self.subscriptions.values()), self.get_tags(effects)
        )
        for e in effects:
            if e.identity in new:
                self._add_subscription(e)
        for d_id in delete:
            self._delete_subscription(d_id)
        for u_id, u_kwargs in update.items():
            self._update_subscription(u_id, u_kwargs)

    def add_command_effects(self, effects):
        for e in effects:
            if not e.is_done():
                e.start()
                self.commands.append(e)

    @classmethod
    def get_tags(cls, l):
        return [a.tag for a in l]

    def _add_subscription(self, effect):
        self.subscriptions[effect.identity] = effect
        effect.start()

    def _delete_subscription(self, identity):
        if identity not in self.subscriptions.keys():
            return
        sub = self.subscriptions.pop(identity)
        sub.done()

    def _update_subscription(self, identity, update_kwargs):
        if identity in self.subscriptions:
            return
        self.subscriptions[identity].update(update_kwargs)

    def collect_sub_msg(self, dt):
        for e in self.subscriptions.values():
            flag, msg = e.get_message()
            if flag:
                self.proxy.push_message(msg)
                return

    def collect_cmd_msg(self, dt):
        for e in self.commands:
            flag, msg = e.get_message()
            if flag:
                self.logger.debug(
                    "New cmd result msg is collected {}".format(msg)
                )
                self.proxy.push_message(msg)
                break
        delete_ids = list()
        for i, e in enumerate(self.commands):
            if e.is_done():
                delete_ids.append(i)
                break
        self.commands = [
            v for i, v in enumerate(self.commands) if i not in delete_ids
        ]


class CommandBase(object):
    pass


class InstantCommandBase(CommandBase):
    pass


class CommandWithThreadWorkerBase(CommandBase):
    pass


class WorkerSideStreamingThread(object):
    thread_sleep_time = 0.01

    def __init__(self, worker, request=None, auto_start=True, daemon=True):
        self.worker = worker
        self.request = request
        self.responses = queue.Queue()
        self.thread = threading.Thread(target=self.thread_worker, daemon=daemon)
        self.stop = threading.Event()
        if auto_start:
            self.start_thread()

    def done(self):
        self.stop.set()

    def thread_worker(self):
        while not self.stop.is_set():
            flag, res = self.worker.get_response(self.request)
            if flag:
                self.responses.put(res)
            time.sleep(self.thread_sleep_time)

    def start_thread(self):
        self.thread.start()

    def get_response(self):
        if self.responses.empty():
            return False, None
        else:
            res = self.responses.get()
            return True, res


class ClientSideStreamingThread(WorkerSideStreamingThread):

    def __init__(self, worker, auto_start=True, daemon=True):
        self.requests = queue.Queue()
        super().__init__(worker, None, auto_start, daemon)

    def thread_worker(self):
        while True:
            if not self.requests.empty():
                req = self.requests.get()
                flag, res = self.worker.get_response(req)
                if flag:
                    self.responses.put(res)
                    break
            time.sleep(self.thread_sleep_time)

    def add_request(self, request):
        self.requests.put(request)


class BidirectionalStreamingThread(ClientSideStreamingThread):

    def thread_worker(self):
        while True:
            if not self.requests.empty():
                req = self.requests.get()
                flag, res = self.worker.get_response(req)
                if flag:
                    self.responses.put(res)
            time.sleep(self.thread_sleep_time)


class RandomSample(InstantCommandBase):

    def __init__(self, population, k, msg, msg_kwargs=None):
        self.msg_constructor = msg
        self.msg_kwargs = msg_kwargs or dict()
        self.population = population
        self.k = k
        super().__init__()

    def get_message(self):
        v = random.sample(self.population, self.k)
        return True, self.msg_constructor(v, **self.msg_kwargs)


class NotifyEverySecondSubscription(SubscriptionBase):
    _payload_type = cache.PayloadTypes.unique_by_class_and_payload
    _payload_attrs = ("msg_class", "interval", "until", "sub_id", "wait")

    def __init__(
            self, msg, msg_kwargs=None, interval=1, wait=0, until=0, sub_id=0):
        self.msg_constructor = msg
        self.msg_class = msg.__class__
        self.msg_kwargs = msg_kwargs or dict()
        self.until = until
        self.sub_id = sub_id
        self.interval = interval
        self.wait = wait
        self.worker = NotifyEverySecWorker(until=self.until, wait=self.wait)
        self.thread = WorkerSideStreamingThread(
            worker=self.worker, request=interval, auto_start=False, daemon=True
        )
        super().__init__()

    def start(self):
        self.thread.start_thread()

    def done(self):
        self.thread.done()

    def get_message(self):
        flag, res = self.thread.get_response()
        if flag:
            return True, self.msg_constructor(time=res, **self.msg_kwargs)
        else:
            return False, None


class NotifyOnceSubscription(SubscriptionBase):
    _payload_type = cache.PayloadTypes.unique_by_class_and_payload
    _payload_attrs = ("msg_class", "second", "msg_kwargs_info", "sub_id")

    def __init__(self, msg, msg_kwargs=None, second=1, sub_id=0):
        self.msg_constructor = msg
        self.msg_class = msg.__class__
        self.sub_id = sub_id
        self.msg_kwargs = msg_kwargs or dict()
        self.msg_kwargs_info = tuple(self.msg_kwargs.items())
        self.second = second
        self.worker = NotifyOnceWorker()
        self.thread = WorkerSideStreamingThread(
            worker=self.worker, request=second, auto_start=False, daemon=True
        )
        super().__init__()

    def start(self):
        self.thread.start_thread()

    def done(self):
        self.thread.done()

    def get_message(self):
        flag, res = self.thread.get_response()
        if flag:
            return True, self.msg_constructor(time=res, **self.msg_kwargs)
        else:
            return False, None


class NotifyEverySecWorker(object):
    def __init__(self, wait=0, until=0):
        self.last_time = time.time() - 10000
        self.start_time = time.time()
        self.wait = wait
        self.until = until

    def get_response(self, request):  # request == interval sec
        now = time.time()
        if now - self.start_time < self.wait:
            return False, now
        if now - self.start_time > self.until > 0:
            return False, now
        if now - self.last_time > request:
            self.last_time = now
            return True, now
        else:
            return False, now


class NotifyOnceWorker(object):
    def __init__(self):
        self.last_time = time.time()
        self.is_responsed = False

    def get_response(self, request):  # request == interval sec
        now = time.time()
        if now - self.last_time > request and self.is_responsed is False:
            self.last_time = now
            self.is_responsed = True
            return True, now
        else:
            return False, now


READ_IMAGE_WORKER_THREAD_POOL = list()


class ReadImageCommand(CommandWithThreadWorkerBase):

    def __init__(self, image_path, msg, msg_kwargs=None):
        self.msg_constructor = msg
        self.msg_kwargs = msg_kwargs or dict()
        if len(READ_IMAGE_WORKER_THREAD_POOL) == 0:
            worker = ReadImageWorker()
            thread = BidirectionalStreamingThread(
                worker=worker, auto_start=True, daemon=True
            )
            READ_IMAGE_WORKER_THREAD_POOL.append(thread)
            READ_IMAGE_WORKER_THREAD_POOL[0] = thread
        self.thread = READ_IMAGE_WORKER_THREAD_POOL[0]
        self.image_path = image_path
        self._is_finished = False

    def start(self):
        req = self.image_path, self.msg_constructor, self.msg_kwargs
        self.thread.add_request(req)

    def is_done(self):
        return self._is_finished

    def done(self):
        pass

    def get_message(self):
        flag, res = self.thread.get_response()
        if flag:
            msg, msg_kwargs, img_path, img = res
            self._is_finished = True
            return True, msg(
                image=img, image_path=img_path, **msg_kwargs
            )
        else:
            return False, None


class ReadImageWorker(object):

    def get_response(self, request):
        img_path, msg, msg_kwargs = request
        if not os.path.isfile(img_path):
            return False, None
        try:
            img = Image.open(img_path)
            return True, (msg, msg_kwargs, img_path, img)
        except:
            return False, None

