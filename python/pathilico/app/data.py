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
import typing

from pathilico.app.header import Api


if typing.TYPE_CHECKING:
    ObjectId = typing.Union[int, bytes]


# Helper Table class and functions which provides `create`, `read`, and `delete`
class TableModel(object):
    def __init__(
            self,
            header: typing.Tuple[str, ...],
            data_types: typing.Tuple[str, ...]) -> None:
        self.unsaved_added_ids = set()
        self.unsaved_deleted_ids = set()
        self.header = header
        self.data_types = data_types
        self.table_rows = dict()


def add_record_to_table(
        table_model: TableModel,
        object_id: 'ObjectId',
        record: typing.Any,
        ignore_staging_state=False) -> TableModel:
    record = tuple(record)
    table_model.table_rows[object_id] = record
    if not ignore_staging_state:
        table_model.unsaved_added_ids.add(object_id)
        table_model.unsaved_deleted_ids = \
            table_model.unsaved_deleted_ids - {object_id}
    return table_model


def delete_record_from_table(
        table_model: TableModel, object_id: 'ObjectId') -> TableModel:
    table_model.table_rows.pop(object_id)
    table_model.unsaved_added_ids = table_model.unsaved_added_ids - {object_id}
    table_model.unsaved_deleted_ids.add(object_id)
    return table_model


def get_records_from_table(
        table_model: TableModel,
        object_ids: typing.List['ObjectId']
) -> typing.Tuple[typing.Tuple['ObjectId', ...], typing.Tuple]:
    object_ids = tuple([i for i in object_ids if i in table_model.table_rows])
    records = tuple([table_model.table_rows[i] for i in object_ids])
    return object_ids, records


def update_saved_status(
        table_model: TableModel,
        saved_added_ids: typing.Tuple['ObjectId', ...],
        saved_deleted_ids: typing.Tuple['ObjectId', ...],
) -> TableModel:
    table_model.unsaved_added_ids = \
        table_model.unsaved_added_ids - set(saved_added_ids)
    table_model.unsaved_deleted_ids = \
        table_model.unsaved_deleted_ids - set(saved_deleted_ids)
    return table_model


def get_unsaved_records(
        table_model: TableModel
) -> typing.Tuple[typing.Tuple['ObjectId', ...], typing.Tuple, typing.Tuple]:
    ids2add = tuple(table_model.unsaved_added_ids)
    ids2delete = tuple(table_model.unsaved_deleted_ids)
    records = tuple([table_model.table_rows[i] for i in ids2add])
    return ids2add, records, ids2delete


# Private
class DatabaseModel(object):
    def __init__(self):
        self.file_path = os.path.expanduser("~/DataForML/svs/pathilico.pickle")
        self.point = TableModel(
            header=("x", "y", "category_id"),
            data_types=("int", "int", "bytes")
        )
        self.area = TableModel(
            header=(
                "x", "y", "width", "height", "contour", "triangulate_indices",
                "category_id"
            ),
            data_types=("int", "int", "int", "int", "bytes", "bytes", "bytes")
        )
        self.category = TableModel(
            header=("name", "project", "red", "green", "blue", "alpha"),
            data_types=("str", "str", "int", "int", "int", "int")
        )


def register_record(
        database_model, object_id, serialized_data, table_name="point",
        ignore_staging_status=False):
    table = getattr(database_model, table_name, None)
    if table is None:
        return database_model
    updated_table = add_record_to_table(
        table, object_id, serialized_data, ignore_staging_status
    )
    setattr(database_model, table_name, updated_table)
    return database_model


def unregister_record(database_model, object_id, table_name="point"):
    table = getattr(database_model, table_name, None)
    if table is None:
        return database_model
    updated_table = delete_record_from_table(table, object_id)
    setattr(database_model, table_name, updated_table)
    return database_model


def get_records(database_model, object_ids, table_name="point"):
    table = getattr(database_model, table_name, None)
    if table is None:
        return list()
    records = get_records_from_table(table, object_ids)
    return records


def get_queries_to_save(database_model, table_name="point"):
    table = getattr(database_model, table_name)
    table_header = table.header
    table_type = table.header
    add_ids, add_records, delete_ids = get_unsaved_records(table)
    return table_header, table_type, add_ids, add_records, delete_ids


# Public
def register_data(
        model, object_id, object_data, data_type, ignore_staging_status=False):
    model.database = register_record(
        model.database, object_id, object_data, table_name=data_type,
        ignore_staging_status=ignore_staging_status
    )
    return model


def unregister_data(model, object_id, data_type):
    model.database = unregister_record(
        model.database, object_id, table_name=data_type
    )
    return model


def get_queries_to_save_records(model):
    queries = list()
    d_name = Api.get_display_name(model)
    db_file_path = model.database.file_path
    if d_name is "":
        return model, queries
    # Add point data
    table_name2save = "annotation_point_{}".format(d_name)
    header, types, add_ids, add_records, delete_ids = get_queries_to_save(
        model.database, table_name="point"
    )
    query = (
        db_file_path, table_name2save, header, types, add_ids, add_records,
        delete_ids
    )
    queries.append(query)
    # Add area data
    table_name2save = "annotation_area_{}".format(d_name)
    header, types, add_ids, add_records, delete_ids = get_queries_to_save(
        model.database, table_name="area"
    )
    query = (
        db_file_path, table_name2save, header, types, add_ids, add_records,
        delete_ids
    )
    queries.append(query)
    return model, queries


def get_queries_to_load_records(model):
    queries = list()
    d_name = Api.get_display_name(model)
    db_file_path = model.database.file_path
    # Add point query
    table_name2load = "annotation_point_{}".format(d_name)
    query = (db_file_path, table_name2load, "point")
    queries.append(query)
    # Add area query
    table_name2load = "annotation_area_{}".format(d_name)
    query = (db_file_path, table_name2load, "area")
    queries.append(query)
    return queries


def set_records_are_saved(model, added_ids, deleted_ids, data_type="point"):
    """

    This function should be called when save to db is success

    :param pathfinder.app.model.Model model:
    :param added_ids:
    :param deleted_ids:
    :param str data_type:
    :return:
    """
    table = getattr(model.database, data_type)
    table = update_saved_status(table, added_ids, deleted_ids)
    setattr(model.database, data_type, table)
    return model


Api.register(DatabaseModel)
Api.register(register_data)
Api.register(unregister_data)
Api.register(get_queries_to_save_records)
Api.register(get_queries_to_load_records)
Api.register(set_records_are_saved)
