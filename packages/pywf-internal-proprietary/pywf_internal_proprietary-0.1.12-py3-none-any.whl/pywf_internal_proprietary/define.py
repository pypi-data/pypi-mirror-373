# -*- coding: utf-8 -*-

"""
Comprehensive Automation Namespace for Python Project Operations

This module provides a unified interface for managing various aspects of a Python project
lifecycle, including virtual environment, dependencies, testing, documentation,
build, and publishing processes.

The PyWf (Python Workflow) class consolidates multiple operational concerns into a
single, cohesive management system, enabling streamlined project automation.

The class uses a composition-based approach, inheriting from multiple specialized
namespace classes to provide a comprehensive project management toolkit.
"""

import typing as T
import os

try:
    import tomllib
except ImportError:  # pragma: no cover
    import toml as tomllib
import dataclasses
from pathlib import Path
from functools import cached_property

from .vendor.home_secret import hs

from .runtime import IS_CI

from .define_01_paths import PyWfPaths
from .define_02_venv import PyWfVenv
from .define_03_deps import PyWfDeps
from .define_04_tests import PyWfTests
from .define_05_docs import PyWfDocs
from .define_06_build import PyWfBuild
from .define_07_publish import PyWfPublish
from .define_08_saas import PyWfSaas
from .define_09_aws import PyWfAws
from .define_10_cloudflare import PyWfCloudflare


