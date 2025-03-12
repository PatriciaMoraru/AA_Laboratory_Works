import pygame


def merge_sort(arr, draw_array, delay, left=0, right=None):
    if right is None:
        right = len(arr) - 1

    if left < right:
        mid = (left + right) // 2
        yield from merge_sort(arr, draw_array, delay, left, mid)
        yield from merge_sort(arr, draw_array, delay, mid + 1, right)
        yield from merge(arr, left, mid, right, draw_array, delay)


def merge(arr, left, mid, right, draw_array, delay):
    left_part = arr[left:mid + 1]
    right_part = arr[mid + 1:right + 1]

    i = j = 0
    k = left

    while i < len(left_part) and j < len(right_part):
        if left_part[i] < right_part[j]:
            arr[k] = left_part[i]
            highlight_index = i + left
            i += 1
        else:
            arr[k] = right_part[j]
            highlight_index = j + mid + 1
            j += 1
        k += 1
        draw_array(arr, highlight1=k, highlight2=highlight_index)
        yield
        pygame.time.delay(delay)

    while i < len(left_part):
        arr[k] = left_part[i]
        highlight_index = i + left
        i += 1
        k += 1
        draw_array(arr, highlight1=k, highlight2=highlight_index)
        yield
        pygame.time.delay(delay)

    while j < len(right_part):
        arr[k] = right_part[j]
        highlight_index = j + mid + 1
        j += 1
        k += 1
        draw_array(arr, highlight1=k, highlight2=highlight_index)
        yield
        pygame.time.delay(delay)
