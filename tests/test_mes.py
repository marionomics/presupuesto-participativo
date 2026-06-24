import pytest
from pb_mes.simulation.mes import run_mes, compute_rho


# ── Unit tests for compute_rho ──────────────────────────────────────

def test_rho_uniform_supporters():
    # 3 supporters with b_i=25 each, cost=40 → rho = 40/3 ≈ 13.333
    shares = {"v1": 25.0, "v2": 25.0, "v3": 25.0}
    rho = compute_rho(["v1", "v2", "v3"], shares, 40.0)
    assert rho == pytest.approx(40 / 3, rel=1e-6)


def test_rho_infeasible_returns_none():
    shares = {"v1": 5.0, "v2": 5.0}
    assert compute_rho(["v1", "v2"], shares, 20.0) is None


def test_rho_one_rich_one_poor():
    # v1 has 5, v2 has 25; cost=20 → v1 contributes 5, v2 contributes 15 → rho=15
    shares = {"v1": 5.0, "v2": 25.0}
    rho = compute_rho(["v1", "v2"], shares, 20.0)
    assert rho == pytest.approx(15.0, rel=1e-6)


# ── Regression: 4-voter example (shadow_paper.tex §3) ───────────────
# Setup: n=4, B=100, b_i=25; 4 projects p1(40,Center), p2(30,Marginal),
# p3(50,Center), p4(20,Marginal)
# Approvals: v1={p1,p3}, v2={p1,p3}, v3={p1,p2}, v4={p2,p4}
# Expected: W = {p1, p2, p4}

def test_4voter_shadow_paper_example():
    approvals = {
        "v1": {"p1", "p3"},
        "v2": {"p1", "p3"},
        "v3": {"p1", "p2"},
        "v4": {"p2", "p4"},
    }
    costs = {"p1": 40.0, "p2": 30.0, "p3": 50.0, "p4": 20.0}
    funded = run_mes(approvals, costs, budget=100.0)
    assert set(funded) == {"p1", "p2", "p4"}


# ── Regression: MES does NOT fund p3 ─────────────────────────────────
def test_4voter_p3_not_funded():
    approvals = {
        "v1": {"p1", "p3"}, "v2": {"p1", "p3"},
        "v3": {"p1", "p2"}, "v4": {"p2", "p4"},
    }
    costs = {"p1": 40.0, "p2": 30.0, "p3": 50.0, "p4": 20.0}
    funded = run_mes(approvals, costs, budget=100.0)
    assert "p3" not in funded


# ── Basic properties ─────────────────────────────────────────────────
def test_funded_set_fits_budget():
    approvals = {"v1": {"p1"}, "v2": {"p2"}, "v3": {"p1", "p2"}}
    costs = {"p1": 30.0, "p2": 30.0}
    funded = run_mes(approvals, costs, budget=50.0)
    assert sum(costs[p] for p in funded) <= 50.0


def test_empty_approvals_returns_empty():
    assert run_mes({}, {}, 100.0) == []


def test_no_affordable_project_returns_empty():
    approvals = {"v1": {"p1"}}
    costs = {"p1": 200.0}
    funded = run_mes(approvals, costs, budget=50.0)
    assert funded == []
