# Register filter for Jinja2

def form_as_p(form):
    return form.as_p()

def register_jinja2_form_filters(jinja_env):
    jinja_env.filters['form_as_p'] = form_as_p 