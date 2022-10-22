import functools
import glob
import multiprocessing
from pathlib import Path
from typing import Union

import libcst as cst
from jinja2 import Template
from libcst.codemod import CodemodContext
from libcst.codemod.commands.remove_unused_imports import RemoveUnusedImportsCommand
from typer import Argument, Option, Typer

from load_env_vars_at_startup._codemod import EnvVar, ReplaceGetEnvCodemod
from load_env_vars_at_startup._templates import SETTINGS_TEMPLATE

app = Typer(add_completion=False)


def rewrite(filename: str, module: str) -> list[EnvVar]:
    with Path(filename).open("r") as file:
        mod = cst.parse_module(file.read())
        wrapper = cst.MetadataWrapper(mod)
        context = CodemodContext(scratch={"module": module}, wrapper=wrapper)
        mod = ReplaceGetEnvCodemod(context).transform_module(mod)
        mod = RemoveUnusedImportsCommand(context).transform_module(mod)

    with Path(filename).open("w") as file:
        file.write(mod.code)

    return context.scratch["env_vars"]  # type: ignore


@app.command()  # type: ignore[misc]
def main(
    dir: Path = Argument(
        ..., exists=True, dir_okay=True, help="Your project directory."
    ),
    config_path: Union[Path, None] = Option(
        None, help="Path of the config module. Defaults to <dir>/config.py."
    ),
) -> None:
    """Load environment variables at startup, please!

    This tool will rewrite your code to load environment variables at startup.
    """
    filenames = glob.glob(glob.escape(str(dir)) + "/**/*.py", recursive=True)
    config_path = config_path or dir / "config.py"
    module = config_path.stem

    _rewrite = functools.partial(rewrite, module=module)

    env_vars: set[EnvVar] = set()
    with multiprocessing.Pool() as pool:
        for result in pool.imap_unordered(_rewrite, filenames):
            env_vars = env_vars.union(result)

    template = Template(source=SETTINGS_TEMPLATE)
    output = template.render({"env_vars": env_vars})

    if len(env_vars) > 0:
        with config_path.open("w") as file:
            file.write(output)


if __name__ == "__main__":
    app()
