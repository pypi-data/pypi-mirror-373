from raystack.core.database.fields import RelatedField
from raystack.core.exceptions import ValidationError

class ForeignKeyField(RelatedField):
    """
    Field for creating foreign key relationships between models.
    """

    def __init__(self, to, on_delete=None, related_name=None, to_field=None, **kwargs):
        """
        :param to: Related model (class or string with model name).
        :param on_delete: Function that defines behavior when related object is deleted.
        :param related_name: Name for reverse relationship (optional).
        :param to_field: Field in related model used for relationship (defaults to PK).
        :param kwargs: Additional parameters.
        """
        super().__init__("INTEGER", **kwargs)
        self.to = to  # Related model
        self.on_delete = on_delete  # Behavior on delete
        self.related_name = related_name  # Name for reverse relationship
        self.to_field = to_field  # Field in related model
        self.cache_name = None  # Name for caching related object

    def contribute_to_class(self, model_class, name):
        """
        Adds field to model metadata and configures relationship.
        """
        super().contribute_to_class(model_class, name)
        self.name = name
        self.cache_name = f"_{name}_cache"

        # Create attribute for storing foreign key value
        setattr(model_class, f"_{name}", None)

        if not hasattr(model_class, '_meta'):
            model_class._meta = {}
        if 'foreign_keys' not in model_class._meta:
            model_class._meta['foreign_keys'] = []
        model_class._meta['foreign_keys'].append(self)

        related_model = self.get_related_model()
        if self.related_name and hasattr(related_model, '_meta'):
            if 'reverse_relations' not in related_model._meta:
                related_model._meta['reverse_relations'] = {}
            related_model._meta['reverse_relations'][self.related_name] = model_class

    def get_related_model(self):
        """
        Returns related model.
        If self.to is a string, searches for model in registry.
        """
        from raystack.core.database.models import ModelMeta
        if isinstance(self.to, str):
            try:
                return ModelMeta.get_model(self.to)
            except KeyError:
                raise ValueError(f"Related model '{self.to}' is not registered in ModelMeta.")
        return self.to
    
    def create_related_instance(self, related_data):
        """
        Creates and returns instance of related model.
        """
        related_model = self.get_related_model()
        return related_model(**related_data)

    def validate(self, value):
        """
        Validates foreign key value.
        """
        related_model = self.get_related_model()
        if value is None:
            return  # Allowed if field is optional
        if not isinstance(value, related_model):
            raise ValidationError(f"Value must be an instance of {related_model.__name__}.")

    def __get__(self, instance, owner):
        """
        Descriptor for getting related object.
        """
        if instance is None:
            return self

        if hasattr(instance, self.cache_name):
            return getattr(instance, self.cache_name)

        related_model = self.get_related_model()
        related_id = instance.__dict__.get(self.name)

        if related_id is None:
            return None

        try:
            related_object = related_model.objects.filter(id=related_id).first()  # type: ignore
        except Exception as e:
            raise ValueError(f"Failed to load related object for field '{self.name}': {e}")

        setattr(instance, self.cache_name, related_object)
        return related_object

    def __set__(self, instance, value):
        """
        Descriptor for setting foreign key value.
        """
        if isinstance(value, self.get_related_model()):
            value = value.id  # If model object is passed, get its id
        elif not isinstance(value, int) and value is not None:
            raise ValueError(f"Invalid value for foreign key '{self.name}': {value}")

        # Set value through internal attribute to avoid recursion
        setattr(instance, f"_{self.name}", value)

        # Clear cache when value changes
        if hasattr(instance, self.cache_name):
            delattr(instance, self.cache_name)