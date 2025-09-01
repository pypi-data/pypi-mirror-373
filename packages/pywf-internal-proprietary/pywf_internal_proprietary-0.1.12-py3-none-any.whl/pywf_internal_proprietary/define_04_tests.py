# -*- coding: utf-8 -*-

"""
Testing Automation for Python Projects.
"""

import typing as T
import subprocess
import dataclasses
from pathlib import Path

from .vendor.emoji import Emoji
from .vendor.os_platform import OPEN_COMMAND

from .logger import logger

if T.TYPE_CHECKING:  # pragma: no cover
    from .define import PyWf


@dataclasses.dataclass
class PyWfTests:
    """
    Namespace class for testing related automation.
    """

    def _do_we_run_test(
        self: "PyWf",
        dir_tests: Path,
    ) -> bool:
        flag = True
        if self.path_venv_bin_pytest.exists() is False:  # pragma: no cover
            logger.error(
                f"{Emoji.red_circle} pytest (.venv/bin/pytest) is not installed in the virtual environment."
            )
            flag = False
        if dir_tests.exists() is False:  # pragma: no cover
            logger.error(
                f"{Emoji.red_circle} tests directory {dir_tests} does not exist."
            )
            flag = False
        return flag

    @logger.emoji_block(
        msg="Run Unit Test",
        emoji=Emoji.test,
    )
    def _run_unit_test(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        A wrapper of ``pytest`` command to run unit test.

        Run:

        .. code-block:: bash

            pytest tests -s --rootdir=/path/to/project/root
        """
        flag = self._do_we_run_test(self.dir_tests)
        if not flag:  # pragma: no cover
            raise RuntimeError(f"{Emoji.red_circle} unit test not run!")
        args = [
            f"{self.path_venv_bin_pytest}",
            f"{self.dir_tests}",
            "-s",
            f"--rootdir={self.dir_project_root}",
        ]
        if quiet:
            args.append("--quiet")
        self.run_command(args, real_run)

    def run_unit_test(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(not verbose):
            return self._run_unit_test(
                real_run=real_run,
                quiet=not verbose,
            )

    run_unit_test.__doc__ = _run_unit_test.__doc__

    @logger.emoji_block(
        msg="Run Code Coverage Test",
        emoji=Emoji.test,
    )
    def _run_cov_test(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        A wrapper of ``pytest`` command to run code coverage test.

        Run:

        .. code-block:: bash

            pytest -s --tb=native --rootdir=/path/to/project/root --cov=package_name --cov-report term-missing --cov-report html:/path/to/htmlcov tests
        """
        flag = self._do_we_run_test(self.dir_tests)
        if not flag:  # pragma: no cover
            raise RuntimeError(f"{Emoji.red_circle} coverage test not run!")
        args = [
            f"{self.path_venv_bin_pytest}",
            "-s",
            "--tb=native",
            f"--rootdir={self.dir_project_root}",
            f"--cov={self.package_name}",
            "--cov-report",
            "term-missing",
            "--cov-report",
            f"html:{self.dir_htmlcov}",
            f"{self.dir_tests}",
        ]
        if quiet:
            args.append("--quiet")
        self.run_command(args, real_run)

    def run_cov_test(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):  # pragma: no cover
        with logger.disabled(not verbose):
            return self._run_cov_test(
                real_run=real_run,
                quiet=not verbose,
            )

    run_cov_test.__doc__ = _run_cov_test.__doc__

    @logger.emoji_block(
        msg="View Code Coverage Test Result",
        emoji=Emoji.test,
    )
    def _view_cov(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        View coverage test output html file locally in web browser.

        It is usually at the ``${dir_project_root}/htmlcov/index.html``

        .. code-block:: bash

            # For MacOS / Linux
            open htmlcov/index.html
            # For Windows
            start htmlcov/index.html
        """
        args = [OPEN_COMMAND, f"{self.path_htmlcov_index_html}"]
        if real_run:  # pragma: no cover
            subprocess.run(args)

    def view_cov(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):  # pragma: no cover
        with logger.disabled(not verbose):
            return self._view_cov(
                real_run=real_run,
                quiet=not verbose,
            )

    view_cov.__doc__ = _view_cov.__doc__

    @logger.emoji_block(
        msg="Run Integration Tests",
        emoji=Emoji.test,
    )
    def _run_int_test(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):  # pragma: no cover
        """
        A wrapper of ``pytest`` command to run integration test.

        Run:

        .. code-block:: bash

            pytest tests_int -s --rootdir=/path/to/project/root
        """
        flag = self._do_we_run_test(self.dir_tests_int)
        if not flag:  # pragma: no cover
            raise RuntimeError(f"{Emoji.red_circle} integration test not run!")
        args = [
            f"{self.path_venv_bin_pytest}",
            f"{self.dir_tests_int}",
            "-s",
            f"--rootdir={self.dir_project_root}",
        ]
        if quiet:
            args.append("--quiet")
        self.run_command(args, real_run)

    def run_int_test(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):  # pragma: no cover
        with logger.disabled(not verbose):
            return self._run_int_test(
                real_run=real_run,
                quiet=not verbose,
            )

    run_int_test.__doc__ = _run_int_test.__doc__

    @logger.emoji_block(
        msg="Run Load Test",
        emoji=Emoji.test,
    )
    def _run_load_test(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):  # pragma: no cover
        """
        A wrapper of ``pytest`` command to run load test.

        Run:

        .. code-block:: bash

            pytest tests_load -s --rootdir=/path/to/project/root
        """
        flag = self._do_we_run_test(self.dir_tests_load)
        if not flag:  # pragma: no cover
            raise RuntimeError(f"{Emoji.red_circle} load test not run!")
        args = [
            f"{self.path_venv_bin_pytest}",
            f"{self.dir_tests_load}",
            "-s",
            f"--rootdir={self.dir_project_root}",
        ]
        if quiet:
            args.append("--quiet")
        self.run_command(args, real_run)

    def run_load_test(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):  # pragma: no cover
        with logger.disabled(not verbose):
            return self._run_load_test(
                real_run=real_run,
                quiet=not verbose,
            )

    run_load_test.__doc__ = _run_load_test.__doc__
