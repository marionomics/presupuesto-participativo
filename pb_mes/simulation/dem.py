import pandas as pd

def run_dem(projects: pd.DataFrame, budget: float) -> list[str]:
    """Greedy funding by descending vote total until budget exhausted."""
    ranked = projects.sort_values("votes", ascending=False)
    funded = []
    remaining = budget
    for _, row in ranked.iterrows():
        if row["cost_mxn"] <= remaining:
            funded.append(row["project_id"])
            remaining -= row["cost_mxn"]
    return funded
