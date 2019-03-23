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
from pathilico.app.header import Api
from pathilico.app.views.welcome_screen import welcome_screen
from pathilico.app.views.pathlogy_view import pathology_view
from pathilico.app.views.file_select_view import file_select_view


def view(model):
    if Api.is_app_mode(model, "annotation"):
        return pathology_view(model)
    elif Api.is_app_mode(model, "welcome_screen"):
        return welcome_screen(model)
    elif Api.is_app_mode(model, "file_select"):
        return file_select_view(model)
    else:
        return pathology_view(model)
