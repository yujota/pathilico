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
        , abbr
        , button
        , div
        , footer
        , h2
        , header
        , input
        , label
        , nav
        , p
        , section
        , span
        , table
        , tbody
        , td
        , text
        , tfoot
        , th
        , thead
        , tr
        )
import Html.Attributes exposing (..)
import Html.Events exposing (onClick, onInput)


bulmaCssLink =
    "https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.4/css/bulma.css"


type alias AnnotationCategory =
    { name : String, uuid : String, color : Color }


type alias Color =
    { r : Int, g : Int, b : Int, name : String }


color2string : Color -> String
color2string color =
    "rgb("
        ++ String.fromInt color.r
        ++ ","
        ++ String.fromInt color.g
        ++ ","
        ++ String.fromInt color.b
        ++ ")"


materialColors =
    [ Color 250 104 0 "Orange", Color 106 0 255 "Indigo" ]


type FieldString
    = Unfilled
    | Temp String
    | Confiremed String


type alias Model =
    { projectName : FieldString
    , categories : List AnnotationCategory
    , wipCategoryName : String
    , wipCategoryColor : Maybe Color
    , wipAvailableColors : List Color
    , isColorSelectModalOpen : Bool
    }


initModel : Model
initModel =
    { projectName = Unfilled
    , categories = []
    , wipCategoryName = ""
    , wipCategoryColor = List.head materialColors
    , wipAvailableColors = materialColors
    , isColorSelectModalOpen = False
    }


type Msg
    = UpdateProjectName String
    | SubmitProjectName
    | UpdateCategoryName String
    | UpdateCategoryColor Color
    | SubmitAnnotationCategory String Color
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
            { model
                | isColorSelectModalOpen = True
                , wipCategoryColor = Nothing
            }

        UpdateCategoryName name ->
            { model | wipCategoryName = name }

        UpdateCategoryColor color ->
            { model | wipCategoryColor = Just color }

        SubmitAnnotationCategory name color ->
            let
                isNotSelectedColor =
                    \c ->
                        if c == color then
                            False

                        else
                            True

                availableColors =
                    List.filter isNotSelectedColor model.wipAvailableColors

                category =
                    AnnotationCategory name "" color
            in
            { model
                | wipCategoryName = ""
                , wipCategoryColor = List.head availableColors
                , wipAvailableColors = availableColors
                , categories = category :: model.categories
                , isColorSelectModalOpen = False
            }



-- View


view : Model -> Html Msg
view model =
    let
        applyStyle =
            Html.node "link"
                [ Html.Attributes.rel "stylesheet"
                , Html.Attributes.href bulmaCssLink
                ]
                []

        messageBox hs =
            div
                [ class "tile is-ancestor"
                ]
                [ div [ class "tile  is-parent" ]
                    [ div [ class "tile is-child box" ] hs
                    ]
                ]

        navBar =
            nav [ class "navbar is-primary" ]
                [ div [ class "navbar-brand" ]
                    [ a [ class "navbar-item" ] [ text "Project Configuration Tool" ] ]
                ]

        page ls =
            div []
                [ applyStyle
                , navBar
                , div [ class "container" ]
                    [ div [ class "tile is-ancestor is-vertical" ] ls
                    ]
                ]

        configureProjNameTxt =
            "Configure annotation catogories for project : "
    in
    case model.projectName of
        Confiremed pName ->
            let
                pNameAndCategoryField =
                    [ div [ class "tile is-parent is-12" ]
                        [ div [ class "tile is-child box" ]
                            [ h2 [] [ text (configureProjNameTxt ++ pName) ]
                            , addCategoryField
                                model.wipCategoryName
                                model.wipCategoryColor
                            ]
                        ]
                    ]

                categoryList =
                    [ div [ class "tile is-parent is-12" ]
                        [ div [ class "tile is-child box" ]
                            [ annotationCategoryList model.categories
                            ]
                        ]
                    ]

                pageContent =
                    if List.isEmpty model.categories then
                        pNameAndCategoryField

                    else
                        pNameAndCategoryField ++ categoryList

                pageContentWithModal =
                    if model.isColorSelectModalOpen then
                        pageContent
                            ++ [ colorSelectModal model.wipCategoryName
                                    model.wipAvailableColors
                                    model.wipCategoryColor
                               ]

                    else
                        pageContent
            in
            page pageContentWithModal

        _ ->
            page
                [ div [ class "tile is-parent" ]
                    [ div [ class "tile is-child box" ]
                        [ text "Enter project name"
                        , projectNameInputField model.projectName
                        ]
                    ]
                ]


