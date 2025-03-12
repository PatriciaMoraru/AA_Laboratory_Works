from collections import deque
import pygame


def counting_sort(arr, exp, draw_array, delay):
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    print(f"\n[DEBUG] Counting Sort Pass (exp = {exp}): Initial array: {arr}")

    for i in range(n):
        index = (arr[i] // exp) % 10
        count[index] += 1
    print(f"[DEBUG] Digit frequency count: {count}")

    for i in range(1, 10):
        count[i] += count[i - 1]
    print(f"[DEBUG] Cumulative count array: {count}")

    for i in range(n - 1, -1, -1):
        index = (arr[i] // exp) % 10
        output[count[index] - 1] = arr[i]
        print(f"[DEBUG] Placing {arr[i]} at position {count[index] - 1}")
        count[index] -= 1

    print(f"[DEBUG] Output array after sorting by digit {exp}: {output}")

    for i in range(n):
        arr[i] = output[i]
        draw_array(arr, highlight1=i, highlight2=count[(arr[i] // exp) % 10])
        pygame.display.update()
        yield
        pygame.time.delay(delay)

    print(f"[DEBUG] Updated array after sorting by exp {exp}: {arr}")


def radix_sort(arr, draw_array, delay):
    if not arr:
        return arr

    max_num = max(arr)
    exp = 1
    print(f"\n[DEBUG] Starting Radix Sort on array: {arr}")

    while max_num // exp > 0:
        print(f"\n[DEBUG] Sorting by digit place {exp}")
        yield from counting_sort(arr, exp, draw_array, delay)
        exp *= 10

    print(f"\n[DEBUG] Final sorted array: {arr}")
