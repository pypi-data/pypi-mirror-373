# -*- coding: utf-8 -*-

"""
Setup automation for AWS services.
"""

import typing as T
import os
import subprocess
import dataclasses
from functools import cached_property

try:
    import boto3
    import botocore.exceptions
except ImportError:  # pragma: no cover
    pass

from .vendor.emoji import Emoji

from .logger import logger
from .runtime import IS_CI
from .helpers import print_command

if T.TYPE_CHECKING:  # pragma: no cover
    from .define import PyWf
    from boto3 import Session
    from mypy_boto3_codeartifact.client import CodeArtifactClient


@dataclasses.dataclass
class PyWfAws:  # pragma: no cover
    """
    Namespace class for AWS setup automation.
    """

    @cached_property
    def boto_ses_codeartifact(self: "PyWf") -> "Session":
        if IS_CI:
            profile_name = None
        else:
            if self.aws_codeartifact_profile:
                profile_name = self.aws_codeartifact_profile
            else:
                profile_name = None
        return boto3.Session(
            profile_name=profile_name,
            region_name=self.aws_region,
        )

    @cached_property
    def codeartifact_client(self: "PyWf") -> "CodeArtifactClient":
        return self.boto_ses_codeartifact.client("codeartifact")

    def get_codeartifact_repository_endpoint(self: "PyWf") -> str:
        """
        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codeartifact/client/get_repository_endpoint.html
        """
        res = self.codeartifact_client.get_repository_endpoint(
            domain=self.aws_codeartifact_domain,
            repository=self.aws_codeartifact_repository,
            format="pypi",
        )
        return res["repositoryEndpoint"]

    def get_codeartifact_authorization_token(
        self: "PyWf",
        duration_minutes: int = 15,
    ) -> str:
        """
        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codeartifact/client/get_authorization_token.html
        """
        res = self.codeartifact_client.get_authorization_token(
            domain=self.aws_codeartifact_domain,
            durationSeconds=duration_minutes * 60,
        )
        return res["authorizationToken"]

    @property
    def poetry_secondary_source_name(self: "PyWf") -> str:
        return self.aws_codeartifact_domain

    @logger.emoji_block(
        msg="Add CodeArtifact as a secondary source",
        emoji=Emoji.install,
    )
    def _poetry_source_add_codeartifact(
        self: "PyWf",
        codeartifact_repository_endpoint: str,
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Run:

        .. code-block:: bash

            poetry source add --secondary ${source_name} "https://${domain_name}-${aws_account_id}.d.codeartifact.${aws_region}.amazonaws.com/pypi/${repository_name}/simple/"
        """
        args = [
            f"{self.path_bin_poetry}",
            "source",
            "add",
            "--priority=supplemental",
            self.poetry_secondary_source_name,
            f"{codeartifact_repository_endpoint}simple/",
        ]
        self.run_command(args, real_run)

    def poetry_source_add_codeartifact(
        self: "PyWf",
        codeartifact_repository_endpoint: str,
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            self._poetry_source_add_codeartifact(
                codeartifact_repository_endpoint=codeartifact_repository_endpoint,
                real_run=real_run,
                quiet=not verbose,
            )

    poetry_source_add_codeartifact.__doc__ = _poetry_source_add_codeartifact.__doc__

    @logger.emoji_block(
        msg="Poetry authorization",
        emoji="🔐",
    )
    def _poetry_authorization(
        self: "PyWf",
        codeartifact_authorization_token: str,
        real_run: bool = True,
        verbose: bool = True,
    ):
        """
        Set environment variables to allow Poetry to authenticate with CodeArtifact.
        It also set the credential to the Poetry config.
        """
        token = codeartifact_authorization_token
        source_name = self.poetry_secondary_source_name.upper()
        if real_run:  # pragma: no cover
            # poetry use environment variables to get the private repository
            # Http basic auth credentials.
            # See: https://python-poetry.org/docs/repositories/#configuring-credentials
            key = f"POETRY_HTTP_BASIC_{source_name}_USERNAME"
            os.environ[key] = "aws"
            logger.info(f"Set environment variable: {key}")

            key = f"POETRY_HTTP_BASIC_{source_name}_PASSWORD"
            os.environ[key] = token
            logger.info(f"Set environment variable: {key}")

            # This command will store the credential in Poetry config.
            # So that even in another shell, or command, poetry lock can
            # still work without setting the environment variable again.
            # See: https://python-poetry.org/docs/repositories/#configuring-credentials
            # On MacOS, poetry will use keyring to store the credentials
            # instead of storing in plain text in the config file.
            args = [
                f"{self.path_bin_poetry}",
                "config",
                f"http-basic.{self.poetry_secondary_source_name}",
                "aws",
                "**token**",
            ]
            print_command(args)
            args[-1] = token
            if real_run:
                logger.info(f"cd to: {self.dir_project_root}")
                subprocess.run(args, cwd=self.dir_project_root)

    def poetry_authorization(
        self: "PyWf",
        codeartifact_authorization_token: str,
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            self._poetry_authorization(
                codeartifact_authorization_token=codeartifact_authorization_token,
                real_run=real_run,
                verbose=verbose,
            )

    poetry_authorization.__doc__ = _poetry_authorization.__doc__

    @property
    def uv_secondary_source_name(self: "PyWf") -> str:
        return self.aws_codeartifact_domain

    @logger.emoji_block(
        msg="uv authorization",
        emoji="🔐",
    )
    def _uv_authorization(
        self: "PyWf",
        codeartifact_authorization_token: str,
        real_run: bool = True,
        verbose: bool = True,
    ):
        """
        Set environment variables to allow uv to authenticate with CodeArtifact.
        """
        token = codeartifact_authorization_token
        source_name = self.uv_secondary_source_name.upper()
        if real_run:  # pragma: no cover
            # uv use environment variables to get the private repository
            # Http basic auth credentials.
            # See: https://docs.astral.sh/uv/reference/environment/#uv_index_url
            key = f"UV_INDEX_{source_name}_USERNAME"
            os.environ[key] = "aws"
            logger.info(f"Set environment variable: {key}")

            key = f"UV_INDEX_{source_name}_PASSWORD"
            os.environ[key] = token
            logger.info(f"Set environment variable: {key}")

    def uv_authorization(
        self: "PyWf",
        codeartifact_authorization_token: str,
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            self._uv_authorization(
                codeartifact_authorization_token=codeartifact_authorization_token,
                real_run=real_run,
                verbose=verbose,
            )

    uv_authorization.__doc__ = _uv_authorization.__doc__

    def _configure_tool_with_aws_code_artifact(
        self: "PyWf",
        tool: str,
        duration_minutes: int = 15,
        real_run: bool = True,
    ):
        aws_account_id = self.boto_ses_codeartifact.client("sts").get_caller_identity()[
            "Account"
        ]
        args = [
            f"{self.path_bin_aws}",
            "codeartifact",
            "login",
            "--tool",
            tool,
            "--domain",
            self.aws_codeartifact_domain,
            "--domain-owner",
            aws_account_id,
            "--repository",
            self.aws_codeartifact_repository,
            "--duration-seconds",
            f"{duration_minutes * 60}",
        ]
        if IS_CI is False:
            if self.aws_codeartifact_profile:
                args.extend(["--profile", self.aws_codeartifact_profile])

        self.run_command(args, real_run)

    @logger.emoji_block(
        msg="Pip authorization",
        emoji="🔐",
    )
    def _pip_authorization(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Run:

        .. code-block:: bash

            aws codeartifact login --tool pip \
                --domain ${domain_name} \
                --domain-owner ${aws_account_id} \
                --repository ${repo_name} \
                --profile ${aws_profile}

        .. note::

            This command will set the default index to AWS CodeArtifact and
            stop using the public PyPI. It will not be able to install a package
            that doesn't exist in AWS CodeArtifact.

            The community raises an issue https://github.com/aws/aws-cli/issues/5409
            and it is not fixed yet. You may want to set the ``extra-index-url``
            instead. This function implements our own solution to set the
            ``extra-index-url`` to the AWS CodeArtifact repository.
        
        Reference:

        - `Configure and use pip with CodeArtifact <https://docs.aws.amazon.com/codeartifact/latest/ug/python-configure-pip.html>`_
        - `AWS CodeArtifact CLI <https://docs.aws.amazon.com/cli/latest/reference/codeartifact/index.html>`_
        """
        token = self.get_codeartifact_authorization_token()
        endpoint = self.get_codeartifact_repository_endpoint()
        endpoint = endpoint.replace("https://", "")
        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]
        index_url = f"https://aws:{token}@{endpoint}/simple/"
        args = [
            f"{self.path_venv_bin_pip}",
            "config",
            "set",
            "global.extra-index-url",
            index_url,
        ]
        self.run_command(args, real_run)

    def pip_authorization(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            self._pip_authorization(
                real_run=real_run,
                quiet=not verbose,
            )

    pip_authorization.__doc__ = _pip_authorization.__doc__

    @logger.emoji_block(
        msg="Twine authorization",
        emoji="🔐",
    )
    def _twine_authorization(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Run

        .. code-block:: bash

            aws codeartifact login --tool twine \
                --domain ${domain_name} \
                --domain-owner ${aws_account_id} \
                --repository ${repo_name} \
                --profile ${aws_profile}

        Reference:

        - `Configure and use twine with CodeArtifact <https://docs.aws.amazon.com/codeartifact/latest/ug/python-configure-twine.html>`_
        - `AWS CodeArtifact CLI <https://docs.aws.amazon.com/cli/latest/reference/codeartifact/index.html>`_
        """
        self._configure_tool_with_aws_code_artifact(tool="twine", real_run=real_run)

    def twine_authorization(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            self._twine_authorization(
                real_run=real_run,
                quiet=not verbose,
            )

    twine_authorization.__doc__ = _twine_authorization.__doc__

    @logger.emoji_block(
        msg="Run twine upload command",
        emoji=Emoji.package,
    )
    def _twine_upload(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Upload Python package to CodeArtifact.

        Run

        .. code-block:: bash

            twine upload dist/* --repository codeartifact
        """
        aws_account_id = self.boto_ses_codeartifact.client("sts").get_caller_identity()[
            "Account"
        ]
        aws_region = self.aws_region
        console_url = (
            f"https://{aws_region}.console.aws.amazon.com/codesuite/codeartifact/d"
            f"/{aws_account_id}/{self.aws_codeartifact_domain}/r"
            f"/{self.aws_codeartifact_repository}/p/pypi/"
            f"{self.package_name}/versions?region={aws_region}"
        )
        logger.info(f"preview in AWS CodeArtifact console: {console_url}")
        args = [
            f"{self.path_bin_twine}",
            "upload",
            f"{self.dir_dist}/*",
            "--repository",
            "codeartifact",
        ]
        self.run_command(args, real_run)

    def twine_upload(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            self._twine_upload(
                real_run=real_run,
                quiet=not verbose,
            )

    twine_upload.__doc__ = _twine_upload.__doc__

    @logger.emoji_block(
        msg="Publish Python package to AWS CodeArtifact",
        emoji=Emoji.package,
    )
    def _publish_to_codeartifact(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        """
        Publish your Python package to AWS CodeArtifact
        """
        try:
            self.codeartifact_client.describe_package_version(
                domain=self.aws_codeartifact_domain,
                repository=self.aws_codeartifact_repository,
                format="pypi",
                package=self.package_name_slug,
                packageVersion=self.package_version,
            )
            if real_run is True:  # pragma: no cover
                message = (
                    f"package {self.package_name_slug!r} "
                    f"= {self.package_version} already exists!"
                )
                raise Exception(message)
        except botocore.exceptions.ClientError as e:  # pragma: no cover
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                pass
            else:
                raise e

        with logger.nested():
            self.twine_upload(real_run=real_run, verbose=verbose)

    def publish_to_codeartifact(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(disable=not verbose):
            self._publish_to_codeartifact(
                real_run=real_run,
                verbose=verbose,
            )

    publish_to_codeartifact.__doc__ = _publish_to_codeartifact.__doc__

    @logger.emoji_block(
        msg="Remove package version from AWS CodeArtifact",
        emoji=Emoji.package,
    )
    def remove_from_codeartifact(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        """
        Remove a specific version of your Python package release AWS CodeArtifact.

        .. warning::

            I suggest don't do this unless you have to.
            If you re-publish your package with the same version,
            then you may need to invalid the poetry cache before doing poetry lock.
        """
        res = input(
            f"Are you sure you want to remove the package {self.package_name_slug!r} "
            f"version {self.package_version!r}? (Y/N): "
        )
        if res == "Y":
            if real_run:  # pragma: no cover
                self.codeartifact_client.delete_package_versions(
                    domain=self.aws_codeartifact_domain,
                    repository=self.aws_codeartifact_repository,
                    format="pypi",
                    package=self.package_name_slug,
                    versions=[self.package_version],
                    expectedStatus="Published",
                )
                logger.info("Package version removed.")
            else:
                logger.info("Not a real run, do nothing.")
        else:
            logger.info("Aborted")
