import asyncio
from raystack.core.database.sqlalchemy import db
from raystack.core.database.fields.related import ForeignKeyField
import inspect

class SyncResult:
    """Helper class to make synchronous results 'awaitable'."""
    def __init__(self, result):
        self._result = result

    def __await__(self):
        yield from ()
        return self._result

    def __iter__(self):
        """Make SyncResult iterable if the wrapped result is iterable."""
        if hasattr(self._result, '__iter__'):
            return iter(self._result)
        raise TypeError(f"'{self._result.__class__.__name__}' object is not iterable")

    def __len__(self):
        """Make SyncResult support len() if the wrapped result has length."""
        if hasattr(self._result, '__len__'):
            return len(self._result)
        raise TypeError(f"'{self._result.__class__.__name__}' object has no len()")

    def __getitem__(self, key):
        """Make SyncResult support indexing if the wrapped result is indexable."""
        if hasattr(self._result, '__getitem__'):
            return self._result[key]
        raise TypeError(f"'{self._result.__class__.__name__}' object is not subscriptable")

    def __bool__(self):
        """Make SyncResult support boolean evaluation."""
        return bool(self._result)
    
    def __getattr__(self, name):
        """Delegate attribute access to the wrapped result."""
        return getattr(self._result, name)

def universal_executor(sync_func, async_func, *args, **kwargs):
    if should_use_async():
        # If async is enabled, return the coroutine directly for awaiting
        return async_func(*args, **kwargs)
    else:
        # If sync, execute the sync function and wrap result for pseudo-awaiting
        return SyncResult(sync_func(*args, **kwargs))

def is_async_context():
    """Accurately determines if we are in an async context"""
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False

def should_use_async():
    """
    Determines whether to use asynchronous mode.
    Now determined by URL in settings, not by execution context.
    """
    return db.is_async_url()

