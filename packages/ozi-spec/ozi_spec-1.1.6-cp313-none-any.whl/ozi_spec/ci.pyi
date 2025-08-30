# ozi_spec/ci.pyi
# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: Unlicense
from __future__ import annotations

from collections.abc import Mapping  # noqa: TCH003,TC003,RUF100
from dataclasses import dataclass
from dataclasses import field

from ozi_spec.base import Default
from ozi_spec.github_ci import GithubMetadata

@dataclass(slots=True, frozen=True, eq=True)
class CheckpointSuite(Default):
    """OZI checkpoint base class."""

    exclude: tuple[str, ...] = field(default_factory=tuple)
    module: tuple[str, ...] = field(default_factory=tuple)
    plugin: Mapping[str, str] = field(default_factory=dict)
    utility: Mapping[str, str] = field(default_factory=dict)
    ignore: tuple[str, ...] = field(default_factory=tuple)

@dataclass(slots=True, frozen=True, eq=True)
class RuffLint(CheckpointSuite):
    """OZI experimental linting and formatting with ruff.
    The goal is parity with the classic lint suite.
    """

    ignore: tuple[str, ...] = (
        'A003',
        'ARG',
        'ANN401',
        'TRY003',
        'B028',
        'B905',
        'D1',
        'D2',
        'D101',
        'D4',
        'FLY',
        'FBT',
        'PGH003',
        'PLR',
        'RET',
        'EM',
        'PLW',
        'PTH',
        'RUF009',
        'RUF012',
        'RUF015',
        'RUF200',
        'SIM',
        'T201',
        'TCH002',
        'TCH004',
        'UP',
        'PERF203',
    )
    module: tuple[str, ...] = ('ruff', 'mypy', 'pyright')
    exclude: tuple[str, ...] = ('meson-private',)
    utility: Mapping[str, str] = field(
        default_factory=lambda: {
            'ruff': 'ruff>=0.1.6',
            'mypy': 'mypy',
            'pyright': 'pyright',
        },
    )

@dataclass(slots=True, frozen=True, eq=True)
class ClassicLint(CheckpointSuite):
    """OZI standard linting and formatting suite."""

    ignore: tuple[str, ...] = ('E203', 'E501', 'TC007', 'TC008')
    module: tuple[str, ...] = ('bandit', 'black', 'flake8', 'isort', 'mypy', 'pyright')
    exclude: tuple[str, ...] = ('venv', 'meson-private', 'subprojects')
    utility: Mapping[str, str] = field(
        default_factory=lambda: {
            'bandit': 'bandit[toml]',
            'black': 'black>=24.3',
            'flake8': 'flake8',
            'isort': 'isort',
            'mypy': 'mypy',
            'pyright': 'pyright',
            'readme-renderer': 'readme-renderer[md]',
        },
    )
    plugin: Mapping[str, str] = field(
        default_factory=lambda: {
            'Flake8-pyproject': 'Flake8-pyproject',
            'flake8-annotations': 'flake8-annotations',
            'flake8-broken-line': 'flake8-broken-line',
            'flake8-bugbear': 'flake8-bugbear',
            'flake8-comprehensions': 'flake8-comprehensions',
            'flake8-datetimez': 'flake8-datetimez',
            'flake8-docstring-checker': 'flake8-docstring-checker',
            'flake8-eradicate': 'flake8-eradicate',
            'flake8-fixme': 'flake8-fixme',
            'flake8-leading-blank-lines': 'flake8-leading-blank-lines',
            'flake8-no-pep420': 'flake8-no-pep420',
            'flake8-pyi': 'flake8-pyi',
            'flake8-pytest-style': 'flake8-pytest-style',
            'flake8-quotes': 'flake8-quotes',
            'flake8-tidy-imports': 'flake8-tidy-imports',
            'flake8-type-checking': 'flake8-type-checking',
        },
    )

@dataclass(slots=True, frozen=True, eq=True)
class ClassicTest(CheckpointSuite):
    """OZI standard testing and coverage."""

    module: tuple[str, ...] = ('coverage', 'pytest')
    plugin: Mapping[str, str] = field(
        default_factory=lambda: {
            'hypothesis': 'hypothesis[all]',
            'pytest-asyncio': 'pytest-asyncio',
            'pytest-cov': 'pytest-cov',
            'pytest-randomly': 'pytest-randomly',
            'pytest-tcpclient': 'pytest-tcpclient',
            'pytest-xdist': 'pytest-xdist',
        },
    )
    utility: Mapping[str, str] = field(
        default_factory=lambda: {
            'coverage': 'coverage[toml]',
            'pytest': 'pytest',
        },
    )

@dataclass(slots=True, frozen=True, eq=True)
class ClassicDist(CheckpointSuite):
    """OZI standard publishing and distribution.

    .. versionchanged:: 0.6
        Added ``cibuildwheel`` and ``twine`` as plugins.

    .. versionchanged:: 0.10
        Moved ``cibuildwheel`` and ``twine`` to utility.
    """

    module: tuple[str, ...] = ('python-semantic-release', 'sigstore')
    utility: Mapping[str, str] = field(
        default_factory=lambda: {
            'python-semantic-release': 'python-semantic-release~=9.14.0',
            'sigstore': 'sigstore',
            'twine': 'twine',
            'cibuildwheel': 'cibuildwheel',
        },
    )
    plugin: Mapping[str, str] = field(
        default_factory=lambda: {},
    )

@dataclass(slots=True, frozen=True, eq=True)
class Build(Default):
    """Build backend and required packages for OZI.

    .. versionchanged:: 0.7
       Invoke added to build-system dependencies.

    .. versionchanged:: 0.8
       All build-system requires moved to OZI.build 1.2 as extra optional_dependencies.

    .. versionchanged:: 0.28
       Add meson key with meson version constraint.
    """

    backend: str = 'ozi_build.buildapi'
    meson: str = 'meson~=1.2,<1.9'
    requires: Mapping[str, str] = field(
        default_factory=lambda: {
            'OZI.build': 'OZI.build[core]~=2.3.2',
        },
    )

@dataclass(slots=True, frozen=True, eq=True)
class CI(Default):
    """Provider-agnostic CI information.

    .. versionchanged:: 0.16
       Moved provenance, gh_action_pypi_publish, and harden_runner to ``github``.

    .. versionchanged:: 1.1
       Moved workflow references into provider keys.
       Removed tox-gh from backend.
    """

    backend: Mapping[str, str] = field(
        default_factory=lambda: {
            'tox': 'tox~=4.18',
        },
    )
    providers: tuple[str, ...] = ('github',)
    github: GithubMetadata = GithubMetadata()
