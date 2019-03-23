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
import math
import time
import functools
import datetime
import itertools
from logging import getLogger

import pyglet
from PIL import Image

import pathilico.pygletelm.cache as cache
import pathilico.app.geometry as geometry
from pathilico.pygletelm.message import WindowResized, WindowApiChangeCursor


LAYERS = dict()


class GlobalWindowInfo(object):
    width = 100
    height = 100


def get_layer_group(ind):
    if ind not in LAYERS:
        LAYERS[ind] = pyglet.graphics.OrderedGroup(ind)
    return LAYERS[ind]


def update_percentile_location_coordination(p, horizontal=True):
    if horizontal:
        l = GlobalWindowInfo.width
    else:
        l = GlobalWindowInfo.height
    if p >= 0:
        r = int(p * l)
    else:
        r = int(l + p * l)
    r = r if r <= l else l
    return r


def friendly_api(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        new_kwargs = dict()
        for k, v in kwargs.items():
            if k == "layer" and isinstance(v, int):
                new_kwargs["group"] = get_layer_group(v)
                new_kwargs["layer"] = v
                continue
            if k in (
                    "x", "x0", "x1", "x2", "radius", "r", "length", "width"
            ) and isinstance(v, float):
                new_kwargs[k] = update_percentile_location_coordination(v)
                continue
            if k in (
                    "y", "y0", "y1", "y2", "height"
            ) and isinstance(v, float):
                new_kwargs[k] = update_percentile_location_coordination(
                    v, False
                )
                continue
            new_kwargs[k] = v
        return f(*args, **new_kwargs)
    return wrapper


# User APIs
class Layer(object):

    def __init__(self):
        self._created = time.time()


class LayerControl(type):

    def __new__(meta, name, bases, class_dict):
        layers = [(k, v) for k, v in class_dict.items() if isinstance(v, Layer)]
        new_layers = [
            (k[0], i)
            for i, k in enumerate(sorted(layers, key=lambda x: x[1]._created))
        ]
        for k, v in new_layers:
            class_dict[k] = v
        for i in range(len(new_layers)+10):
            if i not in LAYERS:
                LAYERS[i] = pyglet.graphics.OrderedGroup(i)
        return type.__new__(meta, name, bases, class_dict)


class LayerList(object, metaclass=LayerControl):
    pass


class View(object):  # User api

    def __init__(self, *view_results):
        """Contain result of view function

        :param Iter[ViewResult] view_results:
        """
        self.drawings = [
            x for v_result in view_results for x in v_result.drawings
        ]
        self.events = [
            x for v_result in view_results for x in v_result.events
        ]


# Factory functions to make primitive drawings
@friendly_api
def simple_box(
        x, y, width, height, color=(255, 255, 255, 255), group=None,
        layer=0, *args, **kwargs):
    box = PrimitiveBox(
        x=x, y=y, width=width, height=height, color=color, group=group
    )
    return WindowObject([box])


@friendly_api
def simple_circle(
        x, y, radius, color=(255, 255, 255, 255), group=None,
        layer=0, *args, **kwargs):
    circle = PrimitiveCircle(x=x, y=y, radius=radius, color=color, group=group)
    return WindowObject([circle])


@friendly_api
def simple_line(
        x0, y0, x1, y1, color=(255, 255, 255, 255), group=None, layer=0,
        *args, **kwargs):
    return WindowObject([PrimitiveLine(x0, y0, x1, y1, color, group=group)])


@friendly_api
def simple_triangle(
        x0, y0, x1, y1, x2, y2, color=(255, 255, 255, 255), group=None, layer=0,
        *args, **kwargs):
    return WindowObject(
        [PrimitiveTriangle(x0, y0, x1, y1, x2, y2, color, group=group)]
    )


@friendly_api
def simple_text_label(
        x, y, text, font_name="Helvetica", font_size=18,
        anchor_x="center", anchor_y="center", font_bold=False,
        font_color=(255, 255, 255, 255), group=None, layer=0, *args, **kwargs):
    return WindowObject([PrimitiveTextLabel(
        x, y, text, font_name, font_size, anchor_x, anchor_y,
        font_color=font_color, font_bold=font_bold, group=group
    )])


@friendly_api
def box_with_text(
        x, y, width, height, text="", color=(100, 100, 100, 255),
        font_name="Helvetica", font_size=18, anchor_x="center",
        anchor_y="center", font_color=(255, 255, 255, 255), group=None, layer=0,
        font_bold=False, *args, **kwargs):
    box = PrimitiveBox(x, y, width, height, color, group)
    text_label_group = get_layer_group(layer+1)
    text_label = PrimitiveTextLabel(
        x+width//2, y+height//2, text, font_name, font_size, anchor_x, anchor_y,
        font_bold=font_bold, font_color=font_color, group=text_label_group
    )
    return WindowObject([box, text_label])


@friendly_api
def simple_image(
        x, y, image, scale=1, group=None, usage="dynamic", layer=0,
        image_id=None, *args, **kwargs):
    image_id = image_id or id(image)
    return WindowObject(
        [PrimitiveImage(x, y, image, scale, group=group, image_id=image_id)]
    )


@friendly_api
def polygon(
        points, group=None, color=(255, 255, 255, 255), layer=0, dim=2,
        index=tuple(), triangulate=False, *args, **kwargs):
    if dim == 2:
        points = list(itertools.chain.from_iterable(points))
    if triangulate:
        index = geometry.triangulate(points)
    p = PrimitivePolygon(vertices=points, group=group, color=color, index=index)
    return WindowObject([p])


@friendly_api
def curve(
        points, group=None, color=(255, 255, 255, 255), layer=0, dim=2,
        index=tuple(), *args, **kwargs):
    if dim == 2:
        points = list(itertools.chain.from_iterable(points))
    p = PrimitiveCurve(vertices=points, group=group, color=color)
    return WindowObject([p])


@friendly_api
def button(
        event_msg, msg_kwargs=None, x=0, y=0, width=100, height=100, group=None,
        layer=0, color=(255, 255, 255, 255), text="", font_bold=False,
        font_name="Helvetica", font_size=18, anchor_x="center",
        anchor_y="center", font_color=(255, 255, 255, 255),  *args, **kwargs):
    box_graphic = PrimitiveBox(x, y, width, height, color, group)
    text_label_group = get_layer_group(layer+1)
    text_label = PrimitiveTextLabel(
        x+width//2, y+height//2, text, font_name, font_size, anchor_x, anchor_y,
        font_bold=font_bold, font_color=font_color, group=text_label_group
    )
    box_event = OnClickBox(
        x, y, width, height, event_msg, msg_kwargs, priority=layer
    )
    return WindowObject([box_graphic, text_label], [box_event])


def mouse_drag_area(
        x, y, width, height, message, msg_kwargs=None, priority=0, layer=0,
        drag_start_msg=None, drag_start_msg_kwargs=None, drag_end_msg=None,
        drag_end_msg_kwargs=None):
    priority = priority or layer
    event = OnMouseDrag(
        x, y, width, height, message, msg_kwargs, priority=priority,
        on_mouse_press_message=drag_start_msg,
        on_mouse_press_kwargs=drag_start_msg_kwargs,
        on_mouse_release_message=drag_end_msg,
        on_mouse_release_kwargs=drag_end_msg_kwargs
    )
    return WindowObject(events=[event])


def mouse_click_area(
        x, y, width, height, message, msg_kwargs=None, priority=0, layer=0):
    priority = priority or layer
    event = OnClickBox(
        x, y, width, height, message, msg_kwargs, priority
    )
    return WindowObject(events=[event])


def mouse_press_area(
        x, y, width, height, message, msg_kwargs=None, priority=0, layer=0):
    priority = priority or layer
    event = OnPressBox(
        x, y, width, height, message, msg_kwargs, priority
    )
    return WindowObject(events=[event])


def mouse_scroll_area(
        x, y, width, height, message, msg_kwargs=None, priority=0, layer=0):
    priority = priority or layer
    event = OnMouseScroll(
        x, y, width, height, message, msg_kwargs, priority
    )
    return WindowObject(events=[event])


def mouse_double_click_area(
        x, y, width, height, message, msg_kwargs=None, modifiers=None,
        priority=100, layer=0):
    priority = priority or layer
    if isinstance(modifiers, str):
        modifiers = getattr(pyglet.window.key, modifiers)
    event = OnDoubleClick(
        x, y, width, height, message, msg_kwargs=msg_kwargs, priority=priority,
        modifiers=modifiers
    )
    return WindowObject(events=[event])


def shortcut_key_release_event(
        message, symbol, modifiers=None, msg_kwargs=None):
    if isinstance(symbol, str):
        symbol = getattr(pyglet.window.key, symbol)
    if isinstance(modifiers, str):
        modifiers = getattr(pyglet.window.key, modifiers)
    event = OnKeyRelease(
        symbol=symbol, modifiers=modifiers, message=message,
        msg_kwargs=msg_kwargs
    )
    return WindowObject(events=[event])


class WindowObject(object):

    def __init__(self, drawings=None, events=None):
        self.drawings = drawings or list()
        self.events = events or list()


class AtomicDrawing(cache.CachedObject):
    _payload_type = cache.PayloadTypes.unique_by_class_and_replaceable_payload

    def __init__(self):
        self.drawing = None
        super().__init__()

    def draw(self, batch):
        pass

    def update(self, update_kwargs):
        pass

    def done(self):
        if hasattr(self, "drawing"):
            del self.drawing


class PrimitiveBox(AtomicDrawing):
    _payload_attrs = ("x", "y", "width", "height", "color", "group")
    _payload_replaceable_attrs = _payload_attrs[:-1]

    def __init__(
            self, x, y, width, height, color=(255, 255, 255, 255), group=None):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.color = color
        self.group = group
        super().__init__()
        self.drawing = None

    def update(self, update_kwargs):
        update_vertices = False
        for k, v in update_kwargs.items():
            if k == "color":
                self.color = v
                self.drawing.colors = self.get_colors(v)[-1]
            elif k in ("x", "y", "width", "height"):
                setattr(self, k, v)
                update_vertices = True
        if update_vertices:
            self.drawing.vertices = self.get_vertices(
                self.x, self.y, self.width, self.height
            )[-1]

    def draw(self, batch):
        vs = self.get_vertices(self.x, self.y, self.width, self.height)
        cs = self.get_colors(self.color)
        self.drawing = batch.add(
            4, pyglet.gl.GL_QUADS, self.group, vs, cs
        )

    @classmethod
    def get_vertices(self, x, y, width, height):
        vs = (
            x, y+height, x, y, x+width, y, x+width, y+height
        )  # top left, bottom left, bottom right, top right
        return "v2i", vs

    @classmethod
    def get_colors(cls, color):
        color_type = "c3B" if len(color) == 3 else "c4B"
        return color_type, color*4


class PrimitiveCircle(AtomicDrawing):
    _payload_attrs = ("x", "y", "radius", "color", "group")
    _payload_replaceable_attrs = _payload_attrs[:-1]

    def __init__(self, x, y, radius, color=(255, 255, 255, 255), group=None):
        self.x, self.y, self.radius = x, y, radius
        self.color = color
        self.group = group
        super().__init__()
        self.drawing = None

    @classmethod
    def get_vertices_and_indices(self, x, y, radius):
        vs = [x, y]
        inds = []
        for i, d in enumerate(range(0, 360, 2)):
            r = math.radians(d)
            h = x + int(radius*math.cos(r))
            v = y + int(radius*math.sin(r))
            vs.append(h)
            vs.append(v)
            inds.extend([0, i, i+1])
        inds[-1] = 1
        return ("v2i", vs), inds

    @classmethod
    def get_colors(cls, color, vs):
        num_vs = len(vs[-1]) // 2
        color_type = "c3B" if len(color) == 3 else "c4B"
        return color_type, color*num_vs

    def draw(self, batch):
        vs, inds = self.get_vertices_and_indices(self.x, self.y, self.radius)
        cs = self.get_colors(self.color, vs)
        self.drawing = batch.add_indexed(
            len(vs[-1])//2, pyglet.gl.GL_TRIANGLES, self.group, inds, vs, cs
        )

    def update(self, update_kwargs):
        for k, v in update_kwargs.items():
            setattr(self, k, v)
        vs, inds = self.get_vertices_and_indices(self.x, self.y, self.radius)
        cs = self.get_colors(self.color, vs)
        self.drawing.vertices = vs[-1]
        self.drawing.indices = inds
        self.drawing.colors = cs[-1]


class PrimitiveLine(AtomicDrawing):
    _payload_attrs = ("x0", "y0", "x1", "y1", "color", "group")
    _payload_replaceable_attrs = _payload_attrs[:-1]

    def __init__(self, x0, y0, x1, y1, color=(255, 255, 255, 255), group=None):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.color = color
        self.group = group
        self.drawing = None
        super().__init__()

    @classmethod
    def get_vertices(self, x0, y0, x1, y1):
        vs = (x0, y0, x1, y1)
        return ("v2i", vs)

    @classmethod
    def get_colors(cls, color):
        color_type = "c3B" if len(color) == 3 else "c4B"
        return color_type, color*2

    def draw(self, batch):
        vs = self.get_vertices(self.x0, self.y0, self.x1, self.y1)
        cs = self.get_colors(self.color)
        self.drawing = batch.add(2, pyglet.gl.GL_LINES, self.group, vs, cs)

    def update(self, update_kwargs):
        for k, v in update_kwargs.items():
            setattr(self, k, v)
        vs = self.get_vertices(self.x0, self.y0, self.x1, self.y1)
        cs = self.get_colors(self.color)
        self.drawing.vertices = vs[-1]
        self.drawing.colors = cs[-1]


class PrimitiveTriangle(AtomicDrawing):
    _payload_attrs = ("x0", "y0", "x1", "y1", "x2", "y2", "color", "group")
    _payload_replaceable_attrs = _payload_attrs[:-1]

    def __init__(
            self, x0, y0, x1, y1, x2, y2, color=(255, 255, 255, 255),
            group=None):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.x2, self.y2 = x2, y2
        self.color = color
        self.group = group
        self.drawing = None
        super().__init__()

    @classmethod
    def get_vertices(self, x0, y0, x1, y1, x2, y2):
        vs = (x0, y0, x1, y1, x2, y2)
        return "v2i", vs

    @classmethod
    def get_colors(cls, color):
        color_type = "c3B" if len(color) == 3 else "c4B"
        return color_type, color*3

    def draw(self, batch):
        vs = self.get_vertices(
            self.x0, self.y0, self.x1, self.y1, self.x2, self.y2
        )
        cs = self.get_colors(self.color)
        self.drawing = batch.add(3, pyglet.gl.GL_TRIANGLES, self.group, vs, cs)

    def update(self, update_kwargs):
        for k, v in update_kwargs.items():
            setattr(self, k, v)
        vs = self.get_vertices(
            self.x0, self.y0, self.x1, self.y1, self.x2, self.y2
        )
        cs = self.get_colors(self.color)
        self.drawing.vertices = vs[-1]
        self.drawing.colors = cs[-1]


class PrimitivePolygon(AtomicDrawing):
    _payload_attrs = ("num_points", "vertices", "color", "group", "index")
    _payload_replaceable_attrs = _payload_attrs[0:3]

    def __init__(
            self, vertices, color=(255, 255, 255, 255), index=tuple(),
            group=None):
        self.num_points = len(vertices) // 2
        self.index = tuple(index)
        self.color, self.group = color, group
        self.vertices = \
            vertices if isinstance(vertices, tuple) else tuple(vertices)
        self.drawing = None
        super().__init__()

    @classmethod
    def get_vertices(self, vs):
        return "v2i", vs

    @classmethod
    def get_colors(cls, color, num_points):
        color_type = "c3B" if len(color) == 3 else "c4B"
        return color_type, color*num_points

    def draw(self, batch):
        vs = self.get_vertices(self.vertices)
        cs = self.get_colors(self.color, num_points=self.num_points)
        if self.index:
            self.drawing = batch.add_indexed(
                self.num_points, pyglet.gl.GL_TRIANGLES, self.group, self.index,
                vs, cs
            )
        else:
            self.drawing = batch.add(
                self.num_points, pyglet.gl.GL_TRIANGLES, self.group, vs, cs
            )

    def update(self, update_kwargs):
        for k, v in update_kwargs.items():
            setattr(self, k, v)
        vs = self.get_vertices(self.vertices)
        cs = self.get_colors(self.color, num_points=self.num_points)
        self.drawing.vertices = vs[-1]
        self.drawing.colors = cs[-1]


class PrimitiveCurve(AtomicDrawing):
    _payload_attrs = (
        "num_points", "vertices", "start_point", "num_alloc", "color", "group"
    )
    _payload_replaceable_attrs = _payload_attrs[:2]

    def __init__(
            self, vertices, color=(255, 255, 255, 255), num_alloc=2048,
            group=None, logger=None):
        self.logger = logger or getLogger("pfcore.GraphicManager")
        self.num_points = len(vertices) // 2
        self.start_point = tuple(vertices[0:2])
        self.vertices = \
            vertices if isinstance(vertices, tuple) else tuple(vertices)
        self.num_alloc = num_alloc
        self.color = color
        self.group = group
        self.drawing = None
        super().__init__()

    @classmethod
    def get_vertices(cls, vertices, num_points, num_alloc):
        vs = vertices + vertices[-2:] * (num_alloc - num_points)
        return ("v2i", vs)

    @classmethod
    def get_indices(cls, num_points, num_alloc):
        if num_points < 2:
            return [0] * 2 * (num_alloc -1)
        inds = [0] \
               + list(itertools.chain.from_iterable(
                   [(i, i) for i in range(1, num_points-1)])
               ) \
               + [num_points-1] * (2*num_alloc - 2*num_points + 1)
        # e.g. [0, 1, 1, 2, 2, 2] when n_points==3 and n_alloc==4
        return inds

    @classmethod
    def get_colors(cls, color, num_alloc):
        color_type = "c3B" if len(color) == 3 else "c4B"
        return color_type, color*num_alloc

    def draw(self, batch):
        self.logger.debug(
            "[PrimitiveCurve] drawing obj start point @ ({})".format(
                self.start_point)
        )
        vs = self.get_vertices(self.vertices, self.num_points, self.num_alloc)
        indices = self.get_indices(self.num_points, self.num_alloc)
        cs = self.get_colors(self.color, self.num_alloc)
        self.drawing = batch.add_indexed(
            self.num_alloc, pyglet.gl.GL_LINES, self.group, indices, vs, cs
        )

    def update(self, update_kwargs):
        for k, v in update_kwargs.items():
            setattr(self, k, v)
        self.logger.debug(
            "[PrimitiveCurve] Updating points {}".format(
                update_kwargs["num_points"]
            )
        )
        vs = self.get_vertices(self.vertices, self.num_points, self.num_alloc)
        indices = self.get_indices(self.num_points, self.num_alloc)
        cs = self.get_colors(self.color, self.num_alloc)
        self.drawing.vertices = vs[-1]
        self.drawing.colors = cs[-1]
        self.drawing.indices = indices


class PrimitiveImage(AtomicDrawing):
    _payload_attrs = ("x", "y", "scale", "image_id", "group", "usage")
    _payload_replaceable_attrs = _payload_attrs[:3]

    def __init__(
            self, x, y, image, scale=1, group=None, usage="dynamic",
            image_id=None, logger=None):
        self.logger = logger or getLogger("pfcore.GraphicManager")
        self.x, self.y, self.scale = x, y, scale
        self.group = group
        self.usage = usage
        self.image = image
        self.drawing = None
        self.image_id = image_id or datetime.datetime.now()
        super().__init__()

    @staticmethod
    def convert_pil_image_to_pyglet_image(pil_image):
        """Convert PIL type image to pyglet image

        :param PIL.Image.Image pil_image: PIL image
        :return: pyglet.image.ImageData
        """
        raw_img = pil_image.tobytes()
        pitch = -1 * pil_image.width * len(pil_image.mode)
        pyg_img = pyglet.image.ImageData(
            pil_image.width, pil_image.height, pil_image.mode,
            raw_img, pitch=pitch
        )
        return pyg_img

    def draw(self, batch):
        if isinstance(self.image, Image.Image):
            self.image = self.convert_pil_image_to_pyglet_image(self.image)
        self.drawing = pyglet.sprite.Sprite(
            self.image, self.x, self.y, batch=batch, group=self.group,
            usage=self.usage
        )
        self.drawing.scale = self.scale
        self.logger.debug("PrimitiveImage {} is drawn".format(self.image_id))

    def update(self, update_kwargs):
        for k in self._payload_replaceable_attrs:
            if k in update_kwargs:
                v = update_kwargs[k]
                setattr(self, k, v)
                setattr(self.drawing, k, v)
        self.logger.debug("PrimitiveImage {} is updated, {}".format(
            self.image_id, update_kwargs))


class PrimitiveTextLabel(AtomicDrawing):
    _payload_attrs = (
        "text", "x", "y", "font_name", "font_size", "anchor_x", "anchor_y",
        "group", "font_bold"
    )
    _payload_replaceable_attrs = ("x", "y")

    def __init__(
            self, x, y, text, font_name="Helvetica", font_size=18,
            anchor_x="center", anchor_y="center", font_bold=False,
            font_color=(255, 255, 255, 255), group=None
    ):
        self.x, self.y, self.text = x, y, text
        self.group = group
        self.font_name, self.font_size = font_name, font_size
        self.font_color, self.font_bold = font_color, font_bold
        self.anchor_x, self.anchor_y = anchor_x, anchor_y
        self.drawing = None
        super().__init__()

    def draw(self, batch):
        self.drawing = pyglet.text.Label(
            self.text, x=self.x, y=self.y, batch=batch, group=self.group,
            font_size=self.font_size, font_name=self.font_name,
            anchor_x=self.anchor_x, anchor_y=self.anchor_y,
            color=self.font_color, bold=self.font_bold
        )

    def update(self, update_kwargs):
        for k in self._payload_replaceable_attrs:
            if k in update_kwargs:
                v = update_kwargs[k]
                setattr(self, k, v)
                setattr(self.drawing, k, v)


class PrimitiveSingleTextLine(AtomicDrawing):
    _payload_attrs = (
        "text", "x", "y", "width", "height", "font_name",
        "font_size", "anchor_x", "anchor_y",
        "group", "font_bold"
    )
    _payload_replaceable_attrs = ("x", "y")

    def __init__(
            self, x, y, text, width=200, height=200, font_name="Helvetica",
            font_size=18,
            anchor_x="center", anchor_y="center", font_bold=False,
            font_color=(255, 255, 255, 255), group=None
    ):
        self.x, self.y, self.text = x, y, text
        self.group = group
        self.font_name, self.font_size = font_name, font_size
        self.font_color, self.font_bold = font_color, font_bold
        self.anchor_x, self.anchor_y = anchor_x, anchor_y
        self.drawing = None
        super().__init__()

    def draw(self, batch):
        self.drawing = pyglet.text.Label(
            self.text, x=self.x, y=self.y, batch=batch, group=self.group,
            font_size=self.font_size, font_name=self.font_name,
            anchor_x=self.anchor_x, anchor_y=self.anchor_y,
            color=self.font_color, bold=self.font_bold
        )

    def update(self, update_kwargs):
        for k in self._payload_replaceable_attrs:
            if k in update_kwargs:
                v = update_kwargs[k]
                setattr(self, k, v)
                setattr(self.drawing, k, v)


class GraphicManager(object):

    def __init__(self, batch, logger=None):
        self.drawings = dict()
        self.my_d = None
        self.batch = batch
        self.logger = logger or getLogger("pfcore.GraphicManager")

    def update_drawings(self, drawings):
        new, update, delete = cache.diff(
            self.get_tags(self.drawings.values()), self.get_tags(drawings)
        )
        for d_id in delete:
            self._delete_drawing(d_id)
        for u_id, u_kwargs in update.items():
            self._update_drawing(u_id, u_kwargs)
        for d in drawings:
            if d.identity in new:
                self._add_drawing(d)

    @classmethod
    def get_tags(cls, l):
        return [a.tag for a in l]

    def _delete_drawing(self, identity):
        if identity not in self.drawings:
            return
        d = self.drawings.pop(identity)
        self.logger.debug("Deleting id {}, {}".format(identity, d))
        d.drawing.delete()
        d.done()

    def _add_drawing(self, drawing):
        self.drawings[drawing.identity] = drawing
        self.logger.debug("Adding id{}, {}".format(drawing.identity, drawing))
        drawing.draw(self.batch)

    def _update_drawing(self, identity, update_kwargs):
        if identity not in self.drawings:
            return
        self.logger.debug("Updating id {}, {}".format(identity, update_kwargs))
        self.drawings[identity].update(update_kwargs)


class PygletWindowApiHandler(object):
    def __init__(
            self, batch, window, proxy, actions=None, on_draw_events=None,
            retina_display=False
    ):
        """The instance is passed to pyglet.window.Window.push_handlers method

        :param pyglet.window.Batch batch:
        :param pyglet.window.Window window:
        :param pathfinder.pygletelm.backend.StateProxy proxy:
        :param on_draw_events:
        """
        self.batch = batch
        self.window = window
        self.actions = actions
        self.on_draw_events = on_draw_events or list()
        self.last_mouse_press_time = time.time() - 100
        self.last_mouse_release_time = time.time() - 100
        self.on_click_position = (-100, -100)
        self.set_global_window_info(window.width, window.height)
        self.proxy = proxy
        self.retina_display = retina_display

    def set_global_window_info(self, width, height):  # TODO: Deprecate
        GlobalWindowInfo.width = width
        GlobalWindowInfo.height = height

    def on_resize(self, width, height):
        if self.retina_display:
            pyglet.gl.glViewport(0, 0, width*2, height*2)
        else:
            pyglet.gl.glViewport(0, 0, width, height)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glOrtho(0, width, 0, height, -1, 1)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        self.set_global_window_info(width, height)
        self.proxy.push_message(WindowResized(width, height))

    def on_click(self, x, y, button, modifiers):  # Additional
        for e in self.actions:
            flag = e("on_click", x, y, button, modifiers)
            if flag:
                return True

    def on_double_click(self, x, y, button, modifiers):  # Additional
        for e in self.actions:
            flag = e("on_double_click", x, y, button, modifiers)
            if flag:
                return True

    def on_key_release(self, symbol, modifiers):
        for e in self.actions:
            flag = e("on_key_release", symbol, modifiers)
            if flag:
                return True

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        for e in self.actions:
            flag = e("on_mouse_scroll", x, y, scroll_x, scroll_y)
            if flag:
                return True

    def on_mouse_press(self, x, y, button, modifiers):
        for e in self.actions:
            flag = e("on_mouse_press", x, y, button, modifiers)
            if flag:
                return True
        self.last_mouse_press_time = time.time()
        self.on_click_position = (x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        for e in self.actions:
            flag = e("on_mouse_release", x, y, button, modifiers)
            if flag:
                return True
        now = time.time()
        if now - self.last_mouse_release_time < 0.8:
            self.last_mouse_release_time = now - 100
            self.last_mouse_press_time = now - 100
            self.on_double_click(x, y, button, modifiers)
            return True
        if now - self.last_mouse_press_time < 0.8:
            if (x, y) == self.on_click_position:
                self.on_click(x, y, button, modifiers)
                self.last_mouse_press_time = now - 100
                self.last_mouse_release_time = now
                return True

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        for e in self.actions:
            flag = e("on_mouse_drag", x, y, dx, dy, button, modifiers)
            if flag:
                return True

    def on_mouse_motion(self, x, y, dx, dy):
        for e in self.actions:
            flag = e("on_mouse_motion", x, y, dx, dy)
            if flag:
                return True

    def on_text(self, text):
        for e in self.actions:
            flag = e("on_text", text)
            if flag:
                return True

    def on_text_motion(self, motion):
        for e in self.actions:
            flag = e("on_text_motion", motion)
            if flag:
                return True

    def on_text_motion_select(self, motion):
        for e in self.actions:
            flag = e("on_text_motion_select", motion)
            if flag:
                return True

    def on_draw(self):
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(
            pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA
        )
        for e in self.on_draw_events:
            flag = e()
            if flag:
                return True
        self.window.clear()
        self.batch.draw()


class EventBase(cache.CachedObject):
    registered_events = tuple()
    _payload_type = cache.PayloadTypes.unique_by_class_and_payload


class OnPressBox(EventBase):
    registered_events = ("on_mouse_press", )
    _payload_attrs = (
        "x", "y", "width", "height", "msg_hash",
    )

    def __init__(
            self, x, y, width, height, message, msg_kwargs=None,
            priority=0):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.msg_constructor = message
        self.msg_hash = str(message) + str(msg_kwargs)
        self.msg_kwargs = msg_kwargs or dict()
        self.priority = priority
        super().__init__()

    def on_mouse_press(self, x, y, button, modifiers):  # -> fired bool, msg Msg
        if self.x <= x <= self.x+self.width \
                and self.y <= y <= self.y+self.height:
            msg = self.msg_constructor(
                x=x, y=y, button=button, modifiers=modifiers, **self.msg_kwargs
            )
            return True, msg
        else:
            return False, None


class OnClickBox(EventBase):
    registered_events = ("on_click", )
    _payload_attrs = (
        "x", "y", "width", "height", "msg_hash",
    )

    def __init__(
            self, x, y, width, height, message, msg_kwargs=None,
            priority=0):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.msg_constructor = message
        self.msg_hash = str(message) + str(msg_kwargs)
        self.msg_kwargs = msg_kwargs or dict()
        self.priority = priority
        super().__init__()

    def on_click(self, x, y, button, modifiers):  # -> fired bool, msg Msg
        if self.x <= x <= self.x+self.width \
                and self.y <= y <= self.y+self.height:
            msg = self.msg_constructor(
                x=x, y=y, button=button, modifiers=modifiers, **self.msg_kwargs
            )
            return True, msg
        else:
            return False, None


class OnDoubleClick(EventBase):
    registered_events = ("on_double_click", )
    _payload_attrs = (
        "x", "y", "width", "height", "msg_hash", "modifiers", "priority"
    )

    def __init__(
            self, x, y, width, height, message, msg_kwargs=None,
            priority=0, modifiers=None):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.msg_constructor = message
        self.msg_hash = str(message) + str(msg_kwargs)
        self.msg_kwargs = msg_kwargs or dict()
        self.priority = priority
        self.modifiers = modifiers
        super().__init__()

    def on_double_click(self, x, y, button, modifiers):
        if self.x <= x <= self.x+self.width \
                and self.y <= y <= self.y+self.height:
            if self.modifiers:
                if not modifiers & self.modifiers:
                    return False, None
            msg = self.msg_constructor(
                x=x, y=y, button=button, modifiers=modifiers, **self.msg_kwargs
            )
            return True, msg
        else:
            return False, None


class OnKeyRelease(EventBase):
    registered_events = ("on_key_release", )
    _payload_attrs = ("symbol", "modifiers", "msg_hash")

    def __init__(
            self, symbol, modifiers, message, msg_kwargs=None, priority=0):
        self.msg_constructor = message
        self.msg_hash = str(message) + str(msg_kwargs)
        self.msg_kwargs = msg_kwargs or dict()
        self.priority = priority
        self.symbol = symbol
        self.modifiers = modifiers
        super().__init__()

    def on_key_release(self, symbol, modifiers):
        if not symbol == self.symbol:
            return False, None
        if not self.modifiers:
            msg = self.msg_constructor(**self.msg_kwargs)
            return True, msg
        if modifiers & self.modifiers:
            msg = self.msg_constructor(**self.msg_kwargs)
            return True, msg
        return False, None


class OnMouseDrag(EventBase):
    registered_events = ("on_mouse_drag", "on_mouse_press", "on_mouse_release")
    _payload_attrs = (
        "x", "y", "width", "height", "msg_hash"
    )

    def __init__(
            self, x, y, width, height, message, msg_kwargs=None,
            on_mouse_press_message=None, on_mouse_press_kwargs=None,
            on_mouse_release_message=None, on_mouse_release_kwargs=None,
            priority=0):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.msg_constructor = message
        self.msg_hash = str(message) + str(msg_kwargs)
        self.msg_kwargs = msg_kwargs or dict()
        self.priority = priority
        self.on_mouse_press_msg = on_mouse_press_message
        self.on_mouse_press_kwargs = on_mouse_press_kwargs or dict()
        self.on_mouse_release_msg = on_mouse_release_message
        self.on_mouse_release_kwargs = on_mouse_release_kwargs or dict()
        super().__init__()

    def is_in_area(self, x, y):
        return (
                self.x <= x <= self.x+self.width
                and self.y <= y <= self.y+self.height
        )

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if self.is_in_area(x, y):
            msg = self.msg_constructor(
                x=x, y=y, dx=dx, dy=dy, button=button, modifiers=modifiers,
                **self.msg_kwargs
            )
            return True, msg
        else:
            return False, None

    def on_mouse_press(self, x, y, button, modifiers):
        if self.on_mouse_press_msg is None:
            return False, None
        if self.is_in_area(x, y):
            msg = self.on_mouse_press_msg(
                x=x, y=y, button=button, modifiers=modifiers,
                **self.on_mouse_press_kwargs
            )
            return True, msg
        else:
            return False, None

    def on_mouse_release(self, x, y, button, modifiers):
        if self.on_mouse_release_msg is None:
            return False, None
        if self.is_in_area(x, y):
            msg = self.on_mouse_release_msg(
                x=x, y=y, button=button, modifiers=modifiers,
                **self.on_mouse_release_kwargs
            )
            return True, msg
        else:
            return False, None


class OnMouseScroll(EventBase):
    registered_events = ("on_mouse_scroll", )
    _payload_attrs = (
        "x", "y", "width", "height", "msg_hash"
    )

    def __init__(
            self, x, y, width, height, message, msg_kwargs=None,
            priority=0):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.msg_constructor = message
        self.msg_hash = str(message) + str(msg_kwargs)
        self.msg_kwargs = msg_kwargs or dict()
        self.priority = priority
        super().__init__()

    def is_in_area(self, x, y):
        return (
                self.x <= x <= self.x+self.width
                and self.y <= y <= self.y+self.height
        )

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.is_in_area(x, y):
            msg = self.msg_constructor(
                x=x, y=y, scroll_x=scroll_x, scroll_y=scroll_y,
                **self.msg_kwargs
            )
            return True, msg
        else:
            return False, None


FOCUSED_ID = [0]
TEXT_FIELDS = dict()
W = pyglet.window.Window()
TEXT_CURSOR = W.get_system_mouse_cursor("text")
W.close()


@friendly_api
def text_field(
        x, y, width, height, padding_top=2, padding_bottom=2, padding_left=2,
        padding_right=2, text="", layer=0, editable=False, message=None,
        background_color=(200, 200, 200, 255), caret_id=100, font_bold=False,
        font_color=(0, 0, 0, 255), font_size=0, font_name="Helvetica",
        msg_kwargs=None, *args, **kwargs):
    base_box_layer_group = get_layer_group(layer)
    field_layer_group = get_layer_group(layer+1)
    box = PrimitiveBox(
        x, y, width, height, color=background_color,
        group=base_box_layer_group
    )
    text = TextField(
        x=x+padding_left, y=y+padding_bottom,
        width=width-padding_left-padding_right, caret_id=caret_id,
        height=height-padding_bottom-padding_top, text=text,
        font_size=font_size, font_name=font_name, font_bold=font_bold,
        group=field_layer_group, editable=editable, font_color=font_color
    )
    if editable and message is not None:
        caret_event = TextCaretEvent(
            message=message, msg_kwargs=msg_kwargs, caret_id=caret_id
        )
        return WindowObject([box, text], events=[caret_event])
    else:
        return WindowObject([box, text])


class TextField(AtomicDrawing):
    _payload_attrs = (
        "caret_id", "x", "y", "font_name", "font_size", "width", "height",
        "group", "font_bold"
    )
    # _payload_replaceable_attrs = ("x", "y")

    def __init__(
            self, x, y, text, width, height, caret_id, font_name="Helvetica",
            font_size=0, font_bold=False,
            font_color=(255, 255, 255, 255), group=None, editable=False,
            *args, **kwargs
    ):
        self.x, self.y, self.text = x, y, text
        self.width, self.height = width, height
        self.group = group
        self.font_color, self.font_bold = font_color, font_bold
        self.document = pyglet.text.document.UnformattedDocument(text)
        if font_size == 0:
            font_size = self.get_font_size(height, font_name)
        self.font_name, self.font_size = font_name, font_size
        self.document.set_style(
            0, -1,
            dict(font_name=font_name, font_size=font_size, color=font_color, bold=font_bold)
        )
        self.drawing = None
        self.caret = None
        self.caret_id = caret_id
        self.editable = editable
        if not editable:
            self._payload_attrs = self._payload_attrs + ("text", )
        super().__init__()

    def update(self, update_kwargs):
        for k, v in update_kwargs.items():
            if k in ("x", "y", "width", "height"):
                setattr(self, k, v)
                if self.drawing:
                    setattr(self.drawing, k, v)
                if self.caret:
                    self.caret.delete()
                    self.caret = None

    def draw(self, batch):
        """
        self.drawing = pyglet.text.layout.IncrementalTextLayout(
            self.document, self.width, self.height, multiline=False,
            batch=batch, group=self.group
        )
        """
        self.drawing = pyglet.text.layout.IncrementalTextLayout(
            self.document, self.width, self.height,
            batch=batch, group=self.group
        )
        if self.editable:
            self.caret = pyglet.text.caret.Caret(
                layout=self.drawing, batch=batch
            )
            TEXT_FIELDS[self.caret_id] = self
        self.drawing.x, self.drawing.y = self.x, self.y

    def done(self):
        if hasattr(self, "caret"):
            if self.caret:
                self.caret.visible = False
        super().done()

    def get_font_size(self, height, font_name="helvetica"):
        d = pyglet.text.document.UnformattedDocument("abcdefghijk")
        d.set_style(
            0, -1, dict(font_name=font_name, font_size=10)
        )
        size_10_font = d.get_font()
        size_10_height = size_10_font.ascent - size_10_font.descent
        d.set_style(
            0, -1, dict(font_name=font_name, font_size=20)
        )
        size_20_font = d.get_font()
        size_20_height = size_20_font.ascent - size_20_font.descent
        h_diff = size_20_height - size_10_height
        font_size = int(
            (height - size_10_height) * 10 / h_diff + 10
        )
        return font_size

    def on_caret_action(self, method_name, *args, **kwargs):
        if self.caret:
            f = getattr(self.caret, method_name)
            f(*args, **kwargs)
        self.text = self.document.text

    def set_caret_visible(self):
        if self.caret:
            self.caret.visible = True

    def set_caret_hidden(self):
        if self.caret:
            self.caret.visible = False


class TextCaretEvent(EventBase):
    registered_events = (
        "on_mouse_press", "on_mouse_drag", "on_text",
        "on_text_motion", "on_text_motion_select", "on_key_press",
    )
    _payload_attrs = (
        "caret_id", "msg_hash"
    )

    def __init__(
            self, message, caret_id, msg_kwargs=None,
            priority=0):
        """Event of text caret

        :param TextCaret text_caret_graphic:
        :param message:
        :param msg_kwargs:
        """
        self.priority = priority
        self.msg_constructor = message
        self.msg_kwargs = msg_kwargs or dict()
        self.msg_hash = str(message) + str(msg_kwargs)
        super().__init__()
        self.caret_id = caret_id

    @property
    def text_caret(self):
        tc = None
        for i, t in TEXT_FIELDS.items():
            if i == self.caret_id:
                tc = t
            else:
                t.set_caret_hidden()
        return tc

    def is_in_area(self, x, y):
        c_x, c_y = self.text_caret.x, self.text_caret.y
        width = self.text_caret.width
        height = self.text_caret.height
        flag = c_x <= x <= c_x+width and c_y <= y <= c_y+height
        if not flag:
            self.text_caret.set_caret_hidden()
        return flag

    def on_mouse_press(self, x, y, button, modifiers):
        if self.is_in_area(x, y):
            FOCUSED_ID[0] = self.caret_id
            self.text_caret.on_caret_action(
                "on_mouse_press", x, y, button, modifiers
            )
            return True, None
        else:
            if FOCUSED_ID[0] == self.caret_id:
                FOCUSED_ID[0] = 0
            return False, None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if FOCUSED_ID[0] == self.caret_id:
            self.text_caret.on_caret_action(
                "on_mouse_drag", x, y, dx, dy, buttons, modifiers
            )
            msg = self.msg_constructor(
                text=self.text_caret.text, **self.msg_kwargs
            )
            return True, msg
        else:
            return False, None

    def on_text(self, text):
        if FOCUSED_ID[0] == self.caret_id:
            self.text_caret.on_caret_action(
                "on_text", text
            )
            msg = self.msg_constructor(
                text=self.text_caret.text, **self.msg_kwargs
            )
            return True, msg
        else:
            return False, None

    def on_text_motion(self, motion):
        if FOCUSED_ID[0] == self.caret_id:
            self.text_caret.on_caret_action(
                "on_text_motion", motion
            )
            msg = self.msg_constructor(
                text=self.text_caret.text, **self.msg_kwargs
            )
            return True, msg
        else:
            return False, None

    def on_text_motion_select(self, motion):
        if FOCUSED_ID[0] == self.caret_id:
            self.text_caret.on_caret_action(
                "on_text_motion_select", motion
            )
            msg = self.msg_constructor(
                text=self.text_caret.text, **self.msg_kwargs
            )
            return True, msg
        else:
            return False, None


class EventManager(object):

    def __init__(self, pyglet_window_api_handler, proxy):
        """Manage events

        :param PygletWindowApiHandler pyglet_window_api_handler:
        :param pathfinder.pygletelm.backend.StateProxy proxy:
        """
        self.api_handler = pyglet_window_api_handler
        self.api_handler.actions = [self.on_action]
        self.proxy = proxy
        self.events = dict()

    def update_events(self, new_events):
        new, update, delete = cache.diff(
            self.get_tags(self.events.values()), self.get_tags(new_events)
        )
        for d_id in delete:
            self._delete_event(d_id)
        for d in new_events:
            if d.identity in new:
                self._add_event(d)

    @classmethod
    def get_tags(cls, l):
        return [a.tag for a in l]

    def _delete_event(self, identity):
        if identity not in self.events:
            return
        d = self.events.pop(identity)
        d.done()

    def _add_event(self, event):
        self.events[event.identity] = event

    def on_action(self, action_name, *args, **kwargs):
        for e in sorted(self.events.values(), key=lambda x: -x.priority):
            if action_name not in e.registered_events:
                continue
            f = getattr(e, action_name)
            triggered, msg = f(*args, **kwargs)
            if triggered:
                if msg == WindowApiChangeCursor:
                    self.api_handler.window.set_mouse_cursor(msg.cursor)
                elif msg is not None:
                    self.proxy.push_message(msg)
                return True
        return False


class Provider(object):

    def __init__(
            self, proxy, resizable_window=True, retina_display=False,
            initial_window_size=(1024, 1024)):
        self.window_obj = pyglet.window.Window(resizable=resizable_window)
        self.window_obj.set_size(*initial_window_size)
        self.batch = pyglet.graphics.Batch()
        self.proxy = proxy
        self.window_api_handler = PygletWindowApiHandler(
            self.batch, self.window_obj, proxy=proxy, retina_display=retina_display
        )
        self.graphic_manager = GraphicManager(self.batch)
        self.event_manager = EventManager(self.window_api_handler, self.proxy)
        self.proxy.view_handlers.register(self.handle_view)
        self.window_obj.push_handlers(self.window_api_handler)

    def handle_view(self, view_result):
        """Handling the return value of view

        :param View view_result:
        """
        drawings = view_result.drawings
        self.graphic_manager.update_drawings(drawings)
        events = view_result.events
        self.event_manager.update_events(events)


def show_view_for_debug(view, timeout=0):
    """Show window of given `view()` function

    :param Callable view: returns the instance of View
    :return:
    """
    window = pyglet.window.Window()
    batch = pyglet.graphics.Batch()
    GlobalWindowInfo.width = window.width
    GlobalWindowInfo.height = window.height
    vs = view()

    @window.event
    def on_draw():
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(
            pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA
        )
        batch.draw()
    for d in vs.drawings:
        d.draw(batch)
    if timeout:
        pyglet.clock.schedule_once(lambda *args: window.close(), timeout)
    pyglet.app.run()


if __name__ == "__main__":
    def view():
        return View(
            simple_circle(x=0.2, y=0.3, radius=0.1),
            simple_triangle(x0=0.3, y0=0.3, x1=0.8, y1=0.4, x2=0.5, y2=0.8)
        )
    show_view_for_debug(view)

