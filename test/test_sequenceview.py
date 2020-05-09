
import random

import unittest

from simplesequenceview import RangeIterator

class TestRangeIterator(unittest.TestCase):

    def test_iter(self):

        samples = ([random.randint(-1000, 1000)
                    for _ in range(random.randint(10, 1000))]
                   for _ in range(20))

        for sample in samples:
            start = random.randint(0, len(sample) - 1)
            end = random.randint(start, len(sample) - 1)
            step = random.randint(1, 7)

            RangeIterator([1, 5, 7, 1, 9, 0], 3, 5)

            self.assertEqual(
                list(iter(RangeIterator(sample, start, end, step))),
                sample[start:end:step])

if __name__ == '__main__':
    unittest.main()
