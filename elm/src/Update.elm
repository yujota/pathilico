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


module Update exposing (Msg(..), getProjectId, update)

import Color exposing (Color)
import File.Download
import Json.Encode
import Model exposing (AnnotationCategory, ColorSelectModalStatus(..), Model)
import Random
import Uuid exposing (Uuid)


type Msg
    = UpdateProjectNameField String
    | SubmitProjectName
    | UpdateWorkingCategoryNameField String
    | UpdateWorkingCategoryColor Color
    | SubmitWorkingCategory String Color
    | UpdateExistingCategoryNameField String
    | UpdateAnnotationCategory Uuid String Color
    | OpenColorSelectModalForWorkingCategory
    | OpenColorSelectModalForExistingCategory Uuid
    | CloseColorSelectModal
    | DeleteCategory Uuid
    | GetProjectId Uuid
    | DownloadConfig


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        DownloadConfig ->
            case model.projectId of
                Just uuid ->
                    let
                        jsonString =
                            Json.Encode.encode 0 <|
                                Model.encodeCategories2Json
                                    model.projectName
                                    uuid
                                    model.categories

                        downloadCmd =
                            File.Download.string
                                "config.json"
                                "application/json"
                                jsonString
                    in
                    ( model, downloadCmd )

                Nothing ->
                    ( model, Cmd.none )

        UpdateProjectNameField string ->
            ( { model | projectName = string }, Cmd.none )

        SubmitProjectName ->
            let
                newMode m =
                    { m
                        | isProjectNameEditable = False
                        , isAddCategoryFieldVisible = True
                    }
            in
            ( { model | mode = newMode model.mode }, Cmd.none )

        UpdateWorkingCategoryNameField string ->
            ( { model | tmpWorkingCategoryName = string }, Cmd.none )

        UpdateWorkingCategoryColor color ->
            let
                newModel =
                    { model | tmpWorkingCategoryColor = Just color }
            in
            ( newModel, Cmd.none )

        SubmitWorkingCategory name color ->
            let
                _ =
                    Debug.log "Submitted" (List.length model.availableColors)

                m u =
                    UpdateAnnotationCategory u name color

                aColors =
                    List.filter
                        (\c -> not (c == color))
                        model.availableColors
            in
            ( { model
                | tmpWorkingCategoryName = ""
                , availableColors = aColors
                , tmpWorkingCategoryColor = List.head aColors
              }
            , Random.generate m Uuid.uuidGenerator
            )

        UpdateExistingCategoryNameField string ->
            ( model, Cmd.none )

        UpdateAnnotationCategory uuid name color ->
            let
                _ =
                    Debug.log "added" name

                newCategory =
                    AnnotationCategory name uuid color

                ( updatedCategories, updatedAvailableColors ) =
                    updateAnnotationCategories
                        newCategory
                        model.categories
                        model.availableColors
            in
            ( { model
                | categories = updatedCategories
                , availableColors = updatedAvailableColors
              }
            , getProjectId
            )

        OpenColorSelectModalForWorkingCategory ->
            let
                newMode m =
                    { m
                        | modalStatus =
                            OpenForWorkingCategory model.tmpWorkingCategoryName
                    }
            in
            ( { model | mode = newMode model.mode }, Cmd.none )

        OpenColorSelectModalForExistingCategory uuid ->
            let
                maybeTargetCategory =
                    getCategoryByUuid uuid model.categories
            in
            case maybeTargetCategory of
                Just category ->
                    let
                        newMode m =
                            { m
                                | modalStatus =
                                    OpenForExistingCategory
                                        uuid
                            }
                    in
                    ( { model | mode = newMode model.mode }, Cmd.none )

                Nothing ->
                    ( model, Cmd.none )

        CloseColorSelectModal ->
            let
                newMode m =
                    { m | modalStatus = ModalIsClosed }
            in
            ( { model | mode = newMode model.mode }, Cmd.none )

        DeleteCategory uuid ->
            let
                maybeTargetCategory =
                    getCategoryByUuid uuid model.categories
            in
            case maybeTargetCategory of
                Just category ->
                    let
                        newList =
                            model.categories
                                |> List.filter (\c -> not (c.uuid == uuid))

                        aColors =
                            category.color :: model.availableColors
                    in
                    ( { model
                        | availableColors = aColors
                        , categories = newList
                      }
                    , getProjectId
                    )

                Nothing ->
                    ( model, Cmd.none )

        GetProjectId uuid ->
            ( { model | projectId = Just uuid }, Cmd.none )


getProjectId : Cmd Msg
getProjectId =
    Random.generate GetProjectId Uuid.uuidGenerator


getCategoryByUuid : Uuid -> List AnnotationCategory -> Maybe AnnotationCategory
getCategoryByUuid uuid categories =
    categories
        |> List.filter (\c -> c.uuid == uuid)
        |> List.head


updateAnnotationCategories :
    AnnotationCategory
    -> List AnnotationCategory
    -> List Color
    -> ( List AnnotationCategory, List Color )
updateAnnotationCategories newCategory categories colors =
    let
        newId =
            newCategory.uuid

        maybeOldCategory =
            getCategoryByUuid newId categories

        updateCat c =
            if newCategory.uuid == c.uuid then
                newCategory

            else
                c
    in
    case maybeOldCategory of
        Just oldCategory ->
            let
                newCategories =
                    List.map
                        (\c ->
                            if c == oldCategory then
                                newCategory

                            else
                                c
                        )
                        categories

                newAvailableColors =
                    colors
                        |> List.filter (\c -> not (c == newCategory.color))
                        |> (::) oldCategory.color
            in
            ( newCategories, newAvailableColors )

        Nothing ->
            let
                newCategories =
                    newCategory :: categories

                newAvailableColors =
                    colors
                        |> List.filter (\c -> not (c == newCategory.color))
            in
            ( newCategories, newAvailableColors )
