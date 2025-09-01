# -*- coding: utf-8 -*-

"""
Source Code Build Automation for Python Projects.
"""

import typing as T
import shutil
import dataclasses

from .vendor.emoji import Emoji
from .vendor.build_dist import (
    build_dist_with_python_build,
    build_dist_with_poetry_build,
)

from .logger import logger

if T.TYPE_CHECKING:  # pragma: no cover
    from .define import PyWf


@dataclasses.dataclass
class PyWfBuild:
    """
    Namespace class for build related automation.
    """

    @logger.emoji_block(
        msg="Build python distribution using pypa-build",
        emoji=Emoji.build,
    )
    def _python_build(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Build python source distribution using
        `pypa-build <https://pypa-build.readthedocs.io/en/latest/>`_.
        
        Run:
        
        .. code-block:: bash
            
            python -m build --sdist --wheel
        """
        if self.dir_dist.exists():
            if real_run:
                shutil.rmtree(self.dir_dist, ignore_errors=True)
        build_dist_with_python_build(
            dir_project_root=self.dir_project_root,
            path_bin_python=self.path_venv_bin_python,
            log_func=logger.info,
            real_run=real_run,
            verbose=not quiet,
        )

    def python_build(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):  # pragma: no cover
        with logger.disabled(not verbose):
            return self._python_build(
                real_run=real_run,
                quiet=not verbose,
            )

    python_build.__doc__ = _python_build.__doc__

    @logger.emoji_block(
        msg="Build python distribution using poetry",
        emoji=Emoji.build,
    )
    def _poetry_build(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Build python source distribution using

        `poetry build <https://python-poetry.org/docs/cli/#build>`_.

        Run:

        .. code-block:: bash

            poetry build
        """
        if self.dir_dist.exists():
            if real_run:
                shutil.rmtree(self.dir_dist, ignore_errors=True)
        build_dist_with_poetry_build(
            dir_project_root=self.dir_project_root,
            path_bin_poetry=self.path_bin_poetry,
            log_func=logger.info,
            real_run=real_run,
            verbose=not quiet,
        )

    def poetry_build(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):  # pragma: no cover
        with logger.disabled(not verbose):
            return self._poetry_build(
                real_run=real_run,
                quiet=not verbose,
            )

    poetry_build.__doc__ = _poetry_build.__doc__
