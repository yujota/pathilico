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
from pathilico.app.views.common import Standards, Images, AppLayers
from pathilico.app.header import Api


class NB(object):
    nav_bar_height = 60
    pf_logo_original_height = Images.pf_logo.height
    logo_v_pad = 4
    logo_h_pad = 12
    pf_logo_height = nav_bar_height - 2 * logo_v_pad
    pf_logo_scale = pf_logo_height / pf_logo_original_height
    pf_logo_width = int(Images.pf_logo.width * pf_logo_scale)


class IW(object):
    width = 320
    height = 180
    bot_bar_height = 45
    txt_v_pad = 1
    point_v_pad = 4
    txt_h_pad = 10


def top_nav_bar(model, color=None, text=""):
    win_w, win_h = Api.get_window_width_and_height(model)
    nb_y = win_h - NB.nav_bar_height  # Nav bar's height
    nb_color = color or colors.MetroColors.Emerald
    bar_base = window_api.simple_box(
        x=0, y=nb_y, width=win_w, height=NB.nav_bar_height,
        color=nb_color,
        layer=AppLayers.BaseMenu
    )
    file_icon = window_api.simple_image(
        image=Images.pf_logo, x=NB.logo_h_pad, y=nb_y + NB.logo_v_pad,
        layer=AppLayers.MenuIcon, scale=NB.pf_logo_scale
    )
    prime_text_str = text or "Select file to open"
    prime_text = window_api.text_field(
        x=2 * NB.logo_h_pad + NB.pf_logo_width, y=nb_y + 2 * NB.logo_v_pad,
        width=300,
        height=NB.nav_bar_height - 4 * NB.logo_v_pad,
        color=colors.WhiteText, font_color=colors.WhiteText,
        layer=AppLayers.MenuIcon,
        text=prime_text_str,
        background_color=(0, 0, 0, 0)
    )
    shadow = window_api.simple_box(
        x=0, y=nb_y-Standards.shadow, width=win_w, height=Standards.shadow,
        layer=AppLayers.Shadow,
        color=Standards.shadow_color
    )
    vs = window_api.View(file_icon, bar_base, shadow, prime_text)
    return window_api.View(vs)


def card_widget(x=0, y=0):
    mock_content = window_api.simple_box(
        x=x, y=y+IW.bot_bar_height, width=IW.width,
        height=IW.height-IW.bot_bar_height,
        color=colors.MetroColors.Lime,
        layer=AppLayers.BaseMenu
    )
    content_height = 0
    bottom_bar = window_api.simple_box(
        x=x, y=y, width=IW.width,
        height=IW.bot_bar_height,
        color=colors.MetroColors.Cyan,
        layer=AppLayers.BaseMenu
    )
    content_height += IW.bot_bar_height
    mock_content = window_api.simple_box(
        x=x, y=y+content_height, width=IW.width,
        height=IW.height-IW.bot_bar_height,
        color=colors.MetroColors.Lime,
        layer=AppLayers.BaseMenu
    )
    content_height += IW.height - IW.bot_bar_height
    top_bar = window_api.simple_box(
        x=x, y=y+content_height, width=IW.width,
        height=IW.bot_bar_height,
        color=colors.MetroColors.Green,
        layer=AppLayers.BaseMenu
    )
    bar_text_str = "aiba.svs"
    bar_text = window_api.text_field(
        x=x+IW.txt_h_pad, y=y+2*IW.txt_v_pad,
        width=IW.width-2*IW.txt_h_pad,
        height=IW.bot_bar_height-2*IW.txt_v_pad,
        color=colors.WhiteText, font_color=colors.WhiteText,
        layer=AppLayers.MenuIcon,
        text=bar_text_str,
        background_color=(0, 0, 0, 0)
    )
    vs = window_api.View(bottom_bar, bar_text, top_bar, mock_content)
    return vs


