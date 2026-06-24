"""
Synthetic ballot generator for the MES counterfactual simulation.

Given aggregate DEM vote totals, generates individual approval ballots
that are statistically consistent with those totals. Each voter is
assigned to exactly one district (proportional to district total votes),
then approves each project in that district independently with probability
votes(p) / votes(district). At least one approval is guaranteed per voter.
"""
import numpy as np
import pandas as pd


def generate_ballots(
    projects: pd.DataFrame,
    n_voters: int,
    seed: int = 42,
) -> dict[str, set[str]]:
    """
    Generate synthetic approval ballots consistent with observed DEM vote totals.

    Parameters
    ----------
    projects : pd.DataFrame
        Must contain columns: project_id (str), district_id (str), votes (int).
    n_voters : int
        Number of synthetic voters to generate.
    seed : int
        Random seed for reproducibility (passed to numpy.random.default_rng).

    Returns
    -------
    dict[str, set[str]]
        Mapping from voter_id (e.g. "v00042") to the set of project_ids
        the voter approves. Each voter approves at least one project, and
        all approvals come from exactly one district.
    """
    rng = np.random.default_rng(seed)

    # District-level total votes for proportional district assignment
    district_totals = projects.groupby("district_id")["votes"].sum()
    district_ids = district_totals.index.tolist()
    district_probs = (district_totals / district_totals.sum()).values

    # Assign all voters to districts in one vectorised call
    assigned_districts = rng.choice(district_ids, size=n_voters, p=district_probs)

    ballots: dict[str, set[str]] = {}

    for voter_idx, district in enumerate(assigned_districts):
        voter_id = f"v{voter_idx:05d}"
        district_projects = projects[projects["district_id"] == district]
        proj_ids = district_projects["project_id"].tolist()
        proj_votes = district_projects["votes"].values.astype(float)
        proj_probs = proj_votes / proj_votes.sum()

        # Independent Bernoulli draw for each project in the district
        approved: set[str] = set()
        for i, pid in enumerate(proj_ids):
            if rng.random() < proj_probs[i]:
                approved.add(pid)

        # Guarantee at least one approval by re-sampling a single project
        if not approved:
            fallback_idx = int(rng.choice(len(proj_ids), p=proj_probs))
            approved.add(proj_ids[fallback_idx])

        ballots[voter_id] = approved

    return ballots
