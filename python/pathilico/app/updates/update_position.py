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
import pathilico.app.port as async


TARGET_MESSAGES = (Msg.Move, Msg.Shrink, Msg.Enlarge, Msg.Rescale)


# APIs for update
def update(msg, model):
    """Positional update

    :param pathfinder.app.message.Msg msg:
    :param pathfinder.app.model.Model model:
    :return:
    """
    if msg == Msg.Move:
        return move(msg, model)
    elif msg == Msg.Shrink:
        return shrink(msg, model)
    elif msg == Msg.Enlarge:
        return enlarge(msg, model)
    elif msg == Msg.Rescale:
        return rescale(msg, model)
    else:
        return model, Commands()


def move(msg, model):
    model = Api.move(model, msg.dx, msg.dy)
    cmds = get_image_queries(model)
    return model, cmds


def rescale(msg, model):
    if msg.enlarge is 1:
        if Api.is_enlargeable(model):
            model = Api.enlarge(model, msg.win_x, msg.win_y)
            cmds = get_image_queries(model)
            return model, cmds
    elif msg.enlarge is -1:
        if Api.is_shrinkable(model):
            model = Api.shrink(model, msg.win_x, msg.win_y)
            cmds = get_image_queries(model)
            return model, cmds
    return model, NO_COMMANDS


def shrink(msg, model):
    if Api.is_shrinkable(model):
        model = Api.shrink(model, msg.x, msg.y)
        cmds = get_image_queries(model)
        return model, cmds
    else:
        return model, Commands()


def enlarge(msg, model):
    if Api.is_enlargeable(model):
        model = Api.enlarge(model, msg.x, msg.y)
        cmds = get_image_queries(model)
        return model, cmds
    else:
        return model, Commands()


def get_image_queries(model):
    cmds = Commands(
        get_openslide_queries(model),
        get_grouped_annotation_image_queries(model)
    )
    return cmds


def get_openslide_queries(model):
    bound = Api.get_bound_for_window(model)
    pathology_ids2show = Api.get_ids_on_districts(
        model, bounds=[bound], data_type="pathology"
    )
    model, pathology_ids, pathology_queries = Api.collect_queries_for_request(
        model, pathology_ids2show
    )
    if pathology_queries:
        f_p = Api.get_file_path(model)
        m = Msg.PathologyRegionAcquired
        qs = [
            (f_p, q.location, q.level, q.size, m, dict(pathology_id=i, query=q))
            for q, i in zip(pathology_queries, pathology_ids)
        ]
        cmds = async.generate_openslide_read_region_commands(qs)
    else:
        cmds = Commands()
    return cmds


def get_grouped_annotation_image_queries(model):
    bound = Api.get_bound_for_window(model)
    ga_ids2show = Api.get_ids_on_districts(
        model, bounds=[bound], data_type="grouped_annotation"
    )
    model, ga_ids, ga_queries = Api.collect_queries_for_request(
        model, ga_ids2show
    )
    if ga_queries:
        m = Msg.GroupedAnnotationImageAcquired
        qs = [
            (m, dict(ga_id=i, query=q), *q)
            for q, i in zip(ga_queries, ga_ids)
        ]
        cmds = async.group_multi_annotation_image(qs)
    else:
        cmds = Commands()
    return cmds
