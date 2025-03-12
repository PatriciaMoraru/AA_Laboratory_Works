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
        pygame.display.update()
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
        pygame.display.update()
        yield
        pygame.time.delay(delay)
        yield from heapify(arr, i, 0, draw_array, delay)
