def winsorize_standard(data, percentile=0.05):
    if len(data) < 4:
        return data[:]

    sorted_data = sorted(data)
    n = len(sorted_data)

    # Calculate index positions for percentile
    lower_idx = int(n * percentile)
    upper_idx = int(n * (1 - percentile)) - 1

    lower_limit = sorted_data[lower_idx]
    upper_limit = sorted_data[upper_idx]

    new_data = []
    for x in data:
        if x < lower_limit:
            new_data.append(lower_limit)
        elif x > upper_limit:
            new_data.append(upper_limit)
        else:
            new_data.append(x)
    return new_data
