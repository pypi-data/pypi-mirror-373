# -*- coding: utf-8 -*-

"""
Enumeration of important paths on local file system.
"""

import typing as T
import sys
import subprocess
import dataclasses
from pathlib import Path
from functools import cached_property

from .helpers import print_command
from .logger import logger
from .runtime import IS_CI

if T.TYPE_CHECKING:  # pragma: no cover
    from .define import PyWf


@dataclasses.dataclass
class PyWfPaths:
    """
    Namespace class for accessing important paths.
    """
    def run_command(
        self: "PyWf",
        args: list[str],
        real_run: bool,
        cwd: T.Optional[Path] = None,
        check: bool = True,
    ):
        """
        Run a command in a subprocess, also print the command for debug,
        and optionally change the current working directory.

        :param args: The command and its arguments to run.
        :param real_run: If True, actually run the command; if False, just print it.
        :param cwd: The directory to change to before running the command.
        :param check: If True, raise an exception if the command fails.
        """
        if cwd is None:
            cwd = self.dir_project_root
        logger.info(f"cd to: {cwd}")
        print_command(args)
        if real_run is True:
            return subprocess.run(args, cwd=cwd, check=check)

    @cached_property
    def dir_home(self: "PyWf") -> Path:
        """
        The user home directory.

        Example: ``${HOME}``
        """
        return Path.home()

    # --------------------------------------------------------------------------
    # Virtualenv
    # --------------------------------------------------------------------------
    _VENV_RELATED = None

    @property
    def dir_venv(self: "PyWf") -> Path:
        """
        The virtualenv directory.

        Example: ``${dir_project_root}/.venv``
        """
        return self.dir_project_root.joinpath(".venv")

    @property
    def dir_venv_bin(self: "PyWf") -> Path:
        """
        The bin folder in virtualenv.

        Example: ``${dir_project_root}/.venv/bin``
        """
        return self.dir_venv.joinpath("bin")

    def get_path_venv_bin_cli(self, cmd: str) -> Path:
        """
        Get the path of a command in virtualenv bin folder.

        Example: ``${dir_project_root}/.venv/bin/${cmd}``
        """
        return self.dir_venv_bin.joinpath(cmd)

    @property
    def path_venv_bin_python(self: "PyWf") -> Path:
        """
        The python executable in virtualenv.

        Example: ``${dir_project_root}/.venv/bin/python``
        """
        return self.get_path_venv_bin_cli("python")

    @property
    def path_venv_bin_pip(self: "PyWf") -> Path:
        """
        The pip command in virtualenv.

        Example: ``${dir_project_root}/.venv/bin/pip``
        """
        return self.get_path_venv_bin_cli("pip")

    @property
    def path_venv_bin_pytest(self: "PyWf") -> Path:
        """
        The pytest command in virtualenv.

        Example: ``${dir_project_root}/.venv/bin/pytest``
        """
        return self.get_path_venv_bin_cli("pytest")

    @property
    def path_venv_bin_sphinx_build(self: "PyWf") -> Path:
        """
        The sphinx-build executable in virtualenv.

        Example: ``${dir_project_root}/.venv/bin/sphinx-build``
        """
        return self.get_path_venv_bin_cli("sphinx-build")

    @property
    def path_venv_bin_bin_jupyter(self: "PyWf") -> Path:
        """
        The jupyter executable in virtualenv.

        Example: ``${dir_project_root}/.venv/bin/jupyter``
        """
        return self.get_path_venv_bin_cli("jupyter")

    @property
    def path_sys_executable(self: "PyWf") -> Path:
        """
        The current Python interpreter path.
        """
        return Path(sys.executable)

    def get_path_dynamic_bin_cli(self, cmd: str) -> Path:
        """
        Search multiple locations to get the absolute path of the CLI command.
        It searches the following locations in order:

        1. the bin folder in virtualenv.
        2. the global Python's bin folder.
        3. Then use the raw command name (string) as the path.

        Example: ``${dir_project_root}/.venv/bin/${cmd}`` or ``${global_python_bin}/${cmd}``
        """
        p = self.dir_venv_bin.joinpath(cmd)
        if p.exists():
            return p
        p = self.path_sys_executable.parent.joinpath(cmd)
        if p.exists():
            return p
        return Path(cmd)

    @property
    def path_bin_virtualenv(self: "PyWf") -> Path:
        """
        The virtualenv CLI command path.

        Example: ``${dir_project_root}/.venv/bin/virtualenv``
        """
        return self.get_path_dynamic_bin_cli("virtualenv")

    @property
    def path_bin_poetry(self: "PyWf") -> Path:
        """
        The poetry CLI command path.

        Example: ``${dir_project_root}/.venv/bin/poetry``
        """
        return self.get_path_dynamic_bin_cli("poetry")

    @property
    def path_bin_uv(self: "PyWf") -> Path:
        """
        The poetry CLI command path.

        Example: ``${dir_project_root}/.venv/bin/uv``
        """
        return self.get_path_dynamic_bin_cli("uv")

    @property
    def path_bin_twine(self: "PyWf") -> Path:
        """
        The twine CLI command path.

        Example: ``${dir_project_root}/.venv/bin/twine``
        """
        return self.get_path_dynamic_bin_cli("twine")

    # --------------------------------------------------------------------------
    # Source code
    # --------------------------------------------------------------------------
    @property
    def dir_python_lib(self: "PyWf") -> Path:
        """
        The current Python library directory.

        Example: ``${dir_project_root}/${package_name}``
        """
        return self.dir_project_root.joinpath(self.package_name)

    @property
    def path_version_py(self: "PyWf") -> Path:
        """
        Path to the ``_version.py`` file where the package version is defined.

        Example: ``${dir_project_root}/${package_name}/_version.py``
        """
        return self.dir_python_lib.joinpath("_version.py")

    # --------------------------------------------------------------------------
    # Pytest
    # --------------------------------------------------------------------------
    _PYTEST_RELATED = None

    @property
    def dir_tests(self: "PyWf") -> Path:
        """
        Unit test folder.

        Example: ``${dir_project_root}/tests``
        """
        return self.dir_project_root.joinpath("tests")

    @property
    def dir_tests_int(self: "PyWf") -> Path:
        """
        Integration test folder.

        Example: ``${dir_project_root}/tests_int``
        """
        return self.dir_project_root.joinpath("tests_int")

    @property
    def dir_tests_load(self: "PyWf") -> Path:
        """
        Load test folder.

        Example: ``${dir_project_root}/tests_load``
        """
        return self.dir_project_root.joinpath("tests_load")

    @property
    def dir_htmlcov(self: "PyWf") -> Path:
        """
        The code coverage test results HTML output folder.

        Example: ``${dir_project_root}/htmlcov``
        """
        return self.dir_project_root.joinpath("htmlcov")

    @property
    def path_htmlcov_index_html(self: "PyWf") -> Path:
        """
        The code coverage test results HTML file.

        Example: ``${dir_project_root}/htmlcov/index.html``
        """
        return self.dir_htmlcov.joinpath("index.html")

    # --------------------------------------------------------------------------
    # Sphinx doc
    # --------------------------------------------------------------------------
    _SPHINX_DOC_RELATED = None

    @property
    def dir_sphinx_doc(self: "PyWf") -> Path:
        """
        Sphinx docs folder.

        Example: ``${dir_project_root}/docs``
        """
        return self.dir_project_root.joinpath("docs")

    @property
    def dir_sphinx_doc_source(self: "PyWf") -> Path:
        """
        Sphinx docs source code folder.

        Example: ``${dir_project_root}/docs/source``
        """
        return self.dir_sphinx_doc.joinpath("source")

    @property
    def dir_sphinx_doc_source_conf_py(self: "PyWf") -> Path:
        """
        Sphinx docs ``conf.py`` file path.

        Example: ``${dir_project_root}/docs/source/conf.py``
        """
        return self.dir_sphinx_doc_source.joinpath("conf.py")

    @property
    def dir_sphinx_doc_source_python_lib(self: "PyWf") -> Path:
        """
        The generated Python library API reference Sphinx docs folder.

        Example: ``${dir_project_root}/docs/source/${package_name}``
        """
        return self.dir_sphinx_doc_source.joinpath(self.package_name)

    @property
    def dir_sphinx_doc_build(self: "PyWf") -> Path:
        """
        The temp Sphinx doc build folder.

        Example: ``${dir_project_root}/docs/build
        """
        return self.dir_sphinx_doc.joinpath("build")

    @property
    def dir_sphinx_doc_build_html(self: "PyWf") -> Path:
        """
        The built Sphinx doc build HTML folder.

        Example: ``${dir_project_root}/docs/build/html
        """
        return self.dir_sphinx_doc_build.joinpath("html")

    @property
    def path_sphinx_doc_build_index_html(self: "PyWf") -> Path:  # pragma: no cover
        """
        The built Sphinx doc site entry HTML file path.

        Example: ``${dir_project_root}/docs/build/html/index.html or README.html
        """
        if self.dir_sphinx_doc_source.joinpath("index.rst").exists():
            return self.dir_sphinx_doc_build_html.joinpath("index.html")

        if self.dir_sphinx_doc_source.joinpath("README.rst").exists():
            return self.dir_sphinx_doc_build_html.joinpath("README.html")

        raise FileNotFoundError(
            str(self.dir_sphinx_doc_build_html.joinpath("index.html"))
        )

    # --------------------------------------------------------------------------
    # Poetry
    # --------------------------------------------------------------------------
    _POETRY_RELATED = None

    @property
    def path_requirements(self: "PyWf") -> Path:
        """
        The requirements.txt file path.

        Example: ``${dir_project_root}/requirements.txt``
        """
        return self.dir_project_root.joinpath("requirements.txt")

    @property
    def path_requirements_dev(self: "PyWf") -> Path:
        """
        The requirements-dev.txt file path.

        Example: ``${dir_project_root}/requirements-dev.txt``
        """
        return self.dir_project_root.joinpath("requirements-dev.txt")

    @property
    def path_requirements_test(self: "PyWf") -> Path:
        """
        The requirements-test.txt file path.

        Example: ``${dir_project_root}/requirements-test.txt``
        """
        return self.dir_project_root.joinpath("requirements-test.txt")

    @property
    def path_requirements_doc(self: "PyWf") -> Path:
        """
        The requirements-doc.txt file path.

        Example: ``${dir_project_root}/requirements-doc.txt``
        """
        return self.dir_project_root.joinpath("requirements-doc.txt")

    @property
    def path_requirements_automation(self: "PyWf") -> Path:
        """
        The requirements-automation.txt file path.

        Example: ``${dir_project_root}/requirements-automation.txt``
        """
        return self.dir_project_root.joinpath("requirements-automation.txt")

    @property
    def path_poetry_lock(self: "PyWf") -> Path:
        """
        The poetry.lock file path.

        Example: ``${dir_project_root}/poetry.lock``
        """
        return self.dir_project_root.joinpath("poetry.lock")

    @property
    def path_poetry_lock_hash_json(self: "PyWf") -> Path:
        """
        The poetry-lock-hash.json file path. It is the cache of the poetry.lock file hash.

        Example: ``${dir_project_root}/poetry-lock-hash.json``
        """
        return self.dir_project_root.joinpath("poetry-lock-hash.json")

    # ------------------------------------------------------------------------------
    # Build Related
    # ------------------------------------------------------------------------------
    _BUILD_RELATED = None

    @property
    def path_pyproject_toml(self: "PyWf") -> Path:
        """
        The pyproject.toml file path.

        Example: ``${dir_project_root}/pyproject.toml``
        """
        return self.dir_project_root.joinpath("pyproject.toml")

    @property
    def dir_build(self: "PyWf") -> Path:
        """
        The build folder for Python or artifacts build.

        Example: ``${dir_project_root}/build``
        """
        return self.dir_project_root.joinpath("build")

    @property
    def dir_dist(self: "PyWf") -> Path:
        """
        The dist folder for Python package distribution (.whl file).

        Example: ``${dir_project_root}/dist``
        """
        return self.dir_project_root.joinpath("dist")

    # --------------------------------------------------------------------------
    # AWS Related
    # --------------------------------------------------------------------------
    _AWS_RELATED = None

    @property
    def path_bin_aws(self: "PyWf") -> Path:
        """
        The AWS CLI executable path.

        Example: ``${dir_project_root}/.venv/bin/aws``
        """
        return self.get_path_dynamic_bin_cli("aws")

    # --------------------------------------------------------------------------
    # Cloudflare
    # --------------------------------------------------------------------------
    _CLOUDFLARE_RELATED = None

    @property
    def dir_node_modules(self: "PyWf") -> Path:
        """
        """
        return self.dir_home.joinpath(".npm-tools", "node_modules")

    @property
    def path_bin_wrangler(self: "PyWf") -> Path:
        """
        The `Cloudflare wrangler <https://developers.cloudflare.com/workers/wrangler/install-and-update/>`_
        CLI command path.
        
        Suggestion:
        
        .. code-block:: bash
        
            mkdir ${HOME}/.npm-tools
            cd ${HOME}/.npm-tools
            npm install wrangler --save-dev
        """
        if IS_CI:
            return Path("wrangler")
        else:
            return self.dir_node_modules.joinpath(".bin", "wrangler")
