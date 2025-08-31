from raystack.core.database.fields import (
    CharField, IntegerField, Field, TextField, BooleanField, DateTimeField,
    AutoField, BigAutoField, BigIntegerField, SmallIntegerField, 
    PositiveIntegerField, PositiveSmallIntegerField, FloatField, DecimalField,
    DateField, TimeField, EmailField, URLField, SlugField, FileField, 
    ImageField, FilePathField, GenericIPAddressField, UUIDField, JSONField,
    BinaryField, ForeignKey, OneToOneField, ManyToManyField, ComputedField,
    IndexField, NullBooleanField
)
from raystack.core.database.manager import Manager
from raystack.core.database.sqlalchemy import db
from raystack.core.database.fields.related import ForeignKeyField

import asyncio


class ModelMeta(type):
    _registry = {}  # Dictionary for storing registered models

    def __new__(cls, name, bases, attrs):
        # Create new class
        new_class = super().__new__(cls, name, bases, attrs)

        # Register model in registry if it's not the base Model class
        if name != "Model":
            cls._registry[name] = new_class

        # Collect fields in _fields dictionary
        fields = {}
        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, Field):  # Check if attribute is Field instance
                attr_value.contribute_to_class(new_class, attr_name)  # Call contribute_to_class
                fields[attr_name] = attr_value

        # Attach _fields to class
        new_class._fields = fields
        return new_class

    @classmethod
    def get_model(cls, name):
        """
        Returns model by name from registry.
        """
        return cls._registry.get(name)


