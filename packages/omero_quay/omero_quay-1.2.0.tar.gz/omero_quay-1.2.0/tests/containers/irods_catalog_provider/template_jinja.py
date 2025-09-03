import sys
from pathlib import Path
from jinja2 import Environment, BaseLoader
import os


def render_template(json_file, template_file):
    env = Environment(loader=BaseLoader())
    env.globals.update(os.environ)

    with Path(template_file).open() as file_:
        template = env.from_string(file_.read())

    with Path(json_file).open('w', encoding='utf-8') as f:
        f.write(template.render())


json_file = sys.argv[1]
template_file = sys.argv[2]

render_template(json_file, template_file)
