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
"""This module is acting like a handler for virtual DOM
"""


class PayloadTypeBase(object):
    _num_id = 100000
    _id = 0

    def __init__(self):
        self.unused_ids = set(range(self._id, self._id+self._num_id))

    def alloc_id(self):
        return self.unused_ids.pop()

    def release_id(self, identity):
        self.unused_ids.add(identity)

    @classmethod
    def diff(cls, old_payloads, new_payloads):
        return list(), dict(), list()


class TheOne(PayloadTypeBase):
    _id = 100000

    @classmethod
    def diff(cls, old_payloads, new_payloads):
        if len(old_payloads) == 0 and len(new_payloads) == 0:
            return list(), dict(), list()
        elif len(old_payloads) == 0 and len(new_payloads) == 1:
            n = new_payloads[0]
            return [n.get_identity()], dict(), list()
        elif len(old_payloads) == 1 and len(new_payloads) == 0:
            o = old_payloads[0]
            return list(), dict(), [o.get_identity()]
        elif len(old_payloads) == 1 and len(new_payloads) == 1:
            n = new_payloads[0]
            o = old_payloads[0]
            if n == o:
                return list(), dict(), list()
            else:
                return [n.get_identity()], dict(), [o.get_identity()]
        else:
            n = new_payloads[-1]
            r = (
                [n.get_identity()], dict(),
                [o.get_identity() for o in old_payloads]
            )
            return r


class UniqueByClass(PayloadTypeBase):
    _id = 200000

    @classmethod
    def diff(cls, old_payloads, new_payloads):
        r_news, r_updates, r_deletes = list(), dict(), list()
        for olds, news in cls.divided_by_categories(old_payloads, new_payloads):
            ns, us, ds = cls.diff_by_categories(olds, news)
            r_news.extend(ns)
            r_updates.update(us)
            r_deletes.extend(ds)
        return r_news, r_updates, r_deletes

    @classmethod
    def divided_by_categories(cls, old_payloads, new_payloads):
        c_keys = set()
        for p in old_payloads+new_payloads:
            c_keys.add(p.actual_cls)
        c_dict = dict()
        for k in c_keys:
            c_dict[k] = (list(), list())
        for o in old_payloads:
            k = o.actual_cls
            c_dict[k][0].append(o)
        for n in new_payloads:
            k = n.actual_cls
            c_dict[k][1].append(n)
        return list(c_dict.values())

    @classmethod
    def diff_by_categories(cls, old_payloads, new_payloads):
        return TheOne.diff(old_payloads, new_payloads)


class UniqueByClassWithReplaceablePayload(PayloadTypeBase):
    _id = 300000

    @classmethod
    def diff(cls, old_payloads, new_payloads):
        r_news, r_updates, r_deletes = list(), dict(), list()
        for olds, news in UniqueByClass.divided_by_categories(
                old_payloads, new_payloads
        ):
            ns, us, ds = UniqueByClass.diff_by_categories(olds, news)
            n_tags = [n_t for n_t in new_payloads if n_t.get_identity() in ns]
            d_tags = [d_t for d_t in old_payloads if d_t.get_identity() in ds]
            ns, us, ds = cls.find_update_tags_then_change(n_tags, us, d_tags)
            r_news.extend(ns)
            r_updates.update(us)
            r_deletes.extend(ds)
        return r_news, r_updates, r_deletes

    @classmethod
    def find_update_tags_then_change(cls, new_tags, update_tags, delete_tags):
        l_n, l_d = len(new_tags), len(delete_tags)
        if not (l_n >= 1 and l_d >= 1):
            ns = [n_t.get_identity() for n_t in new_tags]
            ds = [d_t.get_identity() for d_t in delete_tags]
            return ns, update_tags, ds
        ups = dict()
        ignore_new_tags = list()
        for n_tag in new_tags:
            flag, ds, target, up_kwargs = cls.get_similar_tag(
                n_tag, delete_tags
            )
            if flag:
                delete_tags = ds
                ups[target.get_identity()] = up_kwargs
                ignore_new_tags.append(n_tag)
        new_tags = [t for t in new_tags if t not in ignore_new_tags]
        ns = [n_t.get_identity() for n_t in new_tags]
        ds = [d_t.get_identity() for d_t in delete_tags]
        return ns, ups, ds

    @classmethod
    def get_similar_tag(cls, tag, target_tags):
        """flag, new_target_tags, target_tag, update_kwargs"""
        for i, target in enumerate(target_tags):
            go_next = False
            for a in tag.not_replaceable_attrs:
                if not getattr(tag.actual, a) == getattr(target.actual, a):
                    go_next = True
                    break
            if go_next:
                continue
            update_kwargs = dict()
            for k in tag.replaceable_attrs:
                new_v = getattr(tag.actual, k)
                if not new_v == getattr(target.actual, k):
                    update_kwargs[k] = new_v
            r = (
                True, target_tags[:i]+target_tags[i+1:],
                target, update_kwargs
            )
            return r
        return False, target_tags, None, dict()


