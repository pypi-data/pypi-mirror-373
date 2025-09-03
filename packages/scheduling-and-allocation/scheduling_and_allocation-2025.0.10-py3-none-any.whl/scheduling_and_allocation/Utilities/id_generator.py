"""
DESCRIPTION
Creates and keep tracks of IDs for collections of things

SYNOPSIS

class Foo
    ids = id_gen.IdGenerator()

    def __init__(self, id: Optional[int])
        self.id = Foo.ids.get_new_id(block_id)
"""

from typing import Optional


class IdGenerator:
    """
    A generic class to create and keep track of id numbers for collections of objects
    """

    def __init__(self, the_id: int = -1):
        self._current_id = the_id
        self._iter = self.__iter__()

    def __iter__(self):
        while True:
            self._current_id += 1
            yield self._current_id

    # def _next_id(self, this_id: Optional[int] = None) -> int:
    #     if this_id is not None and this_id > self._current_id:
    #         self._current_id = this_id - 1
    #     return next(self._iter)

    @property
    def current_id(self) -> int:
        """Value of the largest id that was created"""
        return self._current_id

    def get_new_id(self, value: Optional[int|str] = None) -> int:
        """Change the current id, else get the next value"""

        if value is None:
            value = next(self._iter)
        else:
            try:
                value = int(value)
            except TypeError:
                value = next(self._iter)

        self._current_id = max(self._current_id, value)
        return value
