def winsorize_quartiles(data):
    print(">> Custom winsorize_adaptive running!")
    if len(data) < 4:
        return data[:]

    sorted_data = sorted(data)
    n = len(sorted_data)

    # Q1 and Q3 indices
    q1_index = n // 4
    q3_index = (3 * n) // 4
    q1 = sorted_data[q1_index]
    q3 = sorted_data[q3_index]

    # Nearest valid inliers
    lower_replacement = next(x for x in sorted_data if x >= q1)
    upper_replacement = max(x for x in sorted_data if x <= q3)

    new_data = []
    for x in data:
        if x < q1:
            new_data.append(lower_replacement)   # Use nearest inlier above Q1 (85)
        elif x > q3:
            new_data.append(upper_replacement)   # Use nearest inlier below Q3 (93)
        else:
            new_data.append(x)
    return new_data


def winsorize_inliers(data):
    """
    Custom winsorization:
    - Sorts the data
    - Replaces low outliers with the smallest inlier
    - Replaces high outliers with the largest inlier
    - Keeps other values unchanged
    """

    if len(data) < 4:
        return data[:]

    # Sort the data
    sorted_data = sorted(data)

    # Use IQR to detect outliers
    n = len(sorted_data)
    q1_index = n // 4
    q3_index = (3 * n) // 4
    q1 = sorted_data[q1_index]
    q3 = sorted_data[q3_index]
    iqr = q3 - q1
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr

    # Identify inliers
    inliers = [x for x in sorted_data if lower_fence <= x <= upper_fence]

    # Determine nearest inlier values for replacement
    min_inlier = min(inliers)
    max_inlier = max(inliers)

    # Replace outliers
    new_data = []
    for x in data:
        if x < lower_fence:
            new_data.append(min_inlier)
        elif x > upper_fence:
            new_data.append(max_inlier)
        else:
            new_data.append(x)

    return new_data
