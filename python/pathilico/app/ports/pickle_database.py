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
import pickle
import typing
from logging import getLogger

import pathilico.pygletelm.effect as effect


if typing.TYPE_CHECKING:
    TableName = typing.NewType('TableName', str)
    TableHeader = typing.Tuple[str, ...]
    TableType = typing.Tuple[str, ...]
    RecordId = typing.Union[int, bytes]
    Record = typing.Tuple[typing.Union[int, str, bytes], ...]
    Table = typing.Dict[RecordId, Record]
    Tables = typing.Dict[TableName, Table]
    Headers = typing.Dict[TableName, TableHeader]
    Types = typing.Dict[TableName, TableType]
    DataBase = typing.Dict[str, typing.Union[Tables, Headers, Types]]


# Helper functions
def create_database_object() -> 'DataBase':
    d = {
        "tables": dict(),
        "headers": dict(),
        "types": dict()
    }
    return d


def create_new_table(
        db_dict: 'DataBase', table_name: 'TableName',
        table_header: 'TableHeader', table_type: 'TableType'
) -> 'DataBase':
    if (
            table_name in db_dict["tables"]
            or table_name in db_dict["headers"]
            or table_name in db_dict["types"]
    ):
        raise ValueError("Already has table: {}".format(table_name))
    db_dict["tables"][table_name] = dict()
    db_dict["headers"][table_name] = table_header
    db_dict["types"][table_name] = table_type
    return db_dict


def has_table(db_dict: 'DataBase', table_name: 'TableName') -> bool:
    return table_name in db_dict["tables"]


def add_record(
        db_dict: 'DataBase',
        table_name: 'TableName',
        record_id: 'RecordId',
        record: 'Record'
) -> 'DataBase':
    db_dict["tables"][table_name][record_id] = record
    return db_dict


def get_all_records(
        db_dict: 'DataBase', table_name: 'TableName'
) -> typing.Tuple[typing.Tuple['RecordId', ...], typing.Tuple['Record', ...]]:
    keys = tuple(db_dict["tables"][table_name].keys())
    items = tuple(db_dict["tables"][table_name].values())
    return keys, items


def delete_record(
        db_dict: 'DataBase', table_name: 'TableName', record_id: 'RecordId'
) -> 'DataBase':
    db_dict["tables"][table_name].pop(record_id)
    return db_dict


# Private functions
def save(
        file_path, table_name, table_header, table_type,
        add_ids=tuple(), add_records=tuple(), delete_ids=tuple()
):
    try:
        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                db = pickle.load(f)
        else:
            db = create_database_object()
        if not has_table(db, table_name):
            db = create_new_table(db, table_name, table_header, table_type)
        for r_id, rec in zip(add_ids, add_records):
            db = add_record(db, table_name, r_id, rec)
        for r_id in delete_ids:
            db = delete_record(db, table_name, r_id)
        with open(file_path, "wb") as f:
            pickle.dump(db, f)
        return True, ""
    except Exception as e:
        return False, str(e)


def load(file_path, table_name):
    if not os.path.isfile(file_path):
        return False, "File not found", tuple(), tuple()
    try:
        with open(file_path, "rb") as f:
            db = pickle.load(f)
        if not has_table(db, table_name):
            return False, "Table not found", tuple(), tuple()
        r_ids, recs = get_all_records(db, table_name)
        return True, "", r_ids, recs
    except Exception as e:
        return False, str(e), tuple(), tuple()


class PickleDatabaseWorker(object):

    def __init__(self, logger=None):
        self.logger = logger or getLogger("pfapp.PickleDatabase")

    def _get_save_response(self, request):
        (
            msg, msg_kwargs, file_path, table_name, table_header, table_type,
            add_ids, add_records, delete_ids
        ) = request[1:]
        is_succ, error_msg = save(
            file_path, table_name, table_header, table_type, add_ids,
            add_records, delete_ids
        )
        response = ("save", is_succ, error_msg, msg, msg_kwargs)
        return True, response

    def _get_load_response(self, request):
        msg, msg_kwargs, file_path, table_name = request[1:]
        is_succ, error_msg, r_ids, records = load(file_path, table_name)
        response = ("load", is_succ, error_msg, r_ids, records, msg, msg_kwargs)
        return True, response

    def get_response(self, request):
        if request[0] == "save":
            return self._get_save_response(request)
        elif request[0] == "load":
            return self._get_load_response(request)
        else:
            return False, "Undefined {}".format(request[0])


