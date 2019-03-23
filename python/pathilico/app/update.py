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
from pathilico.pygletelm.effect import Commands
import pathilico.app.updates.update_position as update_position
import pathilico.app.updates.update_data as update_data
import pathilico.app.updates.update_ux as update_ux
import pathilico.app.updates.update_annotation as update_annotation
import pathilico.app.updates.update_database as update_database


def update(msg, model):
    if msg in update_position.TARGET_MESSAGES:
        return update_position.update(msg, model)
    elif msg in update_data.TARGET_MESSAGES:
        return update_data.update(msg, model)
    elif msg in update_ux.TARGET_MESSAGES:
        return update_ux.update(msg, model)
    elif msg in update_annotation.TARGET_MESSAGES:
        return update_annotation.update(msg, model)
    elif msg in update_database.TARGET_MESSAGES:
        return update_database.update(msg, model)
    return model, Commands()
