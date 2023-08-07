import pytest
from sys import settrace
from random import randint
from Algoritmos.codigos.ordenacao import *
from Analise.analise import *

values = [
    ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4]),
    ([4, 3, 2, 1, 0], [0, 1, 2, 3, 4]),
    ([3, 1, 4, 0, 2], [0, 1, 2, 3, 4])
]

# Teste flaky
@pytest.mark.parametrize("execution_number", range(5))
def test_criaVetor(execution_number):
    settrace(showTrace)
    rand = randint(0, 10)
    v = criaVetor(5, 5)
    assert rand in v
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

@pytest.mark.parametrize("origin, expected", values)
def test_mergeSort(origin, expected):
    settrace(showTrace)
    v = mergeSort(origin)
    assert expected == v
    settrace(None)