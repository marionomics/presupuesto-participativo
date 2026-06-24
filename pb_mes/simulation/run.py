"""
Main simulation script: DEM vs MES comparison for Durango PP 2025.

Usage:
    python3 -m pb_mes.simulation.run [--budget FLOAT] [--n-voters INT] [--seed INT]
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for PDF output
import matplotlib.pyplot as plt
import pandas as pd

from pb_mes.simulation.data_loader import load_pb_data
from pb_mes.simulation.ballot_generator import generate_ballots
from pb_mes.simulation.dem import run_dem
from pb_mes.simulation.mes import run_mes
from pb_mes.simulation.metrics import welfare, district_allocations, equity_gini

# ── Paths ────────────────────────────────────────────────────────────────────
VOTES_PATH    = "data/raw/pp2025_votes.csv"
PROJECTS_PATH = "data/raw/pp2025_projects.csv"
OUT_FIG_DIR   = "paper/figures"
OUT_TAB_DIR   = "paper/tables"


# ── Main ─────────────────────────────────────────────────────────────────────

def main(budget: float, n_voters: int, seed: int) -> None:
    # ── 1. Load data ──────────────────────────────────────────────────────────
    data = load_pb_data(VOTES_PATH, PROJECTS_PATH, budget=budget)

    # ── 2. DEM baseline ───────────────────────────────────────────────────────
    dem_funded  = run_dem(data.projects, budget)
    dem_welfare = welfare(dem_funded, data.projects)
    dem_alloc   = district_allocations(dem_funded, data.projects)
    dem_gini    = equity_gini(dem_funded, data.projects)

    # ── 3. MES counterfactual ─────────────────────────────────────────────────
    ballots = generate_ballots(data.projects, n_voters=n_voters, seed=seed)
    costs   = dict(zip(data.projects["project_id"], data.projects["cost_mxn"]))
    mes_funded  = run_mes(ballots, costs, budget)
    mes_welfare = welfare(mes_funded, data.projects)
    mes_alloc   = district_allocations(mes_funded, data.projects)
    mes_gini    = equity_gini(mes_funded, data.projects)

    # ── 4. Print summary ──────────────────────────────────────────────────────
    print("\n=== Simulation Results ===")
    print(f"Budget: {budget:,.0f} MXN  |  N voters: {n_voters}  |  Seed: {seed}")
    print(f"\nDEM:  welfare={dem_welfare:.0f}  gini={dem_gini:.3f}  "
          f"funded={len(dem_funded)} projects")
    print(f"MES:  welfare={mes_welfare:.0f}  gini={mes_gini:.3f}  "
          f"funded={len(mes_funded)} projects")
    print(f"\nWelfare gain (MES - DEM): {mes_welfare - dem_welfare:.0f} votes")
    print(f"Equity gain  (DEM Gini - MES Gini): {dem_gini - mes_gini:.3f}")

    print(f"\nDEM funded project IDs: {dem_funded}")
    print(f"MES funded project IDs: {mes_funded}")

    # ── 5. Save figures ───────────────────────────────────────────────────────
    os.makedirs(OUT_FIG_DIR, exist_ok=True)
    _plot_welfare_comparison(dem_welfare, mes_welfare)
    _plot_equity_comparison(dem_alloc, mes_alloc, data.districts, budget)

    # ── 6. Save comparison table ──────────────────────────────────────────────
    os.makedirs(OUT_TAB_DIR, exist_ok=True)
    _write_latex_table(
        dem_funded, mes_funded,
        dem_alloc, mes_alloc,
        dem_welfare, mes_welfare,
        dem_gini, mes_gini,
        data.projects, data.districts,
    )


# ── Plot helpers ─────────────────────────────────────────────────────────────

def _plot_welfare_comparison(dem_w: float, mes_w: float) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    mechanisms = ["DEM (observed)", "MES (counterfactual)"]
    values = [dem_w, mes_w]
    colors = ["#8B1A1A", "#1A6B3A"]
    bars = ax.bar(mechanisms, values, color=colors, width=0.4)
    ax.bar_label(bars, fmt="%.0f votes")
    ax.set_ylabel("Utilitarian welfare (total votes on funded projects)")
    ax.set_title("Welfare Comparison: DEM vs MES\nDurango PP 2025")
    plt.tight_layout()
    path = os.path.join(OUT_FIG_DIR, "fig_welfare_comparison.pdf")
    fig.savefig(path)
    plt.close(fig)
    print(f"Saved {path}")


def _plot_equity_comparison(
    dem_alloc: dict[str, float],
    mes_alloc: dict[str, float],
    districts: list[str],
    budget: float,
) -> None:
    df = pd.DataFrame({
        "District": districts * 2,
        "Mechanism": ["DEM"] * len(districts) + ["MES"] * len(districts),
        "Funding (MXN)": (
            [dem_alloc.get(d, 0) for d in districts]
            + [mes_alloc.get(d, 0) for d in districts]
        ),
    })
    fig, ax = plt.subplots(figsize=(8, 4))
    df_pivot = df.pivot(index="District", columns="Mechanism", values="Funding (MXN)")
    df_pivot.plot(kind="bar", ax=ax, color=["#8B1A1A", "#1A6B3A"])
    equal_share = budget / len(districts)
    ax.axhline(
        equal_share,
        linestyle="--",
        color="gray",
        label=f"Equal share ({equal_share:,.0f} MXN)",
    )
    ax.set_xlabel("")
    ax.set_ylabel("Funded cost (MXN)")
    ax.set_title("District-Level Funding: DEM vs MES\nDurango PP 2025")
    ax.legend()
    plt.xticks(rotation=0)
    plt.tight_layout()
    path = os.path.join(OUT_FIG_DIR, "fig_equity_comparison.pdf")
    fig.savefig(path)
    plt.close(fig)
    print(f"Saved {path}")


# ── Table helper ─────────────────────────────────────────────────────────────

def _write_latex_table(
    dem_f: list[str],
    mes_f: list[str],
    dem_alloc: dict[str, float],
    mes_alloc: dict[str, float],
    dem_w: float,
    mes_w: float,
    dem_g: float,
    mes_g: float,
    projects: pd.DataFrame,
    districts: list[str],
) -> None:
    lines = [
        r"\begin{tabular}{lrr}",
        r"\toprule",
        r"\textbf{Metric} & \textbf{DEM} & \textbf{MES} \\",
        r"\midrule",
        rf"Welfare (total votes) & {dem_w:.0f} & {mes_w:.0f} \\",
        rf"Gini (district equity) & {dem_g:.3f} & {mes_g:.3f} \\",
        rf"Projects funded & {len(dem_f)} & {len(mes_f)} \\",
        r"\midrule",
    ]
    for d in districts:
        dem_v = dem_alloc.get(d, 0.0)
        mes_v = mes_alloc.get(d, 0.0)
        lines.append(
            rf"Funding {d} (MXN) & {dem_v:,.0f} & {mes_v:,.0f} \\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    path = os.path.join(OUT_TAB_DIR, "tab_simulation_comparison.tex")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Saved {path}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run DEM vs MES simulation for Durango PP 2025."
    )
    parser.add_argument(
        "--budget", type=float, default=500_000.0,
        help="Total budget in MXN (default: 500000)",
    )
    parser.add_argument(
        "--n-voters", type=int, default=1_000,
        help="Number of synthetic voters for MES (default: 1000)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42)",
    )
    args = parser.parse_args()
    main(args.budget, args.n_voters, args.seed)
