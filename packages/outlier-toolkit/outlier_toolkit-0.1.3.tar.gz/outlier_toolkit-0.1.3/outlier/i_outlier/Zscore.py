
def detect_outliers_zscore(data, threshold=3):
    n = len(data)
    if n == 0:
        return []
    # Welford's algorithm for mean and variance (no imports)
    mean = 0
    m2 = 0
    count = 0
    for x in data:
        count += 1
        delta = x - mean
        mean += delta / count
        delta2 = x - mean
        m2 += delta * delta2
    variance = m2 / n
    std_dev = variance ** 0.5

    outliers = []
    for i in range(n):
        z = (data[i] - mean) / std_dev
        if z > threshold or z < -threshold:
            outliers.append((i, data[i]))
    return outliers
