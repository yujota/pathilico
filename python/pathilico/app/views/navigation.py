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
from pathilico.app.message import Msg
import pathilico.app.views.widgets as widgets
from pathilico.app.views.common import Standards, Images, AppLayers
from pathilico.app.header import Api


MODE2ICON = {
    'view': Images.pan_icon,
    'point_annotation': Images.add_location_icon
}
MODE2NEXT_MODE = {
    'view': "point_annotation",
    "point_annotation": "view",
}


def navigation_view(model):
    vs = [
        top_nav_bar(model),
        change_annotation_mode_buttons(model),
        zoom_in_out_buttons(model),
        bottom_annotation_color_bar(model)
    ]
    return window_api.View(*vs)


def top_nav_bar(model):
    text = Api.get_display_name(model)
    _, selected_color, _ = \
        Api.get_selected_annotation_category_id_color_and_name(model)
    return widgets.top_nav_bar(model, text=text, color=selected_color)


class BAC(object):  # settings for Bottom Annotation Color bar
    height = 48
    txt_h_pad = 6
    txt_v_pad = 3
    default_width = 120
    icon_size = 36


def bottom_arrow_button(
        x, color, message, icon_image, msg_kwargs=None, width=BAC.height,
        height=BAC.height, y=0):
    vs = [
        window_api.simple_box(
            y=y, x=x, width=width, height=height,
            layer=AppLayers.BaseMenu,
            color=color
        ),
        window_api.simple_image(
            image=icon_image, layer=AppLayers.MenuIcon,
            x=x + (width - 36) // 2,
            y=y + (height - 36) // 2,
        ),
        window_api.mouse_press_area(
            y=y, x=x, width=width, height=height,
            message=message, msg_kwargs=msg_kwargs,
            priority=1000000
        )
    ]
    return window_api.View(*vs)


def bottom_color_button(
        x, width, text, color, message, msg_kwargs=None, y=0,
        height=BAC.height):
    vs = [
        window_api.simple_box(
            y=y, x=x, width=width,
            height=height,
            layer=AppLayers.BaseMenu,
            color=color
        ),
        window_api.text_field(
            x=x+BAC.txt_h_pad, y=y+BAC.txt_v_pad,
            width=width-2*BAC.txt_h_pad,
            height=height-2*BAC.txt_v_pad,
            color=colors.WhiteText, font_color=colors.WhiteText,
            layer=AppLayers.MenuIcon,
            text=text,
            background_color=(0, 0, 0, 0)
        ),
        window_api.mouse_press_area(
            y=y, x=x, width=width, height=height,
            message=message, msg_kwargs=msg_kwargs,
            priority=1000
        )
    ]
    return window_api.View(*vs)


def bottom_annotation_color_bar(model):
    category_list, color_list, name_list = \
        Api.get_annotation_categories_colors_and_names(model)
    win_w, win_h = Api.get_window_width_and_height(model)
    num_item2display = win_w // BAC.default_width or 1
    num_colors = len(color_list)
    if num_colors <= num_item2display:
        width = win_w // num_colors
        vs = list()
        for i in range(num_colors):
            if i is num_colors - 1:
                w = win_w - width*(num_colors-1)
            else:
                w = width
            x = i*width
            box = bottom_color_button(
                x, w, text=name_list[i], color=color_list[i],
                message=Msg.AnnotationTypeSelected,
                msg_kwargs=dict(category_id=category_list[i])
            )
            vs.append(box)
        return window_api.View(*vs)
    vs = list()
    total_width = win_w - 2 * BAC.height
    a_index = Api.get_view_model_values(model, ('bottom_bar_index', ))[0]
    left_index = (num_colors + a_index - 1) % num_colors
    left_color = color_list[left_index]
    left_button = bottom_arrow_button(
        x=0, color=left_color, message=Msg.UpdateViewModel,
        icon_image=Images.arrow_left,
        msg_kwargs=dict(keys=('bottom_bar_index',), values=(left_index,))
    )
    vs.append(left_button)
    right_index = (a_index + 1) % num_colors
    right_color = color_list[(a_index+num_item2display)%num_colors]
    right_button = bottom_arrow_button(
        x=win_w-BAC.height, color=right_color,
        message=Msg.UpdateViewModel,
        msg_kwargs=dict(keys=('bottom_bar_index',), values=(right_index,)),
        icon_image=Images.arrow_right
    )
    vs.append(right_button)
    width = total_width // num_item2display
    for i in range(num_item2display):
        if i is num_item2display-1:
            w = total_width - width*(num_item2display-1)
        else:
            w = width
        text = name_list[(i+a_index)%num_colors]
        color = color_list[(i+a_index)%num_colors]
        type_id = category_list[(i+a_index)%num_colors]
        x = i*width + BAC.height
        box = bottom_color_button(
            x, w, text=text, color=color,
            message=Msg.AnnotationTypeSelected,
            msg_kwargs=dict(category_id=type_id)
        )
        vs.append(box)
    return window_api.View(*vs)


class SQB(object):  # Settings for Square Button
    lb_size = 56  # Large button, note that icon size = 36x36
    sb_size = 36  # Small button, note that icon size = 24x24
    lb_icon_size = 36
    sb_icon_size = 24
    lb_h_pad = 20  # Large button, length to left window frame
    sb_h_pad = lb_h_pad + (lb_size - sb_size) // 2
    v_pad = 16
    shadow_length = 3


