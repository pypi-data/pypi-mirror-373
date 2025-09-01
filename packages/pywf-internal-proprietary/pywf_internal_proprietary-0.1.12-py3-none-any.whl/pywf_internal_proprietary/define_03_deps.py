# -*- coding: utf-8 -*-

"""
Dependency Management Automation for Python Projects.

This module provides comprehensive automation for managing project dependencies
using `Poetry <<https://python-poetry.org/>`_, including locking, installation,
and export ``requirements.txt`` functionalities.
"""

import typing as T
import json
import dataclasses
from pathlib import Path

from .vendor.emoji import Emoji

from .logger import logger
from .helpers import sha256_of_bytes


if T.TYPE_CHECKING:  # pragma: no cover
    from .define import PyWf


@dataclasses.dataclass
class PyWfDeps:
    """
    Namespace class for managing project dependencies using Poetry.
    """

    def _run_poetry_command(
        self: "PyWf",
        args: T.List[str],
        real_run: bool,
        quiet: bool,
    ):
        args = [f"{self.path_bin_poetry}", *args]
        if quiet:
            args.append("--quiet")
        self.run_command(args, real_run)

    @logger.emoji_block(
        msg="Resolve Dependencies Tree",
        emoji=Emoji.install,
    )
    def _poetry_lock(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Lock project dependencies defined in pyproject.toml.

        Resolves and writes exact dependency versions to ``poetry.lock`` file.
        This ensures reproducible builds across different environments.
        You have to run this everytime you changed the ``pyproject.toml`` file.
        And you should commit the latest ``poetry.lock`` file to git.

        Run:

        .. code-block:: bash

            poetry lock

        Ref:

        - poetry lock: https://python-poetry.org/docs/cli/#lock
        """
        return self._run_poetry_command(
            args=["lock"],
            real_run=real_run,
            quiet=quiet,
        )

    def poetry_lock(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            return self._poetry_lock(
                real_run=real_run,
                quiet=not verbose,
            )

    poetry_lock.__doc__ = _poetry_lock.__doc__

    @logger.emoji_block(
        msg="Install package source code without any dependencies",
        emoji=Emoji.install,
    )
    def _poetry_install_only_root(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Install only the package source code in editable mode.

        Skips installing any external dependencies, useful for development
        and testing package structure.

        Run:

        .. code-block:: bash

            poetry install --only-root

        Ref:

        - poetry install: https://python-poetry.org/docs/cli/#install
        """
        return self._run_poetry_command(
            args=["install", "--only-root"],
            real_run=real_run,
            quiet=quiet,
        )

    def poetry_install_only_root(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            return self._poetry_install_only_root(
                real_run=real_run,
                quiet=not verbose,
            )

    poetry_install_only_root.__doc__ = _poetry_install_only_root.__doc__

    @logger.emoji_block(
        msg="Install main dependencies and Package itself",
        emoji=Emoji.install,
    )
    def _poetry_install(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Install main dependencies and the package in editable mode.

        Installs core project dependencies without development or optional groups.

        Run:

        .. code-block:: bash

            poetry install

        Ref:

        - poetry install: https://python-poetry.org/docs/cli/#install
        """
        return self._run_poetry_command(
            args=["install"],
            real_run=real_run,
            quiet=quiet,
        )

    def poetry_install(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            return self._poetry_install(
                real_run=real_run,
                quiet=not verbose,
            )

    poetry_install.__doc__ = _poetry_install.__doc__

    @logger.emoji_block(
        msg="Install dev dependencies",
        emoji=Emoji.install,
    )
    def _poetry_install_dev(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Install development dependencies. Adds dependencies from the
        ``[tool.poetry.group.dev.dependencies]`` group to the project environment.

        Run:

        .. code-block:: bash

            poetry install --extras dev

        Ref:

        - poetry install: https://python-poetry.org/docs/cli/#install
        """
        return self._run_poetry_command(
            args=["install", "--extras", "dev"],
            real_run=real_run,
            quiet=quiet,
        )

    def poetry_install_dev(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            return self._poetry_install_dev(
                real_run=real_run,
                quiet=not verbose,
            )

    poetry_install_dev.__doc__ = _poetry_install_dev.__doc__

    @logger.emoji_block(
        msg="Install test dependencies",
        emoji=Emoji.install,
    )
    def _poetry_install_test(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Install test dependencies. Adds dependencies from the
        ``[tool.poetry.group.test.dependencies]`` group to the project environment.

        Run:

        .. code-block:: bash

            poetry install --extras test

        Ref:

        - poetry install: https://python-poetry.org/docs/cli/#install
        """
        return self._run_poetry_command(
            args=["install", "--extras", "test"],
            real_run=real_run,
            quiet=quiet,
        )

    def poetry_install_test(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            return self._poetry_install_test(
                real_run=real_run,
                quiet=not verbose,
            )

    poetry_install_test.__doc__ = _poetry_install_test.__doc__

    @logger.emoji_block(
        msg="Install doc dependencies",
        emoji=Emoji.install,
    )
    def _poetry_install_doc(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Install documentation build dependencies. Adds dependencies from the
        ``[tool.poetry.group.doc.dependencies]`` group to the project environment.

        Run:

        .. code-block:: bash

            poetry install --extras doc

        Ref:

        - poetry install: https://python-poetry.org/docs/cli/#install
        """
        return self._run_poetry_command(
            args=["install", "--extras", "doc"],
            real_run=real_run,
            quiet=quiet,
        )

    def poetry_install_doc(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            return self._poetry_install_doc(
                real_run=real_run,
                quiet=not verbose,
            )

    poetry_install_doc.__doc__ = _poetry_install_doc.__doc__

    @logger.emoji_block(
        msg="Install automation dependencies",
        emoji=Emoji.install,
    )
    def _poetry_install_auto(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Install automation dependencies. Adds dependencies from the
        ``[tool.poetry.group.auto.dependencies]`` group to the project environment.

        Run:

        .. code-block:: bash

            poetry install --extras auto

        Ref:

        - poetry install: https://python-poetry.org/docs/cli/#install
        """
        return self._run_poetry_command(
            args=["install", "--extras", "auto"],
            real_run=real_run,
            quiet=quiet,
        )

    def poetry_install_auto(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            return self._poetry_install_auto(
                real_run=real_run,
                quiet=not verbose,
            )

    poetry_install_auto.__doc__ = _poetry_install_auto.__doc__

    @logger.emoji_block(
        msg="Install all dependencies for dev, test, doc",
        emoji=Emoji.install,
    )
    def _poetry_install_all(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Install all dependency groups.

        Adds dependencies from all configured groups to the project environment.

        Run:

        .. code-block:: bash

            poetry install --all-extras

        Ref:

        - poetry install: https://python-poetry.org/docs/cli/#install
        """
        return self._run_poetry_command(
            args=["install", "--all-extras"],
            real_run=real_run,
            quiet=quiet,
        )

    def poetry_install_all(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            return self._poetry_install_all(
                real_run=real_run,
                quiet=not verbose,
            )

    poetry_install_all.__doc__ = _poetry_install_all.__doc__

    def _do_we_need_poetry_export(
        self: "PyWf",
        current_poetry_lock_hash: str,
    ) -> bool:
        """
        The ``poetry export`` command is resource-intensive, so we use a
        caching mechanism to avoid unnecessary executions.

        Each time we run :meth:`PyWfDeps._poetry_export`, it calculates the
        SHA-256 hash of the current ``poetry.lock`` file and writes it to
        a cache file named ``poetry-lock-hash.json``, located at the root of the repository.

        Before exporting, the function compares the current hash of ``poetry.lock``
        with the value stored in the cache file. If the hashes differ, it indicates
        that ``poetry.lock`` has changed, and we should run :meth:`PyWfDeps._poetry_export` again.

        An example of the ``poetry-lock-hash.json`` file content::

            {
                "hash": "sha256-hash-of-the-poetry.lock-file",
                "description": "DON'T edit this file manually!"
            }

        Ref:

        - poetry export: https://python-poetry.org/docs/cli/#export

        :param current_poetry_lock_hash: the sha256 hash of the current ``poetry.lock`` file
        """
        if self.path_poetry_lock_hash_json.exists():
            # read the previous poetry lock hash from cache file
            cached_poetry_lock_hash = json.loads(
                self.path_poetry_lock_hash_json.read_text()
            )["hash"]
            return current_poetry_lock_hash != cached_poetry_lock_hash
        else:
            # do poetry export if the cache file not found
            return True

    def _poetry_export_main(
        self: "PyWf",
        with_hash: bool = False,
        real_run: bool = True,
    ):
        """
        Export main project dependencies to ``requirements.txt``.

        :param with_hash: whether to include the hash of the dependencies in the
            requirements.txt file.
        """
        self.path_requirements.unlink(missing_ok=True)
        args = [
            f"{self.path_bin_poetry}",
            "export",
            "--format",
            "requirements.txt",
            "--output",
            f"{self.path_requirements}",
        ]
        if with_hash is False:
            args.append("--without-hashes")
        self.run_command(args, real_run)

    def _poetry_export_group(
        self: "PyWf",
        group: str,
        path: Path,
        with_hash: bool = False,
        real_run: bool = True,
    ):
        """
        Export specific dependency group to ``requirements-{group}.txt``.

        Ref: https://github.com/python-poetry/poetry-plugin-export

        :param group: dependency group name, for example dev dependencies are defined
            in the ``[tool.poetry.group.dev]`` and ``[tool.poetry.group.dev.dependencies]``
            sections of he ``pyproject.toml`` file.
        :param path: the path to the exported ``requirements.txt`` file.
        :param with_hash: whether to include the hash of the dependencies in the
            ``requirements.txt`` file.
        """
        if real_run:
            path.unlink(missing_ok=True)

        args = [
            f"{self.path_bin_poetry}",
            "export",
            "--format",
            "requirements.txt",
            "--output",
            f"{path}",
            "--extras",
        ]
        args.append(group)
        if with_hash is False:
            args.append("--without-hashes")
        self.run_command(args, real_run)

    def _poetry_export_logic(
        self: "PyWf",
        current_poetry_lock_hash: str,
        with_hash: bool = False,
        real_run: bool = True,
    ):
        """
        Run ``poetry export --format requirements.txt ...`` command and write
        the sha256 hash of the current ``poetry.lock`` file to the cache file.

        Run:

        .. code-block:: bash

            poetry export --format requirements.txt --output requirements.txt --without-hashes
            poetry export --format requirements.txt --output requirements-dev.txt --extras dev --without-hashes
            poetry export --format requirements.txt --output requirements-test.txt --extras test --without-hashes
            poetry export --format requirements.txt --output requirements-doc.txt --extras doc --without-hashes
            poetry export --format requirements.txt --output requirements-automation.txt --extras auto --without-hashes

        :param current_poetry_lock_hash: the sha256 hash of the current ``poetry.lock`` file
        :param with_hash: whether to include the hash of the dependencies in the
            requirements.txt file.
        """
        # export the main dependencies
        self._poetry_export_main(with_hash=with_hash, real_run=real_run)

        # export dev, test, doc, auto dependencies
        for group, path in [
            ("dev", self.path_requirements_dev),
            ("test", self.path_requirements_test),
            ("doc", self.path_requirements_doc),
            ("auto", self.path_requirements_automation),
        ]:
            self._poetry_export_group(
                group=group,
                path=path,
                with_hash=with_hash,
                real_run=real_run,
            )

        # write the ``poetry.lock`` hash to the cache file
        if real_run:
            self.path_poetry_lock_hash_json.write_text(
                json.dumps(
                    {
                        "hash": current_poetry_lock_hash,
                        "description": (
                            "DON'T edit this file manually! This file is the cache of "
                            "the poetry.lock file hash. It is used to avoid unnecessary "
                            "expansive 'poetry export ...' command."
                        ),
                    },
                    indent=4,
                )
            )

    @logger.emoji_block(
        msg="Export all dependencies to requirements-***.txt",
        emoji=Emoji.install,
    )
    def _poetry_export(
        self: "PyWf",
        with_hash: bool = False,
        real_run: bool = True,
        quiet: bool = False,
    ) -> bool:
        """
        :return: ``True`` if ``poetry export`` is executed, ``False`` if not.
        """
        poetry_lock_hash = sha256_of_bytes(self.path_poetry_lock.read_bytes())
        if self._do_we_need_poetry_export(poetry_lock_hash):
            self._poetry_export_logic(
                current_poetry_lock_hash=poetry_lock_hash,
                with_hash=with_hash,
                real_run=real_run,
            )
            return True
        else:
            logger.info("already did, do nothing")
            return False

    def poetry_export(
        self: "PyWf",
        with_hash: bool = False,
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            flag = self._poetry_export(
                with_hash=with_hash,
                real_run=real_run,
                quiet=not verbose,
            )
            return flag

    poetry_export.__doc__ = _poetry_export_logic.__doc__

    def _run_uv_command(
        self: "PyWf",
        args: T.List[str],
        real_run: bool,
        quiet: bool,
    ):
        args = [f"{self.path_bin_uv}", *args]
        if quiet:
            args.append("--quiet")
        self.run_command(args, real_run)

    @logger.emoji_block(
        msg="Resolve Dependencies Tree",
        emoji=Emoji.install,
    )
    def _uv_lock(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Lock project dependencies defined in pyproject.toml.

        Resolves and writes exact dependency versions to ``uv.lock`` file.
        This ensures reproducible builds across different environments.
        You have to run this everytime you changed the ``pyproject.toml`` file.
        And you should commit the latest ``uv.lock`` file to git.

        Run:

        .. code-block:: bash

            uv lock

        Ref:

        - uv lock: https://docs.astral.sh/uv/reference/cli/#uv-lock
        """
        return self._run_uv_command(
            args=["lock"],
            real_run=real_run,
            quiet=quiet,
        )

    def uv_lock(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            return self._uv_lock(
                real_run=real_run,
                quiet=not verbose,
            )

    uv_lock.__doc__ = _uv_lock.__doc__
