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
from pythonic_fp.booleans.subtypes.flavored import FBool, truthy, falsy

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

    def test_fbool(self) -> None:
        # Next make sure that FBool does the same as bool
        fbool_t1 = FBool(1, 'foo')
        fbool_t2 = FBool(True, 'bar')

        fbool_f1 = FBool(False, 'foo')
        fbool_f2 = FBool('', 'bar')

        assert fbool_t1 == fbool_t2
        assert fbool_t1 is not fbool_t2

        assert fbool_f1 == fbool_f2
        assert fbool_f1 is not fbool_f2

        foo = 42
        fbool1 = FBool(foo == 1, 'foo')
        fbool2 = FBool(foo != 42, 'foo')
        tup: tuple[int, ...] = (fbool1 and (foo, 42) or fbool2 and (foo, foo, 42)) or ()
        assert tup == ()

        foo = 0
        fbool1 = FBool(foo == 1, 'bar')
        fbool2 = FBool(foo != 42, 'bar')
        tup = (fbool1 and (foo, 42) or fbool2 and (foo, foo, 42)) or ()
        assert tup == (0, 0, 42)

        foo = 0
        fbool1 = FBool(foo == 1, 'foo')
        fbool2 = FBool(foo != 42, 'bar')
        tup = (fbool1 and (foo, 42) or fbool2 and (foo, foo, 42)) or ()
        assert tup == (0, 0, 42)

        foo = 1
        fbool1 = FBool(foo == 1, 'foo')
        fbool2 = FBool(foo != 42, 'foo')
        tup = (fbool1 and (foo, 42) or fbool2 and (foo, foo, 42)) or ()
        assert tup == (1, 42)

        fbool_foo_t = truthy('foo')
        fbool_bar_t = truthy('bar')
        fbool_foo_f = falsy('foo')
        fbool_bar_f = falsy('bar')
        fbool_foo_t is truthy('foo')
        fbool_foo_t is not truthy('foobar')
        fbool_foo_f is falsy('foo')
        fbool_foo_f is not falsy('foobar')
        fbool_foo_f is not fbool_bar_f
        fbool_foo_f == fbool_bar_f
        fbool_foo_t is not fbool_bar_t
        fbool_foo_t == fbool_bar_t
        fbool_foo_t != fbool_bar_f
        fbool_foo_t is ~ fbool_foo_f
        fbool_bar_t is ~ fbool_bar_f
        fbool_foo_t is not ~fbool_bar_f
        fbool_bar_t is not ~fbool_foo_f
        fbool_foo_t == ~fbool_bar_f
        fbool_bar_t == ~fbool_foo_f

    def test_arithmetic(self) -> None:
        bt1 = True
        bt2 = True
        bf1 = False
        bf2 = False

        ft0 = truthy(0)
        ft1 = truthy(1)
        ff0 = falsy(0)
        ff1 = falsy(1)

        assert isinstance(bt1, int)
        assert isinstance(bt1, bool)
        assert not isinstance(bt1, FBool)

        assert isinstance(ft0, int)
        assert isinstance(ft1, int)
        assert isinstance(ff0, int)
        assert isinstance(ff1, int)
        assert not isinstance(ft0, bool)
        assert not isinstance(ft1, bool)
        assert not isinstance(ff0, bool)
        assert not isinstance(ff1, bool)
        assert isinstance(ft0, FBool)
        assert isinstance(ft1, FBool)
        assert isinstance(ff0, FBool)
        assert isinstance(ff1, FBool)

        assert bt1 + bt2 + bf1 + bf2 == 2
        assert bf1 * bf2 == 0
        assert bt1 * bf2 == 0
        assert bt2 * bf1 == 0
        assert bt1 * bt2 == 1

        assert ft0 + ft1 + ff0 + ff1 == 2
        assert ff0 * ff1 == 0
        assert ft0 * ff1 == 0
        assert ft1 * ff0 == 0
        assert ft0 * ft1 == 1

        assert 5 + bf1 == 5
        assert 5 + bt2 == 6
        assert bf1 + 5 == 5
        assert bt2 + 5 == 6

        assert 5 + ff0 == 5
        assert 5 + ft1 == 6
        assert ff0 + 5 == 5
        assert ft1 + 5 == 6

        assert 5 * bf1 == 0
        assert 5 * bt2 == 5
        assert bf1 * 5 == 0
        assert bt2 * 5 == 5

        assert 5 * ff0 == 0
        assert 5 * ft1 == 5
        assert ff0 * 5 == 0
        assert ft1 * 5 == 5

        assert bf1 * ff0 == 0
        assert ff0 * bf1 == 0
        assert bt1 * ff0 == 0
        assert ff0 * bt2 == 0
        assert ft0 * bt1 == 1
        assert bt1 * ft0 == 1
        assert bf1 + ff0 == 0
        assert ff0 + bf1 == 0
        assert bt1 + ff0 == 1
        assert ff0 + bt2 == 1
        assert ft0 + bt1 == 2
        assert bt1 + ft0 == 2

        assert LIE + ft1 == 1
        assert TRUTH + ft1 == 2
        assert ft0 + TRUTH + ft1 == 3
        assert ft0 + SBool(1==1) + 3 == 5
        assert SBool('') + ff0 + ff0 == 0
        assert SBool('foo') + ft1 == 2
