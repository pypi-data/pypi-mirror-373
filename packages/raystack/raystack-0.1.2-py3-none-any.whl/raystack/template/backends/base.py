from raystack.core.exceptions import ImproperlyConfigured, SuspiciousFileOperation
from raystack.template.utils import get_app_template_dirs
from raystack.utils._os import safe_join
from raystack.utils.functional import cached_property


class BaseEngine:
    # Core methods: engines have to provide their own implementation

    def __init__(self, params):
        """
        Initialize the template engine.

        `params` is a dict of configuration settings.
        """
        params = params.copy()
        self.name = params.pop("NAME")
        self.dirs = list(params.pop("DIRS"))
        self.app_dirs = params.pop("APP_DIRS")
        if params:
            raise ImproperlyConfigured(
                "Unknown parameters: {}".format(", ".join(params))
            )

    def get_template(self, template_name):
        """
        Load and return a template for the given name.

        Raise TemplateDoesNotExist if no such template exists.
        """
        raise NotImplementedError(
            "subclasses of BaseEngine must provide a get_template() method"
        )

    @cached_property
    def template_dirs(self):
        """
        Return a list of directories to search for templates.
        """
        # Immutable return value because it's cached and shared by callers.
        result = tuple(self.dirs)
        if self.app_dirs:
            result += get_app_template_dirs(self.app_dirname)
        return result
