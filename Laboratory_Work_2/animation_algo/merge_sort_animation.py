import pygame

def merge_sort(arr, draw_array, delay):
    if len(arr) > 1:
        mid = len(arr) // 2
        left_arr = arr[:mid]
        right_arr = arr[mid:]

        yield from merge_sort(left_arr, draw_array, delay)
        yield from merge_sort(right_arr, draw_array, delay)

        i = j = k = 0

        while i < len(left_arr) and j < len(right_arr):
            if left_arr[i] < right_arr[j]:
                arr[k] = left_arr[i]
                i += 1
            else:
                arr[k] = right_arr[j]
                j += 1
            k += 1
            draw_array(arr)
            pygame.time.delay(delay)
            yield

        while i < len(left_arr):
            arr[k] = left_arr[i]
            i += 1
            k += 1
            draw_array(arr)
            pygame.time.delay(delay)
            yield

        while j < len(right_arr):
            arr[k] = right_arr[j]
            j += 1
            k += 1
            draw_array(arr)
            pygame.time.delay(delay)
            yield


def merge_bu(arr, left, mid, right, draw_array, delay):
    left_part = arr[left:mid + 1]
    right_part = arr[mid + 1:right + 1]

    i = j = 0
    k = left

    while i < len(left_part) and j < len(right_part):
        if left_part[i] < right_part[j]:
            arr[k] = left_part[i]
            i += 1
        else:
            arr[k] = right_part[j]
            j += 1
        k += 1
        draw_array(arr)
        pygame.time.delay(delay)
        yield

    while i < len(left_part):
        arr[k] = left_part[i]
        i += 1
        k += 1
        draw_array(arr)
        pygame.time.delay(delay)
        yield

    while j < len(right_part):
        arr[k] = right_part[j]
        j += 1
        k += 1
        draw_array(arr)
        pygame.time.delay(delay)
        yield


def bottom_up_merge_sort(arr, draw_array, delay):
    n = len(arr)
    size = 1
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(left + size - 1, n - 1)
            right = min(left + 2 * size - 1, n - 1)
            if mid < right:
                yield from merge_bu(arr, left, mid, right, draw_array, delay)
        size *= 2
