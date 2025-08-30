
def remove_outliers(data, method="IQR"):
    n = len(data)
    if n == 0:
        return []

    cleaned_data = []
    if method == "IQR":
        q1 = _quickselect(data[:], n // 4)
        q3 = _quickselect(data[:], (3 * n) // 4)
        IQR = q3 - q1
        lower = q1 - 1.5 * IQR
        upper = q3 + 1.5 * IQR
        for val in data:
            if lower <= val <= upper:
                cleaned_data.append(val)

    elif method == "Zscore":
        mean = 0
        m2 = 0
        count = 0
        for x in data:
            count += 1
            delta = x - mean
            mean += delta / count
            delta2 = x - mean
            m2 += delta * delta2
        std_dev = (m2 / n) ** 0.5
        for val in data:
            z = (val - mean) / std_dev
            if abs(z) <= 3:
                cleaned_data.append(val)

    return cleaned_data

def _quickselect(arr, k):
    def select(left, right, k):
        if left == right:
            return arr[left]
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
