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
import pathilico.pygletelm.window as window_api
import pathilico.app.views.color as colors
import pathilico.app.views.widgets as widgets
from pathilico.app.views.common import AppLayers, Standards
from pathilico.app.header import Api
from pathilico.app.message import Msg


def file_select_view(model):
    nb_txt = "Select file to open"
    win_w, win_h = Api.get_window_width_and_height(model)
    background = window_api.simple_box(
        x=0, y=0, width=win_w, height=win_h, color=colors.WhiteText,
        layer=AppLayers.Bottom
    )
    names, paths = Api.get_explored_file_names_and_paths(model)
    vs = [
        widgets.top_nav_bar(
            model, color=colors.MetroColors.Emerald, text=nb_txt
        ),
        background,
        list_file_names(model, names, paths),
    ]
    return window_api.View(*vs)


class STB(object):
    width = 320
    height = 45
    txt_v_pad = 1
    txt_h_pad = 10
    v_margin = 30
    h_margin = 40
    shadow_length = 3


def simple_txt_button(x, y, txt, color, message, msg_kwargs=None):
    bottom_bar = window_api.simple_box(
        x=x, y=y, width=STB.width, height=STB.height,
        color=color, layer=AppLayers.BaseMenu
    )
    shadow_bar = window_api.simple_box(
        x=x, y=y-STB.shadow_length, width=STB.width+STB.shadow_length,
        height=STB.height+STB.shadow_length,
        color=Standards.shadow_color, layer=AppLayers.Shadow
    )
    bar_text = window_api.text_field(
        x=x+STB.txt_h_pad, y=y+STB.txt_v_pad,
        width=STB.width-2*STB.txt_h_pad,
        height=STB.height-2*STB.txt_v_pad,
        color=colors.WhiteText, font_color=colors.WhiteText,
        layer=AppLayers.MenuIcon,
        text=txt,
        background_color=(0, 0, 0, 0)
    )
    bt = window_api.mouse_press_area(
        y=y, x=x, width=STB.width,
        height=STB.height,
        message=message, msg_kwargs=msg_kwargs,
        priority=1000
    )
    vs = window_api.View(bottom_bar, bar_text, shadow_bar, bt)
    return vs


def list_file_names(model, file_names, file_paths):
    vs = list()
    win_w, win_h = Api.get_window_width_and_height(model)
    num_columns = (win_w - STB.h_margin) // (STB.width + STB.h_margin) or 1
    num_rows = len(file_names) // num_columns
    if len(file_names) % num_columns is not 0:
        num_rows += 1
    h_margin = win_w - STB.width * num_columns - STB.h_margin * (num_columns-1)
    left_h_margin = h_margin // 2
    for r_i in range(num_rows):
        y = win_h - 60 - (r_i + 1) * (STB.v_margin + STB.height)
        for c_i in range(num_columns):
            ind = r_i * num_columns + c_i
            if ind >= len(file_names):
                break
            f_name, f_path = file_names[ind], file_paths[ind]
            x = left_h_margin + (STB.width + STB.h_margin) * c_i
            btn = simple_txt_button(
                x=x, y=y, txt=f_name, color=colors.MetroColors.Green,
                message=Msg.FileSelected, msg_kwargs=dict(path=f_path)
            )
            vs.append(btn)
    return window_api.View(*vs)
