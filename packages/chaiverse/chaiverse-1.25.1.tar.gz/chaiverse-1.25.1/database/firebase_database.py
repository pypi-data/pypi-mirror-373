import json
from typing import Optional

import firebase_admin
import firebase_admin.db
from flatten_dict import flatten

from chaiverse.database.inferno_database_adapter import _InfernoDatabaseAdapter


class _FirebaseDatabase(_InfernoDatabaseAdapter):
    def __init__(self, credentials_file: str, url: str):
        self.credentials_file = credentials_file
        self.url = url
        self._initialize_firebase()

    def reference(self, path: str):
        return firebase_admin.db.reference(path, app=self.app)

    def get(self, path: str, shallow: bool = False):
        firebase_reference = self.reference(path)
        record = firebase_reference.get(shallow=shallow)
        return record

    def set(self, path: str, value):
        firebase_reference = self.reference(path)
        value = serialise_input(value)
        firebase_reference.set(value)

    def update(self, path: str, record: dict):
        firebase_reference = self.reference(path)
        record = serialise_input(record)
        firebase_reference.update(record)

    def multi_update(self, path: str, record: dict):
        # While the logic for this function is the same as update, the intended
        # use-case is different due to the different syntax for multi-path
        # updates
        # See https://firebase.google.com/docs/database/admin/save-data#section-update
        record = flatten(record, reducer="path")
        self.update(path, record)

    def where(self, path, **kwargs):
        firebase_reference = self.reference(path)
        assert len(kwargs) > 0, "No query provided!"
        field_name, field_value = list(kwargs.items())[0]
        record = firebase_reference.order_by_child(field_name).equal_to(field_value).get()
        # Firebase doesn't support querying on multiple keys, so have to
        # filter the further keys here
        records = list(record.values())
        if len(kwargs) > 1:
            records = filter_records(records, kwargs)
        return records

    def remove(self, path):
        assert path not in ["", "/"]
        self.reference(path).delete()

    def query_by_key_range(self, path, start_at=None, end_at=None, limit_to_first: Optional[int] = None, limit_to_last: Optional[int] = None):
        firebase_reference = self.reference(path)
        query = firebase_reference.order_by_key()
        query = self._range_query_modifier(query, start_at, end_at, limit_to_first, limit_to_last)
        result = query.get()
        return result

    def query_by_child_value_range(self, path, by, start_at=None, end_at=None, limit_to_first: Optional[int] = None, limit_to_last: Optional[int] = None):
        firebase_reference = self.reference(path)
        query = firebase_reference.order_by_child(by)
        query = self._range_query_modifier(query, start_at, end_at, limit_to_first, limit_to_last)
        result = query.get()
        return result

    def atomic_add(self, path: str, value: float):
        func = partial(add, y=value)
        self.atomic_set(path, func)

    def atomic_increment(self, path: str):
        self.atomic_set(path, incrementer)

    def atomic_decrement(self, path: str):
        self.atomic_set(path, decrementer)

    def atomic_set(self, path: str, operation: callable):
        """Atomic version of set to avoid write clashes"""
        firebase_reference = self.reference(path)
        firebase_reference.transaction(operation)

    def _initialize_firebase(self):
        name = self.__class__.__name__
        try:
            credentials = firebase_admin.credentials.Certificate(self.credentials_file)
            init_params = {"databaseURL": self.url}
            self.app = firebase_admin.initialize_app(credentials, init_params, name=name)
        except ValueError:
            self.app = firebase_admin.get_app(name=name)

    def _range_query_modifier(self, query, start_at, end_at, limit_to_first, limit_to_last):
        if start_at:
            query = query.start_at(start_at)
        if end_at:
            query = query.end_at(end_at)
        if limit_to_first:
            query = query.limit_to_first(limit_to_first)
        if limit_to_last:
            query = query.limit_to_last(limit_to_last)
        return query


def serialise_input(record: dict):
    json_string = json.dumps(record, default=str)
    serialised_record = json.loads(json_string)
    return serialised_record


def add(x, y):
    return x + y


def incrementer(x):
    """Separate to make testable"""
    x = x if x else 0
    return x + 1


def decrementer(x):
    """Separate to make testable"""
    x = x if x else 0
    return x - 1


def filter_records(records, filters):
    filtered_records = []
    for record in records:
        # If filters is a subset of the record, then its good
        if filters.items() <= record.items():
            filtered_records.append(record)
    return filtered_records
