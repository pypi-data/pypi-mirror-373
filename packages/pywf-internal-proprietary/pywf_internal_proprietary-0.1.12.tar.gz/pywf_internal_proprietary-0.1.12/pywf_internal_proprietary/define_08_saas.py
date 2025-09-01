# -*- coding: utf-8 -*-

"""
Setup SaaS services for your Open Source Python project.
"""

import typing as T
import dataclasses
from functools import cached_property

try:
    import requests
    from github import Github, Auth, Repository
except ImportError:  # pragma: no cover
    pass

from .vendor.emoji import Emoji

from .logger import logger

if T.TYPE_CHECKING:  # pragma: no cover
    from .define import PyWf


@dataclasses.dataclass
class PyWfSaas:  # pragma: no cover
    """
    Namespace class for SaaS service setup automation.
    """

    @cached_property
    def gh(self: "PyWf") -> "Github":
        return Github(auth=Auth.Token(self.github_token))

    @logger.emoji_block(
        msg="Edit GitHub Repo metadata",
        emoji=Emoji.package,
    )
    def _edit_github_repo_metadata(
        self: "PyWf",
        real_run: bool = True,
    ):
        """
        Edit GitHub repo metadata such as description and homepage URL.

        Ref:

        - https://pygithub.readthedocs.io/en/latest/examples/Repository.html

        :returns: a boolean flag to indicate whether the operation is performed.
        """
        with logger.indent():
            logger.info(f"preview at {self.github_repo_url}")
        if real_run:  # pragma: no cover
            repo = self.gh.get_repo(self.github_repo_fullname)
            repo.edit(
                description=self.package_description,
                homepage=self.cloudflare_pages_doc_site_url,
            )
        return real_run

    def edit_github_repo_metadata(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(not verbose):
            return self._edit_github_repo_metadata(
                real_run=real_run,
            )

    edit_github_repo_metadata.__doc__ = _edit_github_repo_metadata.__doc__

    def get_codecov_io_upload_token(
        self: "PyWf",
        real_run: bool = True,
    ) -> T.Optional[str]:
        """
        Get the upload token for codecov io for your GitHub repo.

        Ref:

        - https://docs.codecov.com/reference/repos_retrieve
        - https://docs.codecov.com/reference/repos_config_retrieve

        :returns: the upload token for codecov.io.
        """
        logger.info("Getting codecov.io upload token...")
        url = f"https://app.codecov.io/gh/{self.github_account}/{self.git_repo_name}/settings"
        with logger.indent():
            logger.info(f"preview at {url}")
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.codecov_token}",
        }
        endpoint = "https://api.codecov.io/api/v2"
        url = f"{endpoint}/github/{self.github_account}/repos/{self.git_repo_name}/"
        if real_run:  # pragma: no cover
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            is_private = response.json()["private"]
            if is_private is True:
                raise ValueError("You cannot use codecov.io for private repositories.")

        url = f"{endpoint}/github/{self.github_account}/repos/{self.git_repo_name}/config/"
        if real_run:  # pragma: no cover
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            upload_token = response.json()["upload_token"]
            return upload_token
        else:
            return None

    @logger.emoji_block(
        msg="Setup codecov.io Upload Token on GitHub",
        emoji=Emoji.test,
    )
    def _setup_codecov_io_upload_token_on_github(
        self: "PyWf",
        real_run: bool = True,
    ):
        """
        Apply the codecov upload token to GitHub Action secrets in your GitHub repository.

        Ref:

        - https://docs.codecov.com/reference/repos_retrieve
        - https://docs.codecov.com/reference/repos_config_retrieve
        - https://pygithub.readthedocs.io/en/latest/examples/Repository.html

        :returns: a boolean flag to indicate whether the operation is performed.
        """
        codecov_io_upload_token = self.get_codecov_io_upload_token(real_run=real_run)
        logger.info("Setting up codecov.io upload token on GitHub...")
        with logger.indent():
            logger.info(f"preview at {self.github_actions_secrets_settings_url}")
        if real_run:  # pragma: no cover
            repo = self.gh.get_repo(self.github_repo_fullname)
            repo.create_secret(
                secret_name="CODECOV_TOKEN",
                unencrypted_value=codecov_io_upload_token,
                secret_type="actions",
            )
        return real_run

    def setup_codecov_io_upload_token_on_github(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(not verbose):
            return self._setup_codecov_io_upload_token_on_github(
                real_run=real_run,
            )

    setup_codecov_io_upload_token_on_github.__doc__ = (
        _setup_codecov_io_upload_token_on_github.__doc__
    )

    @logger.emoji_block(
        msg="Setup Secret Env Var on GitHub",
        emoji=Emoji.test,
    )
    def _setup_secret_env_var_on_github(
        self: "PyWf",
        real_run: bool = True,
    ):
        """
        Apply necessary secret environment variable to GitHub Action secrets in your GitHub repository.

        Ref:

        - https://pygithub.readthedocs.io/en/latest/examples/Repository.html

        :returns: a boolean flag to indicate whether the operation is performed.
        """
        logger.info("Setting up Secret Env Var on GitHub...")
        with logger.indent():
            logger.info(f"preview at {self.github_actions_secrets_settings_url}")
        if real_run:  # pragma: no cover
            repo = self.gh.get_repo(self.github_repo_fullname)
            repo.create_secret(
                secret_name="DEVOPS_AWS_ACCOUNT_ID",
                unencrypted_value=self.devops_aws_account_id,
                secret_type="actions",
            )
        return real_run

    def setup_secret_env_var_on_github(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(not verbose):
            return self._setup_secret_env_var_on_github(
                real_run=real_run,
            )

    setup_secret_env_var_on_github.__doc__ = (
        _setup_secret_env_var_on_github.__doc__
    )

