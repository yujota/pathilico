--  Copyright
--    2019 Department of Dermatology, School of Medicine, Tohoku University
--
--  Licensed under the Apache License, Version 2.0 (the "License");
--  you may not use this file except in compliance with the License.
--  You may obtain a copy of the License at
--
--      http://www.apache.org/licenses/LICENSE-2.0
--
--  Unless required by applicable law or agreed to in writing, software
--  distributed under the License is distributed on an "AS IS" BASIS,
--  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
--  See the License for the specific language governing permissions and
--  limitations under the License.


module Model exposing (AnnotationCategory, AppMode, ColorSelectModalStatus(..), Model, encodeCategories2Json, getCategoryByUuid)

import Browser
import Color exposing (Color)
import Json.Encode
import Uuid exposing (Uuid)


jsonVersion =
    "1.0"


type alias Model =
    { projectName : String
    , projectId : Maybe Uuid
    , categories : List AnnotationCategory
    , tmpWorkingCategoryName : String
    , tmpWorkingCategoryColor : Maybe Color
    , tmpExistingCategoryName : String
    , availableColors : List Color
    , mode : AppMode
    }


type alias AnnotationCategory =
    { name : String, uuid : Uuid, color : Color }


type ColorSelectModalStatus
    = ModalIsClosed
    | OpenForWorkingCategory String
    | OpenForExistingCategory Uuid


type alias AppMode =
    { isProjectNameEditable : Bool
    , isAddCategoryFieldVisible : Bool
    , modalStatus : ColorSelectModalStatus
    }


getCategoryByUuid : Uuid -> List AnnotationCategory -> Maybe AnnotationCategory
getCategoryByUuid uuid categories =
    categories
        |> List.filter (\c -> c.uuid == uuid)
        |> List.head


encodeColor2Json : Color -> Json.Encode.Value
encodeColor2Json color =
    Json.Encode.object
        [ ( "name", Json.Encode.string color.name )
        , ( "r", Json.Encode.int color.r )
        , ( "g", Json.Encode.int color.g )
        , ( "b", Json.Encode.int color.b )
        ]


encodeAnnotationCategory2Json : AnnotationCategory -> Json.Encode.Value
encodeAnnotationCategory2Json annotationCategory =
    Json.Encode.object
        [ ( "uuid", Uuid.encode annotationCategory.uuid )
        , ( "name", Json.Encode.string annotationCategory.name )
        , ( "color", encodeColor2Json annotationCategory.color )
        ]


encodeCategories2Json :
    String
    -> Uuid.Uuid
    -> List AnnotationCategory
    -> Json.Encode.Value
encodeCategories2Json projectName id v =
    Json.Encode.object
        [ ( "categories", Json.Encode.list encodeAnnotationCategory2Json v )
        , ( "version", Json.Encode.string jsonVersion )
        , ( "projectName", Json.Encode.string projectName )
        , ( "projectId", Uuid.encode id )
        ]
