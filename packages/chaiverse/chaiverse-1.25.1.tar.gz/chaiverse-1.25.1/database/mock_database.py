from collections import defaultdict
from functools import reduce, partial
from operator import getitem
from typing import Optional

from flatten_dict import unflatten

from chaiverse.lib.dict_tools import deep_get
from chaiverse.database import firebase_database as firebase_db


class MockDatabase():
    def __init__(self):
        nested_dict = lambda: defaultdict(nested_dict)
        self.store = nested_dict()

    def get(self, path: str, shallow=False):
        keys = self._get_keys(path)
        record = self._get_from_store(keys) or {}
        if shallow:
            record = {key: True for key, _ in record.items()}
        record = None if record in [{}, []] else record
        return record

    def is_in_database(self, path: str):
        keys = self._get_keys(path)
        is_in = self._is_in_store(keys)
        record = None
        if is_in:
            record = self.get(path)
        return record is not None

    def set(self, path: str, value: dict):
        keys = self._get_keys(path)
        value = firebase_db.serialise_input(value)
        value = dict_to_default_dict(value)
        self._set_in_store(keys, value)

    def update(self, path: str, record: dict):
        keys = self._get_keys(path)
        record = firebase_db.serialise_input(record)
        record = dict_to_default_dict(record)
        for record_keys, value in record.items():
            self._update_in_store(keys + record_keys.split('/'), value)

    def multi_update(self, path: str, record: dict):
        record = unflatten(record, splitter="path")
        self.update(path, record)

    def where(self, path, **kwargs):
        keys = self._get_keys(path)
        records = self._get_from_store(keys) or {}
        records = list(records.values())
        records = firebase_db.filter_records(records, kwargs)
        return records

    def _remove_recursively(self, keys, current_node, current_index):
        key = keys[current_index]
        if key in current_node:
            if current_index == len(keys) - 1:
                current_node.pop(key)
            else:
                self._remove_recursively(keys, current_node[key], current_index + 1)
                if len(current_node[key]) == 0:
                    current_node.pop(key)

    def remove(self, path: str):
        keys = self._get_keys(path)
        self._remove_recursively(keys, self.store, 0)

    def query_by_key_range(self, path, start_at=None, end_at=None, limit_to_first: Optional[int] = None, limit_to_last: Optional[int] = None):
        if limit_to_first and limit_to_last:
            raise ValueError('Cannot set both first and last limits.')
        keys = self._get_keys(path)
        records = self._get_from_store(keys) or {}
        record_tuples = list(records.items())
        key_func = lambda tuple: tuple[0]
        record_tuples = self._range_query_modifier(record_tuples, start_at, end_at, limit_to_first, limit_to_last, key_func=key_func)
        records = {key: value for key, value in record_tuples} or None
        return records

    def query_by_child_value_range(self, path, by, start_at=None, end_at=None, limit_to_first: Optional[int] = None, limit_to_last: Optional[int] = None):
        if limit_to_first and limit_to_last:
            raise ValueError('Cannot set both first and last limits.')
        keys = self._get_keys(path)
        records = self._get_from_store(keys) or {}
        record_tuples = list(records.items())
        key_func = lambda tuple: deep_get(tuple[1], by)
        record_tuples = self._range_query_modifier(record_tuples, start_at, end_at, limit_to_first, limit_to_last, key_func=key_func)
        records = {key: value for key, value in record_tuples} or None
        return records

    def _range_query_modifier(self, record_tuples, start_at, end_at, limit_to_first, limit_to_last, key_func):
        record_tuples = sorted(record_tuples, key=key_func)
        record_tuples = [
            record_tuple for record_tuple in record_tuples
            if (not start_at or key_func(record_tuple) >= start_at) and (not end_at or key_func(record_tuple) <= end_at)
        ]
        if limit_to_first:
            record_tuples = record_tuples[:limit_to_first]
        if limit_to_last:
            record_tuples = record_tuples[-limit_to_last:]
        return record_tuples

    def atomic_add(self, path: str, value: float):
        func = partial(firebase_db.add, y=value)
        self.atomic_set(path, func)

    def atomic_increment(self, path: str):
        self.atomic_set(path, firebase_db.incrementer)

    def atomic_decrement(self, path: str):
        self.atomic_set(path, firebase_db.decrementer)

    def atomic_set(self, path, operation: callable):
        value = self.get(path)
        value = operation(value)
        self.set(path, value)

    @staticmethod
    def _get_keys(path: str):
        path = path.lstrip("/")
        path = path.rstrip("/")
        keys = path.split("/")
        # To avoid using emptystring as key when
        # interfacing with root leaf
        keys = keys if keys != [""] else []
        return keys

    def _get_from_store(self, keys):
        node = self.store
        for key in keys:
            if key not in node:
                node = None
                break
            node = node[key]
        return node

    def _is_in_store(self, keys):
        node = self.store
        is_in = True
        for key in keys:
            if key not in node:
                is_in = False
                break
            node = node[key]
        return is_in

    def _get_or_create_from_store(self, keys):
        return reduce(getitem, keys, self.store) if keys else self.store

    def _set_in_store(self, keys, value):
        _raise_for_disallowed_key(keys)
        _raise_for_disallowed_key(value)
        value = _deep_remove_none(value) if isinstance(value, dict) else value
        if keys:
            self._get_or_create_from_store(keys[:-1])[keys[-1]] = value
        else:
            self.store = value

    def _update_in_store(self, keys, value):
        current_value = self._get_or_create_from_store(keys[:-1]) or {}
        current_value = current_value.get(keys[-1])
        # Updating is only relevant if both stored value and new value are
        # dicts
        if isinstance(current_value, dict) and isinstance(value, dict):
            value = deep_update(current_value, value)
        self._set_in_store(keys, value)

    @property
    def nested_default_dict(self):
        # To make it easy to do self.store["some"]["key"] without raising
        # KeyError
        return defaultdict(self.nested_default_dict)


