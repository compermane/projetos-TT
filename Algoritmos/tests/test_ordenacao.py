from code.ordenacao import *
import pytest

values = [
    ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4]),
    ([4, 3, 2, 1, 0], [0, 1, 2, 3, 4]),
    ([3, 1, 4, 0, 2], [0, 1, 2, 3, 4])
]

flakyValues = [
    ([0, 1, 2, 3, 4]),
    ([4, 3, 2, 1, 0]),
    ([3, 5, 2, 1, 3])
]

# Teste flaky
@pytest.mark.parametrize("expected", flakyValues)
def test_criaVetor(expected):
    assert expected == criaVetor(5, 5)

# Testes não-flaky
@pytest.mark.parametrize("origin, expected", values)
def test_bubbleSort(origin, expected):
    assert expected == bubbleSort(origin)

@pytest.mark.parametrize("origin, expected", values)
def test_heapSort(origin, expected):
    assert expected == heapSort(origin)

@pytest.mark.parametrize("origin, expected", values)
def test_insertionSort(origin, expected):
    assert expected == insertionSort(origin)