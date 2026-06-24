"""Welfare and equity metrics for comparing mechanism outcomes."""

import pandas as pd
from pb_mes.utils.gini import gini


def welfare(funded: list[str], projects: pd.DataFrame) -> float:
    """Compute total welfare as sum of votes for funded projects.

    Args:
        funded: List of project IDs that are funded.
        projects: DataFrame with columns 'project_id' and 'votes'.

    Returns:
        Sum of votes for funded projects.
    """
    if not funded:
        return 0.0
    funded_df = projects[projects["project_id"].isin(funded)]
    return float(funded_df["votes"].sum())


def district_allocations(funded: list[str], projects: pd.DataFrame) -> dict[str, float]:
    """Compute total funding by district for funded projects.

    Args:
        funded: List of project IDs that are funded.
        projects: DataFrame with columns 'project_id', 'district_id', and 'cost_mxn'.

    Returns:
        Dictionary mapping district_id to total funding (cost_mxn) for that district.
        Includes all districts (with 0.0 if no projects funded in that district).
    """
    alloc = {d: 0.0 for d in projects["district_id"].unique()}
    if funded:
        funded_df = projects[projects["project_id"].isin(funded)]
        for _, row in funded_df.iterrows():
            alloc[row["district_id"]] += row["cost_mxn"]
    return alloc


def equity_gini(funded: list[str], projects: pd.DataFrame) -> float:
    """Compute Gini coefficient of district-level funding allocation.

    Measures inequality in how funding is distributed across districts.
    A Gini of 0 means equal funding in all districts; 1 means all funding
    in a single district.

    Args:
        funded: List of project IDs that are funded.
        projects: DataFrame with columns 'project_id', 'district_id', and 'cost_mxn'.

    Returns:
        Gini coefficient of district-level funding shares in [0, 1].
    """
    alloc = district_allocations(funded, projects)
    return gini(list(alloc.values()))
