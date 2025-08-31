class Field:
    def __init__(self, column_type, primary_key=False, default=None, unique=False, null=False, blank=False, verbose_name=None, help_text=None, choices=None, db_index=False, editable=True, auto_now=False, auto_now_add=False):
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default
        self.unique = unique
        self.null = null
        self.blank = blank
        self.verbose_name = verbose_name
        self.help_text = help_text
        self.choices = choices
        self.db_index = db_index
        self.editable = editable
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add
    
    def contribute_to_class(self, model_class, name):
        """
        Method that links field to model.
        :param model_class: Model class to which field is added.
        :param name: Field name in model.
        """
        self.name = name  # Set field name
        self.model_class = model_class

        # Add field to model fields list
        if not hasattr(model_class, '_meta'):
            model_class._meta = {}
        if 'fields' not in model_class._meta:
            model_class._meta['fields'] = []
        model_class._meta['fields'].append(self)

        # If field is primary key, add it to _meta
        if self.primary_key:
            if 'primary_key' in model_class._meta:
                raise ValueError(f"Model '{model_class.__name__}' already has a primary key.")
            model_class._meta['primary_key'] = self


class RelatedField(Field):
    def __init__(self, to, related_name=None, on_delete=None, **kwargs):
        super().__init__("INTEGER", **kwargs)
        self.to = to
        self.related_name = related_name
        self.on_delete = on_delete or "CASCADE"
    
    def get_related_model(self):
        """
        Returns related model.
        """
        from raystack.core.database.models import ModelMeta
        if isinstance(self.to, str):
            try:
                return ModelMeta.get_model(self.to)
            except KeyError:
                raise ValueError(f"Related model '{self.to}' is not registered in ModelMeta.")
        return self.to

    def contribute_to_class(self, model_class, name):
        """
        Adds field to model metadata and configures relationship.
        """
        super().contribute_to_class(model_class, name)
        self.name = name
        self.cache_name = f"_{name}_cache"  # Set cache_name here

        # Create attribute for storing foreign key value
        setattr(model_class, f"_{name}", None)

        # Add field to model metadata
        if not hasattr(model_class, '_meta'):
            model_class._meta = {}
        if 'foreign_keys' not in model_class._meta:
            model_class._meta['foreign_keys'] = []
        model_class._meta['foreign_keys'].append(self)

        # Configure reverse relationship in related model
        related_model = self.get_related_model()
        if self.related_name and hasattr(related_model, '_meta'):
            if 'reverse_relations' not in related_model._meta:
                related_model._meta['reverse_relations'] = {}
            related_model._meta['reverse_relations'][self.related_name] = model_class


# Basic fields
class CharField(Field):
    def __init__(self, max_length, **kwargs):
        super().__init__(f"VARCHAR({max_length})", **kwargs)
        self.max_length = max_length

class TextField(Field):
    def __init__(self, **kwargs):
        super().__init__("TEXT", **kwargs)

class IntegerField(Field):
    def __init__(self, **kwargs):
        super().__init__("INTEGER", **kwargs)

class BigIntegerField(Field):
    def __init__(self, **kwargs):
        super().__init__("BIGINT", **kwargs)

class SmallIntegerField(Field):
    def __init__(self, **kwargs):
        super().__init__("SMALLINT", **kwargs)

class PositiveIntegerField(Field):
    def __init__(self, **kwargs):
        super().__init__("INTEGER", **kwargs)

class PositiveSmallIntegerField(Field):
    def __init__(self, **kwargs):
        super().__init__("SMALLINT", **kwargs)

class AutoField(Field):
    def __init__(self, **kwargs):
        super().__init__("INTEGER", primary_key=True, **kwargs)

class BigAutoField(Field):
    def __init__(self, **kwargs):
        super().__init__("BIGINT", primary_key=True, **kwargs)

class BooleanField(Field):
    def __init__(self, **kwargs):
        super().__init__("BOOLEAN", **kwargs)

class NullBooleanField(Field):
    def __init__(self, **kwargs):
        super().__init__("BOOLEAN", null=True, **kwargs)

class FloatField(Field):
    def __init__(self, **kwargs):
        super().__init__("REAL", **kwargs)

class DecimalField(Field):
    def __init__(self, max_digits, decimal_places, **kwargs):
        super().__init__(f"DECIMAL({max_digits},{decimal_places})", **kwargs)
        self.max_digits = max_digits
        self.decimal_places = decimal_places

class DateField(Field):
    def __init__(self, **kwargs):
        super().__init__("DATE", **kwargs)

class DateTimeField(Field):
    def __init__(self, auto_now=False, auto_now_add=False, **kwargs):
        super().__init__("DATETIME", **kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add

class TimeField(Field):
    def __init__(self, **kwargs):
        super().__init__("TIME", **kwargs)

class EmailField(Field):
    def __init__(self, max_length=254, **kwargs):
        super().__init__(f"VARCHAR({max_length})", **kwargs)
        self.max_length = max_length

class URLField(Field):
    def __init__(self, max_length=200, **kwargs):
        super().__init__(f"VARCHAR({max_length})", **kwargs)
        self.max_length = max_length

class SlugField(Field):
    def __init__(self, max_length=50, **kwargs):
        super().__init__(f"VARCHAR({max_length})", **kwargs)
        self.max_length = max_length

class FileField(Field):
    def __init__(self, upload_to=None, max_length=100, **kwargs):
        super().__init__(f"VARCHAR({max_length})", **kwargs)
        self.upload_to = upload_to
        self.max_length = max_length

class ImageField(Field):
    def __init__(self, upload_to=None, height_field=None, width_field=None, max_length=100, **kwargs):
        super().__init__(f"VARCHAR({max_length})", **kwargs)
        self.upload_to = upload_to
        self.height_field = height_field
        self.width_field = width_field
        self.max_length = max_length

class FilePathField(Field):
    def __init__(self, path=None, match=None, recursive=False, max_length=100, **kwargs):
        super().__init__(f"VARCHAR({max_length})", **kwargs)
        self.path = path
        self.match = match
        self.recursive = recursive
        self.max_length = max_length

class GenericIPAddressField(Field):
    def __init__(self, protocol='both', unpack_ipv4=False, **kwargs):
        super().__init__("VARCHAR(39)", **kwargs)
        self.protocol = protocol
        self.unpack_ipv4 = unpack_ipv4

class UUIDField(Field):
    def __init__(self, **kwargs):
        super().__init__("VARCHAR(32)", **kwargs)

# Special fields
class JSONField(Field):
    def __init__(self, **kwargs):
        super().__init__("TEXT", **kwargs)

class BinaryField(Field):
    def __init__(self, **kwargs):
        super().__init__("BLOB", **kwargs)

# Relationship fields
class ForeignKey(RelatedField):
    def __init__(self, to, on_delete=None, **kwargs):
        super().__init__(to, on_delete=on_delete, **kwargs)

class OneToOneField(RelatedField):
    def __init__(self, to, on_delete=None, **kwargs):
        super().__init__(to, on_delete=on_delete, **kwargs)

class ManyToManyField(RelatedField):
    def __init__(self, to, through=None, through_fields=None, **kwargs):
        super().__init__(to, **kwargs)
        self.through = through
        self.through_fields = through_fields

# Computation fields
class ComputedField(Field):
    def __init__(self, compute=None, **kwargs):
        super().__init__("COMPUTED", **kwargs)
        self.compute = compute

# Index fields
class IndexField(Field):
    def __init__(self, **kwargs):
        super().__init__("INDEX", **kwargs)
        self.db_index = True
