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
from collections import defaultdict, namedtuple
import functools
import itertools

from pathilico.app.header import Api


ZONE_LENGTH = 256


# Essential APIs
class ZoneModel(object):
    pathology = defaultdict(set)  # ZoneID: set[ObjectId]
    point = defaultdict(set)  # ZoneID: set[ObjectId]
    area = defaultdict(set)  # ZoneID: set[ObjectId]
    grouped_annotation = defaultdict(set)  # ZoneID: set[ObjectId]
    object_id2zone_id = defaultdict(set)
    zone_length = ZONE_LENGTH
    bounds = defaultdict(set)


Bound = namedtuple("ZoneItem", "left bottom right top level")


@functools.lru_cache(maxsize=1024)
def generate_zone_district_id(x, y, level):
    return (level + 1) * 100000000 + (y + 1) * 10000 + x


def get_zone_district_ids(
        left, bottom, right, top, level, zone_length=ZONE_LENGTH):
    """Get zone_ids corresponding to given bound (left, bottom, right, top)"""
    l_i, b_i = left // zone_length, bottom // zone_length
    r_i, t_i = (right-1) // zone_length, (top-1) // zone_length
    return _get_zone_ids(l_i, b_i, r_i, t_i, level)


@functools.lru_cache(maxsize=1024)
def _get_zone_ids(left_index, bottom_index, right_index, top_index, level):
    coordination = itertools.product(
        range(left_index, right_index+1),
        range(bottom_index, top_index+1)
    )
    ids = [
        generate_zone_district_id(x, y, level)
        for x, y in coordination
    ]
    return set(ids)


def register_id(zone_model, object_id, bounds, data_type="pathology"):
    """Bind object id to bounds(area)

    :param ZoneModel zone_model:
    :param int|byte object_id:
    :param List[tuple[int]] bounds: (right, bottom, left, top, level)
    :param str data_type:
    :return ZoneModel:
    """
    data = getattr(zone_model, data_type)
    for l, b, r, t, lev in bounds:
        bound = Bound(
            left=l, bottom=b, right=r, top=t, level=lev
        )
        zone_model.bounds[object_id].add(bound)
        z_ids = get_zone_district_ids(l, b, r, t, lev, zone_model.zone_length)
        zone_model.object_id2zone_id[object_id] = \
            zone_model.object_id2zone_id[object_id] | z_ids
        for z_id in z_ids:
            data[z_id].add(object_id)
    return zone_model


def unregister_id(zone_model, object_id, data_type="pathology"):
    """Unbind object id from zone_model

    :param ZoneModel zone_model:
    :param int|byte object_id:
    :param str data_type:
    :return ZoneModel:
    """
    zone_ids = zone_model.object_id2zone_id.pop(object_id)
    data = getattr(zone_model, data_type)
    for z in zone_ids:
        data[z].remove(object_id)
    zone_model.bounds.pop(object_id)
    return zone_model


def get_object_ids(zone_model, bounds, data_type="pathology"):
    """Get object ids from given bounds

    :param zone_model:
    :param bounds:
    :param str data_type:
    :return:
    """
    result_obj_ids = list()
    data = getattr(zone_model, data_type)
    for l, b, r, t, lev in bounds:
        z_ids = get_zone_district_ids(l, b, r, t, lev, zone_model.zone_length)
        obj_ids = set.union(*[data[k] for k in z_ids])
        for o_id in obj_ids:
            obj_bounds = zone_model.bounds[o_id]
            for o_bound in obj_bounds:
                if is_two_bound_overlaps(o_bound, (l, b, r, t, lev)):
                    result_obj_ids.append(o_id)
                    continue
    obj_ids = set(result_obj_ids)
    return obj_ids


def is_two_bound_overlaps(bound_one, bound_two):
    l1, b1, r1, t1, level1 = bound_one
    l2, b2, r2, t2, level2 = bound_two
    if level1 is not level2:
        return False
    flag = any([r1 < l2, t1 < b1, r2 < l1, t2 < b1])
    return not flag


# Actual implementations for Api
def bind_id_on_districts(model, object_id, bounds, data_type="pathology"):
    zone_model = model.zone
    zone_model = register_id(zone_model, object_id, bounds, data_type)
    model.zone = zone_model
    return model


def unbind_id_on_districts(model, object_id, data_type="pathology"):
    zone_model = model.zone
    zone_model = unregister_id(zone_model, object_id, data_type)
    model.zone = zone_model
    return model


def get_ids_on_districts(model, bounds, data_type="pathology"):
    zone_model = model.zone
    obj_ids = get_object_ids(zone_model, bounds, data_type)
    return obj_ids


Api.register(ZoneModel)
Api.register(bind_id_on_districts)
Api.register(unbind_id_on_districts)
Api.register(get_ids_on_districts)
