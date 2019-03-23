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
import uuid
from collections import namedtuple, defaultdict
import itertools

import pathilico.app.geometry as geometry
from pathilico.app.header import Api


DEFAULT_TILE_SIZE = (1024, 1024)
DEFAULT_COLOR = (0, 0, 0, 0)


class AnnotationModel(object):
    def __init__(self):
        self.points = dict()
        self.areas = dict()
        self.ga_records = dict()
        self.point_id2ga_ids = defaultdict(set)
        self.area_id2ga_ids = defaultdict(set)
        self.colors = dict()
        self.tile_width, self.tile_height = DEFAULT_TILE_SIZE
        self._set_mock_colors()

    def _set_mock_colors(self):
        from pathilico.app.views.color import MetroColors
        self.colors = {
            (12345000 + i).to_bytes(4, 'little'): c[:3] + (200, )
            for i, c in enumerate(MetroColors.all)
        }


GroupedAnnotationRecord = namedtuple(
    "GroupedAnnotationRecord", 'x y level points areas query'
)
GroupedAnnotationImageQuery = namedtuple(
    "GroupedAnnotationImageQuery", 'points polygons tile_size'
)  # points: typing.List[int, int, Color] OpenSl coordinates
PointAnnotationRecord = namedtuple(
    "PointAnnotationRecord", 'x y category_id serialized_data'
)
PointAnnotationSerializedData = namedtuple(
    "PointAnnotationSerializedData", 'x y category_id'
)  # open-slide's lv0 coordinate system
AreaAnnotationRecord = namedtuple(
    "AreaAnnotationRecord",
    'x y width height contour triangulate_indices category_id serialized_data'
)
AreaAnnotationSerializedData = namedtuple(
    "AreaAnnotationSerializedData",
    'x y width height contour triangulate_indices category_id'
)  # open-slide's lv0 coordinate system


# Private
def generate_point_id(file_name, x, y, category_id):
    """Generate unique byte from input values for pathology tile record

    :param str file_name:
    :param int x:
    :param int y:
    :param int category_id:
    :return byte:
    """
    uri = "pathilico.org/v1/file/{}/point/category/{}/x/{}/y/{}".format(
        file_name, category_id, x, y
    )
    pf_id = uuid.uuid5(uuid.NAMESPACE_URL, uri).bytes
    return pf_id


def generate_area_id(file_name, x, y, width, height, category_id):
    """Generate unique byte from input values for pathology tile record"""
    uri_base = "pathilico.org/v1/file/{}/area/".format(file_name)
    params = "category/{}/x/{}/y/{}/width/{}/height/{}".format(
        category_id, x, y, width, height
    )
    pf_id = uuid.uuid5(uuid.NAMESPACE_URL, uri_base + params).bytes
    return pf_id


def generate_grouped_annotation_id(file_name, x, y, level):
    uri = \
        "pathilico.org/v1/file/{}/groupedAnnotation/level/{}/x/{}/y/{}".format(
            file_name, level, x, y
        )
    pf_id = uuid.uuid5(uuid.NAMESPACE_URL, uri).bytes
    return pf_id


def convert_int_seq2bytes(int_seq):
    result = b"".join([
        i.to_bytes(4, 'little')
        for i in int_seq
    ])
    return result


def convert_bytes(b):
    if not len(b) % 4 == 0:
        return False, tuple()
    n = len(b) // 4
    result = tuple([
        int.from_bytes(b[4*i: 4*i+4], 'little') for i in range(n)
    ])
    return True, result


def create_area_annotation_serialized_data(
        x, y, width, height, contour, triangulate_indices, category_id,
        lv0_height):
    """From AreaAnnotationRecord's data create AreaAnnotationSerializedData

    Note that input args are under OpenGL coordinate system but
    the output's attributes area under OpenSlide coordinate system
    """
    openslide_cs_contour = tuple([
        v if i % 2 is 0 else height - v for i, v in enumerate(contour)
    ])
    os_y = lv0_height - height - y
    r = AreaAnnotationSerializedData(
        x=x, y=os_y, width=width, height=height,
        triangulate_indices=convert_int_seq2bytes(triangulate_indices),
        contour=convert_int_seq2bytes(openslide_cs_contour),
        category_id=category_id
    )
    return r


