
class RangeIterator:

    def __init__(self, container, start, end, step=1):
        self.__container = container
        self.__range = iter(range(start, end, step))

    def __iter__(self):
        return self

    def __next__(self):
        return self.__container[next(self.__range)]

class SequenceView:

    def __init__(self, container, start=0, end=-1):

        if end < 0:
            end += len(container)

        self._container = container
        self.__start = start
        self.__end = end
        self.__qtd = 1 + end - start

    def __iter__(self):
        return RangeIterator(self._container, self.__start, self.__end)

    def __reversed__(self):
        return RangeIterator(self._container, self.__end - 1,
                             self.__start - 1, -1)

    def __getitem__(self, index):
        return self._container[self.mapIndexToContainer(index)]

    def mapIndexToContainer(self, index, raise_error=False):
        if index < 0:
            index += self.__qtd

        if index >= self.__qtd:
            if raise_error:
                raise IndexError('sequence view index out of range')
            return None
        return self.__start + index

    def mapIndexFromContainer(self, index, raise_error=False):
        if index < 0:
            index += len(self._container)

        if self.__start <= index < self.__end:
            return index - self.__start

        if raise_error:
            raise IndexError('sequence index out of range')
        return None

class MutableSequenceView(SequenceView):

    def __setitem__(self, index, value):
        self._container[self.mapIndexToContainer(index)] = value
