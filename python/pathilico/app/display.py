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
"""This module provide functions for user experience.
"""
from pathilico.app.header import Api


def get_window_width_and_height(model):
    """Return window width and height

    :param pathfinder.app.model.Model model:
    :return tuple[int, int]:
    """
    w, h = Api.get_window_width_and_height(model)
    return w, h


def get_pathology_display_name(model):
    """Return window width and height

    :param pathfinder.app.model.Model model:
    :return str:
    """
    name = Api.get_display_name(model)
    return name


def get_pathology_image_tiles2display(model):
    """Return window width and height

    :param pathfinder.app.model.Model model:
    :return str:
    """
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


def get_annotation_images_and_info2display(model):
    """Return window width and height

    :param pathfinder.app.model.Model model:
    :return str:
    """
    images = list()
    points = list()
    areas = list()
    return images, points, areas
