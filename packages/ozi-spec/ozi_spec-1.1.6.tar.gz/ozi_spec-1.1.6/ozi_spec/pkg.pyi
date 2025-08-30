# ozi/spec/pkg.py
# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: Unlicense
"""Package specification metadata."""
from __future__ import annotations

from collections.abc import Sequence  # noqa: TCH003,TC003,RUF100
from dataclasses import dataclass
from dataclasses import field

from ozi_spec._license import SPDX_LICENSE_EXCEPTIONS
from ozi_spec._license import SPDX_LICENSE_MAP
from ozi_spec.base import Default

@dataclass(slots=True, frozen=True, eq=True, repr=False)
class PkgVersion(Default):
    """Versioning metadata.

    .. versionchanged:: OZI 1.5
       Default to `angular` semantic instead of `emoji`.

    .. versionchanged:: 0.23
       Default to `conventional` commit semantic, remove ``major_tags`` key.
    """

    semantic: str = 'conventional'
    allowed_tags: tuple[str, ...] = (
        'build',
        'chore',
        'ci',
        'docs',
        'feat',
        'fix',
        'perf',
        'style',
        'refactor',
        'test',
    )
    minor_tags: tuple[str, ...] = ('feat',)
    patch_tags: tuple[str, ...] = ('fix', 'perf', 'build')


@dataclass(slots=True, frozen=True, eq=True)
class PkgRequired(Default):
    """Required files for OZI project publishing."""

    root: tuple[str, ...] = (
        'README',
        'CHANGELOG.md',
        'pyproject.toml',
        'LICENSE.txt',
        '.gitignore',
    )

    source: tuple[str, ...] = ('__init__.py',)

    test: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True, eq=True)
class PkgPattern(Default):
    """Regex patterns (or deferrals) for PKG-INFO headers."""

    name: str = r'^([A-Za-z]|[A-Za-z][A-Za-z0-9._-]*[A-Za-z0-9]){1,80}$'
    version: str = r'^(?P<prefix>v)?(?P<version>[^\\+]+)(?P<suffix>.*)?$'
    keywords: str = r'^(([a-z_]*[a-z0-9],)*{2,650})$'
    email: str = 'defer to RFC'
    license: str = 'defer to SPDX'
    license_id: str = 'defer to SPDX'
    license_exception_id = 'defer to SPDX'
    url: str = 'defer to IDNA'
    author: str = r'^((.+?)(?:,\s*|$)){1,128}$'
    summary: str = r'^(.*){1,255}$'
    copyright_head: str = r'^(.*){1,255}$'
    classifiers: str = r'^([\w\s]*\s\:\:\s)?'


@dataclass(slots=True, frozen=True, eq=True)
class PkgClassifiers(Default):
    """PKG-INFO default classifier metadata."""

    intended_audience: list[str] = field(default_factory=lambda: ['Other Audience'])
    typing: list[str] = field(default_factory=lambda: ['Typed'])
    environment: list[str] = field(default_factory=lambda: ['Other Environment'])
    language: list[str] = field(default_factory=lambda: ['English'])
    development_status: tuple[str] = ('1 - Planning',)


@dataclass(slots=True, frozen=True, eq=True)
class PkgInfo(Default):
    """PKG-INFO defaults metadata.

    .. versionchanged:: 0.23
       Remove deprecated required value ``Home-page``.

    """

    required: tuple[str, ...] = (
        'Author',
        'Author-email',
        'Description-Content-Type',
        'License',
        'Metadata-Version',
        'Name',
        'Summary',
        'Version',
    )
    classifiers: PkgClassifiers = PkgClassifiers()


@dataclass(slots=True, frozen=True, eq=True)
class License(Default):
    """Licensing specification metadata.

    .. versionchanged:: 0.10
       Add ``spdx_version`` key to track SPDX asset version.

    .. versionchanged:: 0.23
       Key ``exceptions`` is now a mapping from exception name to applicable licenses.
    """
    spdx_version: str = '3.26.0'
    ambiguous: dict[str, Sequence[str]] = SPDX_LICENSE_MAP
    exceptions: dict[str, tuple[str, ...]] = SPDX_LICENSE_EXCEPTIONS

@dataclass(slots=True, frozen=True, eq=True, repr=False)
class Pkg(Default):
    """Packaging specification metadata."""

    wheel: bool = True
    sdist: bool = True
    required: PkgRequired = PkgRequired()
    license: License = License()
    pattern: PkgPattern = PkgPattern()
    version: PkgVersion = PkgVersion()
    info: PkgInfo = PkgInfo()
