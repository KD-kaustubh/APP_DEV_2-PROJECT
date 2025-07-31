from jinja2 import Environment, FileSystemLoader


def format_report(template_path, data):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_path.split('/')[-1])
    return template.render(data=data)