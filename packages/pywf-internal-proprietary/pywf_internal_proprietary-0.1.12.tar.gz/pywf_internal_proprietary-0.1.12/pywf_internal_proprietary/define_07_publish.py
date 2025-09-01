# -*- coding: utf-8 -*-

"""
Publish to Python repository related automation.
"""

import typing as T
import dataclasses

try:
    from github import (
        Github,
        GithubException,
        Repository,
        GitTag,
        GitRelease,
    )
except ImportError:  # pragma: no cover
    pass

from .vendor.emoji import Emoji
from .vendor.better_pathlib import temp_cwd

from .logger import logger
from .helpers import bump_version, print_command

if T.TYPE_CHECKING:  # pragma: no cover
    from .define import PyWf


@dataclasses.dataclass
class PyWfPublish:  # pragma: no cover
    """
    Namespace class for publishing to Python repository related automation.
    """

    def bump_version(
        self: "PyWf",
        major: bool = False,
        minor: bool = False,
        patch: bool = False,
        real_run: bool = True,
        verbose: bool = False,
    ):
        """
        Bump a semantic version. The current version has to be in x.y.z format,
        where x, y, z are integers.

        :param major: bump major version.
        :param minor: bump minor version.
        :param patch: bump patch version.
        :param minor_start_from: if bumping major version, minor start from this number.
        :param micro_start_from: if bumping minor version, micro start from this number.
        """
        # update pyproject.toml file
        if self.path_pyproject_toml.exists():
            if major:
                action = "major"
            elif minor:
                action = "minor"
            elif patch:
                action = "patch"
            else:  # pragma: no cover
                raise NotImplementedError
            args = [
                f"{self.path_bin_poetry}",
                "version",
                action,
            ]
            self.run_command(args, real_run)

    @logger.emoji_block(
        msg="Publish to GitHub Release",
        emoji=Emoji.package,
    )
    def _publish_to_github_release(
        self: "PyWf",
        real_run: bool = True,
    ) -> T.Optional["GitRelease"]:  # pragma: no cover
        """
        Create a GitHub Release using the current version based on main branch.

        :returns: a boolean flag to indicate whether the operation is performed.
        """
        logger.info(f"preview release at {self.github_versioned_release_url}")

        release_name = self.package_version
        gh = Github(self.github_token)
        repo = gh.get_repo(self.github_repo_fullname)

        # Check if release exists
        try:
            repo.get_release(release_name)
            logger.info(f"Release {release_name!r} already exists.")
            return None
        except GithubException as e:
            if e.status == 404:
                pass
            else:
                raise e
        except Exception as e:  # pragma: no cover
            raise e

        # Create Tag if not exists
        try:
            repo.get_git_ref(f"tags/{release_name}")
            logger.info(f"Tag {release_name!r} already exists.")
        except GithubException as e:
            if e.status == 404:
                if real_run:
                    default_branch = repo.default_branch
                    commit = repo.get_branch(default_branch).commit
                    commit_sha = commit.sha
                    tag = repo.create_git_tag(
                        tag=release_name,
                        message=f"Release {release_name}",
                        object=commit_sha,
                        type="commit",
                    )
                    repo.create_git_ref(
                        ref=f"refs/tags/{release_name}",
                        sha=tag.sha,
                    )
            else:  # pragma: no cover
                raise e
        except Exception as e:  # pragma: no cover
            raise e

        # Create Release
        if real_run:
            release = repo.create_git_release(
                tag=release_name,
                name=release_name,
                message=f"Release {release_name}",
            )
            return release
        else:
            return None

    def publish_to_github_release(
        self: "PyWf",
        real_run: bool = True,
        verbose: bool = True,
    ):  # pragma: no cover
        with logger.disabled(not verbose):
            return self._publish_to_github_release(
                real_run=real_run,
            )

    publish_to_github_release.__doc__ = _publish_to_github_release.__doc__
