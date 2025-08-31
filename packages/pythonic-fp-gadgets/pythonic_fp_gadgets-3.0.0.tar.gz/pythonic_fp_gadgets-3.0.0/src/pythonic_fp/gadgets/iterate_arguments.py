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

"""Function which returns an iterator of its arguments."""

from collections.abc import Iterator

__all__ = ['ita']


def ita[A](*args: A) -> Iterator[A]:
    """Function returning an iterator of its arguments.

    .. note::

       Does not create an object to iterate over.

         - well, not in the Python world
         - maybe in the C world

    :param args: Objects to iterate over.
    :returns: An iterator of the arguments.

    """
    yield from args
