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
import pathilico.pygletelm.window as window_api
from pathilico.app.message import Msg
from pathilico.app.views.common import AppLayers
from pathilico.app.header import Api


DEL_DRAG_COLOR = (30, 30, 30, 160)


def annotation_view(model):
    if Api.is_annotation_mode(model, "pan"):
        return window_api.View(annotation_graphic(model))
    else:
        vs = [
            annotation_graphic(model),
            annotation_event(model),
        ]
        return window_api.View(*vs)


def annotation_graphic(model):
    image_data, point_data, area_data = \
        Api.get_annotation_info_and_grouped_images_for_display(model)
    vs = list()
    for x, y, img in image_data:
        i = window_api.simple_image(
            x=x, y=y, image=img, layer=AppLayers.AnnotationGroupedImage
        )
        vs.append(i)
    for x, y, color in point_data:
        # color = (0, 255, 0, 180)
        vs.append(point_annotation(x, y, color))
    for contour, tri_indices, color in area_data:
        # color = (0, 255, 0, 180)
        p = window_api.polygon(
            points=contour, color=color, dim=1, triangulate=False,
            layer=AppLayers.AnnotationPolygon, index=tri_indices
        )
        vs.append(p)
    vs.append(delete_drag_area_graphic(model))
    vs.append(drawing_line_graphic(model))
    return window_api.View(*vs)


def drawing_line_graphic(model):
    _, color, _ = \
        Api.get_selected_annotation_category_id_color_and_name(model)
    color = color[:3] + (255, )
    if not Api.is_line_drawing(model):
        return window_api.View()
    points = Api.get_drawing_line_coordinates(model)
    curve = window_api.curve(
        layer=AppLayers.AnnotationTmpLine, color=color, dim=1,
        points=points
    )
    return window_api.View(curve)


def delete_drag_area_graphic(model):
    if Api.is_delete_dragging(model):
        left, bottom, right, top = Api.get_delete_drag_bound(model)
        box = window_api.simple_box(
            x=left, y=bottom, width=right-left, height=top-bottom,
            color=DEL_DRAG_COLOR, layer=AppLayers.DeleteBox
        )
        return window_api.View(box)
    else:
        return window_api.View()


def annotation_event(model):
    category_id, _, _ = \
        Api.get_selected_annotation_category_id_color_and_name(model)
    if Api.is_annotation_mode(model, "point"):
        click_to_add_point = window_api.mouse_press_area(
            0, 0, 10000, 10000, message=Msg.AddPoint,
            msg_kwargs=dict(category_id=category_id),
            priority=AppLayers.AnnotationPoint
        )
        return window_api.View(click_to_add_point)
    elif Api.is_annotation_mode(model, "area"):
        drag_area = window_api.mouse_drag_area(
            0, 0, 10000, 10000, priority=100,
            message=Msg.DrawLineDragAt, drag_start_msg=Msg.DrawLineDragStartAt,
            drag_end_msg=Msg.DrawLineDragEndAt
        )
        return window_api.View(drag_area)
    else:
        drag_area = window_api.mouse_drag_area(
            0, 0, 10000, 10000, priority=100,
            message=Msg.DeleteDragAt, drag_start_msg=Msg.DeleteDragStartAt,
            drag_end_msg=Msg.DeleteDragEndAt
        )
        return window_api.View(drag_area)


# Helper APIs
def point_annotation(x, y, color):
    r = 2
    w = 8
    h = window_api.simple_box(
        x=x-w, y=y-r, width=2*w, height=2*r, color=color,
        layer=AppLayers.AnnotationPoint
    )
    v = window_api.simple_box(
        x=x-r, y=y-w, width=2*r, height=2*w, color=color,
        layer=AppLayers.AnnotationPoint
    )
    return window_api.View(h, v)




