def gini(values: list[float]) -> float:
    """Gini coefficient of a distribution. Returns 0 for perfect equality.

    The Gini coefficient measures inequality on a scale from 0 (perfect
    equality) to 1 (perfect inequality). Computed using the standard formula:
    G = Σ(2i - n - 1) * v_i / (n * Σ v_i) where v is sorted in ascending order.

    Args:
        values: List of non-negative floats representing the distribution.

    Returns:
        Gini coefficient in [0, 1].
    """
    n = len(values)
    if n == 0 or sum(values) == 0:
        return 0.0
    sorted_v = sorted(values)
    cumsum = sum((2 * (i + 1) - n - 1) * v for i, v in enumerate(sorted_v))
    return cumsum / (n * sum(sorted_v))