colorSelectModal : String -> List Color -> Maybe Color -> Html Msg
colorSelectModal categoryName availableColors selectedColor =
    let
        modalHeader =
            header [ class "modal-card-head" ]
                [ p
                    [ class "modal-card-title"
                    ]
                    [ text <| "Select color for:" ++ categoryName ]
                , button
                    [ class "delete"
                    , style "aria-label" "close"
                    , onClick CloseColorSelectModal
                    ]
                    []
                ]

        footerOkButtonAttr =
            case selectedColor of
                Just c ->
                    [ class "button is-success"
                    , onClick <|
                        SubmitAnnotationCategory categoryName c
                    ]

                Nothing ->
                    [ class "button is-static" ]

        modalFooter =
            footer [ class "modal-card-foot" ]
                [ button footerOkButtonAttr [ text "OK" ]
                , button
                    [ class "button", onClick CloseColorSelectModal ]
                    [ text "Cancel" ]
                ]

        colorButton c =
            let
                buttonStyle =
                    case selectedColor of
                        Just sc ->
                            if c == sc then
                                [ style "background-color" (color2string c)
                                , style "color" "white"
                                ]

                            else
                                [ style "color" (color2string c) ]

                        Nothing ->
                            [ style "color" (color2string c) ]
            in
            span
                ([ class "button", onClick (UpdateCategoryColor c) ]
                    ++ buttonStyle
                )
                [ text c.name ]

        selectableColorList =
            if List.isEmpty availableColors then
                text "No available color found"

            else
                div [ class "buttons" ] <| List.map colorButton availableColors

        modalContent =
            section [ class "modal-card-body" ] [ selectableColorList ]
    in
    div [ class "modal is-active" ]
        [ div [ class "modal-background" ] []
        , div [ class "modal-card" ]
            [ modalHeader
            , modalContent
            , modalFooter
            ]
        ]


projectNameInputField : FieldString -> Html Msg
projectNameInputField projectNameField =
    let
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

        name =
            case projectNameField of
                Unfilled ->
                    ""

                Temp string ->
                    string

                Confiremed string ->
                    string

        submitButtonAttr =
            if isValidProjectName projectNameField then
                [ class "button is-info", onClick SubmitProjectName ]

            else
                [ class "button is-static" ]
    in
    div [ class "field is-grouped" ]
        [ p [ class "control is-expanded" ]
            [ input
                [ class "input"
                , placeholder "Input project name"
                , value name
                , onInput UpdateProjectName
                ]
                []
            ]
        , p
            [ class "control" ]
            [ a submitButtonAttr [ text "Go Next" ] ]
        ]


addCategoryField : String -> Maybe Color -> Html Msg
addCategoryField categoryName maybeColor =
    let
        _ =
            Debug.log categoryName

        _ =
            Debug.toString selectColorButton

        isValidCategoryName name =
            if name == "" then
                False

            else
                True

        selectColorButton =
            if not (isValidCategoryName categoryName) then
                a [ class "button is-static" ] [ text "---" ]

            else
                case maybeColor of
                    Just color ->
                        a
                            [ class "button"
                            , style "background-color" (color2string color)
                            , style "color" "white"
                            , onClick OpenColorSelectModal
                            ]
                            [ text <| "Color: " ++ color.name ]

                    Nothing ->
                        a [ class "button", onClick OpenColorSelectModal ]
                            [ text "Select color" ]

        submitCategoryButton =
            case maybeColor of
                Just c ->
                    if isValidCategoryName categoryName then
                        a
                            [ class "button is-info"
                            , onClick <|
                                SubmitAnnotationCategory categoryName c
                            ]
                            [ text "Add category" ]

                    else
                        a [ class "button is-static" ] [ text "Add category" ]

                Nothing ->
                    a [ class "button is-static" ] [ text "Add category" ]
    in
    div [ class "field is-grouped" ]
        [ p [ class "control is-expanded" ]
            [ input
                [ class "input"
                , placeholder "Input category name"
                , onInput UpdateCategoryName
                , value categoryName
                ]
                []
            ]
        , p [ class "control" ] [ selectColorButton ]
        , p [ class "control" ] [ submitCategoryButton ]
        ]


annotationCategoryList : List AnnotationCategory -> Html Msg
annotationCategoryList categories =
    let
        header =
            thead []
                [ tr []
                    [ th [] [ abbr [ title "ID" ] [ text "ID" ] ]
                    , th []
                        [ abbr [ title "Category" ]
                            [ text "Annotation Category" ]
                        ]
                    , th []
                        [ abbr [ title "Color" ]
                            [ text "Annotation Color" ]
                        ]
                    ]
                ]

        footer =
            tfoot []
                [ tr []
                    [ th [] [ abbr [ title "ID" ] [ text "ID" ] ]
                    , th []
                        [ abbr [ title "Category" ]
                            [ text "Annotation Category" ]
                        ]
                    , th []
                        [ abbr [ title "Color" ]
                            [ text "Annotation Color" ]
                        ]
                    ]
                ]

        row category =
            tr []
                [ th [] [ text category.uuid ]
                , td [] [ text category.name ]
                , td [] [ text <| color2string category.color ]
                ]
    in
    table [ class "table is-fullwidth is-hoverable" ]
        [ header
        , tbody [] <| List.map row categories
        , footer
        ]


main =
    Browser.sandbox { init = initModel, update = update, view = view }
