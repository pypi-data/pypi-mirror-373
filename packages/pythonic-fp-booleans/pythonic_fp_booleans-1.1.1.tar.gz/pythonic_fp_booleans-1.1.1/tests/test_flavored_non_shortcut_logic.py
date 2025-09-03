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

from pythonic_fp.booleans.subtypable import TRUTH, LIE
from pythonic_fp.booleans.subtypes.flavored import FBool, truthy, falsy


class TestBitwiseOperations():
    def test_or_not(self) -> None:
        assert truthy(0) is truthy(0) | truthy(0)
        assert truthy(0) == truthy(0) | truthy(0)
        assert TRUTH is truthy(0) | truthy(1)
        assert TRUTH == truthy(0) | truthy(1)
        assert falsy('foo') is ~truthy('foo')
        assert truthy(42) is ~truthy(42) | truthy(42)
        assert TRUTH is ~truthy(42) | truthy(False)
        assert falsy(3.14159) == ~truthy(42) | ~truthy(42)
        assert falsy(3.14159) is not ~truthy(42) | ~truthy(42)
        assert LIE == ~truthy('foo') | ~truthy('bar')
        assert LIE is ~truthy('foo') | ~truthy('bar')
        assert falsy(0) is ~truthy(0) | ~truthy(0)
        assert truthy(1) is truthy(1) | ~truthy(1)
        assert truthy(1) is ~truthy(1) | truthy(1)
        assert LIE is ~truthy(1) | ~truthy(-1)
        assert TRUTH is truthy(1) | ~truthy(-1)
        assert LIE is falsy(2) | falsy(3)
        assert LIE == falsy(2) | falsy(3)
        assert TRUTH is falsy(2) | ~falsy(3)
        assert TRUTH == falsy(2) | ~falsy(3)

        assert TRUTH is falsy(1) | truthy(1) | TRUTH | falsy(1) | falsy(1)
        assert truthy(1) is falsy(1) | truthy(1) | truthy(1) | falsy(1) | falsy(1)
        assert TRUTH is falsy(1) | truthy(1) | truthy(2) | falsy(1) | falsy(1)
        assert LIE is falsy(1)|falsy(1)|~truthy(1)|falsy(1)|~truthy(3)
        assert LIE is falsy(1)|falsy(1)|~truthy(1)|falsy(3)|~truthy(1)
        assert falsy(1) is falsy(1)|falsy(1)|~truthy(1)|falsy(1)|~truthy(1)

    def test_xor_not(self) -> None:
        assert LIE is truthy(1) ^ truthy(2)
        assert TRUTH is truthy(1) ^ ~truthy(2)
        assert falsy(3) is truthy(3) ^ truthy(3)
        assert FBool(10.0 == 5.0 + 5.0, 4) is truthy(4) ^ ~ truthy(4)
        assert truthy(0) is ~truthy(0) ^ truthy(0)
        assert falsy(1) is ~ truthy(1) ^ ~truthy(1)
        assert falsy(2) is ~truthy(2) ^ falsy(2)
        assert truthy(3) is falsy(3) ^ ~falsy(3)
        assert falsy(4) is ~truthy(4) ^ falsy(4)
        assert falsy(5) is falsy(5) ^ falsy(5)

        lie = LIE
        lie1 = falsy(1)
        lie2 = falsy(2)
        truth = TRUTH
        truth1 = truthy(1)
        truth2 = truthy(2)

        assert truth1 is lie1 ^ lie1 ^ truth1 ^ lie1 ^ lie1
        assert lie is lie1 ^ lie2 ^ ~truth1 ^ lie1 ^ ~truth2
        assert truth is lie1 ^ lie2 ^ ~truth1 ^ lie1 ^ truth2 ^ lie1
        assert lie is lie1 ^ lie2 ^ ~truth1 ^ lie1 ^ truth2 ^ truth1
        assert lie1 is lie1 ^ lie1 ^ ~truth1 ^ lie1 ^ truth1 ^ truth1

    def test_and_not(self) -> None:
        lie = LIE
        lie1 = falsy(1)
        lie2 = falsy(2)
        truth = TRUTH
        truth1 = truthy(1)
        truth2 = truthy(2)

        assert truth1 is truth1 & truth1
        assert truth is truth2 & truth
        assert lie2 is truth2 & ~truth2
        assert lie is ~truth1 & truth2
        assert lie is ~truth1 & ~truth2
        assert truth is truth1 & ~lie2
        assert truth1 is truth1 & ~lie1
        assert lie is lie2 & ~lie1
        assert lie is ~truth2 & lie1
        assert lie1 is lie1 & lie1
        assert lie2 is lie2 & lie2
        assert lie is lie2 & lie1

        assert LIE == lie1 & lie2 & truth2 & lie1 & lie1
        assert TRUTH == ~lie1 & ~lie2 & truth1 & ~lie2 & ~lie1

    def test_de_morgan(self) -> None:
        lie1 = falsy(1)
        lie2 = falsy(2)
        truth1 = truthy(1)
        truth2 = truthy(2)

        for sb1 in [truth1, lie1]:
            for sb2 in [truth2, lie2]:
                ~(sb1 & sb2) is ~sb1 | ~sb2
                ~(sb1 | sb2) is ~sb1 & ~sb2

        for sb1 in [truth1, lie1]:
            for sb2 in [truth2, lie2]:
                ~(sb1 & sb2) is ~sb1 | ~sb2
                ~(sb1 | sb2) is ~sb1 & ~sb2
