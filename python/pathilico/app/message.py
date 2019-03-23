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
from pathilico.pygletelm.message import UnionMessage, Message


class Msg(UnionMessage):
    Move = Message("dx", "dy")
    PathologyRegionAcquired = Message(
        "location", "level", "size", "image", "pathology_id", "query"
    )
    GroupedAnnotationImageAcquired = Message("query", "image", "ga_id")
    ExecGroupAnnotation = Message()
    RecordSaved = Message(
        "flag", "error_message", "added_ids", "deleted_ids", "data_type"
    )
    ExecSaveToDatabase = Message()
    RecordLoaded = Message(
        "flag", "error_message", "record_ids", "records", "data_type"
    )
    ExecLoadFromDatabase = Message()
    SlideInfoAcquired = Message(
        "level_count", "level_dimensions", "file_path", "file_name",
        "level_downsamples"
    )
    Enlarge = Message("x", "y")
    Shrink = Message("x", "y")
    Rescale = Message("win_x", "win_y", "enlarge")
    RescaleByMouseScroll = Message("x", "y", "scroll_x", "scroll_y")
    WsiFileListAcquired = Message("file_names", "file_paths")
    FileSelected = Message("path")
    AnnotationTypeSelected = Message("category_id")
    UpdateViewModel = Message("keys", "values")
    AskFilePath = Message()
    AddPoint = Message("x", "y", "category_id")
    DeletePointArea = Message("x", "y", "width", "height")
    DeleteDragStartAt = Message("x", "y")
    DeleteDragAt = Message("x", "y")
    DeleteDragEndAt = Message("x", "y")
    DrawLineDragStartAt = Message("x", "y")
    DrawLineDragAt = Message("x", "y", "dx", "dy")
    DrawLineDragEndAt = Message("x", "y")
    ChangeMode = Message("new_mode")
    ChangeAnnotationMode = Message("new_mode")
