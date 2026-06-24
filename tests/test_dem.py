import pytest
import pandas as pd
from pb_mes.simulation.dem import run_dem

def _make_projects(data):
    return pd.DataFrame(data, columns=["project_id", "district_id", "cost_mxn", "votes"])

def test_dem_funds_highest_vote_first():
    projects = _make_projects([
        ("p1", "d1", 40.0, 300),
        ("p2", "d1", 30.0, 100),
        ("p3", "d2", 50.0, 200),
    ])
    funded = run_dem(projects, budget=90.0)
    assert funded == ["p1", "p3"]  # 40+50=90; p2 ranked 3rd

def test_dem_stops_when_budget_exhausted():
    projects = _make_projects([
        ("p1", "d1", 60.0, 500),
        ("p2", "d1", 60.0, 400),
    ])
    funded = run_dem(projects, budget=90.0)
    assert funded == ["p1"]   # p2 can't fit

def test_dem_funds_nothing_when_all_too_expensive():
    projects = _make_projects([("p1", "d1", 200.0, 999)])
    assert run_dem(projects, budget=100.0) == []
