# ozi/spec/__init__.py
# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: Unlicense
"""Specification API for OZI Metadata."""
from ozi_spec._spec import OZI
from ozi_spec._spec import Metadata
from ozi_spec._spec import Spec
from ozi_spec.base import Default
from ozi_spec.src import CommentPatterns

__all__ = (
    'CommentPatterns',
    'Default',
    'METADATA',
    'Metadata',
    'OZI',
    'Spec',
)

METADATA = Metadata()