def create_area_annotation_record_from_serialized_data(data, lv0_height):
    """From AreaAnnotationRecord's data create AreaAnnotationSerializedData

    Note that input args are under OpenGL coordinate system but
    the output's attributes area under OpenSlide coordinate system
    """
    flag, triangulate_indices = convert_bytes(data.triangulate_indices)
    if not flag:
        return False, tuple()
    flag, contour = convert_bytes(data.contour)
    if not flag:
        return False, tuple()
    gl_contour = tuple([
        v if i % 2 is 0 else data.height - v for i, v in enumerate(contour)
    ])
    gl_y = lv0_height - data.height - data.y
    r = AreaAnnotationRecord(
        x=data.x, y=gl_y, width=data.width, height=data.height,
        contour=gl_contour, triangulate_indices=triangulate_indices,
        category_id=data.category_id, serialized_data=data
    )
    return True, r


def add_point(
        annotation_model, x, y, category_id, lv0_height, display_name):
    """Add point annotation data to annotation model and returns model and id

    Note that this function does not affect grouped annotations

    :param annotation_model:
    :param x:
    :param y:
    :param category_id:
    :param lv0_height:
    :param display_name:
    :return:
    """
    point_id = generate_point_id(display_name, x, y, category_id)
    os_y = lv0_height - y
    point_data = PointAnnotationSerializedData(x, os_y, category_id)
    point_record = PointAnnotationRecord(x, y, category_id, point_data)
    annotation_model.points[point_id] = point_record
    return annotation_model, point_id, point_data


def add_point_from_serialized_data(
        annotation_model, point_id, serialized_point_data, lv0_height
):
    """Add point annotation data to annotation model from serialized_data"""
    serialized_point_data = PointAnnotationSerializedData(
        *serialized_point_data
    )
    x, y, category_id = serialized_point_data
    gl_y = lv0_height - y
    point_record = PointAnnotationRecord(
        x, gl_y, category_id, serialized_point_data
    )
    annotation_model.points[point_id] = point_record
    return annotation_model, point_record


def add_area(
        annotation_model, closed_vs, category_id, lv0_height, display_name,
        reduce_points=True):
    """Add area annotation data to annotation model

    Returns model, flag (check input is valid), id and data.
    Note that this function does not affect grouped annotations

    :param annotation_model:
    :param closed_vs: vertices of points (1-Dimension) OpenGL Coordinate sys
    :param category_id:
    :param lv0_height:
    :param display_name:
    :param bool reduce_points:
    :return:
    """
    if reduce_points:
        closed_vs = geometry.reduce_coordinates(closed_vs, dim_points=1)
    x0, y0, w, h = geometry.get_circumscribed_rectangle(
        closed_vs, dim_points=1
    )
    if not (w > 30, h > 30):
        return annotation_model, False, bytes(), tuple()
    triangulate_indices = geometry.triangulate(closed_vs)
    if not triangulate_indices:
        return annotation_model, False, bytes(), tuple()
    area_id = generate_area_id(
        display_name, x=x0, y=y0, width=w, height=h, category_id=category_id
    )
    contour = tuple([
        v - x0 if i % 2 is 0 else v - y0 for i, v in enumerate(closed_vs)
    ])
    data = create_area_annotation_serialized_data(
        x=x0, y=y0, width=w, height=h, contour=contour,
        triangulate_indices=triangulate_indices, category_id=category_id,
        lv0_height=lv0_height
    )
    record = AreaAnnotationRecord(
        x=x0, y=y0, width=w, height=h, contour=contour,
        triangulate_indices=triangulate_indices, category_id=category_id,
        serialized_data=data
    )
    annotation_model.areas[area_id] = record
    return annotation_model, True, area_id, record


def add_area_from_serialized_data(
        annotation_model, area_id, serialized_area_data, lv0_height
):
    """Add point annotation data to annotation model from serialized_data"""
    serialized_area_data = AreaAnnotationSerializedData(
        *serialized_area_data
    )
    flag, area_record = create_area_annotation_record_from_serialized_data(
        serialized_area_data, lv0_height=lv0_height
    )
    if flag:
        annotation_model.areas[area_id] = area_record
        return True, annotation_model, area_record
    else:
        return False, annotation_model, tuple()


