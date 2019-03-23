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
from pathilico.app.message import Msg
from pathilico.app.ports.file_explore import get_explore_file_commands


class Model(object):
    def __init__(self):
        self.position = Api.PositionModel()
        self.pathology = Api.PathologyModel()
        self.zone = Api.ZoneModel()
        self.resource = Api.ResourceModel()
        self.ux = Api.UXModel()
        self.user = Api.UserModel()
        self.annotation = Api.AnnotationModel()
        self.database = Api.DatabaseModel()
        self.menu = Api.MenuModel()


def init_model():
    model = Model()
    model = Api.update_app_mode(model, "file_select")
    search_dir = ("~/DataForML/svs", )
    cmds = get_explore_file_commands(search_dir, Msg.WsiFileListAcquired)
    return model, cmds
