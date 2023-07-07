from code.ordenacao import *
import pytest

values = [
    ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4]),
    ([4, 3, 2, 1, 0], [0, 1, 2, 3, 4]),
    ([3, 1, 4, 0, 2], [0, 1, 2, 3, 4])
]

@pytest.mark.parametrize("origin, expected", values)
def test_bubbleSort(origin, expected):
    assert expected == bubbleSort(origin)

@pytest.mark.parametrize("origin, expected", values)
def test_heapSort(origin, expected):
    assert expected == heapSort(origin)

@pytest.mark.parametrize("origin, expected", values)
def test_insertionSort(origin, expected):
    assert expected == insertionSort(origin)