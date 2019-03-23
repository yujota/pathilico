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

import pyglet

import pathilico.pygletelm.window as window_api
import pathilico.app.views.color as colors
from pathilico.misc.package import get_path


class Images(object):
    icon_dir = get_path("assets/icons")
    more_icon = pyglet.image.load(
        os.path.join(icon_dir, "more_vert_white_32x32.png")
    )
    file_icon = pyglet.image.load(
        os.path.join(icon_dir, "insert_drive_file_grey_36x36.png")
    )
    pan_icon = pyglet.image.load(
        os.path.join(icon_dir, "pan_tool_white_36x36.png")
    )
    add_location_icon = pyglet.image.load(
        os.path.join(icon_dir, "add_location_white_36x36.png")
    )
    delete_icon = pyglet.image.load(
        os.path.join(icon_dir, "delete_white_36x36.png")
    )
    pen_icon = pyglet.image.load(
        os.path.join(icon_dir, "pen_white_36x36.png")
    )
    create_gray_small = pyglet.image.load(
        os.path.join(icon_dir, "create_grey_24x24.png")
    )
    delete_gray_small = pyglet.image.load(
        os.path.join(icon_dir, "delete_grey_24x24.png")
    )
    add_location_black_small = pyglet.image.load(
        os.path.join(icon_dir, "add_location_black_24x24.png")
    )
    create_black_small = pyglet.image.load(
        os.path.join(icon_dir, "create_black_24x24.png")
    )
    delete_black_small = pyglet.image.load(
        os.path.join(icon_dir, "delete_black_24x24.png")
    )
    pan_black_small = pyglet.image.load(
        os.path.join(icon_dir, "pan_tool_black_24x24.png")
    )
    zoom_out = pyglet.image.load(
        os.path.join(icon_dir, "zoom_out_black_24x24.png")
    )
    zoom_in = pyglet.image.load(
        os.path.join(icon_dir, "zoom_in_black_24x24.png")
    )
    arrow_right = pyglet.image.load(
        os.path.join(icon_dir, "keyboard_arrow_right_white_36x36.png")
    )
    arrow_left = pyglet.image.load(
        os.path.join(icon_dir, "keyboard_arrow_left_white_36x36.png")
    )
    pf_logo = pyglet.image.load(
        os.path.join(icon_dir, "logo.png")
    )


class AppLayers(window_api.LayerList):
    Bottom = window_api.Layer()
    PathologyImage = window_api.Layer()
    AnnotationPoint = window_api.Layer()
    AnnotationPolygon = window_api.Layer()
    AnnotationGroupedImage = window_api.Layer()
    AnnotationTmpLine = window_api.Layer()
    DeleteBox = window_api.Layer()
    Shadow = window_api.Layer()
    BaseMenu = window_api.Layer()
    UIBackground = window_api.Layer()
    UICard = window_api.Layer()
    UICardSurface = window_api.Layer()
    UICardHighLight = window_api.Layer()
    UICardIconOnHighLight = window_api.Layer()
    MenuIcon = window_api.Layer()


class Standards(object):
    bottom_color_bar_height = 60
    top_nav_bar_height = 60
    padding = 14
    half_padding = 7
    shadow = 2
    shadow_color = colors.change_transparency(colors.SecondaryText, 0.5)
    icon_size = 36


def background(model):
    bg_box = window_api.simple_box(
        x=0, y=0, width=model.window.width, height=model.window.height,
        layer=AppLayers.Bottom, color=colors.WhiteText
    )
    return window_api.View(bg_box)


