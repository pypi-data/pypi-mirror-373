
def _quickselect(arr, k):
    def select(left, right, k):
        if left == right:
            return arr[left]
        # deterministic pivot = middle element
        pivot_index = (left + right) // 2
        pivot_value = arr[pivot_index]
        arr[pivot_index], arr[right] = arr[right], arr[pivot_index]
        store_index = left
        for i in range(left, right):
            if arr[i] < pivot_value:
                arr[store_index], arr[i] = arr[i], arr[store_index]
                store_index += 1
        arr[right], arr[store_index] = arr[store_index], arr[right]
        if k == store_index:
            return arr[k]
        elif k < store_index:
            return select(left, store_index - 1, k)
        else:
            return select(store_index + 1, right, k)
    return select(0, len(arr) - 1, k)

def detect_outliers_iqr(data):
    n = len(data)
    if n < 4:
        return []
    arr_copy = data[:]
    q1 = _quickselect(arr_copy, n // 4)
    arr_copy = data[:]
    q3 = _quickselect(arr_copy, (3 * n) // 4)
    IQR = q3 - q1
    lower_bound = q1 - 1.5 * IQR
    upper_bound = q3 + 1.5 * IQR

    outliers = []
    for i, val in enumerate(data):
        if val < lower_bound or val > upper_bound:
            outliers.append((i, val))
    return outliers
