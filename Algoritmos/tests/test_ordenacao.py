import pytest
from sys import settrace
from Algoritmos.codigos.ordenacao import *
from Analise.analise import *

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
    settrace(showTrace)
    v = criaVetor(5, 5)
    assert expected == v
    settrace(None)

# Testes não-flaky
@pytest.mark.parametrize("origin, expected", values)
def test_bubbleSort(origin, expected):
    settrace(showTrace)
    v = bubbleSort(origin)
    assert expected == v
    settrace(None)

@pytest.mark.parametrize("origin, expected", values)
def test_heapSort(origin, expected):
    settrace(showTrace)
    v = heapSort(origin)
    assert expected == v
    settrace(None)

@pytest.mark.parametrize("origin, expected", values)
def test_insertionSort(origin, expected):
    settrace(showTrace)
    v = insertionSort(origin)
    assert expected == v
    settrace(None)