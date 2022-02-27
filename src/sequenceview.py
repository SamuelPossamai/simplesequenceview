
from collections.abc import Sequence, MutableSequence, Iterator
from copy import copy

class RangeIterator(Iterator):

    def __init__(self, container, start, end, step=1):
        self.__container = container
        self.__range = iter(range(start, end, step))

    def __iter__(self):
        return self

    def __next__(self):
        return self.__container[next(self.__range)]

class SequenceView(Sequence):

    @staticmethod
    def __decorateGetItem(container, index):
        if not isinstance(index, slice):
            return super().__getitem__(index)

        return SequenceView(container, index.start, index.stop, index.step)

    @staticmethod
    def decorate(seq_cls):

        new_class = type(seq_cls.__name__, (seq_cls,), {})

        new_class.__getitem__ = SequenceView.__decorateGetItem

        return new_class

    def __init__(self, container, start=0, end=-1, step=1):

        if start is None:
            start = 0

        if end is None:
            end = len(container)
        elif end < 0:
            end += len(container)

        if step is None:
            step = 1

        self._container = container
        self._start = start
        self._end = end
        self._step = step
        self._qtd = 1 + end - start

    def __iter__(self):
        return RangeIterator(self._container, self._start,
                             self._end, self._step)

    def __reversed__(self):
        return RangeIterator(self._container, self._end - 1,
                             self._start - 1, -self._step)

    def __getitem__(self, index):

        if isinstance(index, slice):
            new_view = copy(self)

            if index.stop is not None:
                if index.stop < 0:
                    new_view._end += index.stop
                else:
                    new_view._end += new_view._start + index.stop

            if index.start is not None:
                new_view._start += index.start

            if index.step is not None:
                new_view._step *= index.step

            return new_view

        return self._container[self.mapIndexToContainer(index)]

    def mapIndexToContainer(self, index, raise_error=False):
        if index < 0:
            index += self._qtd

        if index >= self._qtd:
            if raise_error:
                raise IndexError('sequence view index out of range')
            return None
        return self._start + index

    def mapIndexFromContainer(self, index, raise_error=False):
        if index < 0:
            index += len(self._container)

        if self._start <= index < self._end:
            return index - self._start

        if raise_error:
            raise IndexError('sequence index out of range')
        return None

    def __len__(self):
        return self._qtd

class MutableSequenceView(SequenceView, MutableSequence):

    def __setitem__(self, index, value):

        if isinstance(index, slice):

            if index.start is None:
                start = self._start
            else:
                start = self.mapIndexToContainer(index.start)

            if index.end is None:
                end = self._end
            else:
                end = self.mapIndexToContainer(index.end)

            if index.step is None:
                step = self._step
            else:
                step = self._step*index.step

            self._container[start:end:step] = value

        self._container[self.mapIndexToContainer(index)] = value
