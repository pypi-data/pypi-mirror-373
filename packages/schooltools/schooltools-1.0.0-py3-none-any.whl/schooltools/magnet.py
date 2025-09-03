def magnet_sort(arr):
    left = 0
    right = len(arr) - 1

    while left < right:
        min_index = left
        max_index = left
        swapped = False

        for i in range(left, right + 1):
            if arr[i] < arr[min_index]:
                min_index = i
            elif arr[i] > arr[max_index]:
                max_index = i

        # Swap min to the left if needed
        if min_index != left:
            arr[left], arr[min_index] = arr[min_index], arr[left]
            swapped = True

        # Adjust max_index if it was at left
        if max_index == left:
            max_index = min_index

        # Swap max to the right if needed
        if max_index != right:
            arr[right], arr[max_index] = arr[max_index], arr[right]
            swapped = True

        # Early exit if nothing changed
        if not swapped:
            break

        left += 1
        right -= 1

    return arr