def register_point_to_multi_gouped_annotations(
        annotation_model, ga_ids, point_id, level_downsamples
):
    """Update GroupedAnnotation's point data

    :param AnnotationModel annotation_model:
    :param typing.List[byte] ga_ids: Ids of GroupedAnnotationRecord
    :param byte point_id:
    :param level_downsamples:
    :return:
    """
    ga_qs = list()
    for ga_id in ga_ids:
        ga_record = annotation_model.ga_records[ga_id]
        ga_record.points.add(point_id)
        updated_ga_record = update_grouped_annotation_query(
            ga_record, annotation_model.points, annotation_model.areas,
            annotation_model.colors,
            level_downsamples=level_downsamples
        )  # TODO: Delay to update ga_records
        annotation_model.ga_records[ga_id] = updated_ga_record
        ga_query = updated_ga_record.query
        ga_qs.append(ga_query)
    annotation_model.point_id2ga_ids[point_id] = \
        annotation_model.point_id2ga_ids[point_id] | set(ga_ids)
    return annotation_model, ga_ids, ga_qs


def register_area_to_multi_gouped_annotations(
        annotation_model, ga_ids, area_id, level_downsamples
):
    """Update GroupedAnnotation's point data

    :param AnnotationModel annotation_model:
    :param typing.List[byte] ga_ids: Ids of GroupedAnnotationRecord
    :param byte area_id:
    :param level_downsamples:
    :return:
    """
    ga_qs = list()
    for ga_id in ga_ids:
        ga_record = annotation_model.ga_records[ga_id]
        ga_record.areas.add(area_id)
        updated_ga_record = update_grouped_annotation_query(
            ga_record, annotation_model.points, annotation_model.areas,
            annotation_model.colors,
            level_downsamples=level_downsamples
        )  # TODO: Delay to update ga_records
        annotation_model.ga_records[ga_id] = updated_ga_record
        ga_query = updated_ga_record.query
        ga_qs.append(ga_query)
    annotation_model.area_id2ga_ids[area_id] = \
        annotation_model.area_id2ga_ids[area_id] | set(ga_ids)
    return annotation_model, ga_ids, ga_qs


def unregister_point_from_groupe_annotations(
        annotation_model, point_id, level_downsamples):
    """Update GroupedAnnotation's point data

    :param AnnotationModel annotation_model:
    :param byte point_id:
    :param level_downsamples:
    :return:
    """
    ga_qs = list()
    ga_ids = annotation_model.point_id2ga_ids[point_id]
    for ga_id in ga_ids:
        ga_record = annotation_model.ga_records[ga_id]
        new_point_ids = ga_record.points - {point_id}
        ga_record = ga_record._replace(points=new_point_ids)
        updated_ga_record = update_grouped_annotation_query(
            ga_record, annotation_model.points, annotation_model.areas,
            annotation_model.colors,
            level_downsamples=level_downsamples
        )
        annotation_model.ga_records[ga_id] = updated_ga_record
        ga_query = updated_ga_record.query
        ga_qs.append(ga_query)
    annotation_model.point_id2ga_ids[point_id] = \
        annotation_model.point_id2ga_ids[point_id] - set(ga_ids)
    return annotation_model, ga_ids, ga_qs


def unregister_area_from_groupe_annotations(
        annotation_model, area_id, level_downsamples):
    """Update GroupedAnnotation's point data

    :param AnnotationModel annotation_model:
    :param byte area_id:
    :param level_downsamples:
    :return:
    """
    ga_qs = list()
    ga_ids = annotation_model.area_id2ga_ids[area_id]
    for ga_id in ga_ids:
        ga_record = annotation_model.ga_records[ga_id]
        new_area_ids = ga_record.areas - {area_id}
        ga_record = ga_record._replace(areas=new_area_ids)
        updated_ga_record = update_grouped_annotation_query(
            ga_record, annotation_model.points, annotation_model.areas,
            annotation_model.colors,
            level_downsamples=level_downsamples
        )
        annotation_model.ga_records[ga_id] = updated_ga_record
        ga_query = updated_ga_record.query
        ga_qs.append(ga_query)
    annotation_model.area_id2ga_ids[area_id] = \
        annotation_model.area_id2ga_ids[area_id] - set(ga_ids)
    return annotation_model, ga_ids, ga_qs


