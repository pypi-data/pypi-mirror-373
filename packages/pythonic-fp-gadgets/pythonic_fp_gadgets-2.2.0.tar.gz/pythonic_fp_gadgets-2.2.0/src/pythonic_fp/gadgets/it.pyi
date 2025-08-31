from collections.abc import Iterator

__all__ = ['it']

def it[A](*args: A) -> Iterator[A]: ...