class UniqueByClassAndPayload(PayloadTypeBase):
    _id = 400000

    @classmethod
    def diff(cls, old_payloads, new_payloads):
        r_news, r_updates, r_deletes = list(), dict(), list()
        for olds, news in cls.divided_by_categories(old_payloads, new_payloads):
            ns, us, ds = cls.diff_by_categories(olds, news)
            r_news.extend(ns)
            r_updates.update(us)
            r_deletes.extend(ds)
        return r_news, r_updates, r_deletes

    @classmethod
    def get_category(cls, payload):
        return payload.actual_cls, payload.get_values()

    @classmethod
    def divided_by_categories(cls, old_payloads, new_payloads):
        c_keys = set()
        for p in old_payloads+new_payloads:
            c_keys.add(cls.get_category(p))
        c_dict = dict()
        for k in c_keys:
            c_dict[k] = (list(), list())
        for o in old_payloads:
            k = cls.get_category(o)
            c_dict[k][0].append(o)
        for n in new_payloads:
            k = cls.get_category(n)
            c_dict[k][1].append(n)
        return list(c_dict.values())

    @classmethod
    def diff_by_categories(cls, old_payloads, new_payloads):
        return TheOne.diff(old_payloads, new_payloads)


class UniqueByClassAndReplaceablePayload(PayloadTypeBase):
    _id = 500000

    @classmethod
    def diff(cls, old_payloads, new_payloads):
        """

        :param List[PayloadTag] old_payloads:
        :param new_payloads:
        :return:
        """
        r_news, r_updates = list(), dict()
        old_by_cats = dict()  # dict[key=<class, rep_val>, value=[old, new]]
        for p in old_payloads:
            key = (p.actual_cls, p.get_not_replaceable_values())
            if key not in old_by_cats:
                old_by_cats[key] = [p]
            else:
                old_by_cats[key].append(p)
        for new_p in new_payloads:
            key = (new_p.actual_cls, new_p.get_not_replaceable_values())
            if key not in old_by_cats:
                r_news.append(new_p.get_identity())
                continue
            olds = old_by_cats[key]
            if len(olds) == 0:
                r_news.append(new_p.get_identity())
                continue
            ind = -1
            for i, old_p in enumerate(olds):
                if new_p == old_p:
                    ind = i
            if ind >= 0:  # Case: same obj in old_payloads and new_payloads
                olds.pop(ind)
                continue
            old_p = olds.pop()
            ups = dict()
            attrs = old_p.replaceable_attrs
            new_vals = new_p.get_replaceable_values()
            old_vals = old_p.get_replaceable_values()
            for a, nv, ov in zip(attrs, new_vals, old_vals):
                if not nv == ov:
                    ups[a] = nv
            r_updates[old_p.get_identity()] = ups
        r_deletes = [
            p.get_identity() for oc in old_by_cats.values() for p in oc
        ]
        return r_news, r_updates, r_deletes


class PayloadTypes(object):
    the_one = TheOne()
    unique_by_class = UniqueByClass()
    unique_by_class_with_replaceable_payload = \
        UniqueByClassWithReplaceablePayload()
    unique_by_class_and_payload = UniqueByClassAndPayload()
    unique_by_class_and_replaceable_payload = \
        UniqueByClassAndReplaceablePayload()
    all = (
        the_one, unique_by_class, unique_by_class_with_replaceable_payload,
        unique_by_class_and_payload, unique_by_class_and_replaceable_payload
    )


class CachedObject(object):
    _payload_type = PayloadTypes.the_one
    _payload_attrs = tuple()
    _payload_replaceable_attrs = tuple()  # Optional

    def __init__(self):
        self.tag = PayloadTag(
            self, self._payload_attrs, self._payload_type,
            self._payload_replaceable_attrs
        )

    @property
    def identity(self):
        return self.tag.get_identity()

    def done(self):
        pass

    def __del__(self):
        self.done()


class PayloadTag(object):

    def __init__(
            self, obj, attrs=tuple(), payload_type=PayloadTypes.the_one,
            payload_replaceable_attrs=tuple()
    ):
        self.actual = obj
        self.actual_cls = obj.__class__
        self.attrs = attrs
        self.replaceable_attrs = payload_replaceable_attrs
        self.not_replaceable_attrs = tuple(
            [a for a in attrs if a not in payload_replaceable_attrs]
        )
        self.p_type = payload_type
        self.id = None
        self.wrap_acutal_done_func()

    def __del__(self):
        self.drop_identity()
        del self.actual

    def wrap_acutal_done_func(self):
        def wrap(f):
            def w(*args, **kwargs):
                self.drop_identity()
                return f(*args, **kwargs)
            return w
        self.actual.done = wrap(getattr(self.actual, "done", lambda: None))

    def get_values(self):
        return tuple([getattr(self.actual, a) for a in self.attrs])

    def get_not_replaceable_values(self):
        return tuple(
            [getattr(self.actual, a)
             for a in self.attrs if a in self.not_replaceable_attrs])

    def get_replaceable_values(self):
        return tuple(
            [getattr(self.actual, a)
             for a in self.attrs if a in self.replaceable_attrs])

    def get_identity(self):
        if self.id is None:
            self.id = self.p_type.alloc_id()
        return self.id

    def drop_identity(self):
        if self.id is not None:
            self.p_type.release_id(self.id)

    def __eq__(self, other):
        if not self.__class__ == other.__class__:
            return False
        if not self.attrs == other.attrs:
            return False
        for a in self.attrs:
            if not getattr(self.actual, a) == getattr(other.actual, a):
                return False
        return True


def diff(old_tags, new_tags):
    r_new, r_update, r_delete = list(), dict(), list()
    olds = dict()
    news = dict()
    for k in PayloadTypes.all:
        olds[k] = list()
        news[k] = list()
    for old in old_tags:
        k = old.p_type
        olds[k].append(old)
    for new in new_tags:
        k = new.p_type
        news[k].append(new)
    for k in PayloadTypes.all:
        n, u, d = k.diff(olds[k], news[k])
        r_new.extend(n)
        r_delete.extend(d)
        r_update.update(u)
    return r_new, r_update, r_delete
