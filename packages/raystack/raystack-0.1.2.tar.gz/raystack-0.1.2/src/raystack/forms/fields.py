class Field:
    def __init__(self, label=None, required=True, initial=None, help_text=None, widget=None):
        self.label = label
        self.required = required
        self.initial = initial
        self.help_text = help_text
        self.widget = widget
        self.value = initial
        self.errors = []

    def clean(self, value):
        if self.required and (value is None or value == ''):
            self.errors.append('This field is required.')
            raise ValueError('This field is required.')
        return value

    def get_bound_value(self, data, name):
        return data.get(name, self.initial)

    def render(self, name, value=None):
        value = value if value is not None else self.initial or ''
        return f'<input type="text" name="{name}" value="{value}">'  # basic input

class CharField(Field):
    def clean(self, value):
        value = super().clean(value)
        if value is not None:
            value = str(value)
        return value

class IntegerField(Field):
    def clean(self, value):
        value = super().clean(value)
        if value is not None and value != '':
            try:
                value = int(value)
            except (TypeError, ValueError):
                self.errors.append('Please enter an integer.')
                raise ValueError('Please enter an integer.')
        return value 