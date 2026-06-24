"""
Method of Equal Shares (MES) simulation.

Implements the ρ(p) algorithm from the paper:
  compute_rho: find the minimum cost-per-supporter threshold
  run_mes: full MES phase followed by greedy completion phase
"""

RANDOM_SEED = 42


def compute_rho(
    supporters: list[str],
    shares: dict[str, float],
    cost: float,
) -> float | None:
    """
    Compute the minimum ρ ≥ 0 such that Σ_{i∈supporters} min(b_i, ρ) ≥ cost.

    Returns None if infeasible (total available budget across supporters < cost).
    """
    total_available = sum(shares[i] for i in supporters)
    if total_available < cost:
        return None

    # Binary search over [0, max_share]
    lo, hi = 0.0, max(shares[i] for i in supporters)
    for _ in range(64):
        mid = (lo + hi) / 2
        if sum(min(shares[i], mid) for i in supporters) >= cost:
            hi = mid
        else:
            lo = mid
    return hi


def run_mes(
    approvals: dict[str, set[str]],
    costs: dict[str, float],
    budget: float,
) -> list[str]:
    """
    Method of Equal Shares.

    Parameters
    ----------
    approvals : dict[str, set[str]]
        Mapping from voter_id to the set of project_ids that voter approves.
    costs : dict[str, float]
        Mapping from project_id to its cost.
    budget : float
        Total available budget.

    Returns
    -------
    list[str]
        Funded project_ids in funding order (MES phase first, then completion).
    """
    if not approvals or not costs:
        return []

    n = len(approvals)
    # Each voter starts with an equal virtual budget share
    shares: dict[str, float] = {i: budget / n for i in approvals}
    funded: list[str] = []
    remaining: set[str] = set(costs.keys())

    # ── MES phase ──────────────────────────────────────────────────────
    # Repeatedly fund the project with the lowest ρ (cost-per-supporter
    # threshold), deducting each supporter's contribution from their share.
    while True:
        best_p: str | None = None
        best_rho: float = float("inf")

        for p in remaining:
            supporters = [
                i for i in approvals if p in approvals[i] and shares[i] > 0
            ]
            if not supporters:
                continue
            rho = compute_rho(supporters, shares, costs[p])
            if rho is not None and rho < best_rho:
                best_rho = rho
                best_p = p

        if best_p is None:
            break

        # Deduct each supporter's contribution: min(b_i, ρ)
        for i in approvals:
            if best_p in approvals[i] and shares[i] > 0:
                shares[i] -= min(shares[i], best_rho)

        funded.append(best_p)
        remaining.remove(best_p)

    # ── Completion phase: greedy by approval count ──────────────────────
    # Use any remaining budget to fund additional projects, prioritising
    # those with the most supporters (ties broken by project_id for
    # determinism).
    spent = sum(costs[p] for p in funded)
    leftover = budget - spent
    approval_count = {
        p: sum(1 for i in approvals if p in approvals[i])
        for p in remaining
    }
    for p in sorted(remaining, key=lambda p: (-approval_count[p], p)):
        if costs[p] <= leftover:
            funded.append(p)
            leftover -= costs[p]

    return funded
