"""
This codemod replaces the following:

>>> os.getenv("ENV_VAR")

By:

>>> from <settings_module> import settings
... settings.ENV_VAR

It also applies to:

>>> os.environ.get("ENV_VAR")
>>> os.environ["ENV_VAR"]
"""

import logging
import sys
from dataclasses import dataclass
from typing import Any

import libcst as cst
import libcst.matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


@dataclass(frozen=True, eq=True)
class EnvVar:
    name: str
    default: Any


class ReplaceGetEnvCodemod(VisitorBasedCodemodCommand):
    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        context.scratch["env_vars"] = []

    @m.leave(
        m.Expr(
            value=m.Call(func=m.Attribute(value=m.Name("os"), attr=m.Name("getenv")))
        )
    )
    def leave_getenv(self, _: cst.Expr, updated_node: cst.Expr) -> cst.Expr:
        call = cst.ensure_type(updated_node.value, cst.Call)
        name_arg = call.args[0]
        if m.matches(name_arg.value, m.SimpleString()):
            simple_string = cst.ensure_type(name_arg.value, cst.SimpleString)
            name = simple_string.value.strip('"')
        else:
            logger.info("Only simple string literals are supported for now, skipping.")
            return updated_node

        if len(call.args) == 1:
            default = None
        else:
            default_arg = call.args[1]
            default = default_arg.value

        self.context.scratch["env_vars"].append(EnvVar(name=name, default=default))

        AddImportsVisitor.add_needed_import(
            self.context, self.context.scratch["module"], "settings"
        )

        attribute = cst.Attribute(value=cst.Name("settings"), attr=cst.Name(name))
        return updated_node.with_changes(value=attribute)
