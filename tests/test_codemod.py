import textwrap

import libcst as cst
from libcst.codemod import CodemodContext, CodemodTest

from load_env_vars_at_startup._codemod import ReplaceGetEnvCodemod


class TestReplaceGetEnvCodemod(CodemodTest):  # type: ignore[misc]
    TRANSFORM = ReplaceGetEnvCodemod

    def test_getenv(self) -> None:
        before = textwrap.dedent(
            """
            import os
            os.getenv("ENV_VAR")
        """
        )
        after = textwrap.dedent(
            """
            import os
            from module import settings

            settings.ENV_VAR
        """
        )
        wrapper = cst.MetadataWrapper(cst.parse_module(before))
        context = CodemodContext(scratch={"module": "module"}, wrapper=wrapper)
        self.assertCodemod(before, after, context_override=context)

    def test_getenv_wrong_import(self) -> None:
        before = textwrap.dedent(
            """
            from potato import getenv
            getenv("ENV_VAR")
        """
        )
        after = textwrap.dedent(
            """
            from potato import getenv
            getenv("ENV_VAR")
        """
        )
        wrapper = cst.MetadataWrapper(cst.parse_module(before))
        context = CodemodContext(scratch={"module": "module"}, wrapper=wrapper)
        self.assertCodemod(before, after, context_override=context)

    def test_environ_get(self) -> None:
        before = textwrap.dedent(
            """
            import os
            os.environ.get("ENV_VAR")
        """
        )
        after = textwrap.dedent(
            """
            import os
            from module import settings

            settings.ENV_VAR
        """
        )
        wrapper = cst.MetadataWrapper(cst.parse_module(before))
        context = CodemodContext(scratch={"module": "module"}, wrapper=wrapper)
        self.assertCodemod(before, after, context_override=context)

    def test_environ_getattr(self) -> None:
        before = textwrap.dedent(
            """
            import os
            os.environ["ENV_VAR"]
        """
        )
        after = textwrap.dedent(
            """
            import os
            from module import settings

            settings.ENV_VAR
        """
        )
        wrapper = cst.MetadataWrapper(cst.parse_module(before))
        context = CodemodContext(scratch={"module": "module"}, wrapper=wrapper)
        self.assertCodemod(before, after, context_override=context)

    def test_environ_getattr_wrong_import(self) -> None:
        before = textwrap.dedent(
            """
            from potato import environ
            environ["ENV_VAR"]
        """
        )
        after = textwrap.dedent(
            """
            from potato import environ
            environ["ENV_VAR"]
        """
        )
        wrapper = cst.MetadataWrapper(cst.parse_module(before))
        context = CodemodContext(scratch={"module": "module"}, wrapper=wrapper)
        self.assertCodemod(before, after, context_override=context)

    def test_environ_getattr_import(self) -> None:
        before = textwrap.dedent(
            """
            from os import environ
            environ["ENV_VAR"]
        """
        )
        after = textwrap.dedent(
            """
            from os import environ
            from module import settings

            settings.ENV_VAR
        """
        )
        wrapper = cst.MetadataWrapper(cst.parse_module(before))
        context = CodemodContext(scratch={"module": "module"}, wrapper=wrapper)
        self.assertCodemod(before, after, context_override=context)

    def test_environ_get_import(self) -> None:
        before = textwrap.dedent(
            """
            from os import environ
            environ.get("ENV_VAR")
        """
        )
        after = textwrap.dedent(
            """
            from os import environ
            from module import settings

            settings.ENV_VAR
        """
        )
        wrapper = cst.MetadataWrapper(cst.parse_module(before))
        context = CodemodContext(scratch={"module": "module"}, wrapper=wrapper)
        self.assertCodemod(before, after, context_override=context)

    def test_environ_get_wrong_import(self) -> None:
        before = textwrap.dedent(
            """
            from potato import environ
            environ.get("ENV_VAR")
        """
        )
        after = textwrap.dedent(
            """
            from potato import environ
            environ.get("ENV_VAR")
        """
        )
        wrapper = cst.MetadataWrapper(cst.parse_module(before))
        context = CodemodContext(scratch={"module": "module"}, wrapper=wrapper)
        self.assertCodemod(before, after, context_override=context)

    def test_getenv_import(self) -> None:
        before = textwrap.dedent(
            """
            from os import getenv
            getenv("ENV_VAR")
        """
        )
        after = textwrap.dedent(
            """
            from os import getenv
            from module import settings

            settings.ENV_VAR
        """
        )
        wrapper = cst.MetadataWrapper(cst.parse_module(before))
        context = CodemodContext(scratch={"module": "module"}, wrapper=wrapper)
        self.assertCodemod(before, after, context_override=context)
