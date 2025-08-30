# ozi/spec/ci.py
# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: Unlicense
"""Continuous integration specification."""
from __future__ import annotations

from collections.abc import Mapping  # noqa: TCH003,TC003,RUF100
from dataclasses import dataclass
from dataclasses import field

from ozi_spec.base import Default

@dataclass(slots=True, frozen=True, eq=True)
class Publish(Default):
    """Publishing patterns for packaged project."""

    include: tuple[str, ...] = ('*.tar.gz', '*.whl', 'sig/*')
    version: str = '4f60b808859fd63bd4be3bb9cc3e34d7a14c3bf7'

@dataclass(slots=True, frozen=True, eq=True)
class Draft(Default):
    """Draft release patterns for packaged project."""

    version: str = '4f3dcb71f8251f1e8238eb011aa12dd6a9020d23'

@dataclass(slots=True, frozen=True, eq=True)
class Release(Default):
    """Release patterns for packaged project."""

    version: str = 'eb10d9730ae9ad7c7c63e016d714013b4e017d5d'

@dataclass(slots=True, frozen=True, eq=True)
class GenerateProvenance(Default):
    """SLSA provenance generator metadata.

    .. versionadded:: 0.11.7
    """

    version: str = 'v2.0.0'

@dataclass(slots=True, frozen=True, eq=True)
class Provenance(Default):
    """Github provenance generator metadata.

    .. versionadded:: 1.1
    """

    version: str = 'a7369a6ef4a56f442b97615539b8de23dcb1e94e'

@dataclass(slots=True, frozen=True, eq=True)
class Checkpoint(Default):
    """Checkpoint suites to run."""

    suites: tuple[str, ...] = ('dist', 'lint', 'test')
    version: str = 'bc80bd040b1b6705a270fc6b111b08dfe6cde16b'

@dataclass(slots=True, frozen=True, eq=True)
class HardenRunnerEndpoints(Default):
    """Endpoints used in the GitHub CI workflow."""

    # fmt: off
    checkpoint: str = 'files.pythonhosted.org:443 github.com:443 api.github.com:443 oziproject.dev:443 www.oziproject.dev:443 pypi.org:443 registry.npmjs.org:443 objects.githubusercontent.com:443 fulcio.sigstore.dev:443 rekor.sigstore.dev:443 tuf-repo-cdn.sigstore.dev:443 release-assets.githubusercontent.com:443'  # noqa: B950
    draft: str = 'api.github.com:443 github.com:443'  # noqa: B950
    release: str = 'api.github.com:443 files.pythonhosted.org:443 fulcio.sigstore.dev:443 github.com:443 pypi.org:443 rekor.sigstore.dev:443 tuf-repo-cdn.sigstore.dev:443 oziproject.dev:443 www.oziproject.dev:443 objects.githubusercontent.com:443 quay.io:443 cdn01.quay.io:443 cdn02.quay.io:443 cdn03.quay.io:443 downloads.python.org:443 release-assets.githubusercontent.com:443'  # noqa: B950
    provenance: str = 'github.com:443 api.github.com:443 upload.pypi.org:443 uploads.github.com:443 rekor.sigstore.dev:443 tuf-repo-cdn.sigstore.dev:443 fulcio.sigstore.dev:443 ghcr.io:443 pkg-containers.githubusercontent.com:443'  # noqa: B950
    publish: str = 'github.com:443 api.github.com:443 upload.pypi.org:443 uploads.github.com:443 tuf-repo-cdn.sigstore.dev:443 fulcio.sigstore.dev:443 rekor.sigstore.dev:443 ghcr.io:443 pkg-containers.githubusercontent.com:443'  # noqa: B950
    # fmt: on

@dataclass(slots=True, frozen=True, eq=True)
class HardenRunner(Default):
    """Github Step-Security harden runner."""

    version: str = 'ec9f2d5744a09debf3a187a3f4f675c53b671911'
    endpoints: HardenRunnerEndpoints = HardenRunnerEndpoints()

@dataclass(slots=True, frozen=True, eq=True)
class GithubActionPyPI(Default):
    """pypa/gh-action-pypi-publish"""

    version: str = '76f52bc884231f62b9a034ebfe128415bbaabdfc'

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