def _get_disallowed_firebase_keys():
    return [".", "$", "#", "[", "]", "/"]


def _raise_for_disallowed_key(obj):
    disallowed_keys = _get_disallowed_firebase_keys()
    if isinstance(obj, str):
        msg = f"Key {obj} contains disallowed character!"
        assert not any(disallowed in obj for disallowed in disallowed_keys), msg
    elif isinstance(obj, list):
        [_raise_for_disallowed_key(key) for key in obj]
    elif isinstance(obj, dict):
        [_raise_for_disallowed_key(key) for key in obj.keys()]
        [
            _raise_for_disallowed_key(value) for value in obj.values()
            if isinstance(value, dict)
        ]


def _string_is_disallowed(string):
    disallowed_keys = _get_disallowed_firebase_keys()
    return any(disallowed in string for disallowed in disallowed_keys)


def dict_to_default_dict(d):
    if isinstance(d, dict):
        nested_dict = lambda: defaultdict(nested_dict)
        d = defaultdict(nested_dict, {k: dict_to_default_dict(v) for k, v in d.items()})
    return d


def deep_update(mapping, updating_mapping, traverse_dict=True):
    mapping = mapping.copy()
    mapping = _deep_update(mapping, updating_mapping, traverse_dict=traverse_dict) if len(updating_mapping) else {}
    return mapping


def _deep_update(mapping, updating_mapping, traverse_dict=True):
    for k, v in updating_mapping.items():
        if k in mapping and isinstance(mapping[k], dict) and isinstance(v, dict) and traverse_dict:
            # Firebase does not support updating deeply nested dicts, so we
            # ensure that if we go any deeper, we are not updating by setting
            # traverse_dict = False
            mapping[k] = deep_update(mapping[k], v, traverse_dict=False)
        else:
            mapping[k] = v
    return mapping


def _deep_remove_none(mapping):
    for key, value in mapping.items():
        value = _deep_remove_none(value) if isinstance(value, dict) else value
    # We must do it this way to preserve the infinite dict structure of the
    # mapping
    none_keys = [key for key, value in mapping.items() if value == None]
    for key in none_keys:
        mapping.pop(key)
    return mapping
