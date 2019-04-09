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


module Color exposing (Color, materialColors, toRgbString)


type alias Color =
    { r : Int, g : Int, b : Int, name : String }


toRgbString : Color -> String
toRgbString color =
    "rgb("
        ++ String.fromInt color.r
        ++ ","
        ++ String.fromInt color.g
        ++ ","
        ++ String.fromInt color.b
        ++ ")"


defaultColor =
    Color 250 104 0 "Orange"


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