@dataclasses.dataclass
class PyWf(
    PyWfPaths,
    PyWfVenv,
    PyWfDeps,
    PyWfTests,
    PyWfDocs,
    PyWfBuild,
    PyWfPublish,
    PyWfSaas,
    PyWfAws,
    PyWfCloudflare,
):
    """
    Unified Automation Interface for Python Project Management

    :param dir_project_root: Root directory of the project, typically the git
        repository root. It has to have a ``pyproject.toml`` file in it.
    :param toml_data: Parsed configuration data from ``pyproject.toml``
    """

    dir_project_root: Path = dataclasses.field()
    toml_data: T.Dict[str, T.Any] = dataclasses.field()

    # --------------------------------------------------------------------------
    # [project] Configuration Properties
    # --------------------------------------------------------------------------
    @property
    def package_name(self) -> str:
        """Retrieve the package name from pyproject.toml."""
        return self.toml_data["project"]["name"]

    @property
    def package_name_slug(self) -> str:
        """Slugify package name for use in PyPI, readthedocs, etc."""
        return self.package_name.replace("_", "-")

    @property
    def package_version(self) -> str:
        """Retrieve the package version from pyproject.toml."""
        return self.toml_data["project"]["version"]

    @property
    def package_license(self) -> str:
        """Retrieve the package license from pyproject.toml."""
        return self.toml_data["project"]["license"]

    @property
    def package_description(self) -> str:
        """Retrieve the package description from pyproject.toml."""
        return self.toml_data["project"]["description"]

    @property
    def package_author_name(self) -> str:
        """Retrieve the primary author's name from pyproject.toml."""
        return self.toml_data["project"]["authors"][0]["name"]

    @property
    def package_author_email(self) -> str:
        """Retrieve the primary author's email from pyproject.toml."""
        return self.toml_data["project"]["authors"][0]["email"]

    @property
    def package_maintainer_name(self) -> str:
        """Retrieve the primary maintainer's name from pyproject.toml."""
        return self.toml_data["project"]["maintainers"][0]["name"]

    @property
    def package_maintainer_email(self) -> str:
        """Retrieve the primary maintainer's email from pyproject.toml."""
        return self.toml_data["project"]["maintainers"][0]["email"]

    # --------------------------------------------------------------------------
    # [tool.pywf] Configuration Properties
    # --------------------------------------------------------------------------
    @property
    def py_ver_major(self) -> int:
        """Extract major version number from development Python version."""
        return int(self.toml_data["tool"]["pywf"]["dev_python"].split(".")[0])

    @property
    def py_ver_minor(self) -> int:
        """Extract minor version number from development Python version."""
        return int(self.toml_data["tool"]["pywf"]["dev_python"].split(".")[1])

    @property
    def py_ver_micro(self) -> int:
        """Extract micro version number from development Python version."""
        return int(self.toml_data["tool"]["pywf"]["dev_python"].split(".")[2])

    # --- GitHub.com
    @property
    def github_account(self) -> str:
        return self.toml_data["tool"]["pywf"]["github_account"]

    @property
    def github_token_field(self) -> str:
        return self.toml_data["tool"]["pywf"]["github_token_field"]

    @cached_property
    def github_token(self: "PyWf") -> str:  # pragma: no cover
        return hs.v(self.github_token_field)

    @property
    def git_repo_name(self) -> str:
        """
        Git repo name.
        """
        return self.dir_project_root.name

    @property
    def github_repo_fullname(self) -> str:
        return f"{self.github_account}/{self.git_repo_name}"

    @property
    def github_repo_url(self) -> str:
        return f"https://github.com/{self.github_repo_fullname}"

    @property
    def github_actions_secrets_settings_url(self) -> str:
        return f"{self.github_repo_url}/settings/secrets/actions"

    @property
    def github_versioned_release_url(self) -> str:
        return f"{self.github_repo_url}/releases/tag/{self.package_version}"

    # --- codecov.io
    @property
    def codecov_account(self) -> str:
        return self.toml_data["tool"]["pywf"]["codecov_account"]

    @property
    def codecov_token_field(self) -> str:
        return self.toml_data["tool"]["pywf"]["codecov_token_field"]

    @cached_property
    def codecov_token(self) -> str:  # pragma: no cover
        return hs.v(self.codecov_token_field)

    # --- AWS
    @property
    def aws_region(self) -> str:
        return self.toml_data["tool"]["pywf"]["aws_region"]

    @property
    def aws_codeartifact_profile(self) -> str:
        return self.toml_data["tool"]["pywf"]["aws_codeartifact_profile"]

    @property
    def aws_codeartifact_domain(self) -> str:
        return self.toml_data["tool"]["pywf"]["aws_codeartifact_domain"]

    @property
    def aws_codeartifact_repository(self) -> str:
        return self.toml_data["tool"]["pywf"]["aws_codeartifact_repository"]

    @property
    def doc_host_aws_profile(self) -> str:
        """Retrieve AWS profile for documentation hosting."""
        return self.toml_data["tool"]["pywf"]["doc_host_aws_profile"]

    @property
    def doc_host_s3_bucket(self) -> str:
        """Retrieve S3 bucket for documentation hosting."""
        return self.toml_data["tool"]["pywf"]["doc_host_s3_bucket"]

    # --- cloudflare
    @property
    def cloudflare_token_field(self) -> str:
        return self.toml_data["tool"]["pywf"]["cloudflare_token_field"]

    @cached_property
    def cloudflare_token(self) -> str:  # pragma: no cover
        if IS_CI:
            return os.environ["CLOUDFLARE_API_TOKEN"]
        else:
            return hs.v(self.cloudflare_token_field)

    @property
    def devops_aws_account_id(self) -> str:
        """
        The devops AWS Account ID extracted from AWS CodeArtifact PyPI endpoint URL.
        """
        url = self.toml_data["tool"]["poetry"]["source"][0]["url"]
        devops_aws_account_id = url.split("/")[2].split(".")[0].split("-")[-1]
        # print(devops_aws_account_id)  # for debug only
        return devops_aws_account_id

    def _validate_paths(self):
        """
        Validate project root directory and package structure.

        Checks:

        - Verify presence of ``pyproject.toml``
        - Confirm ``package/__init__.py`` exists
        """
        if isinstance(self.dir_project_root, Path) is False:  # pragma: no cover
            self.dir_project_root = Path(self.dir_project_root)

        if (
            self.dir_project_root.joinpath("pyproject.toml").exists() is False
        ):  # pragma: no cover
            raise ValueError(
                f"{self.dir_project_root} does not have a pyproject.toml file! "
                f"it might not be a valid project root directory."
            )
        dir_python_lib = self.dir_project_root.joinpath(self.package_name)
        if dir_python_lib.joinpath("__init__.py").exists() is False:  # pragma: no cover
            raise ValueError(
                f"{dir_python_lib} does not have a __init__.py file, "
                f"the package name {self.package_name} might be invalid."
            )

    def _validate_python_version(self):
        """
        Validate the Python version used in the project.
        """
        if self.py_ver_major != 3:  # pragma: no cover
            raise ValueError(
                f"Python major version has to be 3, but got {self.py_ver_major}."
            )
        if self.py_ver_minor < 11:  # pragma: no cover
            raise ValueError(
                f"PyWf tool only support Python3.11+, but got {self.py_ver_major}.{self.py_ver_minor}"
            )

    def _update_version_file(self):
        """
        Update the version file with current project metadata in ``pyproject.toml``.
        """
        dir_here = Path(__file__).absolute().parent
        path_version_tpl = dir_here / "_version.tpl"
        content = path_version_tpl.read_text(encoding="utf-8").format(
            version=self.package_version,
            description=self.package_description,
            license=self.package_license,
            author=self.package_author_name,
            author_email=self.package_author_email,
            maintainer=self.package_maintainer_name,
            maintainer_email=self.package_maintainer_email,
        )
        self.path_version_py.write_text(content, encoding="utf-8")

    def __post_init__(self):
        self._validate_paths()
        self._validate_python_version()
        self._update_version_file()

    @classmethod
    def from_pyproject_toml(
        cls,
        path_pyproject_toml: Path,
    ):
        """
        Create a :class:`PyWf` instance from a pyproject.toml file.
        """
        path_pyproject_toml = Path(path_pyproject_toml)
        toml_data = tomllib.loads(path_pyproject_toml.read_text(encoding="utf-8"))
        return cls(
            dir_project_root=path_pyproject_toml.parent,
            toml_data=toml_data,
        )
