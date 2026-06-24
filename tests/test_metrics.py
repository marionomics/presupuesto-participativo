import pytest
import pandas as pd
from pb_mes.simulation.metrics import welfare, district_allocations, equity_gini


@pytest.fixture
def projects():
    return pd.DataFrame({
        "project_id": ["p1", "p2", "p3", "p4"],
        "district_id": ["d1", "d1", "d2", "d2"],
        "cost_mxn": [40.0, 30.0, 50.0, 20.0],
        "votes": [300, 100, 200, 80],
    })


def test_welfare_sums_votes(projects):
    assert welfare(["p1", "p3"], projects) == pytest.approx(500.0)


def test_welfare_empty(projects):
    assert welfare([], projects) == 0.0


def test_district_allocations(projects):
    alloc = district_allocations(["p1", "p4"], projects)
    assert alloc == {"d1": 40.0, "d2": 20.0}


def test_district_allocations_includes_zero_districts(projects):
    alloc = district_allocations(["p1"], projects)
    assert alloc["d2"] == 0.0


def test_equity_gini_equal(projects):
    # Fund p1(d1,40) and p3(d2,50) → close but not equal; Gini > 0
    g = equity_gini(["p1", "p3"], projects)
    assert 0.0 <= g <= 1.0


def test_equity_gini_zero_when_equal(projects):
    # Fund p2(d1,30) and p4(d2,30) → equal allocation → Gini = 0
    # Actually costs differ (30 and 20). Let's use equal costs manually.
    proj2 = projects.copy()
    proj2.loc[proj2.project_id == "p4", "cost_mxn"] = 30.0
    g = equity_gini(["p2", "p4"], proj2)
    assert g == pytest.approx(0.0, abs=1e-9)
