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
import itertools

from pathilico.pygletelm.effect import NO_COMMANDS
from pathilico.app.message import Msg
from pathilico.app.updates.update_position import get_image_queries
from pathilico.app.header import Api


TARGET_MESSAGES = (
    Msg.WindowResized, Msg.DeleteDragStartAt, Msg.DeleteDragAt,
    Msg.DrawLineDragStartAt, Msg.DrawLineDragAt, Msg.DrawLineDragEndAt,
    Msg.ChangeMode, Msg.ChangeAnnotationMode, Msg.UpdateViewModel,
    Msg.AnnotationTypeSelected, Msg.WsiFileListAcquired
)


def update(msg, model):
    if msg == Msg.WindowResized:
        return update_window_size(msg, model)
    elif msg == Msg.DeleteDragStartAt:
        return start_delete_drag(msg, model)
    elif msg == Msg.DeleteDragAt:
        return update_delete_drag(msg, model)
    elif msg == Msg.DrawLineDragStartAt:
        return start_line_drawing(msg, model)
    elif msg == Msg.DrawLineDragAt:
        return update_line_drawing(msg, model)
    elif msg == Msg.DrawLineDragEndAt:
        return finish_line_drawing(msg, model)
    elif msg == Msg.ChangeMode:
        return change_mode(msg, model)
    elif msg == Msg.ChangeAnnotationMode:
        return change_annotation_mode(msg, model)
    elif msg == Msg.UpdateViewModel:
        return update_view_model(msg, model)
    elif msg == Msg.AnnotationTypeSelected:
        return update_selected_annotation_type(msg, model)
    elif msg == Msg.WsiFileListAcquired:
        return update_wsi_file_list(msg, model)
    else:
        return model, NO_COMMANDS


def update_window_size(msg, model):
    model = Api.update_window_width_and_height(model, msg.width, msg.height)
    cmds = get_image_queries(model)
    return model, cmds


def start_delete_drag(msg, model):
    model = Api.start_delete_drag(model, msg.x, msg.y)
    return model, NO_COMMANDS


def update_delete_drag(msg, model):
    model = Api.update_delete_drag(model, msg.x, msg.y)
    return model, NO_COMMANDS


def start_line_drawing(msg, model):
    model = Api.start_line_drawing(model, msg.x, msg.y)
    return model, NO_COMMANDS


def update_line_drawing(msg, model):
    model, is_closed, closed_vs = Api.update_line_drawing(
        model, msg.x, msg.y, msg.dx, msg.dy
    )
    if is_closed:
        lv0_closed_vs = itertools.chain(*[
            Api.get_level0_coordinates(model, closed_vs[2*i], closed_vs[2*i+1])
            for i in range(len(closed_vs)//2)
        ])
        lv0_closed_vs = tuple(lv0_closed_vs)
        category_id = \
            Api.get_selected_annotation_category_id_color_and_name(model)[0]
        model = Api.add_area_annotation(
            model, lv0_closed_vs, category_id=category_id
        )
        cmds = get_image_queries(model)
        return model, cmds
    return model, NO_COMMANDS


def finish_line_drawing(msg, model):
    model = Api.finish_line_drawing(model)
    return model, NO_COMMANDS


def change_mode(msg, model):
    model = Api.update_app_mode(model, msg.new_mode)
    return model, NO_COMMANDS


def change_annotation_mode(msg, model):
    model = Api.update_annotation_mode(model, msg.new_mode)
    return model, NO_COMMANDS


def update_view_model(msg, model):
    model = Api.update_view_model_values(model, msg.keys, msg.values)
    return model, NO_COMMANDS


def update_selected_annotation_type(msg, model):
    model = Api.update_selected_annotation_category_id(model, msg.category_id)
    return model, NO_COMMANDS


def update_wsi_file_list(msg, model):
    model = Api.update_explored_file_names_and_paths(
        model, msg.file_names, msg.file_paths
    )
    return model, NO_COMMANDS
