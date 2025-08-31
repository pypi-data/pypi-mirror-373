from pathlib import Path

import jinja2

from raystack.conf import settings
from raystack.template import TemplateDoesNotExist, TemplateSyntaxError
from raystack.utils.functional import cached_property
from raystack.utils.module_loading import import_string
from raystack.forms.renderers import register_jinja2_form_filters

from .base import BaseEngine


class Jinja2(BaseEngine):
    app_dirname = "jinja2"

    def __init__(self, params):
        params = params.copy()
        options = params.pop("OPTIONS").copy()

        super().__init__(params)

        self.context_processors = options.pop("context_processors", [])

        environment = options.pop("environment", "jinja2.Environment")
        environment_cls = import_string(environment)
        
        if "loader" not in options:
            options["loader"] = jinja2.FileSystemLoader(self.template_dirs)

        self.env = environment_cls(**options)
        register_jinja2_form_filters(self.env)

    def get_template(self, template_name):
        try:
            return Template(self.env.get_template(template_name), self)
        except jinja2.TemplateNotFound as exc:
            raise TemplateDoesNotExist(exc.name, backend=self) from exc
        except jinja2.TemplateSyntaxError as exc:
            new = TemplateSyntaxError(exc.args)
            raise new from exc

    @cached_property
    def template_context_processors(self):
        return [import_string(path) for path in self.context_processors]


class Template:
    def __init__(self, template, backend):
        self.template = template
        self.backend = backend
        self.origin = Origin(
            name=template.filename,
            template_name=template.name,
        )

    def render(self, context=None, request=None):
        if context is None:
            context = {}
        if request is not None:
            context["request"] = request
            for context_processor in self.backend.template_context_processors:
                context.update(context_processor(request))
        try:
            return self.template.render(context)
        except jinja2.TemplateSyntaxError as exc:
            new = TemplateSyntaxError(exc.args)
            raise new from exc


class Origin:
    """
    A container to hold debug information as described in the template API
    documentation.
    """

    def __init__(self, name, template_name):
        self.name = name
        self.template_name = template_name
