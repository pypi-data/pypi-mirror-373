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


"""
Truthy-Falsy Booleans
---------------------


Booleans whose "truthy" and "falsy" instances are distinct subtypes."""

import threading
from collections.abc import Hashable
from typing import cast, ClassVar, Final, final
from pythonic_fp.sentinels.novalue import NoValue
from ..subtypable import SBool

__all__ = [
    'TF_Bool',
    'T_Bool',
    'F_Bool',
    'ALWAYS',
    'NEVER',
    'TF_Boolean',
]

_novalue = NoValue()


class TF_Bool(SBool):
    """
    Truthy-Falsy Boolean
    --------------------

    Subclass of ``SBool`` whose truthy values and falsy values are
    different singleton subtypes.

    This type can also do (non-shortcut) Boolean logic using Python
    bitwise operators.
    """

    def __new__(cls, witness: object, flavor: Hashable = NoValue()) -> 'TF_Bool':
        """
        :param witness: Determines which subtype, ``T_Bool`` or ``F_Bool`` is returned.
        :param flavor: Ignored parameter, only two flavors, one truthy and one falsy.
        :returns: either The singleton truthy or singleton falsy subtypes.
        """
        if witness:
            return T_Bool()
        return F_Bool()

    def __repr__(self) -> str:
        if self:
            return 'ALWAYS'
        return 'NEVER'

    def __invert__(self) -> 'TF_Bool':
        if self:
            return F_Bool()
        return T_Bool()

    def __and__(self, other: int) -> SBool:
        if isinstance(other, TF_Bool):
            if self and other:
                return T_Bool()
            return F_Bool()
        return SBool(self and other)

    def __or__(self, other: int) -> SBool:
        if isinstance(other, TF_Bool):
            if self or other:
                return T_Bool()
            return F_Bool()
        return SBool(self or other)

    def __xor__(self, other: int) -> SBool:
        if isinstance(other, TF_Bool):
            if not (self and other) and (self or other):
                return T_Bool()
            return F_Bool()
        return SBool(not (self and other) and (self or other))


@final
class T_Bool(TF_Bool):
    """
    Truthy TF_Bool
    --------------

    The subtype of ``TF_Bool`` which is always truthy.
    """

    _truthy: 'ClassVar[T_Bool | NoValue]' = _novalue
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __new__(
        cls, witness: object = _novalue, flavor: Hashable = _novalue
    ) -> 'T_Bool':
        """

        :param witness: Ignored parameter, a T_Bool is always truthy.
        :param flavor: Ignored parameter, only one truthy "flavor".
        :returns: The truthy ``T_Bool`` singleton instance.

        """
        if cls._truthy is _novalue:
            with cls._lock:
                if cls._truthy is _novalue:
                    cls._truthy = super(SBool, cls).__new__(cls, True)
        return cast(T_Bool, cls._truthy)

    def __repr__(self) -> str:
        return 'ALWAYS'


@final
class F_Bool(TF_Bool):
    """
    Falsy TF_Bool
    -------------

    The subtype of ``TF_Bool`` which is always falsy.
    """

    _falsy: 'ClassVar[F_Bool | NoValue]' = _novalue
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __new__(
        cls, witness: object = _novalue, flavor: Hashable = _novalue
    ) -> 'F_Bool':
        """
        :param witness: Parameter ignored, an ``F_Bool`` is always falsy.
        :param flavor: Parameter ignored, only one falsy "flavor".
        :returns: The falsy ``F_Bool`` singleton instance.
        """
        if cls._falsy is _novalue:
            with cls._lock:
                if cls._falsy is _novalue:
                    cls._falsy = super(SBool, cls).__new__(cls, False)
        return cast(F_Bool, cls._falsy)

    def __repr__(self) -> str:
        return 'NEVER'


TF_Boolean = T_Bool | F_Bool | TF_Bool  #: Use only as a type, never a constructor.

ALWAYS: Final[TF_Boolean] = T_Bool()  #: The truthy singleton ``TF_Bool`` subtype.
NEVER: Final[TF_Boolean] = F_Bool()  #: The falsy singleton ``TF_Bool`` subtype.
