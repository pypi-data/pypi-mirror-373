# ozi/spec/_spec.py
# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: Unlicense
"""Specification API for OZI Metadata."""
from dataclasses import dataclass
from dataclasses import field

from ozi_spec.base import Default
from ozi_spec.ci import RuffLint
from ozi_spec.project import ClassicProject
from ozi_spec.project import PythonProject
from ozi_spec.python import PythonSupport

@dataclass(slots=True, frozen=True, eq=True)
class Spec(Default):
    """OZI Specification metadata."""

    version: str = '1.x'
    python: PythonProject = ClassicProject()

@dataclass(slots=True, frozen=True, eq=True)
class Experimental(Default):
    """Experimental OZI specifications."""

    ruff: RuffLint = RuffLint()

@dataclass(slots=True, frozen=True, eq=True)
class OZI(Default):
    """OZI distribution metadata."""

    version: str = '2.x'
    python_support: PythonSupport = PythonSupport()
    experimental: Experimental = Experimental()

@dataclass(slots=True, frozen=True, eq=True)
class Metadata(Default):
    """OZI metadata."""

    ozi: OZI = OZI()
    spec: Spec = field(default_factory=Spec)
