from collections import deque
import pygame

def counting_sort(arr, exp, draw_array, delay):
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    for i in range(n):
        index = (arr[i] // exp) % 10
        count[index] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    for i in range(n - 1, -1, -1):
        index = (arr[i] // exp) % 10
        output[count[index] - 1] = arr[i]
        count[index] -= 1

    for i in range(n):
        arr[i] = output[i]
        draw_array(arr, highlight1=i)  # Highlight moving elements
        yield  # Yield to allow animation
        pygame.time.delay(delay)


def radix_sort(arr, draw_array, delay):
    if not arr:
        return arr

    max_num = max(arr)
    exp = 1

    while max_num // exp > 0:
        yield from counting_sort(arr, exp, draw_array, delay)
        exp *= 10

def iterative_msd_radix_sort(arr, draw_array, delay):
    if len(arr) <= 1:
        return arr

    from collections import deque
    max_num = max(arr)
    max_digit = len(str(max_num)) - 1

    queue = deque([(arr, max_digit)])
    sorted_list = []

    while queue:
        current_arr, digit = queue.popleft()

        if len(current_arr) <= 1 or digit < 0:
            sorted_list.extend(current_arr)
            draw_array(sorted_list)  # Update visualization
            yield
            pygame.time.delay(delay)
            continue

        buckets = [[] for _ in range(10)]

        for num in current_arr:
            index = (num // (10 ** digit)) % 10
            buckets[index].append(num)

        for bucket in buckets:
            if bucket:
                queue.append((bucket, digit - 1))

        sorted_list.clear()
        for bucket in buckets:
            sorted_list.extend(bucket)
            draw_array(sorted_list)  # Update visualization
            yield
            pygame.time.delay(delay)

    arr[:] = sorted_list  # Update original array

