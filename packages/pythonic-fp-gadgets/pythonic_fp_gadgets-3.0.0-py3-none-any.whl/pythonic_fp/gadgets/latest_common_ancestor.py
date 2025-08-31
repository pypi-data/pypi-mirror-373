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

"""Last Common Ancestor of Two Classes."""

from inspect import getmro

__all__ = ['lca']


def lca(cls1: type, cls2: type) -> type:
    """Find the least upper bound in the inheritance graph
    of two classes.

    .. warning::

       This function can fail with a TypeError. Some error messages
       seen are

         - multiple bases have instance lay-out conflict
         - type 'bool' is not an acceptable base type

       This happens frequently when the function is given
       Python builtin types.

    :param cls1: first class
    :param cls2: second class
    :returns: Least common ancestor base class of ``cls1`` and ``cls2``.
    :raises TypeError: theoretically only from ``inspect.getmto``

    """
    if issubclass(cls1, cls2):
        return cls2
    if issubclass(cls2, cls1):
        return cls1

    for common_ancestor in getmro(type('LcaDiamondClass', (cls1, cls2), {})):
        if issubclass(cls1, common_ancestor) and issubclass(cls2, common_ancestor):
            return common_ancestor
    raise TypeError("latest_common_ancestor: no common ancestor found!!!") 
