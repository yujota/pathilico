module Colors exposing (Color, materialColors)


type alias Color =
    { r : Int, g : Int, b : Int, a : Int }


materialColors =
    [ ( "Orange", Color 250 104 0 255 )
    , ( "Amber", Color 240 163 10 255 )
    , ( "Yellow", Color 227 200 0 255 )
    , ( "Brown", Color 130 90 44 255 )
    , ( "Olive", Color 109 135 100 255 )
    , ( "Steel", Color 100 118 135 255 )
    , ( "Mauve", Color 118 96 138 255 )
    , ( "Sienna", Color 160 82 45 255 )
    , ( "Lime", Color 164 196 0 255 )
    , ( "Green", Color 96 169 23 255 )
    , ( "Emerald", Color 0 138 0 255 )
    , ( "Teal", Color 0 171 169 255 )
    , ( "Cyan", Color 27 161 226 255 )
    , ( "Cobalt", Color 0 80 239 255 )
    , ( "Indigo", Color 106 0 255 255 )
    , ( "Violet", Color 170 0 255 255 )
    , ( "Pink", Color 244 114 208 255 )
    , ( "Magenta", Color 216 0 115 255 )
    , ( "Crimson", Color 162 0 37 255 )
    , ( "Red", Color 229 20 0 255 )
    ]
