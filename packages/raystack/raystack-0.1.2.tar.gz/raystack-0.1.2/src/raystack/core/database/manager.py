import asyncio
from raystack.core.database.query import QuerySet, should_use_async, universal_executor

class Manager:
    def __init__(self, model_class):
        self.model_class = model_class

    def filter(self, **kwargs):
        return QuerySet(self.model_class).filter(**kwargs)

    def all(self):
        return QuerySet(self.model_class).all()

    def create(self, **kwargs):
        return universal_executor(
            QuerySet(self.model_class)._create_sync,
            QuerySet(self.model_class)._create_async,
            **kwargs
        )

    def get(self, **kwargs):
        # get = filter + first
        qs = QuerySet(self.model_class).filter(**kwargs)
        return universal_executor(qs._first_sync, qs._first_async)

    def count(self):
        return universal_executor(QuerySet(self.model_class)._count_sync, QuerySet(self.model_class)._count_async)

    def exists(self):
        return universal_executor(QuerySet(self.model_class)._exists_sync, QuerySet(self.model_class)._exists_async)

    def delete(self, **kwargs):
        qs = QuerySet(self.model_class).filter(**kwargs)
        return universal_executor(qs._delete_sync, qs._delete_async)

            # Support for lazy loading and iteration
    def iter(self):
        """Returns an iterable object with query results (lazy loading)."""
        return QuerySet(self.model_class).iter()

    def get_item(self, key):
        """Gets element by index or slice (lazy loading)."""
        return QuerySet(self.model_class).get_item(key)

    def __iter__(self):
        """Support for direct iteration over Manager (lazy loading)."""
        return self.iter()

    def __getitem__(self, key):
        """Support for Manager indexing (lazy loading)."""
        return self.get_item(key)

    def __aiter__(self):
        """Support for asynchronous iteration over Manager (lazy loading)."""
        return QuerySet(self.model_class).__aiter__()
