#Equal Width Binning
def eq_width_bin(data, bins=5):
    if not data:
        return {}

    min_val, max_val = min(data), max(data)
    bin_width = (max_val - min_val) / bins if bins > 0 else 1

    bins_dict = {}
    for value in data:
        bin_index = int((value - min_val) // bin_width) if bin_width > 0 else 0
        if bin_index == bins:  # edge case for max value
            bin_index -= 1
        bin_range = (min_val + bin_index * bin_width, min_val + (bin_index + 1) * bin_width)
        bins_dict.setdefault(bin_range, []).append(value)

    return bins_dict


#Equal Frequency Binning
def eq_freq_bin(data, bins=5):
    if not data:
        return {}

    sorted_data = sorted(data)
    n = len(sorted_data)
    bin_size = max(1, n // bins)

    bins_dict = {}
    for i in range(bins):
        start = i * bin_size
        end = (i + 1) * bin_size if i < bins - 1 else n
        bins_dict[f"bin_{i+1}"] = sorted_data[start:end]

    return bins_dict


#Custom_binning
def custom_binning(data):
    if not data:
        return {}

    # Sort data
    sorted_data = sorted(data)
    n = len(sorted_data)

    # Calculate Q1, Q3
    q1_index = n // 4
    q3_index = (3 * n) // 4
    q1 = sorted_data[q1_index]
    q3 = sorted_data[q3_index]

    iqr = q3 - q1
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr

    # Split outliers and inliers
    bins_dict = {"below": [], "above": [], "inliers": []}
    for x in data:
        if x < lower_fence:
            bins_dict["below"].append(x)
        elif x > upper_fence:
            bins_dict["above"].append(x)
        else:
            bins_dict["inliers"].append(x)

    return bins_dict