def image_widget(x=0, y=0):
    mock_img = window_api.simple_box(
        x=x, y=y+IW.bot_bar_height, width=IW.width,
        height=IW.height-IW.bot_bar_height,
        color=colors.MetroColors.Lime,
        layer=AppLayers.BaseMenu
    )
    bottom_bar = window_api.simple_box(
        x=x, y=y, width=IW.width,
        height=IW.bot_bar_height,
        color=colors.MetroColors.Green,
        layer=AppLayers.BaseMenu
    )
    bar_text_str = "aiba.svs"
    bar_text = window_api.text_field(
        x=x+IW.txt_h_pad, y=y+2*IW.txt_v_pad,
        width=IW.width-2*IW.txt_h_pad,
        height=IW.bot_bar_height-2*IW.txt_v_pad,
        color=colors.WhiteText, font_color=colors.WhiteText,
        layer=AppLayers.MenuIcon,
        text=bar_text_str,
        background_color=(0, 0, 0, 0)
    )
    vs = window_api.View(mock_img, bottom_bar, bar_text)
    return vs


def simple_txt(x=0, y=0):
    bottom_bar = window_api.simple_box(
        x=x, y=y, width=IW.width,
        height=IW.bot_bar_height,
        color=colors.WhiteText,
        layer=AppLayers.BaseMenu
    )
    icon_box = window_api.simple_box(
        x=x, y=y+IW.point_v_pad, width=IW.txt_h_pad,
        height=IW.bot_bar_height-2*IW.point_v_pad,
        color=colors.MetroColors.Orange,
        layer=AppLayers.BaseMenu
    )
    bar_text_str = "aiba.svs"
    bar_text = window_api.text_field(
        x=x+IW.txt_h_pad*2, y=y+2*IW.txt_v_pad,
        width=IW.width-2*IW.txt_h_pad,
        height=IW.bot_bar_height-2*IW.txt_v_pad,
        color=colors.WhiteText, font_color=colors.PrimaryText,
        layer=AppLayers.MenuIcon,
        text=bar_text_str,
        background_color=(0, 0, 0, 0)
    )
    vs = window_api.View(bottom_bar, bar_text, icon_box)
    return vs


def highlighted_simple_txt(x=0, y=0):
    bottom_bar = window_api.simple_box(
        x=x, y=y, width=IW.width,
        height=IW.bot_bar_height,
        color=colors.WhiteText,
        layer=AppLayers.UICard
    )
    highlight_bar = window_api.simple_box(
        x=x, y=y, width=IW.width,
        height=IW.bot_bar_height,
        color=colors.change_transparency(colors.MetroColors.Lime, 0.5),
        layer=AppLayers.UICardHighLight
    )
    icon_box = window_api.simple_box(
        x=x, y=y+IW.point_v_pad, width=IW.txt_h_pad,
        height=IW.bot_bar_height-2*IW.point_v_pad,
        color=colors.MetroColors.Orange,
        layer=AppLayers.UICardSurface
    )
    delete_icon = window_api.simple_image(
        image=Images.delete_gray_small, x=x+IW.width-24,
        y=y+(IW.bot_bar_height-24)//2,
        layer=AppLayers.UICardIconOnHighLight, scale=1
    )
    pen_icon = window_api.simple_image(
        image=Images.create_gray_small, x=x+IW.width-24*2,
        y=y+(IW.bot_bar_height-24)//2,
        layer=AppLayers.UICardIconOnHighLight, scale=1
    )
    bar_text_str = "aiba.svs"
    bar_text = window_api.text_field(
        x=x+IW.txt_h_pad*2, y=y+2*IW.txt_v_pad,
        width=IW.width-2*IW.txt_h_pad,
        height=IW.bot_bar_height-2*IW.txt_v_pad,
        color=colors.WhiteText, font_color=colors.PrimaryText,
        layer=AppLayers.UICardSurface,
        text=bar_text_str,
        background_color=(0, 0, 0, 0)
    )
    vs = window_api.View(
        bottom_bar, bar_text, icon_box, highlight_bar, delete_icon, pen_icon
    )
    return vs


def file_select_view(model):
    vs = list()
    vs.append(top_nav_bar(model))
    vs.append(image_widget(100, 100))
    vs.append(card_widget(700, 100))
    vs.append(simple_txt(100, 400))
    vs.append(highlighted_simple_txt(700, 400))
    return window_api.View(*vs)