import pytest
import numpy as np
from pb_mes.simulation.ballot_generator import generate_ballots
import pandas as pd


@pytest.fixture
def simple_projects():
    return pd.DataFrame({
        "project_id": ["p1", "p2", "p3"],
        "district_id": ["d1", "d1", "d2"],
        "votes": [100, 100, 200],
    })


def test_returns_correct_number_of_voters(simple_projects):
    ballots = generate_ballots(simple_projects, n_voters=50, seed=42)
    assert len(ballots) == 50


def test_every_voter_approves_at_least_one_project(simple_projects):
    ballots = generate_ballots(simple_projects, n_voters=200, seed=42)
    assert all(len(v) >= 1 for v in ballots.values())


def test_voter_ids_unique(simple_projects):
    ballots = generate_ballots(simple_projects, n_voters=10, seed=42)
    assert len(set(ballots.keys())) == 10


def test_approvals_only_from_one_district(simple_projects):
    # Under DEM-style ballot generation, each voter approves only
    # projects in the district they were assigned to
    ballots = generate_ballots(simple_projects, n_voters=500, seed=42)
    district_map = dict(zip(simple_projects.project_id, simple_projects.district_id))
    for voter, approved in ballots.items():
        districts_in_ballot = {district_map[p] for p in approved}
        assert len(districts_in_ballot) == 1, f"Voter {voter} spans districts: {districts_in_ballot}"


def test_deterministic_with_same_seed(simple_projects):
    b1 = generate_ballots(simple_projects, n_voters=20, seed=7)
    b2 = generate_ballots(simple_projects, n_voters=20, seed=7)
    assert b1 == b2


def test_different_seed_gives_different_ballots(simple_projects):
    b1 = generate_ballots(simple_projects, n_voters=200, seed=1)
    b2 = generate_ballots(simple_projects, n_voters=200, seed=2)
    assert b1 != b2
