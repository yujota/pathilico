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
from pathilico.pygletelm.effect import Commands
from pathilico.app.message import Msg
from pathilico.app.header import Api
import pathilico.app.port as async
import pathilico.app.ports.pickle_database as database


TARGET_MESSAGES = (
    Msg.FileSelected,
    Msg.SlideInfoAcquired,
    Msg.PathologyRegionAcquired,
    Msg.GroupedAnnotationImageAcquired
)


def update(msg, model):
    if msg == Msg.SlideInfoAcquired:
        return update_pathology_info(msg, model)
    elif msg == Msg.PathologyRegionAcquired:
        return update_pathology_tile_image(msg, model)
    elif msg == Msg.FileSelected:
        return file_selected(msg, model)
    elif msg == Msg.GroupedAnnotationImageAcquired:
        return update_grouped_annotation_image(msg, model)
    else:
        return model, Commands()


def get_load_cmds(model):
    cs = list()
    queries = Api.get_queries_to_load_records(model)
    for (file_path, table_name, data_type) in queries:
        c = database.get_load_record_request(
            Msg.RecordLoaded, file_path, table_name,
            msg_kwargs=dict(data_type=data_type)
        )
        cs.append(c)
    cmds = database.wrap_records(*cs)
    return model, cmds


def file_selected(msg, model):
    if not msg.path:
        return model, Commands()
    cmds = Commands(
        async.get_slide_info(msg=Msg.SlideInfoAcquired, file_path=msg.path),
    )
    return model, cmds


def update_pathology_info(msg, model):
    model = Api.update_pathology(
        model, file_path=msg.file_path, file_name=msg.file_name,
        level_count=msg.level_count, level_dimensions=msg.level_dimensions,
        level_downsamples=msg.level_downsamples
    )
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
        model = Api.update_app_mode(model, "annotation")
        if Api.is_app_mode(model, "annotation"):
            model, load_cmds = get_load_cmds(model)
            cmds = Commands(cmds, load_cmds)
    else:
        cmds = Commands()
    return model, cmds


def update_pathology_tile_image(msg, model):
    model = Api.add_image(
        model, object_id=msg.pathology_id, query=msg.query, image=msg.image
    )
    return model, Commands()


def update_grouped_annotation_image(msg, model):
    model = Api.add_image(
        model, object_id=msg.ga_id, query=msg.query, image=msg.image
    )
    return model, Commands()
