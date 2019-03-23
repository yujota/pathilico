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
from pathilico.app.message import Msg
from pathilico.app.views.common import AppLayers
from pathilico.app.views.navigation import navigation_view
from pathilico.app.views.annotation_view import annotation_view
from pathilico.app.header import Api


def pathology_view(model):
    vs = [
        navigation_view(model),
        pathology_images(model),
        pathology_view_events(model),
        annotation_view(model)
    ]
    return window_api.View(*vs)


def pathology_images(model):
    imgs = list()
    for x, y, img in Api.get_pathology_tile_images_for_display(model):
        i = window_api.simple_image(
            x=x, y=y, image=img, layer=AppLayers.PathologyImage
        )
        imgs.append(i)
    return window_api.View(*imgs)


def pathology_view_events(model):
    if Api.is_annotation_mode(model, "pan"):
        vs = [
            viewer_mode_mouse_events(model),
            pathology_keyboard_shortcuts(model)
        ]
        return window_api.View(*vs)
    else:
        return window_api.View()


def viewer_mode_mouse_events(model):
    return window_api.View(
        window_api.mouse_drag_area(0, 0, 10000, 10000, message=Msg.Move),
        window_api.mouse_scroll_area(
            0, 0, 10000, 10000, message=Msg.RescaleByMouseScroll
        ),
        window_api.mouse_double_click_area(
            0, 60, 10000, 10000, message=Msg.Enlarge
        ),
        window_api.mouse_double_click_area(
            0, 60, 10000, 10000, message=Msg.Shrink, modifiers="MOD_SHIFT",
            priority=101
        )
    )


def pathology_keyboard_shortcuts(model):
    win_w, win_h = Api.get_window_width_and_height(model)
    c_x, c_y = win_w // 2, win_h // 2
    return window_api.View(
        window_api.shortcut_key_release_event(
            symbol="PLUS", message=Msg.Enlarge, msg_kwargs=dict(x=c_x, y=c_y)
        ),
        window_api.shortcut_key_release_event(
            symbol="MINUS", message=Msg.Shrink, msg_kwargs=dict(x=c_x, y=c_y)
        ),
        window_api.shortcut_key_release_event(
            symbol="O", modifiers="MOD_CTRL", message=Msg.AskFilePath
        ),
        window_api.shortcut_key_release_event(
            symbol="O", modifiers="MOD_COMMAND", message=Msg.AskFilePath
        )
    )
