#   Copyright
#     2019 Department of Dermatology, School of Medicine, Tohoku University
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


class MaterialDesignColorPalette(object):
    class Primary(object):
        Red = (244, 64, 64, 255)  # #f44336
        Pink = (233, 30, 99, 255)  # #e91e63
        Cyan = (0, 188, 212, 255)  # #00bcd4

    class Dark(object):
        Red = (186, 0, 13, 255)  # #ba000d
        Pink = (176, 0, 58, 255)  # #b0003a
        Cyan = (0, 139, 163, 255)  # #008ba3

    class Light(object):
        Red = (255, 121, 94, 255)  # #ff7961
        Pink = (255, 96, 144, 255)  # #ff6090
        Cyan = (98, 239, 255, 255)  # #62efff

    class Accent(object):
        Red = (255, 82, 82, 255)  # #ff5252
        Pink = (255, 64, 129, 255)  # #ff4081
        Cyan = (25, 255, 255, 255)  # #18ffff

    PrimaryText = (33, 33, 33, 255)  # #212121
    SecondaryText = (117, 117, 117, 255)  # #757575
    WhiteText = (255, 255, 255, 255)  # #FFFFFF
    DividerColor = (189, 189, 189, 255)  # #BDBDBD


Colors = MaterialDesignColorPalette
PrimaryText = (33, 33, 33, 255)  # #212121
SecondaryText = (117, 117, 117, 255)  # #757575
WhiteText = MaterialDesignColorPalette.WhiteText


class FlatUIColors(object):
    """https://www.materialui.co/flatuicolors"""
    rgb = lambda *args: args
    Turquoise = rgb(26,188,156)
    Emeraland = rgb(46,204,113)
    Peterriver = rgb(52,152,219)
    Amethyst = rgb(155,89,182)
    Wetasphalt = rgb(52,73,94)
    Greensea = rgb(22,160,133)
    Nephritis = rgb(39,174,96)
    Belizehole = rgb(41,128,185)
    Wisteria = rgb(142,68,173)
    Midnightblue = rgb(44,62,80)
    Sunflower = rgb(241,196,15)
    Carrot = rgb(230,126,34)
    Alizarin = rgb(231,76,60)
    Clouds = rgb(236,240,241)
    Concrete = rgb(149,165,166)
    Orange = rgb(243,156,18)
    Pumpkin = rgb(211,84,0)
    Pomegranate = rgb(192,57,43)
    Silver = rgb(189,195,199)
    Asbestos = rgb(127,140,141)


class MetroColors(object):
    """https://www.materialui.co/metrocolors"""
    rgb = lambda *args: (args[0], args[1], args[2], 255)
    Orange = rgb(250,104,0)
    Amber = rgb(240,163,10)
    Yellow = rgb(227,200,0)
    Brown = rgb(130,90,44)
    Olive = rgb(109,135,100)
    Steel = rgb(100,118,135)
    Mauve = rgb(118,96,138)
    Sienna = rgb(160,82,45)
    Lime = rgb(164,196,0)
    Green = rgb(96,169,23)
    Emerald = rgb(0,138,0)
    Teal = rgb(0,171,169)
    Cyan = rgb(27,161,226)
    Cobalt = rgb(0,80,239)
    Indigo = rgb(106,0,255)
    Violet = rgb(170,0,255)
    Pink = rgb(244,114,208)
    Magenta = rgb(216,0,115)
    Crimson = rgb(162,0,37)
    Red = rgb(229,20,0)
    all_names = [
        "Orange", "Amber", "Yellow", "Brown", "Olive", "Steel", "Mauve",
        "Sienna", "Lime", "Green", "Emerald", "Teal", "Cyan", "Cobalt",
        "Indigo", "Violet", "Pink", "Magenta", "Crimson", "Red"
    ]
    all = [
        Orange, Amber, Yellow, Brown, Olive, Steel, Mauve, Sienna, Lime, Green,
        Emerald, Teal, Cyan, Cobalt, Indigo, Violet, Pink, Magenta, Crimson, Red
    ]





def change_transparency(color, transparency=1.0):
    return color[0], color[1], color[2], int(255*transparency)


