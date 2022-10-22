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
from libcst.metadata.scope_provider import GlobalScope, ImportAssignment, ScopeProvider

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


@dataclass(frozen=True, eq=True)
class EnvVar:
    name: str
    default: Any


class ReplaceGetEnvCodemod(VisitorBasedCodemodCommand):  # type: ignore[misc]
    DESCRIPTION: str = "Rewrite code to load environment variables at startup."

    METADATA_DEPENDENCIES = (ScopeProvider,)

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        context.scratch["env_vars"] = []

    @m.leave(  # type: ignore[misc]
        m.Expr(
            value=m.Call(
                func=m.Attribute(value=m.Name("os"), attr=m.Name("getenv"))
                | m.Attribute(
                    value=m.Attribute(value=m.Name("os"), attr=m.Name("environ")),
                    attr=m.Name("get"),
                )
            )
        )
    )
    def leave_getenv(self, _: cst.Expr, updated_node: cst.Expr) -> cst.Expr:
        call = cst.ensure_type(updated_node.value, cst.Call)
        name_arg = call.args[0]
        if m.matches(name_arg.value, m.SimpleString()):
            simple_string = cst.ensure_type(name_arg.value, cst.SimpleString)
            name = simple_string.value.strip('"')
        else:
            logger.info(
                "Only simple string literals are supported for now, "
                "please create an issue about this on:\n"
                "https://github.com/Kludex/load-env-vars-at-startup/issues/new."
            )
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

    @m.leave(  # type: ignore[misc]
        m.Expr(
            value=m.Call(
                func=m.Name("getenv")
                | m.Attribute(value=m.Name("environ"), attr=m.Name("get")),
            )
        )
    )
    def from_os(self, original_node: cst.Expr, updated_node: cst.Expr) -> cst.Expr:
        """Replaces `getenv` and `environ.get` calls from `os`."""
        scope = self.get_metadata(ScopeProvider, original_node)

        if isinstance(scope, GlobalScope):
            for assignment in scope.assignments:
                if isinstance(assignment, ImportAssignment):
                    if assignment.get_module_name_for_import() == "os":
                        return self.leave_getenv(original_node, updated_node)

        return updated_node

    @m.leave(  # type: ignore[misc]
        m.Expr(
            value=m.Subscript(
                value=m.Attribute(value=m.Name("os"), attr=m.Name("environ")),
            )
        )
    )
    def leave_environ(self, _: cst.Expr, updated_node: cst.Expr) -> cst.Expr:
        subscript = cst.ensure_type(updated_node.value, cst.Subscript)
        for element in subscript.slice:
            is_string = m.matches(
                element, m.SubscriptElement(slice=m.Index(value=m.SimpleString()))
            )
            if is_string:
                slice = cst.ensure_type(element.slice, cst.Index)
                simple_string = cst.ensure_type(slice.value, cst.SimpleString)
                name = simple_string.value.strip('"')
                self.context.scratch["env_vars"].append(EnvVar(name=name, default=None))

                AddImportsVisitor.add_needed_import(
                    self.context, self.context.scratch["module"], "settings"
                )

                attribute = cst.Attribute(
                    value=cst.Name("settings"), attr=cst.Name(name)
                )
                return updated_node.with_changes(value=attribute)

        return updated_node

    @m.leave(  # type: ignore[misc]
        m.Expr(
            value=m.Subscript(
                value=m.Name("environ"),
            )
        )
    )
    def environ_from_os(
        self, original_node: cst.Expr, updated_node: cst.Expr
    ) -> cst.Expr:
        """Replaces `environ` subscript calls from `os`."""
        scope = self.get_metadata(ScopeProvider, original_node)

        if isinstance(scope, GlobalScope):
            for assignment in scope.assignments:
                if isinstance(assignment, ImportAssignment):
                    if assignment.get_module_name_for_import() == "os":
                        return self.leave_environ(original_node, updated_node)

        return updated_node
