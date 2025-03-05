import pygame

def quick_sort(arr, draw_array, delay, low=0, high=None):
    if high is None:
        high = len(arr) - 1

    if low < high:
        pi = yield from partition(arr, low, high, draw_array, delay)
        yield from quick_sort(arr, draw_array, delay, low, pi - 1)
        yield from quick_sort(arr, draw_array, delay, pi + 1, high)


def partition(arr, low, high, draw_array, delay):
    pivot = arr[high]
    i = low

    for j in range(low, high):
        if arr[j] < pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
        draw_array(arr, i, j)
        pygame.time.delay(delay)
        yield

    arr[i], arr[high] = arr[high], arr[i]
    draw_array(arr, i, high)
    pygame.time.delay(delay)
    yield

    return i

def optimized_quick_sort(arr, draw_array, delay):
    if len(arr) <= 1:
        return arr

    first = arr[0]
    middle = arr[len(arr) // 2]
    last = arr[-1]
    pivot = sorted([first, middle, last])[1]

    left = []
    middle_section = []
    right = []

    for num in arr:
        if num < pivot:
            left.append(num)
        elif num == pivot:
            middle_section.append(num)
        else:
            right.append(num)

        draw_array(left + middle_section + right)
        pygame.time.delay(delay)
        yield

    sorted_left = yield from optimized_quick_sort(left, draw_array, delay)
    sorted_right = yield from optimized_quick_sort(right, draw_array, delay)

    return sorted_left + middle_section + sorted_right

