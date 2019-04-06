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
import File.Download
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
        , i
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
import Json.Encode
import Random
import Uuid


bulmaCssLink =
    "https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.4/css/bulma.css"


fontAwesomeLink =
    "https://use.fontawesome.com/releases/v5.8.1/css/all.css"


type alias AnnotationCategory =
    { name : String, uuid : Uuid.Uuid, color : Color }


jsonVersion =
    "1.0"


encodeAnnotationCategory2Json : AnnotationCategory -> Json.Encode.Value
encodeAnnotationCategory2Json annotationCategory =
    Json.Encode.object
        [ ( "uuid", Uuid.encode annotationCategory.uuid )
        , ( "name", Json.Encode.string annotationCategory.name )
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
    [ Color 250 104 0 "Orange"
    , Color 240 163 10 "Amber"
    , Color 227 200 0 "Yellow"
    , Color 130 90 44 "Brown"
    , Color 109 135 100 "Olive"
    , Color 100 118 135 "Steel"
    , Color 118 96 138 "Mauve"
    , Color 160 82 45 "Sienna"
    , Color 164 196 0 "Lime"
    , Color 96 169 23 "Green"
    , Color 0 138 0 "Emerald"
    , Color 0 171 169 "Teal"
    , Color 27 161 226 "Cyan"
    , Color 0 80 239 "Cobalt"
    , Color 106 0 255 "Indigo"
    , Color 170 0 255 "Violet"
    , Color 244 114 208 "Pink"
    , Color 216 0 115 "Magenta"
    , Color 162 0 37 "Crimson"
    , Color 229 20 0 "Red"
    ]


type FieldString
    = Unfilled
    | Temp String
    | Confiremed String


type alias Model =
    { projectName : FieldString
    , projectId : Maybe Uuid.Uuid
    , categories : List AnnotationCategory
    , wipCategoryName : String
    , wipCategoryColor : Maybe Color
    , wipCategoryId : Maybe Uuid.Uuid
    , wipAvailableColors : List Color
    , isColorSelectModalOpen : Bool
    }


initModel : Model
initModel =
    { projectName = Unfilled
    , projectId = Nothing
    , categories = []
    , wipCategoryName = ""
    , wipCategoryColor = List.head materialColors
    , wipCategoryId = Nothing
    , wipAvailableColors = materialColors
    , isColorSelectModalOpen = False
    }


init : () -> ( Model, Cmd Msg )
init _ =
    ( initModel, Cmd.none )


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none



-- Update


type Msg
    = UpdateProjectName String
    | SubmitProjectName
    | UpdateCategoryName String
    | UpdateCategoryColor (Maybe Uuid.Uuid) Color
    | SubmitAnnotationCategory String Color
    | AddAnnotationCategory String Color Uuid.Uuid
    | DeleteAnnotationCategory Uuid.Uuid
    | OpenColorSelectModal (Maybe Uuid.Uuid) (Maybe Color)
    | CloseColorSelectModal
    | DownloadConfig
    | UpdateProjectId Uuid.Uuid


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        UpdateProjectName name ->
            ( { model | projectName = Temp name }, Cmd.none )

        UpdateProjectId id ->
            ( { model | projectId = Just id }, Cmd.none )

        SubmitProjectName ->
            case model.projectName of
                Unfilled ->
                    ( model, Cmd.none )

                Temp string ->
                    if string == "" then
                        ( model, Cmd.none )

                    else
                        ( { model | projectName = Confiremed string }
                        , Cmd.none
                        )

                Confiremed string ->
                    ( model, Cmd.none )

        CloseColorSelectModal ->
            ( { model | isColorSelectModalOpen = False }, Cmd.none )

        OpenColorSelectModal maybeId maybeColor ->
            ( { model
                | isColorSelectModalOpen = True
                , wipCategoryColor = maybeColor
                , wipCategoryId = maybeId
              }
            , Cmd.none
            )

        UpdateCategoryName name ->
            ( { model | wipCategoryName = name }, Cmd.none )

        UpdateCategoryColor maybeId color ->
            case maybeId of
                Just uuid ->
                    ( model, Cmd.none )

                Nothing ->
                    ( { model | wipCategoryColor = Just color }, Cmd.none )

        DeleteAnnotationCategory uuid ->
            let
                isSelectedCategory c =
                    if c.uuid == uuid then
                        True

                    else
                        False

                getC2Delete =
                    List.head <|
                        List.filter isSelectedCategory model.categories
            in
            case getC2Delete of
                Just category ->
                    ( { model
                        | categories =
                            List.filter
                                (not << isSelectedCategory)
                                model.categories
                        , wipAvailableColors =
                            category.color :: model.wipAvailableColors
                      }
                    , Random.generate UpdateProjectId Uuid.uuidGenerator
                    )

                Nothing ->
                    ( model, Cmd.none )

        AddAnnotationCategory name color id ->
            let
                category =
                    AnnotationCategory name id color
            in
            ( { model
                | categories = category :: model.categories
                , projectId = Nothing
              }
            , Random.generate UpdateProjectId Uuid.uuidGenerator
            )

        DownloadConfig ->
            case model.projectId of
                Just uuidUuid ->
                    case model.projectName of
                        Confiremed pName ->
                            let
                                jsonString =
                                    Json.Encode.encode 0 <|
                                        encodeCategories2Json
                                            pName
                                            uuidUuid
                                            model.categories

                                downloadCmd =
                                    File.Download.string
                                        "config.json"
                                        "application/json"
                                        jsonString
                            in
                            ( model, downloadCmd )

                        _ ->
                            ( model, Cmd.none )

                Nothing ->
                    ( model, Cmd.none )

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

                m =
                    AddAnnotationCategory name color
            in
            ( { model
                | wipCategoryName = ""
                , wipCategoryColor = List.head availableColors
                , wipAvailableColors = availableColors
                , isColorSelectModalOpen = False
              }
            , Random.generate m Uuid.uuidGenerator
            )



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

        applyFontStyle =
            Html.node "link"
                [ Html.Attributes.rel "stylesheet"
                , Html.Attributes.href fontAwesomeLink
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
                    [ a [ class "navbar-item" ]
                        [ text "Project Configuration Tool" ]
                    ]
                ]

        page ls =
            div []
                [ applyStyle
                , applyFontStyle
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
                downloadable =
                    if List.length model.categories > 1 then
                        True

                    else
                        False

                pNameAndCategoryField =
                    [ div [ class "tile is-parent is-12" ]
                        [ div [ class "tile is-child box" ]
                            [ h2 [] [ text (configureProjNameTxt ++ pName) ]
                            , addCategoryField
                                model.wipCategoryName
                                model.wipCategoryColor
                            , downloadConfigButton downloadable
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
                            ++ [ colorSelectModal model.wipCategoryId
                                    model.wipCategoryName
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


colorSelectModal : Maybe Uuid.Uuid -> String -> List Color -> Maybe Color -> Html Msg
colorSelectModal maybeId categoryName availableColors selectedColor =
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
                ([ class "button", onClick (UpdateCategoryColor maybeId c) ]
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
                            , onClick (OpenColorSelectModal Nothing maybeColor)
                            ]
                            [ text <| "Color: " ++ color.name ]

                    Nothing ->
                        a
                            [ class "button"
                            , onClick
                                (OpenColorSelectModal Nothing maybeColor)
                            ]
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
                    , th [] []
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
                    , th [] []
                    ]
                ]

        colorButton cat =
            a
                [ class "button is-small"
                , style "background-color" (color2string cat.color)
                , style "color" "white"
                , onClick
                    (OpenColorSelectModal (Just cat.uuid) (Just cat.color))
                ]
                [ text <| "Color: " ++ cat.color.name ]

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
                        , onClick (DeleteAnnotationCategory category.uuid)
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


downloadConfigButton : Bool -> Html Msg
downloadConfigButton downloadable =
    let
        buttonAttr =
            if downloadable then
                [ class "button is-fullwidth is-success"
                , onClick DownloadConfig
                ]

            else
                [ class "button is-fullwidth is-static" ]
    in
    div []
        [ a
            buttonAttr
            [ text "Download config" ]
        ]


main =
    Browser.element
        { init = init
        , update = update
        , view = view
        , subscriptions = subscriptions
        }
