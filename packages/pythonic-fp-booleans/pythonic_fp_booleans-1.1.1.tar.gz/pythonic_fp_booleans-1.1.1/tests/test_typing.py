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

from pythonic_fp.booleans.subtypable import SBool
from pythonic_fp.booleans.subtypes.flavored import FBool, truthy, falsy
from pythonic_fp.booleans.subtypes.truthy_falsy import TF_Bool, T_Bool, F_Bool


class TestInvert:
    def test_sbool(self) -> None:
        assert ~SBool(True) is SBool(False)
        assert ~SBool(False) is SBool(True)

    def test_fbool(self) -> None:
        assert ~FBool(True, 0) is FBool(False, 0)
        assert ~FBool(True, 0) is not FBool(False, 1)
        assert ~FBool(False, 0) is FBool(True, 0)
        assert ~FBool(False, 0) is not FBool(True, 1)

        assert ~(FBool(False, 'foo') & FBool(False, 'foo')) is FBool(True, 'foo')
        assert ~(FBool(True, 'foo') & FBool(False, 'foo')) is FBool(True, 'foo')
        assert ~(FBool(False, 'foo') & FBool(True, 'foo')) is FBool(True, 'foo')
        assert ~(FBool(True, 'foo') & FBool(True, 'foo')) is FBool(False, 'foo')
        assert ~(FBool(False, 'foo') | FBool(False, 'foo')) is FBool(True, 'foo')
        assert ~(FBool(True, 'foo') | FBool(False, 'foo')) is FBool(False, 'foo')
        assert ~(FBool(False, 'foo') | FBool(True, 'foo')) is FBool(False, 'foo')
        assert ~(FBool(True, 'foo') | FBool(True, 'foo')) is FBool(False, 'foo')
        assert ~(FBool(False, 'foo') ^ FBool(False, 'foo')) is FBool(True, 'foo')
        assert ~(FBool(True, 'foo') ^ FBool(False, 'foo')) is FBool(False, 'foo')
        assert ~(FBool(False, 'foo') ^ FBool(True, 'foo')) is FBool(False, 'foo')
        assert ~(FBool(True, 'foo') ^ FBool(True, 'foo')) is FBool(True, 'foo')

        assert ~(FBool(False, 'foo') & FBool(False, 'bar')) is SBool(True)
        assert ~(FBool(True, 'foo') & FBool(False, 'bar')) is SBool(True)
        assert ~(FBool(False, 'foo') & FBool(True, 'bar')) is SBool(True)
        assert ~(FBool(True, 'foo') & FBool(True, 'bar')) is SBool(False)
        assert ~(FBool(False, 'foo') | FBool(False, 'bar')) is SBool(True)
        assert ~(FBool(True, 'foo') | FBool(False, 'bar')) is SBool(False)
        assert ~(FBool(False, 'foo') | FBool(True, 'bar')) is SBool(False)
        assert ~(FBool(True, 'foo') | FBool(True, 'bar')) is SBool(False)
        assert ~(FBool(False, 'foo') ^ FBool(False, 'bar')) is SBool(True)
        assert ~(FBool(True, 'foo') ^ FBool(False, 'bar')) is SBool(False)
        assert ~(FBool(False, 'foo') ^ FBool(True, 'bar')) is SBool(False)
        assert ~(FBool(True, 'foo') ^ FBool(True, 'bar')) is SBool(True)

        assert ~(truthy(42)) is falsy(42)
        assert ~(falsy(42)) is truthy(42)
        assert ~(truthy(42)) is not falsy(1)
        assert ~(falsy(42)) is not truthy(1)

    def test_truthy_falsy(self) -> None:
        assert ~(T_Bool()) is F_Bool()
        assert ~(F_Bool()) is T_Bool()
        assert ~(TF_Bool(True)) is TF_Bool(False)
        assert ~(TF_Bool(False)) is TF_Bool(True)

    def test_sbool_fbool(self) -> None:
        assert ~(SBool(False) & FBool(False, 'bar')) is SBool(True)
        assert ~(FBool(True, 'foo') & SBool(False)) is SBool(True)
        assert ~(SBool(False) & FBool(True, 'bar')) is SBool(True)
        assert ~(FBool(True, 'foo') & SBool(True)) is SBool(False)
        assert ~(SBool(False) | FBool(False, 'bar')) is SBool(True)
        assert ~(FBool(True, 'foo') | SBool(False)) is SBool(False)
        assert ~(SBool(False) | FBool(True, 'bar')) is SBool(False)
        assert ~(FBool(True, 'foo') | SBool(True)) is SBool(False)
        assert ~(SBool(False) ^ FBool(False, 'bar')) is SBool(True)
        assert ~(FBool(True, 'foo') ^ SBool(False)) is SBool(False)
        assert ~(SBool(False) ^ FBool(True, 'bar')) is SBool(False)
        assert ~(FBool(True, 'foo') ^ SBool(True)) is SBool(True)


class TestArithmetic:
    def test_arithmetic(self) -> None:
        sbt = SBool(1)
        sbf = SBool(0)
        fbt1 = FBool(1, 1)
        fbf1 = FBool(0, 1)
        fbt2 = FBool(1, 2)
        fbf2 = FBool(0, 2)
        tb1 = TF_Bool(1)
        tb2 = TF_Bool(1)
        fb1 = TF_Bool(0)
        fb2 = TF_Bool(0)

        sbt + (fbt1 + tb1) + tb2 == 4
        sbt + (fbt1 - tb1) + fb2 == 1
        (sbt + sbf) * (fbt1 + fbf1 + fbt2 + fbf2) * (tb1 + tb2 + fb1 + fb2) == 4
