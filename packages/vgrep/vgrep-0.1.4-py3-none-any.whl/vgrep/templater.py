from jinja2 import Environment, PackageLoader, select_autoescape


class Templater:
    def __init__(self, template_name):
        self.env = Environment(
            loader=PackageLoader("vgrep"),
            autoescape=select_autoescape()
        )
        self.template = self.env.get_template(template_name)

    def render_template(self, **params):
        return self.template.render(**params)
