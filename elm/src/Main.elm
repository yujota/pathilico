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
import Html
    exposing
        ( Html
        , a
        , button
        , div
        , footer
        , header
        , input
        , label
        , nav
        , p
        , section
        , span
        , text
        )
import Html.Attributes exposing (..)
import Html.Events exposing (onClick, onInput)


bulmaCssLink =
    "https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.4/css/bulma.css"


type alias AnnotationCategory =
    { name : String, uuid : String, color : Color }


type alias WorkInProgressAnnotationCategory =
    { name : FieldString, color : Color }


type alias Color =
    { r : Int, g : Int, b : Int, name : String }


colors =
    [ Color 250 104 0 "Orange", Color 106 0 255 "Indigo" ]


type FieldString
    = Unfilled
    | Temp String
    | Confiremed String


type alias Model =
    { projectName : FieldString
    , categories : List AnnotationCategory
    , wipCategory : WorkInProgressAnnotationCategory
    , isColorSelectModalOpen : Bool
    }


getUnusedColor : Color
getUnusedColor =
    { r = 250, g = 104, b = 0, name = "Orange" }


initModel : Model
initModel =
    { projectName = Unfilled
    , categories = []
    , wipCategory = { name = Unfilled, color = getUnusedColor }
    , isColorSelectModalOpen = True
    }


type Msg
    = UpdateProjectName String
    | ColorSelected Color
    | SubmitProjectName
    | SubmitAnnotationCategory
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

        SubmitAnnotationCategory ->
            model

        ColorSelected color ->
            model


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
        , div [ class "container" ]
            [ messageBox <| [ projectNameField model ]
            , addCategoryField model
            , launchModal model
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


colorButton : Color -> Html Msg
colorButton color =
    let
        rgb =
            \c ->
                "rgb("
                    ++ String.fromInt color.r
                    ++ ","
                    ++ String.fromInt color.g
                    ++ ","
                    ++ String.fromInt color.b
                    ++ ")"
    in
    span [ class "button", style "color" <| rgb color ] [ text color.name ]


selectableColorList : Html Msg
selectableColorList =
    div [ class "buttons" ] <| List.map colorButton colors



{-
   [ span [ class "button" ] [ text "One" ]
   , span [ class "button" ] [ text "Two" ]
   ]
-}


launchModal : Model -> Html Msg
launchModal model =
    case model.isColorSelectModalOpen of
        True ->
            div [ class "modal is-active" ]
                [ div [ class "modal-background" ] []
                , div [ class "modal-card" ]
                    [ header [ class "modal-card-head" ]
                        [ p [ class "modal-card-title" ] [ text "Modal title" ]
                        , button
                            [ class "delete"
                            , style "aria-label" "close"
                            , onClick CloseColorSelectModal
                            ]
                            []
                        ]
                    , section [ class "modal-card-body" ]
                        [ text "Hoge"
                        , selectableColorList
                        ]
                    , footer [ class "modal-card-foot" ]
                        [ button [ class "button is-success" ] [ text "save" ]
                        , button
                            [ class "button"
                            , onClick CloseColorSelectModal
                            ]
                            [ text "Cancel" ]
                        ]
                    ]
                ]

        _ ->
            div [] []



-- TODO: 今日はModalで色の選択ができるように頑張る.


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
    case model.projectName of
        Confiremed string ->
            messageBox
                [ div [ class "field is-grouped" ]
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
                ]

        _ ->
            div [] []


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