def change_annotation_mode_buttons(model):
    lb_y = 66
    x = SQB.sb_h_pad
    sm1_y = lb_y + SQB.v_pad + SQB.lb_size
    sm2_y = sm1_y + SQB.v_pad + SQB.sb_size
    sm3_y = sm2_y + SQB.v_pad + SQB.sb_size
    sm_ys = (sm1_y, sm2_y, sm3_y)
    _, selected_color, _ = \
        Api.get_selected_annotation_category_id_color_and_name(model)
    modes = ('pan', 'point', 'area', 'delete')
    flags = [Api.is_annotation_mode(model, m) for m in modes]
    sm_modes = [m for f, m in zip(flags, modes) if f is False]
    a_mode = [m for f, m in zip(flags, modes) if f is True][0]
    large_icon_names = {
        'pan': 'pan_icon', 'point': 'add_location_icon', 'area': 'pen_icon',
        'delete': 'delete_icon'
    }
    small_icon_names = {
        'pan': 'pan_black_small', 'point': 'add_location_black_small',
        'area': 'create_black_small', 'delete': 'delete_black_small'
    }
    vs = [
        large_button(
            lb_y,
            icon_image=getattr(Images, large_icon_names[a_mode]),
            color=selected_color, next_annotation_mode="pan"
        )
    ]
    for i, sm_name in enumerate(sm_modes):
        y = sm_ys[i]
        icon_img = getattr(Images, small_icon_names[sm_name])
        b = small_button(
            x=x, y=y, icon_image=icon_img,
            message=Msg.ChangeAnnotationMode,
            msg_kwargs=dict(new_mode=sm_name)
        )
        vs.append(b)
    return window_api.View(*vs)


def zoom_in_out_buttons(model):
    nb_height = widgets.NB.nav_bar_height
    win_w, win_h = Api.get_window_width_and_height(model)
    sm1_y = win_h - nb_height - SQB.v_pad - SQB.sb_size
    sm2_y = sm1_y - SQB.v_pad - SQB.sb_size
    x = win_w - SQB.sb_h_pad - SQB.sb_size
    point_x = win_w // 2
    point_y = win_h // 2
    enlarge_d = dict(win_x=point_x, win_y=point_y, enlarge=1)
    shrink_d = dict(win_x=point_x, win_y=point_y, enlarge=-1)
    vs = [
        small_button(
            x=x, y=sm1_y, icon_image=Images.zoom_in,
            message=Msg.Rescale, msg_kwargs=enlarge_d
        ),
        small_button(
            x=x, y=sm2_y, icon_image=Images.zoom_out,
            message=Msg.Rescale, msg_kwargs=shrink_d
        )
    ]
    return window_api.View(*vs)


def small_button(
        x, y, icon_image, message, msg_kwargs, color=colors.WhiteText):
    vs = [
        window_api.simple_box(
            y=y, x=x, width=SQB.sb_size + SQB.shadow_length,
            height=SQB.sb_size + SQB.shadow_length,
            layer=AppLayers.Shadow,
            color=Standards.shadow_color
        ),
        window_api.simple_box(
            y=y, x=x, width=SQB.sb_size,
            height=SQB.sb_size,
            layer=AppLayers.BaseMenu,
            color=color
        ),
        window_api.simple_image(
            image=icon_image, layer=AppLayers.MenuIcon,
            x=x + (SQB.sb_size - SQB.sb_icon_size) // 2,
            y=y + (SQB.sb_size - SQB.sb_icon_size) // 2,
        ),
        window_api.mouse_press_area(
            y=y, x=x, width=SQB.lb_size,
            height=SQB.lb_size,
            message=message, msg_kwargs=msg_kwargs,
            priority=1000
        )
    ]
    return window_api.View(*vs)


def large_button(y, icon_image, next_annotation_mode, color=(180, 0, 30, 255)):
    vs = [
        window_api.simple_box(
            y=y, x=SQB.lb_h_pad, width=SQB.lb_size,
            height=SQB.lb_size + SQB.shadow_length,
            layer=AppLayers.Shadow,
            color=Standards.shadow_color
        ),
        window_api.simple_box(
            y=y, x=SQB.lb_h_pad, width=SQB.lb_size,
            height=SQB.lb_size,
            layer=AppLayers.BaseMenu,
            color=color
        ),
        window_api.simple_image(
            image=icon_image, layer=AppLayers.MenuIcon,
            x=SQB.lb_h_pad + (SQB.lb_size - 36) // 2,
            y=y + (SQB.lb_size - 36) // 2,
        ),
        window_api.mouse_press_area(
            y=y, x=SQB.lb_h_pad, width=SQB.lb_size,
            height=SQB.lb_size,
            message=Msg.ChangeAnnotationMode,
            msg_kwargs=dict(new_mode=next_annotation_mode),
            priority=1000000
        )
    ]
    return window_api.View(*vs)


def debug_menu_buttons(model):
    w, _ = Api.get_window_width_and_height(model)
    return window_api.View(
        window_api.button(
            Msg.ExecGroupAnnotation, x=w-100, y=30, height=40,
            width=80, text="Group!!", layer=AppLayers.MenuIcon,
            color=colors.MetroColors.Amber
        )

    )