PICKLE_DATABASE_WORKER = list()


class SaveOrLoadFromPickleDatabase(effect.CommandWithThreadWorkerBase):
    def __init__(
            self, file_path, table_name, msg,
            table_header=None, table_type=None,
            add_ids=tuple(), add_records=tuple(), delete_ids=tuple(),
            msg_kwargs=None, logger=None, op_type="save"):
        self.logger = logger or getLogger("pfapp.PickleDatabase")
        if len(PICKLE_DATABASE_WORKER) == 0:
            worker = PickleDatabaseWorker()
            thread = effect.BidirectionalStreamingThread(
                worker=worker, auto_start=True, daemon=True
            )
            PICKLE_DATABASE_WORKER.append(thread)
        msg_kwargs = msg_kwargs or dict()
        if op_type == "save":
            request = (
                "save",
                msg, msg_kwargs, file_path,
                table_name, table_header, table_type,
                add_ids, add_records, delete_ids
            )
        else:
            request = (
                "load",
                msg, msg_kwargs, file_path, table_name,
            )
        self.request = request

    def is_done(self):
        return False

    def done(self):
        pass

    def start(self):
        thread = PICKLE_DATABASE_WORKER[0]
        thread.add_request(self.request)

    def _construct_msg_from_save_response(self, res):
        is_succ, error_msg, msg, msg_kwargs = res[1:]
        message = msg(
            flag=is_succ, error_message=error_msg,  **msg_kwargs
        )
        return message

    def _construct_msg_from_load_response(self, res):
        is_succ, error_msg, r_ids, records, msg, msg_kwargs = res[1:]
        message = msg(
            flag=is_succ, error_message=error_msg, record_ids=r_ids,
            records=records, **msg_kwargs
        )
        return message

    def get_message(self):
        if len(PICKLE_DATABASE_WORKER) == 1:
            thread = PICKLE_DATABASE_WORKER[0]
            flag, res = thread.get_response()
            if flag:
                self.logger.debug("Got res from PickleDB worker {}".format(res))
                if res[0] == "save":
                    message = self._construct_msg_from_save_response(res)
                    return True, message
                elif res[0] == "load":
                    message = self._construct_msg_from_load_response(res)
                    return True, message
        return False, None


def get_save_record_request(
        msg, file_path, table_name, table_header, table_type,
        add_ids=tuple(), add_records=tuple(), delete_ids=tuple(),
        msg_kwargs=None):
    cmd = SaveOrLoadFromPickleDatabase(
        file_path=file_path, table_name=table_name, table_header=table_header,
        table_type=table_type, msg=msg, add_ids=add_ids, msg_kwargs=msg_kwargs,
        add_records=add_records, delete_ids=delete_ids, op_type="save"
    )
    return cmd


def get_load_record_request(msg, file_path, table_name, msg_kwargs=None):
    cmd = SaveOrLoadFromPickleDatabase(
        file_path=file_path, table_name=table_name, msg=msg,
        msg_kwargs=msg_kwargs, op_type="load"
    )
    return cmd


def wrap_records(*requests):
    return effect.EffectObject(effects=requests)


if __name__ == "__main__":
    import time
    import random
    r = save(
        "hoge.pickle",
        "hoge",
        ("a", "b"),
        ("str", "str"),
        tuple([random.randint(0, 1000000) for _ in range(10000)]),
        tuple([(random.randint(0, 10000), random.randint(0, 100)) for _ in range(10000)]),
    )
    start = time.time()
    flag, msg, ids, recs = load("hoge.pickle", "hoge")
    print(time.time() - start)
    print(flag, msg, len(ids), len(recs))


