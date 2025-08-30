# ozi/spec/_spec.py
# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: Unlicense
"""Specification API for OZI Metadata."""
from dataclasses import dataclass
from dataclasses import field
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version

from ozi_spec.base import Default
from ozi_spec.ci import RuffLint
from ozi_spec.project import ClassicProject
from ozi_spec.project import PythonProject
from ozi_spec.python import PythonSupport


def _current_version() -> str:
    """Returns the currently installed version of ozi-spec."""
    try:
        version_ = version('ozi-spec')
    except PackageNotFoundError:  # pragma: no cover
        version_ = '1.0'
    return version_


def _ozi_version() -> str:
    """Returns the current OZI release branch."""
    (
        major,
        minor,
        *_,
    ) = _current_version().split('.')
    if int(major) == 0:  # pragma: no cover
        return f'{int(major) + 1}.{int(minor) + 13}'
    return f'{int(major) + 1}.{int(minor)}'


@dataclass(slots=True, frozen=True, eq=True)
class Spec(Default):
    """OZI Specification metadata."""

    version: str = field(
        default_factory=_current_version,
        metadata={'help': 'OZI specification standard version.'},
    )
    python: PythonProject = ClassicProject()


@dataclass(slots=True, frozen=True, eq=True)
class Experimental(Default):
    """Experimental OZI specifications."""

    ruff: RuffLint = RuffLint()


@dataclass(slots=True, frozen=True, eq=True)
class OZI(Default):
    """OZI distribution metadata."""

    version: str = field(
        default_factory=_ozi_version,
        metadata={'help': 'Current release branch of the OZI package.'},
    )
    python_support: PythonSupport = PythonSupport()
    experimental: Experimental = Experimental()


@dataclass(slots=True, frozen=True, eq=True)
class Metadata(Default):
    """OZI metadata."""

    ozi: OZI = OZI()
    spec: Spec = field(default_factory=Spec)
