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
from lru import LRU as LruDict

from pathilico.app.header import Api


class ResourceModel(object):
    def __init__(self):
        self.num_max_images = 300
        self.images = LruDict(self.num_max_images)
        self.requesting = set()
        self.queries = dict()


def add_reservation(resource_model, object_id, query, update=True):
    """Register image's object_id and its query for the creation on async funcs

    Note that query must have `__eq__` method

    :param ResourceModel resource_model:
    :param int|byte object_id:
    :param query:
    :param bool update:
    :return ResourceModel:
    """
    if update and object_id in resource_model.queries:
        return update_reservation(resource_model, object_id, query)
    resource_model.queries[object_id] = query
    return resource_model


def update_reservation(resource_model, object_id, query):
    old_query = resource_model.queries[object_id]
    if old_query == query:
        return resource_model
    resource_model.requesting = resource_model.requesting - {object_id}
    if object_id in resource_model.images:
        del resource_model.images[object_id]
    resource_model.queries[object_id] = query
    return resource_model


def add_image(resource_model, object_id, query, image):
    """Add the image which is the result of async func

    :param ResourceModel resource_model:
    :param int|byte object_id:
    :param query:
    :param image:
    :return ResourceModel:
    """
    if object_id not in resource_model.requesting:
        return resource_model
    current_query = resource_model.queries[object_id]
    if not current_query == query:
        return resource_model
    resource_model.requesting = resource_model.requesting - {object_id}
    resource_model.images[object_id] = image
    return resource_model


def has_image(resource_model, object_id):
    flag = object_id in resource_model.images
    return flag


def get_stored_images(resource_model, object_ids):
    """Collect images corresponding to given object_ids

    :param ResourceModel resource_model:
    :param object_ids:
    :return object_ids, images:
    """
    object_ids = [i for i in object_ids if has_image(resource_model, i)]
    images = [resource_model.images[i] for i in object_ids]
    return object_ids, images


def delete(resource_model, object_id):
    """Delete query, image from model

    :param ResourceModel resource_model:
    :param object_ids:
    :return ResourceModel:
    """
    if object_id in resource_model.images:
        del resource_model.images[object_id]
    resource_model.queries.pop(object_id, None)
    resource_model.requesting = resource_model.requesting - {object_id}
    return resource_model


def request_queries(resource_model, object_ids):
    """Collect queries corresponding to given object_ids

    :param ResourceModel resource_model:
    :param object_ids:
    :return ResourceModel, List[int|byte], queries:
    """
    object_ids = [
        i for i in object_ids
        if (
                i in resource_model.queries
                and i not in resource_model.requesting
                and i not in resource_model.images
        )
    ]
    queries = [resource_model.queries[i] for i in object_ids]
    resource_model.requesting = resource_model.requesting | set(object_ids)
    return resource_model, object_ids, queries


# Actual implementations for Api
def reserve_image_query(model, object_id, query):
    model.resource = add_reservation(model.resource, object_id, query)
    return model


def _add_image(model, object_id, query, image):
    model.resource = add_image(model.resource, object_id, query, image)
    return model


def collect_queries_for_request(model, object_ids):
    model.resource, object_ids, queries = request_queries(
        model.resource, object_ids
    )
    return model, object_ids, queries


def delete_image(model, object_id):
    model.resource = delete(model.resource, object_id)
    return model


def get_images(model, object_ids):
    obj_ids, imgs = get_stored_images(model.resource, object_ids)
    return obj_ids, imgs


Api.register(ResourceModel)
Api.register(reserve_image_query)
Api.register_as(_add_image, "add_image")
Api.register(collect_queries_for_request)
Api.register(delete_image)
Api.register(get_images)


