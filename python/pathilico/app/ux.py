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
import pathilico.app.geometry as geometry

from pathilico.app.header import Api


# Essential APIs
class UXModel(object):
    def __init__(self):
        self.window_width, self.window_height = 640, 480
        self.is_delete_dragging = False
        self.delete_drag_start_at = (-1, -1)
        self.delete_drag_at = (-1, -1)
        self.is_draw_line_dragging = False
        self.draw_line_tmp_points = list()
        self.annotation_point_size = 4


def update_window_size(ux_model, width, height):
    ux_model.window_width = width
    ux_model.window_height = height
    return ux_model


# Actual implementations for Api
def get_window_width_and_height(model):
    w = model.ux.window_width
    h = model.ux.window_height
    return w, h


def update_window_width_and_height(model, width, height):
    model.ux = update_window_size(model.ux, width, height)
    return model


def get_delete_drag_start_coordinates(model):
    result = model.ux.delete_drag_start_at
    return result


def start_delete_drag(model, x, y):
    model.ux.delete_drag_start_at = (x, y)
    model.ux.is_delete_dragging = True
    return model


def update_delete_drag(model, x, y):
    if model.ux.is_delete_dragging:
        model.ux.delete_drag_at = (x, y)
    return model


def finish_delete_drag(model):
    model.ux.delete_drag_start_at = (-1, -1)
    model.ux.delete_drag_at = (-1, -1)
    model.ux.is_delete_dragging = False
    return model


def is_delete_dragging(model):
    return model.ux.is_delete_dragging


def is_line_drawing(model):
    return model.ux.is_draw_line_dragging


def get_delete_drag_bound(model):
    sx, sy = model.ux.delete_drag_start_at
    x, y = model.ux.delete_drag_at
    if any([a == -1 for a in [sx, sy, x, y]]):
        return 0, 0, 0, 0
    left, right = sorted([sx, x])
    bottom, top = sorted([sy, y])
    bound = (left, bottom, right, top)
    return bound


def start_line_drawing(model, x, y):
    model.ux.draw_line_tmp_points = [x, y]
    model.ux.is_draw_line_dragging = True
    return model


def update_line_drawing(model, x, y, dx, dy):
    if model.ux.is_draw_line_dragging is False:
        return model, False, tuple()
    if len(model.ux.draw_line_tmp_points) < 2*3:
        model.ux.draw_line_tmp_points.extend([x, y])
        return model, False, tuple()
    is_closed, closed_vs = geometry.get_closed_curve_points(
        x, y, dx, dy, model.ux.draw_line_tmp_points, dim_points=1
    )
    if is_closed:
        model = finish_line_drawing(model)
        return model, True, closed_vs
    else:
        model.ux.draw_line_tmp_points.extend([x, y])
        return model, False, tuple()


def finish_line_drawing(model):
    model.ux.draw_line_tmp_points = list()
    model.ux.is_draw_line_dragging = False
    return model


def get_drawing_line_coordinates(model):
    return tuple(model.ux.draw_line_tmp_points)


Api.register(UXModel)
Api.register(get_window_width_and_height)
Api.register(update_window_width_and_height)
Api.register(get_delete_drag_start_coordinates)
Api.register(start_delete_drag)
Api.register(update_delete_drag)
Api.register(finish_delete_drag)
Api.register(is_delete_dragging)
Api.register(get_delete_drag_bound)
Api.register(start_line_drawing)
Api.register(update_line_drawing)
Api.register(finish_line_drawing)
Api.register(is_line_drawing)
Api.register(get_drawing_line_coordinates)
