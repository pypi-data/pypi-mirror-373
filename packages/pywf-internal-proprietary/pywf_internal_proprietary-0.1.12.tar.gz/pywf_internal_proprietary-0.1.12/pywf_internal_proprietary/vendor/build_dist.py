# -*- coding: utf-8 -*-

"""
Build Python source distribution.

Usage example:

.. code-block:: python

    from build_dist import build_dist_with_python_build, build_dist_with_poetry_build
"""

import typing as T
import os
import contextlib
import subprocess
from pathlib import Path

__version__ = "0.1.1"


@contextlib.contextmanager
def temp_cwd(path: T.Union[str, Path]):
    """
    Temporarily set the current directory to target path.
    """
    path = Path(path).absolute()
    if not path.is_dir():
        raise ValueError(f"{path} is not a dir!")

    cwd = os.getcwd()
    os.chdir(f"{path}")
    try:
        yield path
    finally:
        os.chdir(cwd)


def build_dist_with_python_build(
    dir_project_root: T.Union[str, Path],
    path_bin_python: T.Union[str, Path],
    log_func: T.Callable = print,
    real_run: bool = True,
    verbose: bool = True,
):
    """
    Build the source distribution with ``python-build``.

    :param dir_project_root: the root directory of your project, it should have
        a setup.py or pyproject.toml file
    :param path_bin_python: the path to python executable, usually the
        virtualenv python
    :param verbose: show verbose output or not

    Reference: https://pypa-build.readthedocs.io/en/latest/
    """
    dir_project_root = Path(dir_project_root).absolute()
    path_bin_python = Path(path_bin_python).absolute()
    with temp_cwd(dir_project_root):
        args = [
            f"{path_bin_python}",
            "-m",
            "build",
            "--sdist",
            "--wheel",
        ]
        log_func("run command: {}".format(" ".join(args)))
        if real_run:
            subprocess.run(args, check=True, capture_output=not verbose)


def build_dist_with_poetry_build(
    dir_project_root: T.Union[str, Path],
    path_bin_poetry: T.Union[str, Path],
    log_func: T.Callable = print,
    real_run: bool = True,
    verbose: bool = True,
):
    """
    Build the source distribution with ``poetry build`` command.

    :param dir_project_root: the root directory of your project, it should have
        a setup.py or pyproject.toml file
    :param path_bin_poetry: the path to poetry executable, could be simply "poetry"
    :param verbose: show verbose output or not

    Reference: https://python-poetry.org/docs/cli/#build
    """
    dir_project_root = Path(dir_project_root).absolute()
    path_bin_poetry = Path(path_bin_poetry)  # poetry could be a global command
    with temp_cwd(dir_project_root):
        args = [
            f"{path_bin_poetry}",
            "build",
        ]
        if verbose is False:
            args.append("--quiet")
        log_func("run command: {}".format(" ".join(args)))
        if real_run:
            subprocess.run(args, check=True)
