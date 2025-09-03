def magnet_sort(arr):
  left = 0
  right = len(arr) - 1

  while left < right:
    min_index = left
    max_index = left
    for i in range(left, right + 1):
      if arr[i] < arr[min_index]:
        min_index = i
      if arr[i] > arr[max_index]:
        max_index = i

    arr[left], arr[min_index] = arr[min_index], arr[left]

    if max_index == left:
      max_index = min_index

    arr[right], arr[max_index] = arr[max_index], arr[right]

    left += 1
    right -= 1

  return arr
    