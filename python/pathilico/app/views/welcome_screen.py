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

import pathilico
import pathilico.pygletelm.window as window_api
import pathilico.app.views.color as colors
from pathilico.app.views.common import Images, AppLayers
from pathilico.app.header import Api
from pathilico.app.message import Msg


AIBA_PATH = os.path.expanduser("~/DataForML/svs/aiba.svs")


def welcome_screen(model):
    img = Images.welcome_screen_image
    win_w, win_h = Api.get_window_width_and_height(model)
    win_rate = win_h / win_w
    img_rate = img.height / img.width
    if win_rate > img_rate:
        scale = win_h / img.height * 1.1
    else:
        scale = win_w / img.width * 1.1
    si = window_api.simple_image(
        y=0, x=0, image=img, layer=AppLayers.Bottom,
        image_id="Splash", scale=scale
    )
    y_position = int(win_h*0.4)
    title_txt = window_api.text_field(
        text="Pathfinder", font_name="Mono",
        x=100, y=y_position+50, width=400, height=80,
        background_color=(0, 0, 0, 0), font_color=(255, 255, 255, 255),
        layer=AppLayers.MenuIcon, padding_left=10,
    )
    desc_text = window_api.text_field(
        text="An annotation app for whole slide images",
        x=100, y=y_position, width=400, height=50,
        background_color=(0, 0, 0, 0), font_color=(255, 255, 255, 255),
        layer=AppLayers.MenuIcon, padding_left=15, padding_bottom=15,
        padding_top=5
    )
    version_str = pathilico.__version__
    if len(version_str) > 13:
        version_str = version_str[:13]
    else:
        version_str = "" * (13 - len(version_str)) + version_str
    version_text = window_api.text_field(
        text=version_str,
        x=350, y=y_position+50+80, width=150, height=40,
        background_color=(0, 0, 0, 0), font_color=(255, 255, 255, 255),
        layer=AppLayers.MenuIcon, padding_left=15, padding_bottom=0,
        padding_top=12
    )
    proj_text = window_api.text_field(
        text="Deep Ackerman", font_bold=True,
        x=110, y=y_position+50+80+5, width=160, height=35,
        background_color=colors.MetroColors.Orange,
        font_color=(255, 255, 255, 255),
        layer=AppLayers.MenuIcon, padding_left=10, padding_bottom=3,
        padding_top=3
    )
    box = window_api.simple_box(
        x=90, y=int(win_h*0.4), width=450, height=170, color=(0, 0, 0, 190),
        layer=AppLayers.BaseMenu
    )
    white_line = window_api.simple_box(
        x=110, y=int(win_h*0.4)+50, width=350, height=3,
        color=(255, 255, 255, 255), layer=AppLayers.MenuIcon
    )
    progress_line = window_api.simple_box(
        x=0, y=win_h-4, width=350, height=4,
        color=(0, 0, 180, 180), layer=AppLayers.BaseMenu
    )
    load_aiba_svs = window_api.simple_box(
        x=0, y=0, width=win_w, height=60,
        color=(30, 30, 30, 230), layer=AppLayers.BaseMenu
    )
    load_aiba_text = window_api.text_field(
        text="Load aiba.svs",
        x=win_w-180, y=10, width=170, height=40,
        background_color=colors.MetroColors.Cyan,
        font_color=(255, 255, 255, 255),
        layer=AppLayers.MenuIcon, padding_left=10, padding_bottom=3,
        padding_top=3
    )
    touch_area = window_api.mouse_press_area(
        x=win_w-180, y=10, width=70, height=40, msg_kwargs=dict(path=AIBA_PATH),
        message=Msg.FileSelected, layer=AppLayers.MenuIcon, priority=AppLayers.MenuIcon
    )
    return window_api.View(
        si, box, white_line, title_txt, version_text, desc_text, proj_text,
        progress_line, load_aiba_svs, load_aiba_text, touch_area
    )