class Model(metaclass=ModelMeta):
    table = None

    def __init__(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.objects = Manager(cls)
        cls.objects.model_class = cls
    
    def __getattr__(self, name):
        """
        Dynamic access to object attributes.
        If attribute doesn't exist, AttributeError is raised.
        """
        if name in self.__dict__:
            return self.__dict__[name]
        raise AttributeError(f"'{self.get_table_name()}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        """
        Dynamic setting of attribute values.
        """
        self.__dict__[name] = value
    
    def __str__(self):
        return "<%s object (%s)>" % (self.get_table_name(), self.id)

    def to_dict(self, exclude_private=True):
        """
        Convert model object to dictionary.
        :param exclude_private: If True, private fields won't be added to dictionary.
        """
        return {
            key: getattr(self, key)
            for key in self.__dict__
            if (not key.startswith("_") or not exclude_private)
        }

    @classmethod
    def get_table_name(cls):
        return (
            cls.table 
            if hasattr(cls, "table") and cls.table 
            else "_".join(cls.__module__.split('.')[1:-1] + [cls.__name__.lower()])
        )

    @classmethod
    def get_table(cls):
        """
        Creates and returns SQLAlchemy table for the model.
        """
        from sqlalchemy import Table, Column, MetaData, Integer, String, Boolean, DateTime, Text, Float
        from raystack.core.database.sqlalchemy import Base
        
        # Create table
        columns = []
        
        for field_name, field in cls._fields.items():
            # Convert field types to SQLAlchemy types
            if field.column_type == int:
                column_type = Integer
            elif field.column_type == str:
                column_type = String(255)  # Default VARCHAR(255)
            elif field.column_type == bool:
                column_type = Boolean
            elif field.column_type == float:
                column_type = Float
            else:
                column_type = String(255)  # Default
            
            primary_key = field.primary_key
            nullable = not field.primary_key
            unique = field.unique
            
            # Create column
            column = Column(
                field_name, 
                column_type, 
                primary_key=primary_key,
                nullable=nullable,
                unique=unique
            )
            
            columns.append(column)
        
        # Create table
        table = Table(
            cls.get_table_name(),
            Base.metadata,
            *columns
        )
        
        return table

    @classmethod
    def create_table(cls):
        """
        Creates table in database using SQLAlchemy.
        """
        columns = []
        
        for field_name, field in cls._fields.items():
            column_def = {
                'name': field_name,
                'type': field.column_type,
                'primary_key': field.primary_key,
                'nullable': not field.primary_key,
                'unique': field.unique
            }
            
            # Handle foreign keys
            if isinstance(field, ForeignKeyField):
                related_model = field.get_related_model()
                table_name = related_model.get_table_name()
                column_def['foreign_key'] = f"{table_name}.id"
            
            columns.append(column_def)

        # # Create table through SQLAlchemy backend
        # db.create_table(cls.get_table_name(), columns)

    def save(self):
        from raystack.core.database.query import universal_executor
        return universal_executor(self._save_sync, self._save_async, self)

    def _save_sync(self):
        print(f"[DEBUG] _save_sync called for {self.__class__.__name__}")
        data = {}
        for field, field_obj in self._fields.items():
            if isinstance(field_obj, AutoField):
                continue  # Don't add id to data at all
            value = getattr(self, field, None)
            if isinstance(field_obj, ForeignKeyField):
                if hasattr(value, 'id'):
                    value = value.id
            data[field] = value
        print(f"[DEBUG] Data to save: {data}")

        def convert_value(value):
            if isinstance(value, (int, float, str, bytes, type(None))):
                return value
            elif hasattr(value, '__str__'):
                return str(value)
            else:
                raise ValueError(f"Unsupported type for database: {type(value)}")

        data = {key: convert_value(value) for key, value in data.items()}
        print(f"[DEBUG] Converted data: {data}")

        id_value = self.__dict__.get('id', None)
        if id_value not in (None, 0, ''):
            set_clauses = []
            for key, value in data.items():
                if isinstance(value, str):
                    set_clauses.append(f'"{key}"=\'{value}\'')
                else:
                    set_clauses.append(f'"{key}"={value}')
            update_query = f"UPDATE {self.get_table_name()} SET {', '.join(set_clauses)} WHERE id={id_value}"
            print(f"[DEBUG] Executing update: {update_query}")
            db.execute(update_query)
        else:
            fields = []
            values = []
            for key, value in data.items():
                fields.append(f'"{key}"')
                if isinstance(value, str):
                    values.append(f"'{value}'")
                else:
                    values.append(str(value))
            insert_query = f"INSERT INTO {self.get_table_name()} ({', '.join(fields)}) VALUES ({', '.join(values)})"
            print(f"[DEBUG] Executing insert: {insert_query}")
            db.execute(insert_query)
            self.id = db.lastrowid()
            print(f"[DEBUG] New id set: {self.id}")
    
    async def _save_async(self):
        # async save implementation
        # Get field values from object
        data = {field: getattr(self, field, None) for field in self._fields}

        # Convert values to supported types
        def convert_value(value):
            if isinstance(value, (int, float, str, bytes, type(None))):
                return value
            elif hasattr(value, '__str__'):
                return str(value)  # Convert object to string if possible
            else:
                raise ValueError(f"Unsupported type for database: {type(value)}")

        data = {key: convert_value(value) for key, value in data.items()}

        # Check if object exists in database
        if hasattr(self, 'id') and self.id is not None:
            # Update existing record (UPDATE)
            set_clauses = []
            for key, value in data.items():
                if key != 'id':
                    if isinstance(value, str):
                        set_clauses.append(f'"{key}"=\'{value}\'')
                    else:
                        set_clauses.append(f'"{key}"={value}')
            
            update_query = f"UPDATE {self.get_table_name()} SET {', '.join(set_clauses)} WHERE id={self.id}"
            await db.execute_async(update_query)
        else:
            # Create new record (INSERT)
            fields = []
            values = []
            for key, value in data.items():
                if key != 'id':
                    fields.append(f'"{key}"')
                    if isinstance(value, str):
                        values.append(f"'{value}'")
                    else:
                        values.append(str(value))

            insert_query = f"INSERT INTO {self.get_table_name()} ({', '.join(fields)}) VALUES ({', '.join(values)})"
            await db.execute_async(insert_query)

            # Get id of created record
            self.id = await db.lastrowid_async()
    
    @classmethod
    def create(cls, **kwargs):
        from raystack.core.database.query import universal_executor
        return universal_executor(cls._create_sync, cls._create_async, **kwargs)

    @classmethod
    def _create_sync(cls, **kwargs):
        instance = cls(**kwargs)
        instance.save()
        return instance

    @classmethod
    async def _create_async(cls, **kwargs):
        instance = cls(**kwargs)
        await instance._save_async()
        return instance
    
    @classmethod
    # The 'get', 'filter', 'all' methods on Model itself are not directly used in urls.py,
    # and they are already async. The QuerySet object handles the sync/async logic.
    # The 'create' method is already handled.

    def delete(self):
        """
        Deletes record from database.
        """
        from raystack.core.database.query import universal_executor
        return universal_executor(self._delete_sync, self._delete_async, self)

    def _delete_sync(self):
        """
        Synchronously deletes record from database.
        """
        if hasattr(self, 'id') and self.id is not None:
            table_name = self.get_table_name()
            query = f"DELETE FROM {table_name} WHERE id = {self.id}"
            db.execute(query)

    async def _delete_async(self):
        """
        Asynchronously deletes record from database.
        """
        if hasattr(self, 'id') and self.id is not None:
            table_name = self.get_table_name()
            query = f"DELETE FROM {table_name} WHERE id = {self.id}"
            await db.execute_async(query)
    

