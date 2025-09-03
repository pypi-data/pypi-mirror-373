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
Subtypable Boolean like classes
===============================

While still compatible with Python shortcut logic, these classes can
be non-shortcut logically composed with Python's bitwise operators.
These classes are implemented with the Singleton Pattern.

Covariant class hierarchy
-------------------------

.. graphviz::

    digraph Booleans {
        bgcolor="deepskyblue";
        int -> bool;
        int -> SBool;
        SBool -> "FBool(h1)";
        SBool -> "FBool(h2)";
        SBool -> "FBool(h3)";
        SBool -> TF_Bool;
        TF_Bool -> T_Bool;
        TF_Bool -> F_Bool;
    }

Contravariant non-shortcut "bitwise" operators
----------------------------------------------

+-------------------+--------+------------+
| Boolean operation | symbol | dunder     |
+===================+========+============+
|       not         | ``~``  | __invert__ |
+-------------------+--------+------------+
|       and         | ``&``  | __and__    |
+-------------------+--------+------------+
|       or          | ``|``  | __or__     |
+-------------------+--------+------------+
|       xor         | ``^``  | __xor__    |
+-------------------+--------+------------+

These operators are contravariant, that is they will return
the instance of the latest common ancestor of their arguments.
More specifically, the instance returned will have the type
of the least upper bound in the inheritance graph of the classes
of the two arguments.

.. warning::

   These "bitwise" operators could raise ``TypeError`` exceptions
   when applied against an ``SBool`` and objects not descended
   from ``int``.

Classes
-------

Class SBool
~~~~~~~~~~~

Base of the hierarchy.

Like Python's built-in ``bool``, ``SBool`` is a subclass of ``int``,
unlike ``bool``, class ``SBool`` can be further subclassed.

Class FBool
~~~~~~~~~~~

For when you need to deal with different "flavors" of the truth.

Each "flavor" corresponds to a hashable value. Instances of ``FBool``
are invariant in their flavor. Best to think of the "flavor" as an
index.

Class TF_Bool
~~~~~~~~~~~~~

Class ``TF_Bool`` consists of just two disjoint subclasses, each one
a singleton.

- class ``T_Bool`` is the  always truthy ``TF_Bool`` subtype
- class ``F_Bool`` is the  always falsy ``TF_Bool`` subtype
"""

__author__ = 'Geoffrey R. Scheller'
__copyright__ = 'Copyright (c) 2025 Geoffrey R. Scheller'
__license__ = 'Apache License 2.0'