class QuerySet:
    def __init__(self, model_class):
        self.model_class = model_class
        self.query = f'SELECT * FROM "{model_class.get_table_name()}"'
        self.params = None
        self.order_by_fields = []

    def filter(self, **kwargs):
        # Always returns QuerySet, not coroutine
        return self._filter_sync(**kwargs)

    def _filter_sync(self, **kwargs):
        new_queryset = QuerySet(self.model_class)
        conditions = []
        for field_name, value in kwargs.items():
            if field_name not in self.model_class._fields:
                raise KeyError(f"Field '{field_name}' does not exist in model '{self.model_class.__name__}'")
            field = self.model_class._fields[field_name]
            if isinstance(field, ForeignKeyField):
                related_model = field.get_related_model()
                if related_model and isinstance(value, related_model):
                    value = value.id
                elif not isinstance(value, int):
                    raise ValueError(f"Invalid value for foreign key '{field_name}': {value}")
            if isinstance(value, str):
                conditions.append(f'"{field_name}"=\'{value}\'')
            else:
                conditions.append(f'"{field_name}"={value}')
        if 'WHERE' in self.query:
            new_queryset.query = f"{self.query} AND {' AND '.join(conditions)}"
        else:
            new_queryset.query = f"{self.query} WHERE {' AND '.join(conditions)}"
        new_queryset.params = None
        return new_queryset

    def all(self):
        # Always returns QuerySet
        return self

    def execute_all(self):
        """Executes the query and returns all results."""
        return universal_executor(self._execute_sync, self._execute_async)

    def order_by(self, *fields):
        # Always returns QuerySet
        new_queryset = QuerySet(self.model_class)
        new_queryset.query = self.query
        new_queryset.params = self.params
        new_queryset.order_by_fields = list(fields)
        order_conditions = []
        for field in fields:
            if field.startswith('-'):
                order_conditions.append(f'"{field[1:]}" DESC')
            else:
                order_conditions.append(f'"{field}" ASC')
        if order_conditions:
            new_queryset.query += f" ORDER BY {', '.join(order_conditions)}"
        return new_queryset

    def execute(self):
        return universal_executor(self._execute_sync, self._execute_async)

    def first(self):
        return universal_executor(self._first_sync, self._first_async)

    def count(self):
        return universal_executor(self._count_sync, self._count_async)

    def exists(self):
        return universal_executor(self._exists_sync, self._exists_async)

    def delete(self):
        return universal_executor(self._delete_sync, self._delete_async)

    def create(self, **kwargs):
        return universal_executor(self._create_sync, self._create_async, **kwargs)

    # All sync methods use only _sync implementations, async — only _async implementations

    def _execute_sync(self):
        result = db.execute(self.query, self.params or (), fetch=True)
        return [
            self.model_class(**dict(zip(self.model_class._fields.keys(), row)))
            for row in result
        ]

    async def _execute_async(self):
        result = await db.execute_async(self.query, self.params or (), fetch=True)
        return [
            self.model_class(**dict(zip(self.model_class._fields.keys(), row)))
            for row in result
        ]

    def _first_sync(self):
        query = f"{self.query} LIMIT 1"
        result = db.execute(query, self.params or (), fetch=True)
        if result:
            row = result[0]
            return self.model_class(**{
                key: value for key, value in zip(self.model_class._fields.keys(), row)
                if key in self.model_class._fields
            })
        return None

    async def _first_async(self):
        query = f"{self.query} LIMIT 1"
        result = await db.execute_async(query, self.params or (), fetch=True)
        if result:
            row = result[0]
            return self.model_class(**{
                key: value for key, value in zip(self.model_class._fields.keys(), row)
                if key in self.model_class._fields
            })
        return None

    def _count_sync(self):
        count_query = self.query.replace('SELECT *', 'SELECT COUNT(*)')
        result = db.execute(count_query, self.params or (), fetch=True)
        return result[0][0] if result else 0

    async def _count_async(self):
        count_query = self.query.replace('SELECT *', 'SELECT COUNT(*)')
        result = await db.execute_async(count_query, self.params or (), fetch=True)
        return result[0][0] if result else 0

    def _exists_sync(self):
        return self._count_sync() > 0

    async def _exists_async(self):
        count_result = await self._count_async()
        return count_result > 0

    def _delete_sync(self):
        delete_query = f'DELETE FROM "{self.model_class.get_table_name()}"'
        if 'WHERE' in self.query:
            where_clause = self.query.split('WHERE')[1]
            delete_query += f" WHERE {where_clause}"
        db.execute(delete_query, self.params or ())
        return True

    async def _delete_async(self):
        delete_query = f'DELETE FROM "{self.model_class.get_table_name()}"'
        if 'WHERE' in self.query:
            where_clause = self.query.split('WHERE')[1]
            delete_query += f" WHERE {where_clause}"
        await db.execute_async(delete_query, self.params or ())
        return True

    def _create_sync(self, **kwargs):
        fields = []
        values = []
        for field_name, value in kwargs.items():
            if field_name not in self.model_class._fields:
                raise KeyError(f"Field '{field_name}' does not exist in model '{self.model_class.__name__}'")
            field = self.model_class._fields[field_name]
            if isinstance(field, ForeignKeyField):
                related_model = field.get_related_model()
                if related_model and isinstance(value, related_model):
                    value = value.id
                elif not isinstance(value, int):
                    raise ValueError(f"Invalid value for foreign key '{field_name}': {value}")
            fields.append(f'"{field_name}"')
            if isinstance(value, str):
                values.append(f"'{value}'")
            else:
                values.append(str(value))
        insert_query = f'INSERT INTO "{self.model_class.get_table_name()}" ({", ".join(fields)}) VALUES ({", ".join(values)})'
        db.execute(insert_query)
        last_id = db.lastrowid()
        if last_id is None:
            raise RuntimeError("Failed to retrieve the ID of the newly created record.")
        return self.model_class.objects.get(id=last_id)

    async def _create_async(self, **kwargs):
        fields = []
        values = []
        for field_name, value in kwargs.items():
            if field_name not in self.model_class._fields:
                raise KeyError(f"Field '{field_name}' does not exist in model '{self.model_class.__name__}'")
            field = self.model_class._fields[field_name]
            if isinstance(field, ForeignKeyField):
                related_model = field.get_related_model()
                if related_model and isinstance(value, related_model):
                    value = value.id
                elif not isinstance(value, int):
                    raise ValueError(f"Invalid value for foreign key '{field_name}': {value}")
            fields.append(f'"{field_name}"')
            if isinstance(value, str):
                values.append(f"'{value}'")
            else:
                values.append(str(value))
        insert_query = f'INSERT INTO "{self.model_class.get_table_name()}" ({", ".join(fields)}) VALUES ({", ".join(values)})'
        await db.execute_async(insert_query)
        last_id = await db.lastrowid_async()
        if last_id is None:
            raise RuntimeError("Failed to retrieve the ID of the newly created record.")
        return await self.model_class.objects.get(id=last_id)

    # Support for iterations and lazy loading
    def __repr__(self):
        """String representation of QuerySet."""
        return f"<QuerySet: {self.model_class.__name__}>"

    def __str__(self):
        """String representation of QuerySet."""
        return f"<QuerySet: {self.model_class.__name__}>"

    # Methods for iterations (work in sync and async contexts)
    def iter(self):
        """Returns an iterable object with query results (lazy loading)."""
        # _iter_async and _iter_sync methods already return iterators/async iterators
        # that are directly awaitable or iterable, so no need for universal_executor here.
        if should_use_async():
            return self._iter_async()
        else:
            return self._iter_sync()

    def _iter_sync(self):
        """Synchronous iteration over results (lazy loading)."""
        # Execute query and return iterator
        result = self._execute_sync()
        for item in result:
            yield item

    async def _iter_async(self):
        """Asynchronous iteration over results (lazy loading)."""
        # Execute query and return async iterator
        result = await self._execute_async()
        for item in result:
            yield item

    def get_item(self, key):
        """Gets element by index or slice."""
        if should_use_async():
            # For __getitem__ when async is used, we need to return an awaitable.
            # _get_item_async returns a coroutine, so it's already compatible.
            return self._get_item_async(key)
        else:
            # For __getitem__ when sync is used, we wrap the result in SyncResult
            # to make it awaitable in calling code if needed.
            return SyncResult(self._get_item_sync(key))

    def _get_item_sync(self, key):
        """Synchronous element retrieval."""
        if isinstance(key, slice):
            # Slice - add LIMIT and OFFSET
            start = key.start or 0
            stop = key.stop
            limit = stop - start if stop is not None else None
            
            new_queryset = QuerySet(self.model_class)
            new_queryset.query = self.query
            new_queryset.params = self.params
            
            if limit is not None:
                new_queryset.query += f" LIMIT {limit}"
            if start > 0:
                new_queryset.query += f" OFFSET {start}"
            
            return new_queryset._execute_sync()
        elif isinstance(key, int):
            # Index - get specific record
            if key < 0:
                raise IndexError("Negative indexing is not supported")
            
            new_queryset = QuerySet(self.model_class)
            new_queryset.query = self.query
            new_queryset.params = self.params
            new_queryset.query += f" LIMIT 1 OFFSET {key}"
            
            result = new_queryset._execute_sync()
            if result:
                return result[0]
            else:
                raise IndexError("Index out of range")
        else:
            raise TypeError("QuerySet indices must be integers or slices")

    async def _get_item_async(self, key):
        """Asynchronous element retrieval."""
        if isinstance(key, slice):
            # Slice - add LIMIT and OFFSET
            start = key.start or 0
            stop = key.stop
            limit = stop - start if stop is not None else None
            
            new_queryset = QuerySet(self.model_class)
            new_queryset.query = self.query
            new_queryset.params = self.params
            
            if limit is not None:
                new_queryset.query += f" LIMIT {limit}"
            if start > 0:
                new_queryset.query += f" OFFSET {start}"
            
            return await new_queryset._execute_async()
        elif isinstance(key, int):
            # Index - get specific record
            if key < 0:
                raise IndexError("Negative indexing is not supported")
            
            new_queryset = QuerySet(self.model_class)
            new_queryset.query = self.query
            new_queryset.params = self.params
            new_queryset.query += f" LIMIT 1 OFFSET {key}"
            
            result = await new_queryset._execute_async() # Fix: should use _execute_async
            if result:
                return result[0]
            else:
                raise IndexError("Index out of range")
        else:
            raise TypeError("QuerySet indices must be integers or slices")

    def __len__(self):
        """Returns the number of records in QuerySet."""
        return self.count()

    def __bool__(self):
        """Checks if records exist in QuerySet."""
        return self.exists()

    def __contains__(self, item):
        """Checks if object is contained in QuerySet."""
        if not isinstance(item, self.model_class):
            return False
        
        # Simple ID check
        if hasattr(item, 'id'):
            return self.filter(id=item.id).exists()
        return False

    def __iter__(self):
        """Support for direct iteration over QuerySet (lazy loading)."""
        return self.iter()

    def __aiter__(self):
        """Support for asynchronous iteration over QuerySet (lazy loading)."""
        return self._iter_async()

    def __getitem__(self, key):
        """Support for QuerySet indexing (lazy loading)."""
        return self.get_item(key)
