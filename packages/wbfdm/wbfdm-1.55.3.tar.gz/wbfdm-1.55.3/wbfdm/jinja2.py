from jinja2 import Environment
from jinjasql import JinjaSql  # type: ignore


def get_environment(**options):
    env = Environment(**options)
    return JinjaSql(env=env, param_style="format").env
