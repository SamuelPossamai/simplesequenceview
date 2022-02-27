
from collections.abc import Sequence, MutableSequence, Iterator

class RangeIterator(Iterator):

    def __init__(self, container, start, end, step=1):
        self.__container = container
        self.__range = iter(range(start, end, step))

    def __iter__(self):
        return self

    def __next__(self):
        return self.__container[next(self.__range)]

class SequenceViewIterator(RangeIterator):

    def __init__(self, view, container, start, end, step=1):
        super.__init__(container, start, end, step)
        self.__view = view

    def __next__(self):
        if not self.__view.isValid():
            raise RuntimeError('container changed size during iteration')

        super().__init__()

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
            end += len(container) + 1

        if step is None:
            step = 1

        self._container = container
        self._container_len = len(container)
        self._start = start
        self._end = end
        self._step = step
        self._qtd = (end - start)//step
        self._invalid = False

    def _createSlice(self, index):
        return type(self)(self._container, index.start, index.stop, index.step)

    def __iter__(self):
        return RangeIterator(self._container, self._start,
                             self._end, self._step)

    def __reversed__(self):
        return RangeIterator(self._container, self._end - 1,
                             self._start - 1, -self._step)

    def _assertNotModified(self):
        if not self.isValid():
            raise RuntimeError('container changed size')

    def restore(self, internal=False):

        new_len = len(self._container)

        if internal is True:
            self._end += (new_len - self._container_len)//self._step

        if self._start > new_len:
            self._start = new_len

        if self._end > new_len:
            self._end = new_len

        self._qtd = (self._end - self._start)//self._step
        self._container_len = new_len
        self._invalid = False

    def isValid(self):

        if len(self._container) != self._container_len:
            self._invalid = True
            return False

        return not self._invalid

    def __getitem__(self, index):

        self._assertNotModified()

        if isinstance(index, slice):
            return self._createSlice(self.mapSliceToContainer(index))

        return self._container[self.mapIndexToContainer(index)]

    def mapIndexToContainer(self, index, raise_error=True):

        if index < 0:
            index += self._qtd

        if index >= self._qtd:
            if raise_error:
                raise IndexError('sequence view index out of range')

            index = self._qtd

        return self._start + index*self._step

    def mapSliceToContainer(self, index):

        if index.start is None:
            start = self._start
        else:
            start = self.mapIndexToContainer(index.start, raise_error=False)

        if index.stop is None:
            stop = self._end
        else:
            stop = self.mapIndexToContainer(index.stop, raise_error=False)

        if index.step is None:
            step = self._step
        else:
            step = self._step*index.step

        return slice(start, stop, step)

    def __len__(self):
        return self._qtd

    def __repr__(self):

        if not self.isValid():
            return f'{type(self).__name__}(INVALID)'

        string = f'{type(self).__name__}([{", ".join(str(i) for i in self)}]'

        if self._start != 0:
            string += f', start={self._start}'
        if self._end != len(self._container):
            string += f', end={self._end}'
        if self._step != 1:
            string += f', step={self._step}'

        return string + ')'

class MutableSequenceView(SequenceView, MutableSequence):

    def __setitem__(self, index, obj):

        self._assertNotModified()

        if isinstance(index, slice):
            index = self.mapSliceToContainer(index)
        else:
            index = self.mapIndexToContainer(index)

        self._container[index] = obj

        self.restore(True)

    def __delitem__(self, index):

        if self._step != 1:
            raise ValueError(
                'attempt to delete element from a non-sequential sequence view'
            )

        self._assertNotModified()

        if isinstance(index, slice):
            index = self.mapSliceToContainer(index)
        else:
            index = self.mapIndexToContainer(index)

        del self._container[index]
        self.restore(True)

    def insert(self, index, obj):

        if self._step != 1:
            raise ValueError(
                'attempt to insert element in a non-sequential sequence view'
            )

        self._assertNotModified()

        self._container.insert(self.mapIndexToContainer(index), obj)

        self.restore(True)

orig = list(range(10))

sequence = MutableSequenceView(orig)

sequence[:] = [1, 2, 3, 4]

print(sequence)
