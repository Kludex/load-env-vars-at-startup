SETTINGS_TEMPLATE = """from pydantic import BaseSettings


class Settings(BaseSettings):
{%- for env_var in env_vars %}
    {{ env_var.name }}: str{{ " = {env_var.default}" if env_var.default }}
{% endfor %}

settings = Settings()
"""  # pragma: no cover
