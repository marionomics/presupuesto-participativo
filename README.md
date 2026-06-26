# Presupuesto Participativo — Mechanism Design for District-Exclusive Voting

A research project on the **district-exclusivity constraint** in Durango, Mexico's
participatory budgeting (*presupuesto participativo*) system, combining mechanism design,
social choice theory, and simulation.

## The question

Durango's rule makes each voter pick **one** district and spend all their votes inside it.
This project asks what strategic and welfare distortions that constraint introduces, and what
alternative rule mitigates them **without** sacrificing geographic equity for marginalized
districts.

## Main results (informal)

The current rule — which we call the **District-Exclusivity Mechanism (DEM)** — is shown to
produce five distinct distortions: preference truncation, noise injection from uninformed
voting, a coordination game with multiple equilibria, a mobilization advantage for organized
institutions, and (the pivot) a tradeoff in which simply deregulating to an **Unrestricted
Allocation Mechanism (UAM)** destroys geographic equity. The proposed remedy is the **Method
of Equal Shares** (Peters, Pierczyński & Skowron 2021), which provides proportional —
hence geographic — representation *by construction* via Extended Justified Representation,
while remaining honestly limited (it is not strategy-proof, and a completion step places part
of the budget without the proportionality guarantee).

The empirical component is a **simulation study**; analysis of real municipal ballot data is
future work.

## Contents of this repository

| Path | What it is |
|------|------------|
| [`notebooks/notebook_v2.tex`](notebooks/notebook_v2.tex) | **Working Notebook (v2)** — a self-contained, motivated, corrected derivation of the whole theory, from mechanism-design foundations to the Method of Equal Shares, with full proofs and worked examples. |
| [`presentation/main.tex`](presentation/main.tex) | Conference/seminar **presentation** (Beamer). |
| `pb_mes/` | Python simulation pipeline (DEM vs. MES) and supporting utilities. |
| `tests/` | Unit tests for the simulation pipeline. |

Compiled PDFs of the notebook and presentation are included alongside their sources.

## Building

```bash
# Notebook
cd notebooks && pdflatex notebook_v2.tex

# Presentation
cd presentation && latexmk -pdf main.tex
```

## Status

Theory complete and reviewed for internal consistency; simulation pipeline in place;
the paper itself is in preparation. Real-data estimation is planned as a follow-up.

## Author

Mario Alberto García Meza — Facultad de Economía, Contaduría y Administración,
Universidad Juárez del Estado de Durango (FECA-UJED).
