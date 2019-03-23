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
from logging import getLogger

import openslide
from PIL import ImageDraw, Image

import pathilico.pygletelm.effect as effect
import pathilico.app.popup as popup


class GetSlideInfo(effect.InstantCommandBase):

    def __init__(self, file_path, msg, msg_kwargs=None, logger=None):
        self.msg_constructor = msg
        self.msg_kwargs = msg_kwargs or dict()
        self.file_path = file_path
        self.logger = logger or getLogger("pfapp.Pathology")
        super().__init__()

    def get_message(self):
        if not os.path.isfile(self.file_path):
            self.logger.warn("File {} not found".format(
                self.file_path
            ))
            return False, "File not found"
        try:
            s = openslide.OpenSlide(self.file_path)
            file_name = os.path.basename(self.file_path)
            msg = self.msg_constructor(
                file_path=self.file_path, file_name=file_name,
                level_count=s.level_count, level_dimensions=s.level_dimensions,
                level_downsamples=s.level_downsamples,
                **self.msg_kwargs
            )
            s.close()
            self.logger.debug("Slide info is acquired")
            return True, msg
        except Exception as e:
            self.logger.error(e)
            return False, e


PATHOLOGY_READER_POOL = list()
PATHOLOGY_READER_LOAD = list()
PATHOLOGY_READER_FILE_PATH = [""]
GROUP_ANNOTATION_WORKER_POOL = list()


class ReadRegionFromPathologySlide(effect.CommandWithThreadWorkerBase):

    def __init__(
            self, file_path, location, level, size, msg, msg_kwargs=None,
            num_workers=4, logger=None):
        self.logger = logger or getLogger("pfapp.Pathology")
        if not PATHOLOGY_READER_FILE_PATH[0] == file_path:
            PATHOLOGY_READER_FILE_PATH[0] = file_path
            PATHOLOGY_READER_POOL.clear()
            PATHOLOGY_READER_LOAD.clear()
        if len(PATHOLOGY_READER_POOL) < num_workers:
            for i in range(num_workers - len(PATHOLOGY_READER_POOL)):
                worker = OpenSlideWorker(
                    file_path=file_path, logger=self.logger
                )
                thread = effect.BidirectionalStreamingThread(
                    worker=worker, auto_start=True, daemon=True
                )
                PATHOLOGY_READER_LOAD.append(0)
                PATHOLOGY_READER_POOL.append(thread)
        self.msg_constructor = msg
        self.msg_kwargs = msg_kwargs or dict()
        self.file_path = file_path
        self.location = location
        self.level = level
        self.size = size
        self.thread_id = 0
        self._is_finished = False

    def is_done(self):
        return self._is_finished

    def start(self):
        req = (
            self.msg_constructor, self.msg_kwargs, self.location, self.level,
            self.size
        )
        self.thread_id = [
            i for i, v in enumerate(PATHOLOGY_READER_LOAD)
            if v == min(PATHOLOGY_READER_LOAD)
        ][0]
        thread = PATHOLOGY_READER_POOL[self.thread_id]
        thread.add_request(req)

    def __str__(self):
        return "ReadRegion: {}".format(self.location)

    def done(self):
        pass

    def get_message(self):
        thread = PATHOLOGY_READER_POOL[self.thread_id]
        flag, res = thread.get_response()
        if flag:
            self.logger.debug("Worker's response collected {}".format(res))
            msg_constructor, msg_kwargs, location, level, size, img = res
            message = msg_constructor(
                location=location, level=level, size=size, image=img,
                **msg_kwargs
            )
            return True, message
        else:
            return False, None


class OpenSlideWorker(object):

    def __init__(self, file_path, logger=None):
        self.slide = openslide.OpenSlide(file_path)
        self.logger = logger or getLogger("pfapp.Pathology")

    def get_response(self, request):
        msg_constructor, msg_kwargs, location, level, size = request
        self.logger.debug("Start reading slide {}, {}".format(location, level))
        try:
            img = self.slide.read_region(location, level, size)
            res = msg_constructor, msg_kwargs, location, level, size, img
            self.logger.debug(
                "Tile image is read {}, {}".format(location, level)
            )
            return True, res
        except Exception as e:
            self.logger.warn(
                "OpenSlideWorker is failed to read {}, {}, {}".format(
                    location, level, e
                ))
            return False, e


def get_slide_info(file_path, msg, msg_kwargs=None):
    cmd = GetSlideInfo(file_path, msg, msg_kwargs)
    return effect.EffectObject(instants=[cmd])


def read_region(file_path, location, level, size, msg, msg_kwargs=None):
    cmd = ReadRegionFromPathologySlide(
        file_path, location, level, size, msg, msg_kwargs
    )
    return effect.EffectObject(effects=[cmd])


def generate_openslide_read_region_commands(queries):
    """

    :param queries:
    :param Iter[file_path, location, level, size, msg, msg_kwargs] queries:
    :return:
    """
    cmds = list()
    for f_path, loc, lev, size, msg, msg_kwargs in queries:
        cmd = ReadRegionFromPathologySlide(
            f_path, loc, lev, size, msg, msg_kwargs
        )
        cmds.append(cmd)
    return effect.EffectObject(effects=cmds)


def read_multi_regions(file_path, requests, msg, msg_kwargs=None):
    """

    :param file_path:
    :param Iter[location, level, size] requests:
    :param msg:
    :param msg_kwargs:
    :return:
    """
    cmds = list()
    for r in requests:
        loc, lev, size = r
        cmd = ReadRegionFromPathologySlide(
            file_path, loc, lev, size, msg, msg_kwargs
        )
        cmds.append(cmd)
    return effect.EffectObject(effects=cmds)


