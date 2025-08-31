# Hard-coded processor for easier use of CSRF protection.
_builtin_context_processors = ("raystack.template.context_processors.csrf",)


class BaseContext:
    def __init__(self, dict_=None):
        self._reset_dicts(dict_)

    def _reset_dicts(self, value=None):
        builtins = {"True": True, "False": False, "None": None}
        self.dicts = [builtins]
        if isinstance(value, BaseContext):
            self.dicts += value.dicts[1:]
        elif value is not None:
            self.dicts.append(value)


class Context(BaseContext):
    "A stack container for variable context"

    def __init__(self, dict_=None, autoescape=True, use_l10n=None, use_tz=None):
        self.autoescape = autoescape
        self.use_l10n = use_l10n
        self.use_tz = use_tz
        self.template_name = "unknown"
        self.template = None
        super().__init__(dict_)
