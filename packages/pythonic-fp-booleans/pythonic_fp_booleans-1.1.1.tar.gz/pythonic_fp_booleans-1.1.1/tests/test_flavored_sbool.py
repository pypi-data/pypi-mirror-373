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

from pythonic_fp.booleans.subtypes.flavored import FBool, truthy, falsy
from pythonic_fp.booleans.subtypable import SBool, TRUTH, LIE

fbt0_1 = FBool(1 == 1, 0)
sbt_1 = SBool(42 == 42)
fbt1_1 = FBool(42, 1)
sbt_2 = SBool(42)

fbf0_1 = FBool(1 < 0, 0)
sbf_1 = SBool(42 != 42)
fbf1_1 = FBool(0, 1)
sbf_2 = SBool('')

class TestIdentiyFBoolEquality():
    def test_identity_fbool(self) -> None:
        # based on identity

        fbt0_1 is fbt0_1
        fbt0_1 is not sbt_1
        sbt_2 is sbt_2
        fbt1_1 is not sbt_2
        fbf0_1 is fbf0_1
        fbf0_1 is not sbf_1
        sbf_2 is sbf_2
        fbf1_1 is not sbf_2

        fbt0_1 is not fbt1_1
        fbt0_1 is not sbt_2
        sbt_2 is sbt_1
        fbt1_1 is not sbt_1
        fbf0_1 is not fbf1_1
        fbf0_1 is not sbf_2
        sbf_2 is  sbf_1
        fbf1_1 is not sbf_1

        fbt0_1 is truthy(0)
        fbt1_1 is truthy(1)
        fbt0_1 is not truthy(1)
        fbt0_1 is not truthy('foobar')
        sbt_1 is TRUTH
        sbt_2 is TRUTH
        sbt_1 is not LIE
        sbt_2 is not LIE
        sbf_1 is LIE
        sbf_2 is LIE
        sbf_1 is not TRUTH
        sbf_2 is not TRUTH

    def test_equality_fbool(self) -> None:
        # based on truthiness

        fbt0_1 == fbt0_1
        fbt0_1 == sbt_1
        sbt_2 == sbt_2
        fbt1_1 == sbt_2
        fbf0_1 == fbf0_1
        fbf0_1 == sbf_1
        sbf_2 == sbf_2
        fbf1_1 == sbf_2

        fbt0_1 == fbt1_1
        fbt0_1 == sbt_2
        sbt_2 == sbt_1
        fbt1_1 == sbt_1
        fbf0_1 == fbf1_1
        fbf0_1 == sbf_2
        sbf_2 == sbf_1
        fbf1_1 == sbf_1

        fbt0_1 != fbf1_1
        fbt0_1 != sbf_2
        sbt_2 != sbf_1
        fbt1_1 != sbf_1
        fbf0_1 != fbt1_1
        fbf0_1 != sbt_2
        sbf_2 != sbt_1
        fbf1_1 != sbt_1

class TestBitwiseOperations():
    def test_or_not(self) -> None:
        assert truthy(0) is (fbt0_1 | fbt0_1)
        assert TRUTH is (sbt_1 | fbt0_1)
        assert TRUTH is (fbt0_1 | fbt1_1)

    def test_xor_not(self) -> None:
        assert LIE is (fbt0_1 ^ sbt_1)
        assert TRUTH is (fbt0_1 ^ sbf_1)
        assert TRUTH is (sbf_1 ^ fbt0_1)
        assert TRUTH is (fbf0_1 ^ ~sbf_1)

        assert LIE is (fbt0_1 ^ sbt_2)
        assert TRUTH is (fbt0_1 ^ sbf_1)
        assert LIE is (fbf0_1 ^ sbf_1)
        assert TRUTH == (~fbf0_1 ^ sbf_1)
        assert TRUTH == (sbf_1 ^ ~fbf0_1)
        assert TRUTH == (~fbf0_1 ^ sbf_2)
        assert LIE == (fbf1_1 ^ sbf_1)
        assert TRUTH == ~(fbf1_1 ^ sbf_1)

    def test_not(self) -> None:
        assert TRUTH is (fbt0_1 & sbt_1)
        assert LIE is (fbt0_1 & ~sbt_1)
        assert LIE is (~fbt0_1 & sbt_1)
        assert LIE is (~fbt0_1 & ~sbt_1)
        assert TRUTH is ~(~fbt0_1 & ~sbt_1)
        assert TRUTH is ~(~fbt0_1 & sbf_1)
        assert LIE is (fbf0_1 & sbf_1)

        assert TRUTH is (fbt0_1 | sbt_1)
        assert TRUTH is (fbt0_1 | ~sbt_1)
        assert TRUTH is (~fbt0_1 | sbt_1)
        assert LIE is (~fbt0_1 | ~sbt_1)
        assert TRUTH is ~(~fbt0_1 | ~sbt_1)
        assert TRUTH is ~(~fbt1_1 | sbf_2)
        assert LIE is (fbf1_1 | sbf_2)

        assert LIE is (fbt0_1 ^ sbt_1)
        assert TRUTH is (fbt0_1 ^ ~sbt_1)
        assert TRUTH is (~fbt0_1 ^ sbt_1)
        assert LIE is (~fbt0_1 ^ ~sbt_1)
        assert TRUTH is ~(~fbt0_1 ^ ~sbt_1)
        assert TRUTH is ~(~fbt1_1 ^ sbf_2)
        assert LIE is ~(fbt1_1 ^ sbf_2)
        assert LIE is (fbf1_1 ^ sbf_2)

        assert TRUTH is (fbt0_1 & sbt_2)
        assert LIE is (fbt0_1 & ~sbt_2)
        assert LIE is (~fbt0_1 & sbt_2)
        assert LIE is (~fbt0_1 & ~sbt_2)
        assert TRUTH is ~(~fbt0_1 & ~sbt_2)
        assert TRUTH is ~(~fbt1_1 & sbf_1)
        assert LIE is (fbf1_1 & sbf_1)

    def test_de_morgan(self) -> None:
        for fb1 in [truthy(0), falsy(0)]:
            for fb2 in [truthy(0), falsy(0)]:
                ~(fb1 & fb2) is (~fb1 | ~fb2)
                ~(fb1 | fb2) is (~fb1 & ~fb2)

        for sb1 in [TRUTH, LIE]:
            for fb2 in [truthy(0), falsy(0)]:
                ~(sb1 & fb2) is (~sb1 | ~fb2)
                ~(sb1 | fb2) is (~sb1 & ~fb2)

        for fb1 in [truthy(0), falsy(0)]:
            for sb2 in [TRUTH, LIE]:
                ~(fb1 & sb2) is (~fb1 | ~sb2)
                ~(fb1 | sb2) is (~fb1 & ~sb2)
