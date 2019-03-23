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
import pyglet

import pathilico.pygletelm.window as window_api


def functional_test_draw_primitive_atomic_drawing():
    window = pyglet.window.Window()
    batch = pyglet.graphics.Batch()

    box = window_api.PrimitiveBox(100, 100, 70, 70)
    box.draw(batch)

    circle = window_api.PrimitiveCircle(200, 200, 45)
    circle.draw(batch)

    line_1 = window_api.PrimitiveLine(300, 300, 350, 350)
    line_1.draw(batch)

    line_2 = window_api.PrimitiveLine(300, 200, 350, 250)
    line_2.draw(batch)

    text = window_api.PrimitiveTextLabel(300, 100, "Hello world")
    text.draw(batch)

    @window.event
    def on_draw():
        window.clear()
        batch.draw()
    pyglet.app.run()


def functional_test_graphic_handler():
    window = pyglet.window.Window()
    batch = pyglet.graphics.Batch()
    gh = window_api.GraphicManager(batch)

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    rs = [25]

    def enlarge_circle(*args):
        rs[0] += 1
        r = rs[0]
        gh.update_drawings([window_api.PrimitiveCircle(200, 200, r)])

    pyglet.clock.schedule_interval(enlarge_circle, 0.1)
    pyglet.app.run()


if __name__ == "__main__":
    functional_test_graphic_handler()
    functional_test_draw_primitive_atomic_drawing()
