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
from pathilico.app.views.color import MetroColors  # For mock
from pathilico.app.header import Api


# Essential APIs
APP_MODES = dict(
    undefined=-1,
    readonly_view=0,
    annotation=1,
    welcome_screen=2,
    file_select=3
)


ANNOTATION_MODES = dict(
    undefined=-1,
    pan=0,
    point=1,
    area=2,
    delete=3
)


MOCK_ANNOTATION_COLORS = MetroColors.all
MOCK_ANNOTATION_NAMES = MetroColors.all_names
MOCK_ANNOTATION_TYPES = tuple([
    (12345000 + i).to_bytes(4, 'little') for i in range(len(MetroColors.all))
])


class AnnotationUtilModel(object):
    def __init__(
            self,
            annotation_types=MOCK_ANNOTATION_TYPES,
            annotation_colors=MOCK_ANNOTATION_COLORS,
            annotation_names=MOCK_ANNOTATION_NAMES
    ):
        self.current_annotation_mode = 0
        self.selected_annotation_index = 0
        self.annotation_colors = annotation_colors
        self.annotation_types = annotation_types
        self.annotation_names = annotation_names


class ViewModel(object):
    _keys = ("bottom_bar_index", )

    def __init__(self):
        self.bottom_bar_index = 0


class UserModel(object):
    def __init__(self):
        self.app_mode = 0
        self.annotation_util = AnnotationUtilModel()
        self.view_model = ViewModel()


# Public APIs
def is_app_mode(model, app_mode):
    app_mode_index = APP_MODES.get(app_mode, -1)
    return model.user.app_mode == app_mode_index


def update_app_mode(model, app_mode):
    app_mode_index = APP_MODES.get(app_mode, -1)
    if app_mode_index is not -1:
        model.user.app_mode = app_mode_index
    return model


def is_annotation_mode(model, annotation_mode):
    mode_index = ANNOTATION_MODES.get(annotation_mode, -1)
    return model.user.annotation_util.current_annotation_mode == mode_index


def update_annotation_mode(model, annotation_mode):
    mode_index = ANNOTATION_MODES.get(annotation_mode, -1)
    if mode_index is not -1:
        model.user.annotation_util.current_annotation_mode = mode_index
    return model


def update_selected_annotation_category_id(model, category_id):
    a_util = model.user.annotation_util
    if category_id in a_util.annotation_types:
        a_util.selected_annotation_index = a_util.annotation_types.index(
            category_id
        )
    return model


def get_selected_annotation_category_id_color_and_name(model):
    a_util = model.user.annotation_util
    if a_util.selected_annotation_index >= len(a_util.annotation_types):
        default = (0, 0, 0, 255)
        r = (b"\x00", default, "")
        return r
    else:
        c_id = a_util.annotation_types[a_util.selected_annotation_index]
        c = a_util.annotation_colors[a_util.selected_annotation_index]
        name = a_util.annotation_colors[a_util.selected_annotation_index]
        return c_id, c, name


def get_annotation_categories_colors_and_names(model):
    a_util = model.user.annotation_util
    r = (
        a_util.annotation_types,
        a_util.annotation_colors,
        a_util.annotation_names
    )
    return r


def get_view_model_values(model, keys):
    vals = [getattr(model.user.view_model, k) for k in keys]
    return tuple(vals)


def update_view_model_values(model, keys, values):
    for k, v in zip(keys, values):
        setattr(model.user.view_model, k, v)
    return model


def is_autosave_enabled(model):
    return True


Api.register(UserModel)
Api.register(is_app_mode)
Api.register(update_app_mode)
Api.register(is_annotation_mode)
Api.register(update_annotation_mode)
Api.register(get_selected_annotation_category_id_color_and_name)
Api.register(get_view_model_values)
Api.register(get_annotation_categories_colors_and_names)
Api.register(update_view_model_values)
Api.register(update_selected_annotation_category_id)
Api.register(is_autosave_enabled)
