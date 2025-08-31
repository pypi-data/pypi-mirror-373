"""
This module collects helper functions and classes that "span" multiple levels
of MVC. In other words, these functions/classes introduce controlled coupling
for convenience's sake.
"""

from raystack.responses import HTMLResponse


def render_template(
    request, template_name, context=None, content_type=None, status=None, using=None
):
    """
    Return an HttpResponse whose content is filled with the result of calling
    raystack.template.loader.render_to_string() with the passed arguments.
    """
    from raystack.template import loader
    
    content = loader.render_to_string(template_name, context, request, using=using)
    return HTMLResponse(content)