def convert_opengl_coordinates2ga_query_coordinates(
        base_x, base_y, scale, x, y, tile_height):
    """To make GroupedAnnotationQuery

    :param int base_x: GroupedAnnotation's x coordinate (OpenGL cs)
    :param int base_y: GroupedAnnotation's y coordinate (OpenGL cs)
    :param int scale: GA level's scale based on level 0
    :param int x:
    :param int y:
    :param tile_height:
    :return tuple[int]: x and y
    """
    new_x = x // scale - base_x
    new_y = tile_height - (y // scale - base_y)
    return new_x, new_y


def update_grouped_annotation_query(
        ga_record, points, areas, category_id2color, level_downsamples,
        tile_size=DEFAULT_TILE_SIZE):
    """Update GroupedAnnotationRecord's query

    This query is for async.create_grouped_annotation_image

    :param GroupedAnnotationRecord ga_record:
    :param dict[byte, PointAnnotationRecord] points:
    :param dict[byte, AreaAnnotationRecord] areas:
    :param dict[byte, tuple[int]] category_id2color:
    :param tuple[int] level_downsamples:
    :param tuple[int] tile_size:
    :return GroupedAnnotationRecord:
    """
    tile_height = tile_size[-1]
    point_ids = ga_record.points
    area_ids = ga_record.areas
    scale = level_downsamples[ga_record.level]
    serialized_points = list()
    serialized_polygons = list()
    for p_record in [points[i] for i in point_ids]:
        pq_x, pq_y = convert_opengl_coordinates2ga_query_coordinates(
            base_x=ga_record.x, base_y=ga_record.y, scale=scale,
            x=p_record.x, y=p_record.y, tile_height=tile_height
        )
        color = category_id2color.get(p_record.category_id, DEFAULT_COLOR)
        # color = (255, 0, 0, 180)  # For debugging
        serialized_points.append((pq_x, pq_y, color))
    for a_record in [areas[i] for i in area_ids]:
        contour = tuple(itertools.chain(*[
            convert_opengl_coordinates2ga_query_coordinates(
                base_x=ga_record.x, base_y=ga_record.y, scale=scale,
                x=a_record.contour[2*i]+a_record.x,
                y=a_record.contour[2*i+1]+a_record.y,
                tile_height=tile_height
            )
            for i in range(len(a_record.contour)//2)
        ]))
        color = category_id2color.get(a_record.category_id, DEFAULT_COLOR)
        # color = (255, 0, 0, 180)  # For debugging
        serialized_polygons.append((contour, color))
    query = GroupedAnnotationImageQuery(
        points=serialized_points, polygons=serialized_polygons,
        tile_size=tile_size
    )
    ga_record = ga_record._replace(query=query)
    return ga_record


def delete_points(annotation_model, point_ids, level_downsamples):
    result = dict()
    for p_id in point_ids:
        annotation_model, ga_ids, ga_queries = \
            unregister_point_from_groupe_annotations(
                annotation_model, p_id, level_downsamples=level_downsamples
            )
        for g_id, g_q in zip(ga_ids, ga_queries):
            result[g_id] = g_q
    ga_ids = list(result.keys())
    ga_queries = list(result.values())
    return annotation_model, ga_ids, ga_queries


def delete_areas(annotation_model, area_ids, level_downsamples):
    result = dict()
    for a_id in area_ids:
        annotation_model, ga_ids, ga_queries = \
            unregister_area_from_groupe_annotations(
                annotation_model, a_id, level_downsamples=level_downsamples
            )
        for g_id, g_q in zip(ga_ids, ga_queries):
            result[g_id] = g_q
    ga_ids = list(result.keys())
    ga_queries = list(result.values())
    return annotation_model, ga_ids, ga_queries


def get_bounds_for_point(lv0_x, lv0_y, level_downsamples, offset=4):
    result = list()
    for lev, scale in enumerate(level_downsamples):
        x = lv0_x // scale
        y = lv0_y // scale
        b = (x-offset, y-offset, x+offset, y+offset, lev)
        result.append(b)
    return result


def get_bounds_for_area(lv0_x, lv0_y, width, height, level_downsamples):
    result = list()
    for lev, scale in enumerate(level_downsamples):
        x = lv0_x // scale
        y = lv0_y // scale
        w = width // scale
        h = height // scale
        b = (x, y, x+w, y+h, lev)
        result.append(b)
    return result


# Actual impl
def add_point_annotation(model, x, y, category_id):
    display_name = Api.get_display_name(model)
    s_height = Api.get_level0_pathology_slide_height(model)
    level_downsamples = Api.get_level_downsamples(model)
    model.annotation, point_id, point_data = add_point(
        model.annotation, x=x, y=y, category_id=category_id,
        lv0_height=s_height, display_name=display_name
    )
    model = Api.register_data(model, point_id, point_data, data_type="point")
    bounds = get_bounds_for_point(x, y, level_downsamples)
    model = Api.bind_id_on_districts(model, point_id, bounds, data_type="point")
    ga_ids = Api.get_ids_on_districts(
        model, bounds, data_type="grouped_annotation"
    )
    model.annotation, ga_ids, ga_queries = \
        register_point_to_multi_gouped_annotations(
            model.annotation, ga_ids=ga_ids, point_id=point_id,
            level_downsamples=level_downsamples
        )
    for g_id, g_query in zip(ga_ids, ga_queries):
        model = Api.reserve_image_query(model, g_id, g_query)
    return model


def add_point_annotation_from_serialized_data(model, point_id, point_data):
    # TODO: This func should be updated to handle multi points
    s_height = Api.get_level0_pathology_slide_height(model)
    level_downsamples = Api.get_level_downsamples(model)
    model.annotation, point_record = add_point_from_serialized_data(
        model.annotation, point_id=point_id, serialized_point_data=point_data,
        lv0_height=s_height
    )
    bounds = get_bounds_for_point(
        point_record.x, point_record.y, level_downsamples
    )
    model = Api.bind_id_on_districts(model, point_id, bounds, data_type="point")
    ga_ids = Api.get_ids_on_districts(
        model, bounds, data_type="grouped_annotation"
    )
    model.annotation, ga_ids, ga_queries = \
        register_point_to_multi_gouped_annotations(
            model.annotation, ga_ids=ga_ids, point_id=point_id,
            level_downsamples=level_downsamples
        )
    for g_id, g_query in zip(ga_ids, ga_queries):
        model = Api.reserve_image_query(model, g_id, g_query)
    return model


def add_area_annotation(model, closed_vs, category_id):
    display_name = Api.get_display_name(model)
    s_height = Api.get_level0_pathology_slide_height(model)
    level_downsamples = Api.get_level_downsamples(model)
    model.annotation, flag, area_id, area_record = add_area(
        model.annotation, closed_vs=closed_vs, category_id=category_id,
        lv0_height=s_height, display_name=display_name, reduce_points=True
    )
    if not flag:
        return model
    model = Api.register_data(
        model, area_id, area_record.serialized_data, data_type="area"
    )
    bounds = get_bounds_for_area(
        lv0_x=area_record.x, lv0_y=area_record.y, width=area_record.width,
        height=area_record.height, level_downsamples=level_downsamples
    )
    model = Api.bind_id_on_districts(model, area_id, bounds, data_type="area")
    ga_ids = Api.get_ids_on_districts(
        model, bounds, data_type="grouped_annotation"
    )
    model.annotation, ga_ids, ga_queries = \
        register_area_to_multi_gouped_annotations(
            model.annotation, ga_ids=ga_ids, area_id=area_id,
            level_downsamples=level_downsamples
        )
    for g_id, g_query in zip(ga_ids, ga_queries):
        model = Api.reserve_image_query(model, g_id, g_query)
    return model


def add_area_annotation_from_serialized_data(model, area_id, area_data):
    s_height = Api.get_level0_pathology_slide_height(model)
    level_downsamples = Api.get_level_downsamples(model)
    flag, model.annotation, area_record = add_area_from_serialized_data(
        model.annotation, area_id=area_id, serialized_area_data=area_data,
        lv0_height=s_height
    )
    if not flag:
        return model
    bounds = get_bounds_for_area(
        lv0_x=area_record.x, lv0_y=area_record.y, width=area_record.width,
        height=area_record.height, level_downsamples=level_downsamples

    )
    model = Api.bind_id_on_districts(
        model, area_id, bounds, data_type="area"
    )
    ga_ids = Api.get_ids_on_districts(
        model, bounds, data_type="grouped_annotation"
    )
    model.annotation, ga_ids, ga_queries = \
        register_area_to_multi_gouped_annotations(
            model.annotation, ga_ids=ga_ids, area_id=area_id,
            level_downsamples=level_downsamples
        )
    for g_id, g_query in zip(ga_ids, ga_queries):
        model = Api.reserve_image_query(model, g_id, g_query)
    return model


def delete_point_annotations(model, point_ids):
    lds = Api.get_level_downsamples(model)
    model.annotation, ga_ids, ga_queries = delete_points(
        model.annotation, point_ids, level_downsamples=lds
    )
    for p_id in point_ids:
        model = Api.unregister_data(model, p_id, data_type="point")
        model = Api.unbind_id_on_districts(model, p_id, data_type="point")
    for g_id, g_query in zip(ga_ids, ga_queries):
        model = Api.reserve_image_query(model, g_id, g_query)
    return model


def delete_area_annotations(model, area_ids):
    lds = Api.get_level_downsamples(model)
    model.annotation, ga_ids, ga_queries = delete_areas(
        model.annotation, area_ids, level_downsamples=lds
    )
    for a_id in area_ids:
        model = Api.unregister_data(model, a_id, data_type="area")
        model = Api.unbind_id_on_districts(model, a_id, data_type="area")
    for g_id, g_query in zip(ga_ids, ga_queries):
        model = Api.reserve_image_query(model, g_id, g_query)
    return model


def get_annotation_info_and_grouped_images_for_display(model):
    bound = Api.get_bound_for_window(model)
    point_ids = Api.get_ids_on_districts(model, [bound], "point")
    area_ids = Api.get_ids_on_districts(model, [bound], "area")
    ga_ids = Api.get_ids_on_districts(model, [bound], "grouped_annotation")
    result_images = list()
    existing_point_id_list = [set()]
    existing_area_id_list = [set()]
    existing_ga_ids, images = Api.get_images(model, ga_ids)
    for ga_id, img in zip(existing_ga_ids, images):
        ga_record = model.annotation.ga_records[ga_id]
        x, y = Api.get_window_coordinates(
            model, ga_record.x, ga_record.y, given_level=ga_record.level
        )
        existing_point_id_list.append(ga_record.points)
        existing_area_id_list.append(ga_record.areas)
        result_images.append((x, y, img))
    missing_point_ids = set(point_ids) - set.union(*existing_point_id_list)
    points = list()
    for p_id in missing_point_ids:
        p_record = model.annotation.points[p_id]
        win_x, win_y = Api.get_window_coordinates(
            model, p_record.x, p_record.y
        )
        color = model.annotation.colors.get(p_record.category_id, DEFAULT_COLOR)
        points.append((win_x, win_y, color))
    missing_area_ids = set(area_ids) - set.union(*existing_area_id_list)
    polygons = list()
    for a_id in missing_area_ids:
        a_record = model.annotation.areas[a_id]
        contour = tuple(itertools.chain(*[
            Api.get_window_coordinates(
                model,
                gl_x=a_record.x+a_record.contour[2*i],
                gl_y=a_record.y+a_record.contour[2*i+1]
            )
            for i in range(len(a_record.contour)//2)
        ]))
        color = model.annotation.colors.get(a_record.category_id, DEFAULT_COLOR)
        polygons.append((contour, a_record.triangulate_indices, color))
    return result_images, points, polygons


def fill_grouped_annotation_records(model):
    """This function should be called when pathology file is selected

    :param pathfinder.app.model.Model model:
    :return pathilico.app.model.Model:
    """
    t_w, t_h = model.annotation.tile_width, model.annotation.tile_height
    widths, heights = Api.get_pathology_slide_widths_and_heights(model)
    display_name = Api.get_display_name(model)
    for level in range(len(widths)):
        w, h = widths[level], heights[level]
        num_hor = w // t_w + 1
        num_ver = h // t_h + 1
        for hor_i, ver_i in itertools.product(range(num_hor), range(num_ver)):
            ga_id = generate_grouped_annotation_id(
                display_name, x=hor_i, y=ver_i, level=level,
            )
            x = hor_i * t_w
            y = ver_i * t_h
            empty_query = GroupedAnnotationImageQuery(
                points=list(), polygons=list(), tile_size=(t_w, t_h)
            )
            rec = GroupedAnnotationRecord(
                x=x, y=y, level=level, points=set(), areas=set(),
                query=empty_query
            )
            model.annotation.ga_records[ga_id] = rec
            model = Api.bind_id_on_districts(
                model, ga_id, [(x, y, x+t_w, y+t_h, level)],
                data_type="grouped_annotation"
            )
    return model


Api.register(AnnotationModel)
Api.register(add_point_annotation)
Api.register(add_point_annotation_from_serialized_data)
Api.register(delete_point_annotations)
Api.register(get_annotation_info_and_grouped_images_for_display)
Api.register(fill_grouped_annotation_records)
Api.register(add_area_annotation)
Api.register(add_area_annotation_from_serialized_data)
Api.register(delete_area_annotations)

