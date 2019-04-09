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


module View exposing (view)

import Color exposing (Color)
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (onClick, onInput)
import Model exposing (AnnotationCategory, Model)
import Update exposing (Msg(..))
import Uuid exposing (Uuid)
import Validate


bulmaCssLink =
    "https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.4/css/bulma.css"


fontAwesomeLink =
    "https://use.fontawesome.com/releases/v5.8.1/css/all.css"


view : Model -> Html Msg
view model =
    div []
        [ applyStyleSheet
        , navBar
        , boxedContentView model
        , colorSelectModalView model
        ]



-- View Helpers


boxedContentView : Model -> Html Msg
boxedContentView model =
    div [ class "container" ]
        [ div
            [ class "tile is-ancestor is-vertical"
            , style "margin-top" "1.5em"
            ]
            [ inputProjectNameFieldView model
            , inputCategoryFieldView model
            , categoryListView model
            , downloadConfigView model
            ]
        ]


inputProjectNameFieldView : Model -> Html Msg
inputProjectNameFieldView model =
    if model.mode.isProjectNameEditable then
        div [ class "tile is-parent" ]
            [ div
                [ class "tile is-child box" ]
                [ inputProjectNameField model.projectName ]
            ]

    else
        div [ class "tile is-parent" ]
            [ div
                [ class "tile is-child box" ]
                [ h4 [ class "title is-4" ]
                    [ text ("Project: " ++ model.projectName) ]
                , h5 [ class "subtitle is-5" ]
                    [ model.projectId
                        |> Maybe.map Uuid.toString
                        |> Maybe.withDefault ""
                        |> (++) "Project ID: "
                        |> text
                    ]
                ]
            ]


inputCategoryFieldView : Model -> Html Msg
inputCategoryFieldView model =
    let
        box ls =
            div [ class "tile is-parent" ]
                [ div
                    [ class "tile is-child box" ]
                    ls
                ]

        limitTxt =
            "Number of annotation categories reached to limit"
    in
    if model.mode.isAddCategoryFieldVisible then
        case model.tmpWorkingCategoryColor of
            Just color ->
                box
                    [ inputCategoryField model.tmpWorkingCategoryName color
                    ]

            Nothing ->
                let
                    maybeColor =
                        List.head model.availableColors
                in
                case maybeColor of
                    Just color ->
                        box
                            [ inputCategoryField model.tmpWorkingCategoryName color
                            ]

                    Nothing ->
                        box
                            [ div []
                                [ h4 [ class "title is-4" ]
                                    [ text "Add Annotation Category" ]
                                , h5 [ class "subtitle is-5" ]
                                    [ text limitTxt ]
                                ]
                            ]

    else
        div [] []


categoryListView : Model -> Html Msg
categoryListView model =
    let
        isVisible =
            List.length model.categories > 0
    in
    if isVisible then
        div [ class "tile is-parent" ]
            [ div
                [ class "tile is-child box" ]
                [ annotationCategoryList model.categories ]
            ]

    else
        div [] []


colorSelectModalView : Model -> Html Msg
colorSelectModalView model =
    let
        showNothing =
            div [] []
    in
    case model.mode.modalStatus of
        Model.ModalIsClosed ->
            showNothing

        Model.OpenForWorkingCategory name ->
            colorSelectModal name
                model.availableColors
                model.tmpWorkingCategoryColor
                UpdateWorkingCategoryColor

        Model.OpenForExistingCategory uuid ->
            let
                maybeCategory =
                    Model.getCategoryByUuid uuid model.categories

                _ =
                    Debug.log "category " maybeCategory
            in
            case maybeCategory of
                Just category ->
                    colorSelectModal category.name
                        model.availableColors
                        (Just category.color)
                        (UpdateAnnotationCategory uuid category.name)

                Nothing ->
                    showNothing


downloadConfigView : Model -> Html Msg
downloadConfigView model =
    let
        isVisible =
            List.length model.categories > 1
    in
    if isVisible then
        div [ class "tile is-parent" ]
            [ div [ class "tile is-child box" ]
                [ h4 [ class "title is-4" ]
                    [ text "You can download config file now" ]
                , a
                    [ class "button is-fullwidth is-success"
                    , onClick DownloadConfig
                    ]
                    [ text "Download config" ]
                ]
            ]

    else
        div [] []



-- Page contents


