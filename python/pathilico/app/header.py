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
import typing

from pathilico.app.di_tools import InterfaceBase, declare_method

if typing.TYPE_CHECKING:
    from pyglet.image import ImageData
    from pathilico.app.position import PositionModel
    from pathilico.app.pathology \
        import PathologyModel, OpenSlideReadRegionQuery
    from pathilico.app.zone import ZoneModel, Bound
    from pathilico.app.resource import ResourceModel
    from pathilico.app.ux import UXModel
    from pathilico.app.user import UserModel
    from pathilico.app.annotation \
        import GroupedAnnotationImageQuery, AnnotationModel, \
        PointAnnotationSerializedData
    from pathilico.app.data \
        import DatabaseModel
    from pathilico.app.model import Model
    from pathilico.app.menu import MenuModel
    ObjectId = typing.Union[int, bytes]
    Query = typing.Union[OpenSlideReadRegionQuery, GroupedAnnotationImageQuery]
    Image = typing.Union[ImageData, bytes]
    Color = typing.Tuple[int, int, int, int]
    AnnotationDisplayType = typing.Tuple[
        typing.List[typing.Tuple[int, int, ImageData]],
        typing.List[typing.Tuple[int, int, Color]],
        typing.List[typing.Tuple[typing.List[int], Color]]
    ]
    AnnotationData = typing.Union[PointAnnotationSerializedData]
    ObjectData = typing.Union[AnnotationData]


