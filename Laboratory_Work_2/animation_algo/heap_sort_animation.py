import pygame

def heapify(arr, n, i, draw_array, delay):
    max_idx = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and arr[left] > arr[max_idx]:
        max_idx = left
    if right < n and arr[right] > arr[max_idx]:
        max_idx = right
    if max_idx != i:
        arr[i], arr[max_idx] = arr[max_idx], arr[i]
        draw_array(arr, i, max_idx)
        yield
        pygame.time.delay(delay)


        yield from heapify(arr, n, max_idx, draw_array, delay)


def heap_sort(arr, draw_array, delay):
    n = len(arr)

    for i in range(n // 2 - 1, -1, -1):
        yield from heapify(arr, n, i, draw_array, delay)

    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        draw_array(arr, 0, i)
        yield
        pygame.time.delay(delay)

        yield from heapify(arr, i, 0, draw_array, delay)

def heapify_ternary(arr, n, i, draw_array, delay):
    while True:
        largest = i
        left = 3 * i + 1
        mid = 3 * i + 2
        right = 3 * i + 3

        if left < n and arr[left] > arr[largest]:
            largest = left
        if mid < n and arr[mid] > arr[largest]:
            largest = mid
        if right < n and arr[right] > arr[largest]:
            largest = right

        if largest == i:
            break

        arr[i], arr[largest] = arr[largest], arr[i]
        draw_array(arr, i, largest)  # Highlight the swap
        yield
        pygame.time.delay(delay)


        i = largest  # Continue heapifying


def heap_sort_ternary(arr, draw_array, delay):
    n = len(arr)

    for i in range(n // 3 - 1, -1, -1):
        yield from heapify_ternary(arr, n, i, draw_array, delay)

    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        draw_array(arr, 0, i)  # Highlight max element swap
        yield
        pygame.time.delay(delay)


        yield from heapify_ternary(arr, i, 0, draw_array, delay)