class AskFileNameDialog(effect.InstantCommandBase):

    def __init__(self, msg, msg_kwargs=None, root_dir=None, logger=None):
        self.msg_constructor = msg
        self.msg_kwargs = msg_kwargs or dict()
        self.root_dir = root_dir
        self.logger = logger or getLogger("pfapp.Pathology")
        super().__init__()

    def get_message(self):
        try:
            f_name = popup.ask_filename(self.root_dir)
            msg = self.msg_constructor(path=f_name, **self.msg_kwargs)
            self.logger.debug("AskFileName Got FileName {}".format(f_name))
            return True, msg
        except Exception as e:
            self.logger.error(e)
            return False, e


def ask_filename_dialog(msg, msg_kwargs=None, root_dir=None):
    cmd = AskFileNameDialog(
        msg=msg, msg_kwargs=msg_kwargs, root_dir=root_dir
    )
    return effect.EffectObject(instants=[cmd])


def create_grouped_annotation_image(
        points=None, polygons=None, tile_shape=(1024, 1024)
):
    """

    :param Iter[(int, int, color)] points:
    :param Iter[Iter[int]] polygons:
    :param tile_shape:
    :return:
    """
    canvas = Image.new("RGBA", tile_shape)
    draw = ImageDraw.Draw(canvas, mode="RGBA")
    for x, y, color in points:
        add_point(draw, x, y, color=color)
    for vs, color in polygons:
        add_polygon(draw, vs, color=color)
    del draw
    return canvas


def add_point(draw, x, y, color=(0, 255, 0, 180), w=8, r=2):
    draw.rectangle((x-w, y-r, x+w, y+r), fill=color)
    draw.rectangle((x-r, y-w, x+r, y+w), fill=color)


def add_polygon(draw, vertices, color=(0, 0, 255, 180)):
    draw.polygon(vertices, fill=color)


class GroupedAnnotationImageWorker(object):

    def __init__(self, logger=None):
        self.logger = logger or getLogger("pfapp.GroupAnnotation")

    def get_response(self, request):
        msg_constructor, msg_kwargs, points, polygons, tile_shape = request
        try:
            img = create_grouped_annotation_image(points, polygons, tile_shape)
            response = msg_constructor, msg_kwargs, img
            self.logger.debug("Grouped image, {}, {}, {}".format(msg_kwargs, img, type(img)))
            return True, response
        except Exception as e:
            self.logger.warning(
                "Failed to group image, {}, {}".format(msg_kwargs, e)
            )
            return False, e


class GroupAnnotationAsImage(effect.CommandWithThreadWorkerBase):

    def __init__(
            self, msg, points=tuple(), polygons=tuple(),
            tile_shape=(1024, 1024), msg_kwargs=None, logger=None):
        self.logger = logger or getLogger("pfapp.GroupAnnotation")
        self.msg_constructor = msg
        self.points, self.polygons = points, polygons
        self.tile_shape = tile_shape
        self.msg_kwargs = msg_kwargs or dict()
        if len(GROUP_ANNOTATION_WORKER_POOL) == 0:
            worker = GroupedAnnotationImageWorker()
            thread = effect.BidirectionalStreamingThread(
                worker=worker, auto_start=True, daemon=True
            )
            GROUP_ANNOTATION_WORKER_POOL.append(thread)

    def is_done(self):
        return False

    def done(self):
        pass

    def start(self):
        request = (
            self.msg_constructor, self.msg_kwargs, self.points, self.polygons,
            self.tile_shape
        )
        thread = GROUP_ANNOTATION_WORKER_POOL[0]
        thread.add_request(request)

    def get_message(self):
        if len(GROUP_ANNOTATION_WORKER_POOL) == 1:
            thread = GROUP_ANNOTATION_WORKER_POOL[0]
            flag, res = thread.get_response()
            if flag:
                self.logger.debug("Got res from gro-anno worker {}".format(res))
                msg_constructor, msg_kwargs, img = res
                message = msg_constructor(image=img, **msg_kwargs)
                return True, message
            else:
                return False, None
        else:
            return False, None


# [(msg, msg_kwargs, points, polygons, tile_shape)]
def group_multi_annotation_image(requests):
    cmds = list()
    for r in requests:
        msg, msg_kwargs, points, polygons, tile_shape = r
        c = GroupAnnotationAsImage(
            msg=msg, msg_kwargs=msg_kwargs, points=points, polygons=polygons,
            tile_shape=tile_shape
        )
        cmds.append(c)
    return effect.EffectObject(effects=cmds)


if __name__ == "__main__":
    # Functional tests
    s_path = os.path.expanduser("~/DataForML/svs/aiba.svs")
    assert os.path.isfile(s_path)

    class MockMessage(object):
        def __init__(self, *args, **kwargs):
            self.args, self.kwargs = args, kwargs

        def __str___(self):
            return "{} + {}".format(self.args, self.kwargs)

    get_si = GetSlideInfo(file_path=s_path, msg=MockMessage)
    f, m = get_si.get_message()
    print(m.kwargs)
    read_reg = ReadRegionFromPathologySlide(
        file_path=s_path, location=(5000, 5000), size=(800, 800), level=0,
        msg=MockMessage
    )
    read_reg.start()
    while True:
        f, m = read_reg.get_message()
        if f:
            break
    m.kwargs["image"].show()
