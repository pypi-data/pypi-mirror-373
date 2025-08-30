# ozi/spec/python.py
# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: Unlicense
"""Python support specification metadata."""
from __future__ import annotations

import platform
from dataclasses import dataclass
from dataclasses import field
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from functools import cached_property
from typing import TYPE_CHECKING
from typing import Protocol
from typing import Sequence
from warnings import warn

from ozi_spec.base import Default
from ozi_spec.base import _FactoryDataclass

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Mapping

pymajor, pyminor, pypatch = map(int, platform.python_version_tuple())
DATE_FORMAT = '%Y-%m-%d'
DEPRECATION_DELTA_WEEKS = 104


class _PythonSupport(_FactoryDataclass, Protocol):  # noqa: DC101
    deprecation_schedule: dict[int, str]
    major: str
    current_date: str

    @cached_property
    def _minor_versions(self: _PythonSupport) -> list[int]: ...  # noqa: DC103
    @property
    def bugfix_minor(self: _PythonSupport) -> int: ...  # noqa: DC102
    @property
    def bugfix(self: _PythonSupport) -> str: ...  # noqa: DC102
    @property
    def security1_minor(self: _PythonSupport) -> int: ...  # noqa: DC102
    @property
    def security1(self: _PythonSupport) -> str: ...  # noqa: DC102
    @property
    def security2_minor(self: _PythonSupport) -> int: ...  # noqa: DC102
    @property
    def security2(self: _PythonSupport) -> str: ...  # noqa: DC102
    @property
    def prerelease_minor(self: _PythonSupport) -> int | None: ...  # noqa: DC102
    @property
    def prerelease(self: _PythonSupport) -> str: ...  # noqa: DC102
    @property
    def classifiers(self: _PythonSupport) -> Sequence[tuple[str, str]]: ...  # noqa: DC102


@dataclass(frozen=True, slots=True, eq=True)
class PythonSupport(Default, _PythonSupport):
    """Python version support for the OZI toolchain."""

    deprecation_schedule: dict[int, str] = field(
        default_factory=lambda: {
            8: date(2024, 10, 1).strftime(DATE_FORMAT),
            9: date(2025, 10, 1).strftime(DATE_FORMAT),
            10: date(2026, 10, 1).strftime(DATE_FORMAT),
            11: date(2027, 10, 1).strftime(DATE_FORMAT),
            12: date(2028, 10, 1).strftime(DATE_FORMAT),
            13: date(2029, 10, 1).strftime(DATE_FORMAT),
            14: date(2030, 10, 1).strftime(DATE_FORMAT),
        },
    )
    major: str = field(init=False, default='3')
    current_date: str = field(
        init=False,
        compare=False,
        default_factory=lambda: datetime.now(tz=timezone.utc).date().strftime(DATE_FORMAT),
    )

    def __post_init__(self: _PythonSupport) -> None:
        """Warn the user if the python version is deprecated or pending deprecation.

        :raises: FutureWarning
        """
        python3_eol = (
            datetime.strptime(
                self.deprecation_schedule.get(
                    pyminor,
                    date(2008, 12, 3).strftime(DATE_FORMAT),
                ),
                DATE_FORMAT,
            )
            .replace(tzinfo=timezone.utc)
            .date()
        )
        ozi_support_eol = python3_eol - timedelta(weeks=DEPRECATION_DELTA_WEEKS)
        if datetime.now(tz=timezone.utc).date() > python3_eol:  # pragma: no cover
            warn(
                f'Python {pymajor}.{pyminor}.{pypatch} is not supported as of {python3_eol}.',
                FutureWarning,
            )
        elif datetime.now(tz=timezone.utc).date() > ozi_support_eol:  # pragma: no cover
            warn(
                f'Python {pymajor}.{pyminor}.{pypatch} support is pending deprecation '
                f'as of {ozi_support_eol}.',
                FutureWarning,
            )

    @cached_property
    def _minor_versions(self: _PythonSupport) -> list[int]:
        """List of currently supported Python minor version integers."""
        return sorted(
            [
                k
                for k, v in self.deprecation_schedule.items()
                if datetime.strptime(v, DATE_FORMAT).replace(tzinfo=timezone.utc)
                - timedelta(weeks=DEPRECATION_DELTA_WEEKS)
                > datetime.strptime(self.current_date, DATE_FORMAT).replace(
                    tzinfo=timezone.utc,
                )
            ],
        )[:4]

    @property
    def bugfix_minor(self: _PythonSupport) -> int:
        """Minor version integer for current bugfix Python release."""
        _, _, bugfix, *_ = self._minor_versions
        return bugfix

    @property
    def bugfix(self: _PythonSupport) -> str:
        """Version string for current bugfix Python release."""
        return '.'.join(map(str, (self.major, self.bugfix_minor)))

    @property
    def security1_minor(self: _PythonSupport) -> int:
        """Minor version integer for the most current security Python release."""
        _, security1, *_ = self._minor_versions
        return security1

    @property
    def security1(self: _PythonSupport) -> str:
        """Version string for the most current security Python release."""
        return '.'.join(map(str, (self.major, self.security1_minor)))

    @property
    def security2_minor(self: _PythonSupport) -> int:
        """Minor version integer for the second most current security Python release."""
        security2, *_ = self._minor_versions
        return security2

    @property
    def security2(self: _PythonSupport) -> str:
        """Version string for the second most current security Python release."""
        return '.'.join(map(str, (self.major, self.security2_minor)))

    @property
    def prerelease_minor(self: _PythonSupport) -> int | None:
        """Minor version integer for current prerelease Python release."""
        _, _, _, *prerelease = self._minor_versions
        return prerelease[0] if prerelease else None

    @property
    def prerelease(self: _PythonSupport) -> str:
        """Version string for current prerelease Python release."""
        if self.prerelease_minor:  # pragma: no cover
            return '.'.join(map(str, (self.major, self.prerelease_minor)))
        return ''  # pragma: defer to good-first-issue

    @property
    def classifiers(self: _PythonSupport) -> Sequence[tuple[str, str]]:  # pragma: no cover
        """Version classifiers for all currently supported Python releases."""
        classifiers = [
            ('Classifier', f'Programming Language :: Python :: {self.major} :: Only'),
            (
                'Classifier',
                f'Programming Language :: Python :: {self.security2}',
            ),
            (
                'Classifier',
                f'Programming Language :: Python :: {self.security1}',
            ),
            (
                'Classifier',
                f'Programming Language :: Python :: {self.bugfix}',
            ),
        ]
        if self.prerelease_minor:  # pragma: defer to spec
            classifiers += [
                ('Classifier', f'Programming Language :: Python :: {self.prerelease}'),
            ]
        return classifiers


_python_support = PythonSupport()


@dataclass(slots=True, frozen=True, eq=True)
class Support(Default):
    """Python implementation and version support info for OZI-packaged projects."""

    classifiers: Sequence[tuple[str, str]] = field(
        default_factory=lambda: _python_support.classifiers,
    )
    implementations: tuple[str, ...] = ('CPython',)
    metadata_version: str = '2.1'
    major: str = '3'
    prerelease: str = _python_support.prerelease
    bugfix: str = _python_support.bugfix
    security1: str = _python_support.security1
    security2: str = _python_support.security2
    deprecation_schedule: Mapping[int, str] = field(
        default_factory=lambda: _python_support.deprecation_schedule,
    )
    deprecation_delta_weeks: int = DEPRECATION_DELTA_WEEKS
