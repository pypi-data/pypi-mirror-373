def replace_outliers(data, method="IQR"):
    n = len(data)
    if n == 0:
        return []
    new_data = data[:]

    # Detect if numeric or categorical
    is_numeric = True
    for x in new_data:
        if not isinstance(x, (int, float)):
            is_numeric = False
            break

    # Compute replacement value
    if not is_numeric:
        # Categorical → use mode
        freq = {}
        for x in new_data:
            freq[x] = freq.get(x, 0) + 1
        max_count = 0
        mode_val = None
        for key, count in freq.items():
            if count > max_count:
                max_count = count
                mode_val = key
        rep_val = mode_val
    else:
        # Numeric → choose mean or median based on skewness
        total = sum(new_data)
        mean = total / n
        sorted_data = sorted(new_data)
        median = sorted_data[n // 2]

        # Compute standard deviation
        m2 = 0
        for x in new_data:
            m2 += (x - mean) ** 2
        std_dev = (m2 / n) ** 0.5

        if std_dev == 0:
            skewness = 0
        else:
            skewness = 3 * (mean - median) / std_dev

        if abs(skewness) < 0.5:
            rep_val = mean
        else:
            rep_val = median

    # Apply method
    if method == "IQR":
        if is_numeric:
            q1 = _quickselect(new_data[:], n // 4)
            q3 = _quickselect(new_data[:], (3 * n) // 4)
            IQR = q3 - q1
            lower = q1 - 1.5 * IQR
            upper = q3 + 1.5 * IQR
            for i in range(n):
                if new_data[i] < lower or new_data[i] > upper:
                    new_data[i] = rep_val
        else:
            # For categorical: replace rare categories with mode
            for i in range(n):
                if freq[new_data[i]] < max_count:
                    new_data[i] = rep_val

    elif method == "Zscore" and is_numeric:
        m2 = 0
        count = 0
        mean = 0
        for x in new_data:
            count += 1
            delta = x - mean
            mean += delta / count
            delta2 = x - mean
            m2 += delta * delta2
        std_dev = (m2 / n) ** 0.5
        for i in range(n):
            z = (new_data[i] - mean) / std_dev
            if abs(z) > 3:
                new_data[i] = rep_val

    return new_data


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
