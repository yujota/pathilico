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
from collections import namedtuple
import itertools
import uuid

from pathilico.app.header import Api


# Essence APIs
class PathologyModel(object):
    def __init__(self, file_path="", tile_size=(1024, 1024), display_name=""):
        self.file_path, self.display_name = file_path, display_name
        self.is_info_acquired = False
        self.num_levels = 0
        self.widths = [0]
        self.heights = [0]
        self.downsamples = [1]
        self.tile_width, self.tile_height = tile_size
        self.tile_records = dict()


PathologyTileImageRecord = namedtuple(
    "PathologyTileImageRecord", "x y level openslide_query"
)
OpenSlideReadRegionQuery = namedtuple(
    "OpenSlideReadRegionQuery", "location level size"
)


# Private
def generate_id(file_name, x, y, level):
    """Generate unique byte from input values for pathology tile record

    :param str file_name:
    :param int x:
    :param int y:
    :param int level:
    :return byte:
    """
    uri = "pathilico.org/v1/file/{}/pathology/level/{}/x/{}/y/{}".format(
        file_name, level, x, y
    )
    pf_id = uuid.uuid5(uuid.NAMESPACE_URL, uri).bytes
    return pf_id


def get_openslide_query(
        x, y, level, tile_width, tile_height, level_heights, level_downsamples):
    """Make OpenSlide's read_region query from given positions (OpenGL cs)

    Note that given x and y coordinates is under
    OpenGl coordinate system, the y-axis points up.
    In contrast, OpenSlide adopted DirectX like
    coordinate system, the y-axis points down.
    """
    slide_x = x
    slide_y = level_heights[level] - y - tile_height
    if not level == 0:
        scale = level_downsamples[level]
        slide_x = scale * slide_x
        slide_y = scale * slide_y
    location = (slide_x, slide_y)
    size = (tile_width, tile_height)
    return location, level, size


def set_pathology_info(
        pathology_model, file_path, file_name, level_count, level_dimensions,
        level_downsamples):
    """Setter for PathologyModel's attributes

    :param PathologyModel pathology_model:
    :param file_path:
    :param file_name:
    :param level_count:
    :param level_dimensions:
    :param level_downsamples:
    :return PathologyModel:
    """
    pathology_model.file_path = file_path
    pathology_model.display_name = file_name
    pathology_model.num_levels = level_count
    pathology_model.widths = [i[0] for i in level_dimensions]
    pathology_model.heights = [i[1] for i in level_dimensions]
    pathology_model.downsamples = [int(l) for l in level_downsamples]
    return pathology_model


def fill_pathology_tile_records(model):
    """This function should be called when pathology file is selected

    :param pathfinder.app.model.Model model:
    :return pathilico.app.model.Model:
    """
    t_w, t_h = model.pathology.tile_width, model.pathology.tile_height
    for level in range(model.pathology.num_levels):
        w, h = model.pathology.widths[level], model.pathology.heights[level]
        num_hor = w // t_w + 1
        num_ver = h // t_h + 1
        for hor_i, ver_i in itertools.product(range(num_hor), range(num_ver)):
            pathology_id = generate_id(
                model.pathology.display_name, x=hor_i, y=ver_i, level=level,
            )
            x = hor_i * t_w
            y = ver_i * t_h
            os_location, os_level, os_size = get_openslide_query(
                x=x, y=y, level=level, tile_width=t_w, tile_height=t_h,
                level_heights=model.pathology.heights,
                level_downsamples=model.pathology.downsamples
            )
            openslide_query = OpenSlideReadRegionQuery(
                location=os_location, level=os_level, size=os_size
            )
            rec = PathologyTileImageRecord(
                x=x, y=y, level=level, openslide_query=openslide_query
            )
            model.pathology.tile_records[pathology_id] = rec
            model = Api.bind_id_on_districts(
                model, pathology_id, [(x, y, x+t_w, y+t_h, level)], "pathology"
            )
            model = Api.reserve_image_query(
                model, object_id=pathology_id, query=openslide_query
            )
    return model


# Public functions (Actual implementations for Api)
def get_file_path(model):
    return model.pathology.file_path


def get_display_name(model):
    return model.pathology.display_name


def get_level_downsamples(model):
    return model.pathology.downsamples


def get_level0_pathology_slide_height(model):
    return model.pathology.heights[0]


def get_pathology_slide_widths_and_heights(model):
    ws = model.pathology.widths
    hs = model.pathology.heights
    return ws, hs


def get_num_levels(model):
    return model.pathology.num_levels


def update_pathology(
        model, file_path, file_name, level_count, level_dimensions,
        level_downsamples):
    model.pathology = set_pathology_info(
        model.pathology, file_path, file_name, level_count, level_dimensions,
        level_downsamples
    )
    model = fill_pathology_tile_records(model)
    model = Api.fill_grouped_annotation_records(model)
    return model


def get_pathology_tile_images_for_display(model):
    bound = Api.get_bound_for_window(model)
    pathology_ids = Api.get_ids_on_districts(
        model, [bound], data_type="pathology"
    )
    pathology_ids, images = Api.get_images(model, pathology_ids)
    result = list()
    for p_id, img in zip(pathology_ids, images):
        p_record = model.pathology.tile_records[p_id]
        x, y = p_record.x - model.position.x, p_record.y - model.position.y
        result.append((x, y, img))
    return result


Api.register(PathologyModel)
Api.register(get_file_path)
Api.register(get_display_name)
Api.register(get_level_downsamples)
Api.register(get_num_levels)
Api.register(get_level0_pathology_slide_height)
Api.register(get_pathology_slide_widths_and_heights)
Api.register(update_pathology)
Api.register(get_pathology_tile_images_for_display)
