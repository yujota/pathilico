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
from pathilico.pygletelm.effect import NO_COMMANDS
from pathilico.app.message import Msg
from pathilico.app.header import Api
import pathilico.app.ports.pickle_database as database
from pathilico.app.updates.update_position import get_image_queries


TARGET_MESSAGES = (
    Msg.ExecSaveToDatabase, Msg.ExecLoadFromDatabase,
    Msg.RecordSaved, Msg.RecordLoaded
)


def update(msg, model):
    if msg == Msg.ExecSaveToDatabase:
        return exec_save(msg, model)
    elif msg == Msg.ExecLoadFromDatabase:
        return exec_load(msg, model)
    elif msg == Msg.RecordSaved:
        return update_saved_record_status(msg, model)
    elif msg == Msg.RecordLoaded:
        return load_records(msg, model)
    return model, NO_COMMANDS


def exec_save(msg, model):
    cs = list()
    model, queries = Api.get_queries_to_save_records(model)
    for (file_path, table_name, table_header, table_type, add_ids,
         add_records, delete_ids) in queries:
        c = database.get_save_record_request(
            Msg.RecordSaved, file_path, table_name, table_header,
            table_type, add_ids, add_records, delete_ids,
            msg_kwargs=dict(
                added_ids=add_ids, deleted_ids=delete_ids,
                data_type="point"
            )
        )
        cs.append(c)
    cmds = database.wrap_records(*cs)
    return model, cmds


def exec_load(msg, model):
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


def update_saved_record_status(msg, model):
    if msg.flag:
        model = Api.set_records_are_saved(
            model, added_ids=msg.added_ids, deleted_ids=msg.deleted_ids,
            data_type=msg.data_type
        )
    return model, NO_COMMANDS


def load_records(msg, model):
    if not msg.flag:
        return model, NO_COMMANDS
    if msg.data_type == "point":
        for r_id, record in zip(msg.record_ids, msg.records):
            model = Api.register_data(
                model, r_id, record, data_type=msg.data_type,
                ignore_staging_status=True
            )
            model = Api.add_point_annotation_from_serialized_data(
                model, r_id, record
            )
    elif msg.data_type == "area":
        for r_id, record in zip(msg.record_ids, msg.records):
            model = Api.register_data(
                model, r_id, record, data_type=msg.data_type,
                ignore_staging_status=True
            )
            model = Api.add_area_annotation_from_serialized_data(
                model, r_id, record
            )
    else:
        return model, NO_COMMANDS
    cmds = get_image_queries(model)
    return model, cmds
