# Copyright 2023-2025 Geoffrey R. Scheller
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Subtypable Booleans."""

import threading
from collections.abc import Hashable
from typing import cast, ClassVar, Final, overload
from pythonic_fp.gadgets.latest_common_ancestor import lca
from pythonic_fp.sentinels.novalue import NoValue

__all__ = ['SBool', 'TRUTH', 'LIE']

_novalue = NoValue()


class SBool(int):
    """Subtypable Booleans.

    Like Python's built in bool, class SBool is a subclass of int.
    Unlike bool, this version can be further subclassed. It can be
    used with Python ``and`` and ``or`` short-cut logic. The ``not``
    operator will just return a ``bool``. Use the ``snot`` function
    to return an ``SBool`` or ``SBool`` subclass.

    This type and its subtypes can also do (non-shortcut) Boolean logic
    using Python bitwise operators.
    """
    _falsy: 'ClassVar[SBool | NoValue]' = _novalue
    _falsy_lock: ClassVar[threading.Lock] = threading.Lock()

    _truthy: 'ClassVar[SBool | NoValue]' = _novalue
    _truthy_lock: ClassVar[threading.Lock] = threading.Lock()

    @overload
    def __new__(cls) -> 'SBool': ...
    @overload
    def __new__(cls, witness: object) -> 'SBool': ...

    def __new__(cls, witness: object = False, flavor: Hashable = _novalue) -> 'SBool':
        """
        :param witness: Determines truthiness of the ``SBool``.
        :returns: The truthy or falsy SBool class instance.
        """
        if witness:
            if cls._truthy is _novalue:
                with cls._truthy_lock:
                    if cls._truthy is _novalue:
                        cls._truthy = super().__new__(cls, 1)
            return cast(SBool, cls._truthy)
        else:
            if cls._falsy is _novalue:
                with cls._falsy_lock:
                    if cls._falsy is _novalue:
                        cls._falsy = super().__new__(cls, 0)
            return cast(SBool, cls._falsy)

    def __init__(self, witness: object = False, flavor: Hashable = _novalue) -> None:
        self._flavor = flavor

    # override in derived classes
    def __repr__(self) -> str:
        if self:
            return 'TRUTH'
        return 'LIE'

    def __invert__(self) -> 'SBool':
        if self:
            return type(self)(False)
        return type(self)(True)

    def __and__(self, other: int) -> int:
        try:
            base_class = lca(type(self), type(other))
        except TypeError:
            if type(other) is bool:
                base_class = int
            else:
                msg = (
                    f"unsupported operand type(s) for &: '{type(self)}' and '{type(other)}'"
                )
                raise TypeError(msg)

        if issubclass(base_class, SBool):
            if self and other:
                return base_class(1)
            return base_class(0)
        else:
            return int(self) & int(other)

    def __or__(self, other: int) -> int:
        try:
            base_class = lca(type(self), type(other))
        except TypeError:
            if type(other) is bool:
                base_class = int
            else:
                msg = (
                    f"unsupported operand type(s) for |: '{type(self)}' and '{type(other)}'"
                )
                raise TypeError(msg)

        if issubclass(base_class, SBool):
            if self or other:
                return base_class(1)
            return base_class(0)
        else:
            return int(self) | int(other)

    def __xor__(self, other: int) -> int:
        try:
            base_class = lca(type(self), type(other))
        except TypeError:
            if type(other) is bool:
                base_class = int
            else:
                msg = (
                    f"unsupported operand type(s) for ^: '{type(self)}' and '{type(other)}'"
                )
                raise TypeError(msg)

        if issubclass(base_class, SBool):
            if self and not other or other and not self:
                return base_class(1)
            return base_class(0)
        else:
            return int(self) ^ int(other)


TRUTH: Final[SBool] = SBool(True)  #: The truthy singleton of type ``SBool``.
LIE: Final[SBool] = SBool(False)  #: The falsy singleton of type ``SBool``.
