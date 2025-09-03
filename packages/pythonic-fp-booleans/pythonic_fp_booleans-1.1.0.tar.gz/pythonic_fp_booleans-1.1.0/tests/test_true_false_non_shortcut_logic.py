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
from pythonic_fp.booleans.subtypes.truthy_falsy import TF_Boolean, TF_Bool, T_Bool, F_Bool
from pythonic_fp.booleans.subtypes.truthy_falsy import ALWAYS, NEVER

false0: TF_Boolean = F_Bool('ignored', 'also ignored')
false1: TF_Boolean = TF_Bool(1 > 42)
false2: TF_Boolean = F_Bool()
false3: TF_Boolean = TF_Bool('')
true0: TF_Boolean = T_Bool('', 'ignored')
true1: TF_Boolean = TF_Bool(1 < 42)
true2: TF_Boolean = T_Bool()
true3: TF_Boolean = TF_Bool('foobar')


class TestConfirmTruthiness():
    assert not false0
    assert not false1
    assert not false2
    assert not false3
    assert true0
    assert true1
    assert true2
    assert true3

class TestBitwiseOperations():
    def test_typed_identity(self) -> None:
        assert TRUTH == ALWAYS
        assert ALWAYS == ALWAYS
        assert ALWAYS != NEVER
        assert NEVER != ALWAYS
        assert NEVER == NEVER
        assert LIE == NEVER
        assert TRUTH is not ALWAYS
        assert ALWAYS is ALWAYS
        assert ALWAYS is not NEVER
        assert NEVER is not ALWAYS
        assert NEVER is NEVER
        assert LIE is not NEVER

        assert true1 == true1
        assert true1 == true2
        assert true2 == true1
        assert true2 == true2
        assert true1 is true1
        assert true1 is true2
        assert true2 is true1
        assert true2 is true2

        assert ALWAYS == true1 == true2
        assert NEVER == false1 == false2

    def test_or_not(self) -> None:
        assert true0 is true0 | true0
        assert true0 == true0 | true0
        assert ALWAYS is true0 | true1
        assert TRUTH == true0 | true1
        assert false3 is ~true2
        assert true3 is ~true3 | true3
        assert ALWAYS is ~true3 | true1
        assert LIE == ~true1 | ~true3
        assert LIE is not ~true1 | ~true3
        assert NEVER == ~true1 | ~true3
        assert NEVER is ~true1 | ~true3
        assert false3 is ~true2 | ~true0
        assert true1 is true1 | ~true1
        assert true2 is ~true1 | true1
        assert NEVER is ~true1 | false2
        assert ALWAYS is true1 | ~false0
        assert NEVER is false2 | false3
        assert NEVER == false2 | false3
        assert TRUTH is ~LIE | ~false2
        assert TRUTH is ~false2 | ~LIE
        assert TRUTH is ALWAYS | TRUTH
        assert TRUTH is TRUTH | ALWAYS
        assert TRUTH is ~NEVER | TRUTH
        assert TRUTH is ~false2 | TRUTH
        assert TRUTH is ~false2 | ~LIE
        assert LIE is false2 | LIE
        assert TRUTH == false2 | ~false3
        assert ALWAYS is false2 | ~false3

        assert TRUTH is false1 | true1 | TRUTH | false1 | false2
        assert true1 is false1 | true1 | true1 | false1 | false3
        assert TRUTH is false3 | true1 | true2 | LIE | false2
        assert NEVER is false1|false1|~true2|false1|~true3
        assert NEVER is false1|false1|~true1|false3|~true1
        assert ALWAYS is true1|false2|~true2|~true3|~true1

    def test_xor_not(self) -> None:
        assert NEVER is true1 ^ true2
        assert ALWAYS is true1 ^ ~true2
        assert false2 is true3 ^ true3
        assert TF_Bool(10.0 == 5.0 + 5.0) is true2 ^ ~ true1
        assert true0 is ~true0 ^ true0
        assert false1 is ~true1 ^ ~true1
        assert false2 is ~true2 ^ false2
        assert true3 is false3 ^ ~false3
        assert NEVER is ~true1^ false2
        assert NEVER is false0 ^ false1

        assert true1 is false1 ^ false1 ^ true1 ^ false1 ^ false1
        assert false2 is false1 ^ false2 ^ ~true1 ^ false1 ^ ~true2
        assert true3 is false1 ^ false2 ^ ~true1 ^ false1 ^ true2 ^ false1
        assert false0 is false1 ^ false2 ^ ~true1 ^ false1 ^ true2 ^ true1
        assert false1 is false1 ^ false1 ^ ~true1 ^ false1 ^ true1 ^ true1

    def test_and_not(self) -> None:
        assert true1 is true1 & true1
        assert true0 is true2 & true0
        assert false2 is true2 & ~true2
        assert false0 is ~true1 & true2
        assert false0 is ~true1 & ~true2
        assert true0 is true1 & ~false2
        assert true1 is true1 & ~false1
        assert false0 is false2 & ~false1
        assert false0 is ~true2 & false1
        assert false1 is false1 & false1
        assert false2 is false2 & false2
        assert false0 is false2 & false1

        assert NEVER is false1 & false2 & true2 & false1 & false1
        assert ALWAYS is ~false1 & ~false2 & true1 & ~false2 & ~false1

    def test_de_morgan(self) -> None:
        for tfb in [true1, false1]:
            for tf2 in [true1, false1]:
                ~(tfb & tf2) is ~tfb | ~tf2
                ~(tfb | tf2) is ~tfb & ~tf2

        for tfb in [true1, false1]:
            for tf2 in [true2, false2]:
                ~(tfb & tf2) is ~tfb | ~tf2
                ~(tfb | tf2) is ~tfb & ~tf2

        for tfb in [true2, false2]:
            for tf2 in [true1, false1]:
                ~(tfb & tf2) is ~tfb | ~tf2
                ~(tfb | tf2) is ~tfb & ~tf2

        for tfb in [true2, false2]:
            for tf2 in [true2, false2]:
                ~(tfb & tf2) is ~tfb | ~tf2
                ~(tfb | tf2) is ~tfb & ~tf2
