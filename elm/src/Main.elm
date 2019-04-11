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


module Main exposing (main)

import Browser
import Color exposing (Color)
import Model exposing (ColorSelectModalStatus(..), Model)
import Update exposing (Msg, update)
import Uuid exposing (Uuid)
import View exposing (view)


main =
    Browser.element
        { init = init
        , update = update
        , view = view
        , subscriptions = subscriptions
        }



-- subscriptions


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none



-- model


init : () -> ( Model, Cmd Msg )
init () =
    ( { projectName = ""
      , projectId = Nothing
      , categories = []
      , tmpWorkingCategoryName = ""
      , tmpWorkingCategoryColor = List.head Color.materialColors
      , tmpExistingCategoryName = ""
      , availableColors = Color.materialColors
      , mode =
            { isProjectNameEditable = True
            , isAddCategoryFieldVisible = False
            , modalStatus = Model.ModalIsClosed

            --, modalStatus = Model.OpenForWorkingCategory "hoge"
            }
      , timeStamp = Nothing
      }
    , Update.getProjectId
    )
