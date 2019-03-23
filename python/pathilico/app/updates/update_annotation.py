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
from pathilico.pygletelm.effect import Commands, NO_COMMANDS
from pathilico.app.message import Msg
from pathilico.app.header import Api
from pathilico.app.updates.update_position \
    import get_grouped_annotation_image_queries


TARGET_MESSAGES = (
    Msg.AddPoint, Msg.DeleteDragEndAt, Msg.DrawLineDragEndAt,
    Msg.ExecGroupAnnotation
)


def update(msg, model):
    if msg == Msg.AddPoint:
        return add_point(msg, model)
    elif msg == Msg.DeleteDragEndAt:
        return delete_annotation(msg, model)
    return model, Commands()


def add_point(msg, model):
    x, y = Api.get_level0_coordinates(model, msg.x, msg.y)
    model = Api.add_point_annotation(model, x, y, msg.category_id)
    cmds = get_grouped_annotation_image_queries(model)
    return model, cmds


def delete_annotation(msg, model):
    start_x, start_y = Api.get_delete_drag_start_coordinates(model)
    model = Api.finish_delete_drag(model)
    c_x, c_y = msg.x, msg.y
    if any([a == -1 for a in [start_x, start_y, c_x, c_y]]):
        return model, NO_COMMANDS
    base_x, base_y, _, _, level = Api.get_bound_for_window(model)
    start_x, start_y = base_x + start_x, base_y + start_y
    c_x, c_y = base_x + c_x, base_y + c_y
    left, right = sorted([start_x, c_x])
    bot, top = sorted([start_y, c_y])
    bound = (left, bot, right, top, level)
    point_ids = Api.get_ids_on_districts(model, [bound], data_type="point")
    model = Api.delete_point_annotations(model, point_ids)
    area_ids = Api.get_ids_on_districts(model, [bound], data_type="area")
    model = Api.delete_area_annotations(model, area_ids)
    cmds = get_grouped_annotation_image_queries(model)
    return model, cmds
