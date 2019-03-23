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
"""This module provides functions for coordinates-system
"""
from pathilico.app.header import Api


# Essence APIs
class PositionModel(object):
    def __init__(self):
        self.x, self.y, self.level = 0, 0, 0


def move(position_model, dx=0, dy=0):
    """Move point of view

    :param PositionModel position_model:
    :param int dx:
    :param int dy:
    :return PositionModel:
    """
    position_model.x -= dx
    position_model.y -= dy
    return position_model


def rescale(x, y, point_x, point_y, current_scale, next_scale):
    r = current_scale / next_scale
    ref_x, ref_y = x + point_x, y + point_y
    new_x = int(ref_x*r) - point_x
    new_y = int(ref_y*r) - point_y
    return new_x, new_y


def enlarge(position_model, point_x, point_y, level_downsamples):
    """Enlarge pathology images (narrow field of vision) by the given point

    :param PositionModel position_model:
    :param int point_x:
        x-axis length from slide's left to the point (in current level)
    :param int point_y:
    :param level_downsamples:
    :return PositionModel:
    """
    current_scale = level_downsamples[position_model.level]
    next_scale = level_downsamples[position_model.level-1]
    new_x, new_y = rescale(
        position_model.x, position_model.y, point_x, point_y, current_scale,
        next_scale
    )
    position_model.x = new_x
    position_model.y = new_y
    position_model.level -= 1
    return position_model


def shrink(position_model, point_x, point_y, level_downsamples):
    """Shrink pathology images (broaden field of vision) by the given point

    :param PositionModel position_model:
    :param point_x:
    :param point_y:
    :param level_downsamples:
    :return PositionModel:
    """
    current_scale = level_downsamples[position_model.level]
    next_scale = level_downsamples[position_model.level+1]
    new_x, new_y = rescale(
        position_model.x, position_model.y, point_x, point_y, current_scale,
        next_scale
    )
    position_model.x = new_x
    position_model.y = new_y
    position_model.level += 1
    return position_model


# Actual implementations for Api
def _move(model, dx=0, dy=0):
    model.position = move(model.position, dx=dx, dy=dy)
    return model


def is_enlargeable(model):
    """Check if pathology image has upper level than current

    :param pathfinder.app.model.Model model:
    :return bool:
    """
    if model.position.level <= 0:
        return False
    else:
        return True


def is_shrinkable(model):
    """Check if pathology image has lower level than current

    :param pathfinder.app.model.Model model:
    :return bool:
    """
    num_levels = Api.get_num_levels(model)
    if model.position.level >= num_levels - 1:
        return False
    else:
        return True


def _enlarge(model, point_x, point_y):
    level_downsamples = Api.get_level_downsamples(model)
    model.position = enlarge(
        model.position, point_x, point_y, level_downsamples
    )
    return model


def _shrink(model, point_x, point_y):
    level_downsamples = Api.get_level_downsamples(model)
    model.position = shrink(
        model.position, point_x, point_y, level_downsamples
    )
    return model


def get_bound_for_window(model):
    p_model = model.position
    win_w, win_h = Api.get_window_width_and_height(model)
    b = (
        p_model.x, p_model.y, p_model.x+win_w, p_model.y+win_h, p_model.level
    )
    return b


def get_level0_coordinates(model, window_x, window_y):
    gl_x = model.position.x + window_x
    gl_y = model.position.y + window_y
    level_downsamples = Api.get_level_downsamples(model)
    scale = level_downsamples[model.position.level]
    lv0_x = gl_x * scale
    lv0_y = gl_y * scale
    return lv0_x, lv0_y


def get_window_coordinates(model, gl_x, gl_y, given_level=0):
    l_ds = Api.get_level_downsamples(model)
    current_level = model.position.level
    if current_level == given_level:
        win_x = gl_x - model.position.x
        win_y = gl_y - model.position.y
        return win_x, win_y
    elif current_level > given_level:
        scale = l_ds[current_level] // l_ds[given_level]
        win_x = gl_x // scale - model.position.x
        win_y = gl_y // scale - model.position.y
        return win_x, win_y
    else:
        scale = l_ds[given_level] // l_ds[current_level]
        win_x = gl_x * scale - model.position.x
        win_y = gl_y * scale - model.position.y
        return win_x, win_y


Api.register(PositionModel)
Api.register_as(_move, "move")
Api.register(is_enlargeable)
Api.register(is_shrinkable)
Api.register_as(_enlarge, "enlarge")
Api.register_as(_shrink, "shrink")
Api.register(get_bound_for_window)
Api.register(get_level0_coordinates)
Api.register(get_window_coordinates)
