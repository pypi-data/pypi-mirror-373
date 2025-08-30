from __future__ import annotations

import abc
from collections.abc import Callable
from functools import wraps
import re
from typing import ClassVar

import dearpygui.dearpygui as dpg  # type: ignore
from dpgmagictag.magictag import MagicTag  # type: ignore

from dpgcontainers.exceptions import NamedChildNotFound
from dpgcontainers.exceptions import UnrenderedException


CONFIGURE_ITEM_KEYS = (
    'callback', 'drag_callback', 'drop_callback', 'enabled', 'filter_key',
    'height', 'indent', 'label', 'payload_type', 'show', 'source',
    'track_offset', 'tracked', 'use_internal_label', 'user_data', 'width',
)


def is_rendered(instance: 'DPGContainersBase'):
    return hasattr(instance, 'id_')

def assert_rendered(method) -> Callable:
    @wraps(method)
    def _inner(*args, **kwargs):
        if not is_rendered(args[0]):
            raise UnrenderedException()
        return method(*args, **kwargs)
    return _inner


class DPGContainersBase(abc.ABC):
    dpg_function_name: ClassVar[str]
    dpg_arguments: ClassVar[tuple[str, ...]]
    dpg_function_cache: ClassVar[Callable | None] = None
    dpg_value_cast: ClassVar[type | None] = None
    rendered_by_id: ClassVar[dict[int, 'DPGContainersBase']] = dict()

    @property
    def dpg_function(self):
        if self.dpg_function_cache is None:
            self.dpg_function_cache = getattr(dpg, self.dpg_function_name)
        return self.dpg_function_cache

    @property
    def children(self) -> list['DPGContainersBase']:
        if not hasattr(self, '_children'):
            self._children: list['DPGContainersBase'] = []
        return list(self._children)

    @children.setter
    def children(self, value: list['DPGContainersBase']):
        self._children = value

    @property
    def parent(self) -> 'DPGContainersBase'|None:
        if not hasattr(self, '_parent'):
            self._parent: 'DPGContainersBase'|None = None
        return self._parent

    @parent.setter
    def parent(self, value: 'DPGContainersBase'):
        self._parent = value

    @property
    def tagged_entities(self) -> dict[str, 'DPGContainersBase']:
        if not hasattr(self, '_tagged_entities'):
            self._tagged_entities: dict[str, 'DPGContainersBase'] = {}
            if hasattr(self, 'tag') and self.tag:
                self._tagged_entities[self.tag] = self
        return self._tagged_entities

    @property
    def named_child_indexes(self) -> dict[str, int]:
        if not hasattr(self, '_named_child_indexes'):
            self._named_child_indexes: dict[str, int] = {}
        return self._named_child_indexes

    def query_all(self, name: str) -> list['DPGContainersBase']:
        found = []
        if name in self.named_child_indexes:
            index = self.named_child_indexes[name]
            found.append(self.children[index])
        for child in self.children:
            try:
                named = child.query_all(name)
            except NamedChildNotFound:
                pass
            else:
                found.extend(named)
        if found:
            return found
        raise NamedChildNotFound(name)

    def query(self, name: str) -> 'DPGContainersBase':
        if name in self.named_child_indexes:
            index = self.named_child_indexes[name]
            return self.children[index]
        for child in self.children:
            try:
                named = child.query(name)
            except NamedChildNotFound:
                pass
            else:
                return named
        raise NamedChildNotFound(name)

    def query_search(self, pattern: str) -> 'DPGContainersBase':
        matcher = re.compile(pattern)
        for name in self.named_child_indexes:
            if matcher.search(name):
                index = self.named_child_indexes[name]
                return self.children[index]
        for child in self.children:
            try:
                found = child.query_search(pattern)
            except NamedChildNotFound:
                pass
            else:
                return found
        raise NamedChildNotFound(pattern)

    def query_search_all(self, pattern: str) -> list['DPGContainersBase']:
        results = []
        matcher = re.compile(pattern)
        for name in self.named_child_indexes:
            if matcher.search(name):
                index = self.named_child_indexes[name]
                results.append(self.children[index])
        for child in self.children:
            try:
                found = child.query(name)
            except NamedChildNotFound:
                pass
            else:
                results.append(found)
        if results:
            return results
        raise NamedChildNotFound(name)

    def search_named_children(self, name: str) -> 'DPGContainersBase':
        '''Deprecated'''
        return self.query(name)


    def __call__(self, *children: 'DPGContainersBase', **named_children: 'DPGContainersBase'):
        for child in children:
            self.add_child(child)

        for name, child in named_children.items():
            self.add_child(child, name=name)

        return self

    def render(self, parent: int|str|'DPGContainersBase'|None = None, tag_prefix: MagicTag | None = None):
        if not hasattr(self, 'id_'):
            dpg_kwargs = {
                arg: getattr(self, arg)
                for arg in self.dpg_arguments
            }
            if parent is None:
                parent = self.parent
            if parent is not None:
                if isinstance(parent, DPGContainersBase):
                    parent_id: int|str = parent.id_
                else:
                    parent_id = parent
                    # parent = self.rendered_by_id[parent]
                # self.parent = parent
                dpg_kwargs['parent'] = parent_id
            if tag_prefix is not None:
                if dpg_kwargs['tag'] != 0:
                    dpg_kwargs['tag'] = tag_prefix / dpg_kwargs['tag']
            id_ = self.dpg_function(**dpg_kwargs)
            self.id_: int = id_
            self.rendered_by_id[id_] = self

        for child in self.children:
            child.render(tag_prefix=tag_prefix)

        return self

    def remove_child(self, child: 'DPGContainersBase'):
        if child not in self.children:
            raise ValueError(f'{child} not in self.children')

        child_index = self._children.index(child)
        for name, index in list(self.named_child_indexes.items()):
            if child_index == index:
                del self.named_child_indexes[name]
            elif index > child_index:
                self.named_child_indexes[name] -= 1

        del self._children[child_index]

    def add_child(
        self,
        child: 'DPGContainersBase',
        prepend: bool=False,
        before: 'DPGContainersBase'|None = None,
        name: str|None = None
    ) -> 'DPGContainersBase':
        children = self.children
        index = len(children)
        if prepend:
            assert before is None, 'Prepend and before are mutually exclusive'
            index = 0
        elif before is not None:
            index = children.index(before)

        children.insert(index, child)
        for named_name, named_index in list(self.named_child_indexes.items()):
            if named_index >= index:
                self.named_child_indexes[named_name] += 1
        if name:
            self.named_child_indexes[name] = index

        self.children = children
        child.parent = self
        return self

    def move(
            self,
            parent: 'DPGContainersBase',
            prepend: bool = False,
            before: 'DPGContainersBase'|None = None,
    ):
        # assert is_rendered(parent), 'Parent must be rendered'
        if self.parent is not None:
            self.parent.remove_child(self)

        parent.add_child(self, prepend=prepend, before=before)
        if prepend:
            assert before is None, 'prepend and before are mutually exclusive'
            children = dpg.get_item_children(parent.id_, 1)
            if children:
                before = self.rendered_by_id[children[0]]

        if is_rendered(self):
            if before is not None:
                dpg.move_item(self.id_, parent=parent.id_, before=before.id_)
            else:
                dpg.move_item(self.id_, parent=parent.id_)


    @assert_rendered
    def delete(self):
        if self.parent is not None:
            self.parent.remove_child(self)
        dpg.delete_item(self.id_)
        del self.rendered_by_id[self.id_]
        del self.id_

    @assert_rendered
    def clear(self):
        for child in self.children:
            child.delete()

    @property
    @assert_rendered
    def configuration(self):
        return dpg.get_item_configuration(self.id_)

    @property
    def value(self):
        return dpg.get_value(self.id_)

    @value.setter
    def value(self, value):
        if self.dpg_value_cast is not None:
            value = self.dpg_value_cast(value)
        dpg.set_value(self.id_, value)

    @assert_rendered
    def set_value(self, value):
        self.value = value

    @assert_rendered
    def configure(self, **kwargs):
        dpg.configure_item(self.id_, **kwargs)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if is_rendered(self):
            if key in CONFIGURE_ITEM_KEYS:
                kwargs = {key: value}
                dpg.configure_item(self.id_, **kwargs)

    @assert_rendered
    def __enter__(self):
        dpg.push_container_stack(self.id_)

    def __exit__(self, exc_type, exc_value, traceback):
        dpg.pop_container_stack()