colorSelectModal : String -> List Color -> Maybe Color -> (Color -> Msg) -> Html Msg
colorSelectModal name colors maybeSelectedColor m =
    let
        totalColors =
            case maybeSelectedColor of
                Just color ->
                    if List.member color colors then
                        colors

                    else
                        color :: colors

                Nothing ->
                    colors

        colorButton c =
            let
                buttonStyle =
                    case maybeSelectedColor of
                        Just sc ->
                            if c == sc then
                                [ style "background-color" (Color.toRgbString c)
                                , style "color" "white"
                                ]

                            else
                                [ style "color" (Color.toRgbString c) ]

                        Nothing ->
                            [ style "color" (Color.toRgbString c) ]
            in
            span
                ([ class "button", onClick (m c) ] ++ buttonStyle)
                [ text c.name ]

        selectableColorList =
            if List.isEmpty colors then
                text "No available color found"

            else
                div [ class "buttons" ] <| List.map colorButton totalColors

        modalContent =
            section [ class "modal-card-body" ] [ selectableColorList ]

        modalHeader =
            header [ class "modal-card-head" ]
                [ p
                    [ class "modal-card-title"
                    ]
                    [ text <| "Select color for: " ++ name ]
                ]

        modalFooter =
            footer [ class "modal-card-foot" ]
                [ button
                    [ class "button is-fullwidth"
                    , onClick CloseColorSelectModal
                    ]
                    [ text "Close" ]
                ]
    in
    div [ class "modal is-active" ]
        [ div [ class "modal-background" ] []
        , div [ class "modal-card" ] [ modalHeader, modalContent, modalFooter ]
        , button
            [ class "modal-close is-large"
            , style "aria-label" "close"
            , onClick CloseColorSelectModal
            ]
            []
        ]


navBar : Html Msg
navBar =
    nav [ class "navbar is-primary" ]
        [ div [ class "navbar-brand" ]
            [ a [ class "navbar-item" ]
                [ text "Project Configuration Tool" ]
            ]
        ]


applyStyleSheet : Html Msg
applyStyleSheet =
    div []
        [ Html.node "link"
            [ Html.Attributes.rel "stylesheet"
            , Html.Attributes.href bulmaCssLink
            ]
            []
        , Html.node "link"
            [ Html.Attributes.rel "stylesheet"
            , Html.Attributes.href fontAwesomeLink
            ]
            []
        ]


inputProjectNameField : String -> Html Msg
inputProjectNameField name =
    let
        submitProjectNameButton =
            if Validate.isValidProjectName name then
                a
                    [ class "button is-info"
                    , onClick SubmitProjectName
                    ]
                    [ text "Add category" ]

            else
                a [ class "button is-static" ] [ text "Add category" ]
    in
    div []
        [ h4 [ class "title is-4" ] [ text "Add Annotation Category" ]
        , div [ class "field is-grouped" ]
            [ p [ class "control is-expanded" ]
                [ input
                    [ class "input"
                    , placeholder "Input project name"
                    , value name
                    , onInput UpdateProjectNameField
                    ]
                    []
                ]
            , p [ class "control" ] [ submitProjectNameButton ]
            ]
        ]


inputCategoryField : String -> Color -> Html Msg
inputCategoryField name color =
    let
        colorSelectButton =
            a
                [ class "button"
                , style "background-color" (Color.toRgbString color)
                , style "color" "white"
                , onClick OpenColorSelectModalForWorkingCategory
                ]
                [ text <| "Color: " ++ color.name ]

        submitAnnotationButton =
            if Validate.isValidCategoryName name then
                a
                    [ class "button is-info"
                    , onClick (SubmitWorkingCategory name color)
                    ]
                    [ text "Add category" ]

            else
                a [ class "button is-static" ] [ text "Add category" ]
    in
    div []
        [ h4 [ class "title is-4" ] [ text "Add Annotation Category" ]
        , div [ class "field is-grouped" ]
            [ p [ class "control is-expanded" ]
                [ input
                    [ class "input"
                    , placeholder "Input category name"
                    , value name
                    , onInput UpdateWorkingCategoryNameField
                    ]
                    []
                ]
            , p [ class "control" ] [ colorSelectButton ]
            , p [ class "control" ] [ submitAnnotationButton ]
            ]
        ]


annotationCategoryList : List AnnotationCategory -> Html Msg
annotationCategoryList categories =
    let
        tableElements =
            [ tr []
                [ th [] [ abbr [ title "ID" ] [ text "ID" ] ]
                , th []
                    [ abbr [ title "Category" ] [ text "Annotation Category" ] ]
                , th []
                    [ abbr [ title "Color" ] [ text "Annotation Color" ] ]
                , th [] []
                ]
            ]

        header =
            thead [] tableElements

        footer =
            tfoot [] tableElements

        colorButton cat =
            a
                [ class "button is-small"
                , style "background-color" (Color.toRgbString cat.color)
                , style "color" "white"
                , onClick (OpenColorSelectModalForExistingCategory cat.uuid)
                ]
                [ text cat.color.name ]

        row category =
            tr []
                [ th [] [ text (Uuid.toString category.uuid) ]
                , td []
                    [ text category.name

                    --, span [ class "icon" ] [ i [ class "fas fa-wrench" ] [] ]
                    ]
                , td [] [ colorButton category ]
                , td []
                    [ a
                        [ class "delete"
                        , onClick (DeleteCategory category.uuid)
                        ]
                        []
                    ]
                ]
    in
    table [ class "table is-fullwidth is-hoverable" ]
        [ header
        , tbody [] <| List.map row categories
        , footer
        ]
