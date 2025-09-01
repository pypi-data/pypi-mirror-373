# -*- coding: utf-8 -*-

"""
Document Build and Deploy Automation for Python Projects.
"""

import typing as T
import shutil
import dataclasses

from .vendor.emoji import Emoji
from .vendor.os_platform import OPEN_COMMAND

from .logger import logger

if T.TYPE_CHECKING:  # pragma: no cover
    from .define import PyWf


@dataclasses.dataclass
class PyWfDocs:
    """
    Namespace class for document related automation.
    """

    @logger.emoji_block(
        msg="Build Documentation Site Locally",
        emoji=Emoji.doc,
    )
    def _build_doc(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        Use sphinx doc to build documentation site locally. It set the
        necessary environment variables so that the ``make html`` command
        can build the HTML successfully.

        Run:

        .. code-block:: bash

            sphinx-build -M html docs/source docs/build
        """
        if real_run:
            shutil.rmtree(
                f"{self.dir_sphinx_doc_build}",
                ignore_errors=True,
            )
            shutil.rmtree(
                f"{self.dir_sphinx_doc_source_python_lib}",
                ignore_errors=True,
            )

        args = [
            f"{self.path_venv_bin_sphinx_build}",
            "-M",
            "html",
            f"{self.dir_sphinx_doc_source}",
            f"{self.dir_sphinx_doc_build}",
        ]
        self.run_command(args, real_run)

    def build_doc(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):  # pragma: no cover
        with logger.disabled(not verbose):
            return self._build_doc(
                real_run=real_run,
                quiet=not verbose,
            )

    build_doc.__doc__ = _build_doc.__doc__

    @logger.emoji_block(
        msg="View Documentation Site Locally",
        emoji=Emoji.doc,
    )
    def _view_doc(
        self: "PyWf",
        real_run: bool = True,
        quiet: bool = False,
    ):
        """
        View documentation site built locally in web browser.

        It is usually at the ``${dir_project_root}/build/html/index.html``

        Run:

        .. code-block:: bash

            # For MacOS / Linux
            open build/html/index.html
            # For Windows
            start build/html/index.html
        """
        args = [OPEN_COMMAND, f"{self.path_sphinx_doc_build_index_html}"]
        self.run_command(args, real_run)

    def view_doc(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(not verbose):
            return self._view_doc(
                real_run=real_run,
                quiet=not verbose,
            )

    view_doc.__doc__ = _view_doc.__doc__

    @logger.emoji_block(
        msg="Deploy Documentation Site To S3 as Versioned Doc",
        emoji=Emoji.doc,
    )
    def _deploy_versioned_doc(
        self: "PyWf",
        bucket: T.Optional[str] = None,
        prefix: str = "projects/",
        aws_profile: T.Optional[str] = None,
        real_run: bool = True,
        quiet: bool = False,
    ) -> bool:  # pragma: no cover
        """
        Deploy versioned document to AWS S3.

        The S3 bucket has to enable static website hosting. The document site
        will be uploaded to ``s3://${bucket}/${prefix}${package_name}/${package_version}/``
        """
        if bool(self.doc_host_s3_bucket) is False:
            logger.info(f"{Emoji.red_circle} doc_host_s3_bucket is not set, skip.")
            return False
        if bucket is None:
            bucket = self.doc_host_s3_bucket
        if aws_profile is None:
            aws_profile = self.doc_host_aws_profile
        args = [
            f"{self.path_bin_aws}",
            "s3",
            "sync",
            f"{self.dir_sphinx_doc_build_html}",
            f"s3://{bucket}/{prefix}{self.package_name}/{self.package_version}/",
        ]
        if aws_profile:
            args.extend(["--profile", aws_profile])
        self.run_command(args, real_run)
        return real_run

    def deploy_versioned_doc(
        self: "PyWf",
        bucket: T.Optional[str] = None,
        prefix: str = "projects/",
        aws_profile: T.Optional[str] = None,
        real_run: bool = True,
        verbose: bool = True,
    ) -> bool:  # pragma: no cover
        with logger.disabled(not verbose):
            return self._deploy_versioned_doc(
                bucket=bucket,
                prefix=prefix,
                aws_profile=aws_profile,
                real_run=real_run,
                quiet=not verbose,
            )

    deploy_versioned_doc.__doc__ = _deploy_versioned_doc.__doc__

    @logger.emoji_block(
        msg="Deploy Documentation Site To S3 as Latest Doc",
        emoji=Emoji.doc,
    )
    def _deploy_latest_doc(
        self: "PyWf",
        bucket: T.Optional[str] = None,
        prefix: str = "projects/",
        aws_profile: T.Optional[str] = None,
        real_run: bool = True,
        quiet: bool = False,
    ) -> bool:  # pragma: no cover
        """
        Deploy the latest document to AWS S3.

        The S3 bucket has to enable static website hosting. The document site
        will be uploaded to ``s3://${bucket}/${prefix}${package_name}/latest/``
        """
        if bool(self.doc_host_s3_bucket) is False:
            logger.info(f"{Emoji.red_circle} doc_host_s3_bucket is not set, skip.")
            return False
        if bucket is None:
            bucket = self.doc_host_s3_bucket
        if aws_profile is None:
            aws_profile = self.doc_host_aws_profile
        args = [
            f"{self.path_bin_aws}",
            "s3",
            "sync",
            f"{self.dir_sphinx_doc_build_html}",
            f"s3://{bucket}/{prefix}{self.package_name}/latest/",
        ]
        if aws_profile:
            args.extend(["--profile", aws_profile])
        self.run_command(args, real_run)
        return real_run

    def deploy_latest_doc(
        self: "PyWf",
        bucket: T.Optional[str] = None,
        prefix: str = "projects/",
        aws_profile: T.Optional[str] = None,
        real_run: bool = True,
        verbose: bool = True,
    ) -> bool:  # pragma: no cover
        with logger.disabled(not verbose):
            return self._deploy_latest_doc(
                bucket=bucket,
                prefix=prefix,
                aws_profile=aws_profile,
                real_run=real_run,
                quiet=not verbose,
            )

    deploy_latest_doc.__doc__ = _deploy_latest_doc.__doc__

    @logger.emoji_block(
        msg="View Latest Doc on AWS S3",
        emoji=Emoji.doc,
    )
    def _view_latest_doc(
        self: "PyWf",
        bucket: T.Optional[str] = None,
        prefix: str = "projects/",
        real_run: bool = True,
        quiet: bool = False,
    ):  # pragma: no cover
        """
        Open the latest document that hosted on AWS S3 in web browser.

        Here's a sample document site url
        https://my-bucket.s3.amazonaws.com/my-prefix/my_package/latest/index.html
        """
        if bool(self.doc_host_s3_bucket) is False:
            logger.info(f"{Emoji.red_circle} doc_host_s3_bucket is not set, skip.")
            return False
        if bucket is None:
            bucket = self.doc_host_s3_bucket
        url = (
            f"https://{bucket}.s3.amazonaws.com/{prefix}{self.package_name}"
            f"/latest/{self.path_sphinx_doc_build_index_html.name}"
        )
        args = [OPEN_COMMAND, url]
        self.run_command(args, real_run)

    def view_latest_doc(
        self: "PyWf",
        bucket: T.Optional[str] = None,
        prefix: str = "projects/",
        real_run: bool = True,
        verbose: bool = True,
    ):  # pragma: no cover
        with logger.disabled(not verbose):
            return self._view_latest_doc(
                bucket=bucket,
                prefix=prefix,
                real_run=real_run,
                quiet=not verbose,
            )

    view_latest_doc.__doc__ = _view_latest_doc.__doc__

    @logger.emoji_block(
        msg="Convert Jupyter Notebook to Markdown",
        emoji=Emoji.doc,
    )
    def _notebook_to_markdown(
        self: "PyWf",
        real_run: bool = True,
    ):
        """
        Convert Jupyter notebooks to Markdown files so they can be
        more efficiently included in the AI knowledge base.
        """
        for path_notebook in self.dir_sphinx_doc_source.glob("**/*.ipynb"):
            if ".ipynb_checkpoints" in str(path_notebook):
                continue
            path_markdown = path_notebook.parent / "index.md"
            args = [
                f"{self.path_venv_bin_bin_jupyter}",
                "nbconvert",
                "--to",
                "markdown",
                str(path_notebook),
                "--output",
                str(path_markdown),
            ]
            self.run_command(args, real_run)

    def notebook_to_markdown(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):
        with logger.disabled(not verbose):
            return self._notebook_to_markdown(
                real_run=real_run,
            )

    notebook_to_markdown.__doc__ = _notebook_to_markdown.__doc__
