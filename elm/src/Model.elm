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


module Model exposing
    ( AnnotationCategory
    , ColorSelectModalStatus(..)
    , Model
    , decodeJson2ProjectConfig
    , encodeCategories2Json
    , getCategoryByUuid
    )

import Browser
import Color exposing (Color)
import Json.Decode
import Json.Encode
import Time exposing (Posix)
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
    , timeStamp : Maybe Posix
    }


type alias AnnotationCategory =
    { name : String, uuid : Uuid, color : Color }


type alias ProjectConfig =
    { name : String
    , uuid : Uuid
    , categories : List AnnotationCategory
    , version : String
    , timeStamp : Posix
    }


type ColorSelectModalStatus
    = ModalIsClosed
    | OpenForWorkingCategory String
    | OpenForExistingCategory Uuid


type alias AppMode =
    { isProjectNameEditable : Bool
    , isAddCategoryFieldVisible : Bool
    , modalStatus : ColorSelectModalStatus
    }


getCategoryByUuid :
    Uuid
    -> List AnnotationCategory
    -> Maybe AnnotationCategory
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


decodeJson2Color : Json.Decode.Decoder Color
decodeJson2Color =
    Json.Decode.map4
        Color
        (Json.Decode.field "r" Json.Decode.int)
        (Json.Decode.field "g" Json.Decode.int)
        (Json.Decode.field "b" Json.Decode.int)
        (Json.Decode.field "name" Json.Decode.string)


encodeAnnotationCategory2Json : AnnotationCategory -> Json.Encode.Value
encodeAnnotationCategory2Json annotationCategory =
    Json.Encode.object
        [ ( "uuid", Uuid.encode annotationCategory.uuid )
        , ( "name", Json.Encode.string annotationCategory.name )
        , ( "color", encodeColor2Json annotationCategory.color )
        ]


decodeJson2AnnotationCategory : Json.Decode.Decoder AnnotationCategory
decodeJson2AnnotationCategory =
    Json.Decode.map3
        AnnotationCategory
        (Json.Decode.field "name" Json.Decode.string)
        (Json.Decode.field "uuid" Uuid.decoder)
        (Json.Decode.field "color" decodeJson2Color)


encodeCategories2Json :
    String
    -> Uuid.Uuid
    -> List AnnotationCategory
    -> Posix
    -> Json.Encode.Value
encodeCategories2Json projectName id v timeStamp =
    Json.Encode.object
        [ ( "categories", Json.Encode.list encodeAnnotationCategory2Json v )
        , ( "version", Json.Encode.string jsonVersion )
        , ( "projectName", Json.Encode.string projectName )
        , ( "projectId", Uuid.encode id )
        , ( "timeStampMillis"
          , (Json.Encode.int << Time.posixToMillis)
                timeStamp
          )
        ]


decodeJson2ProjectConfig : Json.Decode.Decoder ProjectConfig
decodeJson2ProjectConfig =
    Json.Decode.map5
        ProjectConfig
        (Json.Decode.field "projectName" Json.Decode.string)
        (Json.Decode.field "projectId" Uuid.decoder)
        (Json.Decode.field "categories"
            (Json.Decode.list decodeJson2AnnotationCategory)
        )
        (Json.Decode.field "version" Json.Decode.string)
        (Json.Decode.field "timeStampMillis" (Json.Decode.map Time.millisToPosix Json.Decode.int))
