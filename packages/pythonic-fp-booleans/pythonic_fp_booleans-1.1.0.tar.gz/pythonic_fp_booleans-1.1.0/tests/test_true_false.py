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
# See the License for the specific language governing permissions anddd
# limitations under the License.

from pythonic_fp.booleans.subtypable import SBool, TRUTH, LIE
from pythonic_fp.booleans.subtypes.truthy_falsy import (
    TF_Boolean,
    T_Bool,
    F_Bool,
    ALWAYS,
    NEVER,
)


class TestSBool:
    def test_equality(self) -> None:
        assert TRUTH == TRUTH
        assert LIE == LIE
        assert TRUTH != LIE
        assert TRUTH is TRUTH
        assert LIE is LIE
        assert TRUTH is not LIE

        sky_is_blue: SBool = TRUTH
        koalas_eat_meat: SBool = LIE
        water_is_wet: SBool = SBool(True)
        ice_is_hot: SBool = SBool(False)

        assert sky_is_blue == water_is_wet
        assert koalas_eat_meat == ice_is_hot
        assert sky_is_blue != koalas_eat_meat
        assert water_is_wet != ice_is_hot

        assert sky_is_blue is water_is_wet
        assert koalas_eat_meat is ice_is_hot

        if sky_is_blue:
            assert True
        else:
            assert False

        if koalas_eat_meat:
            assert False
        else:
            assert True

        assert sky_is_blue == 1
        assert sky_is_blue != 0
        assert sky_is_blue != 5
        assert koalas_eat_meat == 0
        assert koalas_eat_meat != 1
        assert koalas_eat_meat != 5

        foo: SBool = TRUTH
        assert foo == TRUTH
        foo = LIE
        assert foo == LIE


class TestSBoolSubclass:
    def test_subclass_hierarchy(self) -> None:
        assert issubclass(T_Bool, SBool)
        assert issubclass(F_Bool, SBool)
        assert issubclass(T_Bool, int)
        assert issubclass(F_Bool, int)
        assert issubclass(SBool, int)
        assert issubclass(bool, int)
        assert not issubclass(bool, SBool)
        assert not issubclass(SBool, bool)

    def test_isinstance(self) -> None:
        a_bool = False
        my_int = 0
        myTruth: TF_Boolean = T_Bool(True)
        myLie: TF_Boolean = F_Bool(False)

        assert isinstance(a_bool, int)
        assert isinstance(a_bool, bool)
        assert isinstance(my_int, int)
        assert isinstance(myLie, int)
        assert isinstance(myLie, SBool)
        assert isinstance(myLie, F_Bool)
        assert not isinstance(myLie, T_Bool)
        assert not isinstance(myLie, bool)
        assert isinstance(not myLie, bool)
        assert not isinstance(~myLie, bool)

        a_bool = True
        my_int = 1

        assert isinstance(a_bool, int)
        assert isinstance(a_bool, bool)
        assert isinstance(my_int, int)
        assert isinstance(myTruth, int)
        assert isinstance(myTruth, SBool)
        assert isinstance(myTruth, T_Bool)
        assert not isinstance(myTruth, F_Bool)
        assert not isinstance(myTruth, bool)
        assert isinstance(not myTruth, bool)
        assert not isinstance(~myTruth, bool)


class Test_not:
    def test_not(self) -> None:
        foo: int = 42
        assert isinstance(foo, int)
        assert not isinstance(foo, bool)
        assert isinstance(not foo, int)
        assert isinstance(not foo, bool)
        assert not isinstance(not foo, SBool)

        bar: bool = True
        assert isinstance(bar, int)
        assert isinstance(bar, bool)
        assert isinstance(not bar, int)
        assert isinstance(not bar, bool)
        assert not isinstance(not bar, SBool)

        baz: SBool = TRUTH
        assert isinstance(baz, int)
        assert not isinstance(baz, bool)
        assert isinstance(not baz, int)
        assert isinstance(not baz, bool)
        assert not isinstance(not baz, SBool)

        quuz: SBool = LIE
        assert isinstance(quuz, int)
        assert not isinstance(quuz, bool)
        assert isinstance(not quuz, int)
        assert isinstance(not quuz, bool)
        assert not isinstance(not quuz, SBool)

        putz: SBool = SBool(42)
        assert isinstance(putz, int)
        assert not isinstance(putz, bool)
        assert isinstance(not putz, int)
        assert isinstance(not putz, bool)
        assert not isinstance(not putz, SBool)

        futz: SBool = F_Bool()
        assert isinstance(futz, int)
        assert not isinstance(futz, bool)
        assert isinstance(not futz, int)
        assert isinstance(not futz, bool)
        assert not isinstance(not futz, SBool)

        tutz: SBool = T_Bool()
        assert isinstance(tutz, int)
        assert not isinstance(tutz, bool)
        assert isinstance(not tutz, int)
        assert isinstance(not tutz, bool)
        assert not isinstance(not tutz, SBool)


class TestTruthsAndLies:
    def test_truths_and_lies(self) -> None:
        baseT: SBool = SBool('foofoo')
        baseF: SBool = SBool('')
        derivedT1: TF_Boolean = T_Bool()
        derivedF1: TF_Boolean = F_Bool()
        derivedT2: SBool = T_Bool()
        derivedF2: SBool = F_Bool()

        assert baseT == derivedT1 == derivedT2 == TRUTH == ALWAYS
        assert baseF == derivedF1 == derivedF2 == LIE == NEVER

    def test_identities(self) -> None:
        yooT: SBool = ALWAYS
        mooT: SBool = F_Bool()
        mooF: SBool = T_Bool()
        yooF: SBool = NEVER

        mooT == yooT
        mooF == yooF
        mooT != yooF

        mooT is not yooT
        mooF is not yooF
        mooT is not yooF
