# ozi/spec/project.py
# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: Unlicense
"""Project specification metadata."""
from dataclasses import dataclass

from ozi_spec.base import Default
from ozi_spec.ci import CI
from ozi_spec.ci import Build
from ozi_spec.ci import ClassicDist
from ozi_spec.ci import ClassicLint
from ozi_spec.ci import ClassicTest
from ozi_spec.pkg import Pkg
from ozi_spec.python import Support
from ozi_spec.src import Src


@dataclass(slots=True, frozen=True, eq=True, repr=False)
class PythonProject(Default):
    """Base class for Python Project specification metadata."""

    ci: CI = CI()
    support: Support = Support()
    dist: ClassicDist = ClassicDist()
    lint: ClassicLint = ClassicLint()
    test: ClassicTest = ClassicTest()
    build: Build = Build()
    pkg: Pkg = Pkg()
    src: Src = Src()


@dataclass(slots=True, frozen=True, eq=True, repr=False)
class ClassicProject(PythonProject):
    """OZI project using classic Python checkpoint toolchains."""


@dataclass(slots=True, frozen=True, eq=True, repr=False)
class RuffProject(PythonProject):
    """Alternative to classic project using ruff for linting and formatting."""

    lint: ClassicLint = ClassicLint(
        exclude=('meson-private',),
        module=('ruff', 'mypy', 'pyright'),
        plugin={},
        utility={'ruff': 'ruff>=0.1.6', 'mypy': 'mypy', 'pyright': 'pyright'},
        ignore=(
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
        ),
    )
