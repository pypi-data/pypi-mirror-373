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

class TestBooleanBehaviors():
    def test_bool(self) -> None:
        # First make sure we understand what bool does
        bool_t1 = True
        bool_t2 = bool(42)

        bool_f1 = False
        bool_f2 = bool(0)

        assert bool_t1 == bool_t2
        assert bool_t1 is bool_t2

        assert bool_f1 == bool_f2
        assert bool_f1 is bool_f2

        foo = 42
        bool1 = bool(foo == 1)
        bool2 = bool(foo != 42)
        tup: tuple[int, ...] = (bool1 and (foo, 42) or bool2 and (foo, foo, 42)) or ()
        assert tup == ()

        foo = 0
        bool1 = bool(foo == 1)
        bool2 = bool(foo != 42)
        tup = (bool1 and (foo, 42) or bool2 and (foo, foo, 42)) or ()
        assert tup == (0, 0, 42)

        foo = 1
        bool1 = bool(foo == 1)
        bool2 = bool(foo != 42)
        tup = (bool1 and (foo, 42) or bool2 and (foo, foo, 42)) or ()
        assert tup == (1, 42)

        bool1 = True
        bool2 = False
        bool1 is bool1
        bool2 is bool2
        bool1 is not bool2
        bool1 == (not bool2)
        bool2 == (not bool1)

    def test_sbool(self) -> None:
        # Next make sure that SBool does the same
        sbool_t1 = TRUTH
        sbool_t2 = SBool(1)

        sbool_f1 = LIE
        sbool_f2 = SBool(0)

        assert sbool_t1 == sbool_t2
        assert sbool_t1 is sbool_t2

        assert sbool_f1 == sbool_f2
        assert sbool_f1 is sbool_f2

        foo = 42
        sbool1 = SBool(foo == 1)
        sbool2 = SBool(foo != 42)
        tup: tuple[int, ...] = (sbool1 and (foo, 42) or sbool2 and (foo, foo, 42)) or ()
        assert tup == ()

        foo = 0
        sbool1 = SBool(foo == 1)
        sbool2 = SBool(foo != 42)
        tup = (sbool1 and (foo, 42) or sbool2 and (foo, foo, 42)) or ()
        assert tup == (0, 0, 42)

        foo = 1
        sbool1 = SBool(foo == 1)
        sbool2 = SBool(foo != 42)
        tup = (sbool1 and (foo, 42) or sbool2 and (foo, foo, 42)) or ()
        assert tup == (1, 42)

        sbool1 = TRUTH
        sbool2 = LIE
        sbool1 is sbool1
        sbool2 is sbool2
        sbool1 is not sbool2
        sbool1 == ~sbool2
        sbool2 == ~sbool1

    def test_arithmetic(self) -> None:
        bt1 = True
        bt2 = True
        bf1 = False
        bf2 = False

        st1 = TRUTH
        st2 = TRUTH
        sf1 = LIE
        sf2 = LIE

        assert isinstance(bt1, int)
        assert isinstance(bt1, bool)
        assert not isinstance(bt1, SBool)

        assert isinstance(st1, int)
        assert not isinstance(st1, bool)
        assert isinstance(st1, SBool)

        assert bt1 + bt2 + bf1 + bf2 == 2
        assert bf1 * bf2 == 0
        assert bt1 * bf2 == 0
        assert bt2 * bf1 == 0
        assert bt1 * bt2 == 1

        assert st1 + st2 + sf1 + sf2 == 2
        assert sf1 * sf2 == 0
        assert st1 * sf2 == 0
        assert st2 * sf1 == 0
        assert st1 * st2 == 1

        assert 5 + bf1 == 5
        assert 5 + bt2 == 6
        assert bf1 + 5 == 5
        assert bt2 + 5 == 6

        assert 5 + sf1 == 5
        assert 5 + st2 == 6
        assert sf1 + 5 == 5
        assert st2 + 5 == 6

        assert 5 * bf1 == 0
        assert 5 * bt2 == 5
        assert bf1 * 5 == 0
        assert bt2 * 5 == 5

        assert 5 * sf1 == 0
        assert 5 * st2 == 5
        assert sf1 * 5 == 0
        assert st2 * 5 == 5

        assert bf1 * sf1 == 0
        assert sf1 * bf1 == 0
        assert bt1 * sf1 == 0
        assert sf1 * bt2 == 0
        assert st1 * bt1 == 1
        assert bt1 * st1 == 1
        assert bf1 + sf1 == 0
        assert sf1 + bf1 == 0
        assert bt1 + sf1 == 1
        assert sf1 + bt2 == 1
        assert st1 + bt1 == 2
        assert bt1 + st1 == 2
