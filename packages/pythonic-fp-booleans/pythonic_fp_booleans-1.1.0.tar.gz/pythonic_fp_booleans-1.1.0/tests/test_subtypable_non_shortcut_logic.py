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

from pythonic_fp.booleans.subtypable import SBool, TRUTH, LIE

truth1 = SBool(1 == 1)
truth2 = SBool(42 == 42)
truth3 = SBool(42)

lie1 = SBool(1 == 1+1)
lie2 = SBool(42 != 42)
lie3 = SBool(0)

class TestBitwiseOperations():
    def test_or_not(self) -> None:
        assert TRUTH == truth1 | truth2
        assert TRUTH is truth2 | truth3
        assert TRUTH is truth2 | ~ truth3
        assert TRUTH is ~truth1 | truth3
        assert LIE is ~ truth1 | ~truth3
        assert LIE is ~truth1 | lie2
        assert TRUTH is lie2 | ~lie3
        assert LIE is ~truth2 | lie1
        assert LIE is lie2 | lie1

        assert TRUTH is lie1 | lie2 | truth3 | lie1 | lie3
        assert TRUTH == lie1 | lie2 | truth3 | lie1 | lie3
        assert LIE is lie1|lie2|~truth1|lie1|~truth3
        assert LIE == lie1|lie2|~truth1|lie1|~truth3

    def test_xor_not(self) -> None:
        assert LIE == truth1 ^ truth2
        assert LIE is truth2^truth3
        assert TRUTH is truth2 ^ ~ truth3
        assert TRUTH is ~truth1 ^ truth3
        assert LIE is ~ truth1 ^ ~truth3
        assert LIE is ~truth1 ^ lie2
        assert TRUTH is lie2 ^~lie3
        assert LIE is ~truth2 ^ lie1
        assert LIE == ~truth2 ^ lie1
        assert LIE is lie2 ^ lie1
        assert LIE == lie2 ^ lie1

        assert TRUTH is lie1 ^ lie2 ^ truth3 ^ lie1 ^ lie3
        assert LIE is lie1^lie2^~truth1^lie1^~truth3
        assert TRUTH is lie1^lie2^~truth1^lie1^truth3^lie3
        assert LIE is lie1^lie2^~truth1^lie1^truth3^truth2

    def test_and_not(self) -> None:
        assert TRUTH is truth1 & truth2
        assert TRUTH is truth2&truth3
        assert LIE is truth2 & ~truth3
        assert LIE is ~truth1 & truth3
        assert LIE is ~truth1&~truth3
        assert TRUTH is truth1 &~lie2
        assert LIE is lie2&~lie3
        assert LIE is ~truth2 & lie1
        assert LIE is lie2 & lie1

        assert LIE == lie1 & lie2 & truth3 & lie1 & lie3
        assert LIE is lie1 & lie2 & truth3 & lie1 & lie3
        assert TRUTH == ~lie1 & ~lie2 & truth3 & ~lie1 & ~lie3
        assert TRUTH is ~lie1 & ~lie2 & truth3 & ~lie1 & ~lie3

    def test_de_morgan(self) -> None:
        for sb1 in [truth1, lie1]:
            for sb2 in [truth2, lie2]:
                ~(sb1 & sb2) is ~sb1 | ~sb2
                ~(sb1 | sb2) is ~sb1 & ~sb2

    def test_arbitrary_combo(self) -> None:
        assert TRUTH is lie1 & (lie2 | truth3) | ~lie3 & truth2 | lie2 & ~truth1
