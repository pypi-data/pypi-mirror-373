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

"""Class for a stateful container that can hold at most one item."""

__all__ = ['Box']

from collections.abc import Callable, Iterator
from typing import ClassVar, cast, Final, overload
from pythonic_fp.sentinels.flavored import Sentinel


class Box[T]:
    """Container holding at most one item of a given type.

    .. note::

         - ``Box(item: T)``: contains at one item of type ``T``
         - ``Box[T]()``: creates empty container

       Where type ``T`` is some definite type, which
       could be ``None`` or even ``Never``.

    .. tip ::

       ``Box`` objects can be used in Python match statements.

    """
    __slots__ = ('_item',)
    __match_args__ = ('_item',)

    _sentinel: Final[ClassVar[Sentinel[str]]] = Sentinel('_Box')

    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, item: T) -> None: ...

    def __init__(self, item: T | Sentinel[str] = Sentinel('_Box')) -> None:
        """
        :param item: an "optional" initial contained ``item`` for the ``Box``.
        :returns: New ``Box`` instance.

        """
        self._item = item

    def __bool__(self) -> bool:
        return self._item is not Sentinel('_Box')

    def __iter__(self) -> Iterator[T]:
        if self:
            yield cast(T, self._item)

    def __repr__(self) -> str:
        if self:
            return 'Box(' + repr(self._item) + ')'
        return 'Box()'

    def __len__(self) -> int:
        return 1 if self else 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        if self._item is other._item:
            return True
        if self._item == other._item:
            return True
        return False

    @overload
    def get(self) -> T: ...
    @overload
    def get(self, alt: T) -> T: ...

    def get(self, alt: T | Sentinel[str] = Sentinel('_Box')) -> T:
        """Return the contained item if it exists, otherwise an alternate item.

        :param alt: an "optional" item of type ``T`` to return if ``Box`` is empty
        :returns: contents of ``Box``, or an alternate item if given and ``Box`` empty
        :raises ValueError: when an ``alt`` item is not provided but needed

        """
        if self._item is not self._sentinel:
            return cast(T, self._item)
        if alt is self._sentinel:
            msg = 'Box: get from empty Box with no alternate return item provided'
            raise ValueError(msg)
        return cast(T, alt)

    def pop(self) -> T:
        """Pop the contained item if ``Box`` is not empty.

        :returns: item contained in the ``Box``
        :raises: ``ValueError`` if Box is empty

        """
        if self._item is self._sentinel:
            msg = 'Box: Trying to pop an item from an empty Box'
            raise ValueError(msg)
        popped = cast(T, self._item)
        self._item = self._sentinel
        return popped

    def push(self, item: T) -> None:
        """Push an item into an empty ``Box``.

        :param item: Item to push into the empty ``Box``.
        :raises ValueError: If ``Box`` is not empty.

        """
        if self._item is Sentinel('_Box'):
            self._item = item
        else:
            msg = 'Box: Trying to push an item in a non-empty Box'
            raise ValueError(msg)
        return None

    def put(self, item: T) -> None:
        """Put an item in the Box. Discard any previous contents."""
        self._item = item

    def exchange(self, new_item: T) -> T:
        """Exchange an item with what is in the Box.

        :param ``new_item``: New item to exchange for current item.
        :returns: Original contents of the ``Box``.
        :raises ValueError: If Box is empty.
        """
        if self._item is self._sentinel:
            msg = 'Box: Trying to exchange items from an empty Box'
            raise ValueError(msg)
        popped = cast(T, self._item)
        self._item = new_item
        return popped

    def map[U](self, f: Callable[[T], U]) -> 'Box[U]':
        """Map function ``f`` over contents. We need to return a new
        instance since the type of Box can change.

        :param f: mapping function
        :returns: a new instance

        """
        if self._item is Sentinel('_Box'):
            return Box()
        return Box(f(cast(T, self._item)))

    def bind[U](self, f: Callable[[T], 'Box[U]']) -> 'Box[U]':
        """Flatmap ``Box`` with function ``f``.

        :param f: binding function
        :returns: a new instance

        """
        if self._item is self._sentinel:
            return Box()
        return f(cast(T, self._item))
