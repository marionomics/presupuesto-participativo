import pytest
import pandas as pd
from code.simulation.data_loader import load_pb_data, PBData

def test_load_returns_pbdata(tmp_path):
    votes = tmp_path / "votes.csv"
    votes.write_text("project_id,district_id,votes\np1,d1,100\np2,d1,50\np3,d2,200\n")
    projects = tmp_path / "projects.csv"
    projects.write_text("project_id,district_id,name,cost_mxn\np1,d1,Park,40000\np2,d1,School,30000\np3,d2,Road,50000\n")

    data = load_pb_data(str(votes), str(projects), budget=200000.0, vote_endowment=6)

    assert isinstance(data, PBData)
    assert set(data.projects.project_id) == {"p1", "p2", "p3"}
    assert data.districts == ["d1", "d2"]
    assert data.budget == 200000.0
    assert data.vote_endowment == 6

def test_projects_have_required_columns(tmp_path):
    votes = tmp_path / "votes.csv"
    votes.write_text("project_id,district_id,votes\np1,d1,100\n")
    projects = tmp_path / "projects.csv"
    projects.write_text("project_id,district_id,name,cost_mxn\np1,d1,Park,40000\n")
    data = load_pb_data(str(votes), str(projects), budget=100000.0, vote_endowment=6)
    for col in ["project_id", "district_id", "name", "cost_mxn", "votes"]:
        assert col in data.projects.columns
