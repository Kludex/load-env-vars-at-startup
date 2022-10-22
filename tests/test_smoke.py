import inspect

import load_env_vars_at_startup


def test_smoke() -> None:
    assert inspect.ismodule(load_env_vars_at_startup)
