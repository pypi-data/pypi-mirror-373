# -*- coding: utf-8 -*-

"""
Virtualenv management related automation.
"""

import typing as T
import shutil
import subprocess
import dataclasses

from .vendor.emoji import Emoji
from .vendor.better_pathlib import temp_cwd

from .logger import logger
from .helpers import print_command

if T.TYPE_CHECKING:  # pragma: no cover
    from .define import PyWf


@dataclasses.dataclass
class PyWfVenv:
    """
    Namespace class for Virtualenv management related automation.
    """

    @logger.emoji_block(
        msg="Create Virtual Environment",
        emoji=Emoji.python,
    )
    def _create_virtualenv(
        self: "PyWf",
        using_poetry: bool = True,
        real_run: bool = True,
        quiet: bool = False,
    ) -> bool:
        """
        Run:

        .. code-block:: bash

            $ poetry env use python${X}.${Y}

        :return: a boolean flat to indicate whether a creation is performed.
        """
        if self.dir_venv.exists():
            logger.info(f"{self.dir_venv} already exists, do nothing.")
            return False
        else:
            if using_poetry:
                # Ref: https://python-poetry.org/docs/managing-environments/
                # note that we defined to use in-project = true in poetry.toml file
                args = [
                    f"{self.path_bin_poetry}",
                    "config",
                    "virtualenvs.in-project",
                    "true",
                ]
                if quiet:
                    args.append("--quiet")
                self.run_command(args, real_run=real_run)

                args = [
                    f"{self.path_bin_poetry}",
                    "env",
                    "use",
                    f"python{self.py_ver_major}.{self.py_ver_minor}",
                ]
                if quiet:
                    args.append("--quiet")
                self.run_command(args, real_run=real_run)
            else:
                args = [
                    f"{self.path_bin_virtualenv}",
                    f"-p",
                    f"python{self.py_ver_major}.{self.py_ver_minor}",
                    f"{self.dir_venv}",
                ]
                self.run_command(args, real_run=real_run)

            logger.info("done")
            return True

    def create_virtualenv(
        self: "PyWf",
        using_poetry: bool = True,
        real_run: bool = True,
        verbose: bool = True,
    ) -> bool:  # pragma: no cover
        with logger.disabled(not verbose):
            return self._create_virtualenv(
                using_poetry=using_poetry,
                real_run=real_run,
                quiet=not verbose,
            )

    create_virtualenv.__doc__ = _create_virtualenv.__doc__

    @logger.emoji_block(
        msg="Remove Virtual Environment",
        emoji=Emoji.python,
    )
    def _remove_virtualenv(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ) -> bool:
        """
        Run:

        .. code-block:: bash

            $ rm -r /path/to/.venv

        :return: a boolean flag to indicate whether a deletion is performed.
        """
        if self.dir_venv.exists():
            # don't use rm -r here, we want it to be windows compatible
            if real_run:
                shutil.rmtree(f"{self.dir_venv}", ignore_errors=True)
            logger.info(f"done! {self.dir_venv} is removed.")
            return True
        else:
            logger.info(f"{self.dir_venv} doesn't exists, do nothing.")
            return False

    def remove_virtualenv(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(not verbose):
            return self._remove_virtualenv(
                real_run=real_run,
                quiet=not verbose,
            )

    remove_virtualenv.__doc__ = _remove_virtualenv.__doc__