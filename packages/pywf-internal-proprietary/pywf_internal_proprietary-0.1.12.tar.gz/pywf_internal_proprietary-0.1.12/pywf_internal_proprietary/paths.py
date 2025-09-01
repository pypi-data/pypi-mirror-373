# -*- coding: utf-8 -*-

from pathlib import Path

dir_here = Path(__file__).absolute().parent

# ------------------------------------------------------------------------------
# Python Package Source Code
# ------------------------------------------------------------------------------
dir_package = dir_here
PACKAGE_NAME = dir_here.name
path_version_py = dir_package / "_version.py"

# ------------------------------------------------------------------------------
# Git Repo Directory
# ------------------------------------------------------------------------------
dir_project_root = dir_package.parent
path_pyproject_toml = dir_project_root / "pyproject.toml"

# ------------------------------------------------------------------------------
# Virtual Environment Related
# ------------------------------------------------------------------------------
dir_venv = dir_project_root / ".venv"
dir_venv_bin = dir_venv / "bin"

bin_python = dir_venv_bin / "python"
bin_pip = dir_venv_bin / "pip"
bin_pytest = dir_venv_bin / "pytest"

# ------------------------------------------------------------------------------
# Test Related
# ------------------------------------------------------------------------------
dir_unit_test = dir_project_root / "tests"
dir_int_test = dir_project_root / "tests_int"
dir_load_test = dir_project_root / "tests_load"
dir_htmlcov = dir_project_root / "htmlcov"
path_cov_index_html = dir_htmlcov / "index.html"
