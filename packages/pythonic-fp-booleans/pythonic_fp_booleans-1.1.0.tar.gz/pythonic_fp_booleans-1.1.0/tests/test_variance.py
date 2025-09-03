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

from pythonic_fp.booleans.subtypes.truthy_falsy import TF_Bool, TF_Boolean, T_Bool, F_Bool, ALWAYS, NEVER
from pythonic_fp.booleans.subtypes.flavored import FBool, truthy, falsy
from pythonic_fp.booleans.subtypable import SBool, TRUTH, LIE

class TestBoolWithInt():
    def test_int_bitwise(self) -> None:
        assert 11 & 6 == 2
        assert 11 | 6 == 15
        assert 11 ^ 6 == 13
        assert ~3 == -4
        assert ~4 == -5
        assert ~(-5) == 4

    def test_bool_int(self) -> None:
        assert True | 2 == 3
        assert 12 & False == 0
        assert 13 & True == 1
        assert 14 & True == 0
        assert True & 13 == 1
        assert 12 | True == 13
        assert True | 12 == 13
        assert True ^ 7 == 6
        assert False ^ 7 == 7

    def test_true_false(self) -> None:
        assert True & 1 == 1
        assert True | 1 == 1
        assert True ^ 1 == 0
        assert True & 0 == 0
        assert True | 0 == 1
        assert True ^ 0 == 1
        assert False & 1 == 0
        assert False | 1 == 1
        assert False ^ 1 == 1
        assert False & 0 == 0
        assert False | 0 == 0
        assert False ^ 0 == 0

        assert (True & True) is True
        assert (False & True) is False
        assert (True & False) is False
        assert (False & False) is False
        assert (True | True) is True
        assert (False | True) is True
        assert (True | False) is True
        assert (False | False) is False
        assert (True ^ True) is False
        assert (False ^ True) is True
        assert (True ^ False) is True
        assert (False ^ False) is False

        assert True is not False
        assert False is not True


class TestSBoolWithInt():
    def test_sbool_int(self) -> None:
        assert TRUTH | 2 == 3
        assert 12 & LIE == 0
        assert 13 & TRUTH == 1
        assert 14 & TRUTH == 0
        assert TRUTH & 13 == 1
        assert 12 | TRUTH == 13
        assert TRUTH | 12 == 13
        assert TRUTH ^ 7 == 6
        assert LIE ^ 7 == 7

    def test_truth_lie(self) -> None:
        assert TRUTH & 1 == 1
        assert TRUTH | 1 == 1
        assert TRUTH ^ 1 == 0
        assert TRUTH & 0 == 0
        assert TRUTH | 0 == 1
        assert TRUTH ^ 0 == 1
        assert LIE & 1 == 0
        assert LIE | 1 == 1
        assert LIE ^ 1 == 1
        assert LIE & 0 == 0
        assert LIE | 0 == 0
        assert LIE ^ 0 == 0

        assert 1 & TRUTH == 1
        assert 1 | TRUTH == 1
        assert 1 ^ TRUTH == 0
        assert 0 & TRUTH == 0
        assert 0 | TRUTH == 1
        assert 0 ^ TRUTH == 1
        assert 1 & LIE == 0
        assert 1 | LIE == 1
        assert 1 ^ LIE == 1
        assert 0 & LIE == 0
        assert 0 | LIE == 0
        assert 0 ^ LIE == 0

        assert (TRUTH & TRUTH) is TRUTH
        assert (LIE & TRUTH) is LIE
        assert (TRUTH & LIE) is LIE
        assert (LIE & LIE) is LIE
        assert (TRUTH | TRUTH) is TRUTH
        assert (LIE | TRUTH) is TRUTH
        assert (TRUTH | LIE) is TRUTH
        assert (LIE | LIE) is LIE
        assert (TRUTH ^ TRUTH) is LIE
        assert (LIE ^ TRUTH) is TRUTH
        assert (TRUTH ^ LIE) is TRUTH
        assert (LIE ^ LIE) is LIE

        assert ~TRUTH is LIE
        assert ~LIE is TRUTH


class TestSBoolWithBool():
    def test_sbool_int(self) -> None:
        assert TRUTH & True == 1
        assert TRUTH & False == 0
        assert LIE & True == 0
        assert LIE & False == 0
        assert TRUTH | True == 1
        assert TRUTH | False == 1
        assert LIE | True == 1
        assert LIE | False == 0
        assert TRUTH ^ True == 0
        assert TRUTH ^ False == 1
        assert LIE ^ True == 1
        assert LIE ^ False == 0

        assert True & TRUTH == 1
        assert False & TRUTH == 0
        assert True & LIE == 0
        assert False & LIE == 0
        assert True | TRUTH == 1
        assert False | TRUTH == 1
        assert True | LIE == 1
        assert False | LIE == 0
        assert True ^ TRUTH == 0
        assert False ^ TRUTH == 1
        assert True ^ LIE == 1
        assert False ^ LIE == 0

class TestFBoolWithTFBool:
    fbt1 = FBool(1, 1)
    fbt2 = FBool(1, 2)
    fbf1 = FBool(0, 1)
    fbf2 = FBool(0, 2)
    t_b1 = TF_Bool(1)
    t_b2 = TF_Bool(42)
    f_b1 = TF_Bool(0)
    f_b2 = TF_Bool('')

    assert t_b1 is t_b2
    assert f_b1 is f_b2

    assert fbt1 + fbt2 + fbf1 + fbf2 + t_b1 + t_b2 + f_b1 + f_b2 == 4
    assert fbt1 | fbf1 is truthy(1)
    assert fbt2 | fbt2 is truthy(2)
    assert fbt2 | fbf1 is TRUTH
    assert t_b1 | f_b2 is ALWAYS
    assert f_b1 | f_b2 is NEVER
    assert t_b1 | fbf2 is TRUTH

    assert fbt1 & fbf1 is falsy(1)
    assert fbt2 & fbt2 is truthy(2)
    assert fbt2 & fbf1 is LIE
    assert t_b1 & f_b2 is NEVER
    assert f_b1 & f_b2 is NEVER
    assert t_b1 & fbf2 is LIE

    assert fbt1 ^ fbf1 is truthy(1)
    assert fbt2 ^ fbt2 is falsy(2)
    assert fbt2 ^ fbf1 is TRUTH
    assert t_b1 ^ f_b2 is ALWAYS
    assert f_b1 ^ f_b2 is NEVER
    assert t_b1 ^ fbf2 is TRUTH
