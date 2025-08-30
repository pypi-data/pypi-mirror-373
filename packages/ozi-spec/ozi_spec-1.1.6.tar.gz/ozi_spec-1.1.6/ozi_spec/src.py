# ozi/spec/src.py
# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: Unlicense
"""Source specification metadata."""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Mapping

from ozi_spec.base import Default


@dataclass(slots=True, frozen=True, eq=True)
class SrcFormat(Default):
    """Python source code formatting specification."""

    date: str = '%Y-%m-%d %H:%M:%S'
    line_end: str = 'LF'
    quotes: str = 'single'
    log: str = '%(asctime)s [%(levelname)8s] %(name)s: %(message)s (%(filename)s:%(lineno)s)'
    max_line_length: int = 93
    version_placeholder: str = '{version}'
    max_complexity: int = 6
    min_coverage: float = 100.0
    single_line_imports: bool = True


@dataclass(slots=True, frozen=True, eq=True)
class SrcRequired(Default):
    """Required files for OZI to output with ``ozi-new``.

    .. versionchanged:: 0.9
        Removed :file:`requirements.in` from `root`.
    """

    root: tuple[str, ...] = (
        'README',
        '.gitignore',
        'pyproject.toml',
        'meson.build',
        'meson.options',
        'LICENSE.txt',
        'CHANGELOG.md',
    )
    source: tuple[str, ...] = (
        'meson.build',
        '__init__.py',
        'py.typed',
    )
    test: tuple[str, ...] = ('meson.build',)


@dataclass(slots=True, frozen=True, eq=True)
class SrcRepo(Default):
    """An OZI source repository."""

    hidden_dirs: tuple[str, ...] = ('.git', '.github')
    ignore_dirs: tuple[str, ...] = (
        '.mypy_cache',
        '.ruff_cache',
        '.pytest_cache',
        '.hypothesis',
        '.tox',
        '__pycache__',
    )


@dataclass(slots=True, frozen=True, eq=True)
class SrcTemplate(Default):
    """OZI templates folder layout.
    This is also the relative search directory used when searching
    for ``ozi-new`` user-provided templates in the ``templates/``
    root directory.

    .. versionchanged:: 0.5

        Added ``templates``, ``subprojects`` and modified ``ci_provider``
        to be a dictionary of tuples.

    .. versionchanged:: 0.9
        Removed :file:`requirements.in` from `root`.

    .. versionchanged:: 1.0
        Removed templates for changelog and release notes.

    """

    root: tuple[str, ...] = (
        '.gitignore',
        'meson.build',
        'meson.options',
        'pyproject.toml',
        'README',
        'LICENSE.txt',
        'CHANGELOG.md',
    )
    source: tuple[str, ...] = (
        'project.name/__init__.py',
        'project.name/meson.build',
        'project.name/py.typed',
    )
    test: tuple[str, ...] = ('tests/meson.build',)
    ci_provider: Mapping[str, tuple[str, ...]] = field(
        default_factory=lambda: {
            'github': ('.github/workflows/ozi.yml', '.github/workflows/cleanup.yml'),
        },
    )
    templates: tuple[str, ...] = ()
    subprojects: tuple[str, ...] = ('subprojects/ozi.wrap',)
    add_root: str = field(default='tests/new_test.py.j2')
    add_source: str = field(default='project.name/new_module.py.j2')
    add_test: str = field(default='tests/new_test.py.j2')


@dataclass(slots=True, frozen=True, eq=True)
class CommentPatterns(Default):
    """Search patterns for source comments."""

    flake8_noqa: str = r'^.*#\\s*(flake8|FLAKE8)[:\\s]?\\s(noqa|NOQA)'
    fmt_off: str = r'^.*#\\s*(fmt|FMT)[:\\s]?\\s(off|OFF)'
    fmt_on: str = r'^.*#\\s*(fmt|FMT)[:\\s]?\\s(on|ON)'
    fmt_skip: str = r'^.*#\\s*(fmt|FMT)[:\\s]?\\s(skip|SKIP)'
    isort_dont_add_import: str = (
        r'^.*#\\s*(isort|ISORT)[:\\s]?\\s(dont_add_import|DONT_ADD_IMPORT):\\s'
    )
    isort_dont_add_imports: str = (
        r'^.*#\\s*(isort|ISORT)[:\\s]?\\s(dont_add_imports|DONT_ADD_IMPORTS)'
    )
    isort_off: str = r'^.*#\\s*(isort|ISORT)[:\\s]?\\s(off|OFF)'
    isort_on: str = r'^.*#\\s*(isort|ISORT)[:\\s]?\\s(on|ON)'
    isort_skip_file: str = r'^.*#\\s*(isort|ISORT)[:\\s]?\\s(skip_file|SKIP-FILE)'
    isort_split: str = r'^.*#\\s*(isort|ISORT)[:\\s]?\\s(split|SPLIT)'
    mypy: str = r'^.*#\\s*(mypy|MYPY)[:\\s]?\\s[a-zA-Z0-9_-]*'
    noqa: str = r'^.*#\\s*(noqa|NOQA)[:\\s]?\\s[a-zA-Z0-9_]*'
    nosec: str = r'^.*#\\s*(nosec|NOSEC)'
    pragma_defer_to: str = (
        r'^.*#\\s*(pragma|PRAGMA)[:\\s]?\\s*(defer|DEFER)\\s*(to|TO)\\s*[a-zA-Z0-9_-]*'
    )
    pragma_no_cover: str = r'^.*#\\s*(pragma|PRAGMA)[:\\s]?\\s*(no|NO)\\s*(cover|COVER)'
    pyright_ignore: str = r'^.*#\\s*(pyright|PYRIGHT)[:\\s]?\\s(ignore|IGNORE)'
    type_ignore: str = r'^.*#\\s*(type|TYPE)[:\\s]?\\s(ignore|IGNORE)'


@dataclass(slots=True, frozen=True, eq=True)
class Src(Default):
    """Python source code metadata."""

    format: SrcFormat = SrcFormat()
    required: SrcRequired = SrcRequired()
    template: SrcTemplate = field(default_factory=SrcTemplate)
    allow_files: tuple[str, ...] = ('templates', '.git', '.pre-commit-config.yaml')
    repo: SrcRepo = SrcRepo()
    comments: CommentPatterns = CommentPatterns()
