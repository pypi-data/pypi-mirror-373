from typing import Optional


class _InfernoDatabaseAdapter():
    def is_in_database(self, path: str):
        value = self.get(path, shallow=True)
        return value is not None

    def get(self, path: str, shallow: bool = True):
        raise NotImplementedError

    def set(self, path: str, value):
        raise NotImplementedError

    def update(self, path: str, record: dict):
        raise NotImplementedError

    def multi_update(self, path: str, record: dict):
        raise NotImplementedError

    def where(self, path, **kwargs):
        raise NotImplementedError

    def remove(self, path):
        raise NotImplementedError

    def query_by_key_range(self, path, start_at=None, end_at=None, limit_to_first: Optional[int] = None, limit_to_last: Optional[int] = None):
        raise NotImplementedError

    def query_by_child_value_range(self, path, by, start_at=None, end_at=None, limit_to_first: Optional[int] = None, limit_to_last: Optional[int] = None):
        raise NotImplementedError

    def atomic_set(self, path: str, operation: callable):
        raise NotImplementedError