class Interface(InterfaceBase):

    # pathilico.app.position
    @staticmethod
    @declare_method
    def PositionModel() -> 'PositionModel':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def move(model: 'Model', dx: int, dy: int) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def enlarge(model: 'Model', point_x: int, point_y: int) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def shrink(model: 'Model', point_x: int, point_y: int) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def is_enlargeable(model: 'Model') -> bool:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def is_shrinkable(model: 'Model') -> bool:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_bound_for_window(model: 'Model') -> 'Bound':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_level0_coordinates(model: 'Model', window_x: int, window_y: int
                               ) -> typing.Tuple[int, int]:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_window_coordinates(
            model: 'Model', gl_x: int, gl_y: int, given_level: int
    ) -> typing.Tuple[int, int]:
        raise NotImplementedError

    # pathilico.app.pathology
    @staticmethod
    @declare_method
    def PathologyModel() -> 'PathologyModel':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_file_path(model: 'Model') -> str:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_display_name(model: 'Model') -> str:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_num_levels(model: 'Model') -> int:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_level_downsamples(model: 'Model') -> typing.Tuple[int]:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_level0_pathology_slide_height(model: 'Model') -> int:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_pathology_slide_widths_and_heights(model: 'Model')\
            -> typing.Tuple[typing.Tuple[int], typing.Tuple[int]]:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def update_pathology(
            model: 'Model', file_path: str, file_name: str, level_count: int,
            level_dimensions: typing.List[typing.Tuple[int]],
            level_downsamples: typing.List[typing.Union[int, float]]
    ) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_pathology_tile_images_for_display(
            model: 'Model') -> typing.List[typing.Tuple[int, int, 'ImageData']]:
        raise NotImplementedError

    # pathilico.app.zone
    @staticmethod
    @declare_method
    def ZoneModel() -> 'ZoneModel':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def bind_id_on_districts(
            model: 'Model',
            object_id: 'ObjectId',
            bounds: typing.List['Bound'],
            data_type: str) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def unbind_id_on_districts(
            model: 'Model',
            object_id: 'ObjectId',
            data_type: str) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_ids_on_districts(
            model: 'Model',
            bounds: typing.List['Bound'],
            data_type: str) -> typing.List['ObjectId']:
        raise NotImplementedError

    # pathilico.app.resource
    @staticmethod
    @declare_method
    def ResourceModel() -> 'ResourceModel':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def reserve_image_query(
            model: 'Model', object_id: 'ObjectId', query: 'Query') -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_images(
            model: 'Model', object_ids: typing.List['ObjectId']
    ) -> typing.Tuple[typing.List['ObjectId'], typing.List['ImageData']]:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def add_image(
            model: 'Model', object_id: 'ObjectId', query: 'Query',
            image: 'ImageData') -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def collect_queries_for_request(
            model: 'Model', object_ids: typing.List['ObjectId']
    ) -> typing.Tuple['Model', typing.List['ObjectId'], typing.List['Query']]:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def delete_image(model: 'Model', object_id: 'ObjectId') -> 'Model':
        raise NotImplementedError

    # pathilico.app.ux
    @staticmethod
    @declare_method
    def UXModel() -> 'UXModel':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_window_width_and_height(model: 'Model') -> typing.Tuple[int, int]:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def update_window_width_and_height(
            model: 'Model', width: int, height: int) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_delete_drag_start_coordinates(model: 'Model') -> typing.Tuple[int, int]:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def start_delete_drag(model: 'Model', x: int, y: int) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def update_delete_drag(model: 'Model', x: int, y: int) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def finish_delete_drag(model: 'Model') -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def is_delete_dragging(model: 'Model') -> bool:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_delete_drag_bound(
            model: 'Model') -> typing.Tuple[int, int, int, int]:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def start_line_drawing(model: 'Model', x: int, y: int) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def update_line_drawing(
            model: 'Model', x: int, y: int, dx: int, dy: int
    ) -> typing.Tuple['Model', bool, typing.Tuple[int, ...]]:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def finish_line_drawing(model: 'Model') -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def is_line_drawing(model: 'Model') -> bool:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_drawing_line_coordinates(model: 'Model') -> typing.Tuple[int, ...]:
        raise NotImplementedError

    # pathilico.app.user
    @staticmethod
    @declare_method
    def UserModel() -> 'UserModel':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def is_app_mode(model: 'Model', app_mode: str) -> bool:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def update_app_mode(model: 'Model', app_mode: str) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def is_annotation_mode(model: 'Model', annotation_mode: str) -> bool:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def update_annotation_mode(model: 'Model', annotation_mode: str) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_selected_annotation_category_id_color_and_name(
            model: 'Model') -> typing.Tuple['ObjectId', 'Color', str]:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_view_model_values(
            model: 'Model', keys: typing.Tuple[str, ...]) -> typing.Tuple:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def update_view_model_values(
            model: 'Model',
            keys: typing.Tuple[str, ...],
            values: typing.Tuple) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def update_selected_annotation_category_id(
            model: 'Model',
            category_id: 'ObjectId') -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_annotation_categories_colors_and_names(
            model: 'Model') -> typing.Tuple:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def is_autosave_enabled(model: 'Model') -> bool:
        raise NotImplementedError

    # pathilico.app.annotation
    @staticmethod
    @declare_method
    def AnnotationModel() -> 'AnnotationModel':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def add_point_annotation(
            model: 'Model', x: int, y: int, category_id: 'ObjectId') -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def add_point_annotation_from_serialized_data(
            model: 'Model',
            point_id: 'ObjectId',
            point_data: 'PointAnnotationSerializedData') -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def add_area_annotation(
            model: 'Model',
            closed_vs: typing.Tuple[int, ...],
            category_id: 'ObjectId') -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def add_area_annotation_from_serialized_data(
            model: 'Model',
            point_id: 'ObjectId',
            point_data: 'PointAnnotationSerializedData') -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def delete_point_annotations(
            model: 'Model', point_ids: typing.List['ObjectId']) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def delete_area_annotations(
            model: 'Model', area_ids: typing.List['ObjectId']) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_annotation_info_and_grouped_images_for_display(
            model: 'Model') -> 'AnnotationDisplayType':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def fill_grouped_annotation_records(model: 'Model') -> 'Model':
        raise NotImplementedError

    # pathilico.app.database
    @staticmethod
    @declare_method
    def DatabaseModel() -> 'DatabaseModel':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def register_data(
            model: 'Model', object_id: 'ObjectId', object_data: 'ObjectData',
            data_type: str, ignore_staging_status: bool = False) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def unregister_data(
            model: 'Model', object_id: 'ObjectId', data_type: str) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_queries_to_save_records(
            model: 'Model') -> typing.Tuple['Model', typing.List]:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_queries_to_load_records(model: 'Model') -> typing.List:
        raise NotImplementedError

    @staticmethod
    @declare_method
    def set_records_are_saved(
            model: 'Model',
            added_ids: typing.Tuple['ObjectId'],
            deleted_ids: typing.Tuple['ObjectId'],
            data_type: str) -> 'Model':
        raise NotImplementedError

    # pathilico.app.menu
    @staticmethod
    @declare_method
    def MenuModel() -> 'MenuModel':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def update_explored_file_names_and_paths(
            model: 'Model', names: typing.Tuple[str, ...],
            paths: typing.Tuple[str, ...]) -> 'Model':
        raise NotImplementedError

    @staticmethod
    @declare_method
    def get_explored_file_names_and_paths(
            model: 'Model'
    ) -> typing.Tuple[typing.Tuple[str, ...], typing.Tuple[str, ...]]:
        raise NotImplementedError


class Api(Interface):
    pass
