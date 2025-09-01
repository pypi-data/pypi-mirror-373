# -*- coding: utf-8 -*-

"""
Setup automation for Cloudflare.
"""

import typing as T
import os
import dataclasses

try:
    import boto3
    import botocore.exceptions
    import requests
    from github import Github
except ImportError:  # pragma: no cover
    pass

from .vendor.emoji import Emoji

from .logger import logger
from .runtime import IS_CI

if T.TYPE_CHECKING:  # pragma: no cover
    from .define import PyWf


@dataclasses.dataclass
class PyWfCloudflare:  # pragma: no cover
    """
    Namespace class for Cloudflare setup automation.
    """

    @property
    def cloudflare_pages_doc_site_url(self: "PyWf") -> str:
        """
        Get the URL of the documentation site hosted on Cloudflare Pages.
        """
        return f"http://{self.package_name_slug}.pages.dev/"

    def setup_cloudflare_env_vars(self: "PyWf"):
        os.environ["CLOUDFLARE_API_TOKEN"] = self.cloudflare_token

    @logger.emoji_block(
        msg="Create Cloudflare Pages project",
        emoji=Emoji.doc,
    )
    def _create_cloudflare_pages_project(
        self: "PyWf",
        real_run: bool = True,
    ):
        """
        Create a Cloudflare Pages project using Wrangler CLI.
        """
        self.setup_cloudflare_env_vars()
        args = [
            f"{self.path_bin_wrangler}",
            "pages",
            "project",
            "create",
            self.package_name_slug,
            "--production-branch",
            "main",
        ]
        self.run_command(args, real_run)

    def create_cloudflare_pages_project(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(not verbose):
            return self._create_cloudflare_pages_project(
                real_run=real_run,
            )

    create_cloudflare_pages_project.__doc__ = _create_cloudflare_pages_project.__doc__

    @logger.emoji_block(
        msg="Create Cloudflare Pages project",
        emoji=Emoji.doc,
    )
    def _deploy_cloudflare_pages(
        self: "PyWf",
        real_run: bool = True,
    ):
        """
        Deploy the documentation site to Cloudflare Pages using Wrangler CLI.
        """
        self.setup_cloudflare_env_vars()
        args = [
            f"{self.path_bin_wrangler}",
            "pages",
            "deploy",
            f"{self.dir_sphinx_doc_build_html}",
            f"--project-name={self.package_name_slug}",
        ]
        self.run_command(args, real_run)

    def deploy_cloudflare_pages(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(not verbose):
            return self._deploy_cloudflare_pages(
                real_run=real_run,
            )

    deploy_cloudflare_pages.__doc__ = _deploy_cloudflare_pages.__doc__

    @logger.emoji_block(
        msg="Setup Cloudflare Pages Upload Token on GitHub",
        emoji=Emoji.test,
    )
    def _setup_cloudflare_pages_upload_token_on_github(
        self: "PyWf",
        real_run: bool = True,
    ):
        """
        Apply the cloudflare pages upload token to GitHub Action secrets in your GitHub repository.

        Ref:

        - https://docs.codecov.com/reference/repos_retrieve
        - https://docs.codecov.com/reference/repos_config_retrieve
        - https://pygithub.readthedocs.io/en/latest/examples/Repository.html

        :returns: a boolean flag to indicate whether the operation is performed.
        """
        logger.info("Setting up Cloudflare pages upload token on GitHub...")
        with logger.indent():
            logger.info(f"preview at {self.github_actions_secrets_settings_url}")
        if real_run:  # pragma: no cover
            repo = self.gh.get_repo(self.github_repo_fullname)
            repo.create_secret(
                secret_name="CLOUDFLARE_API_TOKEN",
                unencrypted_value=self.cloudflare_token,
                secret_type="actions",
            )
        return real_run

    def setup_cloudflare_pages_upload_token_on_github(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(not verbose):
            return self._setup_cloudflare_pages_upload_token_on_github(
                real_run=real_run,
            )

    setup_cloudflare_pages_upload_token_on_github.__doc__ = (
        _setup_cloudflare_pages_upload_token_on_github.__doc__
    )
