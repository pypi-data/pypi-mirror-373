# ozi/spec/ci.py
# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: Unlicense
"""Continuous integration specification."""
from __future__ import annotations

from dataclasses import dataclass

from ozi_spec.base import Default


@dataclass(slots=True, frozen=True, eq=True)
class Publish(Default):
    """Publishing patterns for packaged project."""

    include: tuple[str, ...] = ('*.tar.gz', '*.whl', 'sig/*')
    version: str = '@github_publish_version@'


@dataclass(slots=True, frozen=True, eq=True)
class Draft(Default):
    """Draft release patterns for packaged project."""

    version: str = '@github_draft_version@'


@dataclass(slots=True, frozen=True, eq=True)
class Release(Default):
    """Release patterns for packaged project."""

    version: str = '@github_release_version@'


@dataclass(slots=True, frozen=True, eq=True)
class GenerateProvenance(Default):
    """SLSA provenance generator metadata.

    .. versionadded:: 0.11.7
    """

    version: str = '@github_slsa_version@'


@dataclass(slots=True, frozen=True, eq=True)
class Provenance(Default):
    """Github provenance generator metadata.

    .. versionadded:: 1.1
    """

    version: str = '@github_provenance_version@'


@dataclass(slots=True, frozen=True, eq=True)
class Checkpoint(Default):
    """Checkpoint suites to run."""

    suites: tuple[str, ...] = ('dist', 'lint', 'test')
    version: str = '@github_checkpoint_version@'


@dataclass(slots=True, frozen=True, eq=True)
class HardenRunnerEndpoints(Default):
    """Endpoints used in the GitHub CI workflow."""

    # fmt: off
    checkpoint: str = '@github_checkpoint_endpoints@'  # noqa: B950
    draft: str = '@github_draft_endpoints@'  # noqa: B950
    release: str = '@github_release_endpoints@'  # noqa: B950
    provenance: str = '@github_provenance_endpoints@'  # noqa: B950
    publish: str = '@github_publish_endpoints@'  # noqa: B950
    # fmt: on


@dataclass(slots=True, frozen=True, eq=True)
class HardenRunner(Default):
    """Github Step-Security harden runner."""

    version: str = '@github_harden_runner_version@'
    endpoints: HardenRunnerEndpoints = HardenRunnerEndpoints()


@dataclass(slots=True, frozen=True, eq=True)
class GithubActionPyPI(Default):
    """pypa/gh-action-pypi-publish"""

    version: str = '@github_action_pypi_publish_version@'


@dataclass(slots=True, frozen=True, eq=True)
class GithubMetadata(Default):
    """Github specific CI metadata"""

    checkpoint: Checkpoint = Checkpoint()
    draft: Draft = Draft()
    gh_action_pypi_publish: GithubActionPyPI = GithubActionPyPI()
    harden_runner: HardenRunner = HardenRunner()
    slsa_provenance: GenerateProvenance = GenerateProvenance()
    provenance: Provenance = Provenance()
    publish: Publish = Publish()
    release: Release = Release()
