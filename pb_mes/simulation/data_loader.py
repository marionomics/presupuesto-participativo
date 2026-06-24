# code/simulation/data_loader.py
from dataclasses import dataclass
import pandas as pd

@dataclass
class PBData:
    projects: pd.DataFrame   # project_id, district_id, name, cost_mxn, votes
    districts: list[str]
    budget: float
    vote_endowment: int

def load_pb_data(votes_path: str, projects_path: str,
                 budget: float, vote_endowment: int = 6) -> PBData:
    votes = pd.read_csv(votes_path)
    projects = pd.read_csv(projects_path)
    merged = projects.merge(votes[["project_id", "votes"]], on="project_id", how="left")
    merged["votes"] = merged["votes"].fillna(0).astype(int)
    districts = sorted(merged["district_id"].unique().tolist())
    return PBData(projects=merged, districts=districts,
                  budget=budget, vote_endowment=vote_endowment)
