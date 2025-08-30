# ozi/spec/base.py
# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: Unlicense
"""Base dataclasses for OZI Metadata."""
from __future__ import annotations

import reprlib
from dataclasses import MISSING
from dataclasses import Field
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import fields
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import Iterator
from typing import Protocol
from typing import TypeAlias
from typing import TypeVar

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable
    from collections.abc import Mapping

    VT = TypeVar(
        'VT',
        str,
        int,
        float,
        bytes,
        None,
    )
    _Val: TypeAlias = list['_Key[VT]'] | Mapping['_Key[VT]', VT] | VT
    _Key: TypeAlias = VT | _Val[VT]
    _Lambda: TypeAlias = Callable[[], '_FactoryMethod']
    _FactoryMethod: TypeAlias = Callable[[], _Lambda]


class _FactoryDataclass(Protocol):
    """A dataclass that, when called, returns a factory method."""

    ...
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]

    def asdict(self: _FactoryDataclass) -> Mapping[str, _Val[str]]: ...  # noqa: DC102

    def __call__(self: _FactoryDataclass) -> Field[_FactoryMethod]: ...  # noqa: DC104

    def __iter__(  # noqa: DC104
        self: _FactoryDataclass,
    ) -> Iterator[tuple[str, _Val[VT]]]: ...


def get_default(obj: _FactoryDataclass, name: str) -> _Val[VT] | Mapping[str, _Val[str]]:
    """Get a field from a Default by name.

    :param obj: a target object
    :type obj: _FactoryDataclass
    :param name: an attribute name
    :type name: str
    :return: attribute value
    :rtype: _Val[VT] | Mapping[str, _Val[str]]
    """
    default = getattr(obj, name)
    if not isinstance(default, Default):
        return default
    else:
        return default.asdict()


@dataclass(frozen=True, repr=False)
class Default(_FactoryDataclass):
    """A dataclass that, when called, returns it's own default factory field."""

    def __call__(
        self: _FactoryDataclass,
    ) -> Field[_FactoryMethod]:  # pragma: defer to python
        """Returns this dataclass as a Field.

        :return: A Field initialized with a factory method.
        :rtype: Field[_FactoryMethod]
        """
        return Field(
            default=MISSING,
            default_factory=self,  # type: ignore
            init=True,
            repr=True,
            hash=None,
            compare=True,
            metadata={'help': str(self.__class__.__doc__).replace('\n   ', '')},
            kw_only=MISSING,  # type: ignore
        )

    def __iter__(self: _FactoryDataclass) -> Iterator[tuple[str, _Val[VT]]]:
        """Iterate through all fields.

        :yield: Fields as a tuple of name and values
        :rtype: Iterator[tuple[str, _Val[VT]]]
        """
        for f in fields(self):  # pragma: no cover
            if f.repr:
                yield (f.name, get_default(self, f.name))

    def asdict(
        self: _FactoryDataclass,
    ) -> Mapping[str, _Val[str]]:  # pragma: no cover
        """Return a dictionary of all fields where repr=True.
        Hide a variable from the dict by setting repr to False and using
        a Default subclass as the default_factory.
        Typing is compatible with JSON and Jinja2 global namespace.

        .. seealso::

           :std:ref:`jinja2:global-namespace`
        """
        return dict(iter(self)) | {
            'help': str(self.__class__.__doc__).replace('\n   ', ''),
        }

    def __repr__(self: _FactoryDataclass) -> str:
        """Uses reprlib.repr with the default limits."""
        return reprlib.repr(self)

    def __len__(self: _FactoryDataclass) -> int:  # pragma: defer to python
        """Get the total number of keys, including the class docstring."""
        return len(list(iter(asdict(self))))
