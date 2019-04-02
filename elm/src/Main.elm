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
import Colors exposing (Color, materialColors)
import Html exposing (Html, a, button, div, input, label, nav, p, span, text)
import Html.Attributes exposing (..)
import Html.Events exposing (onClick, onInput)


bulmaCssLink =
    "https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.4/css/bulma.css"


type alias AnnotationCategory =
    String


type alias Color =
    { r : Int, g : Int, b : Int, a : Int }


type FieldString
    = Unfilled
    | Temp String
    | Confiremed String


type alias Model =
    { projectName : FieldString
    , categories : List AnnotationCategory
    , isColorSelectModalOpen : Bool
    }


initModel : Model
initModel =
    { projectName = Unfilled
    , categories = []
    , isColorSelectModalOpen = True
    }


type Msg
    = UpdateProjectName String
    | SubmitProjectName
    | OpenColorSelectModal
    | CloseColorSelectModal


update : Msg -> Model -> Model
update msg model =
    case msg of
        UpdateProjectName name ->
            { model | projectName = Temp name }

        SubmitProjectName ->
            case model.projectName of
                Unfilled ->
                    model

                Temp string ->
                    if string == "" then
                        model

                    else
                        { model | projectName = Confiremed string }

                Confiremed string ->
                    model

        CloseColorSelectModal ->
            { model | isColorSelectModalOpen = False }

        OpenColorSelectModal ->
            { model | isColorSelectModalOpen = True }


isValidProjectName : FieldString -> Bool
isValidProjectName nameField =
    case nameField of
        Unfilled ->
            False

        Temp string ->
            if string == "" then
                False

            else
                True

        Confiremed string ->
            True


view : Model -> Html Msg
view model =
    div []
        [ applyStyle
        , navBar
        , launchModal model
        , div [ class "container" ]
            [ messageBox <| [ projectNameField model ]
            , messageBox <| [ addCategoryField model ]
            ]
        ]


projectNameFieldOld : Model -> Html Msg
projectNameFieldOld model =
    div []
        [ input
            [ placeholder "Input project name", onInput UpdateProjectName ]
            []
        , button
            [ onClick SubmitProjectName
            , disabled <| not <| isValidProjectName model.projectName
            ]
            [ text "submit" ]
        , p [ style "background-color" "red" ] [ text "hoge" ]
        ]


getButtonClass : Model -> String
getButtonClass model =
    if isValidProjectName model.projectName then
        "button is-info"

    else
        "button is-static"


launchModal : Model -> Html Msg
launchModal model =
    case model.isColorSelectModalOpen of
        True ->
            div [ class "modal is-active" ]
                [ div [ class "modal-background" ] []
                , div
                    [ class "modal-content" ]
                    [ selectColor ]
                , button
                    [ class "modal-close is-large"
                    , style "aria-label" "close"
                    , onClick CloseColorSelectModal
                    ]
                    []
                ]

        _ ->
            div [] []


selectColor : Html Msg
selectColor =
    div [ class "field" ]
        [ label [ class "label" ] [ text "Label" ]
        , div [ class "control" ] [ input [] [] ]
        ]


projectNameField : Model -> Html Msg
projectNameField model =
    case model.projectName of
        Confiremed string ->
            text <| "Project Name: " ++ string

        _ ->
            div [ class "field is-grouped" ]
                [ p [ class "control is-expanded" ]
                    [ input
                        [ class "input"
                        , placeholder "Input project name"
                        , onInput UpdateProjectName
                        ]
                        []
                    ]
                , p
                    [ class "control"
                    ]
                    [ a
                        [ onClick SubmitProjectName
                        , class <| getButtonClass model
                        ]
                        [ text "Go Next" ]
                    ]
                ]


addCategoryField : Model -> Html Msg
addCategoryField model =
    div [ class "field is-grouped" ]
        [ p [ class "control is-expanded" ]
            [ input
                [ class "input"
                , placeholder "Input category name"
                , onInput UpdateProjectName
                ]
                []
            ]
        , p
            [ class "control"
            ]
            [ a
                [ onClick OpenColorSelectModal
                , class <| getButtonClass model
                ]
                [ text "Color: Magenta" ]
            ]
        , p
            [ class "control"
            ]
            [ a
                [ onClick SubmitProjectName
                , class <| getButtonClass model
                ]
                [ text "Add category" ]
            ]
        ]


applyStyle : Html Msg
applyStyle =
    Html.node "link"
        [ Html.Attributes.rel "stylesheet"
        , Html.Attributes.href bulmaCssLink
        ]
        []


messageBox : List (Html Msg) -> Html Msg
messageBox hs =
    div
        [ class "tile is-ancestor"
        ]
        [ div [ class "tile  is-parent" ]
            [ div [ class "tile is-child box" ] hs
            ]
        ]


navBar : Html msg
navBar =
    nav [ class "navbar is-primary" ]
        [ div [ class "navbar-brand" ]
            [ a [ class "navbar-item" ] [ text "Project Configuration Tool" ] ]
        ]


main =
    Browser.sandbox { init = initModel, update = update, view = view }
