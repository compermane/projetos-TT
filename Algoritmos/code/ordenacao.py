import random

def criaVetor(n, rng) -> list:
    v = list()
    for i in range(n):
        v.append(random.randint(0, rng))

    return v

def bubbleSort(v):
    for i in range(0, len(v) - 1):
        for j in range(i, len(v)):
            if v[i] >= v[j]:
                v[i], v[j] = v[j], v[i]

    return v

def heapify(L, n, i):
    l = (i * 2) + 1
    r = (i * 2) + 2
    largest = i

    if l < n and L[i] < L[l]:
        largest = l
    if r < n and L[largest] < L[r]:
        largest = r
    if largest != i:
        L[i], L[largest] = L[largest], L[i]
        heapify(L, n, largest)


def heapSort(L):
    n = len(L)

    for i in range(n // 2, -1, -1):
        heapify(L, n, i)

    for i in range(n - 1, 0, -1):
        L[i], L[0] = L[0], L[i]
        heapify(L, i, 0)

    return L

def insertionSort(L):
    n = len(L)

    for i in range(2, n):
        k = i
        while k > 1 and L[k] < L[k - 1]:
            L[k], L[k - 1] = L[k - 1], L[k]
            k -= 1

    return L